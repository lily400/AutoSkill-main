from pathlib import Path
import sys
lab = Path(sys.argv[1])
stage = Path(__file__).parent
old = (lab/'scripts/run_clean.py').read_text(encoding='utf-8')
body = old[old.index('    from autoskill import AutoSkill, AutoSkillConfig'):old.index("\n\nif __name__=='__main__':")]
body = body.replace('max_files=1', "max_files=len(input_manifest['inputs'])")
body = body.replace("if len(units)!=1", "if len(units)!=len(input_manifest['inputs'])")
body = body.replace("not units[0].get('text','').strip()", "not all(u.get('text','').strip() for u in units)")
body = body.replace("'Official file loader did not return one nonempty document'", "'Official file loader did not parse every nonempty input'")
body = body.replace("Path(cfg['upstream_path'])", 'upstream')
body = body.replace("utc() + ' ' + redact(str(message))", "utc() + ' ' + redact(str(message))")
body = body.replace("'Official public API starting: one document, empty independent SkillBank'", "'Official public API starting: snapshotted inputs, empty independent SkillBank'")
body = body.replace("metadata={k:manifest[k] for k in ('source_id','source_url','source_commit','sha256','classification','variant')}",
                    "metadata={'case_id': invocation['case_id'], 'condition_id':invocation['condition_id'], 'lab_run_id':run.name, 'input_manifest':input_manifest}")
body = body.replace("raise SystemExit(exit_code)", "return exit_code")
header = '''"""Reuse P0's unchanged official API invocation and transparent HTTP observer."""
from collections import Counter
import hashlib, inspect, json, os, sys, threading, time, traceback
from pathlib import Path
from .io import read, sha256, utc, write as write_json, upstream_inventory as code_inventory


def execute(run):
    cfg = read(run/'config.json')
    key = os.environ[cfg['credential_env']]
    upstream = Path(read(run/'environment.json')['upstream_path'])
    before = read(run/'upstream_before.json')
    store = run/'SkillBank'
    if list(store.iterdir()): raise RuntimeError('SkillBank must be empty before execution')
    input_manifest = read(run/'input_manifest.json')
    source = run/'inputs'
    invocation = read(run/'invocation.json')
    invocation.update(real_generation=True, argv=[sys.executable, '-B', *sys.argv], python=sys.version)
    write_json(run/'invocation.json', invocation)
    write_json(run/'status.json', {'state':'RUNNING', 'real_generation':True, 'updated_at':utc()})
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(upstream))
'''
# Restore observers even if setup fails; preflight is covered by outer execute guard.
body = body.replace("        print('RUN_DIRECTORY='+str(run),flush=True)", "        write_json(run/'status.json', {'state':'COMPLETED' if exit_code==0 else 'FAILED', 'real_generation':True, 'updated_at':utc()})\n        print('RUN_DIRECTORY='+str(run),flush=True)")
(stage/'src/degradation_lab/adapter.py').write_text(header+body+'\n',encoding='utf-8')
shutil_import = __import__('shutil')
shutil_import.copyfile(lab/'scripts/provider_adapter.py', stage/'src/degradation_lab/provider_adapter.py')
print('Built adapter from observed P0 path; original untouched')
