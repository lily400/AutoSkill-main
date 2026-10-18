"""Build a 64-task Markdown appendix and validate existing audit deliverables.

Read-only toward the upstream repository and existing data inventories.
"""
import collections, csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REQUIRED='task_id source_type source_group input_paths document_count document_lengths instruction_visibility skill_scope oracle_type oracle_files shared_rule_candidate rule_dependency_tasks degradation_suitability compatibility_risks verification_status'.split()

def invalid_constant(value): raise ValueError('Non-standard JSON constant: '+value)
def loads(s):return json.loads(s,parse_constant=invalid_constant)
def load(name):return loads((ROOT/name).read_text(encoding='utf-8-sig'))
def key(row):return row['source_type'],row['source_group'],row['task_id']
def narrative(row):return [d for d in row['document_lengths'] if d['narrative_document']]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def oracle_note(t):
 tid=t['task_id']
 if t['source_type']=='domain_knowledge_doc':
  p=t['reference_probe']; note=f"静态齐全；离线参考 {p['passed']}/{p['case_count']}"
  if tid=='lockdate_compliance_gate_001':note+='；日期异常/blocks不一致'
  elif tid=='risk_interpretation_gatekeeper_002':note+='；源评分常数缺失/期望不一致'
  elif tid=='spectrum_concentration_estimator_008':note+='；NaN不自等'
  elif tid=='gatekeeper_minireport_003':note+='；批准token分支未覆盖'
  return note
 if tid.startswith('neurokit2'):return '静态齐全；来源API仅标题骨架；容器未验'
 if tid=='scikitimage-task-001':return '静态齐全；硬编码离线通过；常数模板峰无区分'
 if tid=='scikitimage-task-002':return '静态齐全；硬编码离线通过；隐含参数风险'
 if tid=='pydantic-task-005':return '静态齐全；预建实例重验契约待核'
 if tid=='scrapy-task-024':return '离线正确19/19；单规则错误18/19；非Docker/Agent'
 if tid in {'librosa-task-001','moviepy-task-001','pillow-task-001','pillow-task-002','soundfile-task-021','soundfile-task-022','soundfile-task-023'}:
  return '静态齐全；固定fixture/API字面量弱约束；容器未验'
 if tid=='scrapy-task-050':return '静态齐全；依赖localhost爬取与子进程；容器未验'
 if tid=='soundfile-task-020':return '静态齐全；绑定安装库源码字符串；容器未验'
 return '静态齐全；行为/调用或多输入检查；容器未验'

def main():
 docs=load('sgb_document_tasks_only.json'); rows=[loads(s) for s in (ROOT/'sgb_task_inventory.jsonl').read_text(encoding='utf-8').splitlines()]
 groups=load('sgb_source_groups.json'); summary=load('sgb_data_summary.json'); files=load('sgb_document_files.json'); probe=load('domain_reference_probe_results.json')
 with (ROOT/'sgb_task_inventory.csv').open(encoding='utf-8-sig',newline='') as f:
  csvreader=csv.DictReader(f); headers=csvreader.fieldnames; csvrows=list(csvreader)
 checks=[]
 def check(name,condition,observed,expected):checks.append({'name':name,'passed':bool(condition),'observed':observed,'expected':expected})
 check('jsonl_task_count',len(rows)==187,len(rows),187)
 check('csv_task_count',len(csvrows)==187,len(csvrows),187)
 check('document_task_count',len(docs)==64,len(docs),64)
 missing=[{'task_id':t.get('task_id'),'fields':sorted(set(REQUIRED)-set(t))} for t in rows if not set(REQUIRED)<=set(t)]
 check('jsonl_all_15_required_fields',not missing,missing,[])
 check('csv_all_15_required_columns',set(REQUIRED)<=set(headers),sorted(set(REQUIRED)-set(headers)),[])
 check('unique_full_task_keys',len({key(t) for t in rows})==187,len({key(t) for t in rows}),187)
 check('unique_task_ids',len({t['task_id'] for t in rows})==187,len({t['task_id'] for t in rows}),187)
 expected_docs=[t for t in rows if t['source_type'] in ('code_doc','domain_knowledge_doc')]
 check('document_json_equals_jsonl_subset',docs==expected_docs,len(expected_docs),64)
 csv_by_key={key(t):t for t in csvrows};differences=[]
 for t in rows:
  c=csv_by_key.get(key(t))
  if c is None:differences.append({'task_id':t['task_id'],'field':'MISSING_ROW'});continue
  for field in REQUIRED:
   v=t[field];expected=json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else str(v) if v is not None else ''
   if c[field]!=expected:differences.append({'task_id':t['task_id'],'field':field})
 check('csv_jsonl_required_field_equivalence',not differences,differences,[])
 counts=dict(collections.Counter(t['source_type'] for t in rows));check('source_type_task_counts',counts=={'code_doc':28,'code_repo':123,'domain_knowledge_doc':36},counts,{'code_doc':28,'code_repo':123,'domain_knowledge_doc':36})
 check('source_group_count_all',len(groups)==77 and len({(t['source_type'],t['source_group']) for t in rows})==77,len(groups),77)
 check('source_group_task_sum',sum(g['task_count'] for g in groups)==187,sum(g['task_count'] for g in groups),187)
 group_errors=[]
 for g in groups:
  subset=[t for t in rows if t['source_type']==g['source_type'] and t['source_group']==g['source_group']];sd=[d for t in subset for d in narrative(t)]
  observed={'task_count':len(subset),'task_ids':[t['task_id'] for t in subset],'narrative_document_path_count':len(sd),'unique_document_sha256_count':len({d['sha256'] for d in sd}),'unique_document_sets':len({t['document_set_hash'] for t in subset}),'doc_chars_total':sum(d['chars'] for d in sd),'doc_words_total':sum(d['whitespace_words'] for d in sd)}
  for k,v in observed.items():
   if g[k]!=v:group_errors.append({'source_group':g['source_group'],'field':k,'actual':g[k],'recomputed':v})
 check('all_source_group_aggregates',not group_errors,group_errors,[])
 sd=[d for t in docs for d in narrative(t)];aggregate={'task_count':len(docs),'source_groups':len({(t['source_type'],t['source_group']) for t in docs}),'unique_page_or_context_files_sha256':len({d['sha256'] for d in sd}),'document_path_instances':len(sd),'document_collections_hash':len({t['document_set_hash'] for t in docs})}
 for k,v in aggregate.items():check('combined_'+k,v==summary['documents_combined'][k],v,summary['documents_combined'][k])
 chars={st:sum(d['chars'] for t in docs if t['source_type']==st for d in narrative(t)) for st in ('code_doc','domain_knowledge_doc')}
 for st,v in chars.items():check(st+'_total_chars',v==summary['source_types'][st]['doc_chars']['sum'],v,summary['source_types'][st]['doc_chars']['sum'])
 doc_count_bad=[t['task_id'] for t in docs if t['document_count']!=len(narrative(t))]
 check('per_task_document_counts',not doc_count_bad,doc_count_bad,[])
 uuid=[t['original_context_id'] for t in docs if t['source_type']=='domain_knowledge_doc']
 check('distinct_domain_context_uuid',len(uuid)==36 and len(set(uuid))==36 and all(uuid),len(set(uuid)),36)
 file_map={d['path']:d for d in files}; mismatches=[]
 for d in sd:
  if d['path'] not in file_map or any(d[f]!=file_map[d['path']][f] for f in ('sha256','bytes','chars','whitespace_words')):mismatches.append(d['path'])
 check('document_file_inventory_consistency',not mismatches,mismatches,[])
 check('reference_task_count',probe['tasks']==36 and len(probe['results'])==36,probe['tasks'],36)
 check('reference_case_totals',sum(r['case_count'] for r in probe['results'])==probe['cases']==308,probe['cases'],308)
 check('reference_pass_totals',sum(r['passed'] for r in probe['results'])==probe['passed']==302,probe['passed'],302)
 check('reference_fullpass_tasks',sum(r['passed']==r['case_count'] for r in probe['results'])==probe['all_case_pass_tasks']==33,probe['all_case_pass_tasks'],33)
 scrapy=load('scrapy_oracle_probe_results.json');sr={r['variant']:r for r in scrapy['results']}
 check('scrapy024_oracle_unchanged',scrapy['oracle_sha256_before']==scrapy['oracle_sha256_after'],scrapy['oracle_sha256_after'],scrapy['oracle_sha256_before'])
 check('scrapy024_correct_submission',sr['source_derived_correct_submission']['exit_code']==0 and '19 passed' in sr['source_derived_correct_submission']['stdout'],{'exit_code':sr['source_derived_correct_submission']['exit_code'],'passed':19}, {'exit_code':0,'passed':19})
 check('scrapy024_single_rule_mutant_rejected',sr['single_rule_mutant_ftp_true_to_false']['exit_code']==1 and '1 failed, 18 passed' in sr['single_rule_mutant_ftp_true_to_false']['stdout'],{'exit_code':sr['single_rule_mutant_ftp_true_to_false']['exit_code'],'passed':18,'failed':1},{'exit_code':1,'passed':18,'failed':1})
 text=['# 附录 A：SkillGenBench 全部64个文档任务','',
 '统计快照：GitHub `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。本表由已有机器清单生成；字符数为任务叙述性文档之和，保留工作树 CRLF，不计 Domain 的 `task.json` 描述符。',
 '', '“静态齐全”仅表示有效 Oracle 文件存在且 Python 语法通过；“离线参考 x/y”是公开参考函数与原比较函数的一致性，不代表官方 Docker/Agent 执行。所有187个生成任务外层 `task.json` 均有严格JSON解析失败，属共同风险，此表不逐行重复。',
 '', '|task_id|source_type|source_group|文档数|总字符数|Oracle静态/参考结果或关键风险|','|---|---|---|---:|---:|---|']
 for t in docs:
  text.append('|'+ '|'.join([t['task_id'],t['source_type'],t['source_group'],str(t['document_count']),f"{sum(d['chars'] for d in narrative(t)):,}",oracle_note(t)])+'|')
 text+=['', '**合计：64任务；45个库/上下文簇；106个文档路径实例；73个字节不同页面/context文件；60个文档集合。独立原始出版物数仍未知。**','']
 appendix=ROOT/'appendix_a_tasks.md';appendix.write_text('\n'.join(text),encoding='utf-8')
 check('appendix_task_rows',sum(line.startswith('|') for line in text)-2==64,sum(line.startswith('|') for line in text)-2,64)
 names=['appendix_a_tasks.md','sgb_task_inventory.jsonl','sgb_task_inventory.csv','sgb_document_tasks_only.json','sgb_data_summary.json','sgb_source_groups.json','sgb_document_files.json','domain_reference_probe_results.json','scrapy_oracle_probe_results.json','SGB_DATA_ORACLE_AUDIT_MEMO_ZH.md','scan_sgb_data.py','probe_domain_reference.py','annotate_sgb_data.py','build_data_appendix.py']
 output={'scope':'Validate existing audit inventories and produce Appendix A; no network, no upstream modifications, no new agent/container execution','validation_status':'PASS' if all(x['passed'] for x in checks) else 'FAIL','check_count':len(checks),'passed_checks':sum(x['passed'] for x in checks),'required_fields':REQUIRED,'recomputed_document_aggregate':aggregate,'supplementary_scrapy024_probe':{'source_file':'scrapy_oracle_probe_results.json','scope':scrapy['scope'],'correct_passed':19,'correct_total':19,'single_rule_mutant_passed':18,'single_rule_mutant_failed':1,'models_called':scrapy['models_called'],'limitations':scrapy['limitations']},'checks':checks,'copyable_files':[{'name':name,'bytes':(ROOT/name).stat().st_size,'sha256':sha(ROOT/name)} for name in names]}
 (ROOT/'deliverable_inventory_validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in output.items() if k not in ('checks','copyable_files')},ensure_ascii=False,indent=2))
 if not all(x['passed'] for x in checks):print(json.dumps([x for x in checks if not x['passed']],ensure_ascii=False,indent=2));raise SystemExit(1)

if __name__=='__main__':main()
