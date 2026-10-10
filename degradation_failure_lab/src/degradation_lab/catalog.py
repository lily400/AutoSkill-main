from pathlib import Path
from .io import inside, read, sha256
from .schema import check, unique


class SourceManager:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.catalog = check('catalog', read(self.root / 'data/catalog.json'))
        unique(self.catalog['datasets'], 'dataset_id')
        self.sources, self.datasets = {}, {}
        for dataset in self.catalog['datasets']:
            sid_set = set()
            for path in dataset['source_manifests']:
                source = check('source', read(inside(self.root, path)))
                sid = source['source_id']
                if sid in self.sources: raise ValueError('Duplicate source_id: ' + sid)
                self.verify(source)
                self.sources[sid] = source
                sid_set.add(sid)
            self.datasets[dataset['dataset_id']] = sid_set

    def verify(self, source):
        check('source', source)
        path = inside(self.root, source['local_path'])
        if sha256(path) != source['sha256']: raise ValueError('Source hash mismatch: ' + source['source_id'])
        if 'bytes' in source and path.stat().st_size != source['bytes']: raise ValueError('Source byte count mismatch')
        if source['classification'] == 'OFFICIAL_PAPER_DATA' and not source['paper_snapshot_verified']:
            raise ValueError('Paper snapshot must be explicitly verified')
        if source['classification'] != 'CUSTOM_TEST_DATA':
            import re
            if not re.fullmatch(r'[0-9a-f]{40}', source['source_commit']):
                raise ValueError('Official repository source requires a pinned full commit')
            if not source['source_url'].startswith('https://'): raise ValueError('Official source URL must be HTTPS')
        return path


class CaseManager:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.sources = SourceManager(root)

    def list_cases(self):
        return [p.parent.name for p in sorted((self.root / 'cases').glob('*/case.json'))]

    def load(self, case_id):
        base = inside(self.root, 'cases/' + case_id)
        case = check('case', read(base / 'case.json'))
        rules = check('rules', read(base / 'rules.json'))
        conditions = check('conditions', read(base / 'conditions.json'))
        if {case['case_id'], rules['case_id'], conditions['case_id']} != {case_id}:
            raise ValueError('Case identifiers disagree with directory')
        if not set(case['source_ids']).issubset(self.sources.datasets.get(case['dataset_id'], set())):
            raise ValueError('Case sources must belong to dataset')
        if not inside(self.root, case['generation_config']).is_file(): raise ValueError('Missing generation configuration')
        unique(rules['rules'], 'rule_id'); unique(conditions['conditions'], 'condition_id')
        for rule in rules['rules']:
            self.evidence(case, rule['source_evidence'])
        provenance = rules['provenance']
        if bool(provenance.get('file')) != bool(provenance.get('sha256')): raise ValueError('Incomplete rules provenance')
        if provenance and sha256(inside(self.root, provenance['file'])) != provenance['sha256']:
            raise ValueError('Original rule checklist changed')
        return {'case': case, 'rules': rules, 'conditions': conditions}

    def evidence(self, case, anchors):
        for anchor in anchors:
            if anchor['source_id'] not in case['source_ids']: raise ValueError('Unknown evidence source')
            path = self.sources.verify(self.sources.sources[anchor['source_id']])
            if max(anchor['lines']) > len(path.read_text(encoding='utf-8').splitlines()):
                raise ValueError('Evidence line outside original source')

    def condition(self, bundle, condition_id):
        case = bundle['case']
        candidates = [c for c in bundle['conditions']['conditions'] if c['condition_id'] == condition_id]
        if len(candidates) != 1: raise ValueError('Unknown condition: ' + condition_id)
        condition = candidates[0]
        if condition['kind'] == 'clean' and (condition['operator'] is not None or condition['parameters']):
            raise ValueError('Clean condition cannot apply an operator')
        if condition['kind'] == 'degraded' and not condition['operator']:
            raise ValueError('Degraded condition requires operator identity; no operator is executed here')
        manifest = check('inputs', read(inside(self.root, condition['input_manifest'])))
        if (manifest['case_id'], manifest['condition_id']) != (case['case_id'], condition_id):
            raise ValueError('Input manifest identifiers disagree')
        unique(manifest['inputs'], 'input_id')
        if set(x['source_id'] for x in manifest['inputs']) != set(case['source_ids']):
            raise ValueError('Every case source must have a condition input')
        for item in manifest['inputs']:
            source = self.sources.sources[item['source_id']]
            self.sources.verify(source)
            if item['source_sha256'] != source['sha256']: raise ValueError('Parent source hash mismatch')
            if sha256(inside(self.root, item['path'])) != item['sha256']: raise ValueError('Condition input hash mismatch')
            if condition['kind'] == 'clean' and item['sha256'] != source['sha256']:
                raise ValueError('Clean input differs from original')
            if condition['kind'] == 'degraded' and item['sha256'] == source['sha256']:
                raise ValueError('Degraded input must differ from original; duplicated clean bytes are not a degradation')
        return condition, manifest
