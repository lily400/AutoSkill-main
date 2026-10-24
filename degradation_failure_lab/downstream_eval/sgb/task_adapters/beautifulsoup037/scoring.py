"""Task-037 export evidence and scorer receipts. No process/container backend is enabled."""
import base64
import hashlib
from pathlib import Path

from degradation_lab.io import read, sha256

SOURCE = '/workspace/agent_output.py'
DESTINATION = 'artifacts/workspace/agent_output.py'
UNSCORABLE = ('environment_error', 'submission_ambiguous', 'submission_download_failed',
              'submission_origin_unknown', 'submission_hash_mismatch')


def failure(category, reason):
    return {'failure_category':category, 'error_category':reason,
            'task_result':{'tests':0, 'passed':0}, 'rule_result':{'passed':None}}


def regular_file(path, boundary):
    """Reject links/reparse points and paths escaping the controller's input directory."""
    path, boundary = Path(path), Path(boundary).resolve()
    if not path.resolve().is_relative_to(boundary):
        return False
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part.lstat(), 'st_file_attributes', 0) & 0x400:
            return False
        if part.resolve() == boundary:
            break
    return path.is_file()


def collect_export(artifacts, *, receipt=None, controller=None, trial_id=None):
    """Validate controller-issued evidence. Unsigned dictionaries are never source proof."""
    from .exports import ExportController
    artifacts = Path(artifacts)
    manifest = artifacts / 'manifest.json'
    try:
        files = list(artifacts.rglob('agent_output.py'))
        if len(files) > 1:
            return None, failure('submission_ambiguous', 'duplicate_submission')
        if not regular_file(manifest, artifacts):
            raise ValueError('Missing regular artifact manifest')
        entries = read(manifest)
        if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
            raise ValueError('Invalid Harbor artifact manifest')
        matches = [(i, e) for i, e in enumerate(entries) if e.get('source') == SOURCE
                   or e.get('destination') == DESTINATION]
        if len(matches) != 1:
            raise ValueError('Ambiguous/missing collection entry')
        index, entry = matches[0]
        if (entry.get('source') != SOURCE or entry.get('destination') != DESTINATION
                or entry.get('service') not in (None, 'main') or entry.get('type') != 'file'):
            raise ValueError('Wrong artifact source, destination, service or type')
        bound = (isinstance(controller, ExportController)
                 and controller.verify(receipt, artifacts=artifacts, trial_id=trial_id)
                 and receipt.get('artifact_manifest_sha256') == sha256(manifest)
                 and receipt.get('manifest_entry_index') == index and receipt.get('manifest_entry') == entry)
        if not files and bound and receipt.get('status') == 'source_absent' and entry.get('status') == 'failed':
            return None, failure('submission_missing', 'controller_observed_source_absent')
        if entry.get('status') == 'failed':
            return None, failure('submission_download_failed', 'harbor_collection_failed')
        if entry.get('status') != 'ok' or not bound or receipt.get('status') != 'exported':
            raise ValueError('Export has no authenticated successful controller receipt')
        expected = artifacts / 'workspace/agent_output.py'
        if len(files) != 1 or files[0] != expected or not regular_file(expected, artifacts):
            raise ValueError('Exact regular submission missing or wrong path')
        data = expected.read_bytes()
        if hashlib.sha256(data).hexdigest() != receipt.get('candidate_sha256') or len(data) != receipt.get('candidate_size'):
            return None, failure('submission_hash_mismatch', 'export_size_or_sha256_mismatch')
        return expected, None
    except (OSError, ValueError, TypeError):
        return None, failure('submission_origin_unknown', 'artifact_evidence_invalid')


def execute_scoring(plan):
    """Reserved runtime interface. Independent authorization AND a reviewed backend are missing."""
    raise RuntimeError('Scorer backend NOT_IMPLEMENTED: original Oracle import isolation requires review; no process started')


def inspect_result(plan, result, *, controller=None):
    """Review authenticated fixture receipts only. Never asserts isolation or a real task outcome."""
    from .exports import ExportController, digest
    score = failure('environment_error', 'scorer_receipt_invalid')
    score.update(candidate_sha256=plan['candidate_sha256'],
                 oracle_original_sha256=plan['oracle_sha256'],
                 export_receipt_id=plan.get('export_receipt_id'),
                 request_sha256=plan.get('request_sha256'), trial_id=plan.get('trial_id'),
                 runtime_isolation_verified=False, trusted_score=False, real_agent_outcome=False,
                 task_success=None, evidence_kind='scorer_receipt_review',
                 score_channels={
                     'original_benchmark':{'scorer_id':'sgb-original:' + plan['oracle_sha256'],
                                           'status':'NOT_RUN', 'trusted_score':None},
                     'behavior':{'scorer_id':'bs37-behavior-v1-draft',
                                 'status':'NOT_IMPLEMENTED', 'trusted_score':None}})
    try:
        outputs = result.get('outputs', {})
        score['outputs'] = {
            name:{'sha256':hashlib.sha256(data).hexdigest(),
                  'base64':base64.b64encode(data).decode('ascii')}
            for name, data in outputs.items()
            if name in ('junit_xml', 'reward', 'stdout', 'stderr') and isinstance(data, bytes)}
        score['execution_status'] = result.get('execution_status')
        score['returncode'] = result.get('returncode')
        score['error_type'] = result.get('error_type')
        receipt = plan.get('export_receipt') or {}
        if (not isinstance(controller, ExportController)
                or not controller.verify(plan.get('export_receipt'), artifacts=controller.artifacts,
                                         trial_id=plan.get('trial_id'))
                or plan.get('request_sha256') != digest({k:v for k, v in plan.items() if k != 'request_sha256'})
                or not controller.verify_result_fixture(result)
                or plan.get('task_id') != receipt.get('task_id')
                or plan.get('candidate_sha256') != receipt.get('candidate_sha256')
                or plan.get('task_config_sha256') != receipt.get('task_config_sha256')
                or plan.get('export_receipt_id') != receipt.get('receipt_id')
                or plan['input_sha256'].get(plan['candidate_source']) != plan['candidate_sha256']):
            score['error_category'] = 'scorer_origin_unknown'
            return score
        if (result.get('task_id') != plan['task_id'] or result.get('trial_id') != plan.get('trial_id')
                or result.get('export_receipt_id') != plan.get('export_receipt_id')
                or result.get('request_sha256') != plan.get('request_sha256')
                or result.get('candidate_sha256') != plan['candidate_sha256']
                or result.get('input_sha256') != plan['input_sha256']):
            return score
        if any(sha256(Path(name)) != digest_value for name, digest_value in plan['input_sha256'].items()):
            score['error_category'] = 'scorer_input_changed'
            return score
        candidate, export_error = collect_export(controller.artifacts, receipt=plan['export_receipt'],
                                                  controller=controller, trial_id=plan['trial_id'])
        if export_error or candidate.resolve() != Path(plan['candidate_source']).resolve():
            score['error_category'] = 'scorer_origin_unknown'
            return score
        if result.get('execution_status') in ('timeout', 'error', 'not_run'):
            score['error_category'] = 'scorer_' + result['execution_status']
            return score
        expected = {'junit_xml', 'reward', 'stdout', 'stderr'}
        manifest = result.get('output_manifest', [])
        if (result.get('execution_status') != 'completed' or type(result.get('returncode')) is not int
                or set(outputs) != expected or set(score['outputs']) != expected
                or not isinstance(manifest, list) or len(manifest) != 4
                or any(not isinstance(e, dict) for e in manifest)
                or {e.get('name') for e in manifest} != expected):
            return score
        for entry in manifest:
            data = outputs[entry['name']]
            if (type(entry.get('size')) is not int or entry['size'] != len(data)
                    or entry.get('sha256') != hashlib.sha256(data).hexdigest()):
                score['error_category'] = 'scorer_output_hash_mismatch'
                return score
        from .adapter import normalize_score
        parsed = normalize_score({'returncode':result['returncode'],
                                  'junit_xml':outputs['junit_xml'].decode('utf-8'),
                                  'reward':outputs['reward'].decode('utf-8')}, plan['oracle_tests'])
        score.update(parsed)
        score['score_channels']['original_benchmark'].update(status='OFFLINE_FIXTURE_REVIEW', observed=parsed)
        score['error_category'] = 'none' if parsed['failure_category'] == 'none' else parsed['failure_category']
        return score
    except (AttributeError, KeyError, OSError, TypeError, ValueError):
        return score


def behavior_plan(root):
    """Versioned design only: retain real Tag/identity semantics; execute no Oracle or candidate."""
    from .adapter import verify_assets
    official, mapping = verify_assets(root)
    return {'scorer_id':'bs37-behavior-v1-draft', 'status':'DESIGN_ONLY',
            'execution_status':'NOT_RUN', 'trusted_score':None,
            'original_oracle_sha256':sha256(official / 'tests/eval.py'),
            'retained_behavior_checks':[name for name in mapping['oracle_tests']
                                        if name != 'test_uses_tag_name_assignment'],
            'excluded_source_text_check':'test_uses_tag_name_assignment',
            'semantic_requirements':['same live bs4.Tag object returned', 'only requested tag name changes',
                                     'contents and attributes preserved', 'document tree position preserved'],
            'isolation_status':'BLOCKED: real Tag identity cannot cross a serialization boundary unchanged',
            'score_policy':'Separate metric; never infer behavior success by dropping a failed original test'}
