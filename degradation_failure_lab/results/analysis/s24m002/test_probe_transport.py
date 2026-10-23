"""Supplement existing nine contracts with real post_once + fake opener tests."""
import argparse
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
import urllib.error


class TransportContractTest(unittest.TestCase):
    config = None
    body = None

    def test_frozen_request_has_one_open_and_no_redirect_following(self):
        import single_window_probe as probe
        raw = b'{"fixture": "not-a-model-response"}'
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = raw
        opener = Mock()
        opener.open.return_value = response
        with patch.object(probe.urllib.request, "build_opener", return_value=opener) as build:
            self.assertEqual(raw, probe.post_once(self.config, self.body, "fake-not-a-key"))
        self.assertEqual(1, build.call_count)
        opener.open.assert_called_once()
        request = opener.open.call_args.args[0]
        self.assertEqual("POST", request.get_method())
        self.assertEqual(self.config["endpoint"], request.full_url)
        self.assertEqual(self.body, request.data)
        self.assertEqual(self.config["timeout_s"], opener.open.call_args.kwargs["timeout"])
        self.assertTrue(any(isinstance(h, probe.NoRedirect) for h in build.call_args.args))
        self.assertIsNone(probe.NoRedirect().redirect_request(None, None, 302, "fixture", {}, "https://example.invalid"))

    def test_transport_failure_has_no_second_open(self):
        import single_window_probe as probe
        opener = Mock()
        opener.open.side_effect = urllib.error.URLError("local fixture")
        with patch.object(probe.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(urllib.error.URLError):
                probe.post_once(self.config, self.body, "fake-not-a-key")
        opener.open.assert_called_once()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry-dir", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    def guard(event, values):
        if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
            raise RuntimeError("OFFLINE_ONLY")
    sys.addaudithook(guard)
    sys.path.insert(0, str(args.entry_dir.resolve()))
    import single_window_probe as probe
    TransportContractTest.config, TransportContractTest.body = probe.validate(args.bundle)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TransportContractTest))
    (args.out / "tests.log").write_text(log.getvalue(), encoding="utf-8")
    summary = {"tests_run": result.testsRun, "passed": result.wasSuccessful(), "new_model_requests": 0,
        "transport": "REAL_POST_ONCE_FUNCTION_WITH_LOCAL_FAKE_OPENER", "failures": len(result.failures), "errors": len(result.errors)}
    (args.out / "tests.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if not result.wasSuccessful():
        print(log.getvalue())
        raise SystemExit(1)
