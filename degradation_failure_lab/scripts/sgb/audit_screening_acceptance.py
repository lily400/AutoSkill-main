"""Zero-model positive/negative acceptance for the two audited pilot adapters."""
import importlib
import json
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read, write

output = LAB / 'results/sgb/audits' / sys.argv[1]
output.mkdir(parents=True, exist_ok=False)
reports = []
for task_id, module in [('scrapy-task-024', 'scrapy024'), ('fla_packet_cadence_scope_validator_002', 'fla')]:
    adapter = importlib.import_module('downstream_eval.sgb.task_adapters.audited.' + module)
    fixtures = read(LAB / 'tests/fixtures/sgb/audited' / task_id / 'candidates.json')
    for name, fixture in fixtures.items():
        source = output / task_id / (name + '.py')
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(fixture['source'], encoding='utf-8')
        result = adapter.score(source, output / task_id / name)
        good = (result['infra_ok'] and result['candidate_binding_verified']
                and result['task_result']['passed'] == fixture['passed']
                and set(result['failed_tests']) == set(fixture.get('failed', [])))
        reports.append({'task_id': task_id, 'fixture': name, 'passed': good, 'result': result})
        write(output / 'acceptance.json', {'reports': reports, 'model_calls': 0,
            'status': 'PASS' if len(reports) == 4 and all(r['passed'] for r in reports) else 'INCOMPLETE_OR_FAIL'})
        print(json.dumps({'task': task_id, 'fixture': name, 'accepted': good,
                          'tests': result['task_result'], 'error': result.get('error')}), flush=True)
        if not good:
            raise RuntimeError('Scorer acceptance failed')
