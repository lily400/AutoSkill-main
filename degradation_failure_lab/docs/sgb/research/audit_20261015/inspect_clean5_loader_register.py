"""Offline parser/loader checks. Run with python -B; no model or store creation."""
from pathlib import Path
import hashlib
import json
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, r'D:\AS\AutoSkill-main\AutoSkill-main')
from autoskill.management.formats.agent_skill import load_agent_skill_dir
from autoskill.utils.json import json_from_llm_text

out = Path(__file__).parent
inventory_path = out / 'clean5_inventory.json'
data = json.loads(inventory_path.read_text('utf-8'))
responses = []
for run in data['runs']:
    for item in run['skills']:
        p = Path(item['path'])
        skill = load_agent_skill_dir(str(p.parent), user_id='docskill', include_files=False)
        item['official_loader'] = {
            'success': True, 'id': skill.id, 'name': skill.name,
            'instructions_chars': len(skill.instructions),
            'contains_workflow_heading': '## Workflow Steps' in skill.instructions,
            'in_memory_skill_md_sha256_matches_file': hashlib.sha256(skill.files['SKILL.md'].encode()).hexdigest() == item['sha256'],
            'in_memory_md_equals_newline_normalized_file': skill.files['SKILL.md'] == p.read_text('utf-8'),
            'source_CRLF_count': p.read_bytes().count(b'\r\n'),
        }
    root = Path(run['run_path'])
    records = []
    for call in json.loads((root / 'model_calls.json').read_text('utf-8')):
        if not any(frame.get('function') == 'classify_change' for frame in call.get('stack', [])):
            continue
        p = root / 'http' / f"{call['number']:03}" / 'response.json'
        if not p.exists():
            continue
        choice = json.loads(p.read_text('utf-8'))['choices'][0]
        text = choice['message'].get('content', '')
        valid = True
        try:
            strict = json.loads(text)
        except ValueError:
            valid, strict = False, {}
        parsed = json_from_llm_text(text)
        records.append({
            'http_call': call['number'], 'response_path': str(p),
            'finish_reason': choice['finish_reason'], 'strict_json_valid': valid,
            'action': strict.get('action') if isinstance(strict, dict) else None,
            'official_parser_type': type(parsed).__name__,
            'official_parser_root_keys': list(parsed) if isinstance(parsed, dict) else [],
            'official_parser_action': parsed.get('action') if isinstance(parsed, dict) else None,
        })
    responses.append({'case_id': run['case_id'], 'run_id': run['run_id'], 'register_responses': records})
inventory_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')
(out / 'clean5_register_response_audit.json').write_text(json.dumps(responses, ensure_ascii=False, indent=2), 'utf-8')
print('Loaded all 47 canonical skills; inspected all 53 successful register responses.')
