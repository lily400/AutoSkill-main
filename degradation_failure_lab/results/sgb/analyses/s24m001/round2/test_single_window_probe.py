"""Local fake transport only; process audit hook prohibits network."""
import argparse
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error

import single_window_probe as probe


class ProbeContractTest(unittest.TestCase):
    config = None
    body = None

    def response(self, content, finish="stop"):
        return json.dumps({"model": "fixture-not-a-real-response", "choices": [{"message": {"content": content},
            "finish_reason": finish}], "usage": {"prompt_tokens": 0, "completion_tokens": 0}}).encode()

    def run_case(self, raw=None, error=None):
        calls = []
        def fake(config, body, token):
            calls.append(body)
            self.assertEqual("fake-not-a-key", token)
            if error is not None:
                raise error
            return raw
        with tempfile.TemporaryDirectory(prefix="s24probe_", dir=Path.cwd()) as temp:
            out = Path(temp) / "attempt"
            result = probe.execute_once(self.config, self.body, out, fake, "fake-not-a-key")
            self.assertEqual([self.body], calls)
            self.assertEqual(1, result["http_attempts"])
            self.assertEqual(0, result["retries"])
            with self.assertRaises(FileExistsError):
                probe.execute_once(self.config, self.body, out, fake, "fake-not-a-key")
            self.assertEqual(1, len(calls))
            if error is None:
                self.assertEqual(raw, (out / "response.raw.json").read_bytes())
            return result

    def test_empty_is_not_retried(self):
        self.assertEqual("EMPTY_PLAN", self.run_case(self.response('{"skills": []}'))["state"])

    def test_malformed_json_is_not_repaired(self):
        self.assertEqual("JSON_PARSE_FAILURE", self.run_case(self.response("not json"))["state"])

    def test_schema_mismatch_is_separate(self):
        self.assertEqual("SCHEMA_MISMATCH", self.run_case(self.response('{"skills": "invalid"}'))["state"])

    def test_name_filter_is_separate(self):
        self.assertEqual("CANDIDATE_FILTERED", self.run_case(self.response('{"skills": [{"description": "x"}]}'))["state"])

    def test_nonempty_needs_semantic_review(self):
        result = self.run_case(self.response('{"skills": [{"name": "Storage constraint"}]}'))
        self.assertEqual("NONEMPTY_PLAN_TARGET_REVIEW_REQUIRED", result["state"])
        self.assertEqual(1, len(result["native_plan_candidates"]))
        self.assertEqual(0, result["expand_calls"])

    def test_timeout_is_not_retried(self):
        self.assertEqual("TRANSPORT_ERROR", self.run_case(error=TimeoutError())["state"])

    def test_http_error_and_redirect_do_not_retry(self):
        err = urllib.error.HTTPError("https://example.invalid", 429, "fixture", {}, io.BytesIO(b"fixture error"))
        result = self.run_case(error=err)
        self.assertEqual("HTTP_ERROR", result["state"])
        self.assertEqual(429, result["http_status"])
        self.assertIsNone(probe.NoRedirect().redirect_request(None, None, 302, "fixture", {}, "https://example.invalid"))

    def test_truncated_response_is_not_a_complete_plan(self):
        self.assertEqual("INCOMPLETE_RESPONSE", self.run_case(self.response('{"skills": []}', "length"))["state"])

    def test_bad_envelope_is_distinct(self):
        self.assertEqual("RESPONSE_ENVELOPE_ERROR", self.run_case(b'{"error": "fixture"}')["state"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    def guard(event, values):
        if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
            raise RuntimeError("OFFLINE_ONLY")
    sys.addaudithook(guard)
    ProbeContractTest.config, ProbeContractTest.body = probe.validate(args.bundle)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProbeContractTest))
    (args.out / "tests.log").write_text(log.getvalue(), encoding="utf-8")
    summary = {"tests_run": result.testsRun, "passed": result.wasSuccessful(), "new_model_requests": 0,
               "transport": "LOCAL_FAKE_ONLY", "failures": len(result.failures), "errors": len(result.errors)}
    (args.out / "tests.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if not result.wasSuccessful():
        print(log.getvalue())
        raise SystemExit(1)
