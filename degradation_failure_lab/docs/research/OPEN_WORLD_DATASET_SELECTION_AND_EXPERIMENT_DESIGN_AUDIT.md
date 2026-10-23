# 开放式数据集选型与实验设计审计

审计日期：2026-10-21。目标项目：`D:\AS\AutoSkill-main`。本报告按本轮最新任务重做准入判断；先前报告的“2+1 必须成立”“按生成结果筛选”等建议不再作为本研究规则。本轮只检索、读文件、做离线结构与加载检查，没有运行模型、真实 Agent 或正式退化实验。

## 1. 决策：先批准有限可行性检查，不立即冻结数据集

**主方案：从 GitChameleon 的公开版本敏感代码任务中筛选单任务，以对应版本的开发者原始文档构成一个主研究集。先用 Flask 3.0.0 的 144、164 两题做可行性检查；不强制把原题改造成更长工作流，也不强制凑成 2+1。** 两题只是调试样本，不是足够支持论文结论的数据规模。优先它是因为已有真实源文件、版本约束、起始代码和隐藏测试，可以建立逐项证据链；不是因为它已经接入本工程。综合状态 **PARTIALLY VERIFIED**：文档和任务结构已核验，文档的行为效应、完整生成质量及当前容器执行均未验证。

**唯一备选：Agent-Diff 的 Box 任务 + 固定版本 Box 官方 OpenAPI 文档。** 它提供真实状态修改和有意义的连续操作，但当前文档窗口覆盖和目标判分均有具体缺陷；它是有条件备选，不是可立即启动的替代品。优先 131，再审 141；不能原样接受其 reward。若主方案经预先固定的 A0/A1/A3 校准显示缺少可辨别的知识效应，或合格独立来源过少，才转向这个备选，且必须先修复其准入缺口。

**现阶段推荐方案 A：单一主数据集。** 可支持的主张限于“版本化软件技术文档退化，经原版 Anything2Skill 编译后，如何影响代码执行任务”。不能据此推广到自然业务政策、长篇员工手册或 GUI 操作。外部验证在主机制成立且确有跨类型主张时再增加；不是为了凑数量。MAGE、HANDBOOK 等可提供不同文档类型的线索，但目前没有第二套已经全部通过核验的资源。

最先验证三项风险：

1. **文档知识是否真正起作用。** 任务版本旧、API 常见、提示或 starter 已给关键线索，A0 可能很强。静态分析不能替代 A0/A1/A3；不能伪造基线，也不能用 A2 结果筛选任务。
2. **原版生成器是否保留目标知识并形成可用 Skill。** 能读入文件不等于规则进入窗口，更不等于生成正确。Flask 目标锚点进入了离线窗口，Box 诊断文档却明显丢失契约正文；真实 LLM outline、提取、编译、合并仍未测。
3. **任务与独立 Oracle 是否可重复、能拒绝伪成功。** GitChameleon 需逐题验证参考解、错误解与副作用；Box 原评价已存在漏约束。当前 Docker Linux 引擎不可连接，历史 Gold 成功不能替代当前执行验证。

尚不能正式冻结：独立来源和规则清单、完整版本文档包、逐题 Oracle 反例、A0/A1/A3 校准、固定模型与新预算、生成器完整运行的可记录性。**没有一个已审计候选现在可以宣称“原样下载即可满足全部条件”。** 本结论是研究设计推断，不是模型试验结果。

## 2. 证据口径、检索方法与发现边界

### 2.1 证据标签

| 标签 | 本报告含义 |
|---|---|
| VERIFIED | 已读到对应原始文件/字段/代码，或有明确范围的实际离线检查结果；不外推到未执行环节 |
| PARTIALLY VERIFIED | 关键部分有原始证据，但版本、环境、映射、Oracle 或行为验证仍缺一项以上 |
| UNVERIFIED | 未取得必要资源或尚未检查；论文声称和搜索线索不能替代实现核验 |
| FAILED | 某项实际检查失败，或已观察到违反该项必要条件；仅限定于该检查范围 |

每一节区分“原始观察”“作者报告”“设计判断”“待测假设”。例如，一个 HTML 正文长度 VERIFIED，不代表其 Oracle VERIFIED；论文报告 65 项任务，不代表本地已取得 65 项。以下提到的旧离线反例是本轮重新读取的固定产物，不冒充本轮重跑。

本地证据根目录：

- 新核查：[audit_selection_design_2026-10-21](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21>)，含检索日志、仓库身份、真实 parquet、当前源代码快照索引、长度统计及无模型探针。
- 已下载原始材料：[audit_open_world_2026-10-21](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21>)，本轮复查其原始数据与代码，不沿用其推荐顺序。
- 更早原始材料：[audit_final_review_2026-10-20](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20>)，含 CQA、SOPBench、Agent-Diff 与 Box 原始文件。旧报告不是原始证据的替代品。

### 2.2 开放式发现实际做了什么

发现方向覆盖开发文档/版本迁移、手册到 GUI 操作、政策驱动业务状态、科学论文/实验规程到程序、可执行测试与 Skill 检索。组合检索包括 documentation-grounded tool execution、policy workflow executable benchmark、manual grounded agent、scientific protocol code evaluation、skill retrieval no-skill evaluation 等，而非仅搜索已有 benchmark 名称。先用网页论文检索发现线索，再追官方仓库、数据发布页、相关工作和评价代码。

追踪路线包括：科学数据工作流论文 → SciDataBench → ScienceAgentBench/科学 Agent 相关资源；政策控制 → CAR-bench 及其模拟环境/评分；Skill 选择 → SkillFlow 的原始排除表与使用分析；文档生成代码 → GitChameleon、ExploraCoder、PBTbench；长文档操作 → MAGE、HANDBOOK。没有把新项目数量作为检索成功指标。CAR、SciDataBench 证据不足即停留在线索级，不凭题名升级。

实际检索返回与链接保存在 [search_log.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/search_log.json>)。本次无可调用的专用学术 MCP；OpenAlex 请求遇 HTTP 429，改用网页检索及作者官方材料。部分下载遇 TLS EOF，重试后取得 ScienceAgentBench 的 verified parquet、代码、仓库身份及 SkillFlow 的相关脚本；SciDataBench OpenReview PDF 遇页面挑战，未绕过，也未把搜索摘要当成已读全文。故这是有审计轨迹的开放式发现，不是声称穷尽所有公开资源的系统综述。

### 2.3 候选来源分类

| 类别 | 项目 | 本轮处理 |
|---|---|---|
| 用户历史已提及 | ConditionalQA、SOPBench、AppWorld、Terminal-Bench、CL-Bench、τ-bench、RoTBench、SkillGenBench、SkillsBench、Agent-Diff、RuleArena | 同一准入标准；不因知名度或已有工程优先 |
| 前序自主发现，本轮复查原始材料 | GitChameleon、MAGE、HANDBOOK、PBTbench、ExploraCoder、GDPevo、chi-bench、SkillScriptBench；τ² 的 banking_knowledge 新资源分支 | 区分数据规模、具体样例和未证实部分；共享规则不足不再是排除理由 |
| 本轮新增并取得原始数据/分析代码 | ScienceAgentBench；SkillFlow（IBPA/skill-flow，检索系统） | 前者实际读 102 行 parquet；后者读排除和 Skill 使用分析脚本，作为方法证据 |
| 本轮新增但未取得足够原始材料 | CAR-bench、SciDataBench | 保留为候选线索，UNVERIFIED，不推荐进入实验 |

“新发现”指相对于用户最初提供名单；其中有的已在前序审计中发现，本报告不把它们重新包装成今日首次发现。

## 3. 当前工程核查：不能把历史计划当成已实现能力

### 3.1 工作树与运行状态

**原始观察，VERIFIED。** 当前项目 HEAD 为 `a379e54e1233bd3f3011869f70eaf7fed8762982`。已有 `.idea/vcs.xml` 修改、暂存的 `DATASET_AND_TASK_SELECTION_AUDIT.md` 和两份未跟踪研究报告均保留。不是干净工作树，不能宣称已在某历史 HEAD 上完整复现。代码位置和函数索引见 [current_framework_snapshot.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/current_framework_snapshot.json>)。

`runner.lock.json` 固定 Harbor **0.24.0**、commit **2de4605b9404eada7d341388291e6e469c90330b**，使用原版 Terminus-2；本轮逐一重新计算锁文件列出的 **12 个官方文件 SHA256，全部一致**。这是源代码一致性证据。lock 的 `allow_model_execution=false`、`model_config=null` 是配置现状，不能据此否认历史显式授权启动器已跑过的 Gold。

**当前运行可用性，FAILED。** 只读 `docker inspect` / `docker image inspect` 均因 `dockerDesktopLinuxEngine` 命名管道不存在而退出 1。没有启动 Docker、拉镜像、建容器或修 Runner。镜像是否仍完整存在、容器能否重置均不能确认。[runtime_probe.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/runtime_probe.json>)。该失败是当前基础设施条件，不是数据集科学适用性判定。

### 3.2 现有组件能做什么

| 原始代码位置 | 已核验的能力 | 不应外推的能力/最小适配 |
|---|---|---|
| [runner.lock.json](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/configs/runner.lock.json>)；[harbor_adapter.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/harbor_adapter.py:20>) | 固定官方实现、哈希检查、官方解析器接入、内存中的 CRLF 兼容 | 不证明任意任务镜像能运行；不改官方 Runner |
| [p1.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/p1.py:126>) | 准备 Git restore 任务，按既有 arm 安装 Skill | 直接导入 Git fixture/Oracle；0/14/1 包数量与实验身份专用；没有通用 DirectDoc arm |
| [skill_install.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/skill_install.py:17>) | 校验 canonical/注册/export ID 和包内文件哈希，完整复制包 | 可复用完整包安装；不得只复制 SKILL.md、手工重写官方产物或沿用 14 包假设 |
| [p1_observer.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py:23>) | 核心路径 ACCESS 事件；检查终端观察中完整 Skill 正文；setup 隔离检查 | 只覆盖特定 SKILL.md 路径；不等于读完、理解或采纳；缺 DirectDoc、部分读取、资源/脚本的通用记录 |
| [request_budget.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py:140>) | 请求发出前事务预留；持久化门禁、owner lease、未知结果按消耗处理、不自动重试 | 数据库路径、Gold→A0→A1 顺序、6/18 次限制、模型 wire 参数及停止条件带实验专用假设 |
| [verify.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/git_restore_explicit_source_both_v1/tests/verify.py>)；[oracle.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/git_restore_explicit_source_both_v1/oracle.py:90>) | separate verifier；可信参考状态与导出 artifact 比较；9 个 Git 断言；拒绝部分路径/大小异常 | Git index/对象状态判分不能复用到 Python/API 业务目标；需要独立新测试或状态断言 |

现有 Git Oracle 不在 Agent 可控仓库中执行 Git 命令来信任其自述，而检查受限 artifacts；文件 8 MB、总量 32 MB、1000 项上限以及索引解析是任务专用保护。Python 任务应在独立 verifier 中执行提交代码与隐藏测试，隔离网络、进程和资源；不能照搬“只读数据”威胁模型。Box 则必须由可信服务导出前后状态，不能信任 Agent 自写的数据库快照。

### 3.3 最易误读的 arm 名称与 Gold 结果

| 历史代码中的名称 | 实际内容 | 与本轮定义的关系 |
|---|---|---|
| old A0 | 无 Skill | 大致对应新 A0，但任务、模型、预算不同 |
| old A1 | 安装 14 个生成 Skill | 对应新 A2 的类别；**不是 DirectDoc** |
| Gold | 安装 1 个人工 Skill | 仅 Git 工程校准，不能冒充新数据的 A3 |

重新读取 `runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001`：`Gold-continuation.json` 为 infra_ok=true、task_success=true、skill_read=false、reward=1、9 项断言均真；`http-budget-ledger.json` 记 Gold=2、A0=0、A1=0，Gold STOPPED，halt=`TRIAL_STOP_CONDITION`，两次 HTTP 200，输入 2227、输出 528 token，实际费用 UNKNOWN。这里是**已保存审计快照**，当前 Docker 不可用，未再读取 Linux volume 中权威账本。历史报告的旧 HEAD 不等于本轮工作树。

结论：终态正确并不能证明读过或采用 Skill。索引 description 也可能暴露规则。`finish` 将 Gold 的正文读取当后续实验门禁，是旧工程策略；不得变成新数据“参考 Skill 没读即任务无解”的定义。零模型 `cat` 探针仅证明可见性，也不能当自然读取。

### 3.4 现有 qsv 与模型预算

qsv select/sort manifest 固定 `257ae7b38738688138dc430c2ccb4eef8766f3fc`，来源哈希实测匹配，MIT；已有 generation case 与转换/生成资产。当前 downstream/tasks 中正式任务是 Git restore；没有因 qsv 文件存在就获得一个已验收的 Agent 任务与独立 Oracle。qsv 可作为以后静态映射的候选，不默认当主数据。

历史 smoke 配置使用 `openai/gpt-5.4-mini-2026-03-17` 经既有网关，temperature=0、reasoning=none、单 arm 最多 6 请求、单请求 2048 输出/20000 输入、arm 100000 输入、Agent 300 s、请求 45 s、retry=0。这些是**原文件配置值，不是本轮模型可用性或能力测试**。同一小预算不能直接照搬到长手册/训练模型任务。后续须新实验身份、新账本与明确模型预算；不重置旧账本、不绕过停止条件，也不自动延续历史付费授权。

## 4. 统一候选比较：分别判断源、任务和 Oracle

准入的对象是“版本化文档包 + 具体任务 + 环境 + Oracle”，不是 benchmark 名称。静态准入要求正文可得、规则能定位、任务确实要求相关行为、存在正确实现与独立可验收结果、没有无法消除的泄漏。A0/A1/A3 用于设计校准；A2 是待研究的结果，不能作为筛选变量。规则共享是额外属性。

| 资源 | Source Document | 执行任务/Oracle 原始观察 | 当前决策与证据状态 |
|---|---|---|---|
| GitChameleon + 版本官方文档 | 库文档/源码 docstring 真实；数据里的 docs URL 有漂移/不匹配，需补固定正文 | 328 任务、26 库标签；原始起始代码、版本、visible/hidden pytest；API 数不等于动作难度 | 主候选，PARTIALLY VERIFIED；不直接纳入全部 328 |
| Agent-Diff + Box | Box 官方 OpenAPI 可固定；随 benchmark 简化文档与官方有差异 | 状态服务与任务 CSV 可得；131/141 的断言不足以保证正确关联/全集 | 唯一备选；格式覆盖与原目标 Oracle 的检查 FAILED，需适配后再议 |
| MAGE | LibreOffice Calc 7.1 手册抽取 536 节；存在页面重叠 | 47 Calc 任务，OSWorld GUI 配置与导出后 compare_table；样例部分规则未能对应手册 | PARTIALLY VERIFIED；长手册研究价值高，当前非首选，不因缺 2+1 排除 |
| HANDBOOK | 实际取得 3 份长 HTML SOP；专家构造的虚构组织，不是真实公司规章的自然采样 | 3 个公开任务包及 rubric；一个 HR criterion 有空值误通过反例 | 长文档可得 VERIFIED，完整可靠 Oracle 尚不足；不是缺共享任务而淘汰 |
| τ² banking_knowledge | docs 与 required-doc 标识明确，但政策/任务有生成过程 | 97 题，90 有 assistant gold action，7 仅 user action；88 DB/9 ACTION；可复放目标状态 | 规则执行机制候选 PARTIALLY VERIFIED；不支撑自然来源代表性，不直接取代主方案 |
| ScienceAgentBench（新增） | 公开 domain_knowledge 是人工知识提示，非完整论文正文 | verified parquet 102 题；参考程序和逐题 evaluator 在另发包，未下载；部分图形评分调用模型 | 原始标注 VERIFIED；本研究完整链路 PARTIALLY VERIFIED，暂缓 |
| ExploraCoder | API 文档与多 API 程序任务有关系，需版本固定 | Torchdata Manual task_2 原测试可被假常量输出通过 | 样例 Oracle FAILED；不能凭“调用 API 多”当主实验 |
| PBTbench | 125 个 docs 文件、40 库、100 problem.yaml；部分所谓官方正文是整理文本 | bug/fixed 双环境测试有价值；bidict 文档混淆赋值与 put 的重复规则 | 源规则真值存在反例，PARTIALLY VERIFIED；先纠正文档来源再谈干净退化 |
| GDPevo | 已读 group001 policy，只有有限结构化约束 | 官方树 24 组/240 任务；实际检查 group001 为 read_only，输出计划 JSON | 该组不能支持真实业务写状态终点；不外推所有组均如此 |
| chi-bench | 源材料获取受限 | 官方仓库说明不能替代未得任务/文档 | UNVERIFIED，访问阻断，不纳入 |
| SkillScriptBench | Skill/脚本及第三方资源组合 | 许可与原始文档可追踪性未整体证明 | PARTIALLY VERIFIED，不能当统一自然文档数据集 |
| ConditionalQA | 652 GOV.UK 来源块文档；政策条件丰富 | train+dev 2623 标签题，613 含条件；文本/条件答案评分，非环境执行 | 自然政策与知识保真辅助可用；不作当前执行主集 |
| SOPBench | 程序规则生成的 SOP 与每任务参数 | 8307 任务；约束可覆盖默认值；重放一致性不能保证用户目标 | 来源代表性和目标 Oracle 不合格于原样主实验；不因任务数大通过 |
| AppWorld / Terminal-Bench | 提供执行任务不意味着每题自带可固定源文档真值 | 可提供环境和结果测试，仍需逐题文档映射 | 环境资源候选，不单靠 Docker 便利升级；本轮未做全量重新审计 |
| CL-Bench / RuleArena / RoTBench | 规则/上下文任务可研究知识利用 | 不自动具备本项目要求的动作、状态、副作用 Oracle | 保留相邻方法价值；不声称所有题都不适合，也无本项目 A0 实测 |
| SkillsBench / SkillGenBench / SkillFlow | Skill 包或提取评测资源，不等于同源退化数据真值 | 可借使用对照、任务隔离、错误/成本分析协议 | 方法参考；不能用已有 Skill 反推未经提供的原始来源 |
| CAR-bench（新增） | 汽车政策/场景文件的真实来源与固定正文未完成核验 | 作者 README 报告 254 题及动作/满意度混合评价；未取得固定 raw 样本 | UNVERIFIED，不作已通过候选 |
| SciDataBench（新增） | 科学数据 API/流程线索 | 论文检索页描述 300 场景、1200 checkpoints；正文/代码未充分取得 | UNVERIFIED；该数字是检索线索，未当本地可用规模 |

**通过状态须分开报告：**进入“进一步可行性核验”的主候选 1、备选 1；已经通过全部静态、环境、A0/A1/A3 和正式冻结审查的候选 **0**。排除只是针对当前研究用途或具体样例；不宣称 benchmark 总体没有研究价值。

## 5. 主方案的原始任务、来源与规则映射

### 5.1 GitChameleon 到底提供什么

原始仓库 [GitChameleonBenchmark](https://github.com/mrcabbage972/GitChameleonBenchmark/tree/3a1b6045a6b2a276bd24d715589cb041f8eccb93)，Apache-2.0。实际读取 `dataset/dataset.jsonl`、visible/hidden tests、`gitchameleon/eval_sample.py`。数据记录包含 `python_version`、`library`、`version`、`problem`、`starting_code`、`example_id`、`type_of_change`、`name_of_class_or_func`、`additional_dependencies`、`functional`、`webdev`、`solution_api_call`、`api_calls`、`release_date`、`docs` 等字段；原始样例投影见附录，不把中文解释冒充 JSON。

`docs` 是 URL 列表，不是已经冻结的完整正文。144 的链接混有历史镜像和 stable changelog，164 的 NumPy 链接路径指向 2.2 release 页面；题目要求 Flask 3.0.0/NumPy 1.25.1，不能直接下载 today/stable 当同版本真值。`name_of_class_or_func=app.json_encoder` 是变化主题元数据，不是 Flask 3.0.0 中可用 API 的证明。`functional`/`webdev` 是原始标签，不能擅自把 functional=0 解读为“任务无正确答案”。

**拟输入源**是开发者原始版本 docstring/文档页，而非题目/测试/参考解。已取 Flask 3.0.0 的 `src/flask/json/provider.py`、`src/flask/sansio/app.py` 并机械抽取文档字符串为 Markdown，保留标题和次序。tag 身份 `735a4701d6d5e848241e7d7535db898efb62d400` 已记录；尚不把未明确 peel 的 tag 对象说成已核实的 commit。原始文件与抽取文本均有哈希，可重建。Flask 文档/代码遵循其 [BSD-3-Clause 来源许可](https://raw.githubusercontent.com/pallets/flask/3.0.0/LICENSE.rst)，不能因 benchmark Apache 许可就覆盖上游文档许可。[官方版本源](https://github.com/pallets/flask/tree/3.0.0/src/flask)。正式冻结还需把所有选题的文档、版本、许可逐项入 manifest。

### 5.2 两个独立可入选任务，不是强制 2+1

| 映射项 | 144：已有 Flask app 的集合 JSON | 164：NumPy 数组去重、保留每个 NaN |
|---|---|---|
| 初始条件 | Python 3.10、Flask 3.0.0；starter 已构造 app 并定义 data/eval；补 app_set_up | 同版本 Flask，加 NumPy 1.25.1；starter 已给 DefaultJSONProvider 子类和 default 签名 |
| 用户要求 | 集合编码成排序后的 list；不启动 Web 服务 | unique 数值但每个 NaN 作为不同值；完成 app 配置；不启动服务 |
| 主要来源证据 | provider.py 约 27 行描述 provider 扩展及 app.json 实例；sansio/app.py 约 327–334 行在初始化构造 provider，并允许之后替换实例 | 共享 Flask 注册事实；另需 NumPy 1.25.1 unique 的 equal_nan 参数真值，不能只凭 Flask 段落覆盖全部需求 |
| 关键前提/范围 | app 已经创建；仅改类级 provider 配置不必然更新已有 app.json；自定义 default 处理目标类型，其他类型沿原行为 | 已创建 app 的 provider 注册；目标对象为 ndarray；NaN 去重语义与普通值不同 |
| 正确行为的可观察结果 | 请求上下文返回可解析 JSON，numbers 排序，保留其他可序列化类型行为 | 普通重复值去掉，多个 NaN 保留；非目标类型按约定处理；响应实际使用新 provider |
| 原 Oracle | hidden/visible pytest 检验函数输出 | 隐藏测试包含 unique 结果、两个 NaN、非数组异常等分支；不只看程序不报错 |
| 待加验收 | 证明旧属性/只改 class/常量答案不能过隐藏输入；合法实现均能过；禁止改 fixture/test | 分别构造 NaN 被合并、未装 provider、错误对象类型等独立错误；避免一个错误掩盖另一错误 |

证据位置：[provider 原文](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/extra/flask_3.0.0_provider.py:27>)、[app 原文](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/extra/flask_3.0.0_sansio_app.py:327>)、[144 隐藏测试](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/dataset/hidden_tests/test_sample_144.py>)、[164 隐藏测试](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/dataset/hidden_tests/test_sample_164.py>)。本轮未启动它们所需的固定版本 Python 环境，因此“参考实现能在当前机器正确执行”仍 UNVERIFIED。

**若破坏注册规则，可能发生什么？** 正确终态并不随退化改变。Agent 可能沿用被移除的 json_encoder，或只改 provider class 而保留旧实例，导致已有 app 的 JSON 请求仍失败。144、164 都可能受影响，但可以从源码内省、错误消息、其他文档段落或模型已有知识恢复，所以“必然失败”是错误断言。164 还可能先因 NumPy NaN 参数错而失败；必须分离故障类别。

**若仅破坏 equal_nan 规则，**144 不涉及 ndarray 去重，理论上不受该知识改变影响；164 可能合并 NaN。此关系适用于可选共享/特异性子研究，不能反过来要求每个来源必须有两个依赖题和第三个无关题。168 的 safe_join/stack 也可作可选负对照，但需独立固定 Werkzeug/NumPy 文档，不能以同属 Flask 数据标签就当成立。

### 5.3 简单任务风险不能靠数 API 解决

原数据 328 题中 213 题 `api_calls` 长度为 0 或 1，占 **64.94%**；该字段有 Python builtin 和辅助调用，不是 Agent 工具调用次数，也不是执行步数。144 的多项 api_calls 不代表高难度，164 starter 已泄漏 provider 选择线索。66 的 convolve 模式在任务中已明示，43 的特征数查询很短，208 的图形连线选项也可能属于熟知 API。它们适合标为低知识增益风险层，不能未测即宣称 A0=100%。

反向极端也不合理：若干高 API 数 Librosa 题要求在旧版本实现新 API，难点可能是算法重写而非从文档提取知识。以长代码、多工具调用、模型低通过率作为唯一选题指标，会把问题变成一般编程能力测试。

应按**规则新颖/版本特异性、例外、跨章节依赖、任务提示已泄漏多少、可执行语义难度**分层。一个任务只需一条关键规则也可入选。独立来源以库/发布机构及其版本谱系标注，同库不同页不是完全独立来源。207 个 docs URL 不是 207 篇已冻结独立文档。旧报告中 27 个“重复实体/版本任务”只是元数据分组，不是合格任务数量，更不能用 27/328 作为新设计可用率。

### 5.4 主方案尚缺的 Oracle 证明

官方 `eval_sample.py` 运行 pytest 并依据返回码判通过，这是功能输出检查，比工具轨迹重放更贴近目标。但返回码机制本身不证明测试充足，也不检查所有副作用。正式准入须逐题运行：可信参考解、空实现、常量输出、错误参数、错误版本 API、修改无关文件/测试等反例。隐藏测试只在 verifier 可见；benchmark 原目录、答案、solution、测试名中的解法提示不挂给 Agent。可保留双方一致的公开测试反馈，但不能 A1 看见隐藏失败详情、A2 看不见。

任务输入固定为目标描述、starter、必要数据和环境版本。输出是提交代码 artifact；不强迫使用某个 API 才算对。若存在合法无文档解，应由 A0/行为记录呈现，不人为写 Oracle 禁止它。

## 6. 备选与新增资源的实际样例及缺口

### 6.1 Agent-Diff + Box：业务状态链明确，但原 Oracle 不够

原始统计为 224 题：Slack 59、Box 48、Linear 57、Calendar 60，train/test=179/45；这是读取任务数据所得，不是全数审查通过。Box 随包文档 26 个操作条目，真实规则簇数未知。`tools_required` 重叠只表示使用同接口，不能证明同一条件规则。原始任务行包含 `#`、`question`、`answer`、`test_id`、`test_name`、`service`、`task_horizon`、`operation_type`、`entity_scope`、`information_availability`、`prompt_ambiguity`、`info`；其中 `answer`、`info` 是**字符串化 JSON**，不是原文件里直接嵌套的对象。附录保留这种类型。

`box_131` 让 Agent 建 Economic Data hub 并将既有 macroeconomics 文件夹加入；`box_141` 让 Agent 建 Model Evaluations hub，找出 agent-diff-research 内已有的模型评估 JSON 文件并加入。**141 不要求上传或新建这些文件**，纠正旧描述可能产生的误读。动作分别涉及建立 hub、查询内容、按类型引用正确 ID、在正确 hub 建关联，141 还需枚举和筛选完整集合。`task_horizon=3/4` 是元数据，实际请求数可能因搜索/分页不同。

官方来源不是 benchmark 的简化说明。固定 Box 规范 `a4f3e23d5bd01d9f4398bc1a764d410df3e607a7` 的 v2025.0 文件包含 `/hubs`、`/hubs/{hub_id}/manage_items`；基础 v2024.0 文件提供 `/folders` 等 API。相关证据链为：

`paths[...].post.requestBody → HubItemsManageRequest → operations.items → HubItemOperation → item → HubItemReference.oneOf → FileReference/FolderReference/WeblinkReference`。

关键规则：action 限 add/remove；item 的类型和 id 配对且元素必填；正确 hub_id 是路径参数；版本 header 有限定；parent_id 有局部作用范围。原 schema **没有把父级 operations 标成 required**，不能自行补出该约束。随包简化文档却有不同 required/type 集合；源规则、工具实际实现与预期行为必须先达成一致。创建 hub 的 title 描述“少于 50”和 schema maxLength=50 也存在边界差异，未定真值策略时不能选择 50 字符边界做退化靶点。

映射示例：若把 item 的 folder/file 类型错误编译，131 可能引用失败，141 可能混入错误对象；若丢失路径上的 hub_id 绑定，内容可加入错误 hub。正确结果需要新 hub 的 ID 与全部关联形成闭合关系，不能只找到两个彼此无关的新增行。工具错误信息和 JSON schema 也可能直接暴露正确规则，因此所有 arm 应使用同一工具接口，记录错误反馈；不能只给 Skill arm 删接口说明以制造依赖。

**原判分检查 FAILED，有实际反例。** 重新读取 [agentdiff_stats_and_probes.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/agentdiff_stats_and_probes.json>)：131 空状态增量不通过，但“文件夹关联到错误 hub”通过，“完成目标同时删无关数据”通过；141 “任意八个文件加到错误 hub”通过。以上为前序离线原 evaluator 反例，本轮未启动服务重跑。它们足以否定原样 Oracle，不足以断言每个 Agent-Diff 任务都有同样漏洞。

后续需要专用确定性断言：131 的 hub 精确名称/用户、目标 folder ID、item_type=folder、关联 hub_id 等于新 hub；141 的目标文件集合由可信初态计算，要求精确集合相等、无重复/漏项/额外项，全部指向新 hub；两题检查允许的状态 delta，拒绝无关删除/权限变化。原 diff 引擎、seed/reset 和 API 服务可复用；不能将通用“added 行存在”误认为用户目标已完成。与 Harbor 接入时由服务在 Agent 权限之外导出状态；verifier 读取可信导出，不执行 Agent 自报轨迹。

### 6.2 ScienceAgentBench：本轮新增的原始数据审查

[官方论文](https://arxiv.org/abs/2410.05080)、[固定代码](https://github.com/OSU-NLP-Group/ScienceAgentBench/tree/c26e151ed601ba109dc4d35e057ff8e73fec469d)、[固定数据发布](https://huggingface.co/datasets/osunlp/ScienceAgentBench/tree/9c6e96c9e74572e979b0930ee735041cef528cb7)。实际读取 verified parquet：**102 行、12 字段、4 域、30 个 github_name 标签**；心理/认知 28、地理信息 27、生信 27、计算化学 20。作者报告来源于 44 篇论文；本轮没有取得 44 篇可直接输入生成器的全文，30 个仓库标签也不是 30 篇独立源文档。

真实 instance_id=1 指向 deepchem/deepchem 的 examples/clintox，任务要求训练多任务模型并输出带 SMILES 和预测概率的 CSV；`gold_program_name=clintox_nn.py`、`output_fname=pred_results/clintox_test_pred.csv`、`eval_script_name=clintox_nn_eval.py`。`domain_knowledge` 指明两项预测任务和 ECFP 表征，属于整理后的专家提示；不能把它当论文原文或程序真实运行轨迹。完整字段投影见附录。

原始观察：`domain_knowledge` 字符数最小 0、中位数 524、最大 1753。**这些不是源文档长度。** `dataset_folder_tree` 和 `dataset_preview` 是初始数据说明，`src_file_or_path` 是出处线索，gold/eval 文件名是 verifier 资源索引，不能送给生成器补充答案。

已读 `run_eval.py` 和 `gpt4_visual_judge.py`：执行后评分，部分图形调用 GPT-4o，并存在动态依赖处理。未下载完整 `benchmark_verified.zip`，未取得本例逐题 evaluator、输入数据和参考程序，故不能判断其数值阈值、训练随机性、伪输出抗性。作者 README 说明 2026-04-30 verified 更新修正评价假阴性，提示不能混用旧标注/新 evaluator。代码 MIT，任务多数 CC-BY-4.0，列出的 rasterio/matminer 来源另遵各自许可；发布方要求不在线重分发解压数据。

设计判断：它值得考虑“科学知识到代码”的后续外部研究，但与本轮两题 API 文档相比，增加训练随机性、运算预算、逐题依赖和部分模型判分。缺完整源文档映射及独立 Oracle，不能因为比简单 API 题难就优先。**难不等于文档依赖强。** 当前不列为第二备选。

### 6.3 MAGE、HANDBOOK、τ²：长手册/业务规则路线

**MAGE，PARTIALLY VERIFIED。** 已打开 Calc 任务 `4f07fbe9-70de-4927-a4d5-bb28bc12c52c` 原 JSON，`source` 指向用户提问，`config` 指定初始文件和应用，`evaluator` 指定产物/期望，`postconfig` 负责保存导出。任务是在文本拼接中保持固定小数显示；手册第 258 页 Text operators 能证明拼接语义，却尚未定位到本题完整数字格式规则。这里缺的是**该单任务的必要证据**，不是缺第二道共享题。compare_table 检查表格结果，不证明一定经 GUI 或某函数完成；如允许 Python 改文件，必须对所有 arm 同样允许。GUI 控制和应用镜像也超出现有终端任务已验证范围。[固定仓库](https://github.com/ku-autoai/MAGE/tree/eeebb0136524efae905469e6fe72de84d368aeb4)。代码 MIT、OSWorld 派生 Apache-2.0，手册许可另计；不可把仓库主许可套给整套手册。

**HANDBOOK，PARTIALLY VERIFIED。** 公开三题为 HR Crestwood University、Vanguard Shield Insurance、CareIG Pharmacy，实际文件包括长 HTML SOP、初始 workspace、工具服务与评分项。HR 样例检查员工/部门/校区等业务结果，一个 criterion 使用双向 substring 比较，空部门和空校区也得到通过。前序 [oracle_probes.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/oracle_probes.json>) 只证明这**一条** criterion 假阳性，不能说整个 HR 任务完全通过。原始三包共 51 判据，不能用 1/51 推断全集 Oracle 错误率。作者报告 65 任务/10 基础手册；公开仓库明确只有 3 样例。手册由专家改写行业规范、设定虚构组织及参数，代表长篇政策语言，但不是未加工企业自然文档样本。[固定仓库](https://github.com/surge-ai/handbook/tree/374bc876ba008169e0dc30c1a751859d525cedc4)。未联系作者，未假定能取得全量。

**τ² banking_knowledge，PARTIALLY VERIFIED。** `tasks.json` 中 task_001 的 Gold 信用卡场景可对应 required_documents，但其 gold 操作归 user；不能当 assistant 多步执行题。全 97 题有 7 题如此；90/97=92.78% 仅是含 assistant gold action 的比例，不是本研究合格比例。官方树 698 个 document JSON，本轮只有两份卡规则正文被实际下载；215 个被引用文档、156 个被多题引用都不是“真实共享规则数”。领域生成脚本显示结构化规则、自然语言政策、任务的生成过程。DB evaluator 由 gold 动作产生目标状态再比较，值得借用，但需核对权限、时间、拒绝任务和额外副作用。它很适合控制规则机制，不能冒称自然文档代表性。[固定仓库](https://github.com/sierra-research/tau2-bench/tree/57e54143025bec219b5726884651c98eede202e2)。

### 6.4 排除/待定样例为何没有优于主方案

ExploraCoder 的真实 Torchdata Manual task_2 涉及读 JSON、处理字段、shuffle/cache/batch；原测试只检查有限的数量与形状，常量假 pipe 在前序离线检查通过。本轮不因为它调用 API 多就接受。[论文](https://aclanthology.org/2025.acl-long.887/)、[固定仓库](https://github.com/greenlight2000/ExploraCoder/tree/2d869352cf72bb05858b69d8d67f446d97a07263)。顶层许可证未确认，不把公开访问等同授权再分发。

PBTbench 的真实 BIDC-002 `problem.yaml` 提供 library/version、scope、docs_provided、existing_tests 和 ground_truth/bugs。后两类含缺陷与修补，须隐藏。`docs/bidict_official.md` 对重复 key 的默认行为未区分 `__setitem__` 与 `put`，与 [bidict 0.23.1 原文](https://bidict.readthedocs.io/en/v0.23.1/basic-usage.html) 冲突；清洁来源自身已错，会污染“退化产生错误”的定义。可借其 buggy/fixed 双环境判据，不能原样接受整理稿。[固定仓库](https://github.com/ElliotXinqiWang/PBTbench/tree/cef1aa4b8205c91ad7f0b3c5274b37304ff88765)，代码 MIT、数据 CC-BY-4.0，上游另计。

CAR-bench 的官方 README 展示 task_id/persona/calendar_id/instruction/context_init_config/ground_truth_actions 等结构和 254 题规模，但本轮未取得固定 commit 的原始任务文件，**README 示例不是已核验 raw task JSON**；评价还混合动作目标与模型满意度。SciDataBench 尚停留论文发现线索。两者都不能以“论文说有政策/工具”直接通过。[CAR 官方仓库](https://github.com/CAR-bench/car-bench)、[SciDataBench 论文入口](https://openreview.net/pdf?id=nP3Ye4rlGD)。

ConditionalQA 和 SOPBench 没有因最新取消 2+1 而自动变为主选：前者仍以文本问答为终点，后者仍有程序生成政策、任务参数覆盖及重放 Oracle 问题。CQA 可独立向 Anything2Skill 仅提供来源块，屏蔽 question/answer/conditions/evidence 标签；但提炼政策 Markdown 是否形成可用操作 Skill，须实测而不是命名。官方答案评分不能判断 Skill 规则真假，仍需外部规则标注。两类数据的联合只能做两组不同机制的研究，不应宣称同一来源贯通自然政策和真实业务执行。

## 7. 真实源文档长度与 Anything2Skill 兼容性

### 7.1 计量边界

以下是文件正文的 Unicode 字符数，不是 task prompt 长度，不是 token 数。Markdown 字符数包括机械标题；HTML 同时报告原始 HTML 与去脚本样式后的文本。空白词数仅描述英文文本规模，不用于预算。规则密度需要人工规则原子标注，本轮未伪造“每千字规则数”。完整路径、SHA256、字节、行数和词数见 [source_lengths.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/source_lengths.json>)。

| 实际来源表示 | 字符数 | 章节/块观察 | 计量限制 |
|---|---:|---|---|
| Flask 3.0.0 provider docstrings→MD | 5,003 | 16 个 MD 标题；ingestor 15 节 | 官方源码文档字符串集合，不是整个 Flask 手册 |
| Flask 3.0.0 sansio app docstrings→MD | 17,484 | 29 标题；28 节 | 与 provider 同一库，不算两个独立发布机构 |
| Box v2025.0 原始 OpenAPI JSON | 255,158 | 24 paths | 完整该版本发布文件，不覆盖所有基础 API |
| Box base v2024.0 原始 JSON | 1,809,764 | 187 paths | $ref、重复 schema 不能当等量自然语言规则 |
| Box 两个 endpoint 请求契约诊断子集 | 7,613 | 4 标题；4 节 | 不是完整来源；缺响应/其他操作，不能偷换为完整主输入 |
| CQA paternity 来源块→MD | 7,761 | 24 MD 标题、222 行 | 保留来源块的表示，不是原 HTML 全站页面 |
| qsv select / sort | 4,738 / 5,271 | 7 / 6 标题 | 仅已有两个命令文档 |
| τ Gold / Silver 卡 JSON.content | 1,684 / 1,319 | 各 32 行 | 实际读了两份，不是 698 全文统计 |
| HANDBOOK HR | HTML 77,184；文本 62,064 | 88 HTML headings | 去标签计量不证明表格/列表语义转换正确 |
| HANDBOOK insurance | HTML 58,447；文本 49,475 | 48 headings | 同上 |
| HANDBOOK medical | HTML 59,445；文本 44,637 | 54 headings | 同上 |
| MAGE Calc section collection | 536 节文本总和 1,763,091 | 最长节 24,508；Text operators 1,935 | 页面重叠；不是完整手册去重长度，PDF 全文长度 UNVERIFIED |

这组长度证明候选覆盖短 API 说明、中型源码文档、长 SOP、超长结构化规范；不能据此宣称已覆盖足够独立自然文档或所有长度层的行为效应。主方案目前实读的两个来源都属于 Flask，规模远不足。

### 7.2 当前原版生成配置与实际流程

[deepseek_flash.json](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/generation/deepseek_flash.json>) 配置 recommended 提取、LLM outline、max_candidates_per_unit=4、max_units_per_document=0、单 worker、retry=1、6000 字符 chunk/300 overlap、max_section_chars=10000、hash embedding 256；模型配置的 max_input_chars=100000 字符、max_tokens=16384、150 HTTP/450000 token 上限仅是文件中的设置。本轮没有验证模型端支持值或调用它。

[file_loader.py](<D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/document/file_loader.py:185>) 能读文本/Markdown/JSON；JSON 被读成文本，并没有领域 JSON 自动理解保证；PDF 属已知二进制路径，不会自动得到可靠正文；Word 路径依赖外部转换器。HTML 读成字符串不等于层级、表格和链接已解析。OpenAPI $ref 也不会因后缀为 .json 自动完整解引用。

[pipeline.py](<D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/pipeline.py:324>) 的 ingest→extract→compile→register 为独立环节；支持材料/候选、编译 spec、注册/合并均可能改变最终产物。一次文档可产生多个 Skill；max_candidates 也不等于最终稳定包数。来源引用只能支持追溯，不能证明条件/例外在语义上保真。要固定生成器版本、配置、model identity、输入 manifest、独立输出命名空间，防止历史注册库/缓存跨 clean/degraded 合并。这里是后续运行协议，不是本轮改造代码。

### 7.3 无模型加载和窗口结果

本轮使用原版 loader/ingestor/recommended windowing，**显式 rule-only outline**；Python audit hook 阻止 socket、DNS 和 subprocess，未调用 extraction/compile/register，也未改源文件。这只检查确定性前端，不能冒充配置中 LLM outline 的完整生成。

| 输入 | 文档/节 | 窗口数 | 最大窗口字符 | 判断 |
|---|---:|---:|---:|---|
| Flask provider | 1 / 15 | 3 | 2,372 | app.json 实例规则锚点进入 window 0，VERIFIED；完整规则语义仍待人工核对 |
| Flask app | 1 / 28 | 6 | 2,394 | 构造后替换/子类配置锚点进入 window 1，VERIFIED |
| Box 契约子集 | 1 / 4 | 1 | 356 | 文件加载成功，但契约正文覆盖严重不足，FAILED 于此表示的规则覆盖 |
| qsv select | 1 / 7 | 2 | 2,356 | 加载 VERIFIED，未证明每个参数规则覆盖 |
| qsv sort | 1 / 6 | 1 | 1,277 | 同上；不可只看无异常 |

原代码 [windowing.py:270](<D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/document/windowing.py:270>) 的段落筛选与 process/anchor/noise 启发式会排除一部分长段，长 JSON/契约声明尤其敏感。2400 左右是窗口规划目标，不是模型最大上下文。Box 前序完整 marker 探针也显示 operations/action/oneOf 等关键内容未覆盖；本轮 356 字符结果复现了这一结构现象。[本轮探针](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/current_load_probe.json>)、[前序 Box marker 探针](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/generator/box_probe_results.json>)。

### 7.4 什么可适配，什么属于方法不匹配

机械格式适配可以做：按原顺序抽 docstring/HTML 块，保留标题、表格表头、作用域、脚注和稳定证据 ID；解引用 OpenAPI 时保留 required 所在层级、oneOf 分支、版本与原指针；将 PDF 转换结果与页面对照。不能让模型先改写成任务解法再称原始来源。若要靠人工重写为操作流程才能进入窗口，应单列“重写后的输入”及成本，不伪称原版生成器直接适用。

输入给 A2S 必须仅有源正文和来源元数据；不能含题目、答案、hidden tests 或失败反馈。DirectDoc 使用**同一冻结的转换表示**；另测原格式阅读可作为次要生态效度实验。若 A1 看完整 HTML，A2 只看精简契约，差异混合了预处理损失，不能归因于 Skill 编译。

Flask 文档可以合理编译为“识别版本/生命周期→选择 provider 扩展→处理类型及回退→验证响应”的可复用指南；是否真被编成这种 Skill 尚 UNVERIFIED。CQA 更可能产出政策条件整理：即使仅是知识重述，也能研究压缩/提取保真，但只靠答案评分不足以主张 Agent 程序技能。若主方案 A2 普遍只改排版，报告方法边界，不能人工补步骤后将其算作官方效果。

**重要区分：**源正文/版本不可信、环境与 Oracle 不一致可在 A2 前排除；原版生成器漏规则、零 Skill、编译失败则是研究结果。可以据预定义的输入范围研究适配问题，但不得看过 A2 后静默丢弃这些失败任务。

## 8. 借鉴 Skill 研究的评测协议，但不照搬其选样目标

| 实际查看的工作/资源 | 对方协议或原始证据 | 本研究可借鉴与不可照搬 |
|---|---|---|
| SkillsBench [论文 v4](https://arxiv.org/html/2602.12670v4)、[贡献规范](https://github.com/benchflow-ai/skillsbench/blob/main/CONTRIBUTING.md) | 任务目标与步骤分离，Skill 面向任务类，配无 Skill/人工 Skill/自生成 Skill；jax 样例按数值产物评分 | 借独立终态测试、按需读取和答案隔离；无 Skill 能解不自动淘汰。已读网页代码未固定 commit，不能当已冻结任务集 |
| SkillRefine/PIMS-Bench [论文 v1](https://arxiv.org/html/2609.30674v1) | 作者报告 140 专家任务，40 构建/修订、100 留出；DocOnly/技能条件，COM/solver 与单元格匹配 | 借构建/留出隔离与真实状态目标；其专家轨迹和反馈修订不是本项目纯文档原版 A2S；任务包及授权环境未取得 |
| Agent Skills Can Be Harmful [论文 v1](https://arxiv.org/html/2608.11888v1) | 同任务不同 Skill/无 Skill 差分，精选失败/成本回退案例，成功参考轨迹用于定位 | 借失败分类；精选失败集不能估计总体退化风险，不能仅保留 clean pass/degraded fail |
| MAGE [官方方法代码](https://github.com/ku-autoai/MAGE/tree/eeebb0136524efae905469e6fe72de84d368aeb4/components/rap) | 手册检索用于规划，并有手册覆盖/版本等对照材料 | 借原始文档对照和任务知识映射；按任务检索规划不等同预先冻结通用 Skill |
| SkillFlow [固定仓库](https://github.com/IBPA/skill-flow/tree/6c2402deed3bf57e5f26ea77da48825d0f45dcfa) | 实际 AST 读取排除表：23 项，16 Infrastructure、6 Reproducibility、1 Resource；使用分析区分 no-skill、load 与 helped/hurt/tie | 借基础设施失效与方法失效分开、使用与结果分开；不能推断其完整筛选都无偏，不能把市场约 35K Skill 当 35K 独立源文档 |

SkillFlow 指 IBPA 的检索系统，不是其他同名 lifelong 项目。以上论文成绩没有在本项目复现。曾有“按 clean Skill 成功阈值选题”的建议不适用于本研究；也不采用统一 90%/40% 通过率门槛。我们研究的正是原版生成器可能失败的输入，按 A2 表现挑题会削弱可解释性。

任务太简单的合理处理：先固定语义与版本层，再报告 A0；若 A0 很高但错误文档/Skill 仍会诱导错误，仍能研究**错误知识风险**，不能因无增益就删除。若所有 clean 条件都容易成功，则可靠性、读取成本或错误补偿可能有价值，但不能凭小样本无差异宣称“Skill 没用”。不允许为压低 A0 而给任务添加无关复杂度、私有暗号或强制点名读取文件。

## 9. A0—A3 校准、准入与防选择偏差

### 9.1 信息边界

以下是拟设计协议，尚未执行；本轮基线成功率全部 **UNVERIFIED**。

| 条件 | Agent 可见 | 不能混入 | 用途 |
|---|---|---|---|
| A0 Task-only | 任务、starter/初态、必要版本、共同工具与合法错误反馈 | 额外源文档、Skill、隐藏答案/测试 | 测已有知识与环境可推导能力，不等于“无一切知识” |
| A1 DirectDoc-Clean | A0 + 干净、冻结的源文档及中性索引，按需读取 | 生成 Skill、任务特定参考解 | 测文档能否改善正确知识利用，是核心比较条件 |
| A2 Skill-Clean | A0 + 原版 A2S 从相同来源预先生成并冻结的完整 Skill 包，原生索引 | 另附原文、人工补正、题目/Oracle 反馈修订 | 评价生成器及使用链；结果不参与任务准入 |
| A3 Reference-Skill | A0 + 人工核验、仅含任务类知识的正确参考 Skill | 标准答案、隐藏测试、特定输入输出、从 A2 失败逆向定制的解题稿 | 设计阶段验证知识可表述、Agent/环境可解；不作为 A2 成绩 |

原版包的 frontmatter、resources、scripts 均需保留并记录。若生成包合法包含来源引用或全文附属资源，不能偷偷删除后仍称原版包；记录这条暴露通道，将其作为该生成器的真实行为解释。A2 不另外人为挂载源文档。

索引访问、description 可见、正文部分可见、全文可见、资源/脚本访问分开记录。A1 中性目录给出的标题/摘要长度与 A2 索引暴露并不天然相同；主比较保留各路径真实行为并测量暴露，必要时另做长度匹配诊断，不改官方 Skill 伪造公平。A0 仍可使用所有 arm 共同可用的库内省、help、源码与错误信息；这些是合法补偿渠道。外网若关闭，对所有条件一致关闭，不针对一个条件限制替代知识。

### 9.2 校准决策矩阵

| 观察情况 | 先判断什么 | 允许的决定 |
|---|---|---|
| A0 高，A1/A3 也高 | 文档是否有额外知识效应；知识是否早被 starter/接口透露 | 标为高基线层；可保留研究错误诱导/补偿，不自动删 |
| A0 低，A1/A3 高 | 文档知识与表示形式是否支持行为 | 优先进入知识依赖层；最终资格由预定义规则决定，不看 A2 |
| A1 高、A2 低 | 生成遗漏/失真、发现失败、包预算、正文读取 | 保留并分类，这是关键研究结果 |
| A1 低、A3 高 | 文档长度/查找难度、原始表示、参考 Skill 是否泄漏答案 | 若 A3 无泄漏，可研究组织/检索作用；不当作生成器已解决 |
| A0/A1/A3 全低 | 可信参考解、镜像依赖、工具、任务歧义、Oracle、预算 | 停止解释 Skill 效果；修任务/环境或说明模型能力边界 |
| A2 未生成 Skill/编译失败 | 请求失败与生成语义失败分开 | 计生成失败；预先规定下游空包处理或结构性缺失，不能默默排除 |
| A3 不读正文但任务成功 | 索引信息/已有知识/合法替代路径 | 可证明存在可解行为，不能证明采用参考 Skill，也不按旧 Gold 门禁判不可解 |

必须先用可信参考程序在固定环境通过测试，证明**存在正确路径**；A3 进一步观察目标 Agent 能否借助正确知识完成。这两层不同。A3 失败本身不能反证数学/程序意义上的不可解。

### 9.3 如何冻结，避免根据结果反向选题

先冻结静态候选池及纳入/排除原因；独立记录来源、规则、任务、Oracle 关系。用少量设计样本调预算/协议，设计样本不混进最终留出集。可依据预先规定的 A0/A1/A3 诊断设置难度层或限定研究人群，但须报告被筛掉数量、原因及筛选模型；不把“筛出来的知识依赖子集”代表原 benchmark 全体。对 A2 结果保持盲态，不能据其成功与否选择任务或拟定门槛。

无法盲态时，至少在看到 A2 前版本化记录候选清单、排除理由、阈值依据和统计方案；探索与验证数据分开。两题各 3 次只够排流程问题，不足以稳定估计成功率，不能把 2/3 或 3/3 当普适标准。后续样本量依据 pilot 方差、来源簇数量、预期可检测效应及预算计算；本轮不假装已经做过 power analysis。

## 10. 单一、外部验证与分层研究三种设计

| 方案 | 能回答什么 | 独立性/统计与代价 | 本轮建议 |
|---|---|---|---|
| A 单一 GitChameleon 筛选集 + 官方版本文档 | 版本化技术文档中的规则退化如何经过 A2S 影响代码任务；同题 DirectDoc 对比 | 26 库是候选上限；需实际冻结多个库/规则。两份 Flask 文件和重复运行不能当独立来源。文档转换与执行环境较同质 | **先采用**，承认范围窄；先可行性后定规模 |
| B 主集 + Agent-Diff/Box 外部验证 | 检查从编程规则到 API 状态任务是否也存在编译后风险 | 文档结构与环境同时变化，不能把两集平均差异归于“文档类型”；每集内部做 clean/degraded×路径，再比较方向和失败机制 | 不是现在必需；只有要扩展此类主张、且备选修复通过时采用 |
| C 多文档分层研究集 | 技术说明、结构化规范、长政策/手册的异质效应 | 每类型需多独立来源及规则；如一种类型只配一种执行器，类型与环境完全混淆；复杂度和标注成本显著增加 | 当前不推荐。MAGE/HANDBOOK 只作后续补充线索，不堆成“跨域大结论” |

单一数据集足够支持**边界明确**的问题，不要求题目种类无限多；但当前两题不足以支持总体结论。正式主集可先按 6–10 个库、20–30 个来源/规则单元、40–60 个任务的**规划范围**评估成本；这些不是已经找到的合格数量，也不是保证统计功效的下限。若实际只有一个库或两种规则可映射，应收缩为机制案例研究，不能靠加重复次数补“多来源”。

若组多个公开数据源，每道题必须仍保持自身 source→evidence→task→Oracle 闭环；不能用 CQA 的自然政策、SOPBench 的任意工具、AppWorld 的任意任务拼接成一条虚假的同源链。混合后源规则与环境不一致时，本质上是新构建任务，需要新的真值、Oracle 和来源声明。

## 11. 正式退化实验的拟设计与可识别结论

### 11.1 最小因素设计

对同一冻结来源、同一任务、同一执行器，预先指定三个源版本：Clean、目标规则相关退化、无关段落的匹配退化。每个源版本走 DirectDoc 和 Skill 两条路径，共 6 个条件；另保留 A0，A3 留在设计校准阶段。**本轮没有构造这些正式退化文本。**

初期可选规则原子删除、参数替换、条件/例外范围丢失、顺序或跨段引用损坏。退化强度按真实被改变的规则内容与字符量记录；无关扰动匹配长度/位置/格式，避免把“规则错”和“文件更短、更好检索”混在一起。Source 改变不改变任务真实目标、工具规则和 Oracle。否则只是换了一道题。

每一源版本在独立生成 run/注册命名空间产生冻结包，完整保留生成失败、包数、支撑材料、证据位置、合并轨迹和哈希。不能在执行时根据题目再生成或修 Skill；同包可供所有预先关联任务使用，不要求每个源必须两题。生成随机重复与执行随机重复分别记录，不能把后者误当多个独立生成样本。

### 11.2 指标必须覆盖三个环节

| 层 | 主要指标 | 不能代替什么 |
|---|---|---|
| Source→Skill | 目标规则召回/正确性；参数、前提、例外、范围错误；无依据指令；证据一致性；零产物/编译失败 | 来源引用存在不等于语义蕴含；需要双人独立规则标注与分歧裁决，先可在少量样本建立规范 |
| Skill→行为 | 包可发现、索引曝光、正文/资源实际可见、操作序列与关键参数、纠错反馈 | open/cat/access 只能证明暴露，不证明理解或采纳 |
| 行为→结果 | 独立 Oracle pass、分项目标、错误对象/漏操作/副作用、失败类型；请求/token/时间 | Agent 自述“完成”或 HTTP 200 不是成功；成本比较需区分双方均成功和总体意向分配 |

规则原子包括：前提、动作/结论、参数域、例外、适用对象/版本、证据区间。未出现例外时标“不适用”，不硬凑字段。人工标注不改 A2 产物；规则正确性与任务可解性分别打分，避免因任务成功而倒推 Skill 完全正确。

一个清晰的主效应是“退化相对 clean 的风险增量在两条路径间的差”：

`Δ = [失败率(Skill, 目标退化) − 失败率(Skill, Clean)] − [失败率(DirectDoc, 目标退化) − 失败率(DirectDoc, Clean)]`。

Δ>0 表示在所选任务、模型、预算和表示下，Skill 路径的退化风险增量更大；不自动证明是哪条错误被采用。还需无关退化比较和规则/动作证据。报告来源/规则簇层面的置信区间或分层模型，任务与生成重复嵌套其中；样本小则只报病例和不确定性，不用几十次重复冒充几十个独立来源。

### 11.3 五类失败如何区分

1. 源文档退化影响：DirectDoc-clean 与 DirectDoc-degraded 提供直接参照，但仍含 Agent 检索补偿。
2. 生成器提取/编译变化：对比输入规则与冻结 Skill 的人工语义标注，区分 clean 原有错误和退化增量。
3. 模型已有知识补偿：A0、正确替代 API、源码/帮助/错误反馈说明路径；不能只凭成功断言模型“记住”。
4. 未发现/未读/未用：记录暴露层级；未读也进入主统计，它是系统路径的结果。只分析读取成功者会造成处理后选择偏差。
5. 任务/环境/Oracle 失效：可信参考路径、固定镜像、独立验证与错误反例先通过；基础设施故障单列，不当技能语义错误。

可选因果诊断：在固定错误 Skill 中只修目标规则，配同长度 sham patch，观察动作与结果是否恢复；或者在正确参考 Skill 中只逆向破坏目标规则。该产物必须标为**干预诊断包**，不替代官方 A2 得分。必须控制 index、包名、资源、脚本和长度变化。共享规则多任务传播仅在完成各任务依赖证据和负对照后开展；基础研究无需 2+1。

## 12. 最小可行性计划、工程成本与停止条件

### 12.1 审核后才实施的步骤

| 阶段 | 具体内容 | 验收标准/停止条件 |
|---|---|---|
| 0 当前报告审阅 | 确认单一技术文档主张、两题设计样本、A0–A3 定义及独立预算范围 | 本轮在此结束；不启动 Docker/Agent/生成 |
| 1 无模型任务资格 | 固定 144/164 输入、Python 3.10/Flask 3.0.0/NumPy 1.25.1 与所有传递依赖；取得 NumPy 同版本正文；新 task package、source manifest、独立 verifier | 当前 Docker 需先恢复；参考实现重复正确，空解/常量/旧 API/NaN 错误均被拒；测试与答案不可见。失败则停止进入模型阶段 |
| 2 文档/参考 Skill 资格 | 完整源表示与证据 ID，人工逐原子核对；独立编写 Reference-Skill，不看 A2 输出补答案 | 目标规则真值/作用域无未解冲突；reference 不含具体输入答案；格式转换不改变条件。缺证据就继续补，不用付费生成探路 |
| 3 设计校准 | 两题各 A0/A1/A3，建议每条件 3 次诊断运行；固定模型/工具/预算 | 18 个 Agent episode 的规划，不等于 18 次 HTTP。按 §9 诊断，不设机械成功率阈值；预算耗尽即停 |
| 4 原版 clean A2 | 从相同源预先生成并冻结包，两题各 3 次；记录生成失败和内容错误 | 再 6 个 episode，合计 24；生成请求另外预算。A2 不改变准入名单；完全空包也有预先定义结果处理 |
| 5 扩展/冻结 | 在不看 A2 成败的筛选规则下扩展库/规则；设计样本与留出分开；估算统计功效 | 独立来源不足则只做机制研究；预算/人工标注不足则缩范围，不宣称已冻结大样本 |
| 6 正式退化 | 完整 2 路径×3 源条件、预注册指标与重复；可选修复诊断 | 另行审核正式实验范围。本轮不启动 |

144 已具备 Flask 原始证据，164 的 NumPy 特异规则完整同版本正文仍须入包；该未完成项不可被“以前知道 equal_nan”替代。两题同库，适合检查实验能否识别行为，不足以验证跨库泛化。若发现 144/164 都强天花板，不即时手改题目迫使读 Skill；先按预定义分层选择其他有更强版本/例外依赖的原始任务，并保留首批结果。若整个主候选缺少知识效应或来源覆盖，再触发备选。

### 12.2 最小工程变化，保持官方 Anything2Skill 和 Runner 原样

可复用：固定 Harbor/Terminus-2 接口、完整包 hash 安装、trial artifacts、separate verifier 模式、请求预留账本机制与日志脱敏。必须新增/适配：来源 manifest 与机械格式转换、通用 A0/A1/A2/A3 数据挂载、Doc/Skill 暴露记录、新任务 adapter/可信 Oracle、独立实验身份/预算配置。不能只改 arm 标签继续用旧 Git fixture 和 Gold 读取门禁。

任务镜像与控制镜像不同：GitChameleon 题目要求 Python 3.10，而现有控制层要求较新 Python；可保持控制 Runner 版本，单独固定任务镜像，不能通过升级题目依赖去“兼容”旧镜像从而改变真值。是否更换模型须在 A0/A1/A3 校准后基于预算和可解性决定；不是默认升级模型。Box 若转入，需要可重置服务、可信状态导出与 API/官方文档差异表，成本高于纯代码题。

**粗略工程规划，不是已完成或报价：**在 Docker/基础镜像正常且两题依赖可离线冻结的前提下，主方案两题适配、Oracle 反例和暴露记录约 2–4 人日；扩展到多个库的依赖锁定与逐规则人工标注需另计。Box 两题服务/状态隔离、目标断言、契约转换与一致性验收约 4–8 人日；复杂模拟服务或规格冲突会增加。MAGE 的 GUI 执行与长文档对齐成本更高，当前证据不足以可靠估时。模型额度和金额未估，因为配置、生成包数、请求长度与当前价格均未批准/验证。

### 12.3 停止与替换条件

- 当前 Docker 不可用：停止执行阶段，允许继续静态审计；不改数据选型来掩盖基础设施问题。
- 源版本/规则真值无法确定，或工具实现与来源冲突：暂停该任务，记录原因；不把冲突当 clean 文档。
- 参考程序失败、错误对象/副作用反例被接受、hidden test 泄漏：暂停该任务模型试验，先修资格。
- A0/A1/A3 都失败：排查环境、预算、工具、任务与模型能力；不归因 A2S。
- A2 失败：保留为结果，分析是哪一环；**不是删题或换集的自动条件**。
- 任务层面知识效应无法识别且可扩展来源过少：转 Agent-Diff+Box，前提是格式/实现/Oracle 三项先过。若两条路线都依赖大幅人工重写来源，承认当前原版 A2S 的输入适用边界，重新界定研究，不无限搜库直到碰巧成功。
- 未知请求状态、预算预留失败、重复请求风险、持久化门禁停止：立即停模型，不重试/重置旧账本。

## 13. 结论的证据强度与仍待确定事项

| 问题 | 现在可以回答 | 仍缺证据 |
|---|---|---|
| 优先用什么 | GitChameleon 的版本敏感原题 + 对应官方正文；先单一主集 | 全部候选来源固定、逐题 Oracle 和知识效应 |
| 为什么优于已核查其他候选 | 可定位真实开发规则、明确环境版本、实际提交程序、已有隐藏功能测试；比 QA 更有执行终点，比程序 SOP 更有自然来源，比 Box 少一层已证目标判分缺口 | 不代表任务足够难、生成质量已好或 Oracle 全部可靠 |
| 单一集是否够 | 对软件技术文档这一窄研究范围可以；当前两题本身不够 | 跨库来源数、规则层次和 power analysis |
| 是否立即加外部集 | 不需要。跨 API 状态泛化时才启用唯一备选 Box，并分别估效应 | 规格一致、窗口覆盖、可信终态 Oracle |
| Agent 是否需要 Skill | 未知。需要文档知识也不意味着必须用 Skill，DirectDoc 是核心对照 | A0/A1/A3 校准及 A2 行为记录 |
| 生成器能否稳定产规则 Skill | 离线加载仅证明部分锚点覆盖，不能证明稳定生成 | LLM outline、提取、编译、注册及完整包审计 |
| 当前工程能直接跑吗 | 官方源码哈希一致，历史 Git 校准存在 | 当前 Docker 连接失败；新任务 adapter/Doc arm 未实现 |
| 什么足以冻结 | 版本/许可/正文/规则映射齐全，可信参考与反例通过，模型预算固定，选择规则先于 A2，设计/留出分离 | 以上尚未全满足；本报告不授予实验执行许可 |

最终主张应随证据收缩：如果只能证明源退化导致 Skill 规则错误，尚无行为变化，就报告提取保真结果；若行为变化但不能归因采用错误规则，就报告路径风险，不声称错误传播因果已证；只有规则干预、暴露/动作证据与独立终态共同支持，才讨论错误被下游采用。一个负结果也可能回答研究问题，不能以生成器或 Agent 是否“表现好”决定数据是否值得研究。

## 14. 本轮执行记录与资源身份

实际无模型命令：`D:\anoconda1\python.exe -X utf8 audit_snapshot.py` 读取当前代码/配置、校验锁定官方文件并统计正文；`load_probe.py` 调用原 loader/ingestor、关闭模型/网络/子进程；`candidate_stats.py` 读取 ScienceAgentBench parquet、SkillFlow AST 排除表及完整 Box schema。脚本均在审计目录，正式工程代码未改。下载只是公开最小数据/代码；未导入 ScienceAgentBench evaluator、未执行安装依赖或调用图形 judge。

加载检查成功返回，不等于模型生成成功。Docker 三个只读 inspect 返回失败；网络中的 HTTP 429/TLS EOF/页面挑战记作访问限制，不抹去。保护清单只覆盖明确列出的 61 个工程/生成器源文件和历史审计账本文件，并不声称递归核验了整个磁盘。最终复核见 [protected_files_check.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/protected_files_check.json>)。

| 资源 | 固定身份与说明 |
|---|---|
| 当前 AutoSkill 项目 | `a379e54e1233bd3f3011869f70eaf7fed8762982`；工作树有已存在修改，不以 HEAD 代替所有文件哈希 |
| Harbor | `2de4605b9404eada7d341388291e6e469c90330b`；12 项锁定文件逐一核验 |
| GitChameleon | `3a1b6045a6b2a276bd24d715589cb041f8eccb93`；[论文](https://arxiv.org/abs/2507.12367) |
| Agent-Diff | `3bb9c40707df23d89e5dbc0e40c424ba38c69ff8`；[固定仓库](https://github.com/agent-diff-bench/agent-diff/tree/3bb9c40707df23d89e5dbc0e40c424ba38c69ff8)、[论文](https://arxiv.org/abs/2602.11224)；已读本地 LICENSE 为 MIT |
| Box OpenAPI | `a4f3e23d5bd01d9f4398bc1a764d410df3e607a7`；[官方规范](https://github.com/box/box-openapi/tree/a4f3e23d5bd01d9f4398bc1a764d410df3e607a7)；Apache-2.0 规范仓库 |
| MAGE | `eeebb0136524efae905469e6fe72de84d368aeb4`；来源混合许可分别核对 |
| τ² | `57e54143025bec219b5726884651c98eede202e2`；只对已读文件作判断 |
| HANDBOOK | `374bc876ba008169e0dc30c1a751859d525cedc4`；公开 3 样例，不是作者全量集 |
| GDPevo | `56d60ae4ae5e067d1ec0ee1f850622e69f422179`；[固定仓库](https://github.com/Prism-Shadow/GDPevo/tree/56d60ae4ae5e067d1ec0ee1f850622e69f422179) |
| ExploraCoder | `2d869352cf72bb05858b69d8d67f446d97a07263`；许可未确认 |
| PBTbench | `cef1aa4b8205c91ad7f0b3c5274b37304ff88765` |
| chi-bench | `4444a07fa68a4f1623f841a292a54e284fc8e7f7`；[官方仓库](https://github.com/actava-ai/chi-bench/tree/4444a07fa68a4f1623f841a292a54e284fc8e7f7)，代码 Apache-2.0，手册获取不足 |
| SkillScriptBench | `92cc92baea279d412fcfb1f8b1ef5a2238ff3b45`；[官方仓库](https://github.com/HKUST-KnowComp/SkillScriptBench/tree/92cc92baea279d412fcfb1f8b1ef5a2238ff3b45)，README 未给统一项目许可 |
| ScienceAgentBench | 代码 `c26e151ed601ba109dc4d35e057ff8e73fec469d`；HF `9c6e96c9e74572e979b0930ee735041cef528cb7`；verified parquet 129,086 bytes |
| SkillFlow | `6c2402deed3bf57e5f26ea77da48825d0f45dcfa`；[论文入口](https://openreview.net/forum?id=79D1g9mNrm)；代码 Apache-2.0，市场 Skill 各有来源权益 |

固定 commit 不等于已锁全部依赖、外部链接和数据资产。对仅访问 main 网页或无法取得原始数据的项目，上表不补造身份。后续任何正式实验都需自己的 manifest 与审计账本；不能拿本报告的检索快照当运行许可。


## 附录 A. 真实原始样例投影与字段用途

以下由脚本从本地固定原始副本提取。只保留列出的字段；未新增原始字段。除明确注明的 problem 连续前缀截断外，字段值不改写。中文解释在 JSON 外，不作为原始任务。完整任务/答案文件留在审计目录，不能原样送给生成器或 Agent。

### A.1 GitChameleon 144

来源：[gitchameleon_candidate_raw.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/gitchameleon_candidate_raw.json>)；上游 `dataset/dataset.jsonl` 的 example_id=144。`problem` 只展示原文前 20 个英文词的连续前缀，未补省略号为原字段值；任务余文、starter、答案/测试不在此投影中。

```json
{
  "example_id": "144",
  "python_version": "3.10",
  "library": "flask",
  "version": "3.0.0",
  "problem": "\nComplete the app_set_up function that set-up the app in such manner that the json encoding returns a sorted list\n when",
  "name_of_class_or_func": "app.json_encoder",
  "additional_dependencies": "",
  "docs": [
    "https://tedboy.github.io/flask/interface_api.json_support.html",
    "https://flask.palletsprojects.com/en/stable/changes/"
  ]
}
```

`example_id` 是记录标识；python_version/library/version 指定执行依赖；problem 是 Agent 目标；name_of_class_or_func 是变更主题元数据，不能当有效解法；additional_dependencies 为空不等于没有传递依赖；docs 是原始链接而非冻结正文。真实问题余文要求集合的 JSON 编码返回排序 list，并禁止启动 app。

### A.2 Agent-Diff box_131

来源：[agentdiff_raw_2plus1.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/agentdiff_raw_2plus1.json>)，是原始任务行的保留字段。`answer` 和 `info` 的转义字符串类型保留，没有伪造成嵌套原对象。

```json
{
  "test_id": "box_131",
  "question": "Create a Hub named 'Economic Data' and add the 'macroeconomics' folder to it.",
  "answer": "{\"assertions\":[{\"diff_type\":\"added\",\"entity\":\"box_hubs\",\"where\":{\"title\":{\"eq\":\"Economic Data\"}},\"expected_count\":1},{\"diff_type\":\"added\",\"entity\":\"box_hub_items\",\"where\":{\"item_id\":{\"eq\":\"1973339758\"}},\"expected_count\":1}],\"ignore_fields\":{\"global\":[\"created_at\",\"modified_at\",\"content_created_at\",\"content_modified_at\",\"purged_at\",\"trashed_at\",\"etag\",\"sequence_id\",\"sha1\",\"file_version\",\"path_collection\",\"created_by\",\"modified_by\",\"owned_by\"]}}",
  "task_horizon": 3,
  "info": "{\"service\":\"box\",\"seed_template\":\"box_default\",\"impersonate_user_id\":\"27512847635\",\"eval_type\":\"actionEval\",\"tools_required\":[\"POST /hubs\",\"GET /search\",\"POST /hubs/{id}/manage_items\"]}"
}
```

question 是目标；answer 是 evaluator 的状态断言，不给 Agent；info 含初态模板、身份和接口需求等评测元数据；task_horizon 是数据标签。answer 只对新增 hub 的 title 和关联记录 item_id 分开计数，没有要求两条记录使用同一个 hub_id，这就是错误关联可通过的原因。

### A.3 ScienceAgentBench verified 第 1 条

来源：[sab_raw_examples.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/sab_raw_examples.json>)，由本轮真实 parquet 读取。这里只投影身份、初态结构和输出/评分索引，不把作者知识提示改写为“原始论文”。

```json
{
  "instance_id": 1,
  "domain": "Computational Chemistry",
  "subtask_categories": "Feature Engineering, Deep Learning",
  "github_name": "deepchem/deepchem",
  "src_file_or_path": "examples/clintox",
  "dataset_folder_tree": "|-- clintox/\n|---- clintox_test.csv\n|---- clintox_train.csv",
  "gold_program_name": "clintox_nn.py",
  "output_fname": "pred_results/clintox_test_pred.csv",
  "eval_script_name": "clintox_nn_eval.py"
}
```

完整记录另有 task_inst、domain_knowledge、dataset_preview 三字段。task_inst 是训练并输出预测的目标；domain_knowledge 是整理知识；dataset_preview 为输入数据样例；gold_program_name/eval_script_name 指向未在此 parquet 内含的评测资源。文件名存在不证明对应 evaluator 已读或已运行。

### A.4 MAGE Calc 真实任务的环境与判分字段

来源：[4f07fbe9-70de-4927-a4d5-bb28bc12c52c.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/MAGE/osworld/evaluation_examples/examples/libreoffice_calc/4f07fbe9-70de-4927-a4d5-bb28bc12c52c.json>)。省略 instruction/config/trajectory 和 evaluator.expected/postconfig，保留键和值不改写。

```json
{
  "id": "4f07fbe9-70de-4927-a4d5-bb28bc12c52c",
  "snapshot": "libreoffice_calc",
  "source": "https://superuser.com/questions/1081048/libreoffice-calc-how-to-pad-number-to-fixed-decimals-when-used-within-formula",
  "evaluator": {
    "func": "compare_table",
    "result": {
      "type": "vm_file",
      "path": [
        "/home/user/Padding_Decimals_In_Formular.xlsx",
        "/home/user/Padding_Decimals_In_Formular-Sheet1.csv"
      ],
      "dest": [
        "Padding_Decimals_In_Formular.xlsx",
        "Padding_Decimals_In_Formular-Sheet1.csv"
      ],
      "multi": true
    },
    "options": {
      "rules": [
        {
          "type": "sheet_print",
          "sheet_idx0": "RNSheet1",
          "sheet_idx1": "ENSheet1"
        }
      ]
    }
  }
}
```

source 是用户问题出处，不是手册证据指针；snapshot 选应用环境；evaluator.func/result/options 定义实际比较入口与产物。必须另外读取 expected 与 postconfig 才能重建完整 Oracle，不能靠此投影声称任务已能运行。

## 附录 B. 原始证据索引与本轮统计文件

| 内容 | 文件 |
|---|---|
| 实际源长度及哈希 | [source_lengths.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/source_lengths.json>) |
| 当前原版加载/窗口结果 | [current_load_probe.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/current_load_probe.json>) |
| 新候选实数统计 | [candidate_stats.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/candidate_stats.json>) |
| 当前源代码函数位置与历史证据快照 | [current_framework_snapshot.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/current_framework_snapshot.json>) |
| 当前 Docker 只读探测 | [runtime_probe.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/runtime_probe.json>) |
| 搜索与访问记录 | [search_log.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/search_log.json>) |
| 既有原始数据统计 | [raw_statistics.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/raw_statistics.json>) |
| Box 原 Oracle 反例 | [agentdiff_stats_and_probes.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/agentdiff_stats_and_probes.json>) |
| ExploraCoder/HANDBOOK 原反例 | [oracle_probes.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/oracle_probes.json>) |
| SAB verified 原始 parquet | [sab_verified.parquet](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/sab_verified.parquet>) |
| SAB 逐题评分调度代码 | [run_eval.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/ScienceAgentBench/run_eval.py>) |
| SAB 图形模型评分代码 | [gpt4_visual_judge.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/ScienceAgentBench/gpt4_visual_judge.py>) |
| SkillFlow 真实排除表 | [t12_generate_excluded_tasks.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/skill-flow/analysis/results/t12_generate_excluded_tasks.py>) |
| SkillFlow 使用/结果分析 | [t18_generate_skill_usage.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_selection_design_2026-10-21/skill-flow/analysis/results/t18_generate_skill_usage.py>) |
| Flask 原始题库 | [dataset.jsonl](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/dataset/dataset.jsonl>) |
| GitChameleon pytest 执行入口 | [eval_sample.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/gitchameleon/eval_sample.py>) |
| Box 完整 v2025.0 原始规范 | [openapi-v2025.0.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/box-openapi/openapi/openapi-v2025.0.json>) |
| Box 完整 base 原始规范 | [openapi.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/box-openapi/openapi/openapi.json>) |
