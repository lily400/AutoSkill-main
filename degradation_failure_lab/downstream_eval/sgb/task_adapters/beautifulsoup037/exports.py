"""Controller-owned, session-authenticated Task-037 evidence. Only synthetic fixtures may issue receipts."""
import copy
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import tomllib

from degradation_lab.io import read, sha256
from downstream_eval.integration.harbor_adapter import verify_sources


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class ExportController:
    """Trust anchor lives on the control host, outside Agent/candidate memory and mounts.

    Session HMAC proves controller issuance, NOT successful transport or Oracle isolation.
    There is deliberately no real-export signing path until the Harbor observation hook is reviewed.
    Keys are ephemeral and never serialized. Persisted receipts cannot be independently reverified
    after this controller exits; a durable trust store is a separate runtime prerequisite.
    """
    def __init__(self, root, artifacts, *, task_config, trial_id, fixture):
        if fixture is not True:
            raise RuntimeError('Real export collector NOT_IMPLEMENTED; no runtime authorization')
        from .adapter import TASK_ID
        from .scoring import SOURCE
        if not isinstance(trial_id, str) or not trial_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in trial_id):
            raise ValueError('Explicit safe Trial ID required')
        self.artifacts = Path(artifacts).absolute()
        self.task_config = Path(task_config).absolute()
        if self.task_config.resolve().is_relative_to(self.artifacts.resolve()):
            raise ValueError('Trusted task config cannot be an Agent artifact')
        data = tomllib.loads(self.task_config.read_text(encoding='utf-8'))
        if (data.get('metadata', {}).get('task_id') != TASK_ID
                or data.get('artifacts') != [{'source':SOURCE, 'destination':'workspace/agent_output.py'}]):
            raise ValueError('Task configuration identity or artifact contract mismatch')
        source, lock = verify_sources(Path(root))
        self.trial_id = trial_id
        self._key = secrets.token_bytes(32)
        self.context = {
            'task_id':TASK_ID, 'trial_id':trial_id, 'authority_id':secrets.token_hex(16),
            'artifacts_root':str(self.artifacts), 'task_config_path':str(self.task_config),
            'task_config_sha256':sha256(self.task_config),
            'code_version':{str(p):sha256(p) for p in
                (Path(__file__), Path(root) / 'downstream_eval/sgb/beautifulsoup_scoring.py',
                 Path(root) / 'downstream_eval/sgb/beautifulsoup037.py',
                 Path(root) / 'downstream_eval/sgb/beautifulsoup_exports.py',
                 Path(root) / 'downstream_eval/sgb/beautifulsoup_smoke.py',
                 Path(root) / 'downstream_eval/sgb/task_adapters/__init__.py',
                 Path(root) / 'downstream_eval/sgb/task_adapters/beautifulsoup037/__init__.py',
                 Path(root) / 'downstream_eval/sgb/task_adapters/beautifulsoup037/adapter.py',
                 Path(root) / 'downstream_eval/sgb/task_adapters/beautifulsoup037/scoring.py',
                 Path(root) / 'downstream_eval/sgb/task_adapters/beautifulsoup037/smoke.py',
                 Path(root) / 'downstream_eval/integration/harbor_adapter.py',
                 source / 'src/harbor/trial/artifact_handler.py',
                 source / 'src/harbor/models/trial/artifact_manifest.py')},
            'harbor_version':lock['harbor_version'], 'harbor_commit':lock['harbor_commit'],
        }

    def _mac(self, purpose, value):
        return hmac.new(self._key, purpose.encode() + b'\0' + canonical(value), hashlib.sha256).hexdigest()

    def capture_fixture(self, *, manifest_entries, source_observation):
        """Synthetic counterpart of a future hook AFTER ArtifactHandler.download_artifacts returns.

        manifest_entries represents controller-observed return metadata, independently compared
        with the written host manifest. source_observation is an explicit fixture, not inferred
        from missing local files. No manifest alone proves remote absence.
        """
        from .scoring import SOURCE, DESTINATION, regular_file
        manifest = self.artifacts / 'manifest.json'
        if not regular_file(manifest, self.artifacts) or read(manifest) != manifest_entries:
            raise ValueError('Controller metadata differs from host manifest')
        if source_observation not in ('file', 'absent', 'unknown'):
            raise ValueError('Explicit source observation required')
        if not isinstance(manifest_entries, list) or any(not isinstance(e, dict) for e in manifest_entries):
            raise ValueError('Invalid Harbor collection metadata')
        matches = [(i, e) for i, e in enumerate(manifest_entries)
                   if e.get('source') == SOURCE or e.get('destination') == DESTINATION]
        if len(matches) != 1:
            raise ValueError('Missing/duplicate exact manifest entry')
        index, entry = matches[0]
        if (entry.get('source') != SOURCE or entry.get('destination') != DESTINATION
                or entry.get('type') != 'file' or entry.get('service') not in (None, 'main')
                or entry.get('status') not in ('ok', 'failed', 'empty', 'skipped')):
            raise ValueError('Unexpected manifest entry identity')
        files = list(self.artifacts.rglob('agent_output.py'))
        if len(files) > 1:
            raise ValueError('Duplicate submission')
        expected = self.artifacts / 'workspace/agent_output.py'
        candidate = None
        if files:
            if files != [expected] or not regular_file(expected, self.artifacts):
                raise ValueError('Wrong/unsafe candidate location')
            candidate = expected.read_bytes()
        status = 'origin_unknown'
        if entry['status'] == 'failed':
            status = 'source_absent' if candidate is None and source_observation == 'absent' else 'download_failed'
        elif entry['status'] == 'ok' and candidate is not None and source_observation == 'file':
            status = 'exported'
        body = {
            'schema_version':2, 'evidence_kind':'offline_fixture', **copy.deepcopy(self.context),
            'source':SOURCE, 'destination':DESTINATION,
            'manifest_entry_index':index, 'manifest_entry':copy.deepcopy(entry),
            'artifact_manifest_sha256':sha256(manifest), 'status':status,
            'candidate_size':len(candidate) if candidate is not None else None,
            'candidate_sha256':hashlib.sha256(candidate).hexdigest() if candidate is not None else None,
            'export_source':{'component':'ArtifactHandler.download_artifacts',
                             'observation':'synthetic_fixture', 'source_state':source_observation},
        }
        return {**body, 'receipt_id':digest(body), 'authentication':self._mac('export-fixture', body)}

    def verify(self, receipt, *, artifacts, trial_id):
        if not isinstance(receipt, dict):
            return False
        try:
            body = {k:v for k, v in receipt.items() if k not in ('receipt_id', 'authentication')}
            return (trial_id == self.trial_id and Path(artifacts).absolute() == self.artifacts
                    and all(body.get(k) == v for k, v in self.context.items())
                    and body.get('schema_version') == 2 and body.get('evidence_kind') == 'offline_fixture'
                    and sha256(self.task_config) == self.context['task_config_sha256']
                    and all(sha256(Path(p)) == expected for p, expected in self.context['code_version'].items())
                    and receipt.get('receipt_id') == digest(body)
                    and hmac.compare_digest(receipt.get('authentication', ''), self._mac('export-fixture', body)))
        except (OSError, TypeError, ValueError):
            return False

    def seal_result_fixture(self, result):
        """Authenticate synthetic result metadata; this is never a runtime/scorer attestation."""
        value = copy.deepcopy(result)
        value.update(evidence_kind='offline_fixture', producer='synthetic_fixture_backend')
        value['output_manifest'] = [
            {'name':name, 'size':len(data), 'sha256':hashlib.sha256(data).hexdigest()}
            for name, data in value.get('outputs', {}).items() if isinstance(data, bytes)]
        body = {k:v for k, v in value.items() if k not in ('outputs', 'authentication')}
        value['authentication'] = self._mac('scorer-fixture', body)
        return value

    def verify_result_fixture(self, result):
        try:
            body = {k:v for k, v in result.items() if k not in ('outputs', 'authentication')}
            return (result.get('evidence_kind') == 'offline_fixture'
                    and result.get('producer') == 'synthetic_fixture_backend'
                    and hmac.compare_digest(result.get('authentication', ''), self._mac('scorer-fixture', body)))
        except (AttributeError, TypeError, ValueError):
            return False
