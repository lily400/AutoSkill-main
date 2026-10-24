"""Local fake transports only; no model API is reachable in this test process."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error
import probe

TOKEN = "fixture-only-key"


class ProbeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.body = probe.validate()

    def envelope(self, content, finish="stop"):
        return json.dumps({"model": "fixture", "system_fingerprint": "fixture",
            "choices": [{"message": {"content": content}, "finish_reason": finish}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0}}).encode()

    def run_case(self, raw=None, error=None):
        calls = []
        def fake(config, body, token):
            calls.append(body)
            self.assertEqual(self.body, body)
            if error:
                raise error
            return 200, raw
        with tempfile.TemporaryDirectory(prefix="fixture_", dir=probe.ROOT) as temp:
            out = Path(temp) / "attempt"
            result = probe.execute_once(self.config, self.body, out, fake, TOKEN)
            self.assertEqual(1, len(calls))
            self.assertEqual(0, result["retries"])
            self.assertEqual(0, result["expand_calls"])
            with self.assertRaises(FileExistsError):
                probe.execute_once(self.config, self.body, out, fake, TOKEN)
            self.assertEqual(1, len(calls))
            self.assertEqual(self.body, (out / "request.json").read_bytes())
            self.assertTrue(all(TOKEN.encode() not in p.read_bytes() for p in out.iterdir() if p.is_file()))
            return result

    def test_known_historical_nonempty_parses_locally(self):
        result = self.run_case((probe.ROOT / "historical_response.json").read_bytes())
        self.assertEqual("NONEMPTY_PLAN", result["state"])
        self.assertEqual(4, result["native_candidate_count"])
        self.assertTrue(result["strict_json_valid"])

    def test_empty_stops(self):
        self.assertEqual("EMPTY_PLAN", self.run_case(self.envelope('{"skills": []}'))["state"])

    def test_invalid_json_is_not_repaired(self):
        self.assertEqual("INVALID_JSON", self.run_case(self.envelope("not JSON"))["state"])

    def test_truncation_is_distinct(self):
        self.assertEqual("INCOMPLETE_RESPONSE", self.run_case(self.envelope('{"skills": []}', "length"))["state"])

    def test_nonempty_without_name_is_filtered(self):
        self.assertEqual("CANDIDATE_FILTERED", self.run_case(self.envelope('{"skills": [{}]}'))["state"])

    def test_timeout_does_not_retry(self):
        self.assertEqual("TRANSPORT_ERROR", self.run_case(error=TimeoutError())["state"])

    def test_http_failure_does_not_retry(self):
        error = urllib.error.HTTPError(self.config["endpoint"], 429, "fixture", {}, io.BytesIO(b"fixture"))
        self.assertEqual("HTTP_ERROR", self.run_case(error=error)["state"])

    def test_response_echoing_credential_is_redacted(self):
        result = self.run_case(self.envelope('{"skills": [], "echo": "' + TOKEN + '"}'))
        self.assertEqual("RESPONSE_REDACTED", result["state"])
        self.assertTrue(result["credential_redaction_required"])

    def test_real_transport_function_opens_exactly_once(self):
        response = Mock()
        response.status = 200
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b"fixture"
        opener = Mock()
        opener.open.return_value = response
        with patch.object(probe.urllib.request, "build_opener", return_value=opener) as build:
            self.assertEqual((200, b"fixture"), probe.post_once(self.config, self.body, TOKEN))
        opener.open.assert_called_once()
        request = opener.open.call_args.args[0]
        self.assertEqual(self.body, request.data)
        self.assertEqual(self.config["endpoint"], request.full_url)
        self.assertEqual("POST", request.get_method())
        self.assertTrue(any(isinstance(h, probe.NoRedirect) for h in build.call_args.args))
        self.assertIsNone(probe.NoRedirect().redirect_request(None, None, 302, "fixture", {}, "https://example.invalid"))

    def test_real_transport_failure_has_no_second_open(self):
        opener = Mock()
        opener.open.side_effect = urllib.error.URLError("fixture")
        with patch.object(probe.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(urllib.error.URLError):
                probe.post_once(self.config, self.body, TOKEN)
        opener.open.assert_called_once()

    def test_frozen_request_is_exact_source_copy(self):
        self.assertEqual(Path(self.config["request_source"]).read_bytes(), self.body)


if __name__ == "__main__":
    def guard(event, values):
        if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
            raise RuntimeError("OFFLINE_ONLY")
    sys.addaudithook(guard)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProbeContractTest))
    (probe.ROOT / "contract_tests.log").write_text(log.getvalue(), encoding="utf-8")
    summary = {"tests_run": result.testsRun, "passed": result.wasSuccessful(), "new_model_requests": 0,
               "transport": "LOCAL_FAKE_ONLY", "failures": len(result.failures), "errors": len(result.errors)}
    (probe.ROOT / "contract_tests.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if not result.wasSuccessful():
        print(log.getvalue())
        raise SystemExit(1)
