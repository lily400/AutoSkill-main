import hashlib,importlib.util,json,shutil,sqlite3,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

root=Path(r'D:\AS\AutoSkill-main\degradation_failure_lab');sys.path[:0]=[str(root),str(root/'src')]
from downstream_eval.sgb import runner
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=root/'results/sgb/audits/task003-execution-sn3g001';output=root/'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001'
runner.verify_frozen(root,output)
spec=importlib.util.spec_from_file_location('task003_cli',root/'scripts/sgb/sanctuary002.py')
cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
history=cli.history('task003-preflight-sn3g001')
assert history['status']=='PASS'
db=sqlite3.connect((output/'budget.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)
db.row_factory=sqlite3.Row
arms=[dict(r) for r in db.execute('select arm,state from arms')]
attempts=db.execute('select count(*) from attempts').fetchone()[0]
halt=db.execute('select halt from policy').fetchone()[0];db.close()
assert attempts==9 and halt is None and all(a['state']=='DONE' for a in arms)
results={label:read(output/'outcomes'/label/'result.json') for label in ('NoSkill1','CleanSkill1')}
for label,value in results.items():
    assert value['model_api_results'] is True and value['infra_ok'] is True
    score=value['oracle'];assert score['infra_ok'] is True and score['candidate_binding_verified'] is True
    assert score['task_result']['tests']==8 and not score['task_result']['errors'] and not score['task_result']['skipped']
    assert (score.get('oracle_sha256') or score.get('oracle_original_sha256'))=='57eb8902f1d0a5601bef71f1affaa944c2b946427c0e2e40e9a58c5d48f437eb'
assert not results['NoSkill1']['task_success'] and results['CleanSkill1']['task_success']
assert not any((output/'staged/NoSkill').rglob('*'))
attribution=read(root/'results/sgb/attributions/sn3e001-v1/report.json')
assert attribution['comparability']=='eligible' and attribution['task_difference']=='possible_help'
assert len(attribution['assertion_differences'])==8
assert all(x['difference']=='possible_help' for x in attribution['assertion_differences'])
usage=read(root/'results/sgb/analyses/sn3e001/CleanSkill1-skill-usage.json')
assert usage['counts']['model_file_access_observed']==2
assert usage['counts']['full_body_in_successful_model_request']==0
assert all(r['downstream_links'][0]['delivery']['before_action'] is True for r in attribution['rule_reviews'])
source=root/'data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md'
assert digest(source)=='7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c'
frozen=read(output/'skill_freeze.json');assert frozen['skill_count']==21
for name,h in frozen['files'].items():assert digest(output/'skills'/name)==h
for run_id in ('sn3g001','sn3r001'):
    run=root/'runs/gen/sgb/case003_san/clean'/run_id
    assert all(digest(run/name)==h for name,h in read(run/'artifact_manifest.json').items())
generation=read(root/'runs/gen/sgb/case003_san/clean/sn3r001/execution.json')
assert generation['cumulative_http_attempts']==124 and generation['cumulative_usage_totals']['total_tokens']==514291
git=subprocess.run(['git','-C',str(root.parent),'diff','--check'],capture_output=True,check=True)
names=subprocess.run(['git','-C',str(root.parent),'diff','--name-only'],capture_output=True,text=True,check=True).stdout.splitlines()
assert set(names)=={'degradation_failure_lab/configs/attribution/sn3e001.json','degradation_failure_lab/data/manifests/sgb/gates/t-febd929cffec.json','degradation_failure_lab/results/run_index.jsonl'},names
stamp=datetime.now(timezone.utc).isoformat()
value=dict(schema_version=1,completed_at=stamp,task_id='sanctuary_endgame_scheduler_002',
    final_generator='sn3r001',interrupted_parent='sn3g001',experiment='sn3e001',
    history=history,frozen_execution='VERIFIED',frozen_skills=21,source_sha256=digest(source),
    ledger=dict(arms=arms,http_attempts=attempts,halt=halt),
    generation=dict(cumulative_http_attempts=124,observed_tokens=514291,initial_limit_stop=True,
                    cumulative_caps=dict(http_attempts=300,observed_tokens=1000000)),
    scores={k:dict(task_success=v['task_success'],oracle=v['oracle']['task_result'],http_attempts=v['http_attempts'],token_usage=v['token_usage']) for k,v in results.items()},
    comparability=attribution['comparability'],task_difference=attribution['task_difference'],
    skill_usage=dict(status=usage['status'],counts=usage['counts'],pre_action_rule_fragments_confirmed=True,behavioral_use='UNKNOWN'),
    semantic_review=dict(correct=3,uncertain=1),causal_verification='NOT_PERFORMED_SINGLE_PAIR_HYPOTHESIS',
    provider_billed_cost_usd=None,git_diff_check='PASS',modified_existing_files=names,
    implementation_changes=[],degraded_documents=0,git_commits=0,git_pushes=0)
target=audit/'final-acceptance.json'
if target.exists():raise FileExistsError(target)
target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scripts=audit/'operator-scripts';scripts.mkdir(exist_ok=False)
for filename in ['task003_authorize_generation.py','task003_authorize_resume.py','task003_package_upstream.py','task003_review_and_bind.py','task003_build_attribution.py','task003_final_acceptance.py']:
    shutil.copyfile(Path(__file__).parent/filename,scripts/filename)
report='''# Task003 Sanctuary002：真实 Clean 全流程执行报告

本次已完成真实生成恢复链、质量记录、最终 Skill 冻结、真实包原生零模型验收、一对 NoSkill/CleanSkill 执行、独立原 Oracle 评分及差分归因。没有修改 Anything2Skill 核心、Agent 或 Oracle。

| 条件 | 原 Oracle | 整题成功 | HTTP | 输入 token | 输出 token |
|---|---:|---|---:|---:|---:|
| NoSkill1 | 0/8 | false | 6 | 20142 | 1982 |
| CleanSkill1 | 8/8 | true | 3 | 22029 | 1685 |

两组均 infra_ok=true，候选提交绑定通过，原 8 个断言全部完成，errors=skipped=0。账本两组 DONE、总 9/12 HTTP、halt=null。配置公平性及差分审查 eligible；8 项断言均 FAIL→PASS，整题差分 possible_help。每组仅一次，不估计稳定成功率。

## 来源与生成链

- 原 clean 源文 SHA256：7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c。输入只有该文档，无测试/参考实现。
- sn3g001：提取和编译已完成，注册时达到原 450000 token 阈值而停止；94 HTTP、452392 已观测 token，包含一次失败 HTTP。它是上游额度中止，不是普通下游任务失败。
- 用户明确批准门禁持久变更和完整真实执行，并允许必要额度调整。记录保存在 results/sgb/authorizations/；没有伪造批准来源。
- sn3r001：沿现有安全恢复器复用完成阶段和 9 条分类缓存，追加 30 HTTP、61899 token；父子累计 124 HTTP、514291 已观测 token，累计上限调整为 300 HTTP / 1000000 token。未清零计数或覆盖原运行。
- 1 个文档、13 个窗口、35 条支持证据、35 个草稿、35 个编译 spec；最终活动包 21 个 Skill，公共冻结器已校验完整父子链、最终注册版本、来源及逐文件哈希。

通用单运行 verify 的原始状态保留为 PARTIAL：恢复运行继承阶段、SkillBank 非空，且官方注册去重合并改变了一个非目标 Skill 的正文和 support 集合。没有把这些检查强行改成 PASS。详细原检查与最终活动包校验见 generation-lineage-validation.json；下游使用的是未经修改的公共冻结器认可的最终活动包。

## 规则、读取与行为

三条数值规则经来源比对为 correct；额外回合的完整顺时针表达为 uncertain，未排除该样本或修补正文。Reviewer 为 Codex assistant，明确不是独立人工签审。完整记录见 evaluations/case003_san/clean/sn3r001/pre_downstream.json 和 results/sgb/upstream/sn3r001/manual-quality-audit.md。

CleanSkill 在 episode 1 访问两份相关 SKILL.md；相关 4/10/5 片段进入成功请求 2，随后工具动作 3 写出正确的阈值 4 和标记 10/5。NoSkill 实际提交用了 1 和 2/1。上述代码及时间关系是可校验事实。

使用审计状态仍是 FILE_ACCESSED_BODY_CONTEXT_NOT_FULLY_CONFIRMED：安装/索引为 21，文件访问为 2，完整正文进入成功请求的确认数为 0。不能把规则片段的动作前交付升级为全部正文交付、理解或行为依赖。要求正文读取的协议存在观测限制，但不抹去完整执行与有效评分。

差分仅表明该配对中可能帮助。数值规则解释改进属于有机制证据的候选假设；未做受控规则干预或重复运行，不能宣称稳定收益或已验证因果。四条规则均保留源文→窗口→support→draft→spec→registered→skill 的实体与哈希映射，含显式不确定性。

源文/Skill 的洗牌描述比任务 pile_recycled 的 trigger-turn-only 契约更宽；本次 CleanSkill 按任务契约实现且通过。该范围区别保留，不作为源文错误或已证实失败原因。

## 工程验收与保护

真实包原生 prepare 两组 PASS、模型调用 0；模型运行只启动一次配对。NoSkill staged 目录为空，没有本次源文或 Skill。固定镜像、工具权限、同一 runtime-note、模型、原 Oracle 和预算保持可比。

Windows→Linux 审核曾遇到 resource 及快照源码路径问题。使用既有 Linux 控制环境，并复制 166 份同哈希源码建立临时控制侧路径别名；不挂载给 Agent，不改校验函数、源文或历史快照。记录见 controller-source-path-map.json。

历史保护快照中的全部旧文件校验通过，run_index 只追加；冻结执行文件及两次生成的 artifact manifests 均验证通过。既有修改为已授权 gate、本次归因 spec 和 run_index 的追加，另有新恢复配置和新产物。未提交/推送 Git，未构造退化文档。

费用只报告实际请求和观测 token。提供商真实账单未提供；SDK 的参考成本不当作实际支付金额，失败 HTTP 的未观测使用量也不补成零。

## 复核入口

- results/sgb/baselines/sn3e001/baseline.json、baseline.md：框架正式四状态报告。
- results/sgb/analyses/sn3e001/：逐组评分、读取及成本观测。
- results/sgb/attributions/sn3e001-v1/report.json、report.md：配对资格、逐断言差分、14 个哈希绑定证据和候选归因。
- runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/：Skill 冻结、ledger、原生轨迹、提交与原 Oracle。
- final-acceptance.json：最终保护和验收；operator-scripts/：本次操作脚本，均有已存在输出保护，不能用于重启已有试验。

已停止新增调用。后续重复、规则干预或 Degraded 实验另行设计；本次结果不扩展为完整游戏规则或整个 SkillGenBench 的效果估计。
'''
(audit/'execution-report.md').write_text(report+'\nCompleted UTC: '+stamp+'\n',encoding='utf-8')
print(json.dumps({'history':history['status'],'history_files':history['files'],'frozen_execution':'VERIFIED','ledger_attempts':attempts,'report':str(audit/'execution-report.md')},ensure_ascii=False))
