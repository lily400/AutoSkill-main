"""One input per process. No source document, expected output or test bundle mounted."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys

candidate = Path('/submission/agent_output.py').read_bytes()
request = json.load(sys.stdin)
result = {'candidate_sha256': hashlib.sha256(candidate).hexdigest(), 'ok': False}
try:
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        exec('import math\nimport numpy as np', namespace)
        exec(compile(candidate, '/submission/agent_output.py', 'exec'), namespace)
        result['value'] = namespace['solve'](request['input'])
    result['ok'] = True
    encoded = json.dumps(result, allow_nan=False)
except BaseException as error:
    result = {'candidate_sha256': result['candidate_sha256'], 'ok': False,
              'error': type(error).__name__ + ': ' + str(error)[:2000]}
    encoded = json.dumps(result)
print(encoded)
