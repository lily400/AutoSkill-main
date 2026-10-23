"""Scrapy024 task adapter and deterministic preflight; never initializes an LLM."""
import argparse
import ast
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
from types import SimpleNamespace
import uuid
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent
WORK = AUDIT.parent
SGB = AUDIT / 'SkillGenBench'
SNAPSHOT = WORK / 'audit_gitchameleon_2026-10-22/evidence/project_snapshot'
TASK = 'skill_evaluation/code_doc/scrapy/scrapy-task-024'
SOURCE = 'data_source/code_doc/scrapy/tasks/scrapy-task-024/materials/docs/topics/feed-exports.md'
BASE_IMAGE = 'sha256:b685a4fa58bb19d1814d78a1ec0f0208f351452724f78b20212c984d6e124a34'
SGB_SHA = '5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d'
A2S_SHA = '94c47ca488d4ba4117d20272e66d49b9877e68cf'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8'))


def write(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def freeze(target, raw):
    target = ROOT / target; target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != raw:
        raise ValueError('Frozen file differs; refusing overwrite: ' + str(target))
    if not target.exists():
        target.write_bytes(raw)
    return {'frozen_path':target.relative_to(ROOT).as_posix(), 'sha256':digest(target), 'bytes':len(raw)}


def prepare():
    for repo, expected in [(SGB, SGB_SHA), (AUDIT/'AutoSkill-official-94c47ca', A2S_SHA)]:
        head = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True).strip()
        if head != expected or subprocess.check_output(['git','-C',str(repo),'status','--porcelain'], text=True).strip():
            raise ValueError('Official checkout identity/cleanliness mismatch')
    previous = read(AUDIT/'scrapy_oracle_probe_results.json')
    if digest(SGB/SOURCE) != previous['source_sha256'] or digest(SGB/TASK/'tests/eval.py') != previous['oracle_sha256_before']:
        raise ValueError('Source/Oracle differs from historical audit')
    files = []
    for source, target, role in [
        (SGB/SOURCE, 'stages/generation/sources/topics/feed-exports.md', 'generation_source'),
        (SGB/TASK/'instruction.md', 'stages/agent/instruction.md', 'agent_instruction'),
        (SGB/TASK/'task.toml', 'frozen/task.original.toml', 'task_configuration'),
        (SGB/TASK/'tests/eval.py', 'stages/scorer/oracle/eval.py', 'original_oracle'),
        (SGB/TASK/'tests/test.sh', 'stages/scorer/oracle/test.original.sh', 'original_oracle_runner'),
        (AUDIT/'scrapy_oracle_probe_results.json', 'frozen/history/results.json', 'historical_evidence'),
        (AUDIT/'scrapy_oracle_probe.py', 'frozen/history/probe.py', 'historical_code_not_executed'),
        (SNAPSHOT/'downstream_eval/configs/runner.lock.json', 'frozen/runner.lock.json', 'framework_lock'),
    ]:
        entry = freeze(target, source.read_bytes())
        entry.update(origin=str(source.relative_to(WORK)).replace('\\','/'), role=role)
        files.append(entry)
    framework = []
    snapshot_hashes = read(WORK/'audit_gitchameleon_2026-10-22/audit_manifest.json')
    for name, origin in [('io.py','src/degradation_lab/io.py'),
                         ('skill_install.py','downstream_eval/integration/skill_install.py'),
                         ('p1_observer.py','downstream_eval/integration/p1_observer.py'),
                         ('harbor_adapter.py','downstream_eval/integration/harbor_adapter.py')]:
        source = SNAPSHOT/origin
        if digest(source) != snapshot_hashes['evidence/project_snapshot/'+origin]['sha256']:
            raise ValueError('Framework snapshot drift')
        entry = freeze('frozen/reused/'+name, source.read_bytes())
        entry['origin'] = source.relative_to(WORK).as_posix(); framework.append(entry)
    lock = read(ROOT/'frozen/runner.lock.json')
    for name, relative in [('skills.py','src/harbor/skills.py'),('terminus_2.py','src/harbor/agents/terminus_2/terminus_2.py')]:
        path = ROOT/'frozen/harbor'/name
        if digest(path) != lock['source_files'][relative]['sha256']:
            raise ValueError('Pinned Harbor source mismatch')
        entry = freeze('frozen/harbor/'+name, path.read_bytes())
        entry['origin'] = 'https://raw.githubusercontent.com/harbor-framework/harbor/'+lock['harbor_commit']+'/'+relative
        framework.append(entry)
    source_bytes = (SGB/SOURCE).read_bytes()
    spans = []
    for first,last in [(136,137),(438,449)]:
        text = '\n'.join(source_bytes.decode('utf-8').splitlines()[first-1:last])
        if ('True' not in text or ('FTP' not in text and first==438)):
            raise ValueError('Target rule missing')
        spans.append({'first_line':first,'last_line':last,'text':text})
    source_descriptor = read(AUDIT/'sgb_document_tasks_only.json')
    task_row = next(t for t in source_descriptor if t['task_id']=='scrapy-task-024')
    if task_row['narrative_input_paths'] != [SOURCE]:
        raise ValueError('Ambiguous source selection')
    variants = {}
    for result in previous['results']:
        label = 'correct' if result['variant']=='source_derived_correct_submission' else 'ftp_mutant'
        entry = freeze('fixtures/submissions/'+label+'/agent_output.py', result['submission'].encode('utf-8'))
        entry.update(historical_variant=result['variant'], historical_exit_code=result['exit_code'])
        variants[label] = entry
    if (ROOT/variants['correct']['frozen_path']).read_text('utf-8').replace('"ftp": True','"ftp": False') != (ROOT/variants['ftp_mutant']['frozen_path']).read_text('utf-8'):
        raise ValueError('Historical fixtures are not the single-rule pair')
    oracle_text = (SGB/TASK/'tests/eval.py').read_text('utf-8')
    oracle_tree = ast.parse(oracle_text)
    finder = next(n for n in oracle_tree.body if isinstance(n,ast.FunctionDef) and n.name=='get_target_function')
    freeze('runtime/interface.py', ('import inspect\n\n'+ast.get_source_segment(oracle_text,finder)+'\n').encode())
    # Only pure-Python installed dependencies are copied for offline Linux pytest.
    deps = {}
    for module, dist in [('pytest','pytest'),('_pytest','pytest'),('pluggy','pluggy'),('iniconfig','iniconfig'),('packaging','packaging'),('pygments','Pygments')]:
        source = Path(importlib.util.find_spec(module).origin).parent
        deps[module] = {'distribution':dist, 'version':importlib.metadata.version(dist), 'origin':str(source)}
        for path in source.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc','.pyo'):
                freeze('stages/scorer/deps/'+module+'/'+path.relative_to(source).as_posix(),path.read_bytes())
    py_shim = Path(importlib.util.find_spec('py').origin)
    freeze('stages/scorer/deps/py.py', py_shim.read_bytes())
    deps['py'] = {'distribution':'pytest compatibility shim', 'version':importlib.metadata.version('pytest'), 'origin':str(py_shim)}
    for index in (1,2):
        sid = f'00000000-0000-4000-8000-{index:012d}'
        text = f'---\nid: "{sid}"\nname: "preflight-fixture-{index}"\ndescription: "Deterministic installer and observer fixture only"\n---\n\n# Fixture body\n\nSynthetic read-contract marker {index}. This is not a generated research Skill.\n'
        freeze('fixtures/skills/'+sid+'/SKILL.md', text.encode('utf-8'))
        freeze('fixtures/skills/'+sid+'/references/fixture.txt', f'asset-{index}\n'.encode())
    inventory = {p.relative_to(ROOT).as_posix():digest(p) for directory in ['frozen','stages','fixtures','runtime'] for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'manifest_revisions' not in p.parts}
    before = {str(p.relative_to(WORK)):digest(p) for p in [AUDIT/n for n in ['decision_report.md','candidate_shortlist.md','repair_plan.md','next_step_plan.md','scrapy_oracle_probe.py','scrapy_oracle_probe_results.json']]}
    manifest = {'schema_version':1,'task_id':'scrapy-task-024','source_kind':'SkillGenBench task-curated release material; not a verified complete/latest upstream manual',
                'skillgenbench_commit':SGB_SHA,'anything2skill_commit':A2S_SHA,'harbor_commit':lock['harbor_commit'],
                'base_image':BASE_IMAGE,'source_relative_path':SOURCE,'source_raw_sha256':digest(SGB/SOURCE),
                'source_normalized_lf_sha256':hashlib.sha256(source_bytes.replace(b'\r\n',b'\n').replace(b'\r',b'\n')).hexdigest(),
                'target_rule_id':'scrapy024.ftp-default-overwrite','rule_supports':spans,'input_fixture_files':[],
                'files':files,'reused_framework_files':framework,'historical_variants':variants,'pytest_dependencies':deps,
                'frozen_inventory':inventory,'protected_audit_hashes':before,'model_calls':0,
                'generation_stage_files':['sources/topics/feed-exports.md'], 'agent_stage_files':['instruction.md'],
                'formal_skill_generation':'NOT_RUN','historical_main_repository':'not read; accessible frozen snapshots used'}
    manifest['adapter_files'] = {name:digest(ROOT/name) for name in [
        'preflight.py','reuse.py','loading_contract.py','harbor_entry.py','test_preflight.py',
        'config/runtime.json','task/task.toml','access_policy.json']}
    if (ROOT/'source_manifest.json').exists() and read(ROOT/'source_manifest.json') != manifest:
        old = read(ROOT/'source_manifest.json')
        stable = set(old)-{'pytest_dependencies','frozen_inventory'}
        if (any(old[k]!=manifest[k] for k in stable) or
                any(manifest['frozen_inventory'].get(k)!=v for k,v in old['frozen_inventory'].items())):
            raise ValueError('Manifest drift; refusing to change frozen source/code/fixtures')
        freeze('frozen/manifest_revisions/'+digest(ROOT/'source_manifest.json')+'.json', (ROOT/'source_manifest.json').read_bytes())
    write(ROOT/'source_manifest.json',manifest)
    policy = {'schema_version':1,'default':'deny','network':'none','docker_socket_in_task_containers':False,
              'runtime_user':'65532:65532','rootfs_read_only':True,'scrapy_required':False,
              'generation':{'read_only_mounts':{'stages/generation':'/sources-root'},'allow_files':['sources/topics/feed-exports.md'],'write_files':[]},
              'agent':{'read_only_mounts':{'stages/agent/instruction.md':'/workspace/instruction.md','approved fixture package set':'/harbor/skills'},'allow_files':['instruction.md'],'write_files':['/workspace/** (private tmpfs)','/tmp/** (private tmpfs)'],'final_submission':'/workspace/agent_output.py'},
              'candidate':{'read_only_mounts':{'selected submission only':'/submission','runtime/worker.py + extracted interface.py only':'/runtime'},'receives':'one function input, no expected/test/source bytes'},
              'scorer':{'read_only_mounts':{'stages/scorer/oracle':'/oracle','stages/scorer/deps':'/deps','candidate bytes for source assertions only':'/submission','hash-bound responses only':'/responses','oracle_bridge.py only':'/bridge'},'write_files':['/results/junit.xml']},
              'forbidden_in_generation_or_agent':['oracle','tests','expected','reference','history','host audit directory','other source files'],
              'enforcement':'minimal bind mounts + nonroot/read-only/no-network Docker profiles; generator manifest API also denies path escape',
              'scoring_protocol':'unchanged original assertions; module loader supplied by response bridge; candidate executes in a separate container',
              'real_agent_body_read_verified':False}
    write(ROOT/'access_policy.json',policy)
    return manifest


def verify():
    manifest = read(ROOT/'source_manifest.json')
    for name,h in {**manifest['frozen_inventory'],**manifest.get('adapter_files',{})}.items():
        if digest(ROOT/name) != h:
            raise ValueError('Frozen artifact drift: '+name)
    for name,h in manifest['protected_audit_hashes'].items():
        if digest(WORK/name) != h:
            raise ValueError('Protected historical audit changed: '+name)
    return manifest


def read_stage(stage, relative):
    policy = read(ROOT/'access_policy.json')[stage]
    if relative not in policy['allow_files']:
        raise PermissionError('File is not whitelisted')
    original = ROOT/'stages'/stage/relative
    path = original.resolve()
    if not path.is_relative_to((ROOT/'stages'/stage).resolve()) or original.is_symlink():
        raise PermissionError('Path escape')
    return path.read_bytes()


class Docker:
    def __init__(self, output):
        self.output = output; self.records=[]

    def call(self, args, data=None, timeout=45, check=True):
        proc = subprocess.run(['docker',*args], input=data, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
        record={'command':['docker',*args], 'return_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
        self.records.append(record); write(self.output/'commands.json',self.records)
        if check and proc.returncode:
            raise RuntimeError('Docker operation failed: '+proc.stderr[:1200])
        return proc

    def start(self, mounts, writable_workspace=False):
        args=['create','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
              '--user','65532:65532','--pids-limit','64','--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
              '--env','PYTHONDONTWRITEBYTECODE=1','--env','PYTEST_DISABLE_PLUGIN_AUTOLOAD=1']
        if writable_workspace:
            args += ['--tmpfs','/workspace:rw,noexec,nosuid,size=16m,uid=65532,gid=65532']
        for source,target,writable in mounts:
            args += ['--mount',f'type=bind,source={source.resolve()},target={target}'+('' if writable else ',readonly')]
        cid = self.call([*args,BASE_IMAGE,'sleep','600']).stdout.strip()
        inspected = json.loads(self.call(['inspect',cid]).stdout)[0]
        observed = {m['Destination']:m['RW'] for m in inspected['Mounts'] if m['Type']=='bind'}
        expected = {target:rw for _,target,rw in mounts}
        if observed != expected or inspected['HostConfig']['NetworkMode']!='none' or not inspected['HostConfig']['ReadonlyRootfs']:
            raise ValueError('Container policy differs from declared mounts')
        self.call(['start',cid]); return cid

    def execute(self,cid,command,data=None,check=True):
        return self.call(['exec',*(['-i'] if data is not None else []),cid,*command],data=data,check=check)

    def stop(self,cid):
        self.call(['rm','-f',cid],check=False)


def policy_check(docker, stage, output, skills=None):
    roots={'generation':(ROOT/'stages/generation','/sources-root'),'agent':(ROOT/'stages/agent','/workspace'),
           'scorer':(ROOT/'stages/scorer/oracle','/oracle')}
    source,target=roots[stage]
    mounts=[((source/'instruction.md') if stage=='agent' else source,
             '/workspace/instruction.md' if stage=='agent' else target,False),
            (ROOT/'runtime/policy_probe.py','/runtime/policy_probe.py',False)]
    if skills: mounts.append((skills,'/harbor/skills',False))
    allowed={'generation':['/sources-root/sources/topics/feed-exports.md'],'agent':['/workspace/instruction.md'], 'scorer':['/oracle/eval.py']}[stage]
    forbidden=['/var/run/docker.sock','/workspace/tests/eval.py','/audit/decision_report.md','/expected.json','/history/results.json']
    if stage!='generation':forbidden += ['/sources-root/sources/topics/feed-exports.md']
    if stage!='scorer':forbidden += ['/oracle/eval.py','/responses/responses.json']
    cid=docker.start(mounts,writable_workspace=stage=='agent')
    try:
        request={'allowed':allowed,'forbidden':forbidden}
        if stage=='agent':
            request.update(allowed_write='/workspace/agent_output.py',forbidden_write=['/workspace/instruction.md','/outside-workspace.py'])
        result=json.loads(docker.execute(cid,['python','-B','/runtime/policy_probe.py'],json.dumps(request)).stdout)
        assert result['uid']==65532 and not result['scrapy_installed'] and result['external_network']=='BLOCKED'
        assert all(v=='DENIED_OR_ABSENT' for v in result['forbidden'].values())
        if stage=='agent':
            assert result['submission_write']=='PASS' and all(v=='DENIED' for v in result['forbidden_writes'].values())
        expected={target+'/'+p.relative_to(source).as_posix():digest(p) for p in source.rglob('*') if p.is_file()}
        assert all(expected[k]==v for k,v in result['allowed_hashes'].items())
        write(output/(stage+'_policy.json'),{'status':'PASS',**result})
    finally:docker.stop(cid)


def oracle_inputs():
    tree=ast.parse((ROOT/'stages/scorer/oracle/eval.py').read_text('utf-8'));inputs=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef):
            for deco in node.decorator_list:
                if isinstance(deco,ast.Call) and isinstance(deco.func,ast.Attribute) and deco.func.attr=='parametrize':
                    values=ast.literal_eval(deco.args[1]); inputs.extend(v[0] if isinstance(v,tuple) else v for v in values)
            for call in ast.walk(node):
                if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='func' and len(call.args)==1:
                    if isinstance(call.args[0],ast.Constant):inputs.append(call.args[0].value)
    if len(inputs)!=15:raise ValueError('Original Oracle input inventory drift')
    return inputs


def score_submission(submission, output, docker):
    """Controller endpoint for a Harbor-exported submission; no Agent/model loop."""
    output.mkdir(parents=True,exist_ok=False)
    submission=Path(submission).resolve(); manifest=verify()
    worker_dir=output/'worker';worker_dir.mkdir()
    for name in ['worker.py','interface.py']:shutil.copyfile(ROOT/'runtime'/name,worker_dir/name)
    response={'candidate_sha256':digest(submission),'oracle_sha256':digest(ROOT/'stages/scorer/oracle/eval.py'),
              'run_id':output.name,'task_id':'scrapy-task-024','calls':{}}
    cid=docker.start([(submission,'/submission/agent_output.py',False),(worker_dir,'/runtime',False)])
    try:
        probe=json.loads(docker.execute(cid,['python','-B','-c',(ROOT/'runtime/policy_probe.py').read_text('utf-8')],
            json.dumps({'allowed':['/submission/agent_output.py'],
                        'forbidden':['/oracle/eval.py','/responses/responses.json','/workspace/tests/eval.py',
                                     '/sources-root/sources/topics/feed-exports.md','/audit/decision_report.md','/var/run/docker.sock']})).stdout)
        assert probe['allowed_hashes']['/submission/agent_output.py']==response['candidate_sha256']
        assert probe['uid']==65532 and not probe['scrapy_installed'] and probe['external_network']=='BLOCKED'
        assert all(v=='DENIED_OR_ABSENT' for v in probe['forbidden'].values())
        write(output/'candidate_policy.json',{'status':'PASS',**probe})
        for operation,value in [('metadata',None),*[('call',x) for x in oracle_inputs()]]:
            raw=docker.execute(cid,['python','-B','/runtime/worker.py'],json.dumps({'operation':operation,'input':value})).stdout
            result=json.loads(raw)
            if operation=='metadata':response['metadata']=result
            else:response['calls'][json.dumps([type(value).__name__,value],sort_keys=True)]=result
    finally:docker.stop(cid)
    write(output/'responses/responses.json',response)
    verdict_dir=output/'verdict';verdict_dir.mkdir()
    mounts=[(ROOT/'stages/scorer/oracle','/oracle',False),(ROOT/'stages/scorer/deps','/deps',False),
            (submission,'/submission/agent_output.py',False),(output/'responses','/responses',False),
            (ROOT/'runtime/oracle_bridge.py','/bridge/oracle_bridge.py',False),(verdict_dir,'/results',True)]
    cid=docker.start(mounts)
    try:
        proc=docker.execute(cid,['env','PYTHONPATH=/deps:/bridge','TEST_ROOT_DIR=/submission','python','-B','-m','pytest',
                                 '-p','no:cacheprovider','-p','oracle_bridge','/oracle/eval.py','--junitxml=/results/junit.xml','-q'],check=False)
    finally:docker.stop(cid)
    (output/'pytest.stdout.txt').write_text(proc.stdout,'utf-8');(output/'pytest.stderr.txt').write_text(proc.stderr,'utf-8')
    junit=verdict_dir/'junit.xml'
    if not junit.exists():raise RuntimeError('Oracle environment did not produce JUnit results: '+proc.stderr)
    tree=ElementTree.parse(junit);cases=list(tree.iter('testcase'))
    failures=[{'name':c.attrib['name'],'detail':c.find('failure').attrib.get('message','')} for c in cases if c.find('failure') is not None]
    errors=[c.attrib['name'] for c in cases if c.find('error') is not None]
    ftp=[c for c in cases if 'test_supported_backends[ftp://' in c.attrib['name']]
    result={'protocol':'unchanged original 19 assertions + candidate response bridge; original source assertions read exact submitted bytes',
            'oracle_original_sha256':response['oracle_sha256'],'candidate_sha256':response['candidate_sha256'],
            'environment':'Linux Python3.13.9, no-network, nonroot, isolated candidate and trusted scorer containers',
            'task_result':{'tests':len(cases),'passed':len(cases)-len(failures)-len(errors),'failed':len(failures),'errors':len(errors),'exit_code':proc.returncode},
            'rule_result':{'rule_id':manifest['target_rule_id'],'assertion':ftp[0].attrib['name'] if len(ftp)==1 else None,
                           'passed':len(ftp)==1 and ftp[0].find('failure') is None and ftp[0].find('error') is None},
            'failures':failures,'loading_errors':[response['metadata']] if not response['metadata'].get('ok') else [],
            'environment_errors':errors,'revised_oracle':'NOT_CREATED','model_calls':0}
    result['failure_category'] = ('loading_error' if result['loading_errors'] else 'environment_error' if errors or len(cases)!=19 else
                                  'target_rule_error' if len(failures)==1 and not result['rule_result']['passed'] else
                                  'task_assertion_error' if failures else 'none')
    write(output/'task_result.original.json',result['task_result'])
    write(output/'rule_result.original_assertion.json',result['rule_result'])
    write(output/'result.json',result);return result


def loading_check(docker,output):
    from reuse import methods
    from loading_contract import installed_packages,summarize
    methods=methods(); expected={p.parent.name:methods['inventory'](p.parent) for p in (ROOT/'fixtures/skills').glob('*/SKILL.md')}
    paths={p.parent.name:p for p in (ROOT/'fixtures/skills').glob('*/SKILL.md')}
    packages=installed_packages(paths,expected,methods['inventory'],methods['Terminus2']._parse_skill_frontmatter)
    installed=output/'installed_skills';methods['copy_packages'](packages,installed)
    if {s.name for s in methods['resolve_skills']([installed])}!=set(packages):raise ValueError('Official resolver dropped a package')
    policy_check(docker,'agent',output,installed)
    cid=docker.start([(ROOT/'stages/agent/instruction.md','/workspace/instruction.md',False),(installed,'/harbor/skills',False)],writable_workspace=True)
    events=[]
    try:
        class Environment:
            async def is_dir(self,path):
                return docker.execute(cid,['test','-d',path],check=False).returncode==0
            async def exec(self,command,timeout_sec=10):
                proc=docker.execute(cid,['sh','-c',command],check=False)
                return SimpleNamespace(return_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
        agent=methods['Terminus2']();agent.skills_dir='/harbor/skills'
        xml=asyncio.run(agent._build_skills_section(Environment()));(output/'available_skills.xml').write_text(xml,'utf-8')
        entries=list(ElementTree.fromstring(xml));discovered={Path(e.findtext('location')).parent.name:e for e in entries}
        if set(discovered)!=set(packages):raise ValueError('Native discovery differs from installed IDs')
        for index,(sid,package) in enumerate(packages.items()):
            if methods['inventory'](installed/sid)!=expected[sid]:raise ValueError('Installed hashes differ')
            common={'run_id':output.name,'skill_id':sid,'skill_sha256':package['sha256']}
            events += [{**common,'event':'discovered','skill_name':discovered[sid].findtext('name')},
                       {**common,'event':'invoked','call_id':str(index),'read_path':'/harbor/skills/'+sid+'/SKILL.md'}]
            proc=docker.execute(cid,['cat','/harbor/skills/'+sid+'/SKILL.md'])
            assert hashlib.sha256(proc.stdout.encode()).hexdigest()==package['sha256']
            events.append({**common,'event':'returned','call_id':str(index),'is_error':False,'return_code':proc.returncode,'visible_output':proc.stdout})
        summary=summarize(events,packages,output.name,methods['body_visible'])
        assert set(summary['body_exposed_ids'])==set(packages)
        summary.update(status='PASS',installed_hashes=methods['inventory'](installed),fixture_packages_only=True)
        write(output/'loading_events.json',events);write(output/'loading_result.json',summary)
    finally:docker.stop(cid)


def run_linux(run_id, oracle_only=False, access_only=False):
    manifest=verify();output=ROOT/'runs'/run_id
    if not re.fullmatch(r'[a-z0-9-]{1,64}',run_id):raise ValueError('Unsafe run ID')
    output.mkdir(parents=True,exist_ok=False)
    write(output/'source_manifest.snapshot.json',manifest)
    docker=Docker(output)
    try:
        engine=docker.call(['info','--format','{{json .ServerVersion}}'])
        image=docker.call(['image','inspect',BASE_IMAGE,'--format','{{.Id}}']).stdout.strip()
        assert image==BASE_IMAGE
        write(output/'environment.json',{'docker_server':json.loads(engine.stdout),'image_id':image,'platform':'linux','model_calls':0})
        if not oracle_only:
            for stage in ['generation','scorer']:policy_check(docker,stage,output)
            loading_check(docker,output)
        results={}
        if not access_only:
            results={name:score_submission(ROOT/entry['frozen_path'],output/name,docker) for name,entry in manifest['historical_variants'].items()}
            assert results['correct']['task_result']=={'tests':19,'passed':19,'failed':0,'errors':0,'exit_code':0}
            assert results['ftp_mutant']['task_result']=={'tests':19,'passed':18,'failed':1,'errors':0,'exit_code':1}
            assert results['correct']['rule_result']['passed'] and not results['ftp_mutant']['rule_result']['passed']
        verify()
        summary={'status':'PASS','scope':'oracle_only' if oracle_only else 'access_and_loading_only' if access_only else 'full_preflight', 'run_id':run_id,'oracle_results':results,'model_calls':0,'real_agent_runs':0,
                 'anything2skill_runs':0,'formal_skills_generated':0,'real_agent_body_read_verified':False}
        write(output/'result.json',summary);print(json.dumps({'status':'PASS','run_id':run_id}))
    except Exception as error:
        write(output/'result.json',{'status':'FAIL_OR_BLOCKED','error_type':type(error).__name__,'error':str(error),'model_calls':0})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','verify','run-linux','score-linux','access-linux']);parser.add_argument('--run-id')
    args=parser.parse_args()
    if args.action=='prepare':prepare();print('FROZEN')
    elif args.action=='verify':verify();print('HASHES_VERIFIED')
    else:run_linux(args.run_id or 'linux-'+uuid.uuid4().hex[:12],oracle_only=args.action=='score-linux',access_only=args.action=='access-linux')
