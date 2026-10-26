"""Hash-bound reviewer annotations and temporally ordered rule-delivery evidence."""
from copy import deepcopy
from difflib import unified_diff
import json
import re

from degradation_lab.io import sha256
from downstream_eval.integration.skill_usage import _compact
from .attribution_contract import STAGES


def _pointer(document, pointer):
    value, ancestors = document, [document]
    if pointer == '':
        return value, ancestors
    if not isinstance(pointer, str) or not pointer.startswith('/'):
        raise ValueError('Invalid JSON pointer')
    for key in pointer[1:].split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list) and (not key.isdecimal() or (len(key) > 1 and key[0] == '0')):
            raise ValueError('Invalid JSON array index')
        try:
            value = value[int(key)] if isinstance(value, list) else value[key]
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise ValueError('Unresolvable JSON pointer: ' + pointer) from error
        ancestors.append(value)
    return value, ancestors


def _locate(path, locator):
    kind, at = locator['kind'], locator['value']
    text = path.read_text(encoding='utf-8')
    if kind == 'file':
        if at is not None:
            raise ValueError('File locator takes null')
        return text, []
    if kind == 'lines':
        lines = text.splitlines()
        if not isinstance(at, list) or not at or len(set(at)) != len(at) or any(
                type(i) is not int or i < 1 or i > len(lines) for i in at):
            raise ValueError('Invalid evidence line numbers')
        return '\n'.join(lines[i - 1] for i in at), []
    if kind == 'json_pointer':
        return _pointer(json.loads(text), at)
    if type(at) is not int or at < 1:
        raise ValueError('Event/step locator requires a positive integer')
    if kind == 'jsonl_event':
        events = [json.loads(s) for s in text.splitlines() if s.strip()]
        if at > len(events):
            raise ValueError('Event outside evidence log')
        return events[at - 1], [events[at - 1]]
    matches = [s for s in json.loads(text)['steps'] if s.get('step_id') == at]
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous trajectory step')
    return matches[0], matches


def _verify_annotation(files, entry, trials, generations):
    path = files.path(entry['artifact_path'])
    owner = generations.get(entry['run_id'])
    allowed = False
    if owner:
        allowed = path.is_relative_to(files.path(owner['path']))
        for item in owner['source_inputs'].get('inputs', []):
            original = item.get('original_path')
            if original and path == files.path(original):
                allowed = entry['artifact_sha256'] == item.get('source_sha256')
    for trial in trials.values():
        if trial and entry['run_id'] == trial['run_id']:
            run = files.path(trial['paths']['run'])
            allowed |= path.is_relative_to(run)
            manifest = files.json(run / 'execution_manifest.json', {})
            for name, expected in manifest.items():
                if path == files.path(name) and expected == entry['artifact_sha256']:
                    allowed = True
    if not allowed:
        raise ValueError('Evidence belongs to another run or unbound artifact: ' + entry['evidence_id'])
    result = deepcopy(entry)
    result['resolved_path'] = path.relative_to(files.root).as_posix()
    if not path.is_file() or entry['artifact_sha256'] is None:
        if entry['claim_status'] != 'unknown' or not entry['missing_reason']:
            raise ValueError('Missing evidence requires unknown status and a reason')
        result.update(verification='unknown', excerpt=None)
        return result, None
    if sha256(files.track(path, entry['artifact_path'])) != entry['artifact_sha256']:
        raise ValueError('Evidence hash mismatch: ' + entry['evidence_id'])
    value, ancestors = _locate(path, entry['locator'])
    entity = entry['entity_id']
    if entity:
        ids = {str(a[k]) for a in ancestors if isinstance(a, dict)
               for k in ('window_id', 'support_id', 'draft_id', 'skill_id', 'doc_id', 'id', 'step_id') if k in a}
        if path.name == 'SKILL.md':
            ids.update(re.findall(r'^id: "([^"\n]+)"', path.read_text(encoding='utf-8'), re.M))
        if entry['stage'] == 'source' and owner:
            ids.update(i['source_id'] for i in owner['source_inputs'].get('inputs', []))
        if entity not in ids:
            raise ValueError('Evidence entity does not match locator: ' + entry['evidence_id'])
    result.update(verification='verified', excerpt=value)
    return result, next((a for a in reversed(ancestors) if isinstance(a, dict)), None)


def rule_delivery(files, trial, link):
    result = {'before_action': None, 'successful_request_numbers': [], 'action_event': link['action_event'],
              'behavioral_use': 'UNKNOWN', 'reason': 'Missing rule, action, or observation evidence'}
    if not trial or not link['skill_id'] or not link['skill_lines'] or link['action_event'] is None:
        return result
    sid = link['skill_id']
    known = {x['skill_id']: x for x in (trial.get('usage') or {}).get('per_skill', [])}
    if sid not in known:
        raise ValueError('Rule Skill is not in this trial: ' + sid)
    skill = files.path(trial['paths']['stage']) / sid / 'SKILL.md'
    text = files.track(skill).read_text(encoding='utf-8')
    lines = text.splitlines()
    requested = link['skill_lines']
    if any(n > len(lines) for n in requested):
        raise ValueError('Rule excerpt exceeds frozen Skill')
    frontmatter = next((i + 1 for i, line in enumerate(lines[1:], 1) if line == '---'), 0)
    if min(requested) <= frontmatter:
        raise ValueError('Body rule evidence must be outside frontmatter')
    fragment = _compact('\n'.join(lines[n - 1] for n in requested))
    if not fragment:
        raise ValueError('Rule excerpt is empty')
    observer = files.path(trial['paths']['trial']) / 'p1-observer'
    requests = files.events(observer / 'p1-model-requests.jsonl')
    http = files.events(observer / 'p1-model-http.jsonl')
    tools = files.events(observer / 'p1-tool-actions.jsonl')
    reads = files.events(observer / 'p1-skill-reads.jsonl')
    summary = files.json(observer / 'p1-summary.json')
    if any(x is None for x in (requests, http, tools, reads, summary)):
        return result
    if link['action_event'] > len(tools):
        raise ValueError('Action event exceeds this trial log')
    action = tools[link['action_event'] - 1]
    if action.get('stage') != 'submitted' or action.get('actor') != 'model_tool':
        raise ValueError('Action anchor is not an observed model tool submission')
    if summary.get('mode') != 'paid':
        result['reason'] = 'Controlled probe is not model-directed use'
        return result
    successful = {e['logical_request_number']: e for e in http
                  if e.get('http_status') is not None and 200 <= e['http_status'] < 300}
    if not successful or action.get('time') is None:
        return result
    complete_clock = True
    for number, request in enumerate(requests, 1):
        if number not in successful:
            continue
        if request.get('mode') != 'paid':
            continue
        when, received = request.get('time'), successful[number].get('time')
        if when is None or received is None:
            complete_clock = False
            continue
        contexts = '\n'.join(m.get('content', '') for m in request.get('messages', [])
                             if m.get('role') != 'assistant' and isinstance(m.get('content'), str))
        contexts = re.sub(r'<available_skills\b[^>]*>.*?</available_skills>', '', contexts, flags=re.S)
        prior_read = any(e.get('skill_id') == sid and e.get('actor') == 'model_tool'
                         and e.get('time') is not None and e['time'] <= when for e in reads)
        if (when <= received < action['time'] and fragment in _compact(contexts)
                and prior_read and known[sid]['model_file_access_observed'] is True):
            result['successful_request_numbers'].append(number)
    found = bool(result['successful_request_numbers'])
    result['before_action'] = True if found else False if complete_clock else None
    result['reason'] = ('Frozen rule excerpt reached a successful request before the anchored action'
                        if found else 'No qualifying pre-action excerpt match; absence of reliance is not established')
    return result


def _completed_intervention(files, intervention, evidence, trials, generations):
    """Bind a canonical text patch to the actual two artifacts, not just a status flag."""
    parent, child, patch = (evidence[intervention[k]] for k in
                            ('parent_evidence_id', 'child_evidence_id', 'patch_evidence_id'))
    if any(e['locator']['kind'] != 'file' for e in (parent, child, patch)):
        raise ValueError('Completed intervention requires whole-file patch evidence')
    if parent['artifact_sha256'] == child['artifact_sha256']:
        raise ValueError('Intervention did not change the artifact')
    before, after = (files.path(e['artifact_path']).read_text(encoding='utf-8') for e in (parent, child))
    expected = ''.join(unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                    fromfile='before', tofile='after'))
    if files.path(patch['artifact_path']).read_text(encoding='utf-8') != expected:
        raise ValueError('Patch does not describe the parent/child change')
    scope = intervention['scope']
    remaining = []
    for side, entry in zip(('reference', 'target'), (parent, child)):
        trial = trials[side]
        p = files.path(entry['artifact_path'])
        if scope == 'submission':
            bound = entry['artifact_sha256'] == trial['oracle'].get('candidate_sha256')
            remaining.append(trial['skill_files'])
        elif scope == 'loading_protocol':
            bound = p == files.path(trial['paths']['run']) / 'configs' / (trial['label'] + '.json')
            remaining.append(trial['skill_files'])
        elif scope == 'skill':
            staged = files.path(trial['paths']['stage'])
            bound = p.is_relative_to(staged)
            rel = p.relative_to(staged).as_posix() if bound else ''
            bound &= trial['skill_files'].get(rel) == entry['artifact_sha256']
            remaining.append({k: v for k, v in trial['skill_files'].items() if k != rel})
        else:
            generation = generations.get(trial['generator_run_id'])
            inputs = generation['source_inputs']['inputs'] if generation else []
            matched = [i for i in inputs if p == files.path(generation['path']) / i['path']
                       and i['sha256'] == entry['artifact_sha256']]
            bound = len(matched) == 1
            remaining.append([(i['source_id'], i['sha256']) for i in inputs if i not in matched])
        if not bound:
            raise ValueError('Intervention artifact is not bound to its trial: ' + side)
    if remaining[0] != remaining[1]:
        raise ValueError('Intervention changed artifacts outside its declared target')


def review_evidence(files, spec, trials, generations, comparability, changes):
    evidence, entities = {}, {}
    for entry in spec['evidence']:
        row, entity = _verify_annotation(files, entry, trials, generations)
        evidence[row['evidence_id']], entities[row['evidence_id']] = row, entity
    def refs(ids, verified=False):
        if any(i not in evidence for i in ids):
            raise ValueError('Unknown evidence reference')
        rows = [evidence[i] for i in ids]
        if verified and (not rows or any(x['verification'] != 'verified' for x in rows)):
            raise ValueError('A supported statement requires verified evidence')
        return rows
    rules = []
    declared_interventions = {i['intervention_id']: i for i in spec['interventions']}
    for original in spec['rules']:
        rule = deepcopy(original)
        generation = generations.get(rule['generator_run_id'])
        if not generation or rule['parent_rule_id'] not in {r['rule_id'] for r in generation['rules']}:
            raise ValueError('Rule does not belong to the selected generator checklist')
        stages = [s['stage'] for s in rule['stages']]
        if stages != sorted(set(stages), key=STAGES.index):
            raise ValueError('Rule stages must be unique and in pipeline order')
        stage_entities = {}
        intervention = declared_interventions.get(rule.get('intervention_id'))
        if rule.get('intervention_id') and intervention is None:
            raise ValueError('Rule version references an unknown intervention')
        for stage in rule['stages']:
            entries = refs(stage['evidence_ids'], stage['status'] != 'unknown')
            allowed_runs = {rule['generator_run_id']}
            if intervention and stage['stage'] == 'skill' and intervention['scope'] == 'skill':
                treatment = trials.get('target')
                if treatment and intervention['treatment'] == spec['target']:
                    allowed_runs.add(treatment['run_id'])
            if any(e['run_id'] not in allowed_runs or e['stage'] != stage['stage'] for e in entries):
                raise ValueError('Rule stage evidence belongs to another run/stage')
            stage_entities[stage['stage']] = [entities[e['evidence_id']] for e in entries if entities[e['evidence_id']]]
        # Verify entity relationships when adjacent anchors are supplied. Semantic omission remains manual.
        windows = {e['window_id'] for e in stage_entities.get('window', []) if 'window_id' in e}
        supports = {e['support_id'] for e in stage_entities.get('support', []) if 'support_id' in e}
        drafts = {e['draft_id'] for e in stage_entities.get('draft', []) if 'draft_id' in e}
        for support in stage_entities.get('support', []):
            if windows and support.get('metadata', {}).get('window_id') not in windows:
                raise ValueError('Support does not belong to mapped window')
        for draft in stage_entities.get('draft', []):
            if supports and not supports.intersection(draft.get('support_ids', [])):
                raise ValueError('Draft does not link mapped support')
        for spec_row in stage_entities.get('spec', []):
            if drafts and not drafts.intersection(spec_row.get('metadata', {}).get('source_draft_ids', [])):
                raise ValueError('Compiled Skill does not link mapped draft')
        compiled_ids = {e['skill_id'] for e in stage_entities.get('spec', []) if 'skill_id' in e}
        for stage in rule['stages']:
            if stage['stage'] in ('registered', 'skill') and compiled_ids:
                if any(evidence[e]['entity_id'] not in compiled_ids for e in stage['evidence_ids']):
                    raise ValueError('Registered/final Skill does not match the mapped compiled entity')
        rule['first_observed_loss'] = next((s['stage'] for s in rule['stages']
                                         if s['status'] in ('omitted', 'altered')), None)
        rule['localization_limit'] = 'Earliest annotated loss, not a causal verdict; unobserved stages remain unknown.'
        for link in rule['downstream_links']:
            trial = trials[link['side']]
            if trial and trial['generator_run_id'] != rule['generator_run_id']:
                raise ValueError('Rule linked to another generation trial')
            assertions = (trial or {}).get('assertions') or {}
            if any(name not in assertions for name in link['assertions']):
                raise ValueError('Rule references an unknown Oracle assertion')
            if link['oracle_not_covered'] != (not link['assertions']):
                raise ValueError('Oracle coverage must be explicit')
            link['delivery'] = rule_delivery(files, trial, link)
        rules.append(rule)
    rule_ids = {r['rule_id'] for r in rules}
    interventions = {i['intervention_id']: deepcopy(i) for i in spec['interventions']}
    for intervention in interventions.values():
        if not set(intervention['target_rule_ids']) <= rule_ids:
            raise ValueError('Intervention references an unknown rule')
        refs([intervention['parent_evidence_id']], True)
        if intervention['status'] == 'completed':
            if (spec['comparison_kind'] != 'intervention' or comparability != 'eligible'
                    or intervention['control'] != spec['reference'] or intervention['treatment'] != spec['target']):
                raise ValueError('Completed intervention requires this eligible controlled pair')
            refs([intervention['patch_evidence_id'], intervention['child_evidence_id']], True)
            _completed_intervention(files, intervention, evidence, trials, generations)
    claims = deepcopy(spec['claims'])
    for claim in claims:
        refs(claim['evidence_ids'], claim['status'] in ('observed', 'intervention_supported'))
        if not set(claim['rule_ids']) <= rule_ids:
            raise ValueError('Claim references an unknown rule')
        if claim['primary_cause'] and claim['primary_cause'] not in claim['candidate_causes']:
            raise ValueError('Primary cause must be one of the reviewed candidates')
        if claim['scope'] == 'causal' and claim['status'] == 'observed':
            raise ValueError('Observed differential outcomes alone cannot establish causation')
        if claim['status'] in ('inferred', 'hypothesis') and not (claim['alternatives'] or claim['missing_evidence']):
            raise ValueError('Inference or hypothesis requires alternatives or missing evidence')
        claim['intervention_scopes'] = sorted({interventions[i]['scope'] for i in claim['intervention_ids'] if i in interventions})
        if claim['status'] == 'intervention_supported':
            covered = {a for r in rules if r['rule_id'] in claim['rule_ids']
                       for link in r['downstream_links'] for a in link['assertions']}
            if (not claim['intervention_ids'] or any(i not in interventions or interventions[i]['status'] != 'completed'
                    for i in claim['intervention_ids']) or not any(
                        c['assertion'] in covered and c['difference'] in ('possible_help', 'possible_harm') for c in changes)):
                raise ValueError('Intervention support requires completed intervention and measured differential evidence')
            if any(not set(claim['rule_ids']) <= set(interventions[i]['target_rule_ids']) for i in claim['intervention_ids']):
                raise ValueError('Intervention did not target the claimed rules')
        if claim['primary_cause'] == 'agent_rule_misapplication' and claim['status'] not in ('hypothesis', 'unknown'):
            relevant = [r for r in rules if r['rule_id'] in claim['rule_ids']]
            if not relevant or not all(any(s['stage'] == 'skill' and s['status'] == 'preserved' for s in r['stages'])
                    and any(l['delivery']['before_action'] is True for l in r['downstream_links']) for r in relevant):
                raise ValueError('Rule misapplication requires pre-action delivery evidence')
        if not set(claim['intervention_ids']) <= set(interventions):
            raise ValueError('Unknown intervention reference')
    return {'review_evidence': list(evidence.values()), 'rule_reviews': rules,
            'claims': claims, 'interventions': list(interventions.values()),
            'semantic_validation': 'Reviewer annotations; hash/entity checks do not certify semantic truth.'}
