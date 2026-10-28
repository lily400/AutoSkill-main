"""Strict dependency-free validation of the published schemas' used keywords.

This is deliberately not a general JSON Schema engine. Unknown keywords fail.
All schemas in schemas/ are also valid JSON Schema Draft 2020-12 documents.
"""
import re

STR = {'type': 'string', 'minLength': 1}
ID = dict(STR, pattern=r'^[A-Za-z0-9][A-Za-z0-9_-]*$')
HASH = dict(STR, pattern=r'^[0-9a-f]{64}$')
CASE_ID = dict(STR, pattern=r'^case[0-9]{3,}_[a-z0-9_]+$')
PARAMS = {'type': 'object'}
NULL_STR = {'type': ['string', 'null']}


def array(item, minimum=0, unique=False):
    return {'type': 'array', 'items': item, 'minItems': minimum, 'uniqueItems': unique}


def obj(fields, optional=()):
    return {'type': 'object', 'properties': fields,
            'required': [k for k in fields if k not in optional], 'additionalProperties': False}


ANCHOR = obj({'source_id': ID, 'lines': array({'type': 'integer', 'minimum': 1}, 1)})
SCHEMAS = {
    'catalog': obj({'schema_version': {'const': 1}, 'datasets': array(obj({
        'dataset_id': ID, 'description': STR, 'source_manifests': array(STR, 1, True)}), 1)}),
    'source': obj({
        'source_id': ID, 'source_url': STR, 'source_repository': STR,
        'source_commit': STR, 'source_path': STR, 'license': STR,
        'downloaded_at': STR, 'sha256': HASH, 'document_type': STR,
        'corresponding_cli_command': NULL_STR, 'classification': {'enum': [
            'OFFICIAL_PAPER_DATA', 'RECONSTRUCTED_OFFICIAL_SOURCE', 'CUSTOM_TEST_DATA', 'PUBLISHED_DATASET_SNAPSHOT']},
        'paper_snapshot_verified': {'type': 'boolean'}, 'local_path': STR,
        'bytes': {'type': 'integer', 'minimum': 1},
        'variant': {'enum': ['clean']}, 'transform': {'const': None},
        'provenance': obj({'file': STR, 'sha256': HASH})
    }, ('corresponding_cli_command', 'bytes', 'variant', 'transform', 'provenance')),
    'case': obj({'schema_version': {'const': 1}, 'case_id': CASE_ID, 'dataset_id': ID,
        'title': STR, 'source_ids': array(ID, 1, True), 'generation_config': STR,
        'pipeline_overrides': obj({'domain': STR, 'domain_type': STR, 'family_name': STR},
                                 ('domain', 'domain_type', 'family_name')),
        'execution_gate': STR}, ('execution_gate',)),
    'rules': obj({'schema_version': {'const': 1}, 'case_id': CASE_ID,
        'classification': {'const': 'CUSTOM_TEST_DATA'}, 'provenance': obj({
            'file': STR, 'sha256': HASH}, ('file', 'sha256')),
        'rules': array(obj({'rule_id': ID, 'text': STR, 'source_evidence': array(ANCHOR, 1),
                           'rule_type': STR, 'annotation_status': {'enum': [
                               'analyst_checklist', 'human_annotated', 'pending']}}), 1)}),
    'conditions': obj({'schema_version': {'const': 1}, 'case_id': CASE_ID,
        'conditions': array(obj({'condition_id': ID, 'kind': {'enum': ['clean', 'degraded']},
            'input_manifest': STR, 'operator': NULL_STR, 'parameters': PARAMS}), 1)}),
    'inputs': obj({'schema_version': {'const': 1}, 'case_id': CASE_ID, 'condition_id': ID,
        'inputs': array(obj({'input_id': ID, 'source_id': ID, 'source_sha256': HASH,
                            'path': STR, 'sha256': HASH}), 1)}),
    'evaluation': obj({'schema_version': {'const': 1}, 'evaluation_id': ID,
        'case_id': CASE_ID, 'condition_id': ID, 'run_id': ID, 'created_at': STR,
        'method': {'enum': ['manual', 'automatic']}, 'reviewer': STR,
        'provenance': obj({'file': STR, 'sha256': HASH}, ('file', 'sha256')),
        'records': array(obj({'record_id': ID, 'rule_id': ID,
            'judgment_scope': {'enum': ['rule_preservation', 'generated_addition']},
            'status': {'enum': ['unreviewed', 'correct', 'incorrect', 'uncertain']},
            'source_evidence': array(ANCHOR, 1), 'skill_ids': array(STR, 0, True),
            'trace_refs': array(obj({'stage': {'enum': ['window', 'support', 'draft', 'spec', 'skill']},
                                     'entity_id': STR})),
            'generated_evidence': array(obj({'skill_id': STR, 'lines': array(
                {'type': 'integer', 'minimum': 1}, 1)})),
            'error_types': array({'enum': ['condition_error', 'exception_omission',
                'parameter_mismatch', 'unsupported_addition', 'rule_omission', 'template_residue']}, 0, True),
            'notes': {'type': 'string'}}), 1)})
}


def validate(value, schema, path='$'):
    supported = {'$schema', 'title', 'type', 'const', 'enum', 'properties', 'required',
                 'additionalProperties', 'items', 'minItems', 'uniqueItems', 'minimum', 'minLength', 'pattern'}
    if set(schema) - supported:
        raise ValueError('Unsupported schema keyword')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'boolean': bool, 'null': type(None)}
    if 'type' in schema:
        ts = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        if not any(type(value) is types[t] for t in ts):
            raise ValueError(path + ': invalid type')
    if 'const' in schema and (value != schema['const'] or type(value) != type(schema['const'])):
        raise ValueError(path + ': invalid constant')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(path + ': invalid enum')
    if isinstance(value, dict):
        missing = set(schema.get('required', [])) - value.keys()
        extra = value.keys() - schema.get('properties', {}).keys()
        if missing or (schema.get('additionalProperties') is False and extra):
            raise ValueError(f'{path}: missing={sorted(missing)}, unknown={sorted(extra)}')
        for k, s in schema.get('properties', {}).items():
            if k in value: validate(value[k], s, path + '.' + k)
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0): raise ValueError(path + ': too few items')
        if schema.get('uniqueItems') and any(v in value[:i] for i,v in enumerate(value)):
            raise ValueError(path + ': duplicate items')
        for i,v in enumerate(value): validate(v, schema['items'], f'{path}[{i}]')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0): raise ValueError(path + ': empty string')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ValueError(path + ': invalid identifier/hash')
    if type(value) is int and value < schema.get('minimum', value):
        raise ValueError(path + ': below minimum')
    return value


def check(kind, value):
    return validate(value, SCHEMAS[kind])


def unique(items, key):
    values = [item[key] for item in items]
    if len(values) != len(set(values)): raise ValueError('Duplicate ' + key)
