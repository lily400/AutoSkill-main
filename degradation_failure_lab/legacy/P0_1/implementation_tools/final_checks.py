import json, pathlib, shutil, subprocess, sys, time
lab=pathlib.Path(sys.argv[1]).resolve(); stage=pathlib.Path(__file__).parent
sys.path.insert(0,str(stage/'src'))
from degradation_lab.io import read, write, utc, inventory, upstream_inventory
for folder in ('src','tests'):
    for src in (stage/folder).rglob('*'):
        if src.is_file():
            dest=lab/src.relative_to(stage); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dest)
shutil.copyfile(stage/'README.md',lab/'README.md')
shutil.copyfile(stage/'case002_example.md',lab/'reports/P0_1/case002_example.md')
(lab/'.gitattributes').write_text('# Exact bytes for new raw sources and run snapshots; legacy P0 attributes unchanged.\n'
    '/data/legacy_bytes/** -text\n/data/raw_sources/** -text\n/data/condition_inputs/** -text\n/runs/case*/** -text\n',encoding='utf-8')
review=lab/'evaluations/case001_qsv_select/clean/p0_qsv_select_clean_002/p0_initial_review.json'
value=read(review); value['created_at']=utc(); write(review,value)
commands=[
    (['scripts/lab.py','list'],0),
    (['scripts/lab.py','validate'],0),
    (['scripts/lab.py','plan','--case','case001_qsv_select','--condition','clean','--repeat','1'],0),
    (['scripts/lab.py','verify','--run','p0_qsv_select_clean_002','--out','results/exports/p0_qsv_select_clean_002'],0),
    (['scripts/lab.py','verify','--run','p0_qsv_select_clean_001','--out','results/exports/p0_qsv_select_clean_001'],1),
    (['scripts/verify_run.py','--run','runs/p0_qsv_select_clean_002'],0),
    (['scripts/lab.py','aggregate','--out','results/aggregates/P0_1'],0),
    (['-m','unittest','discover','-s','tests','-v'],0)]
records=[]
for n,(args,expected) in enumerate(commands,1):
    cmd=[sys.executable,'-B',*args]; started=time.monotonic()
    r=subprocess.run(cmd,cwd=lab,capture_output=True)
    stdout=r.stdout.decode('utf-8',errors='replace'); stderr=r.stderr.decode('utf-8',errors='replace')
    name=f'command_{n:02d}.log'; (lab/'reports/P0_1'/name).write_text(stdout+stderr,encoding='utf-8')
    records.append({'argv':cmd,'cwd':str(lab),'returncode':r.returncode,'expected_returncode':expected,
                    'seconds':round(time.monotonic()-started,3),'log':'reports/P0_1/'+name})
    print(json.dumps({'command':args,'returncode':r.returncode,'expected':expected}))
    if r.returncode!=expected: print(stdout+stderr)
write(lab/'reports/P0_1/commands.json',records)
before=read(lab/'reports/P0_1/project_before.json'); after=inventory(lab)
preserved=[p for p in before if p.startswith(('runs/','reports/','data/','configs/'))]
changed=[p for p in preserved if after.get(p)!=before[p]]
official_before=read(lab/'reports/P0_1/upstream_before.json')
official_after=upstream_inventory(lab.parent/'AutoSkill-main')
write(lab/'reports/P0_1/preservation.json',{'protected_existing_files':len(preserved),'changed':changed,
    'upstream_files':len(official_before),'upstream_unchanged':official_before==official_after,
    'upstream_before':official_before,'upstream_after':official_after})
git=subprocess.run(['git','-C',str(lab.parent),'status','--short','--','AutoSkill-main','degradation_failure_lab'],capture_output=True)
(lab/'reports/P0_1/git_status.txt').write_bytes(git.stdout)
bad=[r for r in records if r['returncode']!=r['expected_returncode']]
write(lab/'reports/P0_1/acceptance.json',{'status':'PASS' if not bad and not changed and official_before==official_after else 'PARTIAL',
    'paid_model_calls_this_stage':0,'new_real_runs':0,'formal_cases':['case001_qsv_select'],
    'fixture_case002':'TemporaryDirectory only; three changed-input conditions times three isolated preparations',
    'commands':len(records),'unexpected_command_failures':bad,'protected_file_changes':changed,
    'upstream_unchanged':official_before==official_after,'review_scope':'Engineering refactor, not a new paid reproduction or quality accuracy claim'})
print(json.dumps({'protected_changes':changed,'upstream_unchanged':official_before==official_after,'unexpected_commands':len(bad)}))
