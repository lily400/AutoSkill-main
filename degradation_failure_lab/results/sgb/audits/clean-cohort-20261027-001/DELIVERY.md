# Clean 10 任务：零模型修复与执行准备交付

日期：2026-10-27。研究目标仍是 A2S 文档生成 Skill → Terminus-2 NoSkill/CleanSkill 配对；本轮没有新的付费模型调用，没有生成新 Skill，没有开展退化。

现有流程可以继续使用。统一配对、失败分类、正式索引及版本追溯已修复并完成必要回归。当前不是“10 个任务全部就绪”：5 个技术 READY，5 个 NEEDS_WORK；1 个历史配对可正式复用，2 个 Scrapy 新配对完成最终零模型预检，另 2 个领域任务需要先授权提取 Skill。未经新增授权，本轮不启动任何付费运行。

## 1. 实际修改及验证依据

未重写 Agent、SkillBank、Harbor 或预算系统。两个新领域任务共用同一个 JSON 观察适配器。修改清单共 56 个文件：其中包括两套任务各 10 个资产文件、各 4 个 case 配置文件；原题面和原始 Oracle 是校验一致后复制的资产，不是改写测试。

| 修改位置 | 改动和作用 |
|---|---|
| `configs/sgb/clean_pair_protocol.json`、`downstream_eval/sgb/protocol.py`、`clean_skill_read.md` | `clean-pair-v1` 固定两臂各一次、模型、预算和通用阅读协议；两臂都接收同一阅读说明。校验实际 Harbor 配置，防止“两臂彼此相等但一起偏离正式协议”。 |
| `downstream_eval/sgb/pilot.py`、`runner.py` | prepare 冻结协议、任务配置和执行代码；执行前再次验证。异常也保存每臂结果、批结果和停止证据。仅在既有账本允许时继续另一臂；不复位、不重发、不清除未知请求。 |
| `downstream_eval/scoring/results.py`、`sgb/attribution.py` | 分开任务失败、预算耗尽、基础设施故障。没有提交/非法提交/候选程序超时等可在有控制器证据时记任务失败，不要求伪造 JUnit；普通错误答案仍要求真实完整 JUnit，哈希不符仍阻断。 |
| `audited/common.py`、`audited/scrapy024.py`、`scrapy041/adapter.py` | 缺失或非法导出返回明确的候选失败，而不是一概记基础设施故障；保留传输、来源和哈希错误为基础设施问题。 |
| `sgb/cohort.py`、`src/degradation_lab/cli.py`、`configs/sgb/clean10.json` | 正式汇总显式索引 10 个不同任务及其唯一配对，检查 task/case/generator 身份，沿用 `attribution.audit_pair`。不再依赖仅含 legacy_runs 的旧入口。保留部分配对已发生的结果；未启动臂不造分数。 |
| `data/manifests/sgb/history_clean10.json`、本目录版本快照 | 按内容哈希查找历史代码，不覆盖旧运行，不用历史别名授权执行。 |
| `audited/json_task.py`、`audited/agent.py` | 新增 JSON 任务通过配置绑定现有原生执行和 FLA 评分桥，逐字校验原题面/Oracle/testcases/setup/source，不为每题写一套框架。 |
| `src/degradation_lab/runner.py`、两个新 BLOCKED gate | 仅新任务使用 `exact-generation-v1`，校验 case/condition/run/config SHA/HTTP 与 Token 上限后才允许凭据及执行；原授权门禁不变。新 JSON 下游也核验精确 generator/experiment/task-config SHA/12 次上限。 |
| 两个 case、task config、运行资产、正反例 fixture；`tasks.jsonl`、dataset manifest | 接入 monitoring/capacity；187 行 registry 只更新对应 2 行，其余 185 行逐字保留，更新 registry 哈希。fixture 仅用于零模型工程测试，不进入 Agent 输入。 |
| `tests/test_clean_cohort.py`、`test_sgb_runner.py`、`test_sgb_task_contract.py` | 覆盖失败分类、未知 HTTP、部分配对、身份混用、协议偏移、门禁和 JSON 资产。更新控制器异常应有标准结果的工程断言；没有修改 SGB 原始测试。 |

逐文件哈希与差异：[changes.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/changes.json>)、[changes.diff](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/changes.diff>)。`before/` 保存可用旧版本，`revisions/` 保存中间修复版本；清单中的 first_saved_revision 对新文件可能是本轮早期版本，不冒充仓库初始版本。

正式协议：`openai/gpt-5.4-mini-2026-03-17`，相同 base URL、API 格式、temperature=0、reasoning=none；每臂 6 次 HTTP、单请求输入≤20,000、累计输入≤100,000、输出≤2,048、请求45秒、Agent300秒、setup90秒、Verifier60秒、重试0。相同题面、工具、环境、网络限制、独立 Oracle 和通用阅读说明；唯一实验处理是 CleanSkill 安装冻结包并提供索引。原始任务之间的 Oracle/依赖可以不同，同一任务两臂必须相同。

失败解释：

- `task_failure`：错误答案、无提交、非法提交、候选程序自身超时；按整题失败计数，测试数可以为0。
- `budget_exhausted`：已知 HTTP/输入 Token 限额或 Agent 时间耗尽；按本次固定预算下的失败保留，不从成功率分母剔除。
- `infrastructure_failure`：环境/评分器故障、哈希或来源问题、非2xx/RESERVED/UNKNOWN 请求等；结果标为不可评分，单列，不当作 Agent 成败。未知请求的账本停止策略继续生效。

## 2. 修复前后零模型验证

| 验证 | 修复前 | 修复后 |
|---|---|---|
| 原 runner 基线 | 22/22 通过 | 扩展后24/24通过 |
| 三个针对性回归：缺失提交、预算中止记录与安全继续、评分器异常记录 | 旧 runner 代码在内存加载，3/3失败 | 3/3通过 |
| 本轮相关套件（去重） | — | 170/170通过：runner24、pilot11、SGB17、task-contract12、attribution27、新 cohort15、Scrapy041 11、Sanctuary42、request-budget11 |
| 广义 framework 套件，同样的 Windows 路径/依赖归一环境 | 17通过、1失败 | 17通过、同1失败 |
| 两个新 JSON 任务真实隔离评分器 | — | reference 10/10与8/8；规则破坏 fixture 1/10与0/8，四项工程验收均达到预期 |

广义套件的既存失败位于 `tests/test_framework.py:94`，错误假定仓库只有 case001_qsv_select；修复前已有13个 case，本轮后15个。未扩大范围修改该测试，因此不声称全仓测试全绿。早期 Linux 全仓尝试还遇到控制容器未挂载 A2S 上游目录的导入错误，不能将该环境错误视为代码回归；相关组件已在适合的平台单独验证。

reference fixture 来自公开参考实现，只验证观察与评分传输自洽；其通过不能证明实验有效。新任务另行检查了原文规则与发布测试的关系，见下面证据。所有工程结果明确 `real_agent_outcome=false`，不会进入正式任务成功率。

[前后回归](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/before-after-regressions.json>)；[Windows最终测试](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/release-windows-tests.json>)；[Linux新增测试](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/release-linux-tests.json>)；[其余Linux组件](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/final-linux-tests.json>)；[预算测试](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/test_request_budget.py.linux.log>)；[广义测试前后](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/framework-baseline-comparison.json>)；[JSON隔离评分](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/json-acceptance/acceptance.json>)；

## 3. 10 个任务最新准入及最少工作

READY 表示任务语义、原文、评分和当前适配已达到准入条件；生成/执行授权另行判断。NEEDS_WORK 不进入正式付费队列。所有文档是本地固定的 SGB 任务文档快照，不把它们等同于完整上游出版物。

| 顺序 / 任务 | 文档与Verifier | 状态 | 已有材料与最少剩余工作 |
|---|---|---|---|
| 1. `sanctuary_endgame_scheduler_002` | 领域规则；8例JSON（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/domain_knowledge_doc/clbench_Empirical_Discovery_Simulation_Simulation_Environment/sanctuary_endgame_scheduler_002/tests/eval.py>)） | **READY** | 可复用 sn3r001→sn3e001；不用重跑。规则覆盖和真实轨迹已核验。 |
| 2. `scrapy-task-024` | 编程文档：feed exports；发布eval（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/a3831d75f00d59a0/feed-exports.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/scrapy/scrapy-task-024/tests/eval.py>)） | **READY** | 复用 s24a001 的15包；c24f002预检PASS，获批后执行一次配对并分析。 |
| 3. `scrapy-task-041` | 4份编程文档；发布eval＋既有观察桥（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/dad43df16d07e2c3/offsite.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/scrapy/scrapy-task-041/tests/eval.py>)） | **READY** | 复用 s41r003 的45包；c41f002预检PASS。保留 allow_offsite 提取遗漏；披露版本适配。 |
| 4. `monitoring_gap_brief_classifier_001` | 生态监测领域文档；10例JSON（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/afa2a07eb645af22/context.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/domain_knowledge_doc/clbench_Domain_Knowledge_Reasoning_Science/monitoring_gap_brief_classifier_001/tests/eval.py>)） | **READY** | case101_monitor/通用JSON适配已验收；先批准 m01g001提取，再冻结、精确授权、prepare m01f001、配对。 |
| 5. `capacity_aware_edge_admission_controller_006` | 交通容量/时序规则；8例JSON（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/0e5060b3133dcd4b/context.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/domain_knowledge_doc/clbench_Empirical_Discovery_Simulation_Simulation_Environment_2/capacity_aware_edge_admission_controller_006/tests/eval.py>)） | **READY** | case102_capacity/同一JSON适配已验收；先批准 e06g001提取，再冻结、精确授权、prepare e06f001、配对。 |
| 6. `pydantic-task-001` | validators编程文档；发布eval（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/46a8a05c8a6e74d7/validators.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/pydantic/pydantic-task-001/tests/eval.py>)） | **NEEDS_WORK** | 固定Pydantic2依赖；补对象/日志观察与顺序破坏反例。原Oracle部分日志为自报证据，须披露范围。 |
| 7. `scrapy-task-050` | depth＋settings两文档；发布eval（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/96e60bee5903c18a/depth.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/scrapy/scrapy-task-050/tests/eval.py>)） | **NEEDS_WORK** | 明确仅验证配置语义的范围；补有界隔离loopback爬取观察，配置和正反例验收；无需重写爬虫框架。 |
| 8. `pydantic-task-004` | TypeAdapter＋unions两文档；发布eval（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/b2eebb8a33d02993/type_adapter.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/pydantic/pydantic-task-004/tests/eval.py>)） | **NEEDS_WORK** | 补完嵌套辨别联合与metadata语法的规则到测试核对；与001共享一类Pydantic观察桥。 |
| 9. `ops_pack_gate_a_egress_veto_002` | 运营规则文档；发布JSON精确比较（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/caa86c07f64d6016/context.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/domain_knowledge_doc/clbench_Rule_System_Application_Legal_Regulatory_2/ops_pack_gate_a_egress_veto_002/tests/eval.py>)） | **NEEDS_WORK** | 请求字段、重叠与优先级有契约缺口。仅允许接口澄清；若需要注入文档阈值/答案或改Oracle则替换。 |
| 10. `shark_warranty_safety_gate_001` | 操作/安全流程文档；发布JSON精确比较（[原文](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/sgb/5a8bd61d/a42ca100c5cea725/context.md>)；[Verifier](<D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/domain_knowledge_doc/clbench_Procedural_Task_Execution_Instructional_Procedures/shark_warranty_safety_gate_001/tests/eval.py>)） | **NEEDS_WORK** | issue代码/顺序及温度笔误未闭合。只有不暴露目标规则的澄清才可准入，否则替换。 |

[准入清单与全部源文档/Oracle SHA](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/sgb/clean10.json>)；[替代任务排除记录](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/admission.json>)。

monitoring：原文96–126、168行建立系统/非系统/待加强监测分类；逐条核对10个发布例，保留任务提供的输出枚举与默认约定，不向 Agent 提供参考函数。capacity：原文R26/R27、事故半开区间、车道映射、N3/N4周期及取整例（154–161、225–235、293–330、570–572行）可支撑8例；任务自身明确只对N3/N4信号化，按任务抽象执行。两者均可由 A2S 直接处理 Markdown，未来也适合按规则单元做可控退化；本轮不施加退化。

Scrapy041 使用既有 Scrapy2.13观察环境；发布任务声明2.12，而提供的 offsite 文档反映更新API。两臂同环境，现有桥通过正反例验收，但结论限于已披露的派生环境，不能称为完全复现原SGB默认环境。Skill 内缺失 allow_offsite 是保留的提取失败证据，不手工补写。

已检查并排除的替代项：BeautifulSoup037 要求题面未承诺的同对象身份与字面 `.name=` 赋值，澄清该机制会泄露目标解法；FLA002 未定义分类编码且以子串启发式识别共享；wall scheduler 有冲突阈值/全局优先级；proactive delay 的定时常量无来源依据；soundfile010/015 题面已给出关键API，未建立剩余文档依赖；gatekeeper 和 ternary mux 有任意错误码/信号名精确比较。保留这些任务的历史，不为凑10降低准入标准。

当前覆盖编程文档、领域规则、多文档；操作流程任务仍未准入，不能宣称该类型已有正式覆盖。

## 4. 历史复用、版本和最终预检

- **正式复用**：Sanctuary `sn3r001→sn3e001`；真实模型/预算/两臂通用阅读说明符合当前协议，`audit_pair=eligible`，执行清单573项可追溯，9项通过相同内容哈希的存档恢复。结果为 NoSkill整题失败（0/8），CleanSkill整题成功（8/8）；仅一组观测。
- **仅复用生成包**：Scrapy024 `s24a001` 与 Scrapy041 `s41r003`。旧下游的阅读协议不符合本次正式协议，旧结果保留在探索材料，不能并入本队列；本轮已准备新配对，不重新提取。
- FLA历史生成与下游保留，因Oracle语义问题排除正式统计；已有BeautifulSoup/Pydantic工程验收也不冒充真实Agent结果。
- 历史生成均为 DeepSeek flash、同类提取策略，但总调用/Token门槛不同：s24a001=150/450k，sn3r001=300/1m，s41r003=250/900k；文档数分别1/1/4。它们可用于各自固定Skill的下游配对；不得声称是统一生成预算下的跨任务提取成功率实验。

[integrity.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/integrity.json>) 验证 19,111 个历史产物、99 个源文件、2,001 个原始任务资产零漂移；四个历史生成清单共2,401个文件及各自A2S上游身份零漂移。没有新增 m01g001/e06g001 生成目录。原有授权门禁未改，两个新增门禁仍BLOCKED。

历史索引仍有8个旧哈希无法恢复：5个来自早期s24d001代码，3个来自未评分工程预检版本。已明确标记 unresolved，没有推测重建旧代码；这些运行不能据此声称完全复现。Sanctuary正式复用链不受影响。

[release-verification.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/release-verification.json>)：c24f002冻结564项、c41f002冻结629项，全部当前哈希一致；readiness=PASS，四臂均NEW，HTTP attempts=0，无batch.started。[superseded_preparations.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/superseded_preparations.json>) 将早期z001/f001标为未执行的工程准备，保留原账本，不纳入正式结果。

[正式汇总](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/clean10-preparation-20261027-001/summary.json>)：planned_tasks=10、planned_trials=20、ready_tasks=5、completed_pairs=1；其余9题未开始。该入口同时保留 observed_records；不把工程fixture和未执行记录计作失败。

## 5. 每任务执行路径和下一批准确命令

共同路径：`lab.py`核验case/source/gate → 现有A2S生成入口 → `pilot.py freeze/prepare`从已有生成包冻结Skill、版本、任务与执行清单 → 通用Terminus-2/Harbor执行两臂 → 现有隔离观察/评分桥运行原Oracle → 每臂结果与账本 → `pilot.py analyze`生成Skill读取/上下文/失败报告 → `lab.py sgb cohort`结合`attribution.audit_pair`汇总。

三个已有生成任务复用上面的已固定gen ID；两个新领域任务共用json_task→fla.score；Pydantic两题共用一类待补的对象观察；Scrapy050沿用Scrapy观察家族；ops/shark只有语义准入后才填写JSON配置。不为每个任务开发Agent或预算系统。

以下付费命令仅为交付，**本轮未执行**。第一批建议先Scrapy024，再Scrapy041；各自仅一次固定配对：

```powershell
$lab = 'D:\AS\AutoSkill-main\degradation_failure_lab'
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase run -Task scrapy-task-024 -Experiment c24f002
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase analyze -Task scrapy-task-024 -Experiment c24f002 -Output results/sgb/analyses/c24f002
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase run -Task scrapy-task-041 -Experiment c41f002
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase analyze -Task scrapy-task-041 -Experiment c41f002 -Output results/sgb/analyses/c41f002
```

已有包装器负责凭据与显式付费环境开关，不能以凭据存在作为授权。若中止，只执行status/analyze检查；不要再次运行同一run命令，也不要重置账本或自动开新实验补跑。

第二批先取得两个新生成run的精确授权，并通过现有方式设置DEEPSEEK_API_KEY，再执行：

```powershell
python -B "$lab\scripts\lab.py" run --case case101_monitor --condition clean --repeat 1 --run-id m01g001
python -B "$lab\scripts\lab.py" run --case case102_capacity --condition clean --repeat 1 --run-id e06g001
```

当前这两条被BLOCKED gate阻断。生成完成后先核验/冻结；精确批准新下游的generator/experiment/task-config SHA/预算，再完成最终prepare。新JSON gate本身会被执行清单冻结，因此不要在最终prepare之后修改gate；若状态变化应使用新的准备身份，不覆盖或修补已有冻结清单。

```powershell
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase freeze -Task monitoring_gap_brief_classifier_001 -GeneratorRun m01g001 -Output results/sgb/skill-freezes/m01g001
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase freeze -Task capacity_aware_edge_admission_controller_006 -GeneratorRun e06g001 -Output results/sgb/skill-freezes/e06g001
# 精确下游授权完成后，以下prepare为零模型最终预检；通过后才能run。
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase prepare -Task monitoring_gap_brief_classifier_001 -GeneratorRun m01g001 -Experiment m01f001
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase prepare -Task capacity_aware_edge_admission_controller_006 -GeneratorRun e06g001 -Experiment e06f001
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase run -Task monitoring_gap_brief_classifier_001 -Experiment m01f001
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase run -Task capacity_aware_edge_admission_controller_006 -Experiment e06f001
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase analyze -Task monitoring_gap_brief_classifier_001 -Experiment m01f001 -Output results/sgb/analyses/m01f001
& "$lab\scripts\sgb\Invoke-Pilot.ps1" -Phase analyze -Task capacity_aware_edge_admission_controller_006 -Experiment e06f001 -Output results/sgb/analyses/e06f001
python -B "$lab\scripts\lab.py" sgb cohort --config configs/sgb/clean10.json --output results/sgb/analyses/clean10-after-next-batch-001
```

输出目录应是新路径；结果索引拒绝覆盖旧分析。其余5个NEEDS_WORK不提供虚假的可执行命令，完成表中最少适配/语义门槛后才绑定case/gen/experiment。

## 6. 新模型预算与所需授权

| 范围 | 调用/Token规划 | 授权要求 |
|---|---|---|
| 下一批Scrapy024＋041 | 2配对×2臂×6=**最多24次HTTP**；累计输入上限合计400k，输出上限合计49,152 | 精确批准c24f002/c41f002及其冻结配置/模型/预算；不含任何重跑 |
| monitoring＋capacity提取 | 2×150=**最多300次HTTP**；每run observed-total阈值450k，合计900k | case/clean/run/config SHA/HTTP/Token精确授权后才更新新gate |
| 上述两个新任务下游 | 2配对，最多24次HTTP；同一正式协议 | 提取与冻结后按精确gen/experiment/task-config SHA/12次每配对授权 |
| 从现有1配对走到10配对的条件规划 | 尚需9配对≤108次HTTP；若另7题均需新提取且沿用150/450k，则≤1,050次生成HTTP、3.15m observed-total阈值 | 仅是容量规划，5题尚未准入，不能整体授权执行 |

A2S observed-total是响应后观察的停止阈值，最后一次响应可越过该数，不能称作严格Token硬上限；HTTP上限按现有门禁执行。金额需要实际账户输入/输出/缓存单价；本地证据不足，不编造美元估价。预算触顶、未知计费或基础设施中止都不自动追加预算。

[authorization-proposal.json（仅提案，未授权）](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-cohort-20261027-001/authorization-proposal.json>) 保存下一批两个配对的profile/执行清单SHA和两个生成请求的config SHA。

## 7. 完成后统计与失败诊断口径

主结果按不同任务的整题二元成功计算：20次预定执行、实际执行数、完整可比配对数、每臂通过/任务失败/预算失败/基础设施不可评分数，以及两臂四格配对结果。基础设施缺失和未启动单列，报告完整配对与全部已观察记录，不能静默丢弃失败或把测试例数相加充当任务成功率。当前仅1组配对，不据此宣称稳定改善。

每题保存原文清单与hash、生成版本/请求日志、最终Skill包与hash、实际安装与索引、全文读取/成功请求内上下文证据、Agent动作/提交/评分哈希、原始JUnit、预算账本与failure_kind。实际读取不等于行为依赖。

提取诊断：原文知识是否存在→切分/筛选/提取遗漏→合并压缩或错误→最终包覆盖与引用失配；不手工修复Skill。执行诊断：加载/检索/未读或只读部分、读后规则应用错误、实现/格式/提交错误、预算耗尽、基础设施故障、Oracle契约不充分。归因需要具体规则和动作证据；只有分数差异时标为证据不足。

剩余工程优先级：先执行获批的两组Scrapy；再生成两个已准入JSON任务；同时只补一个Pydantic观察家族和Scrapy050有界观察。ops/shark若无法在不透露规则的情况下闭合契约，就替换候选，维持准入标准。
