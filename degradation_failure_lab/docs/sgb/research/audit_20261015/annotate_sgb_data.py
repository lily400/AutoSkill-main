"""Apply evidence-qualified semantic annotations to scan outputs; upstream is read only."""
from pathlib import Path
import csv, hashlib, json, re

ROOT=Path(__file__).resolve().parent; REPO=ROOT/'SkillGenBench'
def readjson(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def writejson(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PURPOSE={
'beautifulsoup4-task-037':'重命名Tag且保留对象身份、子树、属性、父级位置；源码要求.name赋值',
'librosa-task-001':'单一矩阵fixture：stack_memory n_steps=3 delay=-1结果与运行时一致；API名/字面量源码检查',
'moviepy-task-001':'固定MP4/MP3元数据与运行时一致；仅API名检查，不证明close要求被执行',
'neurokit2-task-012':'多种分形维数、CV、outlier/consensus和输入响应；真实库计算与部分skip分支',
'neurokit2-task-014':'微状态管线顺序、数组形状、cluster数量；大量monkeypatch假实现约束调用契约',
'neurokit2-task-017':'EMD、全频energy、>5%选择、重建、fit error；monkeypatch约束调用参数和返回格式',
'neurokit2-task-024':'至少三种detrend、功率改善、最优method和结果形状；调用spy',
'neurokit2-task-038':'Hjorth及至少两种complexity、数值关系、低/高频分类；多输入真实库参考',
'neurokit2-task-044':'ECG波段特征、分类规则、异常索引及信号响应；缺neurokit2时importorskip',
'neurokit2-task-046':'多信号质量/伪迹mask/权重/merge；数值阈值和signal_merge spy',
'pillow-task-001':'固定灰度图片：clipped add与modulo add中心像素；API名源码检查',
'pillow-task-002':'固定帧APNG结果与reference一致；源码检查save_all/append_images/disposal/blend',
'pydantic-task-001':'Annotated validator种类、顺序日志、多个输入仿射输出；排除decorator方式',
'pydantic-task-004':'不同field discriminator的dict/model输入、嵌套union、序列化和错误标签',
'pydantic-task-005':'配置边界、预建instance重验与dict输入、禁止手工字符串变换；默认instance重验假设需核',
'scikitimage-task-001':'固定图像match_template padding形状/peak；仅字符串检查API调用',
'scikitimage-task-002':'固定角点图像，灰度/255、threshold_rel=.01、min_distance=1、前8坐标；仅API字符串检查',
'scrapy-task-024':'7 URI正例、6未知scheme反例、empty/None；纯Python返回bool与错误类型',
'scrapy-task-041':'Spider类、allowed_domains、offsite Request/meta与AST禁用全局改动；无实际offsite网络爬取',
'scrapy-task-050':'DEPTH_LIMIT=0及解释；localhost HTTP fixture + subprocess真实多层crawl',
'soundfile-task-007':'5 format/subtype组合与运行时check_format一致；AST和monkeypatch防硬编码',
'soundfile-task-010':'r+、seek(500)、truncate无参数、持久化500frames；spy及实际文件多次验证',
'soundfile-task-012':'start1000/stop1500片段、mono/stereo、top-level read spy、防全文件读取',
'soundfile-task-015':'WAV/PCM24代码和人类描述；属性访问spy/伪值可区分硬编码',
'soundfile-task-020':'无seek/tell对象拒绝、异常信息、从安装源码提取约束；特定源码字符串依赖版本',
'soundfile-task-021':'固定音频copy_metadata结果；源码出现API名，未证明调用',
'soundfile-task-022':'固定FLOAT音频读int32结果；仅dtype/int32源码字符串检查',
'soundfile-task-023':'固定音频read8/relative seek-3/read5和cursor结果；仅API名字检查',
}
FIXED={'librosa-task-001','moviepy-task-001','pillow-task-001','pillow-task-002','scikitimage-task-001','scikitimage-task-002','soundfile-task-021','soundfile-task-022','soundfile-task-023'}

def main():
 rows=[json.loads(s) for s in (ROOT/'sgb_task_inventory.jsonl').read_text(encoding='utf-8').splitlines()]
 probes=readjson(ROOT/'domain_reference_probe_results.json'); by_probe={r['task_id']:r for r in probes['results']}
 for t in rows:
  tid=t['task_id']; st=t['source_type']; t['language']='INFERRED: predominantly English; automated CJK/nonASCII counts recorded per document'
  t['original_publication_count']='UNVERIFIED: files are pages/excerpts/assembled contexts, not independent original publications'
  t['narrative_input_paths']=[d['path'] for d in t['document_lengths'] if d['narrative_document']]
  t['descriptor_input_paths']=[d['path'] for d in t['document_lengths'] if not d['narrative_document']]
  t['document_file_count_including_descriptors']=len(t['input_paths'])
  for d in t['document_lengths']:
   txt=(REPO/d['path']).read_text(encoding='utf-8-sig');d['normalized_lf_chars']=len(txt);d['normalized_lf_sha256']=hashlib.sha256(txt.encode()).hexdigest()
   d['literal_backslash_n_count']=txt.count('\\n');d['non_whitespace_C0_count']=sum(ord(c)<32 and c not in '\t\r\n' for c in txt);d['longest_line_chars']=max(map(len,txt.splitlines()),default=0)
  if st=='code_doc':
   t['oracle_semantic_review']={'status':'OBSERVED static instruction/assertion/control-flow review; no full official execution','purpose':PURPOSE[tid]}
   t['domain']='OBSERVED: '+t['source_group']+' Python library/API'
   t['active_oracle_files']=[t['task_toml'].rsplit('/',1)[0]+'/tests/'+x for x in ('test.sh','eval.py')]
   if tid in FIXED:t['compatibility_risks'].append('INFERRED: fixed fixture + source-token checks allow hardcoded-output implementations; demonstrated only for two scikitimage tasks by separate probe')
   if t['source_group']=='neurokit2':
    t['compatibility_risks'].append('OBSERVED: provided functions/*.md are API-name/heading skeletons; resources are external-link lists; detailed API contract is not in supplied text')
    t['verification_status']['source_sufficiency']='OBSERVED insufficient local API details; trained model/library inspection may compensate, not source-supported skill extraction'
    t['degradation_suitability']='CONDITIONAL: pre-existing source incompleteness dominates; do not label this supplied Clean corpus a fully sufficient original document'
   if tid=='scikitimage-task-001':t['compatibility_risks'].append('OBSERVED offline probe: constant template variance=0; both expected peaks [0,0], so coordinate semantics are not discriminated')
   if tid=='scikitimage-task-002':t['compatibility_risks'].append('OBSERVED: oracle fixes threshold_rel=.01 and image /255 preprocessing while supplied instruction/doc omit those constants')
   if tid=='pydantic-task-005':t['compatibility_risks'].append('UNVERIFIED: pre-instantiated dataclass lowercasing may require explicit revalidate_instances; dependency and instruction contract need P3 check')
   if tid in ('soundfile-task-010','soundfile-task-023','soundfile-task-007'):
    t['shared_rule_candidate']={'status':'INFERRED operational candidate, NOT verified document-causal dependence','rule':'SoundFile cursor offsets and tell are in frames; seek default absolute vs whence=1 relative','dependent_tasks':['soundfile-task-010','soundfile-task-023'],'nondependent_control':['soundfile-task-007'],'evidence':'soundfile-task-010/materials/docs/_modules/soundfile.md lines 821-874; soundfile-task-023/materials/docs/seek_overlap.md lines 3-6','limitations':'different official document sets for task010/023; instruction010 already spells out seek(500); task023 fixed-fixture oracle is weak; source-level frozen skill and local intervention not tested'}
    t['rule_dependency_tasks']=['soundfile-task-010','soundfile-task-023']
  elif st=='domain_knowledge_doc':
   context=REPO/t['narrative_input_paths'][0]; s=context.read_text(encoding='utf-8-sig');m=re.search(r'\*\*task_id\*\*:\s*([0-9a-f-]+)',s)
   t['original_context_id']=m.group(1) if m else None
   metadata=readjson(REPO/t['descriptor_input_paths'][0]);t['domain']=t['source_group'].removeprefix('clbench_').removesuffix('_2')
   t['task_type']=metadata.get('type');t['published_rule_locations']=metadata.get('info_locations',[])
   t['oracle_semantic_review']={'status':'OBSERVED common comparator + all public testcase structures and reference-call AST; source/expected semantic correctness not fully established','purpose':metadata.get('type'),'comparison':'recursive exact keys/strings/lists, numeric math.isclose rel1e-5 abs1e-8','official_case_count':t['oracle_case_count']}
   t['active_oracle_files']=[t['task_toml'].rsplit('/',1)[0]+'/tests/'+x for x in ('test.sh','eval.py','testcases.json')]
   t['reference_probe']=by_probe[tid];t['verification_status']['oracle_execution']='OBSERVED offline published-reference + unchanged comparator check only; official shell/container/agent UNVERIFIED'
   t['compatibility_risks'].append('OBSERVED: public tests/testcases.json includes solution_code and expected outputs; keep entirely outside generation and agent-visible materials')
   t['shared_rule_candidate']='OBSERVED: one official downstream task per context UUID; zero within-context 2-dependent+1-control groups'
   if by_probe[tid]['passed']!=by_probe[tid]['case_count']:t['compatibility_risks'].append('OBSERVED offline reference inconsistency: '+str(by_probe[tid]['passed'])+'/'+str(by_probe[tid]['case_count'])+' pass; inspect reference vs source vs expected before attributing any model failure')
   if tid=='gatekeeper_minireport_003':t['compatibility_risks'].append('OBSERVED: reference uses process-salted hash(seed) for approval token; all 9 expected tokens are None, leaving approval path untested')
   if tid=='risk_interpretation_gatekeeper_002':
    t['compatibility_risks'].append('OBSERVED: context.md line112 substitutes scoring/rules with a bracketed placeholder; reference constants .521/.173/.241/.065/.447/.250/.705/.515 do not appear anywhere in generation source bundle')
    t['verification_status']['source_sufficiency']='OBSERVED scoring-rule specification missing at its claimed context location; source-to-oracle sufficiency fails for exact document-specific constants'
   hazards=[d for d in t['document_lengths'] if d['narrative_document'] and (d['non_whitespace_C0_count'] or d['literal_backslash_n_count']>100 or d['longest_line_chars']>4000)]
   if hazards:t['compatibility_risks'].append('OBSERVED raw text extraction/layout artifacts (C0/form-feed, literal backslash-n, or long lines); see document_lengths. These flags are not by themselves proof of semantic corruption')
  else:t['oracle_semantic_review']={'status':'UNVERIFIED semantics; full structural inventory only; supplementary source type'}
  t['compatibility_risks']=list(dict.fromkeys(t['compatibility_risks']))
 (ROOT/'sgb_task_inventory.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in rows),encoding='utf-8')
 fields=list(dict.fromkeys(k for t in rows for k in t))
 with (ROOT/'sgb_task_inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in t.items()} for t in rows)
 summary=readjson(ROOT/'sgb_data_summary.json')
 summary['domain_reference_probe']={k:v for k,v in probes.items() if k!='results'}
 summary['shared_rule_coverage']={'published_rule_to_multiple_tasks_mapping':0,'verified_2dependent_1control_source_groups':0,'operational_candidate_groups':1,'candidate_source':'soundfile','limitations':'0 verified is not proof of mathematical impossibility; candidate requires uniform source and causal intervention; no claim from shared library name alone'}
 summary['documents_combined']={'task_count':64,'source_groups':45,'unique_page_or_context_files_sha256':73,'document_path_instances':106,'document_collections_hash':60,'original_independent_publications':'UNKNOWN','parent_families':'9 libraries + CLBench-derived corpus; 36 distinct CLBench context UUIDs are clusters, not necessarily independent publications','verified_official_executable_oracles':0,'complete_static_oracle_bundles':64,'active_python_oracles_syntax_valid':64,'same_test_sh_sha256':'2ad84cb7df6840331626a506a5e106ddb79de898da1737bf21471f1d3b8d472a'}
 for st in ('code_doc','domain_knowledge_doc'):
  docs=[d for t in rows if t['source_type']==st for d in t['document_lengths'] if d['narrative_document']];unique={d['sha256']:d for d in docs}.values()
  summary['source_types'][st].update({'unique_document_chars':sum(d['chars'] for d in unique),'unique_document_whitespace_words':sum(d['whitespace_words'] for d in unique),'all_document_whitespace_words':sum(d['whitespace_words'] for d in docs)})
 writejson(ROOT/'sgb_data_summary.json',summary)
 writejson(ROOT/'sgb_document_tasks_only.json',[t for t in rows if t['source_type']!='code_repo'])
 print('Annotated',len(rows),'tasks; document-only detailed entries',sum(t['source_type']!='code_repo' for t in rows))
if __name__=='__main__':main()
