"""Versioned offline attribution input contract; uses the lab's schema validator."""
from degradation_lab.schema import STR, HASH, ID, array, obj, validate

CAUSES = ['source_missing_or_ambiguous', 'window_selection_loss', 'evidence_or_draft_loss',
          'compile_or_register_change', 'skill_delivery_failure', 'agent_rule_misapplication',
          'environment_tool_or_oracle', 'insufficient_evidence']
FUNCTIONAL = ['APM', 'EM.BDR', 'EM.ESM', 'TIF.OWG', 'TIF.IRF', 'TIF.RRO', 'AM', None]
STAGES = ['source', 'window', 'support', 'draft', 'spec', 'registered', 'skill']
STATUS = ['observed', 'inferred', 'hypothesis', 'intervention_supported', 'unknown']
NULL_TEXT = {'type': ['string', 'null']}
NULL_HASH = {'type': ['string', 'null'], 'pattern': HASH['pattern']}
REFERENCE = obj({'run_path': STR, 'label': STR})
EVIDENCE = obj({
    'evidence_id': ID, 'artifact_path': STR, 'artifact_sha256': NULL_HASH,
    'run_id': STR, 'stage': STR, 'entity_id': NULL_TEXT,
    'locator': obj({'kind': {'enum': ['file', 'lines', 'json_pointer', 'jsonl_event', 'trajectory_step']},
                    'value': {'type': ['string', 'integer', 'array', 'null'],
                              'items': {'type': 'integer', 'minimum': 1}},
                    'coordinate_space': {'enum': ['original_source', 'generation_input',
                        'normalized_text', 'skill_body', 'artifact']}}),
    'claim_status': {'enum': STATUS}, 'claim': STR, 'missing_reason': NULL_TEXT})
RULE = obj({
    'rule_id': STR, 'parent_rule_id': STR, 'generator_run_id': STR, 'claim': STR,
    'reviewer': STR, 'review_status': {'enum': ['provisional', 'reviewed']},
    'stages': array(obj({'stage': {'enum': STAGES}, 'status': {'enum': [
        'preserved', 'altered', 'omitted', 'ambiguous', 'unknown']},
        'evidence_ids': array(ID), 'rationale': STR}), 1),
    'downstream_links': array(obj({'side': {'enum': ['reference', 'target']},
        'assertions': array(STR, unique=True), 'oracle_not_covered': {'type': 'boolean'},
        'skill_id': NULL_TEXT, 'skill_lines': array({'type': 'integer', 'minimum': 1}, unique=True),
        'action_event': {'type': ['integer', 'null'], 'minimum': 1}, 'interpretation': STR}))})
# Optional for a manually repaired package derived from the same generation run.
RULE['properties']['intervention_id'] = NULL_TEXT
CLAIM = obj({'claim_id': ID, 'rule_ids': array(STR, unique=True),
    'scope': {'enum': ['preservation', 'behavior', 'causal']}, 'status': {'enum': STATUS},
    'text': STR, 'evidence_ids': array(ID, unique=True), 'downstream_category': {'enum': FUNCTIONAL},
    'candidate_causes': array({'enum': CAUSES}, unique=True),
    'primary_cause': {'enum': CAUSES + [None]}, 'alternatives': array(STR),
    'missing_evidence': array(STR), 'reviewer': STR, 'intervention_ids': array(ID, unique=True)})
INTERVENTION = obj({'intervention_id': ID, 'version': STR,
    'status': {'enum': ['planned', 'completed']},
    'scope': {'enum': ['source', 'skill', 'submission', 'loading_protocol']},
    'parent_evidence_id': ID, 'patch_evidence_id': NULL_TEXT, 'child_evidence_id': NULL_TEXT,
    'target_rule_ids': array(STR, 1, True), 'expected_effect': STR,
    'control': dict(REFERENCE, type=['object', 'null']),
    'treatment': dict(REFERENCE, type=['object', 'null'])})
SPEC = obj({'schema_version': {'const': 1}, 'analysis_id': ID, 'pair_id': ID,
    'task_id': STR, 'comparison_kind': {'enum': ['no_skill_clean', 'clean_degraded', 'intervention']},
    'reference': dict(REFERENCE, type=['object', 'null']),
    'target': dict(REFERENCE, type=['object', 'null']),
    'evidence': array(EVIDENCE), 'rules': array(RULE), 'claims': array(CLAIM),
    'interventions': array(INTERVENTION)})


def validate_spec(spec):
    validate(spec, SPEC)
    for collection, key in [('evidence', 'evidence_id'), ('claims', 'claim_id'),
                            ('interventions', 'intervention_id')]:
        ids = [r[key] for r in spec[collection]]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate ' + key)
    ids = [(r['rule_id'], r['generator_run_id'], r.get('intervention_id')) for r in spec['rules']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate rule/version')
    return spec


def published_schema():
    return dict(SPEC, title='Offline attribution pair and review specification',
                **{'$schema': 'https://json-schema.org/draft/2020-12/schema'})
