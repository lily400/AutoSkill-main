"""Post-Agent controller hook; reuses Harbor's Environment download interface."""
import asyncio
from pathlib import Path

from preflight import ROOT, Docker, score_submission, verify


async def export_submission(environment, destination):
    destination = Path(destination).resolve()
    if not destination.is_relative_to(ROOT) or destination.exists():
        raise ValueError('Submission export must be a new path inside this task bundle')
    destination.parent.mkdir(parents=True, exist_ok=True)
    await environment.download_file(source_path='/workspace/agent_output.py', target_path=destination)
    if not destination.is_file() or destination.is_symlink():
        raise ValueError('No regular exported submission')
    return destination


async def score_harbor_submission(environment, output):
    """Call after the existing Agent finishes; the Agent never receives scorer mounts."""
    verify()
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError('Output outside task bundle')
    output.mkdir(parents=True, exist_ok=False)
    submission = await export_submission(environment, output/'export/agent_output.py')
    docker = Docker(output)
    return await asyncio.to_thread(score_submission, submission, output/'score', docker)
