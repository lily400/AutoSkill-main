"""Task003 asset audit, isolated fixture acceptance and quality/authorization checks. No model calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read, sha256, write
from downstream_eval.sgb import pilot


def history(audit_id, create=False):
    if not audit_id or not pilot.runner._identifier(audit_id):
        raise ValueError('A safe --audit-id is required')
    output = LAB / 'results/sgb/audits' / audit_id
    path = output / 'history.json'
    if create:
        output.mkdir(parents=True, exist_ok=False)
        files = {p.relative_to(LAB).as_posix(): {'sha256': sha256(p), 'bytes': p.stat().st_size}
                 for directory in ('runs', 'results', 'evaluations') for p in (LAB / directory).rglob('*')
                 if p.is_file() and not p.is_relative_to(output) and '__pycache__' not in p.parts}
        write(path, {'files': files, 'append_only': ['results/run_index.jsonl']})
        return {'status': 'SNAPSHOT', 'files': len(files), 'path': str(path), 'model_calls': 0}
    baseline = read(path)
    changed = []
    for name, expected in baseline['files'].items():
        p = LAB / name
        if not p.is_file():
            changed.append(name)
        elif name in baseline['append_only']:
            with p.open('rb') as stream:
                prefix = stream.read(expected['bytes'])
            if hashlib.sha256(prefix).hexdigest() != expected['sha256']:
                changed.append(name)
        elif sha256(p) != expected['sha256']:
            changed.append(name)
    if changed:
        raise ValueError('Historical files changed or missing: ' + json.dumps(changed))
    return {'status': 'PASS', 'files': len(baseline['files']), 'append_only_checked': baseline['append_only'], 'model_calls': 0}


def baseline_report(task, generator, experiment):
    from degradation_lab.io import inventory
    from downstream_eval.sgb.attribution import audit_pair
    output = LAB / 'runs/eval/sgb' / task.TASK_ID / experiment
    analysis_path = LAB / 'results/sgb/analyses' / experiment / 'analysis.json'
    review_path = task.check_review(generator)
    profile = read(output / 'profile.json')
    if profile['generator_run_id'] != generator or profile['task_id'] != task.TASK_ID:
        raise ValueError('Wrong generator or task in the requested report')
    analysis = read(analysis_path)
    if analysis['experiment_id'] != experiment:
        raise ValueError('Wrong pilot analysis')
    specification = LAB / 'configs/attribution' / (experiment + '.json')
    attribution = audit_pair(LAB, read(specification))
    saved_attribution = LAB / 'results/sgb/attributions' / (experiment + '-v1') / 'report.json'
    if read(saved_attribution)['spec_digest'] != attribution['spec_digest']:
        raise ValueError('Exported attribution report differs from the current review specification')
    binding = pilot.load_binding(LAB, task.TASK_ID)
    config = task.execution_config(output, generator, binding['conditions'])
    pilot.runner.verify_frozen(LAB, output)
    pilot.runner.verify_ledger(LAB, output, config, profile)
    ledger = pilot.status(LAB, binding, experiment)
    expected_rules = {r['rule_id'] for r in read(LAB / f'cases/sgb/{task.CASE_ID}/rules.json')['rules']}
    required_stages = {'source', 'window', 'support', 'draft', 'spec', 'registered', 'skill'}
    reviewed = {r['rule_id'] for r in attribution['rule_reviews'] if r['review_status'] == 'reviewed'
                and {s['stage'] for s in r['stages']} == required_stages and r['downstream_links']}
    exposed = {r['rule_id'] for r in attribution['rule_reviews']
        if any(link['side'] == 'target' and link['delivery']['before_action'] is True
               for link in r['downstream_links'])}
    outcomes = {label: read(output / 'outcomes' / label / 'result.json')
                if (output / 'outcomes' / label / 'result.json').is_file() else {}
                for label in binding['conditions']}
    clean = next(r for r in analysis['results'] if r['label'] == 'CleanSkill1')
    complete = (ledger['status'] == 'COMPLETED' and attribution['comparability'] == 'eligible'
        and expected_rules <= reviewed
        and expected_rules <= exposed
        and clean['skill_usage']['counts']['full_body_in_successful_model_request'] > 0)
    destination = LAB / 'results/sgb/baselines' / experiment
    destination.mkdir(parents=True, exist_ok=False)
    value = {'status': 'COMPLETE' if complete else 'INCOMPLETE_REVIEW_OR_EXECUTION',
        'task_id': task.TASK_ID, 'generator': generator, 'experiment': experiment,
        'source_sha256': task.verify_assets()['source_document']['sha256'],
        'ledger': ledger, 'comparability': attribution['comparability'], 'task_difference': attribution['task_difference'],
        'outcomes': outcomes, 'quality_review_sha256': sha256(review_path),
        'rule_review_complete': expected_rules <= reviewed, 'skill_usage': clean['skill_usage'],
        'target_rule_context_before_action_confirmed': expected_rules <= exposed,
        'price_usd_per_million_tokens': profile.get('price_usd_per_million_tokens'),
        'cost_usd': None, 'cost_reason': 'Exact provider billing is unverified; actual token usage is recorded per trial.',
        'model_calls_in_report': 0}
    write(destination / 'baseline.json', value)
    files = {str(p.relative_to(LAB)): sha256(p) for p in [analysis_path, specification, review_path,
             saved_attribution, saved_attribution.with_suffix('.md')]}
    files.update({str((output / name).relative_to(LAB)): digest for name,digest in inventory(output).items()})
    write(destination / 'evidence-manifest.json', files)
    lines = ['# Sanctuary Task003 Clean baseline', '', 'Status: ' + value['status'],
        '', 'Protocol: one paired NoSkill/CleanSkill run; identical conditional body-reading instruction.',
        '', 'Comparability: ' + attribution['comparability'] + '; result: ' + attribution['task_difference'],
        '', '| Condition | Passed / 8 | Task success | HTTP attempts | Tokens |', '|---|---:|---|---:|---|']
    for label,result in outcomes.items():
        lines.append(f"| {label} | {result.get('oracle',{}).get('task_result',{}).get('passed')} | "
            f"{result.get('task_success')} | {result.get('http_attempts')} | {json.dumps(result.get('token_usage'))} |")
    lines += ['', 'Cost USD: unknown; use the provider billing record before reporting money spent.',
        '', f'Upstream quality review: `{review_path.relative_to(LAB).as_posix()}`',
        f'Pilot evidence: `{analysis_path.relative_to(LAB).as_posix()}`',
        f'Attribution specification: `{specification.relative_to(LAB).as_posix()}`',
        f'Attribution report: `{saved_attribution.with_suffix(".md").relative_to(LAB).as_posix()}`',
        '', 'Each assertion is a whole input/output case, not an independent causal case. Reading does not prove reliance.',
        'Both failures cannot establish Skill-induced harm. Source, prompt, runtime and Oracle scope limits remain in the admission report.',
        'COMPLETE means an auditable paired execution and rule review; task functionality is reported separately above.']
    (destination / 'baseline.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return {'status': value['status'], 'report': str(destination / 'baseline.md'), 'model_calls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('audit', 'acceptance', 'quality', 'authorization', 'history-start', 'history-check', 'report'))
    parser.add_argument('--audit-id', help='Acceptance/history directory name under results/sgb/audits')
    parser.add_argument('--authorization-phase', choices=('generation', 'downstream'), default='generation')
    parser.add_argument('--generator-run', default='sn3g001')
    parser.add_argument('--experiment', default='sn3e001')
    args = parser.parse_args()
    if os.name == 'nt':
        runtime = read(LAB / 'configs/downstream_runtime.json')
        mount = runtime['project_mount']
        command = ['docker', 'exec', '--env', 'PYTHONPATH=' + mount + ':' + mount + '/src',
            '--env', 'LITELLM_LOCAL_MODEL_COST_MAP=True', runtime['control_container'],
            runtime['python_executable'], '-B', mount + '/scripts/sgb/sanctuary002.py', *sys.argv[1:]]
        return subprocess.run(command).returncode
    if args.phase in ('history-start', 'history-check'):
        result = history(args.audit_id, create=args.phase == 'history-start')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    from downstream_eval.sgb.task_adapters.audited import sanctuary002 as task
    if args.phase == 'report':
        result = baseline_report(task, args.generator_run, args.experiment)
    elif args.phase == 'audit':
        manifest = task.verify_assets()
        binding = pilot.load_binding(LAB, task.TASK_ID)
        result = {'status': 'PASS', 'task_id': task.TASK_ID, 'case_id': task.CASE_ID,
            'source_sha256': manifest['source_document']['sha256'], 'original_assertions': 8,
            'conditions': binding['conditions'], 'gate': read(task.GATE), 'model_calls': 0}
    elif args.phase == 'quality':
        path = task.check_review(args.generator_run)
        result = {'status': 'PASS', 'review': str(path), 'sha256': sha256(path), 'model_calls': 0}
    elif args.phase == 'authorization':
        result = task.check_authorization(args.authorization_phase, args.generator_run, args.experiment)
    else:
        if not args.audit_id or not pilot.runner._identifier(args.audit_id):
            parser.error('acceptance requires a safe new --audit-id')
        output = LAB / 'results/sgb/audits' / args.audit_id
        output.mkdir(parents=True, exist_ok=False)
        fixtures = read(LAB / f'tests/fixtures/sgb/audited/{task.TASK_ID}/candidates.json')
        reports = []
        for name, fixture in fixtures.items():
            candidate = output / (name + '.py')
            candidate.write_text(fixture['source'], encoding='utf-8')
            score = task.score(candidate, output / name)
            good = (score['infra_ok'] and score['candidate_binding_verified']
                and score['task_result']['tests'] == 8 and score['task_result']['passed'] == fixture['passed']
                and set(score.get('failed_tests', [])) == set(fixture['failed']))
            reports.append({'fixture': name, 'accepted': good, 'result': score})
            result = {'status': 'PASS' if len(reports) == len(fixtures) and all(r['accepted'] for r in reports)
                      else 'INCOMPLETE_OR_FAIL', 'model_calls': 0, 'real_agent_outcome': False, 'reports': reports}
            write(output / 'acceptance.json', result)
            print(json.dumps({'fixture': name, 'accepted': good, 'counts': score['task_result'],
                              'error': score.get('error')}, ensure_ascii=False), flush=True)
            if not good:
                raise RuntimeError('Zero-model acceptance failed; preserve this audit and inspect result.json')
        result = {'status': result['status'], 'model_calls': 0, 'report': str(output / 'acceptance.json')}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
