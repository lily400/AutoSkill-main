# 研究数据集选型与下游任务设计审计

审计日期：2026-10-20。项目：`D:\AS\AutoSkill-main`；研究目录：`D:\AS\AutoSkill-main\degradation_failure_lab`。

本报告只记录审计、公开资料检索和实验设计。本轮没有修改正式实验实现，没有调用真实模型，没有新增付费请求，也没有生成正式退化数据。文中的实验矩阵、Oracle 改动和接入工作均为待审阅方案。

## 1. 推荐结论与证据边界

**推荐采用分层组合：ConditionalQA 作为自然来源文档与规则传播的主数据层；Leezekun/SOPBench 的固定政策子集作为可执行机制层；现有 Git restore 作为工程校准；AppWorld 作为执行层的后备。** 这是有条件的选型，不是宣布这些数据已经全部通过正式实验准入。当前没有一个已审计候选能直接、完整地满足自然文档、共享规则任务、冻结 Skill、自主读取、独立状态 Oracle 和因果归因的全部要求。

ConditionalQA 已有独立来源文档、答案和证据，能避免从下游任务答案反造 Skill；但它主要检验回答正确性，不能替代业务动作实验。SOPBench 有实际状态和操作约束，但来源 SOP 与环境程序同源，且原生评测需要加固；它不能独自支撑“真实自然文档退化”的外推。两层分别报告，不合并成一个总成功率。选择这个组合的依据是两层分别补足证据链，而非任务数或接入方便程度。

**最急需解决的问题不是扩展任务数量，而是确认规则在什么位置被暴露、是否改变行为，以及 Oracle 是否确实验证用户目标。** 最新 Git Gold 实验任务成功，但未观察到 Skill 正文读取；A0、A1 没有运行。这既不能说明生成 Skill 有效，也不能说明生成 Skill 无效。

证据等级在全文统一使用：

| 标记 | 含义 | 可以支持的结论 |
|---|---|---|
| S | 本轮直接检查本地文件、源码、公开仓库材料，或重新统计/核对哈希 | 文件结构、实现行为的静态依据；不等于真实运行通过 |
| H | 已有报告、原始轨迹或此前离线探针记录，本轮审阅 | 对相应固定版本和运行的历史结论；不冒充本轮重跑 |
| P | 论文或作者页面声明 | 数据集设计和论文实验主张；不自动等于当前发布内容 |
| I | 本报告提出的适配、干预、任务或验收方案 | 待实施设计 |
| U | 未获取、未核实或尚未执行 | 不计入已具备能力 |

“存在代码”“历史离线测试通过”“真实模型调用成功”“有因果证据”是四个不同状态。下文不将它们互相替代。

## 2. 当前工程的真实状态

### 2.1 版本、生成流程与中间表示

本轮前段审计记录的当前根仓库 HEAD 为 `a379e54e1233bd3f3011869f70eaf7fed8762982`，提交时间 2026-10-19；工作树初始无改动。实际 Anything2Skill 上游位于根目录内的 `AutoSkill-main` 子目录。将当前上游 164 个文件与 Git clean 生成记录的 `upstream_before.json` 对照，164 个均匹配。这是当前文件核对结果，不只是引用历史 before/after 相等。[生成适配器](D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/adapter.py)

适配器调用原版 `AutoSkill4Doc.extract_from_doc` 和文件加载流程，按运行隔离 store，并保存输入与上游快照。模型提供商接入和 HTTP 观察位于适配层。已运行配置包含 recommended pipeline、LLM outline、每 unit 最多 4 个候选、`max_units=0`、6000 字符分块、300 字符重叠、10000 字符最大 section。**这些是字符配置，不是 token 上限，也不证明整篇源文档的目标规则实际进入了某次模型请求。** 后续必须检查加载结果、窗口覆盖及实际请求。

Git clean 生成的一次实际中间运行有：

| 阶段 | 已观察到的结构 | 尚缺什么 |
|---|---|---|
| ingest | 1 document、10 windows；document 含 raw_text、sections、checksum/content_hash；window 含 doc_id、段落范围、text、span、strategy | 人工确认的原子规则及重复证据集合 |
| extract | 17 supports、17 drafts；support 含 excerpt、relation、confidence | support 不是独立真值；必须检验片段是否真的支持完整条件 |
| compile | 17 specs；含 skill_body、适用性、禁忌、workflow、constraints、cautions、output | 规则、例外、数值与作用域的语义对应 |
| register | 14 个注册结果及关联支持、生命周期、版本与 provenance | 注册后的规则合并、遗漏及任务依赖映射 |

因此无需为了评价 IR 修改核心生成算法。应新增外部审计映射，将 `source span → rule → window → support/draft → spec → registered skill` 串联起来。尚不存在可以直接当作 gold 的完整规则—任务图。

### 2.2 47 份 canonical Skill：来源与完整性

以既有 clean 审计清单中的成功运行和 canonical 路径为准，本轮重新计算 47 份 Skill 的 SHA-256，**47/47 与清单一致**。完整文件路径、skill ID、预期哈希、当前哈希见[本轮逐文件核验](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-20/canonical_skill_hash_audit.json)；原清单见[skill_inventory.csv](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/five_case_clean_audit/skill_inventory.csv)。

| 来源 | canonical clean run | Skill 数 | 历史请求尝试/成功 | 历史 token 合计 |
|---|---|---:|---:|---:|
| qsv select | `raecd75e08b34` | 4 | 18 / 18 | 57,472 |
| qsv sort | `rd9ced750fa54` | 3 | 13 / 10 | 29,885 |
| docker cp | `rab9a070dfa59` | 2 | 9 / 8 | 28,979 |
| git restore | `r18307cee4f4c` | 14 | 67 / 67 | 197,674 |
| ripgrep guide | `r64cee24fae18` | 24 | 96 / 96 | 324,936 |
| 合计 | 5 次成功 clean 生成 | **47** | **203 / 199** | **638,946** |

请求数和 token 为已有生成记录 H，哈希为本轮 S。物理目录中的 104 个 `SKILL.md` 包含投影/重复，不能计为 104 个独立生成样本。clean 审计中的 156 个规则审阅单元，历史分类为 correct 53、partial 29、mixed 14、omitted 59、uncertain 1；这些单元不是已经证明穷尽、独立、原子化且双人确认的规则全集，不能直接作为论文错误率分母。clean 本身的缺陷也不是退化造成的增量效应。

历史审计还记录了注册 decision 解析回退与最终 body/spec 对应情况。这可帮助定位流程，但“有输出、注册成功、body 与 spec 相同”不代表语义正确。[既有 clean 分析目录](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/five_case_clean_audit)

### 2.3 P1-C 最新真实执行：成功的是任务，不是已证明的 Skill 传播

应按运行链审阅，不能引用较旧 README 的 401 状态覆盖较新的结果：

| 运行 | 实际状态 | 正确解读 |
|---|---|---|
| `p1-c-20261019-001` | 较早报告指出持久预算阻断 | 已被后续实现和恢复过程推进，不能当作最新唯一状态 |
| `p1-c-smoke-20261019-001` | Gold 遇到 `No module named downstream_eval`，0 HTTP；A0/A1 未运行 | 导入故障，不是模型任务失败 |
| `p1-c-recovery-20261019-001` | Gold 2 次 HTTP 200；9/9 断言通过；A0/A1 `NOT_RUN` | 真实执行和验证链可运行，但触发 Skill 使用停止条件 |

最新原始证据：[恢复报告](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/report.md)、[预算账本](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/http-budget-ledger.json)、[实验结果](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/experiment-result.json)。

Gold 的真实动作先查看状态，再执行 `git restore --source=<commit-A> --staged --worktree -- target.txt`，再查看状态；第二次模型响应没有命令。输入 2,227、输出 528、缓存 0，合计 2,755 token。当前恢复 lineage 中 smoke 为 0 次、recovery 为 2 次 HTTP，不能据此概括所有历史连通性尝试。真实计费金额未核实，不能从参考价格推算成实付费用。

观察器报告 installed=1、discovered=1，首个请求含 Skill 索引信息；正文未预先内联。inotify 已建立 watch，但付费 trial 的 kernel read log 为空；动作轨迹没有正文读取，`model_read_ids=[]`、`full_body_visible_ids=[]`。因此应记录为“索引信息可见、没有正文读取证据”，不能把正确命令归因于正文。索引名称/描述本身提示了指定源和两个恢复位置，预训练知识与 metadata 提示都可能解释成功。[使用观察汇总](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/paid_trials/p1-c-recovery-20261019-001-Gold/p1-observer/p1-summary.json)

账本中 Gold `STOPPED`，A0/A1 `NEW`，停止原因 `TRIAL_STOP_CONDITION`。这是使用机制的诊断停止，不是 Gold 的 API、容器或任务 Oracle 失败；A0/A1 也不能记作 0% 成功。报告中的执行快照 HEAD `c8865067…` 是历史运行版本，与当前 HEAD 不能混为一谈。

运行环境记录为 Harbor 0.24.0，commit `2de4605b9404eada7d341388291e6e469c90330b`，Linux Docker、官方 Terminus-2 加兼容/观察层；模型为历史记录中的 `openai/gpt-5.4-mini-2026-03-17`。agent image 为 `sha256:148e27160303bbc5566edc0714a8476b4c6c2ca4925871d8e6fcce9df89a24e0`，verifier image 为 `sha256:4bfeebc3de41ad79e74908c5da730f33ac23e0238508c24e5cff2f80082accfe`。后续复现实验应以 manifest 的完整 digest 为准，不能只写“用了 Docker”。

### 2.4 已具备与仍需补齐

| 能力 | 当前证据 | 审计判断 |
|---|---|---|
| 持久请求预算与失败计费语义 | S 源码；H 11/11 fake transport 测试 | SQLite 事务预留、未知失败消耗预算、阻止重复/并发启动；本轮未重跑这些测试 |
| Linux 下游链路、独立 verifier | H 离线验证与 Gold 真实轨迹 | 既有 12/12 离线检查、6 种 native verifier 正反例为历史结果 |
| Skill 安装、索引和文件观察 | S 代码；H 真实 Gold | 可区分部分阶段；尚不能完整确认目标规则片段在下一模型请求中可见 |
| 自主读取与采用生成 Skill | U | 不能从 Gold 成功推出 A1 有效 |
| DirectDoc | U／I | 当前 A0/A1/Gold 结构没有已验证的对应源文档执行臂 |
| 源文档规则 gold 与共享依赖图 | 部分历史审阅；完整图 U | 需要外部标注，不改核心 Anything2Skill |
| 多数据集 Oracle | Git 有真实验证；其他 I | 九项 Git 断言不能通用复制 |
| 正式成组退化实验 | U | 当前证据不足以回答退化是否经 Skill 放大风险 |

预算实现见[request_budget.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py)，观察实现见[p1_observer.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py)。现有每臂 6 请求、全局 18 请求等边界是特定 pilot 配置；后续必须新建研究 scope，不能解锁或重用已经停止/消耗的账本。

## 3. 从研究问题推导准入条件

研究对象是 `源文档 → 证据/规则 → 退化 → 原版 Anything2Skill → 冻结 Skill → 实际暴露与行为 → 独立 Oracle → 结果`，并与对应版本的 DirectDoc 比较。

### 3.1 硬性门槛

| 门槛 | 入选需要的证据 | 不通过时如何处理 |
|---|---|---|
| G1 来源可固定 | 有可获取源文件、版本、哈希、来源/许可；自然文档与程序生成 SOP 单独标识 | 无文档或仅有任务答案：排除主研究；程序生成 SOP 只能承担机制层 |
| G2 规则与证据可定位 | 原子规则的条件、动作/结论、参数、例外、作用域；支持及重复片段 | 只有主题相似：不计依赖关系 |
| G3 可形成共享规则簇 | 至少两项语义上依赖同一规则的任务与一项不依赖的负对照；给出反事实证明 | 不凑数量；候选保留但该簇不准入 |
| G4 干预可隔离 | 只改源文档；任务、接口、环境、真实标准答案固定；相关/无关/表面变化可分离 | 同时改接口或 ground truth：退出主因果比较 |
| G5 原版生成可审计 | 固定加载转换；目标片段实际进入 IR/请求；输出整套 Skill 可冻结 | 仅“文件能打开”不够；不能暗改生成核心来救某候选 |
| G6 两臂可公平执行 | DirectDoc 与 Skill 臂用同一 executor/model/tools/task/budget；原文与答案隔离 | 默认 prompt 注入完整 clean 规则、测试可见或 Skill 缺失静默回退：不准入 |
| G7 Oracle 独立且目标充分 | 正确答案/状态与禁止副作用可从可信输入计算；正反例、空轨迹、边界验证 | 只判调用形式、substring 或复演“自己做过的动作”：须加固 |
| G8 暴露与行为可观察 | 发现、文件访问、规则可见、动作与最终状态可对齐；观察器已校准 | 不可观测时只能报告总效果，不能声称具体传播机制 |
| G9 可复现和可使用 | 数据使用条件明确，环境/版本锁定，预算与失败策略预注册 | 许可或关键环境未确认：不执行正式实验 |

G3 是共享规则设计的门槛，不要求原数据自带现成的“三任务套装”。新增任务可以使用，但必须标记为研究者构造并验证真实依赖，不能靠要求某条命令或强制读某文件制造依赖。G7 对 QA 是独立答案/条件判定，对执行任务还必须含状态和事件；通过 QA 门槛不等于通过执行层门槛。

**语义依赖不等于知识来源依赖。** 改变规则可改变正确答案，证明任务在语义上依赖它；模型也可能从预训练、任务措辞、索引或代码知道规则。后者需要 A0、metadata 观察和局部修补来辨别，不能靠研究者断言“必须读文档”。自主不读取是合法实验结果，不应事后删除这些 trial。

### 3.2 加分项与排序原则

通过相应门槛后，优先考虑：独立自然来源、已标注证据、多条件/例外丰富、同规则多情境、确定性状态 Oracle、离线运行、跨来源规模、接入成本。本文不给伪精确加权总分：当前关键缺口是门槛型缺口，任务数再大也不能抵消规则不可追踪或 Oracle 不可信。

## 4. 检索策略、材料与统一比较

### 4.1 检索与证据链

按三条路线检索：文档/条件推理与证据标注，SOP/API/程序文档驱动的执行任务，Skill 生成/加载及鲁棒性。检索词组合包含 document-grounded agent、conditional rules、SOP benchmark、tool documentation robustness、skill generation benchmark、skill harmful、documentation code generation；逐个核对官方论文、官方仓库/数据卡、实际样例、评测代码和许可。

本轮使用 `nature-academic-search` 的多来源核验工作流；主要材料来自 arXiv/ACL Anthology、官方 GitHub、官方数据页/Hugging Face。结合 10 月 15—18 日的本地候选审计与公开快照，本轮重新检查关键 CQA/SOP 数据、Skill 清单、P1 轨迹，并补查 RoTBench、Agent Skills Can Be Harmful、OPERATE 等。并非每个候选都重新下载了完整数据；以下逐项标记深度。原始 GitHub 下载失败不能被当作内容不存在，RoTBench 的部分数据文件下载未完成，相关数量保留为 P。

历史材料：[开放候选目录](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/open_discovery_catalog.md)、[规则/条件数据审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/cl_rules_notes.md)、[政策执行审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/policy_workflow_notes.md)、[API 执行审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/api_execution_notes.md)、[既有开放选型报告](D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/DATASET_AND_TASK_OPEN_SELECTION_2026-10-18.md)。

### 4.2 候选来源、真实组成与可复用内容

| ID / 候选 | 原始论文与官方材料 | 实际组成、版本和核验深度 | 可复用与必须适配 |
|---|---|---|---|
| C1 ConditionalQA | [ACL 2022](https://aclanthology.org/2022.acl-long.253/)；[官方页](https://haitian-sun.github.io/conditionalqa/)；[仓库固定版本](https://github.com/haitian-sun/ConditionalQA/tree/77bd295952daf415548b3244db10880d3d55cfe0) | S：v1_0 的 652 文档；train 2338、dev 285、无答案 test 804；文档 HTML blocks 与任务 answers/conditions/evidences 分离 | 复用源文档和带标签任务；新增原子规则图、严格覆盖计分及终端答案提交。官方数据 CC BY-SA 4.0；代码的 `LISCENSE` 为 BSD-2，不可混用 |
| C2 SOPBench（Leezekun） | [论文 2503.08669](https://arxiv.org/abs/2503.08669)；[固定仓库](https://github.com/Leezekun/SOPBench/tree/8790ed7406acbd22270f90bd1c4038de3fc5db8f) | S：7 域 830 任务：bank134、dmv97、healthcare124、hotel195、library66、market172、university42；task 含初始数据库、约束、参数、动作图；SOP 从环境约束生成 | 复用任务、状态、工具和 SOP；需政策等价筛选、终端 API bridge、业务目标 Oracle。代码 MIT、数据 CC BY 4.0，仍应随快照保存许可证 |
| C3 AppWorld | [论文 2407.18901](https://arxiv.org/abs/2407.18901)；[固定仓库](https://github.com/StonyBrookNLP/appworld/tree/42b5bcf3cd334fee33f0c37c02070a9f5807add5)；[公开 bundle](https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.2.0.bundle) | H：公开 0.2.0 bundle 实际 732 任务/244 场景，train90、dev57、normal168、challenge417；论文 750 不是此快照计数；11 标准 API-doc JSON 包括 supervisor/api_docs | 复用数据库、API 和任务测试；要证明分页等共享规则实际必要，隔离 DB/测试。代码 Apache-2.0；受保护数据及派生物再分发有专门条件，不能一概当作 Apache 数据 |
| C4 SkillGenBench | [论文 2605.18693](https://arxiv.org/abs/2605.18693)；[固定仓库](https://github.com/QuantaAlpha/SkillGenBench/tree/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d)；[官方发布数据](https://huggingface.co/datasets/anonymous-skillgenbench/SkillGenBench) | S/H：目录实际 187 instruction：123 repo、28 code/doc、36 domain；后两类 64 任务、45 来源组、73 独立文本哈希；308 是测试用例不是任务 | 可复用源资料与部分 task/test；共享规则 2+1 尚未完成，需修复生成/评测路径契约、去掉泄漏和静默回退。各来源的上游许可需逐项保留 |
| C5 RoTBench | [原论文 2401.08326](https://arxiv.org/abs/2401.08326)；[EMNLP 2024](https://aclanthology.org/2024.emnlp-main.19/)；[官方仓库](https://github.com/Junjie-Ye/RoTBench/tree/637e43ae9a978036774c92bb2ab11a83609e304b) | P：7 场景、105 clean queries、568 tools；S：First_Turn/Third_Turn 各 5 个 JSON 路径、TS/PI/CF evaluator；数据下载不全，未独立复数 | 可借鉴噪声类型与调用诊断；名称/参数接口本身随扰动变化，不满足本研究固定工具接口的主比较 |
| C6 Terminal-Bench / 2.0 | [2.0 论文](https://arxiv.org/abs/2601.11868)；[官方仓库](https://github.com/harbor-framework/terminal-bench) | P：2.0 为 89 个任务；任务指令、容器、验证和参考解。H：已有审计使用 `2e29ca91…` 的另一发布阶段快照，不能将该 main 快照叫作 2.0 | 可复用执行协议、容器/任务资源；需要重新锁定 2.0 正式 release 并筛选文档规则簇。heat-pump 案例的 20 claims 是一个任务内部对象，不是 20 个共享规则任务 |
| C7 Agent Skills Can Be Harmful | [原论文](https://arxiv.org/abs/2608.11888) | P：从 SkillsBench/SWE-SkillsBench 汇集并筛选 307 harmful cases，125 功能、182 效率；84/490 为文中起始任务池，20664 是潜在比较数量，不是独立任务数。已查方法设置 | 可复用配对失效分类、成本与轨迹分析思路；未定位到可核实的独立 SkillTriage 完整数据/仓库；缺来源文档退化链，不能当发生率无偏样本 |
| C8 Anything2Skill 本地资源 | [本地上游](D:/AS/AutoSkill-main/AutoSkill-main)；[clean 审计](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/five_case_clean_audit) | S/H：本地五来源、47 canonical Skill；不是具有成套独立任务/Oracle 的统一公开 benchmark | 复用原版编译器、IR、生成记录和已有 Skill。当前没有核实到其自带可直接满足 G1—G9 的通用下游任务集；不能从生成 demo 推断有评测答案 |
| C9 Git / qsv / ripgrep | [Git 固定源](https://github.com/git/git/blob/a52a24e03c8c711f1d5e252fba78f9276908129b/Documentation/git-restore.txt)；[qsv 固定仓库](https://github.com/jqnatividad/qsv/tree/257ae7b38738688138dc430c2ccb4eef8766f3fc)；[ripgrep 官方源](https://github.com/BurntSushi/ripgrep) | S/H：Git restore 一个已实现任务及 verifier；qsv select/sort、ripgrep 已有源与 Skill，尚无同等级真实执行证据；本地固定源与可执行程序版本须再核对 | 适合工程校准和 CLI 扩展；新任务/fixture/Oracle 需构造。常见命令容易凭既有知识完成；上游代码/文档许可分别核对 |
| C10 CL-bench | [论文 2602.03587](https://arxiv.org/abs/2602.03587)；[官方仓库](https://github.com/Tencent-Hunyuan/CL-bench)；[数据页](https://huggingface.co/datasets/tencent/CL-bench) | H：数据 revision `b28a5832…`，1899 任务、500 contexts、621 多轮；messages/rubrics/metadata。规则可能在 system context 与对话中，不全是独立文档 | 可借鉴复杂条件任务，但需去除题干规则泄漏、核对 clean 冲突、替换/审计 LLM rubric。数据条款限制 distilling/adapting 等用途，离线 Skill 编译是否属于允许评测需明确，暂不准入 |
| C11 RuleArena | [ACL 2025](https://aclanthology.org/2025.acl-long.27/)；[官方固定仓库](https://github.com/SkyRiver-2000/RuleArena/tree/59f60f6b4eb93a9b6d187ec781349d4f15618903) | H：航空、税务、NBA 三域规则与程序/数值答案；航空已有共享条件候选。未把论文总量当作本轮已核实可用量 | 数值/条件层辅助；要替换金额 substring 判定并核对规则表—代码一致性，主要不测真实动作。仓库 MIT 不自动覆盖外部规则文档 |
| C12 SOP-Bench（Amazon） | [论文 2506.08119](https://arxiv.org/abs/2506.08119)；[固定仓库](https://github.com/amazon-science/SOP-Bench/tree/f6d43858b94cf439854038101bce0eecd3e16eae)；[数据](https://huggingface.co/datasets/amazon/sop-bench) | P：10 域、1800+；H：SOP、决策/工具材料，部分工具实际是查标签 CSV，非业务状态；与 C2 不是同一数据集 | SOP 内容层候选；需要严格答案与真实状态适配，不能将查标签当执行。数据 CC BY-NC 4.0 及来源条件须记录 |
| C13 DocPrompting / tldr | [论文 2207.05987](https://arxiv.org/abs/2207.05987)；[官方代码](https://github.com/shuyanzhou/docprompting)；[tldr](https://huggingface.co/datasets/neulab/tldr)；[CoNaLa](https://huggingface.co/datasets/neulab/docprompting-conala) | H/P：文档检索、shell/Python 任务、oracle_man 关联；本轮未完整复数，端到端独立状态 Oracle U | 可复用文档—任务候选映射；检索 oracle 不是任务执行 oracle，BLEU/命令匹配不能替代状态正确。代码 Apache-2.0，具体数据许可另核 |
| C14 AgentDocsBench | 未定位到正式论文；[官方固定仓库](https://github.com/SaidiSouhaieb/agentdocsbench/tree/c7071d2ab0d8b7e04b08abe88b3ed202b414e265) | H：15 stress tasks、16 fake Nimbus SDK docs；可查 task/starter/sdk/verifier；MIT | 人工 API 机制样例；共享 retry 规则有候选，但实现代码暴露与部分 verifier 遗漏导致混淆，不作真实自然文档主集 |
| C15 UXL skills / oneTBB | 未定位到独立 benchmark 论文；[官方固定仓库](https://github.com/uxlfoundation/skills/tree/ba807a8bb42a5b68da6e33965155cd800aac0668) | H：41 Harbor tasks，26 execution、13 answer-quality、2 hardware；作者 ceiling 声明不是本研究的真实执行结果 | 软件泛化扩展；需锁定外部手册版本、找到第二个真实执行依赖任务并独立验证指标。仓库 Apache-2.0，来源文档另核 |
| C16 SkillsBench | [论文 2602.12670](https://arxiv.org/abs/2602.12670)；[官方固定仓库](https://github.com/benchflow-ai/skillsbench/tree/f860ecf02ef53412a030f8661c83d644b739ff01) | H/P：curated skills、执行任务和测试；论文/快照数量不能混用，当前可用规则簇数 U | 任务池与加载机制参考；需追溯原始源文档，隔离参考解/测试。不能从现成 Skill 反推自然来源证据 |
| C17 OPERATE | 未核实独立论文；[官方固定仓库](https://github.com/Xnhyacinth/OPERATE/tree/bfcfab934a85ef13aaa6c2a5d1c9c19b726eeb2e) | S：manifest v0.62 记 769 scenarios、502 physical-source；lite 141/82，provenance 文档却为 144/85；formal_ready=true 但 leaderboard_eligible/public_release_ready=false。已读 manifest、provenance、CityLearn YAML 与 scorer 部分 | 有动作轨迹、时序来源/源行哈希和契约；“physical-source”主要是时序/模拟器数据，不等于规则手册。需解决版本冲突和来源规则缺口；MIT code 加各上游资源条款，暂不作为主集 |

### 4.3 统一比较矩阵：来源、依赖与干预

以下“可设计”均不代表已运行。所有候选的共同前提是先验证目标证据确实进入原版加载/分块流程。`待建` 表示需要实质性标注或构造；`未证` 表示现有材料尚不支持；`隔离后` 表示必须先排除泄漏。

| ID | Source documents | Rule traceability | Task dependencies | Multiple dependent tasks | Negative controls | Skill generation compatibility | Degradation compatibility | DirectDoc feasibility | Skill-arm feasibility |
|---|---|---|---|---|---|---|---|---|---|
| C1 | 真实网页快照 | 原生 evidence，需原子化 | QA 有依据 | 已定位 2 项 | 已定位 1 项 | HTML 固定转换后可设计 | 可，需处理重复片段 | 可，终端只读文档 | 可，整包冻结待运行 |
| C2 | 程序生成 SOP | 条款与约束可对照 | 须锁同一政策 | 已定位成功/拒绝分支 | 已定位不同动作 | Markdown 可设计 | 可，只改 SOP | 可，剥离系统 clean SOP | 可，需 bridge 与隔离 |
| C3 | API 文档 | 参数/规则可定位 | 需排除替代 API | 有候选，必要性未证 | 有候选 | JSON 固定转文档 | 可，接口不能变 | 可 | 隔离后可 |
| C4 | 混合 repo/doc/domain | 需从来源重建 | 多任务≠共享规则 | 未完成 2+1 | 待建 | 原版外接可设计 | 有条件 | 隔离后可 | 路径/回退需修复 |
| C5 | 工具 schema/描述 | 调用规格可定位 | 调用依赖 | 未证长文规则簇 | 待建 | 可序列化，研究对象偏离 | 原方案改变接口 | 技术可，语义不可直接对齐 | 需重构实验，非直接复用 |
| C6 | 任务材料不一 | 子集待筛 | 多为任务目标依赖 | 未证同源簇 | 待建 | 文本子集可 | 子集可 | 子集可 | 需自行生成/冻结 |
| C7 | 缺原始来源链 | Skill 内容可审阅 | 失效配对 | 未证源规则簇 | 原无 Skill 对照不等价 | 原源 U | 非文档退化设计 | 缺源 | 现成 Skill 可，但不回答编译效应 |
| C8 | 五种本地文档 | 部分历史映射 | 通用任务关系缺 | 待建 | 待建 | 已实际生成 | 设计可 | 尚未实现 | 47 已冻结可核验 |
| C9 | 固定 CLI 手册 | 高 | Git 已有/qsv 待建 | qsv 方案见第 7 节 | qsv 方案可 | 已实际生成 | 可 | 待实现 | 已生成，采用未证 |
| C10 | context/对话混合 | 可标注 | 题干常重复规则 | 须筛选 | 须筛选 | 技术可，条款待明确 | clean 冲突/泄漏先处理 | 可但边界复杂 | 许可与 oracle 阻断 |
| C11 | 领域规则/表格 | 可 | 数值依赖较清晰 | 航空候选 | 可设计 | 文本/表格需覆盖检查 | 可 | 可 | 可设计 |
| C12 | SOP 文档 | 可 | 决策标签依赖 | 待核 | 待核 | 可设计 | 可 | 可 | 可设计 |
| C13 | 手册与检索语料 | oracle_man 非原子规则 | 检索相关≠必要 | 待核 | 待建 | 可设计 | 子集可 | 可 | 待建 |
| C14 | 人工 SDK docs | retry 可定位 | 代码可能绕过文档 | 候选但判分不充分 | feature flag 候选 | 可设计 | 可 | 隔离后可 | 隔离后可 |
| C15 | oneTBB 等手册 | 可定位 | 待核独立贡献 | 第二执行任务未证 | 待建 | 可设计 | 可 | 可 | 已有加载思路 |
| C16 | 已有 Skill，原源不齐 | 须回溯源 | skill/task 关联 | 未证同源簇 | 待建 | 原源补齐后 | 原源补齐后 | 原源不足 | 可复用安装结构 |
| C17 | 时序/模拟器来源 | 源行≠规则证据 | 控制策略/契约依赖 | 手册规则簇未证 | 待建 | 需另找真实手册 | 不能以传感器扰动冒充文档退化 | 手册缺口 | 需较大新建 |

### 4.4 统一比较矩阵：验证、归因、成本与处置

| ID | Oracle quality | Harbor compatibility | Attribution quality | Cost and reproducibility | Limitations / Evidence level | 处置 |
|---|---|---|---|---|---|---|
| C1 | 现有 QA scorer 需修复覆盖率；条件严格判定需人工 gold | 低：答案文件 + verifier | 规则链强；没有业务动作 | 低环境成本；固定 652 文档/任务快照 | S/H/P；语义证据强、执行/采用 U | 主内容层，有条件准入 |
| C2 | 原生 replay 不足；新增任务目标/副作用/拒绝判定 | 中：离线服务 + CLI bridge | 政策同源、执行链可设计 | 无外部业务费；政策/状态版本需锁 | S/H/P；实际 Terminus 执行 U | 主机制层，有条件准入 |
| C3 | DB/task tests 较强，仍需检查遗漏 | 中高：多 app 服务/依赖 | API 规则与动作可连；必要性未证 | 离线可复现，环境和许可成本较高 | H/P；分页候选 U | 第一执行备选 |
| C4 | 测试强弱混合，有泄漏/回退 | 中 | 缺共享规则/输入暴露控制 | 仓库任务依赖多；64 doc/domain 较可控 | S/H/P；真实模型复现 U | 生成对照与辅助任务池 |
| C5 | 调用字符串指标，不是最终状态 | 调用 harness 适配中 | 接口扰动与知识扰动混杂 | 数据轻，完整样例未下齐 | S/P/U | 噪声分类参考，排除主集 |
| C6 | 逐任务测试，需单独审计 | 低至中，现框架接近 | 缺共同源规则图 | 容器资源随任务变化；必须锁 release | H/P，不能偷换 2.0 版本 | 执行基础设施/任务池 |
| C7 | 通过/失败配对与成本；非新独立真值 | 取决于上游环境 | 可借鉴 attribution；筛选偏差 | 发布材料 U | P；有害样本不可估总体发生率 | 方法参考 |
| C8 | 生成审阅不是下游 Oracle | 生成端已接；执行端有限 | IR 强、规则 gold 缺 | 历史生成成本已记录；正式矩阵未跑 | S/H | 现工程底座 |
| C9 | Git 强且专用；qsv/rg 待建 | Git 低，其他低至中 | 文档必要性偏弱 | 离线低成本；CLI/文档版本需匹配 | S/H，Gold 未读正文 | 校准与后备 CLI 扩展 |
| C10 | rubric/LLM 依赖，非独立状态 | QA 低，可信判分成本高 | 多轮/context 泄漏影响 | 许可解释与语义判分阻断 | H/P；当前不满足 G7/G9 | 暂时排除正式生成实验 |
| C11 | 程序数值参考可复用，原 string scorer 不够 | 低 | 数值规则传播可解释 | 离线；上游规则与代码须一致 | H/P | 内容层备用/数值辅助 |
| C12 | 标签/模糊匹配需替换 | 中 | 状态链不足 | 离线潜力；非商业及来源限制 | H/P | SOP 内容补充 |
| C13 | 未核实全任务执行 Oracle | 中 | 检索关系有用，执行归因不足 | 语料可固定，工具环境需建 | H/P/U | CLI 文档/任务来源池 |
| C14 | 部分错误可漏检 | 低至中 | 人工来源、代码泄漏 | 小规模可复现 | H；机制 toy，不作现实外推 | 小型诊断备用 |
| C15 | execution/regex/self-report 混合 | 较低，已有 Harbor 结构 | 须去掉自报指标与源未固定 | 硬件任务成本另计 | H/P | 软件域扩展 |
| C16 | 逐任务测试需隔离 | 较低至中 | 原文→Skill 链缺 | 版本分叉、来源许可需查 | H/P/U | 下游任务与加载参考 |
| C17 | 大型 scorer，未完整验证 | 高，多后端 | 物理来源≠文档规则 | manifest/provenance 不一致，依赖重 | S/P/U | 暂不投入主线 |

### 4.5 会直接影响选型的实现发现

1. **SkillGenBench 不能按“现成生成—执行完整链”直接接入。** 既有离线探针发现 agnostic 生成输出与评测期待的 shared/tasks 路径不一致，缺 Skill 时可能回退 legacy，默认源文档/测试/参考内容的可见性需隔离；不同 no-skill 路径也未必使用同 executor。resolver 支持 root 或唯一 child，多个 child 会报错；不能误说它总会丢失 references/assets，包级材料实际上被保留。64 个 doc/domain bundle 语法有效不代表 64 个 Agent 任务已验证。历史 helper 的 302/308 case、33 个完整通过任务是参考实现探针，不是 Agent 结果。[既有可行性审计](D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/ANYTHING2SKILL_SKILLGENBENCH_FEASIBILITY_AUDIT_2026-10-15.md)

2. **RoTBench 的扰动对象与本研究不同。** 实际 evaluator 计算 tool selection、parameter identification、content filling；其名称/参数扰动改变工具使用契约。可移植噪声 taxonomy，不能把原 leaderboard 分数解释成源文档退化通过 Skill 传播的效应。[固定评测代码](https://github.com/Junjie-Ye/RoTBench/blob/637e43ae9a978036774c92bb2ab11a83609e304b/Code/Evaluation/evaluate.py)

3. **CL-bench 暂停的是特定研究用途准入。** 数据条款含对训练、蒸馏、适配等用途的限制；本报告不作法律定性，也不擅自认为写 SKILL.md 必然允许或必然禁止。在该用途明确前不运行生成实验。技术上仍有多轮边界、规则重述和判分独立性缺口。[官方数据卡](https://huggingface.co/datasets/tencent/CL-bench)

4. **OPERATE 的 source-grounded 不能直接读作文档规则 grounded。** 本轮 CityLearn 样例可定位 CSV 行和控制输出，但并未提供满足本课题的自然手册—原子规则—共享任务证据。其 141/82 与说明文档 144/85 的不一致也应先消解。[固定 manifest](https://github.com/Xnhyacinth/OPERATE/blob/bfcfab934a85ef13aaa6c2a5d1c9c19b726eeb2e/benchmark_manifest.json)、[provenance](https://github.com/Xnhyacinth/OPERATE/blob/bfcfab934a85ef13aaa6c2a5d1c9c19b726eeb2e/docs/DATA_PROVENANCE.md)

## 5. 主内容层样例：ConditionalQA 的共享资格规则

### 5.1 固定来源、原子规则与生成输入

使用 C1 固定 commit 的 v1_0 `documents.json`，本地对应[文档快照](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/cl_rules/cqa_documents.json)。文档数组索引 27，URL 为 `https://www.gov.uk/paternity-pay-leave`。这是数据集历史快照，不代表当前政策；实验 gold 以快照与核验后的任务为准，不用于现实政策咨询。

目标规则 R-CQA-26：在相应陪产假适用范围内，连续受雇达到 26 周是资格要求之一。直接证据 `contents[51]` 位于 `[47] Paternity Leave` 标题下。原文短引：**“at least 26 weeks”**。`contents[58]` 在 `[53] Paternity Pay` 标题下重复相同文字，`[106]` 还含代孕情境的相近条件；它们是残余文字线索，但不能未经作用域核验就算作陪产假规则的等价支持。时间规则 R-CQA-QW 是另一个原子规则：qualifying week 位于预产周之前第 15 周，直接证据 `contents[52]`，Pay 部分 `[59]` 有相同定义。不能把工龄与时间两个规则合成一个后再声称两个任务都依赖其全部条件。

生成输入为此完整文档的确定性 HTML→文本/Markdown 转换，保留标题、列表顺序、作用域和重复段落；转换前后均留哈希与 block/span 对照。不给 Anything2Skill 提供任务、答案、evidences 标签或“应该生成什么规则”的提示。预期输出为原版生成的完整 canonical Skill 包，数量 K 由生成器决定；不能挑一个最好的 Skill 当作该臂。

目标 Skill 应保留 26 周门槛、适用对象/假期类型、时间基准及相关条件，避免把陪产假与陪产工资等范围混并。其它规则也需记录，不能只评价是否出现数字 26。

### 5.2 两个依赖任务和一个独立负对照

任务直接复用[train 数据](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/cl_rules/cqa_train.json)；下面是中文说明，不是改写后的正式测试输入。

| 任务 | 原始情境/问题 | 依赖与预期正确结果 | Oracle 与失败例 |
|---|---|---|---|
| `train-20`，依赖任务 1 | 新工作约两个月，距离孩子出生约 20 周，询问是否满足陪产假资格 | R-CQA-26 + R-CQA-QW：资格周前只有约 5 周，连续工作不足 26 周；原答案 no | 固定任务 ID，结构化 yes/no=no；不得同时声称资格已满足；误把预产时累计工龄当判定基准或回答 yes 为错 |
| `train-41`，依赖任务 2 | 已工作 20 周，孩子约 6 个月后出生，询问需要受雇多久 | 询问门槛，答案 26 weeks；确实依赖 R-CQA-26，但并非必须进行 `train-20` 的时间推算 | 数值=26、单位=weeks、对象与问题匹配；6 周/26 月、只回答当前 20 周或矛盾附加结论为错 |
| `train-2`，负对照 | 已受雇超过 3 年，询问须提前多久告知雇主 | notice 规则：至少在预产周前 15 周通知；证据 `contents[71]`，不依赖工龄 26 周门槛 | 数值/单位/时间锚点正确；不能把“已满足资格”当作通知问题的答案 |

这里的负对照与 qualifying week 恰好同为数字 15，但它们是不同的规则和证据，不能按数字重合误连边。T1、T2 共用的是 26 周门槛，不是完整时间复合规则。

为证明共享语义依赖，设计反事实 R-CQA-26=6 周：T1 的该资格条件判断可能改变，T2 的门槛答案明确改变，而 T0 的通知要求保持不变。这个反事实仅用于依赖验证；正式退化臂仍按原始真实规则判分。T1 的全部其它必要条件仍需逐项核实，不能把一个条件满足当作充分资格。

### 5.3 退化、两条执行路径与判分加固

| 版本/路径 | 设计 |
|---|---|
| clean | 原快照及固定转换，不清除不便处理的重复内容 |
| 相关信息退化 | 改变 `[51]` 的 26→6 或删除该条件，主分析先固定这一单片段干预。另行标注所有同义、同作用域支持和跨作用域文字线索；保留 `[58]`/`[106]` 时不能声称数字信息已从全文移除。若另做跨段落统一修改，须标记为多个规则范围的干预，不冒称只改一个原子规则 |
| 无关信息退化 | 在三个任务均不依赖的产检陪同等另一规则上做同类型、尽量匹配长度的编辑；不得改 `[71]` 通知规则。最终匹配程度逐项记录 |
| 表面退化 | 只改变排版/HTML 展示形式且经独立复核语义不变；单独一组，不能与数值变更合并解释 |
| DirectDoc | Agent 执行时只读对应版本的完整文档；文档索引提供主题与路径，实际读取自主选择 |
| Skill | 在任务揭示前由对应文档版本生成并冻结完整包；运行时只给该包，不提供 clean 原文、检索旁路或 gold |

Oracle 输入为固定任务清单、审阅后的答案/条件 gold 与 Agent 结构化答案文件。评测器在隔离容器中运行，原始数据中的 answers/evidences 不进 actor 容器。本地原 scorer 的缺失预测分支先设置零，但 append 位于 else 中，可能将漏答排除出均值分母；因此必须按预定 ID 集计分，缺失=错、重复/额外 ID 单列异常。原始 exact HTML condition F1 可作兼容指标，但它既不理解同义表达，也不保证所有必要条件严格满足。[原 evaluator](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/cl_rules/cqa_evaluate.py:33)

新指标以严格答案、必要条件集合、矛盾/额外错误条件为主。开放文本的语义等价采用盲审人工双评和裁决；自动数值、单位、布尔、ID 覆盖检查先行。此三题可以主要靠确定性检查，但不能据此宣称整个 ConditionalQA 已有无人工确定性语义 Oracle。

记录源 block/span、生成 IR、Skill 所有同义规则位置、索引中是否已含门槛、实际终端读取内容、截断后进入下一模型请求的目标跨度、最终回答。QA 层的“动作”主要是检索/读取/提交，不能称作成功执行真实业务。

## 6. 主执行层样例：SOPBench 固定图书馆政策

### 6.1 来源与政策一致性

使用 C2 的固定 commit。来源为[固定 library_system_prompt.md](https://github.com/Leezekun/SOPBench/blob/8790ed7406acbd22270f90bd1c4038de3fc5db8f/reference/prompts/library_system_prompt.md)，本地[完整快照](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/leezekun-sop/SOPBench-8790ed7406acbd22270f90bd1c4038de3fc5db8f/reference/prompts/library_system_prompt.md)。`borrow_book` 条款 44—52 行中的目标规则 R-SOP-DUP 为：申请借阅的 book ID 不得已在该用户 borrowed 中；第 48 行关键短引 **“must not exist”**。其它条件包括登录、库存、受限书的会员条件、借阅数上限。

不能直接将 66 个 library tasks 全部挂到同一默认 SOP：`env/task.py` 会用每个任务的 constraints 和 constraint_parameters 替换目标动作的默认政策。历史 inventory 中 144 个任务的结构和参数与默认政策匹配，只能作为进一步语义检查的候选，不是已经通过的 144 个样本；其中 library 18、university 33 也是候选量。正式入选需逐任务确认完整有效政策一致。[任务加载代码](https://github.com/Leezekun/SOPBench/blob/8790ed7406acbd22270f90bd1c4038de3fc5db8f/env/task.py)

生成输入为固定完整 SOP，既不附任务初始状态，也不附 action graph、`action_should_succeed`、constraint evaluator 或参考工具序列。原版 Anything2Skill 输出整个包并冻结。目标 Skill 应保留“同一用户已借该书则拒绝”及其范围，不能变为所有用户共享禁借，也不能遗漏其它许可条件。

### 6.2 可核查的 2+1 原始任务

ID 使用 `domain/action/零基数组索引`，是本报告为定位原数据定义的审计 ID，不冒充原发布中的全局 ID。[原任务文件](https://github.com/Leezekun/SOPBench/blob/8790ed7406acbd22270f90bd1c4038de3fc5db8f/data/library_tasks.json)；[本地三任务完整抽取](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/sopbench_library_2plus1_samples.json)。

| 任务 | 已核对的状态与真实依赖 | 正确行为/期望状态 | 专用 Oracle |
|---|---|---|---|
| `library/borrow_book/25`，依赖成功分支 | pepperoni 请求 Beloved（93TC00Q）；borrowed 空，库存 1，会员有效到交互日 2024-10-10，借阅上限 2，其余条件满足 | 成功认证、读取必要事实、借阅一次；该书库存 1→0，用户新增到期日 2024-10-24 的借阅；其它业务字段不变 | 核对调用者、对象、认证、期望数据库差分与一次有效借阅事件；错用户、错书、重复动作或无借阅均失败 |
| `library/borrow_book/27`，依赖拒绝分支 | mario 已借 93TC00Q（原到期日 2024-10-10）；会员到 10-11、库存及数量条件满足；仍请求借同书 | 识别重复借阅并明确拒绝；保持业务状态。不能先还书再重借、换书或改账号来绕过 | 需要确证已有借阅的查询证据与结构化拒绝结果；业务差分为空且无借阅/归还/扣费事件。空轨迹/no-op 不能仅因状态没变而通过 |
| `library/pay_late_fee/0`，不依赖目标规则 | pepperoni 余额 30，late_book_count=2，每本费用 3；目标是支付已有滞纳金 | 成功认证并扣 6，余额=24；原实现的 late_book_count 仍为 2，其它业务状态不变 | 验证正确账号、一次扣费、金额与允许差分；多扣、扣他人、修改 borrowed 或将计数清零均失败 |

最后一项忠实于这个 benchmark 的固定实现：`pay_late_fee` 只扣余额，并不清零逾期计数。不能按现实图书馆直觉修正 gold。允许的会话认证状态与业务状态分开记录，否则正常登录也会被“全库不变”误判。[library 实现](https://github.com/Leezekun/SOPBench/blob/8790ed7406acbd22270f90bd1c4038de3fc5db8f/env/domains/library/library.py)

依赖证明：若目标文字被反向改为“已在 borrowed 中才能借”，成功分支与拒绝分支的判断都可能反转；付费任务不依赖该条件。若只删掉禁止重复借阅条件，主要影响拒绝分支，不能预言成功分支也必定变坏。重复借阅禁止本身可能是常识，所以这组三任务首先验证机制可测性；后续应扩展到数值、例外和非默认政策，但必须保留同源同政策约束。

### 6.3 两臂、退化和环境隔离

clean 使用完整 SOP；相关退化分别设置目标否定词丢失、条件反转或条件删除，不能将这些类型混成一个 severity。无关退化选择三个任务不依赖的房间预约条款，匹配编辑类型；不能改付费条款。表面排版变化另列。真实数据库、约束规范、工具 schema、任务标准答案均保持 clean 版本。

采用允许研究规则遵守行为的 prompt 模式，只由环境执行固有技术约束；若 program 模式自动强制所有业务规则，会把错误 Skill 的效应屏蔽。必须明确该模式的环境行为并以离线探针验证，不能仅看配置名。真实业务服务则可能有强约束保护，其外推结论另讨论。

DirectDoc 臂自主访问完整对应 SOP；Skill 臂只访问对应 frozen package。两臂共用中性 API 文档、完整允许工具集、终端 executor 和状态服务。系统 prompt、工具描述、异常信息中不能偷偷保留完整 clean SOP；不得把 constraint_hint、动作图、成功标签或 gold 顺序发给 actor。不得按任务只提供“正确的几个工具”，否则工具筛选本身泄漏路线。

当前 Terminus-2 使用终端动作，SOPBench 原生函数调用不能声称零改动直连。建议将现有工具封装成薄 CLI/API bridge，数据库与约束/验证代码在 actor 不可读写的服务容器，actor 只见中性 schema、认证参数及合法状态查询结果。阻止直接读取数据库文件、Python 内部对象、测试与参考实现；正常查询 API 仍可用。不要求执行固定命令序列，只要求满足政策、目标与副作用约束。

### 6.4 原生 Oracle 为什么必须补强

原 evaluator 主要将 actor 的动作序列在严格环境中复演、比较响应和最终数据库；这可以检测一部分违规，但“复演自身动作”不等于“达成了正确目标”。静态检查指出以下需要验证的失败面：[evaluator.py](https://github.com/Leezekun/SOPBench/blob/8790ed7406acbd22270f90bd1c4038de3fc5db8f/env/evaluator.py)。

- 空轨迹、执行了其它合法动作、操作错误对象，可能无法仅靠同序列 replay 排除；新 Oracle 必须绑定用户目标、用户身份与目标对象。
- 参数回退使用 truthiness 的位置需以 `0`、`false` 等合法值验证，不能让它们被错误替换。
- 登录实现中状态设置与凭证校验的先后需要负例验证，不能把“出现 logged-in 状态”当作认证成功。
- SOP 中余额“more than”与实现 `>=` 在恰等费用时可能不一致；本组三任务避开该边界，但不能因此称整个域一致。遇到冲突应公开标注/排除，或另立修订 benchmark 版本，不能静默修 gold。

以上为静态风险，不是本轮已经执行成功的漏洞利用。新增 Oracle 独立计算期望差分，不把同一业务实现当作唯一真值；同时使用受信服务事件记录，识别先破坏后恢复的暂态副作用。拒绝任务需满足事实检查、明确拒绝、无业务副作用三项，而非“什么都没做”。

无需模型的验收探针至少包括：正确成功、正确拒绝、空轨迹、错用户/错书、错误密码、重复借阅、双重扣费、额外合法充值、伪造结果、先改后恢复、日期边界、余额相等、参数 0/false。预期结果由人工规则表独立给出，不能靠被测代码自己生成所有 expected。

## 7. 明确的后备与不强行通过的候选

### 7.1 AppWorld：有执行基础，但共享规则必要性尚未通过

候选规则为 Spotify `show_playlist_library` 分页：page_index 默认 0、page_limit 默认 5、允许 1—20。历史审计定位 `692c77d_1`（从播放列表为歌曲评分）、`b7a9ee9_1`（关注播放列表相关 artists）及 `ccb4494_1`（喜欢队列歌曲，作为分页负对照）。文档输入应为固定 API 文档包，输出为完整 frozen Skill；预期 Oracle 是目标记录集合与禁止额外更新。

**暂不把它当作已完成的 2+1 样例。** 参考解循环 page 0—9 不证明任务一定需要后续页面，也不证明不存在另一个合法 API。须在初始数据库中证明目标集合跨页、两个任务都必须覆盖后页、负对照无需该规则，并审查测试是否忽略 updated records。DirectDoc/Skill 与分页数字退化可按统一协议设计，但必要性和隔离缺口未补齐前不运行主实验。若 SOP 的约束/认证问题导致加固成本失控，优先推进此替代路线，而非继续扩大 SOP 子集。

### 7.2 qsv：低成本的明确任务设计，仍不宣称“必须读 Skill”

固定本地来源为 `qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md`，SHA-256 `74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。证据行 57—61 的示例说明第三个同名 Foo 列使用 `Foo[2]`（索引从 0 计）。原文短引 **“third column named 'Foo'”**。生成输入为完整 select 文档，输出冻结完整包；需要保留重复表头、索引语义、列顺序等条件。[本地原源](D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md)

三个任务均为**拟新增 fixture，尚未构造正式数据**：

| 任务 | fixture / 目标 | 期望行为与 Oracle |
|---|---|---|
| Q1 依赖 | 表头 `ID,Foo,Foo,Foo,Note`，每个同名列值不同；导出第三个 Foo 的全部记录 | 输出对应第 4 个物理列；逐行值、表头、顺序正确，输入不变 |
| Q2 依赖 | 表头 `Foo,ID,Foo,Note,Foo`，仍取第三个 Foo 并同时导出 ID | 输出为 `ID,Foo`，值取第 2 与第 5 个物理列，顺序保持；不能靠记住 Q1 的列号 |
| Q0 负对照 | 同一源语法下只需选择唯一 ID 与 Note | 唯一列选择正确，不依赖重复列索引 |

相关退化将重复索引说明改成从 1 计或破坏该例子的索引；无关退化选择这三题均不用的范围/反选条款；表面改动另列。DirectDoc 读取对应文档，Skill 读取其冻结包。Oracle 使用保留重复表头的列表式 CSV 解析，不能用按键合并的 DictReader 产生假 gold；核对输出、输入哈希与工作区允许变化。日志关联 target span 与实际命令/文件输出。

这些任务在使用 qsv 重名选择语法时共享目标规则；但是 Python/位置索引等合法方法可能绕开它。不能禁用所有替代方法来伪造文档必要性。若 A0 与局部干预表明规则对行为无影响，该组只能保留为 CLI 观察校准，不能声称已经证明文档传播。正式接入还需锁定 qsv 二进制版本并确认与手册语法一致。

### 7.3 现有 Git 的保留价值

固定源 `git-restore.txt` SHA-256 为 `2afb2f9183ad599a490c32fd174df66b0532abbe252887bc5c8b57d82a60f468`，7082 bytes，源 commit `a52a24e…`。已有任务让目标文件的工作区和 index 回到 commit A，同时保持 HEAD/refs 和其它文件；A/HEAD/index/worktree 四种内容不同，有脏的其它 tracked 文件与 untracked sentinel。这是好的独立状态验证案例，适合校准日志、隔离、DirectDoc 和读取可见性。[已有任务](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/git_restore_explicit_source_both_v1)

九项断言覆盖目标 worktree bytes/mode、目标 index blob/mode、HEAD/refs、不相关 tracked worktree、不相关 tracked index、untracked sentinel、其它 worktree 变化、完整 index、额外 commit/object/metadata。verifier 从受信 baseline 和原始状态验证，不运行 actor 的 Git/配置。最后一项较严格，可能排除会产生额外对象但最终工作区正确的替代解；这是当前任务合同，不能不加解释迁移到所有 Git 任务。该案例常见且索引提示明显，不应成为文档依赖的唯一科研来源。

## 8. 三层评价：生成质量、使用机制、最终结果

### 8.1 外部规则与证据图

建议最小外部记录包含：`source_id/revision/hash`、`evidence_id/block/span/hash`、`rule_id`、条件/结论/参数/例外/范围、等价证据集合、`task_id`、必要规则集合、可替代路径、依赖理由、负对照理由、标注者与裁决。每个退化版本另存 edit/span/type/severity、目标规则、残余支持及哈希；每次生成存运行配置、IR 和全部 canonical 输出。

任务可以依赖多个规则，规则可由多个片段共同支持，同一片段也可支持不同规则，应使用带集合条件的关系图，而非强制一对一。以 source/rule cluster 划分训练式开发、人工校准和正式评价，避免同源近重复任务泄漏。生成器只能看源文档；评审者可看 gold，但下游 actor 不能访问审计图中的答案与规则判断。

### 8.2 Skill 生成质量：区分支持性与世界正确性

必须同时保留两套参照：①当前输入文档支持什么；②固定原始任务世界中什么是正确的。忠实编译已被污染的 6 周规则，是“输入支持但世界错误”，不能算生成器无依据幻觉；源条件删除后仍生成原来正确的 26 周，是“当前输入缺支持但世界正确”，可能来自既有知识，不能直接算事实错误。

| 指标/检查 | 计算单位 | 自动化边界 |
|---|---|---|
| 完整规则保留率 | 已人工确认的规则；条件、参数、例外、范围均正确才记完整 | 人工语义标注为主；数字/枚举检查辅助 |
| omission / partial / contradiction / wrong scope | 每条规则并报告 uncertain | 双人独立、盲于臂标签的评阅与裁决；部分保留不当完整 |
| 生成声明的支持率 | 每个生成声明是否有当前输入支持 | span 回链可自动检查存在，支持关系仍需语义审查 |
| 任务加权规则风险 | 各任务必要规则中错误/缺失情况 | 依赖图固定后可算；与全源覆盖率并报 |
| 危险指导与副作用建议 | 不必要删除、绕过约束、错误对象等 | 任务合同与人工复核，不只关键词计数 |
| 冗余、相互矛盾、路由碎片化 | 整个 frozen bundle，而非单一 SKILL.md | 重复候选自动找，语义最终确认 |
| IR 首个可观察偏差 | source→ingest→extract→compile→register→final | 哈希/字段/跨度可自动定位；首次语义偏差人工确认 |

保留率分母来自完整审阅的规则全集；支持率分母来自生成声明，两者不能混淆。对共享源的 14 个 Skill 不应当作 14 次独立文档实验。自动工具可核验路径、hash、缺失 ID、证据跨度、数值和格式；本轮不调用独立付费 judge。若未来用 LLM judge，应作为经人工校准的辅助，不让同一生成模型同时充当唯一裁判。

IR 归因报告“规则首次在哪个可见产物中缺失/变化”，而非声称读出了模型内部原因。若 clean 目标证据从未进入 ingest window/模型请求，应标记输入覆盖失败；不能将其包装成退化导致的生成能力下降。

### 8.3 Agent 使用机制：分级而非单一 read=true

| 层级 | 需要的证据 | 不能推出什么 |
|---|---|---|
| M0 installed | 安装 manifest、包哈希、可访问路径 | 不证明发现 |
| M1 discoverable / metadata exposed | 实际首个请求中的索引、名称、描述、路径 | 不证明读正文；metadata 可能已暴露规则 |
| M2 file accessed | 受信文件/工具日志，区分 actor、runner、verifier | open/access 不证明内容进入模型上下文 |
| M3 target span exposed | 实际工具返回，经截断/转义后进入下一模型请求的目标跨度 | 正文出现不证明被理解或采用；partial 与 full 分开 |
| M4 action consistent | 参数、顺序、对象、拒绝/执行与目标规则相符 | 常识、任务提示、其它文件也可导致相同行为 |
| M5 intervention responsive | 局部修补/反向破坏在固定其余条件下改变相关动作/结果 | 仍需排除路由、长度、其它规则改变等混淆 |

现 observer 已有文件事件与完整正文可见检测；完整文本匹配对部分读取、相关 references 和目标跨度还不充分。最低扩展是记录规则跨度在 metadata、SKILL.md、references/脚本和下一模型请求中的实际可见性；同时留原始工具输出与截断后的内容。模型自述“我使用了 Skill”只作为文本，不作为读取证据。

主分析保留原版生成的名称/描述，因为它们是编译产物的一部分；不可为了“防泄漏”悄悄重写后仍称原版 Skill。需要另设诊断性 metadata-only 或匹配的中性索引条件，明确属于不同处理，用于分离正文与索引贡献。强制读取、把全文塞进 prompt 只能作为内容可用性诊断，不能替代自主发现主结果。

建议报告：安装率、索引可见率、目标跨度暴露率、暴露后的相关动作比例、无正文成功比例、规则干预响应率，以及各状态的不可观察比例。未经干预的“读过且动作相符”只能称一致性证据。主效果按全部分配 trial 计算，不在退化之后只挑读过的 trial。

### 8.4 最终任务结果与失败诊断

统一结果壳只包含身份、版本、运行状态、任务完成、约束符合、副作用、理由及证据引用；实际判定由任务专用 verifier 实现。至少分开 `PASS`、`TASK_FAIL`、`INFRA_ERROR`、`BUDGET_STOP`、`NOT_RUN` 和 `NOT_OBSERVABLE`，不把未运行或观测丢失直接塞进失败率。

| 任务类型 | 核心真值 | 副作用/边界 |
|---|---|---|
| CQA | 固定答案、单位/条件、作用域、矛盾声明 | 缺失/重复 ID、漏条件、乱加结论、文件输出格式 |
| SOP | 用户目标 + 独立期望状态差分 + 政策约束 + 受信事件 | 错用户/对象、重复动作、无理由拒绝、空轨迹、暂态后恢复、认证与业务字段 |
| Git | 指定目标 bytes/mode、index、refs 及完整工作区/metadata 合同 | 原有九项仅适用于该固定 fixture 与 index 格式假设 |
| qsv | CSV 列/行/值/顺序与重复表头语义 | 输入被改、其它文件变化、换工具但结果合法的替代解 |
| AppWorld | 任务级目标记录集合/字段与禁止变化 | 现测试未覆盖的更新、额外 app 变化、直接 DB 旁路 |

诊断按证据组合，允许多个原因并存：

- 环境没启动或请求未发出：基础设施失败，不归因 Skill。
- Gold 的确暴露了正确规则仍失败、A0 也失败：能力/工具使用或任务理解不足的候选解释，需轨迹确认。
- Skill 有错但没有目标跨度暴露：已证明生成缺陷，尚未证明它传播到动作。
- 正确 Skill 未被读取：发现/选择问题或不需要它；不能称生成内容导致失败。
- 错误规则可见，动作与之相符，局部正确修补能挽救：较强传播证据；仍检查是否修补改变了其它因素。
- 最终状态对但出现禁止的中间操作：任务完成与过程安全分开，整体约束判定不通过。

## 9. 对照、局部干预与统计解释

### 9.1 主实验矩阵

| 臂 | 生成阶段 | 执行时可见信息 |
|---|---|---|
| A0 | 无 | 同一任务、工具与通用环境，无来源文档和 Skill |
| D-C / D-R / D-U | 无 | clean / 相关退化 / 无关退化源文档 |
| S-C / S-R / S-U | 分别由 C/R/U 独立调用原版生成并冻结 | 对应完整 Skill 包，无原文旁路 |
| Gold | 人工审核的 clean 规则包 | 诊断正确知识可用性与观察链，不冒充生成结果 |

所有主臂固定 task、初始状态、工具 schema、真实 gold、executor/model、温度、预算和重试策略；顺序随机化或成组平衡。DirectDoc 与 Skill 的信息长度本来不同，这是总效果的一部分，应记录成本；可另做预算敏感性分析，不以逐 token 相等作为主公平性的唯一条件。来源转换、索引呈现和允许检索方式预先固定。

不得将 clean Skill 与坏文档混用后当作 S-R；不得为每个下游任务重生成定制 Skill；不得根据 outcome 选择最好生成 seed。输出包可跨同源任务复用，但因此形成簇相关，需要在分析中保留。

### 9.2 主效应与否定性结果

以损失 L（失败=1 或预注册连续损失）表示：

`ΔS = E[L(S-R) − L(S-C)]`

`ΔD = E[L(D-R) − L(D-C)]`

`编译路径交互 = ΔS − ΔD`

同时报告相关相对无关退化的差值，以及目标依赖任务相对负对照的差值。信息删除、数值错误、否定词反转、排版变化分别分析，不能合并为没有统一含义的 severity。若 S-C 已经丢规则，需报告 clean floor 与不同增量，不能删除这些坏 clean 输出来美化退化效应。

这些比较估计的是所选执行协议下的总效果和交互；**不能仅凭“读过 Skill”这个处理后的变量分层，就宣称识别了因果中介效应。** 读取路径是描述性机制分析，需要额外随机干预才能更强地归因。

首轮每源只 2 个依赖任务 + 1 个负对照，不能用于宽泛显著性宣称。正式阶段按来源/规则簇进行配对与分层 bootstrap 或适当层级模型，报告效应量与置信区间；生成重复与执行重复作为不同层级。增加同一来源的上百次运行不能替代更多独立来源。CQA 与 SOP 分层报告，不能以任务数加权混成“总体 Agent 成功率”。

### 9.3 局部干预的解释力

在冻结生成结果后另建不可变派生包：①只修复目标规则；②同长度的无关 sham 修改；③在 clean 包中反向破坏目标规则。每个版本独立哈希，全部同义规则位置与 references 都需审查。若只修正文而 metadata 仍给出相反规则，要保留并解释这个冲突，不能声称“仅一个规则已彻底修复”。

源文档修补后重新生成与直接修 Skill 是两个不同干预：前者测试编译稳定性，后者测试现有产物中该规则的作用。后者不是原版自然生成输出，只作机制诊断。若正确修补无挽救、反向破坏无影响，应降低对目标规则因果作用的判断，而不是只展示有利 case。

## 10. 从当前状态到首轮实验的最短路线

### 10.1 本轮之后的实施顺序

| 阶段 | 最小工作 | 验收证据 | 优先级 |
|---|---|---|---|
| 0 审阅与冻结协议 | 审阅本报告；确定 CQA/SOP 两源与 6 任务；锁版本/许可/真实标准；预注册失败政策 | 任务—规则—证据表、来源/fixture/工具 hashes、数据可用性结论 | P0 |
| 1 无模型补齐 | DirectDoc 安装路径；目标跨度/metadata 观察；CQA 严格答案 verifier；SOP 任务目标 Oracle 和最薄 bridge | 离线正反例通过、actor 不能读 gold/数据库代码、观察器区分全读/部分/截断/未读 | P0 |
| 2 校准已有 Git | 复用现有容器/fixture，建立新的有限 scope；检查自主发现与真实请求中的跨度 | 记录读取/未读均可判定；Gold 的知识可用性及 verifier 正例；不重复消耗旧停止账本 | P1，真实调用须后续实施阶段 |
| 3 六任务可行性 pilot | 2 个源，各 1 条共享规则与 2+1 任务；C/R/U，D/S，A0/Gold | 每个失败能归为任务/环境/预算/观测；全部主臂可运行、包被冻结 | P1 |
| 4 扩展正式研究 | 优先增加独立来源与规则类型，再增加生成/执行重复 | 预注册样本量、效应阈值、统计计划；独立评审与Oracle边界覆盖 | P2 |

必须新增/修改的是适配与评价层：DirectDoc、暴露日志、外部规则表、任务专用 Oracle、SOP bridge、预算 scope 配置。无需替换 Harbor/Terminus-2，也无需改变 Anything2Skill 核心。现有持久预算、隔离 verifier 和 artifact 记录应复用；不能为赶进度绕过已修复的预算保护。

人工工作集中在：CQA 规则原子化及 3 个任务语义复核；SOP 固定政策一致性和独立 expected delta；盲审生成规则；公开来源许可/版本表。首轮 CQA 和 SOP 共 6 项均复用原始任务内容，仅增加固定输入/输出契约与 Oracle；qsv 的 3 个任务是后备新构造，不与原生任务混记。

### 10.2 规模与成本预算口径

最小可行 pilot：2 来源 × 3 文档版本 = **6 次生成 pipeline 运行**，每次输出完整包；不是 6 次 HTTP，因为每个 pipeline 可能包含多次调用。6 任务 × 3 版本 × 2 路径 = **36 次主执行 trial**，再加 6 A0、6 Gold，共 **48 次下游 trial**。Git 校准、重跑、局部修补与表面退化诊断不包含在 48 内，必须分别预算。

若后续使用 3 次独立生成、每包 3 次执行，DirectDoc 每版本 3 次，则主 trial 为 `6 × 3 × (3 × 3 + 3) = 216`，加 A0 18、Gold 18，总计 **252**；生成 pipeline 为 `2 × 3 × 3 = 18`。这仅解释重复层级，不是建议立即花费该预算；只有两个源仍不足以支持泛化。

费用使用 `生成各请求输入/输出/缓存 token × 实际计费单价 + 下游对应 token + 环境费用`，另报预留与失败消耗。以小规模实测分位数制定新 scope 上限，不能把历史 638,946 token 简单乘成新数据固定成本，更不能用参考价格假装真实账单。开发工作量粗估为 CQA 1—2 人日、SOP 2—4 人日、AppWorld 后备 3—6 人日；这是审计规划估计，不是测量结果或承诺。

### 10.3 正式退化实验的放行条件

1. **来源门槛**：真实源/程序生成源类别明确，固定快照、许可和转换可复现；不混入任务答案。
2. **规则门槛**：两个依赖任务与一个负对照的理由经独立复核；目标重复片段、其它必要规则及替代路径已列明。
3. **输入门槛**：clean 目标证据确实进入 Anything2Skill 加载产物和相关请求；IR 到最终包可追踪；保留完整包。
4. **Oracle 门槛**：正确、空轨迹、错对象、缺答、额外副作用、边界等离线用例通过；期望值不全由被测实现自己生成。
5. **隔离门槛**：actor 看不到 gold、参考解、测试、原 clean SOP、服务端约束实现或数据库文件；允许的中性 API 不泄漏政策答案。
6. **可观察门槛**：能够校准区分 metadata 可见、访问但不进入上下文、目标部分可见、完整可见、截断与未读；不要求每项正式任务都必须读取。
7. **基线门槛**：正确知识可用性经过 Gold 诊断；记录 A0 的知识绕过与 clean 失败。若任务本身定义/工具不可用先修复；不得因结果不利事后筛掉 clean 失败。
8. **运行门槛**：所有臂相同模型/工具/预算策略，scope 与失败语义清楚；固定任务顺序随机化方法、样本量、停止条件及统计估计量。

### 10.4 风险、否证与停止规则

| 观察结果 | 对研究主张的影响 | 下一步/停止条件 |
|---|---|---|
| clean 文档的目标片段未进入生成请求 | 无法研究该规则的编译传播 | 暂停此源；检查转换/窗口，优先换适配来源，不暗改核心算法 |
| 相同 SOP 与任务有效政策不一致，或 Oracle 无法区分空轨迹/错误目标 | 正确性真值不足 | 排除此任务；若域级普遍存在且加固成本过高，切换 AppWorld/CLI 后备 |
| A0 与各臂接近，目标规则修补/反向破坏也无影响 | 文档知识对该任务不构成可观察影响 | 降为校准或换更有规则依赖的来源；不能以“模型鲁棒”解释所有不敏感结果 |
| 自主 Agent 大多不读，而强制注入才有效 | 自主使用链存在瓶颈；自然传播假设可能不成立 | 如实报告自然不使用；强制实验另列，不能替换主结果 |
| 正确修补没有挽救，或 sham 同样挽救 | 目标规则归因不足 | 检查其它规则、长度与路由；不声称该规则导致失败 |
| 相关与无关退化影响相同，负对照也同幅下降 | 可能是长度/排版/发现负担，而非目标语义规则 | 增加匹配控制；若无法隔离，停止规则级因果主张 |
| `ΔS − ΔD ≤ 0`，且区间排除预设有意义的正效应 | 不支持“Skill 编译放大风险”，可能缓冲或近似等效 | 保留否定结果；不能不断换数据直到正向显著 |
| 严格服务端约束拦截所有错误动作 | 测到环境保护效应，而非 Skill 对最终状态的直接风险 | 分开报告违规尝试与最终状态；不把零最终失败当 Skill 正确 |
| 许可不明确、无法固定必要服务或来源发生不可追溯变化 | 可复现/可使用门槛失败 | 暂停该候选，使用已合格替代来源 |

正式研究需预先规定最小有意义效应与置信区间目标；不得用 pilot 的显著性来决定持续加样本直到支持假设。研究问题本身不要求“退化一定有害”或“Skill 一定放大”；证据也可能支持缓冲、无效应或主要发生在发现阶段。

## 11. 尚未核实与不能写进论文的结论

- CQA/SOP 在当前 Harbor + Terminus-2 中的真实 DirectDoc/Skill 成组运行尚未执行；本轮没有新模型证据。
- CQA 全量条件答案的语义正确性、原始 evidence 完整性、全部重复段落覆盖尚未人工复核；三任务可定位不等于全量已经准入。
- SOP 的 144 个默认政策匹配候选未逐一完成语义审查；认证、truthiness 和余额边界风险未通过本轮运行探针确认；服务桥与新 Oracle 尚未实现。
- AppWorld 的两项分页任务是否不可由其它 API/已知信息绕过，目标是否确实跨页，以及全部测试对额外更新的覆盖，尚未完成验收。
- SkillGenBench 的共享规则 2+1、无泄漏同 executor 对照、当前路径适配和真实 Agent 全量通过率未核实；不能引用参考 helper 通过率替代。
- Terminal-Bench 的正式 2.0 发布快照尚未在本轮重新完整固定；既有较新仓库快照不能替代指定版本。
- RoTBench 部分 JSON 下载未完成，其论文数量没有被独立全量重算。Agent Skills Can Be Harmful 的完整独立公开数据/仓库未定位，不等于断言永远不公开。
- CL-bench 数据条款对本研究的离线编译用途尚未明确；其它来源文档及派生材料再发布许可需逐来源记录。
- OPERATE manifest/provenance 计数冲突及全部 scorer/backends 未完整验证；当前不会因 ready 字段而宣称可直接正式评测。
- qsv/ripgrep 的二进制与来源版本匹配、新任务和 Oracle 尚未实现；现有 Git 只证明固定案例链路，不能推出其它 CLI 可用。
- 47 份 Skill 的哈希完整性已核验，语义完备性尚无独立 gold 全量证明；历史 156 单元审计不能直接当正式错误率。
- Gold 成功但未读正文；A0/A1 未运行。因此当前不能写出“生成 Skill 提升任务成功率”“退化造成下游失败”或“Skill 相对 DirectDoc 更脆弱”等结论。
- 当前成本只有 token/请求证据，实付金额未知；开发人日与未来 trial 数属于计划，不是已发生费用或运行。

## 12. 本轮证据索引与交付验收

本轮重新生成的只读审计产物：

- [47 份 canonical Skill 路径与哈希](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-20/canonical_skill_hash_audit.json)
- [CQA 与 SOP 实际数据计数](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-20/dataset_counts.json)
- [关键已检查证据文件哈希](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-20/inspected_evidence_hashes.json)
- [公开材料获取记录](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-20/public_sources/fetch-manifest.json)与[GitHub blob 获取记录](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-20/public_sources/blob-fetch-manifest.json)：含失败/不完整项，不把失败当成功。

原始代码与实验索引：

- [下游实现目录](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval)
- [当前 Git task/fixture/verifier](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/git_restore_explicit_source_both_v1)
- [Gold Skill](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/gold/SKILL.md)
- [最新 P1-C 恢复报告](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/report.md)
- [SkillGenBench 既有可行性审计](D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/ANYTHING2SKILL_SKILLGENBENCH_FEASIBILITY_AUDIT_2026-10-15.md)
- [既有下游 Oracle 开放选型](D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/DOWNSTREAM_BENCHMARK_AND_ORACLE_OPEN_SELECTION_2026-10-16.md)

本报告已覆盖准入标准、真实工程状态、17 类候选的统一比较、两组原生 2+1 样例和一组 CLI 后备设计、三层评价、任务专用 Oracle、主效应与机制干预、最小实验数量、放行与否证条件。**下一步先审阅本报告，再实施适配层与离线验收；本轮不继续修改实验代码或启动模型实验。**
