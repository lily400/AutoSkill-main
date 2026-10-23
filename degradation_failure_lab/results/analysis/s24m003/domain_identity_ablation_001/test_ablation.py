"""Local-only checks for the new paired gate and preregistered field boundary."""
import copy
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
        raise RuntimeError("No network or child process in contract tests")
sys.addaudithook(offline)
import ablation as a


class PairContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.bodies = a.validate()

    def temporary(self):
        temp = tempfile.TemporaryDirectory(prefix="local_contract_", dir=a.ROOT)
        assert Path(temp.name).resolve().is_relative_to(a.ROOT.resolve())
        self.addCleanup(temp.cleanup)
        return Path(temp.name) / "pair"

    def empty(self):
        return json.dumps({"model": "local-fixture", "system_fingerprint": "fixture",
            "choices": [{"message": {"content": '{"skills": []}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}).encode()

    def test_original_bytes_and_exact_identity_boundary(self):
        self.assertEqual(self.bodies["A"], (a.HISTORY / "request.json").read_bytes())
        left, right = [a.expanded(json.loads(self.bodies[k])) for k in ("A", "B")]
        diff = a.check_diff(json.loads(self.bodies["A"]), json.loads(self.bodies["B"]))
        self.assertEqual(len(diff), 3)
        for key in ("document", "section", "excerpt", "max_candidates"):
            self.assertEqual(left["messages"][1]["content"][key], right["messages"][1]["content"][key])
        self.assertEqual(left["messages"][1]["content"]["document"]["metadata"]["domain_type"], "default")

    def test_unregistered_changes_rejected_before_transport(self):
        original = json.loads(self.bodies["A"])
        b = json.loads(self.bodies["B"])
        def change_user(request, key, value):
            user = json.loads(request["messages"][1]["content"])
            user[key] = value
            request["messages"][1]["content"] = json.dumps(user, ensure_ascii=False)
        variants = []
        for key, value in (("excerpt", "changed"), ("section", {}), ("max_candidates", 3), ("document", {})):
            changed = copy.deepcopy(b); change_user(changed, key, value); variants.append(changed)
        changed = copy.deepcopy(b); changed["temperature"] = 0.1; variants.append(changed)
        changed = copy.deepcopy(b); changed["messages"][0]["content"] += "\nReturn nonempty."; variants.append(changed)
        user = json.loads(b["messages"][1]["content"])
        user["taxonomy"]["asset_tree"] = []
        changed = copy.deepcopy(b); changed["messages"][1]["content"] = json.dumps(user); variants.append(changed)
        for index, changed in enumerate(variants):
            with self.subTest(change=index), self.assertRaises(AssertionError):
                a.check_diff(original, changed)

    def test_two_attempts_exact_bodies_and_restart_refused(self):
        calls = []
        def fake(config, body, token):
            calls.append(body); return 200, self.empty()
        output = self.temporary()
        result = a.execute_pair(self.config, self.bodies, output, fake, "local-test-token")
        self.assertEqual(calls, [self.bodies["A"], self.bodies["B"]])
        self.assertEqual([result[k]["state"] for k in ("A", "B")], ["EMPTY_PLAN", "EMPTY_PLAN"])
        with self.assertRaises(FileExistsError):
            a.execute_pair(self.config, self.bodies, output, fake, "local-test-token")
        self.assertEqual(len(calls), 2)

    def test_timeout_not_retried_and_not_repaired(self):
        calls = []
        def fake(config, body, token):
            calls.append(body)
            if len(calls) == 1:
                raise TimeoutError("fixture")
            return 200, self.empty()
        result = a.execute_pair(self.config, self.bodies, self.temporary(), fake, "local-test-token")
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["A"]["state"], "TRANSPORT_ERROR")
        self.assertEqual(result["B"]["state"], "EMPTY_PLAN")
        self.assertTrue(all(v["retries"] == v["json_repair_requests"] == 0 for v in result.values()))

    def test_http_failure_not_retried(self):
        calls = []
        def fake(config, body, token):
            calls.append(body)
            raise urllib.error.HTTPError(config["endpoint"], 429, "fixture", None, io.BytesIO(b'{"fixture":true}'))
        result = a.execute_pair(self.config, self.bodies, self.temporary(), fake, "local-test-token")
        self.assertEqual(len(calls), 2)
        self.assertEqual([result[k]["state"] for k in ("A", "B")], ["HTTP_ERROR", "HTTP_ERROR"])

    def test_real_transport_two_opens_no_redirect_or_sdk(self):
        h = a.helper()
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return outer.empty()
        class Opener:
            def open(self, request, timeout):
                opens.append(request.data)
                outer.assertEqual(timeout, 180)
                return Response()
        outer = self; opens = []; handlers = []
        def build(*args):
            handlers.extend(args); return Opener()
        with patch.object(a, "helper", return_value=h), patch.object(h.urllib.request, "build_opener", side_effect=build):
            a.execute_pair(self.config, self.bodies, self.temporary(), h.post_once, "local-test-token")
        self.assertEqual(opens, [self.bodies["A"], self.bodies["B"]])
        redirects = [item for item in handlers if isinstance(item, h.NoRedirect)]
        self.assertEqual(len(redirects), 2)
        self.assertIsNone(redirects[0].redirect_request(None, None, 307, "", {}, "https://invalid.example"))

    def test_missing_token_stops_before_reserving_or_transport(self):
        calls = []
        output = self.temporary()
        with self.assertRaises(AssertionError):
            a.execute_pair(self.config, self.bodies, output, lambda *args: calls.append(args), "")
        self.assertFalse(output.exists())
        self.assertEqual(calls, [])


if __name__ == "__main__":
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PairContract))
    (a.ROOT / "contract_tests.log").write_text(stream.getvalue(), encoding="utf-8")
    a.write(a.ROOT / "contract_tests.json", {"tests": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "passed": result.wasSuccessful(), "real_model_http_requests": 0,
        "network_and_subprocess_audit_guard": True, "test_script_sha256": a.sha(Path(__file__).read_bytes())})
    print(stream.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)
