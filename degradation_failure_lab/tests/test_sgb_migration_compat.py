"""SGB migration contracts; fixtures write only to external temporary directories.

KnownUnsupportedBoundaries reproduces two limitations, not compatibility successes.
Real Agent/Harbor transport, Oracle execution and isolation remain unverified.
Existing BS tests already cover the Agent initialization guard, fixture-only receipts,
NOT_IMPLEMENTED scoring, and exclusion of engineering records from success rates.
"""
import contextlib
import hashlib
import importlib
import inspect
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings

sys.dont_write_bytecode = True
LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src'), str(LAB / 'tests')]

import test_sgb as management_fixtures
from tests import test_sgb_beautifulsoup_smoke as smoke_fixtures
from degradation_lab.io import read, sha256, write
from degradation_lab.sgb import CONFIG, REGISTRY
import downstream_eval.sgb as sgb
from downstream_eval.sgb import management

OLD = 'downstream_eval.sgb.'
NEW = OLD + 'task_adapters.beautifulsoup037.'
MODULES = (
    ('beautifulsoup037', 'adapter'),
    ('beautifulsoup_scoring', 'scoring'),
    ('beautifulsoup_exports', 'exports'),
    ('beautifulsoup_smoke', 'smoke'),
)
MIGRATED_FILES = {
    'downstream_eval/sgb/' + old + '.py' for old, _ in MODULES
} | {
    'downstream_eval/sgb/task_adapters/__init__.py',
    'downstream_eval/sgb/task_adapters/beautifulsoup037/__init__.py',
} | {
    'downstream_eval/sgb/task_adapters/beautifulsoup037/' + new + '.py'
    for _, new in MODULES
}
PUBLIC_SIGNATURES = {
    'adapter': {
        'verify_assets':'(root)',
        'execution_config':'(task, profile)',
        'prepare':'(root, destination, *, profile, packages, agent_image, verifier_image, verifier_timeout_sec)',
        'validate_prepared':'(root, destination)',
        'scoring_plan':'(root, submission, output, *, image, timeout_sec, export_receipt=None, export_controller=None, trial_id=None)',
        'normalize_score':'(result, expected_tests)',
        'grade_export':'(root, trial, output, *, image, timeout_sec, execute=None, export_receipt=None, export_controller=None)',
        'task_success':'(score)',
    },
    'scoring': {
        'failure':'(category, reason)', 'regular_file':'(path, boundary)',
        'collect_export':'(artifacts, *, receipt=None, controller=None, trial_id=None)',
        'execute_scoring':'(plan)', 'inspect_result':'(plan, result, *, controller=None)',
        'behavior_plan':'(root)',
    },
    'exports': {
        'canonical':'(value)', 'digest':'(value)',
        'ExportController':'(root, artifacts, *, task_config, trial_id, fixture)',
        'ExportController.capture_fixture':'(self, *, manifest_entries, source_observation)',
        'ExportController.verify':'(self, receipt, *, artifacts, trial_id)',
        'ExportController.seal_result_fixture':'(self, result)',
        'ExportController.verify_result_fixture':'(self, result)',
    },
    'smoke': {
        'probe':'(root, prepared, output, *, task_id, runtime=False)',
        'main':'(argv=None)',
    },
}


class ExternalFixture(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='sgb-migration-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.assertFalse(self.root.resolve().is_relative_to(LAB.parent.resolve()))
        for name in ('socket.socket.connect', 'socket.socket.connect_ex',
                     'socket.getaddrinfo', 'subprocess.Popen'):
            guard = patch(name, side_effect=AssertionError('Offline migration test only'))
            guard.start()
            self.addCleanup(guard.stop)


class ManagementCompatibility(ExternalFixture):
    def test_public_exports_and_signatures(self):
        expected = {'plan':'(root, tasks=None)', 'prepare':'(root, tasks, preparation_id)',
                    'aggregate':'(root, tasks, analysis_id)'}
        for name, signature in expected.items():
            with self.subTest(name=name):
                self.assertIs(getattr(sgb, name), getattr(management, name))
                self.assertEqual(str(inspect.signature(getattr(sgb, name))), signature)

    def test_public_exception_contract(self):
        management_fixtures.registry_fixture(self.root)
        for module in (sgb, management):
            with self.subTest(module=module.__name__):
                with self.assertRaisesRegex(ValueError, 'Unknown SGB task'):
                    module.plan(self.root, ['missing-fixture-task'])
                with self.assertRaisesRegex(ValueError, '^Unsafe preparation ID$'):
                    module.prepare(self.root, None, '../escape')
                with self.assertRaisesRegex(ValueError, '^Unsafe analysis ID$'):
                    module.aggregate(self.root, None, '../escape')
        self.assertFalse((self.root / 'results').exists())

    def test_lab_script_dispatches_all_three_management_commands(self):
        management_fixtures.registry_fixture(self.root)
        for name, option, identity in (
                ('plan', None, None),
                ('prepare', '--preparation-id', 'fixture-preparation'),
                ('aggregate', '--analysis-id', 'fixture-analysis')):
            with self.subTest(command=name):
                argv = ['lab.py', '--root', str(self.root), 'sgb', name,
                        '--task', 'fixture-task-0']
                if option:
                    argv += [option, identity]
                buffer = io.BytesIO()
                with io.TextIOWrapper(buffer, encoding='utf-8', write_through=True) as output:
                    with patch.object(sys, 'argv', argv), patch.object(sys, 'path', sys.path.copy()), \
                         patch.object(sgb, name, wraps=getattr(management, name)) as dispatched, \
                         contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit:
                        runpy.run_path(str(LAB / 'scripts/lab.py'), run_name='__main__')
                    self.assertEqual(exit.exception.code, 0)
                    result = json.loads(buffer.getvalue().decode('utf-8'))
                args = (self.root.resolve(), ['fixture-task-0'])
                dispatched.assert_called_once_with(*(args + ((identity,) if option else ())))
                self.assertEqual((result['model_calls'], result['agent_runs']), (0, 0))
        self.assertEqual(read(self.root / 'results/sgb/audits/fixture-preparation/preparation.json')['scope'],
                         'METADATA_AND_INTEGRITY_ONLY')
        self.assertFalse((self.root / 'runs').exists())

    def test_linked_history_aggregate_keeps_trial_mean_and_integrity_checks(self):
        rows = management_fixtures.registry_fixture(self.root)
        history = self.root / 'fixture-history.json'
        write(history, {'results':[
            {'label':'pass', 'condition':'CleanSkill', 'task_success':True, 'infra_ok':True},
            {'label':'wrong', 'condition':'CleanSkill', 'task_success':False, 'infra_ok':True},
            {'label':'infra', 'condition':'CleanSkill', 'task_success':False, 'infra_ok':False},
        ]})
        rows[0]['legacy_runs'] = [{'path':history.name, 'sha256':sha256(history)}]
        registry = self.root / REGISTRY
        registry.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
        config = read(self.root / CONFIG)
        config['registry_sha256'] = sha256(registry)
        write(self.root / CONFIG, config)
        before = history.read_bytes()
        selected = ['fixture-task-0', 'fixture-task-1']
        old = sgb.aggregate(self.root, selected, 'fixture-legacy-entry')
        direct = management.aggregate(self.root, selected, 'fixture-direct-entry')
        self.assertEqual({k:v for k, v in old.items() if k != 'summary_path'},
                         {k:v for k, v in direct.items() if k != 'summary_path'})
        self.assertEqual(old['conditions']['CleanSkill'],
                         {'observed':3, 'passed':1, 'failed':1, 'unscorable':1,
                          'success_rate_among_scorable':0.5})
        self.assertEqual(old['tasks_without_observed_trials_count'], 1)
        for analysis in ('fixture-legacy-entry', 'fixture-direct-entry'):
            observed = read(self.root / 'results/sgb/analyses' / analysis / 'trials.json')
            self.assertEqual([r['outcome'] for r in observed], ['passed', 'failed', 'unscorable'])
            self.assertTrue(all(r['evidence'] == history.name for r in observed))
        self.assertEqual(history.read_bytes(), before)
        with self.assertRaises(FileExistsError):
            sgb.aggregate(self.root, selected, 'fixture-legacy-entry')
        with patch.object(management, 'sha256', return_value='0' * 64):
            with self.assertRaisesRegex(ValueError, '^Historical results changed$'):
                sgb.aggregate(self.root, selected, 'fixture-drift')
        self.assertFalse((self.root / 'results/sgb/analyses/fixture-drift').exists())


class BeautifulSoupMigration(unittest.TestCase):
    # Reuse fixture builders, not TestCase inheritance or imported TestCase names.
    setUp = smoke_fixtures.BeautifulSoupSmoke.setUp
    prepare = smoke_fixtures.BeautifulSoupSmoke.prepare
    export = smoke_fixtures.BeautifulSoupSmoke.export

    def test_all_old_modules_alias_canonical_implementations_and_paths(self):
        for old_name, new_name in MODULES:
            with self.subTest(module=old_name):
                old = importlib.import_module(OLD + old_name)
                new = importlib.import_module(NEW + new_name)
                self.assertIs(old, new)
                self.assertEqual(old.__spec__.name, NEW + new_name)
                self.assertEqual(Path(old.__file__).resolve(),
                                 LAB / 'downstream_eval/sgb/task_adapters/beautifulsoup037' / (new_name + '.py'))
                with patch.object(old, 'migration_fixture_attribute', object(), create=True):
                    self.assertIs(old.migration_fixture_attribute, new.migration_fixture_attribute)

    def test_public_functions_classes_and_defaults_remain_compatible(self):
        for old_name, new_name in MODULES:
            old = importlib.import_module(OLD + old_name)
            new = importlib.import_module(NEW + new_name)
            for name, expected in PUBLIC_SIGNATURES[new_name].items():
                with self.subTest(module=old_name, public_name=name):
                    left, right = old, new
                    for part in name.split('.'):
                        left, right = getattr(left, part), getattr(right, part)
                    self.assertIs(left, right)
                    self.assertEqual(str(inspect.signature(left)), expected)

    def test_old_module_monkeypatch_reaches_canonical_function_globals(self):
        adapter, scoring, exports, smoke = [
            importlib.import_module(OLD + old_name) for old_name, _ in MODULES]
        with patch.object(adapter, 'read', side_effect=RuntimeError('fixture read')) as reader:
            with self.assertRaisesRegex(RuntimeError, '^fixture read$'):
                importlib.import_module(NEW + 'adapter').verify_assets(self.root)
        reader.assert_called_once_with(self.root / adapter.MAPPING)
        marker = {'fixture_only':True}
        with patch.object(scoring, 'failure', return_value=marker) as failure:
            result = importlib.import_module(NEW + 'scoring').collect_export(self.root / 'absent')
        self.assertIs(result[1], marker)
        failure.assert_called_once_with('submission_origin_unknown', 'artifact_evidence_invalid')
        with patch.object(exports, 'canonical', return_value=b'fixture canonical') as canonical:
            self.assertEqual(importlib.import_module(NEW + 'exports').digest({}),
                             hashlib.sha256(b'fixture canonical').hexdigest())
        canonical.assert_called_once_with({})
        with patch.object(smoke, 'probe', return_value={
                'run_kind':'runtime_smoke', 'execution_status':'NOT_RUN'}) as probe, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(importlib.import_module(NEW + 'smoke').main([
                '--root', str(LAB), '--prepared', str(self.output),
                '--output', str(self.root / 'engineering'), '--task-id', adapter.TASK_ID]), 0)
        probe.assert_called_once_with(LAB, self.output, self.root / 'engineering', task_id=adapter.TASK_ID)

    def test_reload_each_old_alias_keeps_canonical_module_identity(self):
        modules = [(OLD + old, NEW + new, importlib.import_module(OLD + old))
                   for old, new in MODULES]
        snapshots = [(module, module.__dict__.copy()) for _, _, module in modules]
        try:
            for old_name, new_name, module in modules:
                with self.subTest(module=old_name):
                    self.assertIs(importlib.reload(module), module)
                    self.assertIs(importlib.import_module(old_name), module)
                    self.assertIs(importlib.import_module(new_name), module)
        finally:
            # Reload creates new class objects; restore globals so other tests'
            # already-imported ExportController references are not made stale.
            for module, snapshot in snapshots:
                module.__dict__.clear()
                module.__dict__.update(snapshot)

    def test_old_smoke_command_cold_resolution_calls_canonical_static_probe(self):
        self.prepare()
        smoke = importlib.import_module(NEW + 'smoke')
        old_name = OLD + 'beautifulsoup_smoke'
        imported = importlib.import_module(old_name)
        argv = [old_name, '--root', str(LAB), '--prepared', str(self.output),
                '--output', str(self.root / 'engineering'), '--task-id', smoke.bs.TASK_ID]
        # Emulate cold command resolution; warm runpy is explicitly unsupported below.
        del sys.modules[old_name]
        try:
            with patch.object(sys, 'argv', argv), patch.object(smoke, 'probe', wraps=smoke.probe) as probe, \
                 contextlib.redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as exit:
                runpy.run_module(old_name, run_name='__main__')
            self.assertEqual(exit.exception.code, 0)
            probe.assert_called_once_with(LAB, self.output, self.root / 'engineering', task_id=smoke.bs.TASK_ID)
            self.assertEqual(json.loads(output.getvalue())['execution_status'], 'NOT_RUN')
            record = read(self.root / 'engineering/smoke.json')
            self.assertFalse(record['real_agent_outcome'])
            self.assertIsNone(record['task_success'])
        finally:
            sys.modules[old_name] = imported

    def test_smoke_code_identity_covers_new_code_shims_and_package_markers(self):
        self.prepare()
        smoke = importlib.import_module(NEW + 'smoke')
        record = smoke.probe(LAB, self.output, self.root / 'engineering', task_id=smoke.bs.TASK_ID)
        files = record['code_version']['files']
        self.assertTrue(MIGRATED_FILES <= files.keys())
        for name in MIGRATED_FILES:
            with self.subTest(path=name):
                self.assertEqual(files[name], sha256(LAB / name))

    def test_fixture_receipt_identity_covers_ten_migration_files(self):
        _, _, receipt = self.export()
        files = receipt['code_version']
        for name in MIGRATED_FILES:
            with self.subTest(path=name):
                self.assertEqual(files[str(LAB / name)], sha256(LAB / name))
        self.assertEqual(receipt['evidence_kind'], 'offline_fixture')
        self.assertEqual(receipt['export_source']['observation'], 'synthetic_fixture')

    def test_simulated_implementation_hash_drift_invalidates_fixture_receipt(self):
        artifacts, _, receipt = self.export()
        exports = importlib.import_module(NEW + 'exports')
        original_sha256 = exports.sha256
        self.assertTrue(self.controller.verify(receipt, artifacts=artifacts, trial_id=self.trial_id))
        for _, implementation in MODULES:
            changed = (LAB / 'downstream_eval/sgb/task_adapters/beautifulsoup037' /
                       (implementation + '.py')).resolve()
            def changed_hash(path):
                return '0' * 64 if Path(path).resolve() == changed else original_sha256(path)
            with self.subTest(implementation=implementation), patch.object(exports, 'sha256', side_effect=changed_hash):
                self.assertFalse(self.controller.verify(receipt, artifacts=artifacts, trial_id=self.trial_id))
        self.assertTrue(self.controller.verify(receipt, artifacts=artifacts, trial_id=self.trial_id))


class PydanticMigration(ExternalFixture):
    def setUp(self):
        super().setUp()
        self.old_name = OLD + 'pydantic001'
        self.new_name = OLD + 'task_adapters.pydantic001.demo'
        self.old = importlib.import_module(self.old_name)
        self.demo = importlib.import_module(self.new_name)

    def test_alias_public_signatures_and_module_attributes(self):
        self.assertIs(self.old, self.demo)
        self.assertEqual(self.old.__spec__.name, self.new_name)
        self.assertEqual(self.old.CASE_ID, 'case001_pyd')
        self.assertEqual(self.old.TASK_PATH, 'downstream_eval/tasks/sgb/code_doc/pydantic-task-001')
        for name, signature in {'verify_assets':'(root)', 'score':'(root, submission, output)',
                                'demonstrate':'(root, audit_id)', 'main':'()'}.items():
            with self.subTest(name=name):
                self.assertIs(getattr(self.old, name), getattr(self.demo, name))
                self.assertEqual(str(inspect.signature(getattr(self.old, name))), signature)
                self.assertIs(getattr(self.old, name).__globals__, self.demo.__dict__)
        with patch.object(self.old, 'CASE_ID', 'fixture-case'):
            self.assertEqual(self.demo.CASE_ID, 'fixture-case')

    def test_old_module_monkeypatch_reaches_implementation_globals(self):
        with patch.object(self.old, 'read', side_effect=ValueError('fixture read refusal')) as reader:
            with self.assertRaisesRegex(ValueError, '^fixture read refusal$'):
                self.demo.verify_assets(self.root)
        reader.assert_called_once_with(self.root / self.old.TASK_PATH / 'asset_manifest.json')

    def test_reload_old_module_preserves_alias_without_polluting_other_tests(self):
        snapshot = self.demo.__dict__.copy()
        try:
            self.assertIs(importlib.reload(self.old), self.demo)
            self.assertIs(importlib.import_module(self.old_name), self.demo)
            self.assertIs(importlib.import_module(self.new_name), self.demo)
            self.assertEqual(self.demo.LAB, LAB)
        finally:
            # Keep previously imported function references valid in the same test process.
            self.demo.__dict__.clear()
            self.demo.__dict__.update(snapshot)

    def test_root_task_and_frozen_assets_resolve_independently_of_cwd(self):
        self.assertEqual(Path(self.demo.__file__).resolve(),
                         LAB / 'downstream_eval/sgb/task_adapters/pydantic001/demo.py')
        self.assertEqual(self.demo.LAB, LAB)
        with contextlib.chdir(self.root):
            task, row = self.old.verify_assets(self.demo.LAB)
        self.assertEqual(task, LAB / self.demo.TASK_PATH)
        self.assertEqual(row['original_task_id'], 'pydantic-task-001')
        self.assertEqual(row['generation_case_id'], self.demo.CASE_ID)
        manifest = read(task / 'asset_manifest.json')
        self.assertEqual(sha256(task / 'asset_manifest.json'),
                         '8ec59c3ddef9f4469c120b5c79b17945046fdd7e01a93d0912b411baac86e4e1')
        for name, digest in manifest['files'].items():
            with self.subTest(asset=name):
                self.assertEqual(sha256(task / name), digest)

    def test_asset_hash_drift_is_refused_before_any_scoring(self):
        task = LAB / self.demo.TASK_PATH
        original_sha256 = self.demo.sha256
        for name in read(task / 'asset_manifest.json')['files']:
            changed = (task / name).resolve()
            def changed_hash(path):
                return '0' * 64 if Path(path).resolve() == changed else original_sha256(path)
            with self.subTest(asset=name), patch.object(self.old, 'sha256', side_effect=changed_hash), \
                 patch.object(self.demo, 'score', side_effect=AssertionError('No scoring')) as scorer:
                with self.assertRaises(ValueError) as error:
                    self.demo.verify_assets(LAB)
                self.assertEqual(str(error.exception), 'Task asset drift: ' + name)
                scorer.assert_not_called()

    def test_existing_script_dispatches_main_without_running_demo_or_score(self):
        for status, code in (('PASS', 0), ('FAIL', 2)):
            with self.subTest(status=status), patch.object(sys, 'argv', [
                    'pydantic001.py', '--audit-id', 'fixture-cli']), \
                 patch.object(sys, 'path', sys.path.copy()), \
                 patch.object(self.old, 'demonstrate', return_value={
                     'status':status, 'model_calls':0}) as demonstrate, \
                 patch.object(self.demo, 'score', side_effect=AssertionError('No scorer')) as scorer, \
                 contextlib.redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as exit:
                runpy.run_path(str(LAB / 'scripts/sgb/pydantic001.py'), run_name='__main__')
            self.assertEqual(exit.exception.code, code)
            demonstrate.assert_called_once_with(LAB, 'fixture-cli')
            scorer.assert_not_called()
            self.assertEqual(json.loads(output.getvalue()), {'status':status, 'model_calls':0})

    def test_old_module_cold_command_forwards_to_canonical_main(self):
        # As with the BS smoke shim, cold command resolution is distinct from warm runpy.
        del sys.modules[self.old_name]
        try:
            with patch.object(self.demo, 'main', return_value=0) as main, \
                 self.assertRaises(SystemExit) as exit:
                runpy.run_module(self.old_name, run_name='__main__')
            self.assertEqual(exit.exception.code, 0)
            main.assert_called_once_with()
        finally:
            sys.modules[self.old_name] = self.old


class KnownUnsupportedBoundaries(ExternalFixture):
    """Passing here means a documented limitation was reproduced, not supported."""

    def test_warm_runpy_old_smoke_name_has_loader_error(self):
        old_name = OLD + 'beautifulsoup_smoke'
        module = importlib.import_module(old_name)
        with warnings.catch_warnings(record=True) as observed:
            warnings.simplefilter('always', RuntimeWarning)
            with self.assertRaisesRegex(ImportError, 'cannot handle'):
                runpy.run_module(old_name, run_name='__main__')
        self.assertTrue(any(old_name in str(w.message) for w in observed))
        self.assertIs(sys.modules[old_name], module)

    def test_package_plan_patch_does_not_replace_management_prepare_global(self):
        management_fixtures.registry_fixture(self.root)
        with patch.object(sgb, 'plan', side_effect=AssertionError('Unsupported package-level interception')) as package, \
             patch.object(management, 'plan', wraps=management.plan) as implementation:
            sgb.prepare(self.root, ['fixture-task-0'], 'fixture-known-boundary')
        package.assert_not_called()
        implementation.assert_called_once_with(self.root, ['fixture-task-0'])


if __name__ == '__main__':
    unittest.main()
