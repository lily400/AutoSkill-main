"""SGB Task-024 paths and launch guards; all subprocesses and model I/O are blocked."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.io import read,write
from degradation_lab.sgb import audit_registry
from downstream_eval.sgb.scrapy024 import TASK,calibration_output,scorer_module
from test_sgb import registry_fixture


class SGBLayout(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='sgblayout-',dir=LAB.parent if sys.platform=='win32' else None)
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        for name in ['socket.socket.connect','subprocess.run']:
            mock=patch(name,side_effect=AssertionError('No real subprocess/network/model calls'))
            mock.start();self.addCleanup(mock.stop)

    def test_active_adapter_and_all_scorer_bytes_are_inside_sgb(self):
        self.assertEqual(TASK,LAB/'downstream_eval/tasks/sgb/code_doc/scrapy-task-024')
        self.assertEqual(read(TASK/'adapter.json')['runner'],'downstream_eval.sgb.scrapy024')
        scorer_module()  # Verifies every frozen scorer asset after relocation.
        for old in ['downstream_eval/tasks/scrapy_task024_v1','downstream_eval/scrapy024.py',
                    'downstream_eval/integration/scrapy_agent.py','downstream_eval/sgb.py',
                    'scripts/scrapy024.py','scripts/Invoke-Scrapy024Calibration.ps1']:
            self.assertFalse((LAB/old).exists(),old)

    def test_new_output_is_namespaced_and_old_experiment_cannot_be_reused(self):
        self.assertEqual(calibration_output(self.root,'s24d002'),self.root/'runs/eval/sgb/scrapy-task-024/s24d002')
        (self.root/'runs/downstream/scrapy-task-024/s24d001').mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError,'Historical experiment ID'):
            calibration_output(self.root,'s24d001')
        for name in ['../escape','s24d001/child','s24d9999']:
            with self.assertRaises(ValueError):calibration_output(self.root,name)
        self.assertFalse((self.root/'runs/eval').exists())

    def test_completed_namespaced_batch_cannot_be_reused(self):
        output=self.root/'runs/eval/sgb/scrapy-task-024/s24d001'
        output.mkdir(parents=True);(output/'batch.started').write_text('FIXTURE',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'Historical experiment ID'):
            calibration_output(self.root,'s24d001')

    def test_host_launcher_uses_sgb_module_and_stops_before_old_batch_dispatch(self):
        path=LAB/'scripts/sgb/scrapy024.py'
        spec=importlib.util.spec_from_file_location('sgb_scrapy_launcher',path)
        launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
        self.assertEqual(launcher.LAB,LAB);self.assertEqual(launcher.TASK,TASK)
        with patch.object(sys,'argv',[str(path),'prepare','--experiment','s24d001']):
            with self.assertRaisesRegex(RuntimeError,'Historical experiment ID'):launcher.main()
        out=self.root/'runs/eval/sgb/scrapy-task-024/s24d002'
        write(out/'skills_manifest.json',{'fixture_only':True})
        with patch.object(launcher,'LAB',self.root),patch.object(sys,'argv',[str(path),'prepare','--experiment','s24d002']),\
             patch.object(launcher.subprocess,'run') as run:
            run.return_value.returncode=0
            self.assertEqual(launcher.main(),0)
            self.assertIn('downstream_eval.sgb.scrapy024',run.call_args.args[0])

    def test_audit_rejects_adapter_outside_its_sgb_task(self):
        import json
        from degradation_lab.io import sha256
        from degradation_lab.sgb import REGISTRY,CONFIG
        rows=registry_fixture(self.root)
        rows[0].update(existing_task_adapter='downstream_eval/tasks/standalone',
                       downstream_task_path='downstream_eval/tasks/sgb/code_repo/fixture-task-0')
        path=self.root/REGISTRY;path.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
        config=read(self.root/CONFIG);config['registry_sha256']=sha256(path);write(self.root/CONFIG,config)
        with self.assertRaisesRegex(ValueError,'outside its SGB task directory'):audit_registry(self.root)


if __name__=='__main__':unittest.main()
