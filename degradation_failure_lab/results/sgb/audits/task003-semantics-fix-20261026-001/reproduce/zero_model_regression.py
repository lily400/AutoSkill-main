"""Audit-only reproducible unittest harness; no real model or Agent execution."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument('--platform', choices=['linux','windows'], required=True)
args = parser.parse_args()
root = Path(r'D:\AS\AutoSkill-main\degradation_failure_lab' if args.platform=='windows'
            else '/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab')
sys.path[:0] = [str(root/'tests'),str(root),str(root/'src')]
os.environ['LITELLM_LOCAL_MODEL_COST_MAP']='True'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
selectors = (['test_sgb_sanctuary002.py','test_pilot_workflow.py','test_sgb_runner.py',
              'test_request_budget.py','test_network_isolation.py','test_sgb_task_contract.py',
              'test_framework.Framework.test_new_run_evaluation_contract'] if args.platform=='linux'
             else ['test_attribution.py','test_skill_usage.py','test_skill_freeze.py'])
rows = []
with tempfile.TemporaryDirectory(prefix='task003-test-source-') as directory:
    source = Path(directory)
    for name in ('AutoSkill4Doc/pipeline.py','autoskill/__init__.py'):
        path = source/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('# TEST ONLY: source shape for fixture=True; no generation code\n')
    with patch.dict(os.environ,{'ANYTHING2SKILL_SOURCE':str(source)}), \
         patch('socket.socket.connect', side_effect=AssertionError('Real network forbidden')), \
         patch('socket.getaddrinfo', side_effect=AssertionError('Real DNS forbidden')):
        for selector in selectors:
            log = io.StringIO()
            with redirect_stdout(log), redirect_stderr(log):
                suite = (unittest.defaultTestLoader.discover(str(root/'tests'),pattern=selector)
                         if selector.endswith('.py') else unittest.defaultTestLoader.loadTestsFromName(selector))
                result = unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
            rows.append(dict(suite=selector,tests=result.testsRun,success=result.wasSuccessful(),
                             failures=len(result.failures),errors=len(result.errors),
                             skipped=len(result.skipped),log=log.getvalue()))
value = dict(platform=args.platform,root=str(root),python=sys.version,selectors=selectors,
             tests=sum(r['tests'] for r in rows),success=all(r['success'] for r in rows),
             model_calls=0,real_agent_runs=0,formal_ledgers_modified=0,suites=rows)
print(json.dumps(value,ensure_ascii=False))
raise SystemExit(0 if value['success'] else 1)
