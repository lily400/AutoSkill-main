"""Isolated unchanged-oracle checks; no Agent or model requests."""
from pathlib import Path
import json
from unittest.mock import patch
from degradation_lab.io import read, write
from downstream_eval.sgb.pilot import load_binding, adapter_for

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent / 'json-acceptance'
rows = []
with patch('httpx.AsyncClient.send', side_effect=AssertionError('No model HTTP')), \
     patch('httpx.Client.send', side_effect=AssertionError('No model HTTP')):
    for task_id in ('monitoring_gap_brief_classifier_001', 'capacity_aware_edge_admission_controller_006'):
        config = load_binding(ROOT, task_id)
        adapter = adapter_for(ROOT, config)
        adapter.verify_assets()
        for name, fixture in read(ROOT / config['fixtures']).items():
            candidate = OUT / task_id / (name + '.py')
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text(fixture['source'])
            result = adapter.score(candidate, OUT / task_id / name)
            accepted = (result['infra_ok'] and result['candidate_binding_verified']
                and result['task_result']['tests'] == config['expected_oracle_tests']
                and result['task_result']['passed'] == fixture['passed']
                and set(result['failed_tests']) == set(fixture['failed']))
            rows.append(dict(task_id=task_id, fixture=name, accepted=accepted, result=result))
            print(json.dumps(dict(task_id=task_id,fixture=name,accepted=accepted,
                                 counts=result['task_result'])), flush=True)
write(OUT / 'acceptance.json', dict(model_calls=0, real_agent_outcome=False, rows=rows))
raise SystemExit(not all(r['accepted'] for r in rows))
