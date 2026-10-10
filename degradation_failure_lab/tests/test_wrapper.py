import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'scripts'))
from common import LAB, new_run, sha256
from run_clean import validate_config


class BaselineGuards(unittest.TestCase):
    def test_real_source_hash_and_classification(self):
        m=json.loads((LAB / 'data/manifests/qsv_select_canonical.json').read_text(encoding='utf-8'))
        self.assertEqual(sha256(LAB / m['local_path']),m['sha256'])
        self.assertEqual(m['classification'],'RECONSTRUCTED_OFFICIAL_SOURCE')
        self.assertFalse(m['paper_snapshot_verified'])

    def test_isolation_and_collision_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            first=new_run(d,'one')
            (first / 'SkillBank/sentinel').write_text('old registry')
            second=new_run(d,'two')
            self.assertEqual(list((second/'SkillBank').iterdir()),[])
            with self.assertRaises(FileExistsError): new_run(d,'one')

    def test_mock_and_literal_key_are_rejected(self):
        with self.assertRaises(ValueError): validate_config({'llm':{'provider':'mock'}})
        with self.assertRaises(ValueError): validate_config({'llm':{'provider':'openai','api_key':'not-a-real-key'}})
        with self.assertRaises(ValueError): validate_config({'llm':{'provider':'openai','response':'fake'}})

    def test_adapter_changes_only_thinking_parameter(self):
        from common import UPSTREAM
        sys.path.insert(0,str(UPSTREAM))
        from autoskill.llm.factory import build_llm
        from provider_adapter import build
        cfg={'provider':'openai','model':'deepseek-flash','max_tokens':256}
        baseline=build_llm(cfg)._build_payload(system='original system',user='original input',temperature=0,stream=False)
        adapted=build(cfg)._build_payload(system='original system',user='original input',temperature=0,stream=False)
        self.assertEqual(adapted.pop('thinking'),{'type':'disabled'})
        self.assertEqual(adapted,baseline)


if __name__=='__main__': unittest.main()
