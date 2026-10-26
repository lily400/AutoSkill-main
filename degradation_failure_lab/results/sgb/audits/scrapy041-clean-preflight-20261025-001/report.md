# Scrapy041 多源文档处理审查与 Clean 生成前检查

结论：**BLOCKED — 未取得本任务明确的模型预算授权，按用户第三节要求停在真实生成前。**

这不是生成失败或下游任务失败。本轮完成多源处理审查、四文档 case 配置、输入快照和零模型验证。真实生成、最终 Skill 质量评估、Skill 冻结、NoSkill/CleanSkill Agent 运行均为 **NOT_RUN**；模型调用、真实 Agent 运行和 Skill 生成为 **0**。未构造退化文档。

日期：2026-10-25。本地基线：6fac24ebd24954ae5c5f97393a64d343015aa0c0。开始时工作树干净；本轮变更未提交、未推送。此前 041 适配和网络隔离已在当前提交中。Anything2Skill 实际源码位于 D:/AS/AutoSkill-main/AutoSkill-main；实验目录位于 D:/AS/AutoSkill-main/degradation_failure_lab。

## 1. 方法选择：方案 A

选择：**一个 case、四份保持独立身份的源文档；逐文档构造窗口、提取和编译，再依次向同一个本次运行专用 SkillBank 注册协调。**

需要修正 A 的措辞：当前代码不是将所有文档的原始候选混在一起全局编译。文档级编译分组包含 doc_id，跨文档协调主要发生在注册层。一次传入四份文件所在目录仍是 A；把四份原文拼接成一篇新文档才是 B。

### 原始方法证据

核对了 [Anything2Skill 原论文 v3，第 3.2–3.3 节](https://arxiv.org/html/2606.09316v3#S3)。论文描述逐记录证据窗口、Plan/Expand、文档级编译，以及持久 SkillBank 的检索协调、版本更新和可见技能树。因此 A 符合方法定位。论文不证明本次本地运行成功，也不保证协调后规则正确。无源文档暴露的 Skill-only 下游对照是本研究的评测配置。

### 当前实际调用链

以下源码均在本轮读取，字节哈希见 code-freeze.json。未根据 README 推断运行行为。

| 阶段 | 实际位置 | 代码核查结果 |
|---|---|---|
| 来源与条件 | lab/src/degradation_lab/catalog.py:53,79 | 加载 case/rules/conditions；Clean 输入须引用原文且哈希一致；每个 source 必须有对应输入 |
| 配置解析 | lab/src/degradation_lab/runner.py:59 | 合并共享配置及 case overrides；max_documents 等于输入数，本次为 4 |
| 新运行准备 | lab/src/degradation_lab/runner.py:81 | 排他创建新 run，复制输入，建立空 SkillBank，记录配置及代码 |
| 生成入口 | lab/src/degradation_lab/adapter.py:12,29,49,162 | 一次建立 SDK；非恢复运行拒绝非空库；仅将 run/inputs 目录传给 extract_from_doc |
| 文件导入 | AutoSkill4Doc/document/file_loader.py:84,114,133 | 排序遍历目录，每个文件形成独立单元并保留 source_file；不拼接四份全文 |
| 提取 | AutoSkill4Doc/pipeline.py:1004 | 按文档定位自己的窗口；当前 LLM outline 未执行，不能虚构窗口数 |
| 编译 | AutoSkill4Doc/pipeline.py:1362,1411；stages/compiler.py:185 | 当前文档的草稿和支持传给编译器；分组键含 doc_id |
| 注册 | AutoSkill4Doc/pipeline.py:1495,1551 | 每份文档的编译结果依次注册到同一个 pipeline registry |
| 协调 | AutoSkill4Doc/store/versioning.py:2390,2403,2436,2449,2484 | 读取已有技能、检索邻居、判断 lifecycle；merge 分支实际调用合并，并非只登记名称 |
| 去重及持久化 | AutoSkill4Doc/store/versioning.py:2126,2921,2944 | 同层去重；按 ID upsert；保存 lifecycle、change、version 和 provenance |
| Store 与可见树 | AutoSkill4Doc/store/versioning.py:967,995,999,3104 | 更新涉及 ID，再读取当前库集合并投影可见树；不为每份文档重建库 |
| 聚合结果 | AutoSkill4Doc/store/intermediate.py:1006,1177 | 按文档保存结果，再按 ID 聚合；保留来源、版本与错误 |

注册实现支持 create、strengthen、revise、merge、split、unchanged、discard 等分支。**代码支持不等于 041 实际发生**；本轮跨文档决策数量是 UNKNOWN，而不是“已合并”或“0 次合并”。

### A/B/C 比较

| 方案 | 来源、预算与协调 | 额外实现 | 决策 |
|---|---|---|---|
| A：分文档处理，共享本次运行的库 | 来源与窗口证据保留；逐窗口请求；文档间可互补、更新及去重；顺序可能影响协调 | 已支持，仅补 case/映射 | **采用** |
| B：四份原文拼接 | 改变文档边界、编译分组和来源定位；长文本预算更难控制；拼接后仍可能切窗口，不等于一个模型请求 | 需拼接材料及额外来源映射 | 不采用 |
| C：四个隔离库独立生成后组合 | 单文档问题容易定位；没有当前跨文档协调；直接并集可产生重复/冲突；追加合并又成为另一处理因素 | 独立生成可复用，组合协议须另行定义 | 留作必要诊断，不作本轮主实验 |

研究设计建议：保留现有完整方法，固定输入集合、顺序、领域、算法和预算规则；Clean/退化条件保持协调机制一致。不同条件和独立生成重复使用各自的新库，不能将 Clean 库继续用于退化条件。四份文档属于同一任务，不是四个独立下游任务。

## 2. 041 来源身份

任务 scrapy-task-041；任务键 t-8d3bed6236cf；文档包 b-083578378ffb0792；SkillGenBench 快照 5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d。官方 Oracle SHA-256 为 6b3c519e661c41f3650bb8fa33b64edbd709592a42b1f75b577f7ac4fc64c44b。

| 固定顺序 | 文件 | 字节数 | 路径（相对 lab） |
|---|---|---:|---|
| input001 | offsite.md | 3,912 | data/raw_sources/sgb/5a8bd61d/dad43df16d07e2c3/offsite.md |
| input002 | downloader-middleware.md | 42,822 | data/raw_sources/sgb/5a8bd61d/491f737b9d4743ec/downloader-middleware.md |
| input003 | request-response.md | 66,045 | data/raw_sources/sgb/5a8bd61d/9f6d99ec9d95647c/request-response.md |
| input004 | spider-middleware.md | 24,070 | data/raw_sources/sgb/5a8bd61d/3772c49ba00a9fe4/spider-middleware.md |

总计 136,849 字节、136,431 字符。4 份原文、4 个来源 manifest 及 11 个官方资产均核对通过，完整哈希见 source-map.json。没有重新抓取替换原文。

目标规则在 offsite.md:60 和 downloader-middleware.md:651–654 有直接支持，request-response.md:703 另有名称/链接。后续局部退化要记录重复支持，不能因其他文档补偿而把无下降解释为文档质量无影响。本轮没有实施退化。

## 3. 最小配置调整

新增：
- cases/sgb/case041_scrapy/case.json
- cases/sgb/case041_scrapy/conditions.json
- cases/sgb/case041_scrapy/inputs/clean.json
- cases/sgb/case041_scrapy/rules.json
- data/manifests/sgb/gates/t-8d3bed6236cf.json：**BLOCKED**
- configs/experiments/sgb/scrapy041_clean.json：**DRAFT_AWAITING_BUDGET_AUTHORIZATION**

修改：
- data/manifests/sgb/tasks.jsonl：仅 041 行，绑定 generation_case_id，登记 preflight 和预算/未生成状态；其他 186 行逐字节不变。
- configs/datasets/sgb.json：同步注册表哈希。

本目录是唯一新增审计目录，保存输入镜像、哈希、验收脚本和报告。未修改 Anything2Skill、公共执行器、041 Oracle/运行时、网络策略或 024 历史产物。

domain_type 固定为 scrapy，复用 configs/generation/deepseek_flash.json。当前无 scrapy.yaml，实际沿用默认分类结构并设置领域身份；没有增加领域关键词或 taxonomy。沿用 recommended、LLM outline、每单元最多 4 候选、chunk 6000/overlap 300、section 10000、retrieval threshold 0.3 等配置。max_documents=4 是输入映射，不是算法修改。完整生效配置见 preflight.json。

rules.json 是分析清单，不进入生成输入目录。任务指令、task.json、Oracle、隐藏测试及参考答案也不在生成输入中。

## 4. 零模型验证及边界

实测通过：
- 官方 load_file_units 读出 4 个非空独立单元，文本和 SHA 与原文一致。
- 读取审计证明，该加载调用期间 lab 内读取路径仅为 input-snapshot 下四份源文档。
- CaseManager、四输入映射、领域参数和 max_documents 检查通过。
- 实际调用 ExperimentRunner.run，在模型导入/请求前被 BLOCKED gate 阻断，未创建真实生成运行。
- 注册表完整性检查覆盖 187 任务并通过；Windows plan 路径检查通过。
- **54 项相关离线测试通过，0 失败、0 错误、0 跳过。**

验收容器为已有固定 controller 镜像，network=none、无凭据、无 Docker socket、代码只读，本审计目录可写；Python hook 阻断 socket/subprocess，import guard 禁止模型 SDK 和 Agent/Trial 模块。

**范围限制**：以上不是完整提取或真实 Agent 验收。可信生成包装进程的操作系统账户并不因此失去读取仓库其他文件的权限；此处证明输入选择与本次加载访问，不能冒称生成进程的 OS 文件系统隔离。现有生成模型未配置任意文件读取工具；真实生成仍需复核保存的逐请求输入。

### 状态、覆盖与产物风险

1. 未预创建或复用真实 SkillBank。未来新运行排他建目录、验证空库；各文档之间保留同一个库。
2. 注册会合并、更新或归档技能，这是生命周期变化，不能把历史 upsert 数直接当最终活动技能数。
3. 生成完成后须对齐最终活动 registry、Users 导出、版本及哈希，检查 discard/merge/deprecate 的去向。不能未经核对便把 024 的“全部历史注册 ID 等于导出 ID”要求用于所有多文档结果。
4. 预算耗尽的部分产物不得冒充完整四文档 CleanSkill，不得自动换 ID 重开预算。
5. 输入路径 input001–004 固定排序；不能在条件间改变文档处理顺序。
6. LLM outline 未执行，窗口、候选、编译和注册数量不使用模拟值替代。

此前公共网络修复的 10 个代码文件及 041 适配/测试的 21 个代码资产哈希未变。未启动新任务 Agent，因此没有新的 Agent 网络运行结论，不替代此前验收。未来正式准备须继续通过公共网络检查。

## 5. 预算审查与具体申请方案

凭据检查只返回布尔值：DeepSeek 当前进程凭据存在；Zhizengzeng 现有 DPAPI CheckOnly 成功。未输出/写入明文密钥，检查未发模型请求。**凭据存在不是预算授权。**

现有账本：
- 024：总额度 36、记录 27 请求，scope=scrapy-task-024/s24r005/initial-calibration；剩余额度不能转给 041。
- 041 零模型验收：总额度 0、请求 0，scope 为 zero-model-fixture；不能复用为付费账本。
- 未找到 041 已授权的生成或真实 Agent 预算。

待授权方案，当前未生效：

| 阶段 | 申请额度及约束 |
|---|---|
| 上游 | 1 次四文档生成；DeepSeek / deepseek-flash；最多 150 次实际 HTTP 尝试；沿用输出参数 16,384 及原阶段配置 |
| 上游 Token 停止 | 已观测累计 Token 达 450,000 后不开始下一请求；**不是硬计费 Token 上限**，末次响应可能越界，usage 缺失可能低估 |
| 下游 | 1 次 NoSkill + 1 次 CleanSkill；沿用 openai/gpt-5.4-mini-2026-03-17 及既有提供商配置；每组最多 6 请求，总计 12 |
| 下游其他限制 | 每请求输入 20,000、每 trial 输入总计 100,000、每请求输出 2,048；Agent 300 秒、请求 45 秒；num_retries=0；两组相同 |
| 停止条件 | 不自动追加预算或扩大重复；生成不完整、包未冻结或环境异常时不启动下游 |

150 次并不保证处理完成：真实窗口和候选数未知，不能虚构完整调用量或费用。若需要严格金额/Token 上限，须先确认可强制执行的限额。实际服务商计费费率未核定。

generator_run_id=null；s41r001 和 s41d001 只是计划 ID，真实目录未创建。预算批准后仍须进行正式准备，不能将本审计 PASS 当作付费 readiness。041 已有 paid_batch，但真实生成导出、双组 staging、预算账本与配置冻结仍需在获得真实 Skill 后完成最小接线；本轮按预算门禁停止，未伪造产物。

## 6. 质量、下游结果与研究判断

| 文档 | 文件加载 | 真实窗口/候选/编译数 | 注册/协调 |
|---|---|---|---|
| offsite.md | PASS | NOT_RUN / UNKNOWN | NOT_RUN |
| downloader-middleware.md | PASS | NOT_RUN / UNKNOWN | NOT_RUN |
| request-response.md | PASS | NOT_RUN / UNKNOWN | NOT_RUN |
| spider-middleware.md | PASS | NOT_RUN / UNKNOWN | NOT_RUN |

最终 Skill 清单、质量缺陷、支持图、包完整性和哈希冻结均为 NOT_AVAILABLE。没有拿夹具或旧 Skill 冒充生成结果。

| 条件 | 提供/读取 Skill | Oracle | 观察结论 |
|---|---|---|---|
| NoSkill | NOT_RUN | NOT_RUN | 无真实结果 |
| CleanSkill | NOT_RUN | NOT_RUN | 无真实结果 |

因此不能推断组间差异、Skill 缺陷造成失败、Agent 依据 Skill 行动，或统计/因果效果。

- A 实验有效性/准入：预算未明确授权；真实生成输入和最终活动包仍待记录验证。此前零模型验收不能扩展成真实试点结论。
- B 流程复用：四文档 case 和来源绑定已补齐；正式准备仍待产物及预算，不能仅凭 adapter.json 的 READY 字段启动。
- C Skill 形式质量：本次未生成 Skill，没有可报告的新缺陷，也没有修改算法的证据。

当前不扩大任务或开始退化。先完成 041 Clean 生成和最小双组试点，再判断需要更多 Clean 验证还是退化研究。方法与静态代码支持 A，不是生成成功的证据。

## 7. 证据与下一步

- source-map.json、input-snapshot/：来源、完整哈希、固定顺序与原文镜像。
- code-freeze.json：生成核心、提示词、包装和配置哈希。
- validate.py、preflight.json、windows-plan.json：实际零模型验证。
- unit-tests.log、unit-test-summary.json：54 项测试。
- budget-audit.json、budget-proposal.json：账本 scope 与待授权方案。
- registry-change.json：041 变更及其余 186 行不变。
- history-before.json、preservation.json：**14,260 个受保护文件无改动/缺失**，网络及 041 代码未变。
- git diff --check：通过。

下一步唯一优先行动：**明确批准或调整上述 041 专用模型预算。** 此前保持 gate=BLOCKED，不调用模型、不生成 Skill、不启动 Agent。这个预算要求直接来自用户本轮第三节“如果没有明确授权的可用模型预算，停止在生成前并报告需要的预算”，不是额外引入的确认流程。
