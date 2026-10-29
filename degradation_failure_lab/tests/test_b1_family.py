"""Family-stage acceptance tests. Invented fixtures only; all network/model calls blocked."""
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB/'src')]
from degradation_lab.family import FamilyRegistry, CATALOG, POLICY, SOURCES, TASKS, create, jsonl, validate_catalog, main
from degradation_lab.io import read, sha256, resolve_upstream
from degradation_lab.runner import ExperimentRunner

sys.path.insert(0, str(resolve_upstream(LAB)))
from AutoSkill4Doc.taxonomy import load_skill_taxonomy
from AutoSkill4Doc.models import DocumentRecord, TextSpan, VersionState
from AutoSkill4Doc.stages.extractor import LLMDocumentSkillExtractor
from AutoSkill4Doc.stages.compiler import LLMSkillCompiler
from AutoSkill4Doc.store import versioning

TEMP = Path(r'D:\ASdoc') if Path(r'D:\ASdoc').is_dir() else Path(tempfile.gettempdir())
BASE_CATALOG, BASE_POLICY = read(LAB/CATALOG), read(LAB/POLICY)


class FamilyStage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='b1-family-test-', dir=TEMP)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for target in ('socket.socket.connect', 'socket.socket.connect_ex', 'socket.create_connection',
                       'urllib.request.urlopen', 'autoskill.llm.openai.OpenAIChatLLM.complete'):
            blocker = patch(target, side_effect=AssertionError('Zero-model test forbids network/model calls'))
            blocker.start(); self.addCleanup(blocker.stop)
        create(self.root/CATALOG, BASE_CATALOG)
        create(self.root/POLICY, BASE_POLICY)
        create(self.root/'configs/environment.json', {'upstream_path': str(resolve_upstream(LAB))})
        self.evidence = create(self.root/'review.json', {'evidence': 'Invented fixture review, not benchmark evidence'})
        self.refs = []
        self.a = self.source('fixture-a', 'Invented first framework rule.')
        self.b = self.source('fixture-b', 'Invented complementary framework rule.')
        create(self.root/'data/catalog.json', {'schema_version': 1, 'datasets': [{
            'dataset_id': 'fixture', 'description': 'invented test sources',
            'source_manifests': [r['manifest'] for r in self.refs]}]})
        create(self.root/SOURCES, [self.assignment(self.a), self.assignment(self.b)], lines=True)
        self.registry = FamilyRegistry(self.root)
        self.config = read(LAB/'configs/generation/clean_five.json')
        self.config['pipeline']['domain_type'] = 'scrapy'

    def source(self, sid, text):
        p = self.root/'data/raw_sources'/sid/'context.md'
        p.parent.mkdir(parents=True); p.write_text(text, encoding='utf-8')
        manifest = self.root/'data/manifests'/f'{sid}.json'
        value = {'source_id': sid, 'source_url': 'fixture-only', 'source_repository': 'fixture',
                 'source_commit': 'fixture', 'source_path': p.name, 'license': 'fixture',
                 'downloaded_at': datetime.now(timezone.utc).isoformat(), 'sha256': sha256(p),
                 'document_type': 'fixture', 'classification': 'CUSTOM_TEST_DATA',
                 'paper_snapshot_verified': False, 'local_path': p.relative_to(self.root).as_posix(),
                 'bytes': p.stat().st_size}
        create(manifest, value)
        ref = {'source_id': sid, 'sha256': value['sha256'],
               'manifest': manifest.relative_to(self.root).as_posix(), 'manifest_sha256': sha256(manifest)}
        self.refs.append(ref)
        return ref

    def assignment(self, ref, family='scrapy-framework', secondary=()):
        return {'classification_version': 'sgb-family-v1', 'catalog_sha256':sha256(self.root/CATALOG), 'source_id': ref['source_id'],
                'source_sha256': ref['sha256'], 'source_manifest': ref['manifest'],
                'source_manifest_sha256': ref['manifest_sha256'], 'primary_family_id': family,
                'secondary_family_ids': sorted(secondary), 'assignment_scope': 'primary_batch' if secondary else 'family_batch',
                'mixed': bool(secondary), 'status': 'APPROVED',
                'evidence_reference': [{'path': str(self.evidence), 'sha256': sha256(self.evidence)}]}

    def remap(self, rows):
        (self.root/SOURCES).write_text(''.join(json.dumps(x)+'\n' for x in rows), encoding='utf-8')
        return FamilyRegistry(self.root)

    def runtime(self):
        result = self.registry.resolve([self.a], task_key='fixture-task')
        runtime = self.registry.runtime(self.config, result, self.root/'runtime')
        return result, read(runtime['generation_config']), runtime

    def test_full_catalog_14_domains_69_families(self):
        r = FamilyRegistry(LAB)
        self.assertEqual((len(r.catalog['domains']), len(r.families)), (14, 69))
        self.assertEqual(sum(f['initial_role']=='primary' for f in r.families.values()), 67)

    def test_all_99_content_hashes_and_212_aliases(self):
        r = FamilyRegistry(LAB); checked = r.validate()
        self.assertGreaterEqual(checked['unique_source_contents'],99)
        self.assertGreaterEqual(checked['source_aliases'],212)
        initial={h for task in jsonl(LAB/'data/manifests/sgb/tasks.jsonl') for h in [s['sha256'] for s in task['sources']]}
        self.assertEqual(len(initial),99)
        self.assertTrue(initial.issubset(r.by_hash))
        self.assertTrue(all(r.by_hash[h]['status']=='APPROVED' for h in initial))
        for row in r.rows:
            self.assertEqual(r.assignment(row), r.assignment(r.by_hash[row['source_sha256']]))

    def test_all_187_tasks_match_derived_map(self):
        r = FamilyRegistry(LAB); rows = r.task_map()
        self.assertEqual(rows, jsonl(LAB/TASKS))
        self.assertEqual(len(rows), 187)
        self.assertEqual(sum(x['routing_status']=='SOURCE_PENDING' for x in rows), 18)
        self.assertEqual(sum(x['routing_status']=='READY_PRIMARY_BATCH' for x in rows), 2)

    def test_b0_ten_runtime_profiles_preserve_config(self):
        r = FamilyRegistry(LAB)
        tasks = [('sanctuary_endgame_scheduler_002','case003_san','sanctuary-rules'),
                 ('scrapy-task-024','case024_sgb','scrapy-framework'),
                 ('scrapy-task-041','case041_scrapy','scrapy-framework'),
                 ('monitoring_gap_brief_classifier_001','case101_monitor','sawcs-monitoring'),
                 ('capacity_aware_edge_admission_controller_006','case102_capacity','afn-simulation'),
                 ('pydantic-task-001','case001_pyd','pydantic-validation'),
                 ('scrapy-task-050','case050_scrapy','scrapy-framework'),
                 ('pydantic-task-004','case004_pyd','pydantic-validation'),
                 ('reviews_csv_conformance_validator_007','case103_reviews','sku-review-workflow'),
                 ('referee_attempt_decision_router_009','case104_referee','powerlifting-officiating')]
        for task, case, family in tasks:
            with self.subTest(case=case):
                t = r.registered_task(task); resolved = r.resolve(t['sources'], task_key=t['task_key'])
                _, _, manifest, cfg = ExperimentRunner(LAB).resolve(case, 'clean')
                self.assertEqual({i['source_sha256'] for i in manifest['inputs']}, set(resolved['source_set']))
                before = copy.deepcopy(cfg)
                output = r.runtime(cfg, resolved, self.root/case)
                self.assertEqual(output['family_id'], family)
                self.assertTrue(output['profile_id'])
                self.assertEqual(cfg, before)

    def test_all_families_can_materialize_one_candidate(self):
        for fid in self.registry.families:
            with self.subTest(family=fid):
                result = {'classification_version': self.registry.version, 'catalog_sha256':self.registry.catalog_hash, 'routing_status': 'READY',
                          'primary_family_id': fid, 'assignment_scope': 'family_batch'}
                output = self.registry.runtime(self.config, result, self.root/fid)
                taxonomy = read(output['taxonomy_path'])
                self.assertEqual([f['id'] for f in taxonomy['family_candidates']], [fid])

    def test_task_name_does_not_change_family(self):
        x = self.registry.resolve([self.a], task_key='scrapy-looking-name')
        y = self.registry.resolve([self.a], task_key='unrelated-pydantic-name')
        x.pop('task_key'); y.pop('task_key')
        self.assertEqual(x, y)

    def test_complementary_documents_keep_joint_batch(self):
        result = self.registry.resolve([self.a, self.b])
        self.assertEqual(result['routing_status'], 'READY')
        self.assertEqual(result['primary_family_id'], 'scrapy-framework')
        self.assertEqual(len(result['source_set']), 2)

    def test_different_families_require_routing(self):
        r = self.remap([self.assignment(self.a), self.assignment(self.b, 'pydantic-validation')])
        result = r.resolve([self.a, self.b])
        self.assertEqual(result['routing_status'], 'ROUTING_REQUIRED')
        self.assertIsNone(result['primary_family_id'])

    def test_declared_conflicts_require_routing_even_same_family(self):
        result = self.registry.resolve([self.a, self.b], rule_conflicts=['fixture incompatible versions'])
        self.assertEqual(result['routing_status'], 'ROUTING_REQUIRED')

    def test_empty_sources_pending(self):
        self.assertEqual(self.registry.resolve([])['routing_status'], 'SOURCE_PENDING')

    def test_new_unreviewed_content_requires_classification(self):
        ref = self.source('fixture-new', 'Invented unknown rule system.')
        result = self.registry.resolve([ref], task_key='scrapy-task-fake')
        self.assertEqual(result['routing_status'], 'CLASSIFICATION_REQUIRED')
        self.assertIsNone(result['primary_family_id'])

    def test_mixed_source_retains_secondary_and_coarse_scope(self):
        r = self.remap([self.assignment(self.a, 'sanctuary-rules', ['boardgame-cafe-service'])])
        result = r.resolve([self.a])
        self.assertEqual(result['routing_status'], 'READY_PRIMARY_BATCH')
        self.assertEqual(result['assignment_scope'], 'primary_batch')
        self.assertEqual(set(result['involved_families']), {'sanctuary-rules','boardgame-cafe-service'})

    def test_pending_source_review_blocks(self):
        row = self.assignment(self.a)
        row.update(status='CLASSIFICATION_REQUIRED', assignment_scope='unresolved', primary_family_id=None)
        self.assertEqual(self.remap([row]).resolve([self.a])['routing_status'], 'CLASSIFICATION_REQUIRED')

    def test_reviewed_routing_status_blocks(self):
        row = self.assignment(self.a); row.update(status='ROUTING_REQUIRED', assignment_scope='unresolved')
        self.assertEqual(self.remap([row]).resolve([self.a])['routing_status'], 'ROUTING_REQUIRED')

    def test_duplicate_family_id_rejected(self):
        c = copy.deepcopy(BASE_CATALOG); c['families'].append(c['families'][0])
        with self.assertRaises(ValueError): validate_catalog(c)

    def test_duplicate_domain_id_rejected(self):
        c = copy.deepcopy(BASE_CATALOG); c['domains'].append(c['domains'][0])
        with self.assertRaises(ValueError): validate_catalog(c)

    def test_ambiguous_alias_rejected(self):
        c = copy.deepcopy(BASE_CATALOG); c['families'][1]['aliases'].append(c['families'][0]['family_name'])
        with self.assertRaises(ValueError): validate_catalog(c)

    def test_unknown_family_in_map_rejected(self):
        with self.assertRaises(ValueError): self.remap([self.assignment(self.a, 'unknown')])

    def test_same_content_conflicting_assignment_rejected(self):
        alias = self.source('fixture-alias', 'Invented first framework rule.')
        with self.assertRaises(ValueError):
            self.remap([self.assignment(self.a), self.assignment(alias, 'pydantic-validation')])

    def test_illegal_secondary_relation_rejected(self):
        with self.assertRaises(ValueError):
            self.remap([self.assignment(self.a, secondary=['scrapy-framework'])])

    def test_source_bytes_must_pass_existing_admission(self):
        (self.root/read(self.root/self.a['manifest'])['local_path']).write_text('Changed bytes.',encoding='utf-8')
        with self.assertRaises(ValueError): self.registry.resolve([self.a])

    def test_manifest_identity_must_match(self):
        invalid = dict(self.a, sha256='0'*64)
        with self.assertRaises(ValueError): self.registry.resolve([invalid])

    def test_source_manifest_drift_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.resolve([dict(self.a, manifest_sha256='0'*64)])

    def test_duplicate_source_reference_rejected(self):
        with self.assertRaises(ValueError): self.registry.resolve([self.a, self.a])

    def test_new_document_reuses_reviewed_existing_family(self):
        ref = self.source('fixture-new', 'Another independently reviewed framework rule.')
        before = (self.root/SOURCES).read_bytes()
        answer = self.registry.register_source(ref['manifest'], family_id='scrapy-framework',
            evidence=self.evidence, reviewer='fixture-reviewer', note='Invented source-based review')
        self.assertEqual(answer['status'], 'REGISTERED')
        self.assertTrue((self.root/SOURCES).read_bytes().startswith(before))
        self.assertEqual(self.registry.resolve([ref])['primary_family_id'], 'scrapy-framework')
        self.assertEqual(len(self.registry.families), 69)

    def test_alias_reuses_content_assignment_without_task_lookup(self):
        ref = self.source('fixture-alias', 'Invented first framework rule.')
        self.assertEqual(self.registry.resolve([ref])['primary_family_id'], 'scrapy-framework')
        self.registry.register_source(ref['manifest'], evidence=self.evidence, reviewer='fixture', note='Alias of same bytes')
        self.assertIn('fixture-alias', self.registry.by_id)

    def test_unknown_family_registration_does_not_fallback(self):
        ref = self.source('fixture-new', 'Unknown text.')
        before = (self.root/SOURCES).read_bytes()
        with self.assertRaises(ValueError):
            self.registry.register_source(ref['manifest'], family_id='nonexistent',
                evidence=self.evidence, reviewer='fixture', note='Fixture review')
        self.assertEqual((self.root/SOURCES).read_bytes(), before)

    def test_unknown_system_is_not_registered_silently(self):
        ref = self.source('fixture-new', 'Unknown text.')
        before = (self.root/SOURCES).read_bytes()
        answer = self.registry.register_source(ref['manifest'], evidence=self.evidence, reviewer='fixture', note='Review needed')
        self.assertEqual(answer['routing_status'], 'CLASSIFICATION_REQUIRED')
        self.assertEqual((self.root/SOURCES).read_bytes(), before)

    def proposal(self, version='sgb-family-v2'):
        f = copy.deepcopy(BASE_CATALOG['families'][0])
        f.update(family_id='fixture-new-family',family_name='Invented new rule system',aliases=[])
        p = self.root/'proposal.json'
        create(p, {'classification_version':version,'families':[f]})
        return p

    def test_new_catalog_version_extends_without_overwriting_history(self):
        before = sha256(self.root/CATALOG), sha256(self.root/SOURCES)
        self.registry.extend(self.proposal(), 'catalog-v2.json', 'sources-v2.jsonl')
        r = FamilyRegistry(self.root, catalog='catalog-v2.json', source_map='sources-v2.jsonl')
        self.assertEqual(len(r.families), 70)
        ref = self.source('fixture-new', 'New independent rule.')
        r.register_source(ref['manifest'], family_id='fixture-new-family',
                          evidence=self.evidence, reviewer='fixture', note='New system reviewed')
        self.assertEqual(r.resolve([ref])['primary_family_id'], 'fixture-new-family')
        self.assertEqual((sha256(self.root/CATALOG),sha256(self.root/SOURCES)),before)

    def test_catalog_extension_requires_new_version(self):
        with self.assertRaises(ValueError):
            self.registry.extend(self.proposal('sgb-family-v1'),'v1.json','v1.jsonl')

    def test_catalog_extension_cannot_replace_existing_definition(self):
        p = self.root/'proposal.json'
        create(p, {'classification_version':'sgb-family-v2','families':[BASE_CATALOG['families'][0]]})
        with self.assertRaises(ValueError): self.registry.extend(p,'v2.json','v2.jsonl')

    def test_catalog_extension_never_overwrites_files(self):
        p = self.proposal(); create(self.root/'v2.json',{})
        with self.assertRaises(FileExistsError): self.registry.extend(p,'v2.json','v2.jsonl')

    def test_runtime_missing_taxonomy_is_error(self):
        result = self.registry.resolve([self.a])
        with self.assertRaises(ValueError): self.registry.check_runtime(self.config,result)

    def test_runtime_profile_mismatch_is_error(self):
        result, config, _ = self.runtime(); config['pipeline']['profile_id']='wrong'
        with self.assertRaises(ValueError): self.registry.check_runtime(config,result)

    def test_runtime_empty_family_id_is_error(self):
        result, config, output = self.runtime()
        taxonomy = read(output['taxonomy_path']); taxonomy['family_candidates'][0]['id']=''
        Path(output['taxonomy_path']).write_text(json.dumps(taxonomy),encoding='utf-8')
        with self.assertRaises(ValueError): self.registry.check_runtime(config,result)

    def test_runtime_global_candidates_are_rejected(self):
        result, config, output = self.runtime()
        taxonomy = read(output['taxonomy_path'])
        taxonomy['family_candidates'].append({'id':'pydantic-validation','name':'Other'})
        Path(output['taxonomy_path']).write_text(json.dumps(taxonomy),encoding='utf-8')
        with self.assertRaises(ValueError): self.registry.check_runtime(config,result)

    def test_runtime_preserves_custom_taxonomy_non_family_fields(self):
        base = load_skill_taxonomy(domain_type='scrapy').to_dict()
        base['taxonomy_id']='fixture-custom'
        base['asset_types'][0]['label']='Fixture independent asset label'
        create(self.root/'custom.yaml',base)
        self.config['pipeline']['skill_taxonomy_path']=str(self.root/'custom.yaml')
        effective = load_skill_taxonomy(domain_type='scrapy',taxonomy_path=str(self.root/'custom.yaml')).to_dict()
        _,_,output = self.runtime(); actual = read(output['taxonomy_path'])
        for field in ('taxonomy_id','asset_types','asset_tree','domain_root','family_axis'):
            self.assertEqual(actual[field],effective[field])

    def test_default_control_retains_legacy_empty_id_only_explicitly(self):
        result = self.registry.resolve([self.a])
        out = self.registry.runtime(self.config,result,self.root/'control',mode='default-control')
        self.assertEqual(out['family_id'],'')
        self.assertEqual(out['family_name'],'未分类技能')
        with self.assertRaises(ValueError):
            self.registry.check_runtime(read(out['generation_config']),result,mode='classified')

    def test_pending_resolution_cannot_materialize(self):
        with self.assertRaises(ValueError):
            self.registry.runtime(self.config,self.registry.resolve([]),self.root/'blocked')
        self.assertFalse((self.root/'blocked').exists())

    def test_runtime_output_cannot_overwrite(self):
        self.runtime()
        with self.assertRaises(FileExistsError):
            self.registry.runtime(self.config,self.registry.resolve([self.a]),self.root/'runtime')

    def test_family_id_is_not_a_public_pipeline_argument(self):
        result,config,_ = self.runtime()
        config['pipeline']['family_id']='scrapy-framework'
        with self.assertRaises(ValueError): self.registry.check_runtime(config,result)

    def test_catalog_rename_requires_new_mapping_version(self):
        catalog=read(self.root/CATALOG)
        catalog['families'][0]['family_name']='Changed visible label in same version'
        (self.root/CATALOG).write_text(json.dumps(catalog),encoding='utf-8')
        with self.assertRaises(ValueError): FamilyRegistry(self.root)

    def test_new_task_registration_is_independent_of_sgb_snapshot(self):
        task=self.root/'T11.json'
        create(task,{'task_key':'T11-independent','sources':[self.a,self.b]})
        args=['b1_family.py','register-task','--task-json',str(task),'--output','T11.family.json']
        with patch('sys.argv',args),patch('sys.stdout',new_callable=io.StringIO):
            self.assertEqual(main(self.root),0)
        result=read(self.root/'T11.family.json')
        self.assertEqual(result['task_key'],'T11-independent')
        self.assertEqual(result['primary_family_id'],'scrapy-framework')
        self.assertEqual(len(result['source_set']),2)
        self.assertFalse((self.root/'data/manifests/sgb/tasks.jsonl').exists())

    def test_new_domain_can_be_added_with_new_version(self):
        family=copy.deepcopy(BASE_CATALOG['families'][0])
        family.update(domain_id='fixture-domain',family_id='fixture-family',
                      family_name='New fixture Family',aliases=[])
        proposal=self.root/'domain-proposal.json'
        create(proposal,{'classification_version':'sgb-family-v2',
                         'domains':[{'domain_id':'fixture-domain','domain_name':'Fixture Domain'}],
                         'families':[family]})
        self.registry.extend(proposal,'catalog-v2.json','sources-v2.jsonl')
        r=FamilyRegistry(self.root,catalog='catalog-v2.json',source_map='sources-v2.jsonl')
        self.assertEqual(len(r.catalog['domains']),15)


    def fixture_draft(self):
        _,_,out = self.runtime()
        expected = {k:out[k] for k in ('family_id','family_name','profile_id')}
        doc = DocumentRecord(doc_id='fixture-doc', source_type='fixture',title='Invented source',
                             domain='scrapy',raw_text='Fixture rule.',metadata=expected,
                             content_hash=hashlib.sha256(b'Fixture rule.').hexdigest())
        extractor = LLMDocumentSkillExtractor(llm=object(),llm_rate_limit_requests=0,
                                              taxonomy=load_skill_taxonomy(domain_type='scrapy',taxonomy_path=out['taxonomy_path']))
        support,draft = extractor._build_support_and_draft(record=doc,section_heading='Fixture',
            span=TextSpan(start=0,end=13),unit_text=doc.raw_text,unit_type='paragraph',
            item={'name':'Fixture skill','description':'Invented fixture only','prompt':'Perform the fixture step.',
                  'asset_type':'session_skill','workflow_steps':['Perform the fixture step.']})
        self.assertIsNotNone(draft)
        return doc,support,draft,expected

    def test_document_to_skilldraft_metadata_without_model(self):
        _,_,draft,expected = self.fixture_draft()
        self.assertEqual({k:draft.metadata[k] for k in expected},expected)

    def fixture_spec(self):
        doc,support,draft,expected = self.fixture_draft()
        compiler = LLMSkillCompiler(llm=object(),llm_rate_limit_requests=0)
        payload = {'skills':[{'name':'Fixture skill','description':'Invented fixture only',
                    'prompt':'Perform the fixture step.','asset_type':'session_skill',
                    'workflow_steps':['Perform the fixture step.'],'source_draft_ids':[draft.draft_id],
                    'support_ids':[support.support_id]}]}
        with patch('AutoSkill4Doc.stages.compiler.llm_complete_json_with_retries',return_value=payload):
            specs = compiler._compile_group(drafts=[draft],supports=[support],target_state=VersionState.DRAFT)
        self.assertEqual(len(specs),1)
        return doc,support,specs[0],expected

    def test_skilldraft_to_skillspec_metadata_without_model(self):
        _,_,spec,expected = self.fixture_spec()
        self.assertEqual({k:spec.metadata[k] for k in expected},expected)

    def test_metadata_is_present_before_first_reconcile(self):
        doc,support,spec,expected = self.fixture_spec()
        spec.metadata = {k:v for k,v in spec.metadata.items() if k not in expected}
        registry=MagicMock();registry.list_skills.return_value=[]
        class Intercept(Exception):pass
        def inspect_first(**kwargs):
            self.assertEqual({k:kwargs['skills'][0].metadata[k] for k in expected},expected)
            raise Intercept()
        with patch.object(versioning,'VersionManager') as manager, \
             patch.object(versioning,'build_document_skill_retriever',return_value=object()), \
             patch.object(versioning,'_store_root_from_context',return_value=str(self.root)), \
             patch.object(versioning,'build_llm',side_effect=AssertionError('No model construction')):
            manager.return_value.reconcile.side_effect=inspect_first
            with self.assertRaises(Intercept):
                versioning.register_versions(registry=registry,documents=[doc],support_records=[support],
                    skill_specs=[spec],llm=object(),metadata=expected,llm_rate_limit_requests=0)


if __name__ == '__main__':
    unittest.main()
