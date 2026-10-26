"""Read-only paired attribution. No Agent, model, Docker or scorer imports/execution."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

from degradation_lab.artifacts import load_run
from degradation_lab.io import inside, read, sha256, utc
from downstream_eval.integration.skill_usage import audit_skill_usage
from .attribution_contract import validate_spec


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class EvidenceFiles:
    """Only files actually inspected are indexed; original paths remain in the report."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.files = {}

    def path(self, relative):
        return inside(self.root, relative)

    def track(self, path, requested=None):
        path = Path(path).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Evidence path escapes lab')
        rel = path.relative_to(self.root).as_posix()
        if path.is_file():
            row = {'path': rel, 'sha256': sha256(path), 'aliases': []}
            previous = self.files.setdefault(rel, row)
            if previous['sha256'] != row['sha256']:
                raise ValueError('Evidence changed during analysis: ' + rel)
            if requested and str(requested) != rel and str(requested) not in previous['aliases']:
                previous['aliases'].append(str(requested))
        return path

    def json(self, path, default=None):
        path = Path(path)
        if not path.is_file():
            return deepcopy(default)
        return read(self.track(path))

    def events(self, path):
        if not Path(path).is_file():
            return None
        return [json.loads(s) for s in self.track(path).read_text(encoding='utf-8').splitlines() if s.strip()]

    def unchanged(self):
        for row in self.files.values():
            if sha256(self.path(row['path'])) != row['sha256']:
                raise ValueError('Evidence changed during analysis: ' + row['path'])


def _stored_relative(root, value):
    """Translate a stored project path; never follow arbitrary host absolute paths."""
    text = str(value).replace('\\', '/')
    marker = '/' + Path(root).name + '/'
    if marker in text:
        return text.split(marker, 1)[1]
    if text.startswith('/') or ':' in text:
        raise ValueError('Stored path is outside the lab: ' + text)
    return text


def _normalized_config(config):
    value = deepcopy(config)
    for key in ('trial_name', 'trials_dir'):
        value.pop(key, None)
    agent = value.get('agent', {})
    agent.pop('skills', None)
    for key in ('p1_manifest', 'p1_profile'):
        agent.get('kwargs', {}).pop(key, None)
    return value


def _assertions(files, directory, oracle):
    paths = list(directory.rglob('junit.xml')) if directory.is_dir() else []
    if len(paths) != 1:
        return None, 'Missing or ambiguous JUnit evidence'
    try:
        tree = ElementTree.parse(files.track(paths[0]))
    except ElementTree.ParseError:
        return None, 'Malformed JUnit evidence'
    rows = {}
    counts = dict(tests=0, passed=0, failed=0, errors=0, skipped=0)
    for node in tree.iter('testcase'):
        name = node.attrib.get('name')
        if not name or name in rows:
            return None, 'Missing or duplicate assertion identity'
        state = ('errors' if node.find('error') is not None else 'failed' if node.find('failure') is not None
                 else 'skipped' if node.find('skipped') is not None else 'passed')
        counts['tests'] += 1
        counts[state] += 1
        rows[name] = {'status': state, 'classname': node.attrib.get('classname')}
    expected = oracle.get('task_result', {})
    if not counts['tests'] or any(counts[k] != expected.get(k, 0) for k in counts):
        return None, 'JUnit counts disagree with Oracle'
    return rows, None


def _generation(files, generator_id):
    if not generator_id:
        return None
    try:
        identity, path, result, stages = load_run(files.root, generator_id)
    except ValueError:
        return None
    manifest = files.json(path / 'artifact_manifest.json', {})
    bad = []
    for rel, expected in manifest.items():
        p = inside(path, rel)
        if not p.is_file() or sha256(files.track(p)) != expected:
            bad.append(rel)
    inputs = files.json(path / 'input_manifest.json', {})
    for item in inputs.get('inputs', []):
        for p, expected in [(inside(path, item['path']), item['sha256']),
                            (files.path(item['original_path']), item['source_sha256'])]:
            if not p.is_file() or sha256(files.track(p)) != expected:
                bad.append(p.relative_to(files.root).as_posix())
    config = files.json(path / 'config.json', {})
    condition = files.json(path / 'condition.json', {})
    calls = files.json(path / 'model_calls.json', [])
    return {'run_id': generator_id, 'case_id': identity['case_id'], 'path': identity['path'],
            'document_condition': condition, 'source_inputs': inputs,
            'generation_config': config, 'generation_config_sha256': sha256(path / 'config.json') if config else None,
            'upstream_code': files.json(path / 'upstream_before.json'),
            'models_observed': sorted({str(c.get('model_returned')) for c in calls if c.get('model_returned')}),
            'manifest_sha256': sha256(path / 'artifact_manifest.json') if manifest else None,
            'integrity': 'mismatch' if bad else 'verified' if manifest else 'unknown',
            'mismatches': bad, 'official_status': result.get('status'),
            'rules': files.json(path / 'rules.json', {}).get('rules', [])}


def _load_trial(files, ref, task_id):
    if ref is None:
        return None
    run = files.path(ref['run_path'])
    if not run.is_relative_to(files.root / 'runs'):
        raise ValueError('Trial must reference a saved run')
    label = ref['label']
    if '/' in label or '\\' in label or label in ('.', '..'):
        raise ValueError('Unsafe trial label')
    issues = []
    profile = files.json(run / 'profile.json', {})
    manifest = files.json(run / 'execution_manifest.json', {})
    package = files.json(run / 'skills_manifest.json', {})
    arm = files.json(run / 'manifests' / (label + '.json'), {})
    outcome = files.json(run / 'outcomes' / label / 'result.json')
    batch = files.json(run / 'batch_results.json', {})
    batched = [x for x in batch.get('results', []) if x.get('label') == label]
    if outcome is None and len(batched) == 1:
        outcome = batched[0]
    elif outcome is not None and batched and outcome != batched[0]:
        issues.append('Per-arm result disagrees with batch result')
    outcome = outcome or {}
    config = files.json(run / 'configs' / (label + '.json'), {})
    trial = run / 'trials' / config.get('trial_name', '__missing__')
    if not config:
        candidates = [p for p in (run / 'trials').glob('*/config.json') if p.parent.name.endswith(label.lower())]
        if len(candidates) == 1:
            config = files.json(candidates[0], {})
            trial = candidates[0].parent
    if not trial.resolve().is_relative_to(run.resolve()):
        raise ValueError('Trial path escapes run')
    native = files.json(run / 'outcomes' / label / 'native.json')
    if native is None:
        native = files.json(trial / 'result.json', {})
    native = native or {}
    bound_run_files = set()
    for name, expected in manifest.items():
        p = files.path(name)
        if p.is_relative_to(run):
            bound_run_files.add(p)
            if not p.is_file() or sha256(files.track(p, name)) != expected:
                issues.append('Frozen run file mismatch: ' + name)
    oracle = outcome.get('oracle') or {}
    scoring = run / 'outcomes' / label / 'oracle'
    result_paths = list(scoring.rglob('result.json')) if scoring.is_dir() else []
    # New scorer results and the embedded result must describe the same submitted bytes.
    for p in result_paths:
        scored = files.json(p, {})
        if scored.get('candidate_sha256') and any(scored.get(k) != oracle.get(k)
                for k in ('candidate_sha256', 'task_result')):
            issues.append('Scorer result disagrees with recorded outcome')
    assertions, assertion_error = _assertions(files, scoring, oracle)
    candidate_digest = oracle.get('candidate_sha256')
    candidate_files = [p for p in trial.rglob('agent_output.py') if p.is_file()]
    candidate = next((p for p in candidate_files if sha256(p) == candidate_digest), None)
    if candidate:
        files.track(candidate)
    if candidate_files and candidate is None:
        issues.append('Submitted bytes disagree with Oracle candidate hash')
    if oracle.get('candidate_binding_verified') is False:
        issues.append('Oracle explicitly rejected candidate binding')
    if oracle.get('loading_errors') or oracle.get('environment_errors'):
        issues.append('Oracle reported loading or environment errors')
    usage = None
    try:
        if arm:
            usage = audit_skill_usage(run, label, trial)
            for p in usage['evidence_files']:
                files.track(Path(p))
    except ValueError as error:
        issues.append(str(error))
    stage_name = PurePosixPath(str(arm.get('staged_root', '')).replace('\\', '/')).name
    staged = run / 'staged' / stage_name
    if stage_name in ('', '.', '..'):
        staged = run / 'staged' / '__missing__'
    kwargs = config.get('agent', {}).get('kwargs', {})
    expected_paths = {'p1_profile': run / 'profile.json',
                      'p1_manifest': run / 'manifests' / (label + '.json')}
    for key, expected in expected_paths.items():
        if key in kwargs and files.path(_stored_relative(files.root, kwargs[key])) != expected:
            issues.append('Agent configuration references another ' + key)
    installed_paths = config.get('agent', {}).get('skills')
    no_skill = (outcome.get('condition') or profile.get('conditions', {}).get(label)) == 'NoSkill'
    empty_no_skill = no_skill and installed_paths == [] and not arm.get('files') and not arm.get('metadata')
    if (installed_paths is not None and not empty_no_skill
            and [files.path(_stored_relative(files.root, p)) for p in installed_paths] != [staged]):
        issues.append('Agent configuration does not install the declared staged directory')
    for p in staged.rglob('*'):
        if p.is_file():
            files.track(p)
    condition = outcome.get('condition') or profile.get('conditions', {}).get(label)
    if condition is None and label.startswith(('NoSkill', 'CleanSkill')):
        condition = 'NoSkill' if label.startswith('NoSkill') else 'CleanSkill'
    task_name = PurePosixPath(str(config.get('task', {}).get('path', '')).replace('\\', '/')).name
    if profile.get('task_id') not in (None, task_id) or native.get('task_name') not in (None, task_name):
        issues.append('Task identity mismatch')
    if arm and arm.get('arm', label) != label:
        issues.append('Skill manifest belongs to another arm')
    if condition == 'NoSkill' and (arm.get('files') or arm.get('metadata')):
        issues.append('NoSkill contains Skill treatment')
    if condition != 'NoSkill' and package.get('packages'):
        frozen_files = {}
        for sid, entry in package['packages'].items():
            source = files.path(entry['source_path']).parent
            for name, expected in entry.get('files', {}).items():
                p = inside(source, name)
                frozen_files[sid + '/' + name] = expected
                if not p.is_file() or sha256(files.track(p)) != expected:
                    issues.append('Generated package differs from frozen delivery: ' + sid + '/' + name)
        if arm.get('files') != frozen_files:
            issues.append('Delivered package inventory differs from generation freeze')
    stopped = files.json(run / 'batch_stop.json')
    if not outcome:
        missing = 'Missing completed outcome' + (': ' + str(stopped.get('error_type')) if stopped else '')
    else:
        missing = None
    counts = oracle.get('task_result', {})
    scorable = (type(outcome.get('task_success')) is bool and outcome.get('infra_ok') is True
        and not native.get('exception_info') and oracle.get('infra_ok', True) is True
        and counts.get('tests', 0) > 0 and counts.get('errors', 0) == 0 and counts.get('skipped', 0) == 0
        and candidate is not None and assertions is not None and not issues)
    if scorable and outcome['task_success'] != (counts.get('passed') == counts.get('tests')):
        issues.append('Task success disagrees with all-test success')
        scorable = False
    if outcome.get('model_api_results') is not True or native.get('finished_at') is None:
        scorable = False
        missing = missing or 'No completed observed Agent execution'
    execution_state = ('scored_completion' if scorable else 'budget_stop_unresolved'
        if stopped and 'budget' in json.dumps(stopped).lower() else 'execution_error_unresolved'
        if native.get('exception_info') else 'incomplete_or_invalid_evidence')
    generator_id = arm.get('generator_run_id') or package.get('generator_run_id') or profile.get('generator_run_id')
    fixed = {k: v for k, v in manifest.items() if not k.startswith('runs/')}
    # Keep historical fingerprints, not current checkout versions, for execution identity.
    task_assets = {k: v for k, v in fixed.items() if '/tasks/' in k and '/template' not in k}
    code = {k: v for k, v in fixed.items() if k.endswith('.py') and '/tasks/' not in k}
    extra = config.get('extra_instruction_paths', [])
    extra_hashes = []
    for path in extra:
        key = _stored_relative(files.root, path)
        extra_hashes.append(manifest.get(key))
    fairness = files.json(run / 'fairness.json', {})
    runtime = fairness.get('runtime') or {}
    controls = {
        'task_id': profile.get('task_id'), 'task_checksum': native.get('task_checksum'),
        'task_assets': task_assets or None, 'model': profile.get('model'), 'budget': profile.get('budget'),
        'agent_info': native.get('agent_info'), 'agent_code': code or None,
        'runtime_versions': files.json(run / 'runtime_versions.json'),
        'agent_image': profile.get('frozen_agent_image_id') or fairness.get('image_id'),
        'runtime': runtime or None, 'extra_instruction_hashes': extra_hashes if all(extra_hashes) else None,
        'configuration': _normalized_config(config) if config else None,
        'oracle_hash': oracle.get('oracle_sha256') or oracle.get('oracle_original_sha256'),
        'assertion_set': sorted(assertions) if assertions else None,
    }
    # A complete task checksum covers task inputs and environment recipe; no host filesystem guess.
    if config and extra == []:
        controls['extra_instruction_hashes'] = []
    required_frozen = [run / 'profile.json', run / 'configs' / (label + '.json'),
                       run / 'manifests' / (label + '.json'), run / 'skills_manifest.json']
    controls['frozen_run_identity'] = True if all(p in bound_run_files for p in required_frozen) else None
    return {'reference': ref, 'run_id': run.name, 'label': label, 'condition': condition,
        'case_id': package.get('case_id'), 'generator_run_id': generator_id,
        'document_condition': None if condition == 'NoSkill' else package.get('condition', 'unknown'),
        'controls': controls, 'scorable': scorable, 'integrity_issues': issues,
        'execution_state': execution_state,
        'missing_evidence': [x for x in (missing, assertion_error) if x],
        'task_success': outcome.get('task_success'), 'oracle': oracle, 'assertions': assertions,
        'usage': usage, 'skill_files': arm.get('files'), 'skill_manifest': package,
        'raw_outcome': outcome, 'batch_stop': stopped,
        'paths': {'run': run.relative_to(files.root).as_posix(),
                  'trial': trial.relative_to(files.root).as_posix(),
                  'stage': staged.relative_to(files.root).as_posix(),
                  'candidate': candidate.relative_to(files.root).as_posix() if candidate else None}}


def _compare(left, right):
    if left is None or right is None:
        return 'unknown'
    return 'equal' if left == right else 'different'


def classify(reference, target, eligible=True):
    if not eligible or type(reference) is not bool or type(target) is not bool:
        return 'unresolved'
    return {(False, True): 'possible_help', (True, False): 'possible_harm',
            (True, True): 'both_passed', (False, False): 'both_failed'}[(reference, target)]


def audit_pair(root, spec):
    """Pure historical audit. Semantic statements are explicit reviewer annotations."""
    validate_spec(spec)
    files = EvidenceFiles(root)
    sides = {k: _load_trial(files, spec[k], spec['task_id']) for k in ('reference', 'target')}
    generations = {}
    for trial in sides.values():
        if trial and trial['generator_run_id'] not in generations:
            generations[trial['generator_run_id']] = _generation(files, trial['generator_run_id'])
        if trial:
            generation = generations.get(trial['generator_run_id'])
            trial['document_condition_id'] = trial['document_condition']
            trial['document_condition'] = (None if trial['condition'] == 'NoSkill' else
                generation['document_condition'].get('kind') if generation else None)
    checks = []
    def check(name, left, right):
        checks.append({'field': name, 'status': _compare(left, right), 'reference': left, 'target': right})
    left, right = sides.values()
    if left and right:
        loading_intervention = (spec['comparison_kind'] == 'intervention' and len(spec['interventions']) == 1
                                and spec['interventions'][0]['scope'] == 'loading_protocol')
        for key in left['controls']:
            if loading_intervention and key == 'extra_instruction_hashes':
                continue
            if loading_intervention and key == 'configuration':
                a, b = deepcopy(left['controls'][key]), deepcopy(right['controls'][key])
                if a is not None and b is not None:
                    for value in (a, b):
                        value.pop('extra_instruction_paths', None)
                        value.pop('extra_instructions', None)
                check('configuration_except_declared_loading_instruction', a, b)
                continue
            check(key, left['controls'][key], right['controls'][key])
        treatment = (left['condition'], right['condition'])
        if spec['comparison_kind'] == 'no_skill_clean':
            check('treatment', treatment, ('NoSkill', 'CleanSkill'))
            check('clean_document_condition', right['document_condition'], 'clean')
            # The associated generator identity is fixed even in the NoSkill manifest.
            check('associated_generator', left['generator_run_id'], right['generator_run_id'])
        elif spec['comparison_kind'] == 'clean_degraded':
            check('document_conditions', [left['document_condition'], right['document_condition']], ['clean', 'degraded'])
            lg, rg = (generations.get(t['generator_run_id']) for t in (left, right))
            if lg and rg:
                for key in ('generation_config', 'upstream_code'):
                    check(key, lg[key], rg[key])
                li, ri = lg['source_inputs'].get('inputs', []), rg['source_inputs'].get('inputs', [])
                check('original_sources', [(i['source_id'], i['source_sha256']) for i in li],
                      [(i['source_id'], i['source_sha256']) for i in ri])
                check('input_changed', [i['sha256'] for i in li] != [i['sha256'] for i in ri], True)
                check('degradation_operator_declared', bool(rg['document_condition'].get('operator')), True)
            else:
                check('generation_records', None, None)
        else:
            check('single_declared_intervention', len(spec['interventions']), 1)
            if len(spec['interventions']) == 1:
                scope = spec['interventions'][0]['scope']
                if scope != 'source':
                    check('intervention_associated_generator', left['generator_run_id'], right['generator_run_id'])
                else:
                    lg, rg = (generations.get(t['generator_run_id']) for t in (left, right))
                    for key in ('generation_config', 'upstream_code'):
                        check('intervention.' + key, lg.get(key) if lg else None, rg.get(key) if rg else None)
                    def originals(g):
                        return [(i['source_id'], i['source_sha256']) for i in g['source_inputs'].get('inputs', [])] if g else None
                    check('intervention.original_sources', originals(lg), originals(rg))
    else:
        check('paired_runs', None, None)
    for side, trial in sides.items():
        if trial:
            checks.append({'field': side + '.execution', 'status': 'different' if trial['integrity_issues']
                else 'equal' if trial['scorable'] else 'unknown',
                'reference': 'completed, bound, scorable',
                'target': trial['integrity_issues'] or trial['missing_evidence'] or trial['scorable']})
        if trial and trial['controls']['frozen_run_identity'] is not True:
            check(side + '.frozen_identity_available', None, True)
    for gid, generation in generations.items():
        status = generation.get('integrity') if generation else None
        check('generation_integrity.' + str(gid), None if status == 'unknown' else status, 'verified')
    statuses = [c['status'] for c in checks]
    comparability = 'ineligible' if 'different' in statuses else 'unknown' if 'unknown' in statuses else 'eligible'
    eligible = comparability == 'eligible' and bool(left and right and left['scorable'] and right['scorable'])
    outcome = classify(left['task_success'] if left else None, right['task_success'] if right else None, eligible)
    changes = []
    if left and right and left['assertions'] and right['assertions']:
        for name in sorted(set(left['assertions']) | set(right['assertions'])):
            a, b = left['assertions'].get(name), right['assertions'].get(name)
            a, b = a['status'] if a else None, b['status'] if b else None
            label = classify(a == 'passed', b == 'passed', eligible and a is not None and b is not None)
            changes.append({'assertion': name, 'reference': a, 'target': b, 'difference': label})
    from .attribution_evidence import review_evidence
    review = review_evidence(files, spec, sides, generations, comparability, changes)
    files.unchanged()
    return {'schema_version': 1, 'analysis_id': spec['analysis_id'], 'pair_id': spec['pair_id'],
        'spec_digest': digest(spec),
        'task_id': spec['task_id'], 'comparison_kind': spec['comparison_kind'], 'created_at': utc(),
        'spec': deepcopy(spec), 'comparability': comparability, 'control_checks': checks,
        'task_difference': outcome, 'assertion_differences': changes, 'trials': sides,
        'generations': generations, **review, 'evidence_files': list(files.files.values()),
        'limits': ['Historical evidence only; no model, Agent, container or Oracle replay.',
                  'Package delivery is not behavioral reliance; semantic labels are reviewer annotations.',
                  'First observed rule loss is not proof of downstream causation.',
                  'Unknowns are not agreement. Possible effects are not stable causal estimates.']}


def markdown(report):
    lines = ['# CleanSkill downstream attribution', '',
        f"- Analysis: `{report['analysis_id']}`; pair: `{report['pair_id']}`",
        f"- Comparability: **{report['comparability']}**",
        f"- Task difference: **{report['task_difference']}**", '',
        '| Arm | Condition | Passed / tests | Skill evidence |', '|---|---|---|---|']
    for side, trial in report['trials'].items():
        if trial:
            c = trial['oracle'].get('task_result', {})
            lines.append(f"| {side}: {trial['run_id']}/{trial['label']} | {trial['condition']} | "
                         f"{c.get('passed', '?')}/{c.get('tests', '?')} | {(trial['usage'] or {}).get('status', 'UNKNOWN')} |")
        else:
            lines.append(f'| {side} | missing | unknown | unknown |')
    lines += ['', '## Pair qualification', '']
    for check in report['control_checks']:
        lines.append(f"- `{check['field']}`: {check['status']}")
    lines += ['', '## Assertion differences', '']
    for row in report['assertion_differences']:
        if row['difference'] != 'both_passed':
            lines.append(f"- `{row['assertion']}`: {row['reference']} → {row['target']} ({row['difference']})")
    lines += ['', '## Rule and mechanism review', '']
    for rule in report['rule_reviews']:
        lines.append(f"- `{rule['rule_id']}` ({rule['generator_run_id']}): {rule['claim']}; "
                     f"first observed loss = {rule['first_observed_loss']}; review = {rule['review_status']}")
        for stage in rule['stages']:
            lines.append(f"  - {stage['stage']}: {stage['status']} — {stage['rationale']}")
        for link in rule['downstream_links']:
            lines.append(f"  - {link['side']}: rule context before action = {link['delivery']['before_action']}; "
                         f"behavioral use = UNKNOWN; {link['interpretation']}")
    for claim in report['claims']:
        lines.append(f"- [{claim['status']}; {claim['scope']}] {claim['text']} "
                     f"(reviewer: {claim['reviewer']}; evidence: {', '.join(claim['evidence_ids'])})")
    lines += ['', '## Evidence', '']
    for row in report['review_evidence']:
        lines.append(f"- `{row['evidence_id']}`: `{row['artifact_path']}` {row['locator']}; "
                     f"sha256 `{row['artifact_sha256']}`; {row['verification']}")
    lines += ['', '## Interventions', '']
    for intervention in report['interventions']:
        lines.append(f"- `{intervention['intervention_id']}` v{intervention['version']}: "
                     f"{intervention['status']}; {intervention['expected_effect']}")
    lines += ['', '## Limits', ''] + ['- ' + text for text in report['limits']]
    return '\n'.join(lines) + '\n'


def export_report(root, spec, output):
    root = Path(root).resolve()
    destination = Path(output).resolve()
    analysis_root = root / 'results/sgb/attributions'
    if not destination.is_relative_to(analysis_root) or destination == analysis_root:
        raise ValueError('Output must be a new directory under results/sgb/attributions')
    if destination.exists():
        raise FileExistsError(destination)
    report = audit_pair(root, spec)
    destination.mkdir(parents=True, exist_ok=False)
    for name, value in [('report.json', json.dumps(report, ensure_ascii=False, indent=2) + '\n'),
                        ('report.md', markdown(report))]:
        with (destination / name).open('x', encoding='utf-8') as stream:
            stream.write(value)
    return report
