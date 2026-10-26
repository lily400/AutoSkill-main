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
    from downstream_eval.sgb.attribution import audit_pair, classify
    from downstream_eval.sgb.attribution_contract import STAGES

    if not pilot.runner._identifier(generator):
        raise ValueError('Safe generator ID required')
    binding = pilot.load_binding(LAB, task.TASK_ID)
    output = pilot.output_path(LAB, binding, experiment)
    destination = LAB / 'results/sgb/baselines' / experiment
    if destination.exists():
        raise FileExistsError(destination)
    assets = task.verify_assets()
    missing, inputs = [], {}

    def optional(path):
        if not path.is_file():
            missing.append(path.relative_to(LAB).as_posix())
            return None
        inputs[path.relative_to(LAB).as_posix()] = sha256(path)
        return read(path)

    profile = optional(output / 'profile.json')
    if profile is not None and any(profile.get(k) != v for k, v in (
            ('generator_run_id', generator), ('task_id', task.TASK_ID), ('experiment_id', experiment))):
        raise ValueError('Wrong generator, task or experiment in profile')
    analysis_path = LAB / 'results/sgb/analyses' / experiment / 'analysis.json'
    analysis = optional(analysis_path)
    if analysis is not None and analysis.get('experiment_id') != experiment:
        raise ValueError('Wrong pilot analysis')
    review_path = LAB / f'evaluations/{task.CASE_ID}/clean/{generator}/pre_downstream.json'
    review = optional(review_path)
    review_status, review_reason = 'missing', None
    if review is not None:
        try:
            task.check_review(generator)
            review_status = 'reviewed'
        except RuntimeError as error:
            review_status, review_reason = 'pending_review', str(error)
    gate = optional(task.GATE)
    approved = (gate or {}).get('downstream', {})
    if (review is not None and approved.get('experiment_id') == experiment
            and approved.get('generator_run_id') == generator and approved.get('quality_review_sha256')
            and approved['quality_review_sha256'] != sha256(review_path)):
        raise ValueError('Review hash differs from the bound authorization')

    manifest = optional(output / 'execution_manifest.json')
    missing_frozen = set()
    for name, digest in (manifest or {}).items():
        path = pilot.inside(LAB, name)
        if not path.is_file():
            missing_frozen.add(name)
            missing.append(name)
        elif sha256(path) != digest:
            raise ValueError('Frozen execution file changed: ' + name)
    ledger = pilot.status(LAB, binding, experiment)
    if profile and manifest and (output / 'budget.sqlite3').is_file():
        config = task.execution_config(output, generator, binding['conditions'])
        pilot.runner.verify_ledger(LAB, output, config, profile)

    run_path = output.relative_to(LAB).as_posix()
    base_spec = dict(schema_version=1, analysis_id=experiment+'-report', pair_id=experiment+'-pair',
        task_id=task.TASK_ID, comparison_kind='no_skill_clean',
        reference={'run_path':run_path,'label':'NoSkill1'}, target={'run_path':run_path,'label':'CleanSkill1'},
        evidence=[], rules=[], claims=[], interventions=[])
    specification = LAB / 'configs/attribution' / (experiment + '.json')
    supplied = optional(specification)
    spec = supplied if supplied is not None else base_spec
    if spec['task_id'] != task.TASK_ID or spec['comparison_kind'] != 'no_skill_clean':
        raise ValueError('Attribution specification belongs to another task or treatment')
    for side in ('reference', 'target'):
        if spec[side] is not None and spec[side] != base_spec[side]:
            raise ValueError('Attribution must not borrow a trial from another batch or condition')
    pair = audit_pair(LAB, spec)
    # A missing declared comparison does not erase independently completed trials.
    execution = pair if all(spec[s] == base_spec[s] for s in ('reference','target')) else audit_pair(LAB, base_spec)
    saved_path = LAB / 'results/sgb/attributions' / (experiment + '-v1') / 'report.json'
    saved = optional(saved_path)
    if saved is not None:
        if saved.get('task_id') != task.TASK_ID:
            raise ValueError('Saved attribution belongs to another task')
        if supplied is not None and saved.get('spec_digest') != pair['spec_digest']:
            raise ValueError('Exported attribution differs from the current review specification')
    for generation in execution['generations'].values():
        if generation and generation['case_id'] != task.CASE_ID:
            raise ValueError('Generation belongs to another task case')
        if generation and generation['integrity'] == 'mismatch':
            raise ValueError('Generation/source integrity mismatch: ' + str(generation['mismatches']))

    expected_tests = binding['expected_oracle_tests']
    expected_oracle = assets['files']['oracle/eval.py']
    trial_status, success, usage, outcomes = {}, {}, {}, {}
    for label, side in (('NoSkill1','reference'), ('CleanSkill1','target')):
        trial = execution['trials'][side]
        oracle = (trial or {}).get('oracle') or {}
        raw = (trial or {}).get('raw_outcome') or {}
        issues = []
        for issue in (trial or {}).get('integrity_issues', []):
            absent = issue.startswith('Frozen run file mismatch: ') and issue.split(': ',1)[1] in missing_frozen
            no_score_yet = (issue == 'Submitted bytes disagree with Oracle candidate hash'
                            and not oracle.get('candidate_sha256') and not raw)
            if not absent and not no_score_yet:
                issues.append(issue)
        if issues:
            raise ValueError('Trial integrity error: ' + '; '.join(issues))
        if trial and trial['generator_run_id'] not in (None, generator):
            raise ValueError('Trial belongs to another generation')
        if trial and trial['case_id'] not in (None, task.CASE_ID):
            raise ValueError('Trial belongs to another task case')
        oracle_id = oracle.get('oracle_sha256') or oracle.get('oracle_original_sha256')
        if oracle.get('task_id') not in (None, task.TASK_ID):
            raise ValueError('Score belongs to another task')
        if oracle_id is not None and oracle_id != expected_oracle:
            raise ValueError('Score was produced by another Oracle')
        counts = oracle.get('task_result', {})
        if oracle.get('infra_ok') is True and counts.get('tests', 0) and counts['tests'] != expected_tests:
            raise ValueError('Oracle assertion count differs from the task contract')
        score_valid = bool(trial and raw.get('model_api_results') is True and oracle.get('infra_ok') is True
            and oracle.get('candidate_binding_verified') is True and trial['paths']['candidate']
            and trial['assertions'] is not None and counts.get('tests') == expected_tests
            and not counts.get('errors') and not counts.get('skipped') and oracle_id == expected_oracle)
        if score_valid and raw.get('task_success') is not (counts.get('passed') == expected_tests):
            raise ValueError('Task success disagrees with the original Oracle score')
        success[label] = raw['task_success'] if score_valid else None
        started = bool(raw or (output / 'batch.started').exists()
                       or (trial and (LAB / trial['paths']['trial']).exists()))
        trial_status[label] = ('completed' if score_valid and trial['scorable'] else
                               'partial' if started else 'not_started')
        observed = (trial or {}).get('usage')
        usage[label] = observed or {'status':'INCOMPLETE_EVIDENCE', 'behavioral_use':{'status':'UNKNOWN'}}
        outcomes[label] = raw
    execution_status = ('completed' if all(s == 'completed' for s in trial_status.values()) else
                        'not_started' if all(s == 'not_started' for s in trial_status.values()) else 'partial')
    comparability = pair['comparability']
    if comparability == 'eligible' and any(s is None for s in success.values()):
        comparability = 'unknown'
    difference = classify(success['NoSkill1'], success['CleanSkill1'], comparability == 'eligible')
    expected_rules = {r['rule_id'] for r in read(LAB / f'cases/sgb/{task.CASE_ID}/rules.json')['rules']}
    reviewed = [r for r in pair['rule_reviews'] if r['review_status'] == 'reviewed']
    if comparability != 'eligible':
        attribution_status = 'not_comparable'
    elif not supplied or not expected_rules <= {r['parent_rule_id'] for r in reviewed}:
        attribution_status = 'pending_review'
    elif any(not r['downstream_links'] or {s['stage'] for s in r['stages']} != set(STAGES) or any(
            s['status'] == 'unknown' or not s['evidence_ids'] for s in r['stages']) for r in reviewed):
        attribution_status = 'insufficient_evidence'
    else:
        attribution_status = 'reviewed'
    files = dict(inputs)
    tracked = execution['evidence_files'] + pair['evidence_files']
    tracked += [{'path':(output/name).relative_to(LAB).as_posix(), 'sha256':digest}
                for name,digest in inventory(output).items()]
    for entry in tracked:
        name, digest = entry['path'], entry['sha256']
        if name in files and files[name] != digest:
            raise ValueError('Evidence changed during reporting: ' + name)
        files[name] = digest
    if any(not pilot.inside(LAB,name).is_file() or sha256(pilot.inside(LAB,name)) != digest
           for name,digest in files.items()):
        raise ValueError('Evidence changed during reporting')
    destination.mkdir(parents=True, exist_ok=False)
    value = {'schema_version':2, 'task_id':task.TASK_ID, 'generator':generator, 'experiment':experiment,
        'experiment_execution_status':execution_status, 'trial_execution_status':trial_status,
        'skill_usage_status':{label:u['status'] for label,u in usage.items()}, 'skill_usage':usage,
        'task_success':success, 'attribution_status':attribution_status,
        'comparability':comparability, 'task_difference':difference,
        'attribution_details':{k:pair[k] for k in ('rule_reviews','review_evidence','claims','interventions','semantic_validation')},
        'source_sha256':assets['source_document']['sha256'], 'ledger':ledger, 'outcomes':outcomes,
        'upstream_review_status':review_status, 'upstream_review_reason':review_reason,
        'semantic_findings':task.review_findings(review) if review is not None else [],
        'quality_review_sha256':sha256(review_path) if review is not None else None,
        'missing_evidence':sorted(set(missing)), 'model_calls_in_report':0,
        'cost_usd':None, 'cost_reason':'Exact provider billing is unverified; actual usage remains in the trial records.'}
    write(destination / 'baseline.json', value)
    write(destination / 'evidence-manifest.json', files)
    lines = ['# Sanctuary Task003 Clean baseline', '',
        'Execution: '+execution_status, 'Comparability: '+comparability,
        'Attribution: '+attribution_status+'; differential result: '+difference, '',
        '| Condition | Execution | Task success | Skill usage | Passed / tests |', '|---|---|---|---|---|']
    for label in binding['conditions']:
        counts = outcomes[label].get('oracle',{}).get('task_result',{})
        lines.append(f"| {label} | {trial_status[label]} | {success[label]} | {usage[label]['status']} | "
                     f"{counts.get('passed')} / {counts.get('tests')} |")
    lines += ['', 'Semantic findings: '+json.dumps(value['semantic_findings'],ensure_ascii=False),
        '', 'Missing evidence: '+json.dumps(value['missing_evidence'],ensure_ascii=False),
        '', 'Execution completion does not require task success, Skill reading, or a complete mechanism trace.',
        'Reading does not prove understanding or reliance. Reviewed attribution does not establish causation;',
        'claim evidence levels remain observed/inferred/hypothesis/intervention_supported as explicitly validated.',
        'Noncompliance with required reading remains a usage/protocol observation, not an erased execution.',
        'USD cost is unknown. Inspect the original trial usage and provider billing before reporting money spent.']
    (destination / 'baseline.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return {k:value[k] for k in ('experiment_execution_status','attribution_status','comparability')} | {
        'report':str(destination/'baseline.md'), 'model_calls':0}



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
        result = {'review_status': 'reviewed', 'semantic_findings': task.review_findings(read(path)),
                  'review': str(path), 'sha256': sha256(path), 'model_calls': 0}
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
