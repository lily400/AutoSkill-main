"""Local checks for exact-byte reverse-order replication, with networking prohibited."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

def offline(event, args):
    if event.startswith("socket.") or event in ("subprocess.Popen", "os.system"):
        raise RuntimeError("Contract test forbids networking and child processes")
sys.addaudithook(offline)
import replication as r


class ReplicationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.bodies = r.validate()

    def output(self):
        temp = tempfile.TemporaryDirectory(prefix="contract_", dir=r.ROOT)
        assert Path(temp.name).resolve().is_relative_to(r.ROOT.resolve())
        self.addCleanup(temp.cleanup)
        return Path(temp.name) / "pair"

    def envelope(self, content='{"skills": []}'):
        return json.dumps({"model": "fixture", "system_fingerprint": "fixture",
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}).encode()

    def test_frozen_bytes_parameters_and_metadata(self):
        self.assertEqual(list(self.bodies), ["B", "A"])
        for arm in ("B", "A"):
            self.assertEqual(self.bodies[arm], (r.PRIOR / "live" / arm / "request.json").read_bytes())
            self.assertEqual(r.sha(self.bodies[arm]), r.EXPECTED[arm])
        users = {arm: json.loads(json.loads(body)["messages"][1]["content"]) for arm, body in self.bodies.items()}
        for key in ("excerpt", "section", "document", "max_candidates"):
            self.assertEqual(users["B"][key], users["A"][key])

    def test_real_transport_B_then_A_two_opens_no_redirect_and_restart_rejected(self):
        helper = r.helper(); outer = self; opens = []; handlers = []
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return outer.envelope()
        class Opener:
            def open(self, request, timeout):
                opens.append(request.data)
                outer.assertEqual(timeout, 180)
                return Response()
        def build(*args):
            handlers.extend(args); return Opener()
        output = self.output()
        with patch.object(r, "helper", return_value=helper), patch.object(helper.urllib.request, "build_opener", side_effect=build):
            result = r.execute_pair(self.config, self.bodies, output, helper.post_once, "local-test-token")
            with self.assertRaises(FileExistsError):
                r.execute_pair(self.config, self.bodies, output, helper.post_once, "local-test-token")
        self.assertEqual(opens, [self.bodies["B"], self.bodies["A"]])
        self.assertEqual([item["arm"] for item in map(json.loads, (output/"events.jsonl").read_text().splitlines())
                          if item["state"] == "ATTEMPT_STARTED"], ["B", "A"])
        self.assertEqual([result[k]["state"] for k in ("B", "A")], ["EMPTY_PLAN", "EMPTY_PLAN"])
        redirect_handlers = [h for h in handlers if isinstance(h, helper.NoRedirect)]
        self.assertEqual(len(redirect_handlers), 2)
        self.assertIsNone(redirect_handlers[0].redirect_request(None, None, 307, "", {}, "https://invalid.example"))

    def test_timeout_and_http_error_each_consume_one_attempt(self):
        calls = []
        def transport(config, body, token):
            calls.append(body)
            if len(calls) == 1:
                raise TimeoutError("fixture")
            raise urllib.error.HTTPError(config["endpoint"], 429, "fixture", None, io.BytesIO(b'{"fixture":true}'))
        result = r.execute_pair(self.config, self.bodies, self.output(), transport, "local-test-token")
        self.assertEqual(calls, [self.bodies["B"], self.bodies["A"]])
        self.assertEqual(result["B"]["state"], "TRANSPORT_ERROR")
        self.assertEqual(result["A"]["state"], "HTTP_ERROR")

    def test_invalid_json_has_no_repair_or_extra_attempt(self):
        calls = []
        def transport(config, body, token):
            calls.append(body); return 200, self.envelope("{")
        result = r.execute_pair(self.config, self.bodies, self.output(), transport, "local-test-token")
        self.assertEqual(calls, [self.bodies["B"], self.bodies["A"]])
        self.assertEqual([result[k]["state"] for k in ("B", "A")], ["INVALID_JSON", "INVALID_JSON"])
        self.assertTrue(all(item["retries"] == item["json_repair_requests"] == 0 for item in result.values()))

    def test_missing_credential_zero_attempt(self):
        calls = []; output = self.output()
        with self.assertRaises(AssertionError):
            r.execute_pair(self.config, self.bodies, output, lambda *args: calls.append(args), "")
        self.assertEqual(calls, [])
        self.assertFalse(output.exists())


if __name__ == "__main__":
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ReplicationContract))
    (r.ROOT/"contract_tests.log").write_text(stream.getvalue(), encoding="utf-8")
    r.write(r.ROOT/"contract_tests.json", {"tests":result.testsRun, "failures":len(result.failures),
        "errors":len(result.errors), "passed":result.wasSuccessful(), "real_model_http_requests":0,
        "network_and_subprocess_audit_guard":True, "test_script_sha256":r.sha(Path(__file__).read_bytes())})
    print(stream.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)
