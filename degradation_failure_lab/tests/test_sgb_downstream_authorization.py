"""Zero-model grants and preparation; all mutations use temporary fixtures."""
from contextlib import closing, redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read, write, sha256, inventory
from downstream_eval.sgb import downstream_authorization as auth, pilot, runner
from downstream_eval.integration.request_budget import BudgetStop, Ledger


class DownstreamAuthorization(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='sgb-authorization-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name in ('socket.socket.connect', 'socket.socket.connect_ex', 'socket.getaddrinfo', 'subprocess.Popen'):
            guard = patch(name, side_effect=AssertionError('No network, model or real subprocess'))
            guard.start(); self.addCleanup(guard.stop)
        self.task = {'schema_version': 1, 'task_id': 'fixture-task', 'case_id': 'fixture-case',
                     'adapter': auth.ADAPTER, 'conditions': auth.CONDITIONS,
                     'task_path': 'downstream_eval/tasks/sgb/audited/fixture-task',
                     'runtime_lock': 'runtime.json', 'profile_template': 'downstream_eval/configs/p1_smoke.json',
                     'approval_environment_variable': 'SGB_AUDIT_ALLOW_PAID',
                     'json_observation': {'setup_code': 'import re'},
                     'freeze_files': ['gate.json']}
        self.gate = {'task_id': 'fixture-task', 'status': 'PASS', 'authorization_contract': 'exact-generation-v1',
                     'requested_generation': {'authorization_status': 'AUTHORIZED', 'run_id': 'g1'},
                     'downstream': {'experiment_id': 'old-paid'}}
        write(self.root / 'gate.json', self.gate)
        write(self.root / 'cases/sgb/fixture-case/case.json', {'case_id': 'fixture-case', 'execution_gate': 'gate.json'})
        write(self.root / 'configs/tasks/sgb/fixture-task.json', self.task)
        row = {'original_task_id': 'fixture-task', 'pilot_config': {
            'path': 'configs/tasks/sgb/fixture-task.json',
            'sha256': sha256(self.root / 'configs/tasks/sgb/fixture-task.json')}}
        (self.root / 'registry.jsonl').write_text(json.dumps(row) + '\n', encoding='utf-8')
        write(self.root / 'configs/datasets/sgb.json', {'registry': 'registry.jsonl',
                                                     'registry_sha256': sha256(self.root / 'registry.jsonl')})
        generation = self.root / 'runs/gen/sgb/fixture-case/clean/g1'
        write(generation / 'official_result.json', {'status': 'completed', 'errors': []})
        write(generation / 'invocation.json', {'run_id': 'g1', 'case_id': 'fixture-case', 'condition_id': 'clean',
              'execution_kind': 'official', 'real_generation': True})
        for name in ('configs/sgb/clean_pair_protocol.json', self.task['profile_template'],
                     'downstream_eval/sgb/clean_skill_read.md'):
            target = self.root / name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((LAB / name).read_bytes())
        self.old = self.output('old-paid'); self.old.mkdir(parents=True)
        (self.old / 'batch.started').write_text('Never restart')
        (self.old / 'budget.sqlite3').write_bytes(b'untouched historical ledger')
        self.history = inventory(self.old)
        spec = importlib.util.spec_from_file_location('authorization_cli_fixture', LAB / 'scripts/sgb/authorize_downstream.py')
        self.cli = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.cli)

    def output(self, experiment='new-pair'):
        return self.root / 'runs/eval/sgb/fixture-task' / experiment

    def cli_call(self, experiment='new-pair', approve=True):
        args = ['authorize_downstream.py', '--task', 'fixture-task', '--generator-run', 'g1', '--experiment', experiment]
        if approve:
            args.append('--approve')
        with patch.object(self.cli, 'ROOT', self.root), patch.object(sys, 'argv', args), redirect_stdout(io.StringIO()) as stdout:
            self.cli.main()
        return stdout.getvalue()

    def prepare(self, experiment='new-pair'):
        runtime = {'agent_image_id': 'sha256:agent', 'scorer_image_id': 'sha256:scorer'}
        write(self.root / self.task['runtime_lock'], runtime)
        for name in ('downstream_eval/p1.py', 'downstream_eval/scoring/results.py', 'scripts/sgb/pilot.py',
                     'scripts/sgb/Invoke-Pilot.ps1', 'configs/downstream_runtime.json',
                     'downstream_eval/configs/runner.lock.json', 'data/manifests/sgb/tasks.jsonl',
                     'scripts/sgb/authorize_downstream.py'):
            p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text('fixture')
        (self.root / self.task['task_path']).mkdir(parents=True, exist_ok=True)

        def execution(output, generator, conditions):
            return runner.ExecutionConfig(task_id='fixture-task', task_path=self.root / self.task['task_path'],
                experiment_id=Path(output).name, generator_run_id=generator,
                budget_scope='fixture-task/g1/' + Path(output).name, agent_import_path='fixture:NeverRun',
                trial_prefix='audit-', conditions=conditions, skill_conditions=('CleanSkill',), unscorable_categories=())

        def configure(output, label, mode, config):
            raw = runner.trial_config(output, label, mode, config)
            raw['extra_instruction_paths'] = [str(self.root / 'downstream_eval/sgb/clean_skill_read.md')]
            return SimpleNamespace(trial_name=raw['trial_name'], model_dump=lambda **kwargs: raw)

        def freeze(root, generator, output, **kwargs):
            (output / 'skills').mkdir(parents=True)
            return {}

        adapter = SimpleNamespace(verify_assets=Mock(), execution_config=execution, configure=configure,
                                  native_trial=Mock(), grade_export=Mock(), paid_batch=Mock())
        versions = {'harbor': '0.24.0', 'litellm': '1.93.0', 'openai': '2.24.0', 'httpx': '0.28.1'}
        with patch.object(pilot, 'adapter_for', return_value=adapter), \
             patch('downstream_eval.integration.harbor_adapter.verify_sources', return_value=(None, {'harbor_version': '0.24.0'})), \
             patch.object(pilot.importlib.metadata, 'version', side_effect=versions.__getitem__), \
             patch.object(pilot.subprocess, 'run', side_effect=lambda args, **kwargs: SimpleNamespace(stdout=args[3])), \
             patch.object(pilot, 'freeze_generation', side_effect=freeze), \
             patch.object(pilot, '_probe', return_value=[{'status': 'PASS', 'model_calls': 0}]) as probe:
            result = pilot.prepare(self.root, self.task, 'g1', experiment)
        self.assertEqual(probe.call_count, 1)
        adapter.native_trial.assert_not_called(); adapter.paid_batch.assert_not_called()
        return result

    def test_cli_preview_and_independent_grants_preserve_history_and_gate(self):
        before = inventory(self.root)
        self.assertIn('PREVIEW_ONLY', self.cli_call(approve=False))
        self.assertEqual(inventory(self.root), before)
        self.cli_call(); self.cli_call('second-pair')
        a = auth.authorization_path(self.root, 'fixture-task', 'new-pair')
        digest = sha256(a)
        self.assertIn('ALREADY_AUTHORIZED', self.cli_call())
        self.assertEqual(sha256(a), digest)
        self.assertEqual(read(self.root / 'gate.json'), self.gate)
        self.assertEqual(inventory(self.old), self.history)
        self.assertTrue(auth.authorization_path(self.root, 'fixture-task', 'second-pair').is_file())

    def test_existing_paid_and_prepared_experiments_cannot_be_reauthorized_or_restarted(self):
        for experiment in ('old-paid', 'legacy-prepared'):
            output = self.output(experiment); output.mkdir(parents=True, exist_ok=True)
            (output / 'budget.sqlite3').write_bytes(b'untouched historical ledger')
            before = inventory(output)
            with self.assertRaisesRegex(RuntimeError, 'NEW ID'):
                self.cli_call(experiment)
            with self.assertRaisesRegex(RuntimeError, 'never be reset'):
                pilot.prepare(self.root, self.task, 'g1', experiment)
            self.assertEqual(inventory(output), before)
        with self.assertRaisesRegex(RuntimeError, 'already started'):
            pilot.run(self.root, self.task, 'old-paid')
        self.assertEqual(inventory(self.old), self.history)

    def test_grant_mismatches_are_rejected_without_overwriting(self):
        self.cli_call(); path = auth.authorization_path(self.root, 'fixture-task', 'new-pair'); original = path.read_bytes()
        for field, value in [('task_id', 'another-task'), ('generator_run_id', 'g2'), ('experiment_id', 'another'),
                             ('task_config_sha256', '0' * 64), ('per_arm_http_limit', 7), ('max_http_calls', 13),
                             ('max_http_calls', 12.0), ('conditions', {})]:
            with self.subTest(field=field, value=value):
                data = json.loads(original); data[field] = value; write(path, data); digest = sha256(path)
                with self.assertRaisesRegex(RuntimeError, 'grant identity'):
                    self.cli_call()
                self.assertEqual(sha256(path), digest)
        path.write_bytes(original)

    def test_missing_grant_blocks_prepare_before_any_runtime_or_output(self):
        with patch.object(pilot, 'adapter_for', side_effect=AssertionError('Authorization must be checked first')):
            with self.assertRaisesRegex(RuntimeError, 'missing or invalid'):
                pilot.prepare(self.root, self.task, 'g1', 'never-approved')
        self.assertFalse(self.output('never-approved').exists())

    def test_authorized_prepare_freezes_grant_and_creates_only_fresh_budget(self):
        self.cli_call(); result = self.prepare(); output = self.output()
        self.assertEqual((result['status'], result['model_calls']), ('READY', 0))
        profile = auth.validate_prepared(self.root, self.task, output)
        reference = profile['downstream_authorization']; manifest = read(output / 'execution_manifest.json')
        self.assertEqual((output / 'authorization.json').read_bytes(), (self.root / reference['path']).read_bytes())
        self.assertEqual(manifest[reference['path']], reference['sha256'])
        self.assertEqual(manifest[(output / 'authorization.json').relative_to(self.root).as_posix()], reference['sha256'])
        with closing(sqlite3.connect((output / 'budget.sqlite3').as_uri() + '?mode=ro', uri=True)) as db:
            policy = json.loads(db.execute('SELECT data FROM policy').fetchone()[0])
            self.assertEqual((policy['per_trial_limit'], policy['global_limit']), (6, 12))
            self.assertEqual(policy['budget']['num_retries'], 0)
            self.assertEqual(db.execute('SELECT count(*) FROM attempts').fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM arms WHERE state='NEW'").fetchone()[0], 2)
        digest = sha256(output / 'budget.sqlite3')
        with self.assertRaisesRegex(RuntimeError, 'never be reset'):
            pilot.prepare(self.root, self.task, 'g1', 'new-pair')
        self.assertEqual(sha256(output / 'budget.sqlite3'), digest)
        self.assertEqual(inventory(self.old), self.history)

    def test_run_validation_uses_experiment_grant_and_rejects_tampering(self):
        self.cli_call(); self.prepare(); output = self.output()
        if sys.platform == 'win32':
            # The Linux scorer is imported but never executed by this authorization test.
            with patch.dict(sys.modules, {'resource': Mock()}):
                from downstream_eval.sgb.task_adapters.audited import json_task
        else:
            from downstream_eval.sgb.task_adapters.audited import json_task
        paid = Mock()
        with patch.object(json_task, 'bind', return_value=(None, None, None, paid)):
            adapter = json_task.for_task(self.root, self.task)
        adapter.paid_batch(output); paid.assert_called_once_with(output); paid.reset_mock()
        snapshot = output / 'authorization.json'; original = snapshot.read_bytes()
        snapshot.write_bytes(b'{}')
        with self.assertRaisesRegex(RuntimeError, 'frozen evidence'):
            adapter.paid_batch(output)
        paid.assert_not_called(); snapshot.write_bytes(original)
        path = auth.authorization_path(self.root, 'fixture-task', 'new-pair'); original = path.read_bytes()
        value = json.loads(original); value['authorized_at'] = 'modified'; write(path, value)
        with self.assertRaisesRegex(RuntimeError, 'profile differs'):
            adapter.paid_batch(output)
        paid.assert_not_called(); path.write_bytes(original)
        for field, value in [('task_id', 'wrong'), ('generator_run_id', 'wrong'), ('experiment_id', 'wrong'),
                             ('task_config_sha256', '0' * 64)]:
            original = read(output / 'profile.json'); changed = deepcopy(original); changed[field] = value
            write(output / 'profile.json', changed)
            with self.assertRaises(RuntimeError): adapter.paid_batch(output)
            paid.assert_not_called(); write(output / 'profile.json', original)
        manifest = read(output / 'execution_manifest.json'); manifest.pop(str(path.relative_to(self.root)).replace('\\', '/'))
        write(output / 'execution_manifest.json', manifest)
        with self.assertRaisesRegex(RuntimeError, 'frozen evidence'): adapter.paid_batch(output)
        paid.assert_not_called()

    def test_six_per_arm_twelve_global_and_no_budget_recreation(self):
        self.cli_call(); self.prepare(); ledger = Ledger(self.output() / 'budget.sqlite3')
        usage = SimpleNamespace(prompt_tokens=1, cache_tokens=0, completion_tokens=1)
        for arm in ('NoSkill1', 'CleanSkill1'):
            trial = 'audit-' + arm.lower(); lease = ledger.begin(arm, trial); ledger.attach(arm, trial, lease)
            for _ in range(6):
                number = ledger.reserve(arm, trial, lease, 1); ledger.headers(number, 200); ledger.response(number, usage)
            with self.assertRaises(BudgetStop): ledger.reserve(arm, trial, lease, 1)
            ledger.finish(arm, trial, lease, {'infra_ok': True, 'task_success': True, 'skill_read': False})
        snapshot = ledger.snapshot()
        self.assertEqual(snapshot['counts'], {'NoSkill1': 6, 'CleanSkill1': 6})
        self.assertEqual(snapshot['global_reserved_attempts'], 12)
        with self.assertRaises(FileExistsError): Ledger.create(ledger.path, {})
        with self.assertRaises(BudgetStop): ledger.begin('NoSkill1', 'audit-noskill1')


if __name__ == '__main__':
    unittest.main()
