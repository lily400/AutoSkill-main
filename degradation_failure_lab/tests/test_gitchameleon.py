import hashlib,json,pathlib,sys,unittest
from unittest.mock import patch
LAB=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB/'src'))
from degradation_lab.catalog import CaseManager
from degradation_lab.runner import ExperimentRunner
from degradation_lab.io import sha256,read
from degradation_lab.schema import SCHEMAS

class GitChameleonImport(unittest.TestCase):
    def setUp(self):
        self.network=patch('urllib.request.urlopen',side_effect=AssertionError('No model/network calls in validation'))
        self.network.start();self.addCleanup(self.network.stop)

    def test_full_original_dataset_and_tests_unchanged(self):
        root=LAB/'.external/gitchameleon/3a1b6045a6b2a276bd24d715589cb041f8eccb93'
        manifest=read(root/'archive_manifest.json')
        self.assertEqual(sha256(root/'upstream/dataset/dataset.jsonl'),'978c7c581cad399989cb8399ec208ddd0edb6260ef576b3ce442aeaae455609e')
        for path,item in manifest['files'].items():self.assertEqual(sha256(root/path),item['sha256'],path)

    def test_only_safe_public_task_fields(self):
        allowed={'example_id','python_version','library','version','problem','starting_code','additional_dependencies'}
        original={r['example_id']:r for r in (json.loads(l) for l in (LAB/'.external/gitchameleon/3a1b6045a6b2a276bd24d715589cb041f8eccb93/selected_original_rows.jsonl').read_text().splitlines())}
        for tid in ['144','164']:
            public=read(LAB/f'downstream_eval/tasks/gitchameleon_{tid}_v1/agent_input.json')
            self.assertEqual(set(public),allowed)
            self.assertEqual(public,{k:original[tid][k] for k in allowed})

    def test_three_conditions_and_unchanged_companion_allowed(self):
        manager=CaseManager(LAB)
        for case in ['case144_gch','case164_gch']:
            bundle=manager.load(case)
            self.assertEqual([c['condition_id'] for c in bundle['conditions']['conditions']],['c00','c01','c02'])
            plans=[ExperimentRunner(LAB).plan(case,c) for c in ['c00','c01','c02']]
            self.assertEqual(len({p['input_count'] for p in plans}),1)
            for cid in ['c00','c01','c02']:manager.condition(bundle,cid)
        bundle=manager.load('case164_gch')
        _,clean=manager.condition(bundle,'c00');_,degraded=manager.condition(bundle,'c01')
        self.assertEqual(clean['inputs'][0]['sha256'],degraded['inputs'][0]['sha256'])
        self.assertNotEqual(clean['inputs'][1]['sha256'],degraded['inputs'][1]['sha256'])

    def test_unchanged_entire_corpus_rejected(self):
        manager=CaseManager(LAB);bundle=manager.load('case164_gch')
        _,manifest=manager.condition(bundle,'c01')
        for item in manifest['inputs']:
            item['path']='data/condition_inputs/'+item['input_id']+'.md';item['sha256']=item['source_sha256']
        native_read=__import__('degradation_lab.catalog',fromlist=['read']).read
        def condition_hash(p):
            for item in manifest['inputs']:
                if str(p).replace('\\','/').endswith(item['path']):return item['sha256']
            return sha256(p)
        with patch('degradation_lab.catalog.read',side_effect=lambda p:manifest if str(p).endswith('c01.json') else native_read(p)),patch('degradation_lab.catalog.sha256',side_effect=condition_hash):
            # Source verification remains real; only the condition fixture is replaced.
            with self.assertRaisesRegex(ValueError,'duplicated clean bytes'):manager.condition(bundle,'c01')

    def test_fidelity_and_deletions(self):
        clean=LAB/'data/raw_sources/gitchameleon/prepared'
        flask=(clean/'flask_json.md').read_text();numpy=(clean/'numpy_unique.md').read_text()
        self.assertIn('attribute afterwards.',flask);self.assertIn('equal_nan=True',numpy)
        semantic='If True, collapses multiple NaN values in the return array into one.'
        self.assertIn(semantic,numpy)
        relevant=(LAB/'data/condition_inputs/gitchameleon/164/c01/numpy_unique.md').read_text()
        irrelevant=(LAB/'data/condition_inputs/gitchameleon/164/c02/numpy_unique.md').read_text()
        self.assertNotIn(semantic,relevant);self.assertIn('equal_nan=True',relevant);self.assertIn(semantic,irrelevant)
        for delta in read(LAB/'data/manifests/gitchameleon_fidelity.json')['degradations']:
            self.assertEqual(sha256(LAB/delta['file']),delta['sha256'])
            self.assertTrue((LAB/delta['diff_file']).is_file())

    def test_gate_blocks_before_prepare_or_model(self):
        for case in ['case144_gch','case164_gch']:
            native=__import__('degradation_lab.runner',fromlist=['read']).read
            def blocked(p):return {'status':'BLOCKED'} if str(p).endswith('gates.json') else native(p)
            with patch('degradation_lab.runner.read',side_effect=blocked),patch.object(ExperimentRunner,'prepare',side_effect=AssertionError('No run may be created')):
                with self.assertRaisesRegex(RuntimeError,'execution gate'):ExperimentRunner(LAB).run(case,'c00')

    def test_published_schemas_match_code(self):
        for name in ['case','source']:
            schema=read(LAB/f'schemas/{name}.schema.json');schema.pop('$schema');schema.pop('title')
            self.assertEqual(schema,SCHEMAS[name])

if __name__=='__main__':unittest.main()
