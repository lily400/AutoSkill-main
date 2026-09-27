"""Versioned JSON Schemas; only the documented subset is used by our validator."""
from pathlib import Path
from evidence import save

VERSION = '4.0'
S = {'type': 'string', 'minLength': 1}
TEXT = {'type': 'string'}
ID = {'type': 'string', 'pattern': r'^[A-Za-z0-9][A-Za-z0-9_.-]*$'}
HASH = {'type': 'string', 'pattern': r'^[a-f0-9]{64}$'}
INT = {'type': 'integer', 'minimum': 0}
POS = {'type': 'integer', 'minimum': 1}
BOOL = {'type': 'boolean'}
NUM = {'type': 'number'}
NULL = {'type': 'null'}
ANY = {'type': 'object'}

def enum(*values): return {'enum': list(values)}
def nullable(spec): return {'anyOf': [spec, NULL]}
def arr(item, minimum=0): return {'type': 'array', 'items': item, 'minItems': minimum}
def mapping(value): return {'type': 'object', 'additionalProperties': value}
def obj(**fields):
    return {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}
def record(**fields): return obj(schema_version=enum(VERSION), **fields)

SPLIT = enum('development', 'validation', 'heldout_test')
OFFICIAL = obj(domain=S, domain_type=S, family_name=S)
RULE = obj(rule_id=ID, source_text=S)
ERROR = obj(record=nullable(POS), field=nullable(S), message=TEXT)
EXPECTED = obj(outcome=enum('success','error'), outputs=mapping(TEXT), error_record=nullable(POS), error_field=nullable(S))
CHECK = obj(name=S, passed=BOOL, reason=TEXT)

SCHEMAS = {
    'case': record(case_id=ID, case_key=ID, version=POS, title=S, status=enum('draft','frozen'),
        source_id=ID, source_version=S, family_id=ID, split=SPLIT, usage=enum('development_only','research'),
        source_record=S, source_file=S, source_sha256=HASH, contract_file=S, task_files=arr(S,1),
        variant_files=arr(S,1), official=OFFICIAL),
    'source': record(case_id=ID, source_id=ID, source_version=S, family_id=ID,
        origin=obj(kind=enum('locally_authored','repository','publication','web','other'), uri=nullable(S),
            revision=nullable(S), license=nullable(S), unknown_reason=nullable(S)),
        document_file=S, document_sha256=HASH, description=S),
    'family': record(family_id=ID, name=S, grouping_basis=S, source_ids=arr(ID,1),
        review_status=enum('pending','reviewed'), review_note=S),
    'split': record(split_id=ID, version=POS, status=enum('draft','frozen'), policy=S,
        assignments=arr(obj(case_id=ID, source_id=ID, family_id=ID, split=SPLIT),1),
        heldout_locked=BOOL, formal_ready=BOOL, reason=S),
    'variant': record(variant_id=ID, version=POS, case_id=ID, source_id=ID, source_version=S,
        family_id=ID, condition=enum('clean','degraded'), input_file=S, input_sha256=HASH,
        clean_variant_id=ID, clean_sha256=HASH, contract_id=ID, degradation_file=nullable(S), status=enum('frozen')),
    'degradation': record(degradation_id=ID, case_id=ID, variant_id=ID, type=S,
        severity=obj(value={'type':'number','minimum':0}, unit=S), seed=INT,
        generator=obj(file=S, sha256=HASH, version=S), parameters=ANY,
        edits=arr(obj(start=INT, end=INT, before=TEXT, after=TEXT),1),
        recoverability=obj(status=enum('pending','recoverable','irrecoverable','conflicting'),
            reviewer=nullable(S), evidence=S, rule_ids=arr(ID))),
    'contract': record(contract_id=ID, case_id=ID, version=POS, source_id=ID, source_version=S,
        source_sha256=HASH, rules=arr(RULE,1), review_status=enum('pending','reviewed'), review_note=S),
    'task': record(task_id=ID, case_id=ID, source_id=ID, family_id=ID, split=SPLIT,
        purpose=SPLIT, contract_id=ID, judge_id=ID, prompt=S, inputs=mapping(TEXT), expected=EXPECTED,
        covered_rule_ids=arr(ID), coverage_note=S),
    'judge': record(judge_id=ID, case_id=ID, version=S, implementation_file=S, implementation_sha256=HASH,
        reference_file=S, reference_sha256=HASH, policy=S, limitations=arr(S)),
    'run': record(run_id=ID, case_id=ID, source_id=ID, source_version=S, family_id=ID, split=SPLIT,
        variant_id=ID, method_id=ID, generation_repeat=POS, kind=enum('preflight','generation'),
        status=enum('preflight','preflight_only','running','completed_unreviewed','failed','timeout','interrupted','artifact_validation_failed','framework_changed'),
        input_sha256=HASH, dataset_freeze_sha256=HASH, comparison_fingerprint=nullable(HASH),
        structural_pass=nullable(BOOL), semantic_status=enum('pending','not_applicable'), execution_status=enum('not_run'),
        failure=obj(category=enum('infrastructure','generation','evidence','interrupted','unknown','none'),
            stage=nullable(S), evidence=arr(S)), program_ir_status=enum('not_applicable','not_run'),
        started_at_utc=S, finished_at_utc=nullable(S)),
    'execution': record(execution_id=ID, case_id=ID, source_id=ID, family_id=ID, task_id=ID,
        contract_id=ID, judge_id=ID, run_id=nullable(ID), mode=enum('generated_skill','reference','no_skill'),
        execution_repeat=POS, status=enum('not_run','running','completed','failed','blocked'),
        failure_category=enum('none','infrastructure','generation','execution','unknown'), reason=S,
        executor=obj(id=ID, version=S, model=nullable(S)), input_before=mapping(HASH), input_after=mapping(HASH),
        actual_outputs=mapping(TEXT), error=nullable(ERROR), exit_code=nullable({'type':'integer'}),
        started_at_utc=S, finished_at_utc=nullable(S), dataset_freeze_sha256=HASH,
        run_checksums_sha256=nullable(HASH), standard_hashes=mapping(HASH)),
    'judgment': record(judgment_id=ID, execution_id=ID, case_id=ID, task_id=ID, judge_id=ID,
        status=enum('passed','failed','not_run'), passed=nullable(BOOL), checks=arr(CHECK), reason=S,
        execution_checksums_sha256=HASH, judge_sha256=HASH, created_at_utc=S),
    'comparison': record(comparison_id=ID, clean_run_id=ID, degraded_run_id=ID, case_id=ID,
        source_id=ID, family_id=ID, method_id=ID, generation_repeat=POS, comparable=BOOL, reasons=arr(S),
        clean_status=ANY, degraded_status=ANY, eligible_for_skill_quality_comparison=BOOL,
        semantic_score_delta=nullable(NUM), task_success_delta=nullable(NUM),
        metrics_status=enum('not_run','computed'), metric_reason=S),
    'program_ir': record(ir_id=ID, case_id=ID, source_id=ID, variant_id=ID, run_id=ID, ir_version=S,
        status=enum('not_run','generated','invalid','validated'), goal=nullable(S), inputs=arr(S), preconditions=arr(S),
        steps=arr(obj(step_id=ID, action=S, depends_on=arr(ID), kind=enum('action','for_each'))),
        branches=arr(obj(condition=S, then_step_ids=arr(ID), else_step_ids=arr(ID))),
        invariants=arr(S), outputs=arr(S), checks=arr(S), unresolved=arr(S),
        provenance_file=nullable(S), validation_reason=S),
}

def export(root):
    for name, schema in SCHEMAS.items():
        save(Path(root)/'schemas'/(name+'.schema.json'),
             {'$schema':'https://json-schema.org/draft/2020-12/schema', 'title':name, **schema})

if __name__ == '__main__': export(Path(__file__).resolve().parents[1])
