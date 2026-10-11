"""Task-local staging installer; not part of the research framework."""
import json, pathlib, shutil, sys
lab = pathlib.Path(sys.argv[1]).resolve()
stage = pathlib.Path(__file__).parent
sys.path.insert(0, str(stage/'src'))
from degradation_lab.io import read, write, sha256
from degradation_lab.schema import SCHEMAS
for folder in ('src','scripts','tests'):
    for src in (stage/folder).rglob('*'):
        if src.is_file():
            dst = lab/src.relative_to(stage)
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dst)
cfg=read(lab/'configs/clean_qsv_select_non_thinking.json')
write(lab/'configs/environment.json', {'upstream_path':cfg.pop('upstream_path')})
cfg.pop('source_manifest')
overrides={k:cfg['pipeline'].pop(k) for k in ('domain','domain_type','family_name')}
cfg['pipeline'].pop('max_documents')
cfg['llm']['connector_factory']='degradation_lab.provider_adapter:build'
cfg['configuration_note']='Shared model/transport/budget configuration. Case and source identities are separate. Original upstream prompts and stage budgets unchanged.'
write(lab/'configs/generation/deepseek_flash.json',cfg)
source=read(lab/'data/manifests/qsv_select.json')
sid=source['source_id']; case_id='case001_qsv_select'; base=lab/'cases'/case_id
write(lab/'data/catalog.json',{'schema_version':1,'datasets':[{'dataset_id':'qsv','description':'Pinned official sources reconstructed from qsv; not confirmed paper snapshots',
    'source_manifests':['data/manifests/qsv_select.json']}]})
write(base/'case.json',{'schema_version':1,'case_id':case_id,'dataset_id':'qsv','title':'qsv select Clean baseline',
    'source_ids':[sid],'generation_config':'configs/generation/deepseek_flash.json','pipeline_overrides':overrides})
rules=read(lab/'data/manifests/qsv_select_rules.json')
write(base/'rules.json',{'schema_version':1,'case_id':case_id,'classification':'CUSTOM_TEST_DATA',
    'provenance':{'file':'data/manifests/qsv_select_rules.json','sha256':sha256(lab/'data/manifests/qsv_select_rules.json')},
    'rules':[{'rule_id':r['id'],'text':r['rule'],'source_evidence':[{'source_id':sid,'lines':r['lines']}],
              'rule_type':'command_behavior','annotation_status':'analyst_checklist'} for r in rules['rules']]})
write(base/'conditions.json',{'schema_version':1,'case_id':case_id,'conditions':[{'condition_id':'clean','kind':'clean',
    'input_manifest':f'cases/{case_id}/inputs/clean.json','operator':None,'parameters':{}}]})
write(base/'inputs/clean.json',{'schema_version':1,'case_id':case_id,'condition_id':'clean','inputs':[{
    'input_id':'input001','source_id':sid,'source_sha256':source['sha256'],'path':source['local_path'],'sha256':source['sha256']}]})
write(lab/'runs/legacy_index.json',[{'case_id':case_id,'condition_id':'clean','run_id':f'p0_qsv_select_clean_{n}',
    'path':f'runs/p0_qsv_select_clean_{n}'} for n in ('001','002')])
for name,schema in SCHEMAS.items(): write(lab/'schemas'/(name+'.schema.json'),dict(schema,**{'$schema':'https://json-schema.org/draft/2020-12/schema','title':name}))
trace=read(lab/'runs/p0_qsv_select_clean_002/exports/traceability.json')
A='3aab94b4-5f80-54ee-89cd-136656f9e5d6'; B='a4333861-781b-5e31-8d77-8610cdcd674d'
by_id={s['skill_id']:s for s in trace}
line_map={'R1':{A:[39]},'R2':{A:[41,43]},'R3':{A:[42]},'R4':{A:[44,46],B:[32]},'R5':{A:[46,94]},'R6':{A:[47]},'R7':{}}
notes=[
    '正确表达；未执行命令。',
    '正确表达；普通位置与同名出现次数的索引区别得以保留。',
    '正确表达。',
    '命令规则正确表达；B 的额外使用限制不受原文支持，单列 generated_addition 记录。',
    '正确表达主要规则；跨 qsv 版本/随机算法的严格重现性未验证。',
    '引用要求已表达；原示例转义写法的 PowerShell 实际参数传递仍待人工/执行审核。',
    '缺失；当前技能集合未覆盖整份帮助文档。第二窗口规划为空，非原文缺失。']
def refs(ids):
    out=[]
    for sid in ids:
        s=by_id[sid]
        for stage,key in [('window','window_ids'),('support','support_ids'),('draft','source_draft_ids')]:
            out += [{'stage':stage,'entity_id':v} for v in s[key]]
        out += [{'stage':'spec','entity_id':sid},{'stage':'skill','entity_id':sid}]
    return list({(r['stage'],r['entity_id']):r for r in out}.values())
records=[]
for r,note in zip(rules['rules'],notes):
    ids=list(line_map[r['id']])
    records.append({'record_id':r['id']+'_preservation','rule_id':r['id'],'judgment_scope':'rule_preservation',
        'status':'uncertain' if r['id']=='R6' else ('incorrect' if r['id']=='R7' else 'correct'),
        'source_evidence':[{'source_id':sid,'lines':r['lines']}], 'skill_ids':ids,'trace_refs':refs(ids),
        'generated_evidence':[{'skill_id':sk,'lines':ln} for sk,ln in line_map[r['id']].items()],
        'error_types':['rule_omission'] if r['id']=='R7' else [],'notes':note})
records.append({'record_id':'R4_addition','rule_id':'R4','judgment_scope':'generated_addition','status':'incorrect',
    'source_evidence':[{'source_id':sid,'lines':[87,90,154]}],'skill_ids':[B],'trace_refs':refs([B]),
    'generated_evidence':[{'skill_id':B,'lines':[36,64]}],'error_types':['unsupported_addition'],
    'notes':'仅在输出将共享或发布时使用不受原文支持；不改变 R4 命令规则正确表达的原始判断。'})
reviewfile=lab/'reports/quality_review.md'
write(lab/f'evaluations/{case_id}/clean/p0_qsv_select_clean_002/p0_initial_review.json',{
    'schema_version':1,'evaluation_id':'p0_initial_review','case_id':case_id,'condition_id':'clean','run_id':'p0_qsv_select_clean_002',
    'created_at':'2026-10-10T00:00:00+00:00','method':'manual','reviewer':'assistant_source_comparison_imported_from_P0',
    'provenance':{'file':'reports/quality_review.md','sha256':sha256(reviewfile)},'records':records})
# Existing retention rules remain; pinned P0 experiments remain tracked and untouched.
ignore=lab/'.gitignore'
ignore.write_text(ignore.read_text(encoding='utf-8')+'\n# New full run artifacts: retain locally, commit only curated snapshots explicitly.\n/runs/case*/\n/results/exports/\n/results/aggregates/\n',encoding='utf-8')
print(json.dumps({'installed':'generic package + case001 + schemas + legacy index + imported review', 'source_keys':list(source)}))
