# CleanSkill 离线下游失败归因

此分析入口依次审查配对资格、计算结果差分、连接规则与行为证据。CleanSkill 只表示从 clean 文档生成，不保证 Skill 内容正确。入口不导入实验 Agent、pilot 或模型客户端，不启动 Docker，也不重放 Oracle。

## 使用

在 `degradation_failure_lab` 目录执行：

```powershell
python -B scripts/sgb/attribution.py --spec configs/attribution/s24p002.json --output results/sgb/attributions/s24p002-attribution-v1
```

输出包含 `report.json` 与 `report.md`。省略 `--output` 只向 stdout 输出 JSON。输出必须是 `results/sgb/attributions` 内尚不存在的子目录；重复执行时使用新的版本目录。不会覆盖旧报告、实验结果、预算账本或生成产物。输入/证据不能越出实验室目录。JSON 无效、引用错误或声明的证据哈希不符会报错，不会生成看似可信的结论。

输入契约位于 `schemas/attribution.schema.json`；对应实现 `downstream_eval/sgb/attribution_contract.py` 使用现有 schema 校验器。十个明确指定 reference/target 的历史规格在 `configs/attribution`。不自动搜索可拼接的对照，也不自动挑选最好的重复。

零模型验证：

```powershell
python -B -m unittest discover -s tests -p test_attribution.py
python -B -m unittest discover -s tests -p test_skill_usage.py
```

`HistoricalAttribution` 需要仓库中的历史产物；`OfflineAttribution` 使用临时合成夹具。历史测试将网络连接和子进程启动设为失败。受限 Windows 环境可将 Python `tempfile.tempdir` 指向可写测试目录；这不改变被审计仓库。

## 复用与实现边界

| 层 | 本次增量 | 复用已有能力 |
|---|---|---|
| P0 | 显式配对规格、旧/新历史读取、身份核验、输出防覆盖 | `io.inside` 的路径别名、`artifacts.load_run`、冻结与执行清单 |
| P1 | 五类任务结果、逐断言差分、异常/缺失门槛 | 原始 Oracle JSON、JUnit、候选提交及原测试身份 |
| P2 | 原子规则阶段链接、实体关系、动作前的规则正文暴露 | 原子规则父检查项、现有生成中间产物、`audit_skill_usage` |
| P3 | 双轴标签、逐声明证据状态、替代解释、人工审核状态 | 既有人工错误追踪字段的语义，不复制历史审核结论 |
| P4 | clean/degraded 与干预版本的离线记录/校验 | 现有 condition、输入清单、生成配置、Skill 冻结身份 |

没有新增运行器、冻结系统、安装器、Oracle、窗口生成器或模型分类器。`inspect_run` 的结构通过仍不等于规则正确。报告中的语义标签来自规格里的审核声明；哈希、实体和时序校验不能认证文字含义。示例审核均为 `provisional`，等待研究者审核。

旧人工表 `results/analysis/five_case_clean_audit/error_traceability.csv` 可作为审核来源，字段对应如下：`source_rule_id → parent_rule_id`、`original_requirement → rule.claim`、`generated_statement/supporting_artifact → evidence.claim + locator`、`first_observed_stage → stages`、`verification_status/evidence_level → review_status/claim.status`、`downstream_risk → hypothesis`、`counting_note → alternatives/missing_evidence`。不得把旧批次人工结论直接继承为新生成批次的已证实事实。已有 `trace_filtering.py` 继续用于特定窗口筛选案例；本入口不重建它。

## 配对资格与差分

每个比较必须固定任务 checksum、任务/测试资产哈希、模型端点和参数、预算、Agent 实现及版本、运行时与镜像、附加指令、配置和 Oracle 身份。实验启动前冻结的配置、清单与包文件会重新核验；生成清单、原始源文件和实际输入也校验。历史执行代码使用当时保存的指纹，不要求今天的整个工作树回滚到历史版本。

配对状态：`eligible`（核验一致）、`ineligible`（存在已知冲突）、`unknown`（无已知冲突但证据缺失）。同样缺失的两项不是一致。历史相对/绝对路径通过现有 relocation 解析，原路径保留在 `evidence_files.aliases`；内容核验独立进行。只在合格且两边可评分时生成结果差分。

| reference → target | 任务级类别 |
|---|---|
| FAIL → PASS | `possible_help` |
| PASS → FAIL | `possible_harm` |
| PASS → PASS | `both_passed` |
| FAIL → FAIL | `both_failed` |
| 缺组、评分缺失/不一致、环境异常、身份不明 | `unresolved` |

整体 PASS 要求全部原始断言通过。逐断言记录独立输出；整体两组失败时仍可看到特定断言退步，但不会被升级为任务级额外失败。多个断言不自动成为多个独立因果案例。异常、缺失与预算停止分别保存于 `execution_state`、`batch_stop`、`integrity_issues`、`missing_evidence`，不猜测超时是否由 Skill 诱发。像 `f02u001` 这样没有完整绑定评分的 BudgetStop 只能 unresolved；正常预算内已评分的实现错误按其实际评分处理。需要证明阻碍性工作流程导致预算耗尽时，仍需审核动作/预算证据及干预。

主协议为自主读取：正文未读取不使配对本身失效，可衡量提供 Skill 的总体影响；但不能支持正文规则机制。索引、名称和描述也可能影响行为。要求读取的实验必须有相同协议的对照，单列为 `loading_protocol` 干预。

## 双轴分类与证据等级

功能表现轴沿用论文 [Agent Skills Can Be Harmful, §III–IV](https://arxiv.org/html/2608.11888v1) 的名称：

| 代码 | 名称 |
|---|---|
| APM | Applicability Mismatch |
| EM.BDR | Environment Mismatch / Broken Dependency or Runtime |
| EM.ESM | Environment Mismatch / Environment-State Mismatch |
| TIF.OWG | Task-Implementation Fault / Obstructive Workflow Guidance |
| TIF.IRF | Task-Implementation Fault / Incorrect Required-Element Fill |
| TIF.RRO | Task-Implementation Fault / Required-Element Omission |
| AM | Artifact Misplacement |

来源/传递轴：`source_missing_or_ambiguous`、`window_selection_loss`、`evidence_or_draft_loss`、`compile_or_register_change`、`skill_delivery_failure`、`agent_rule_misapplication`、`environment_tool_or_oracle`、`insufficient_evidence`。这些是审核标签，不是自动关键词诊断。相邻阶段定位需要源/窗口/support/draft/spec/注册/最终正文的实际证据；最早观察到损失不等于最终失败的唯一原因。

每条声明分别使用 `observed/inferred/hypothesis/intervention_supported/unknown`。已证实声明必须有可解析且哈希匹配的引用；直接声明 `observed` 的因果结论会被拒绝。推断需写替代解释，假设写缺失证据。`agent_rule_misapplication` 的非假设标签还要求最终规则被审核为保留，且规则正文在相关动作前进入成功模型请求；实现不会推断模型的心理过程。

## 案例

| 规格 | 历史 NoSkill → CleanSkill | 合格差分及边界 |
|---|---|---|
| s24p001 | 14/19 → 12/19 | both_failed；FTP PASS→FAIL；仅索引 |
| s24p002 | 13/19 → 19/19 | possible_help；FTP FAIL→PASS；相关正文在写入动作前进入成功请求 |
| s24p003 | 12/19 → 19/19 | possible_help；FTP FAIL→PASS；仅索引，不认定正文机制 |
| f02d001/002/003 | 各 1/9 → 1/9 | both_failed；无正文依赖证据 |
| f02u003 | 缺对照 → 1/9 | unknown/unresolved；要求读取的单组机制案例 |
| f02u001-incomplete | 缺对照/执行未完成 | unknown/unresolved；BudgetStop |
| cross-protocol | s24p002 NoSkill 与 s24u002 CleanSkill | ineligible，指令/实现等条件不同 |
| legacy-new | s24d001 NoSkill 与 s24p002 CleanSkill | ineligible，生成和执行条件不同 |

BRO：源/选中窗口/support 保留具体角色映射；角色参考 draft 将其泛化，spec、注册及最终角色正文未恢复，`first_observed_loss=draft`。这定位信息损失，不证明相对 NoSkill 的额外失败。`f02u003` 提交把常量写为 `coordinator`，原测试用 `BRO`，且存在多个其他错误。规格保留“补回 BRO 可能改善局部 recipient 判断”的 hypothesis 和 planned 干预，不承诺整任务通过。

Scrapy：最终 Skill 保留 FTP 默认 True、追加条件和 APPE 限制。当前原子映射以默认值断言为验收目标；APPE 不在该断言覆盖范围。`s24p002` 的动作前规则暴露增强机制证据，但模型已有知识和随机性仍是替代解释。完整正文进入请求仍不等于遵循，`behavioral_use` 始终 UNKNOWN。

## 证据格式与跨条件接口

`evidence` 每项记录路径、SHA-256、所属 run、stage、entity_id、locator、claim_status、claim、missing_reason。定位器支持文件、行号数组、JSON Pointer、JSONL 第 N 个非空事件、trajectory step_id。JSON 数组索引从 0 开始，其他行/事件从 1 开始。缺值使用 null 加原因，禁止虚构 hash。输入规格本体以 canonical JSON `spec_digest` 记录；被读取文件以字节哈希记录。

`coordinate_space` 必须区分 `original_source/generation_input/normalized_text/skill_body/artifact`。不跨版本复用行号。`rule_id` 是稳定的语义原子 ID，`parent_rule_id` 链接已有任务检查项，`generator_run_id` 标识生成版本；同一次生成派生的人工修复使用可选 `intervention_id` 区分规则版本。状态为 `preserved/altered/omitted/ambiguous/unknown`；可多对多关联断言，未覆盖时 `oracle_not_covered=true`。

正文暴露关联具体 Skill 行、JSONL 工具动作事件、成功请求序号。判定要求 paid 请求、HTTP 2xx、非 assistant 上下文中的规则片段、现有观察器确认的模型文件访问，且原始读取事件发生在请求之前、请求和响应时间均在动作之前。匹配时排除 Skill 索引块。控制探针不会算作模型读取。空规则正文（例如 BRO 已丢失）不能凭同一 Skill 的其他文字推断该规则暴露。

NoSkill 的 `document_condition=null`；其 generator_run_id 仅标识比较背景。Clean/Degraded 使用实际生成 condition.kind，保留 condition_id、operator、parameters、源哈希、输入哈希、配置、上游指纹和最终包版本。不同输入哈希、同原始源、同生成配置与代码才可比较；相同字节不能声称退化。单次生成不能排除生成随机性；生成 run 与下游 run 分别编号，本入口不把它们合并为独立重复样本。

干预记录包含版本、scope、父/补丁/子证据、预期规则、control/treatment 和 planned/completed。completed 必须对应当前合格 pair；父/子绑定实际输入、staged Skill、候选提交或读取协议配置；其他包文件保持一致。补丁必须是整文件证据，并等于 UTF-8 文本的 canonical unified diff（`difflib.unified_diff(..., fromfile='before', tofile='after')`）。多文件干预应拆成新分析版本；不会默认放宽控制变量。`loading_protocol` 只允许额外指令字段变化，Agent/工具/环境等仍需一致。未执行计划不能标为 intervention_supported；支持该等级还必须在其目标规则覆盖的断言上观测到差分。输出还保存声明所依据的 `intervention_scopes`；提交修复仅验证代码缺陷，不自动证明 Skill 对 Agent 的作用。源文档干预还必须固定原始源身份、生成配置和上游代码。

当前产物为离线历史分析；没有执行任何新退化生成、Skill 修复或模型干预。人工语义复核与后续受控实验仍需另行开展。
