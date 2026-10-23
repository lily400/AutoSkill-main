"""Scrapy024 preparation/launch; only 'run' may invoke paid Agent requests."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.io import inventory,read,sha256,write
from degradation_lab.artifacts import load_run
from downstream_eval.integration.skill_install import canonical_packages,copy_packages

PREFLIGHT=Path(r'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\scrapy024_preflight')
CONTROL='harbor-p0-control-20261018'
LINUX_ROOT='/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab'
TASK=LAB/'downstream_eval/tasks/scrapy_task024_v1'


def prepare_files(experiment):
    output=LAB/'runs/downstream/scrapy-task-024'/experiment
    output.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('scrapy_preflight_frozen',PREFLIGHT/'preflight.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    prior=module.verify()
    run=LAB/'runs/case024_scrapy/clean/s24r005'
    saved=read(run/'artifact_manifest.json')
    if any(sha256(run/name)!=h for name,h in saved.items()):
        raise ValueError('Generator run changed')
    identity,_,result,stages=load_run(LAB,'s24r005')
    expected={s['id'] for s in stages['register']['upserted_store_skills']}
    if result['status']!='completed' or not expected:
        raise ValueError('No completed registered Skill set')
    source_docs={d['doc_id'] for d in stages['ingest']['documents']}
    if any(set(p['doc_ids'])!=source_docs for p in stages['register']['provenance_links']):
        raise ValueError('Unexpected registered source documents')
    seed=read(run/'resume.json')['seed_skillbank']
    if any('/Users/' in '/'+p or p.endswith('/SKILL.md') for p in seed):
        raise ValueError('Resume seed unexpectedly contained historical final Skills')
    paths=[p for p in (run/'SkillBank/Users').rglob('SKILL.md')]
    export=output/'canonical_files.json'
    write(export,{'unique_program_skill_count':len(expected),'canonical_program_skills':[str(p) for p in paths]})
    config={'generator_run_id':'s24r005','case_id':'case024_scrapy','condition':'clean',
            'expected_skill_count':len(expected),'skill_manifest':export.relative_to(LAB).as_posix()}
    packages=canonical_packages(LAB,config)
    copy_packages(packages,output/'skills')
    write(output/'skills_manifest.json',{'generator_run_id':'s24r005','source_manifest_sha256':sha256(run/'artifact_manifest.json'),
          'registry_ids':sorted(expected),'packages':{sid:{'path':p['path'].relative_to(LAB).as_posix(),
          'version':next(s['version'] for s in stages['register']['upserted_store_skills'] if s['id']==sid),
          'metadata':p['metadata'],'files':p['files']} for sid,p in packages.items()},
          'all_generated_skill_files':[{ 'path':p.relative_to(run).as_posix(),'sha256':sha256(p)} for p in (run/'SkillBank').rglob('SKILL.md')],
          'source_doc_ids':sorted(source_docs),'resume_parent':'s24m005','seed_final_skills':0})
    TASK.mkdir(parents=True,exist_ok=True)
    def frozen_copy(source,destination):
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists() and sha256(destination)!=sha256(source):
            raise ValueError('Existing Task-024 asset differs: '+str(destination))
        if not destination.exists():shutil.copyfile(source,destination)
    frozen_copy(PREFLIGHT/'stages/agent/instruction.md',TASK/'instruction.md')
    scorer=TASK/'scorer'
    for rel in ['preflight.py','harbor_entry.py','runtime/worker.py','runtime/interface.py','runtime/oracle_bridge.py','runtime/policy_probe.py']:
        frozen_copy(PREFLIGHT/rel,scorer/rel)
    for prefix in ['stages/scorer','fixtures/submissions']:
        for source in (PREFLIGHT/prefix).rglob('*'):
            if source.is_file():frozen_copy(source,scorer/source.relative_to(PREFLIGHT))
    frozen=inventory(scorer)
    manifest=scorer/'source_manifest.json'
    expected_manifest={'schema_version':1,'task_id':'scrapy-task-024','target_rule_id':prior['target_rule_id'],
                       'frozen_inventory':frozen,'protected_audit_hashes':{},
                       'reuse_source':str(PREFLIGHT),'reuse_manifest_sha256':sha256(PREFLIGHT/'source_manifest.json'),
                       'scope':'Portable subset of the original preflight scorer; no original Oracle changes'}
    if manifest.exists():
        # The manifest is not included in its own inventory.
        expected_manifest['frozen_inventory'].pop('source_manifest.json',None)
        if read(manifest)!=expected_manifest:raise ValueError('Scorer freeze changed')
    else:write(manifest,expected_manifest)
    write(output/'task_asset_manifest.json',{'instruction_sha256':sha256(TASK/'instruction.md'),
          'original_oracle_sha256':sha256(scorer/'stages/scorer/oracle/eval.py'),
          'preflight_root':str(PREFLIGHT),'preflight_manifest_sha256':sha256(PREFLIGHT/'source_manifest.json'),
          'scorer_manifest_sha256':sha256(manifest)})
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['prepare','run'])
    parser.add_argument('--experiment',default='s24d001')
    args=parser.parse_args()
    import re
    if not re.fullmatch(r's24d[0-9]{3}',args.experiment):raise ValueError('Use an s24dNNN experiment ID')
    if args.phase=='prepare':
        output=LAB/'runs/downstream/scrapy-task-024'/args.experiment
        if not output.exists():prepare_files(args.experiment)
        elif not (output/'skills_manifest.json').is_file():
            raise RuntimeError('Incomplete freeze; do not overwrite the existing experiment')
    elif not os.environ.get('ZHIZENGZENG_API_KEY'):
        raise RuntimeError('Use Invoke-Scrapy024Calibration.ps1; no request sent')
    command=['docker','exec','--env','PYTHONPATH='+LINUX_ROOT+':'+LINUX_ROOT+'/src']
    if args.phase=='run':
        command+=['--env','ZHIZENGZENG_API_KEY','--env','SCRAPY024_ALLOW_PAID=1']
    command += [CONTROL,'/opt/harbor-venv/bin/python','-B','-m','downstream_eval.scrapy024',args.phase,
                '--experiment',args.experiment]
    result=subprocess.run(command)
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
