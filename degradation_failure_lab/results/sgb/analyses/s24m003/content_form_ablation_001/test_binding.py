"""Offline tests for the new input binding and reused two-attempt gate."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
def offline(event,args):
    if event.startswith("socket.") or event in ("subprocess.Popen","os.system"):
        raise RuntimeError("No network/child processes in contract tests")
sys.addaudithook(offline)
import execute_content_form as e

class BindingContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.config,cls.bodies=e.validate()
    def output(self):
        temp=tempfile.TemporaryDirectory(prefix="contract_",dir=e.ROOT)
        assert Path(temp.name).resolve().is_relative_to(e.ROOT.resolve())
        self.addCleanup(temp.cleanup)
        return Path(temp.name)/"pair"
    def response(self,content='{"skills": []}'):
        return json.dumps({"model":"fixture","system_fingerprint":"fixture",
          "choices":[{"message":{"content":content},"finish_reason":"stop"}],
          "usage":{"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}}).encode()

    def test_frozen_input_mapping_and_preserved_span(self):
        for arm in ("A","B"):
            self.assertEqual(self.bodies[arm],(e.DESIGN/arm/"request.json").read_bytes())
            self.assertEqual(e.sha(self.bodies[arm]),e.EXPECTED[arm])
            user=json.loads(json.loads(self.bodies[arm])["messages"][1]["content"])
            self.assertEqual(user["taxonomy"]["domain_type"],"scrapy")
            self.assertEqual(user["section"]["span"],{"start":15603,"end":17155})
            self.assertEqual(len(user["excerpt"]),1552 if arm=="A" else 1643)

    def test_reused_gate_real_transport_two_opens_no_redirect_restart_rejected(self):
        old=e.pair_helper(); helper=old.helper(); outer=self; opens=[]; handlers=[]
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return outer.response()
        class Opener:
            def open(self,request,timeout):
                opens.append(request.data);outer.assertEqual(timeout,180);return Response()
        def build(*args):handlers.extend(args);return Opener()
        out=self.output()
        with patch.object(helper.urllib.request,"build_opener",side_effect=build):
            send=e.bounded_transport(self.config,out,helper.post_once)
            result=old.execute_pair(self.config,self.bodies,out,send,"local-test-token")
            with self.assertRaises(FileExistsError):
                old.execute_pair(self.config,self.bodies,out,send,"local-test-token")
        self.assertEqual(opens,[self.bodies["A"],self.bodies["B"]])
        starts=[json.loads(line)["arm"] for line in (out/"events.jsonl").read_text().splitlines()
                if json.loads(line)["state"]=="HTTP_ATTEMPT_STARTED"]
        self.assertEqual(starts,["A","B"])
        redirects=[h for h in handlers if isinstance(h,helper.NoRedirect)]
        self.assertEqual(len(redirects),2)
        self.assertIsNone(redirects[0].redirect_request(None,None,307,"",{},"https://invalid.example"))
        self.assertEqual([result[a]["state"] for a in ("A","B")],["EMPTY_PLAN","EMPTY_PLAN"])

    def test_failure_and_invalid_json_not_retried_or_repaired(self):
        calls=[];out=self.output();old=e.pair_helper()
        def post(config,body,token):
            calls.append(body)
            if len(calls)==1:
                raise urllib.error.HTTPError(config["endpoint"],429,"fixture",None,io.BytesIO(b"{}"))
            return 200,self.response("{")
        result=old.execute_pair(self.config,self.bodies,out,e.bounded_transport(self.config,out,post),"local-test-token")
        self.assertEqual(calls,[self.bodies["A"],self.bodies["B"]])
        self.assertEqual(result["A"]["state"],"HTTP_ERROR")
        self.assertEqual(result["B"]["state"],"INVALID_JSON")
        self.assertTrue(all(x["retries"]==x["json_repair_requests"]==0 for x in result.values()))

    def test_duplicate_or_changed_bytes_stopped_before_post(self):
        calls=[];out=self.output();out.mkdir()
        def post(config,body,token):
            calls.append(body);return 200,self.response()
        send=e.bounded_transport(self.config,out,post)
        send(self.config,self.bodies["A"],"local-test-token")
        with self.assertRaises(AssertionError):send(self.config,self.bodies["A"],"local-test-token")
        with self.assertRaises(AssertionError):send(self.config,self.bodies["B"]+b"\n","local-test-token")
        send(self.config,self.bodies["B"],"local-test-token")
        with self.assertRaises(AssertionError):send(self.config,self.bodies["B"],"local-test-token")
        self.assertEqual(calls,[self.bodies["A"],self.bodies["B"]])

if __name__=="__main__":
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BindingContract))
    (e.ROOT/"contract_tests.log").write_text(stream.getvalue(),encoding="utf-8")
    e.write(e.ROOT/"contract_tests.json",{"tests":result.testsRun,"passed":result.wasSuccessful(),
        "failures":len(result.failures),"errors":len(result.errors),"real_model_http_requests":0,
        "network_and_subprocess_audit_guard":True,"test_script_sha256":e.sha(Path(__file__).read_bytes())})
    print(stream.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)
