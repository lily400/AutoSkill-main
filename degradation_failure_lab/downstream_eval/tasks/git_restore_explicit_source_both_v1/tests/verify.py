"""Executed only inside Harbor's separate verifier, from trusted /tests files."""
import json
import tempfile
from pathlib import Path

from fixture import build
from oracle import evaluate, trusted_state

output = Path('/logs/verifier')
output.mkdir(parents=True, exist_ok=True)
# A stale reward can never survive a parser or infrastructure failure.
(output / 'reward.txt').write_text('0\n')
with tempfile.TemporaryDirectory(prefix='trusted-git-') as directory:
    reference = Path(directory) / 'repo'
    fixture = build(reference)
    expected = trusted_state(reference, fixture)
    result = evaluate(Path('/work/repo'), expected)
(output / 'assertions.json').write_text(json.dumps(result, indent=2) + '\n')
(output / 'reward.txt').write_text('1\n' if result['success'] else '0\n')
