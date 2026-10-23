"""Real filesystem/network probes, independent of the declarative policy gate."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys

policy = json.loads(sys.stdin.read())
allowed = {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in policy['allowed']}
forbidden = {}
for path in policy['forbidden']:
    try:
        Path(path).read_bytes()
        forbidden[path] = 'READABLE'
    except (OSError, ValueError):
        forbidden[path] = 'DENIED_OR_ABSENT'
writes = {}; submission_write = 'NOT_REQUESTED'
if policy.get('allowed_write'):
    path=Path(policy['allowed_write']);path.write_bytes(b'preflight-write-probe\n')
    assert path.read_bytes()==b'preflight-write-probe\n';path.unlink();submission_write='PASS'
    for name in policy['forbidden_write']:
        try:
            with Path(name).open('ab'):
                pass
            writes[name]='WRITABLE'
        except OSError:
            writes[name]='DENIED'
try:
    socket.create_connection(('1.1.1.1', 443), timeout=1).close()
    network = 'CONNECTED'
except OSError:
    network = 'BLOCKED'
print(json.dumps({'allowed_hashes':allowed, 'forbidden':forbidden, 'external_network':network,
                  'scrapy_installed':importlib.util.find_spec('scrapy') is not None,
                  'uid':os.getuid(),'submission_write':submission_write,'forbidden_writes':writes}))
