"""Namespaced pilot over the existing original-assertion Scrapy024 scorer."""
from pathlib import Path

from degradation_lab.io import read, sha256, write
from downstream_eval.sgb.scrapy024 import scorer_module
from downstream_eval.sgb.task_adapters.scrapy041.scoring import docker_executor
from .common import bind, native_trial


def verify_assets():
    return scorer_module().verify()


def score(submission, output, *, expected_sha256=None):
    source, output = Path(submission), Path(output)
    if not source.is_file() or source.is_symlink() or source.stat().st_size > 131072:
        raise ValueError('Invalid submission')
    digest = sha256(source)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError('Export hash mismatch')
    module = scorer_module()
    docker = docker_executor(output, module.BASE_IMAGE)
    base_start = docker.start

    def start(mounts, writable_workspace=False):
        for path, target, writable in mounts:
            if target == '/results' and writable:
                path.chmod(0o777)
        cid = base_start(mounts, writable_workspace)
        try:
            docker.network(cid, 'scorer' if any(m[1] == '/oracle' for m in mounts) else 'candidate')
        except BaseException:
            docker.stop(cid)
            raise
        return cid

    # The legacy executor already bounds each Docker command with a timeout.
    docker.start = start
    result = module.score_submission(source, output, docker)
    responses = read(output / 'responses/responses.json')
    bound = (sha256(source) == digest == result['candidate_sha256'] == responses['candidate_sha256']
             and responses['oracle_sha256'] == result['oracle_original_sha256'])
    counts = result['task_result']
    infra = bound and counts['tests'] == 19 and counts['errors'] == 0
    result.update(candidate_binding_verified=bound, infra_ok=infra,
                  task_success=infra and counts['passed'] == 19,
                  failed_tests=[f['name'] for f in result['failures']])
    write(output / 'result.json', result)
    return result


execution_config, configure, grade_export, paid_batch = bind('scrapy-task-024', score, verify_assets)
