"""Full SGB archival layout and historical path compatibility, without model calls."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.artifacts import resolve_run,load_run
from degradation_lab.catalog import CaseManager
from degradation_lab.io import inside,read,sha256,write,resolve_upstream
from degradation_lab.relocations import MANIFEST,archived_path,historical_input,relocated


class SGBArchive(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='sgbarc-',dir=LAB.parent);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        guard=patch('socket.socket.connect',side_effect=AssertionError('No real network/model calls'))
        guard.start();self.addCleanup(guard.stop)

    def test_no_separate_scrapy_source_case_run_or_manifest_remains(self):
        for name in ['data/raw_sources/scrapy','data/manifests/sgb_scrapy024_feed_exports.json',
                     'data/manifests/sgb_scrapy024_provenance.json','cases/case024_scrapy',
                     'runs/case024_scrapy','runs/downstream/scrapy-task-024',
                     'results/analysis/s24m001','results/analysis/s24m002','results/analysis/s24m003',
                     'results/analysis/s24m005_partial_success_audit.md','results/analysis/scrapy_task024_downstream_readiness.md',
                     'docs/research/ANYTHING2SKILL_SKILLGENBENCH_AUDIT_2026-10-15']:
            self.assertFalse((LAB/name).exists(),name)

    def test_legacy_source_identity_belongs_to_sgb_and_uses_one_canonical_file(self):
        manager=CaseManager(LAB);bundle=manager.load('case024_scrapy')
        self.assertEqual(bundle['case']['dataset_id'],'skillgenbench')
        self.assertNotIn('skillgenbench_docs',manager.sources.datasets)
        old=manager.sources.sources['sgb-scrapy024-feed-exports']
        current=manager.sources.sources['sgb-94375f344c6a7754']
        self.assertEqual(old['local_path'],current['local_path'])
        self.assertEqual(old['classification'],'PUBLISHED_DATASET_SNAPSHOT')
        self.assertFalse(old['paper_snapshot_verified'])
        manager.condition(bundle,'clean')

    def test_old_relative_and_absolute_paths_resolve_to_unchanged_bytes(self):
        old='data/raw_sources/scrapy/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/feed-exports.md'
        canonical=inside(LAB,old)
        self.assertTrue(canonical.relative_to(LAB).as_posix().startswith('data/raw_sources/sgb/'))
        self.assertEqual(archived_path(LAB/old),canonical)
        self.assertEqual(sha256(canonical),'a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d')

    def test_old_run_ids_resolve_under_sgb_without_changing_registration(self):
        for rid in ['s24m001','s24m002','s24m003','s24m004','s24m005','s24r005']:
            identity,path=resolve_run(LAB,rid)
            self.assertEqual(identity['case_id'],'case024_scrapy')
            self.assertTrue(path.relative_to(LAB).as_posix().startswith('runs/gen/sgb/'))
        _,_,result,stages=load_run(LAB,'s24r005')
        self.assertEqual(result['status'],'completed')
        self.assertEqual(len(stages['register']['upserted_store_skills']),15)

    def test_relocation_rejects_root_escape_and_matches_whole_prefix(self):
        write(self.root/MANIFEST,{'paths':{'old':'new'}})
        self.assertEqual(relocated(self.root,self.root/'old/a'),self.root/'new/a')
        self.assertEqual(relocated(self.root,self.root/'older/a'),self.root/'older/a')
        write(self.root/MANIFEST,{'paths':{'old':'../escape'}})
        with self.assertRaisesRegex(ValueError,'escapes project'):inside(self.root,'old/a')
        with self.assertRaises(ValueError):inside(self.root,'../escape')

    def test_relocated_loader_retains_logical_path_and_exact_stat_signature(self):
        sys.path.insert(0,str(resolve_upstream(LAB)))
        from AutoSkill4Doc.document import file_loader
        from AutoSkill4Doc.pipeline import DocumentBuildPipeline
        logical=self.root/'old/inputs';physical=self.root/'new/inputs'
        physical.mkdir(parents=True);(physical/'sample.md').write_text('FIXTURE source only\n',encoding='utf-8')
        write(self.root/MANIFEST,{'paths':{'old':'new'}})
        native_loader=file_loader.load_file_units;native_signature=DocumentBuildPipeline._file_input_signature
        expected=native_signature(file_path=str(physical));expected['path']=str(logical)
        with historical_input(logical):
            units,path=file_loader.load_file_units(str(logical))
            self.assertEqual(path,str(logical));self.assertEqual(units[0]['source_file'],str(logical/'sample.md'))
            self.assertEqual(DocumentBuildPipeline._file_input_signature(file_path=str(logical)),expected)
        self.assertIs(file_loader.load_file_units,native_loader)
        self.assertIs(DocumentBuildPipeline._file_input_signature,native_signature)
        self.assertFalse(logical.exists())


if __name__=='__main__':unittest.main()
