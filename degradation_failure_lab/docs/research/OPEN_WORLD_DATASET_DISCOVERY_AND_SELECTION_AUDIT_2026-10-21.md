# 开放式候选发现与最终选型审计（2026-10-21）

本报告在 2026-10-20 复审之后开展新的开放式检索。它更新选型决策，不替换或伪装成前一轮原始数据审计。边界：只读资源、固定版本、离线统计与两个评分反例；没有调用生成模型、Agent 或模拟用户，没有改动正式 Anything2Skill、Skill、Oracle 或请求账本。

## 1. 决策先行

**没有发现可以原样用于正式研究、且已证明满足全部十项条件的现成 Benchmark。** 这既适用于旧名单，也适用于本轮新增候选。“有文档、有工具、有测试”不等于具有可归因的文档→Skill→跨任务错误传播链路。

**唯一主方案：以 GitChameleon 2.0 的真实版本化开发文档和执行任务为种子，建立规模受控、规则可追踪的操作任务子集。** 这是一项需要补充标注、筛选和必要任务重构的研究数据集建设方案，不是宣布原始 328 道代码补全题全部合格。优先验收 Flask JSON provider 规则簇，再决定是否扩展到其他库。选择依据是实际存在可固定的开发者文档、真实运行语义、多任务共用规则及隐藏测试，且规则直接控制代码行为；不是因为它能接入 Harbor。

**唯一备选：官方服务文档＋Agent-Diff 的复杂工作流子集。** 必须先补齐真实目标和副作用 Oracle，再确认同一规则支持多个复杂任务。Box 131/141/117 只用于工程验收；正式候选应转向 Calendar 的周期事件/实例作用域等规则簇。上一轮对 Agent-Diff 的优先级下调：本轮发现的版本文档资源在来源真实性和行为契约上提供了更直接的证据。

两方案均处于**条件准入**，当前“全部通过”的候选数为 **0**。如果主方案只能形成短代码补全题，或 Agent 在 NoSkill 下已稳定完成且不用文档，则不把它包装成 Agent Skill 主实验。备选若同样失败，则暂停执行层主张，继续构造有真实业务需求的任务；不能降低准入标准来保留推荐。

ConditionalQA 保留为可选的条件规则保真辅助材料；SOPBench 不作为主执行层。两者组合不能互相补出同一条完整因果链，也不作为本轮第二备选。

## 2. 我们真正需要的任务与判据

需要的是：**依据可定位的外部操作契约，完成有状态、可重复、可独立验收的工作；同一契约至少支持两个不同任务，另有一个作用域外负对照。** 多工具调用、长上下文、低成功率，都不是知识依赖的充分证据。困难可能来自 UI 定位、算术、随机用户、基础设施或不完整 Oracle。

统一硬门槛如下。P=当前原始证据支持；C=可通过明确适配达到但尚未验收；F=原生不满足；U=证据不足。C 不按 P 计数。

|门槛|实际要验证什么|
|---|---|
|G1 真实固定来源|来源独立于测试题；真实生产/软件文档；版本、许可、哈希可保存；合成的自然语言不算自然来源|
|G2 规则可定位|前提、结论、参数、例外、范围、证据位置明确；查出重复表述与交叉引用|
|G3 复用与负对照|两个任务需要同一语义规则；一个不依赖该规则；不能用共享 URL 或函数名替代证明|
|G4 原版生成适配|不改 A2S 生成算法；内容覆盖、规则型操作性、完整包可安装；可加载不等于生成有效|
|G5 公平对照|同一 clean/degraded 来源分别给 DirectDoc 与预先冻结的 Skill；工具、预算、任务保持一致|
|G6 独立行为/结果验证|记录读取、关键操作和最终状态；Oracle 不读待测 Skill；拒绝错误对象、额外副作用、空交付|
|G7 干预有效|局部修补、反向破坏、sham 和不相关退化；不改真实工具语义、任务事实和正确答案|
|G8 规模与独立性|报告来源、规则簇、任务和重复层级；不能将同一规则的重试当独立样本|
|G9 难度与知识效应|NoSkill、DirectDoc-clean、Skill-clean 都校准；任务可解且有文档信息作用空间；不强制阅读|
|G10 可实施性|独立 verifier、环境版本、文件/服务隔离可做到；成本可控且限制如实公开|

必须分开记录：来源规则真值、生成规则正确性、Skill 是否被发现/读取、是否采用目标规则、任务正确性。读取只能证明暴露；采用需要操作参数、决策与干预响应的证据。

## 3. 开放式发现过程与检索边界

采用 nature-academic-search 的多来源检索流程。实际可用入口为网页搜索、arXiv、ACL Anthology、OpenReview、作者 GitHub、Hugging Face 数据目录；本会话没有可直接调用的学术专用 MCP 检索服务。第三方摘要只作线索，结论回到论文/作者仓库。日期截止为 2026-10-21；没有声称穷尽所有公开资源。

阶段 A 不从项目名开始，使用了文档驱动执行、软件手册、新 API、政策检索、共享规则、状态 Oracle、文档噪声等组合检索。完整成功查询及返回结果保存在 `search_log.json`。最初新搜索连接器参数错误、Git 网络代理失败、若干 TLS EOF、GitHub API 限流均保留为访问限制；通过官方 raw 文件或 Git 只读取回补，未用猜测补字段。

|扩展路径（阶段 B）|新增线索及研究作用|
|---|---|
|长手册/政策 Agent → HANDBOOK.md related work|ST-WebAgentBench、业务 JourneyBench：过程合规与负面动作判据；不是同名视觉 JourneyBench|
|政策检索/业务工具 → FraudBench → τ-Knowledge|发现结构化生成的政策库、任务级 required_documents 和独立 gold-state 比较；继续检查来源是否自然|
|未见库/文档执行 → ExploraCoder → 版本演化相邻工作|Torchdata-Manual、LibEvolutionEval、GitChameleon 2.0；从词法相似评价推进到实际执行测试|
|真实软件用户手册 → MAGE → OSWorld 固定任务|真实 PDF、页码结构、操作任务、文档陈旧/删减消融；检查 GUI 难度与知识难度的区别|
|规则组合/自演化 → GDPevo|共享环境、5+5 同源任务、规则重组；检查到底是否真的修改业务状态|
|Skill 故障/错误传播 → SkillScriptBench、WildSkills|clean/doc/script/joint 与 NoSkill/Original/Fixed；发现工程化暴露会影响外推|
|文档语义不变量 → PBT-Bench|真软件库、性质测试、buggy/fixed 对照；进一步查其可用源码与任务是否包含独立来源文档|
|隐含流程/副作用 → World of Workflows|提供状态传播环境，但“隐藏规则”不自动等于有可退化来源手册|

停止本轮扩展的依据：上述不同方向均已产生候选并沿至少一条相关工作继续追踪；对最有希望的来源/任务结合做原始数据核验，当前主要缺口已明确为共享规则标注、知识效应和 Oracle。未逐个下载所有文献，也不以数量代替匹配。

### 3.1 候选来源必须分清

**用户此前提供或点名：** Terminal-Bench 2.0、CL-Bench、AppWorld、τ-bench、ConditionalQA、SOPBench、RoTBench、SkillGenBench、SkillsBench、Agent-Diff、RuleArena、DocPrompting、AgentDocsBench、Anything2Skill 及 Agent Skills Can Be Harmful。

**前一轮已经自主发现/提及，本轮不冒充新发现：** ExploraCoder、SkillNet-Gym、PIMS 等。Torchdata-Manual 在本轮进行了更深原始核验，属于旧线索扩展。

**本轮新发现并纳入针对性审查：** GitChameleon 2.0、MAGE、τ-Knowledge（虽然属于 τ 家族，但知识域和资源是本轮沿 FraudBench 发现）、HANDBOOK.md、GDPevo、χ-Bench、SkillScriptBench、PBT-Bench、ST-WebAgentBench、业务 JourneyBench、World of Workflows、LibEvolutionEval、DeepStress；WildSkills 作为错误传播测评方法的重要新相关工作。

检索还返回其他任务合成、文档产物和代码生成项目；与核心链路联系弱或未经原始核验的条目不凑入候选清单，也不计入通过数量。检索日志保留这些线索。

## 4. 新候选原始核验：关键发现

以下本地路径以 `C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/` 为根，简称 A。各仓库 `_identity.json` 固定提交，`_tree.json` 是官方文件清单，`_download_*.json` 记录实际下载与失败。统计是固定快照的结果，不把论文 headline 当本地规模。

### 4.1 GitChameleon 2.0：最值得继续建设的自然技术文档种子

[论文](https://arxiv.org/abs/2507.12367)；[官方仓库](https://github.com/mrcabbage972/GitChameleonBenchmark/tree/3a1b6045a6b2a276bd24d715589cb041f8eccb93)。Apache-2.0 仓库许可证；所链接的开发文档须分别保留各上游许可，不能由仓库许可统一覆盖。

**已读取：** `dataset/dataset.jsonl` 全部 328 条；所选任务 hidden/visible tests；`gitchameleon/data_model.py`、`eval_sample.py`；官方 Flask 3.0.0 文档 docstring、API RST 和 changelog。部分无关测试下载发生 TLS 错误，所选 144/164/168 的关键文件可用；不声称本地镜像完整。

原始记录字段如下（真实字段摘录见附录 A）。`problem` 是要求；`starting_code` 是 Agent 的初始代码；`python_version/library/version/additional_dependencies` 固定环境；`test` 是可见测试文本；`solution` 是标准实现；`docs` 是参考链接；`type_of_change/name_of_class_or_func/api_calls` 是变化及 API 元数据。**禁止把整条记录喂给生成器或 Agent：其中有答案和测试。** A2S 仅接收来源文档，Agent 只接收必要任务与 starter。

实际统计：328 题、26 个 library 标签、207 个不同 docs URL，所有题有 docs。14 个“同 library/version/entity”重复组里，4 个的 entity 是空字符串或 `-`；排除后仅 **10 组、27 题（8.23%）**，而且仍未等于 10 个语义规则簇。213/328 题的 `api_calls` 长度为 0 或 1（64.94%）；该字段也含 Python 内置函数，不能当工具调用数或真实难度。已有规模能提供筛选材料，不能据此宣称有数百个跨任务 Skill 实验单位。

来源问题很具体：`docs` 多为 `/stable/`、`/main/`，也有第三方旧镜像；本轮访问 Flask `/en/3.0.x/api/` 实际重定向到当前 3.1.x。必须从匹配发布标签/提交获取源文档，而不是保存一个看似带版本的 URL。Flask 3.0.0 标签核得 `735a4701d6d5e848241e7d7535db898efb62d400`，原始文本另有 SHA256。

其 Oracle 比 SOPBench 更直接：运行隐藏 pytest，对序列化值、NaN 数量、路径拒绝、dtype 等检查；不是仅对 Agent 的同一错误轨迹重放。但这仍是功能测试，尚不覆盖任意副作用、测试规避、全局 monkey patch 或环境污染；必须在 separate verifier 下验证输出并检查额外改动。

**最重要的限制：** 原生任务多数短，部分 starter 已给出 `DefaultJSONProvider` 等关键结构；任务 `164` 的 NaN 要求也由 prompt 明说。它能研究版本契约的执行错误，但还不能证明编译 Skill 比直接读文档有独立价值。主方案只采用规则簇筛选后的任务；必要的工作流扩展必须标为新构造任务，不冒称原始 Benchmark。

### 4.2 MAGE＋OSWorld：自然手册最贴近，但不是现成的同规则任务集

[论文](https://arxiv.org/abs/2610.23012)；[官方仓库](https://github.com/ku-autoai/MAGE/tree/eeebb0136524efae905469e6fe72de84d368aeb4)。主代码 MIT，OSWorld 派生部分 Apache-2.0；LibreOffice 指南按其 GPLv3+ 或 CC-BY-4.0+ 条款，Slack 文档另有权益限制。不能给整个混合仓库统一标 MIT。

直接读了 `docs/ASSET_ATTRIBUTION.md`、任务生成配置、Calc `section.json`、全部 **47 个 Calc 原始 evaluation task JSON**、`compare_table`。Calc 7.1 指南的结构化文件为 **536 条 section**，含 `title, level, path, start_page, end_page, next_start_page, is_leaf, text, text_page_count, image_paths`。它是带页码的抽取结果，**不是 536 份独立自然来源**；不同 section 会重复同页内容。本轮没下载 10.7 MB PDF，也未逐页视觉比对，表格/图示保真未验收。

手册出处是真实 LibreOffice Documentation Team，版本 7.1（2021）；仓库还列 Impress 7.6、Writer 7.3。已发布 RAP 派生任务数为 47/47/23，但不能与原任务相加。训练任务 228/102/105 是作者从手册生成的任务，不能当独立人工真实任务。

原始任务 JSON 的 `source` 指向用户问题，`config` 下载/打开初始文件，`evaluator.result/expected/options` 定义产物与判据，`postconfig` 保存/导出文件。比如 `4f07fbe9-70de-4927-a4d5-bb28bc12c52c` 要在拼接文本中固定小数位；Oracle 导出 CSV 后比显示值。它确实验证产物，但不能判断是否使用 TEXT 规则、是否只是硬编码结果或经 Python 处理。因此保持合法替代方法时，Skill 的必要性仍未知。

核查了一个**不能批准的** 2+1 设想：上述小数拼接题、`4de54231-e4b5-49e3-b2ba-61a0bec721c0` 拼接四列并保留两位、`6e99a1ad-07d2-4b66-a1ce-ece6d99c20a5` 仅格式化数值列。虽然语义看似共用格式规则，但读取的手册 `Text operators`（第 258 页）只说明拼接与 CONCATENATE，未找到足以证明“TEXT 数字格式如何影响拼接”的明确条款。**不能因为同属 Calc 格式任务就认定依赖同一规则。** 此组未通过规则证据门槛，不能拿来作为第二个已验证组。

MAGE 已研究旧手册和部分手册，对我们有直接启发；但其任务相关 RAP 计划不是预先编译冻结后跨任务复用的 SKILL.md。GUI agent、截图、软件版本会增加混淆和当前 Terminus-2 的适配工作。它比 CQA 更贴近操作研究，仍不足以替代主方案；本轮不列为最终备选。

### 4.3 τ-Knowledge：共享文档与状态验证很强，但来源是合成的

[论文](https://arxiv.org/abs/2603.04370)；正式代码实际位于 [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench/tree/57e54143025bec219b5726884651c98eede202e2)。搜索中的 SierraAI/tau-knowledge URL 返回 404，未据此判资源不存在，而是追踪官方发布找到 banking_knowledge 域。

实际目录有 **698 份 document JSON**；当前 tasks.json **97 题**，88 题 `reward_basis=["DB"]`，9 题 `["ACTION"]`。90 题有 assistant gold action，7 题全部 gold action 属 user；不能把后者当 Agent 自己执行业务操作。97 题共引用 215 份 required_documents，其中 156 份被至少两题引用；这仍只是文档重叠候选数。

读了 task_001、实际引用的 Gold/Silver 文档、提示及 evaluator。文档是 `id,title,content`，content 为 Markdown。Gold 文档有订阅资格、费用、返现、额度和申请步骤；原样出现“minimum credit score: $720”这种类型错误，进一步说明不能将合成材料当生产政策。

task_001 是用户 Sarah Bosch 的选卡场景，期望 **user** 调用 `apply_for_credit_card` 选择 Gold Rewards Card；免费订阅只有被问及才告知。该题测试询问和建议导致模拟用户动作，混入用户模拟。目标 Gold 文档同时被 9 题引用，不能直接视为 9 题共享同一订阅规则。

`evaluator_env.py` 创建独立 gold environment，执行 gold actions，再比较两侧 agent/user DB hash；**这比 SOP 的同轨迹一致性更有研究价值。** 但纯终态仍可能漏临时泄漏或先错后恢复；ACTION 评价也要查多余动作。只读操作日志可影响 hash 的设计需明确。对本课题要冻结用户策略、记录工具授予和访问、补过程约束。

决定性来源证据在论文 §4：先用 LLM 生成结构化业务变量，再生成文章，之后人工与 LLM 共建任务/数据库。公开性与机制很好，**G1 的自然来源不满足**。不把它推荐为自然退化主数据，避免因检索困难和政策密度而掩盖外部有效性缺口。

### 4.4 HANDBOOK.md：公开规模不足，而且“确定性”不等于“正确”

[论文](https://arxiv.org/abs/2607.25398)；[固定仓库](https://github.com/surge-ai/handbook/tree/374bc876ba008169e0dc30c1a751859d525cedc4)，Apache-2.0。论文 65 题、10 基础手册；公开 README 明写只放 **3 个样例**。不得把 65 题当已下载可实验规模，也未联系作者或代发邮件。

公开任务是 Harbor 目录：`instruction.md/system_prompt.md/task.toml`、`environment/initial_workspace/*.html` 手册与业务文件、各服务初始 JSON、`tests/rubrics.json` 和 `sop_verifier.py`。三题实际 22/12/17 条 rubric，共 **51 条**：35 expected_output、16 incorrect_behavior。保险样例的 12 条全部是 expected_output，不能笼统说每题都完整检查禁止行为。

手册由专家改写行业指南，虚构公司，每题修改阈值/规则；不是独立自然公司原始手册。同一基础模板不等于同一冻结政策。公开三题分别不同公司，当前没有真实共享规则 2+1。

**实测评分反例：** HR 第一条人员记录 rubric 要求三人的部门和校区正确。我们仅在审计临时目录构造姓名、ID、email 正确，但 department/campus 全空的 Excel；原始 `verifier_code` 返回 `pass=true, score=1.0`。原因是 `req['dept'] in dept or dept in req['dept']` 接受空子串，campus 同样。这是一个判据的假阳性，**不是宣称整个任务能空跑通过**。见 `oracle_probes.json`。

可借鉴：按 required/forbidden 分离，跨文件/服务验收；不直接采用为主集。

### 4.5 GDPevo：真实存在复用结构，但不能把“业务分析”叫成业务状态操作

[论文](https://arxiv.org/abs/2608.03764)；[固定仓库](https://github.com/Prism-Shadow/GDPevo/tree/56d60ae4ae5e067d1ec0ee1f850622e69f422179)，Apache-2.0。实际 24 个 task_group、每组 5 train＋5 test，共 **240**；旧版 120 题不能和新版合并。

读取 group001 完整 YAML、10 个 prompts、shared DB、server/generator 和部分评分器。`env.state_mode: read_only`，API 是查询数据与 `/api/policies`。任务要求返回 JSON 业务交接计划；“CRM create/update counts”是答案中的计划/统计，**不代表执行了 CRM 写入**。

`harborcrm_data.json["policies"]` 包括 contact_hygiene、lead_followup、prospecting、sponsor_status；例如去重优先级和事件结束后天数。它支持真实的共享规则考察，但规则是研究构造，政策与 DB 同文件生成，且政策 API 可绕过 Skill。若改成写操作任务，需新接口/Oracle，已不是原生资源。其5+5和训练反馈独立于测试的设计值得借鉴，原生不满足自然来源＋实际业务状态修改。

### 4.6 ExploraCoder/Torchdata-Manual：不能只数多 API

[论文](https://aclanthology.org/2025.acl-long.887/)；[固定仓库](https://github.com/greenlight2000/ExploraCoder/tree/2d869352cf72bb05858b69d8d67f446d97a07263)。本地读取 100 条 `Torchdata_Manual.jsonl` 和 MonkBeat_Eval；官方目录未见顶层 LICENSE，数据再分发需澄清，不能假定开放仓库即自由许可。

真实字段 `task_id/task/prompt/canonical_solution/test`。task_2 要从文件解析 JSON、展开、加索引、分批、转列、洗牌、缓存；参考实现确有多 API。但四个断言只查输出长度 32、首元素是 dict、有 index、首 index 长度 16 或 4。

**实测：** 完全不读文件，固定返回 32 个 `{'index': list(range(16))}`，原始 test 通过。此题 Oracle 不验证大多数目标。复杂 API 参考解不能保证合法替代实现也必须读文档，论文针对旧模型的 unseen 设定也不能直接用于 2026 模型。作为多 API 工作流构造方法借鉴，不选主数据。

### 4.7 其他新候选的核验深度与去向

|候选及第一方证据|实际观察/访问状态|统一准入结果|
|---|---|---|
|[χ-Bench](https://github.com/actava-ai/chi-bench/tree/4444a07fa68a4f1623f841a292a54e284fc8e7f7)、[论文](https://arxiv.org/abs/2605.16679)|75 基础任务；README 的任务数据 public/gated 描述不同段有不一致；手册明确 gated，需申请；1279 文档与论文1290+版本口径不同；每 trial 的 workspace judge 使用 LLM，模拟患者/同行也调用模型|手册及原始完整任务未获准访问，U；不能拿标题中的 policy-rich 当 P；不以 Harbor 支持推荐|
|[SkillScriptBench](https://github.com/HKUST-KnowComp/SkillScriptBench/tree/92cc92baea279d412fcfb1f8b1ef5a2238ff3b45)、[论文](https://arxiv.org/abs/2610.04008)|150修复任务＋50包×4状态；输入 REQUEST.md＋原 Skill/scripts；evaluator/runtime另发；README 明确尚无项目级许可证，第三方各自条款|原生研究对象是已有 Skill 修复，不是独立源文档→A2S；F；可借鉴doc/script分离和clean保持|
|[PBT-Bench](https://github.com/ElliotXinqiWang/PBTbench/tree/cef1aa4b8205c91ad7f0b3c5274b37304ff88765)、[论文](https://arxiv.org/abs/2605.15229)|Git树实数100个problem.yaml；读取bidict四任务、文档/patch/ground_truth和两种评分入口；代码MIT、数据CC-BY-4.0、原库各自许可|高相关，但原生文档存在已证语义错误且强制文档优先；不直接采用，见下述补充|
|[ST-WebAgentBench](https://github.com/segev-shlomov/ST-WebAgentBench)、[论文](https://arxiv.org/abs/2410.06703)|官方描述375任务，政策由 POLICY_CONTEXT 注入；trace evaluator 支持 consent/order/sensitive data等|提供合规执行/评价方法；独立自然来源与冻结规则映射未核，G1 U；未做全量原始审计|
|[JourneyBench业务版本](https://aclanthology.org/2026.eacl-industry.15/)|SOP graph 与 User Journey Coverage Score；不是视觉同名集|轨迹顺序不等于业务终态；自然手册/许可/完整资源未核，U|
|[World of Workflows](https://github.com/Skyfall-Research/world-of-workflows)、[论文](https://arxiv.org/abs/2601.22130)|官方目录描述ServiceNow实例、audit trajectory、constraint/task completion数据；论文与README workflow数量不同|隐藏动态/执行基座有用；独立规则文档、可离线完整复现未证，U；不把4000+程序规则当自然来源|
|[LibEvolutionEval](https://lib-evolution-eval.github.io/)、[论文](https://arxiv.org/abs/2412.04478)|版本化文档与真实/合成completion；主要F1/MRR|来源可借用，原生缺我们需要的执行Oracle，F|
|[DeepStress](https://arxiv.org/abs/2607.13920)|动态合成检索文档，操纵可信性/相关性/事实性，评价问答|退化因子设计可借用；非冻结源→Skill→业务执行，F|

### 4.8 PBT-Bench 的进一步原始核查改变了初筛判断

GitHub API限流后取得浅层Git元数据，固定 `cef1aa4b8205c91ad7f0b3c5274b37304ff88765`。读取 `libraries/bidict/problems/BIDC-002..005/` 的任务元数据及可取得的文档/测试；BIDC-003 文档下载失败，未假装完整读取。没有运行库patch、Agent或Docker。BIDC-002原始YAML含id/library/library_version/scope/docs_provided/existing_tests/ground_truth/bugs；每个bug有函数、触发条件和patch。必须把这些隐藏bug描述与ground_truth留在verifier侧，不能作为生成输入。

这个资源比泛泛代码补全更有意思：Agent写性质测试，目标是在固定正确库通过、固定缺陷库失败；同一库下多个缺陷任务有复用潜力，能记录Agent编写/执行测试的行为。但多个bug是否依赖同一规则仍要核，buggy/fixed是评分所需的两环境，文档退化条件之间应固定这两环境，不能同时换patch。

**发现一处不能忽视的来源冲突：** BIDC-002的 `docs/bidict_official.md` 自称官方API文档，却在“Duplication Handling”写默认重复key抛KeyDuplicationError。真实 [bidict 0.23.1 Basic Usage](https://bidict.readthedocs.io/en/v0.23.1/basic-usage.html) 明确说明 `b[existing_key]=new_value` 默认覆盖；`put/putall` 的较严格默认又不同。这个整理稿遗漏方法作用域且把 ON_DUP_DEFAULT 写错；BIDC-003元数据自身也描述了正常key更新。不能把文件名“official”当自然来源证据。

`eval/prompts/pbt_hypothesis.j2` 明确要求读完文档、前期不读源码、每测试必须@given；不符合本研究自主采用协议。`eval/run_eval.py` 简入口仅按pytest返回码区分PASS/FAIL，F→P不是全面防作弊或有效性质证明；实际批量入口 `run_pbt.py` 另有patch、函数过滤与逐bug评分，未执行验收，不把简入口发现直接外推整个正式评分器。它可以提供性质测试Oracle设计，当前不是已证明可靠的来源→Skill主集。若以后用真实上游文档替换整理稿并重做协议，属于明确标注的适配研究，须重新过门槛。

## 5. 与已知候选统一比较

下表不以流行度、总题量或 Docker 接入排名。旧候选细节见前一轮完整审计及原始本地证据，本轮不重复虚报为新发现。

|候选|G1真实来源|G2规则|G3共享＋负对照|G4 A2S|G5公平|G6Oracle|G7干预|G8规模|G9知识效应|G10成本|结论|
|---|---|---|---|---|---|---|---|---|---|---|---|
|GitChameleon筛选/重构子集|P/C版本冻结|P部分|P静态一组/C运行与扩展|C已有加载探针|C|C有隐藏测试|C|C|U|C|主方案建设种子|
|官方文档＋Agent-Diff|C匹配版本|P部分|P Box静态/C复杂组|C|C|F原生/C增强|C|C|U|C|唯一备选|
|MAGE＋OSWorld|P手册/C渲染|P段落/C目标|U|C|C|C产物检查|C|C少数手册|U|C较高|最值得保留的非推荐新资源|
|τ-Knowledge|F合成|P文档|C重叠多未逐规则|C|C|C gold DB|C|C|U|C用户模拟|机制资源，不作自然主集|
|HANDBOOK公开样例|F专家虚构政策|P|F只有3异公司样例|C|C|F已实证判据漏洞|C|F公开规模|U|C|排除当前主选|
|GDPevo group001|F构造政策|P|C|C|C|F只读计划非业务状态|C|C24组|U|C|方法参考|
|ConditionalQA|P政府原文|P|P已审两组|C规则摘要风险|C|F原评分不足|C|P文本来源量|U|C|QA辅助，不是执行主层|
|SOPBench|F程序SOP|P|P窄固定政策组|C|C泄漏需去除|F严重假阳性|C|C政策一致性低|U|C公开工具缺口|不作主执行层|
|SkillGenBench|C源类型混合|C|U|C贴近生成|F原协议强制读取等需改|C|C|C|U|C|借鉴task-agnostic分离；非直接采用|
|SkillsBench|C既有Skill资源|C|U|U独立生成来源|C|C强于纯文本评分|C|C|U|C|评测方法资源，非源文档链现成答案|
|AppWorld / Terminal-Bench 2.0|C任务各自|C|U|U|C|C需按题审|C|C|U|C|执行环境强不能替代源规则映射|
|CL-Bench / RuleArena|C部分规则来源|C|C|U规则Skill价值|C|F对当前有状态执行主张|C|C|U|C|规则/上下文辅助；不作执行主集|
|RoTBench|F工具扰动为主要变量|U|U|U|C|C|F不等于只退化来源|C|U|C|不匹配当前干预对象|
|AgentDocsBench|C用户自己提供|U|U|C|C|C可接verifier|C|U|U|C|框架，不自动提供合格研究数据|
|PBT-Bench原生|F已审整理稿/C换真源|C|U|C|F强制读源/C协议|C双环境未验收|C|C100题40库|U|C|文档/协议须重做；非直接主用|
|χ-Bench|U受限手册|U|U|U|U|C混合LLM judge|U|U公开可用量|U|C较高|证据不足|
|SkillScriptBench|F无独立生成源|C Skill内规则|U|F现有包修复任务|C|U外部runtime未验收|C包内干预|C350配置|U|C|修复研究参考|
|ST-WebAgentBench|U政策来源|C|U|C|C需移除重复注入|C轨迹判据|C|U共享规则规模|U|C|来源/原始映射待核|
|JourneyBench业务版|U|C图规则|U|U|U|C图覆盖/终态U|U|U|U|U|证据不足|
|World of Workflows|U独立文档|C程序约束|U|U|U|C状态/轨迹|C|U可取得完整实例|U|C远程服务|证据不足|
|LibEvolutionEval|C版本文档|C|U|C|C|F主要词法评分|C|C|U|C|文档资源，非执行主集|
|DeepStress|F动态合成|C|U|F非预编译Skill|C|F问答为主|C噪声因子|C|U|C|退化方法参考|

上述矩阵中的 P 仅限注明范围。尤其 G3 的静态依赖证明不等于已经在锁定环境中完成反事实执行；C/U 一律不能计为完整准入。不同候选的 F 不能互相抵消。

**分类结果：** 全部硬门槛已通过：无。进入有条件建设：主方案与唯一备选。存在明确原生硬缺陷而排除直接主用：CQA、SOP、HANDBOOK公开样例、GDPevo已审组、Torchdata-Manual原评分、PBT已审整理文档与原协议、SkillScriptBench、RoTBench、LibEvolutionEval、DeepStress等。证据不足：χ-Bench、ST-WebAgentBench、JourneyBench、WoW及多数尚未逐规则核查的旧执行资源。F 是对本研究主用途的判断，不是否定论文自身价值。

## 6. 主方案的真实 2+1 与干预逻辑

本组是**真实原任务的最小资格检查组**，不是已经充分复杂的正式主实验：GitChameleon `144`、`164` 依赖 JSON provider 注册规则；`168` 作非依赖。

来源为 Flask 3.0.0 官方开发文档。`src/flask/json/provider.py:18` 的类文档说明：替换 provider 可通过 Flask 子类设置 provider class，或将 `app.json` 设置为 provider 实例。`src/flask/sansio/app.py:327` 构造时实例化，随后文档说明可在之后赋值。`CHANGES.rst:65` 说明旧 json_encoder 属性移除。三者构成条件、版本范围和动作对象：**对于已经实例化的 Flask app，仅给实例换 json_provider_class 不会自动重建 app.json；需显式替换 provider 实例，或在类构造前选择 provider。** 这是由文档和实际初始化代码共同核实的结论，不把“必须使用某一行标准答案”当契约。

|原任务|目标与其他规则|正确结果与目标干预预期|
|---|---|---|
|144，Flask3.0.0，Python3.10|现有 app 序列化 set 为有序列表；需要 provider default 分派＋注册；排序规则由题目给出|`{3,1,2}`输出 JSON 中 numbers=[1,2,3]；若错误 Skill 只赋 class 不替换实例，set 仍不可序列化；模型若自行修复/采用另一合法机制则不受影响|
|164，Flask3.0.0＋NumPy1.25.1|序列化数组为去重列表，每个 NaN 仍保留；除注册还需 equal_nan/类型转换/非数组回退|原hidden test要求[1,NaN,2,NaN,3]结果长度5、含1/2/3和2个NaN；错误注册使数组不能按自定义规则序列化；即使注册修复，错误NaN规则仍可使任务失败|
|168，同Flask3.0.0＋NumPy1.25.1|安全拼路径＋stack的dtype/casting；不调用jsonify，不用app.json|路径越界抛NotFound，safe降精度抛TypeError，unsafe允许；局部破坏JSON provider注册应不改变它；如果源整体损坏影响safe_join才可能变化|

原始 starter 164 已包含 `DefaultJSONProvider`，所以只测“发现 provider 类型”会泄漏答案；我们选择“已建 app 的实例注册”这个未完成操作。即便如此，预训练知识、源码、错误消息和测试反馈均可能恢复，须保留并记录合法旁路。**不能强制 Agent 阅读 Skill，也不能只因它绕过 Skill 成功就删题。** 在预先定义的 pilot 中判断知识效应是否足够；正式分析包括所有分配任务的效果，并另报暴露后机制分析。

源中 provider 类文档和 app 属性文档重复了替换方法。只删其中一处并不能预测错误传播。退化要区分：单处局部删减（允许冗余恢复）与事先标注的全部同义证据共同退化；后者不得顺手破坏其他规则。反向破坏 Skill 时，仅替换目标注册建议；修补时只恢复该规则；sham 只改同长度非语义措辞。Oracle 始终以 clean 来源和真实运行行为为真值，**不会随退化文本改标准答案**。

### 6.1 为什么仍需建设，而非立刻跑328题

主方案第一组只证明链路可定位；正式数据还需：按 source/version/rule-family 分组，筛选多阶段输出/状态变换；对 starter、工具帮助、测试反馈逐项登记信息来源；必要时将同一实际工作需求扩展为多文件/多对象任务。扩展须保留真实规则与独立最终检查，不能为了强制用 Skill 任意禁止 Python、源码探索或替代 API。

若扩展只是把一道题重复20次、堆长prompt或要求固定工具序列，仍不合格。可接受的拟构造方向是同一应用内多个 payload 类型、两 app 隔离、schema与边界保持、错误输入处理；它们应来自实际需求而非直接从错误Skill反推唯一答法。独立标注员确认规则依赖和负对照后才能入库。

## 7. 唯一备选的具体最小方案与切换条件

沿用前一轮已经逐字段核查的 Agent-Diff＋官方 Box 来源包，固定 Agent-Diff `3bb9c40707df23d89e5dbc0e40c424ba38c69ff8`，Box规范 `a4f3e23d5bd01d9f4398bc1a764d410df3e607a7`。原始记录及反例位于 A 的相邻目录 `audit_final_review_2026-10-20/alternatives/`；不是本轮新构造JSON。

|真实任务|关系|资格检查要求|
|---|---|---|
|box131|创建EconomicData并将宏观经济文件夹1973339758关联目标hub|正确hub、正确item.type/id、创建＋关联均发生，禁止多余关联|
|box141|ModelEvaluations、8个JSON、research folder1173971943的组合|除hub管理契约还依赖文件定位、上传等；按原任务逐项验收，不用仅同端点算依赖|
|box117|在investments5610825569下建立Analysis2026文件夹|负对照不依赖hub管理项规则；保留文件夹API来源一致|

共享目标是官方 manage_items 请求中 add 操作与 item 类型/ID 的契约。修坏后前两题可能遗漏/错关联；负对照不应受影响。工具错误响应可能提示格式，Agent 可自行恢复；需记录恢复而非伪称完全由Skill支配。

原 Oracle 对错误hub关联、额外删除、错误文件等存在上一轮已执行的假阳性。Box2+1仅先检验 strengthened Oracle 和安装/观察接口，不作为“任务够难”的证据。正式备选向 Calendar177/178/184 的周期、例外和实例范围候选扩展；此复杂组的完整来源语义与 Oracle **仍未验收**。若只能用 Box 简单契约、复杂组两周内不能建立可信规则映射，则备选停止，不能降格用它完成论文主张。

切换主→备选条件：主方案在预注册的两个来源 pilot 中，合法替代知识使 NoSkill 持续饱和、规则无法形成多任务簇、或固定环境/Oracle建设超预算；并且备选已满足同一门槛。不是主方案失败就自动认定备选合格。

## 8. 原版 Anything2Skill：本轮新增的实际加载证据

沿用 `D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc`，未改源码。`a2s_probe.py` 设置审计钩子阻止网络和子进程，`dont_write_bytecode=True`。仅用原 loader/ingestor，以 `outline_fallback_mode='rule'` 运行 recommended 窗口；**不是正式配置中的 LLM outline，也没有抽取、编译、合并、注册或生成 Skill。**

对官方 Flask provider.py、sansio/app.py，按 AST 源顺序提取 standalone docstring/属性文档，逐条保留原文及源行号，输出 Markdown；没有输入测试题、标准实现或benchmark答案。结果：provider 5003字符、15文档块、15sections、3windows，最大2372字符；app 17484字符、28块/sections、6windows，最大2394字符。目标 `app.json` 实例规则出现在 provider window0，app 属性替换规则出现在 app window1。覆盖已在 `a2s/probe_results.json` 中验证。

该探针只证明来源转换后可加载并覆盖目标。通用 AST 转换未解析全部 Sphinx cross-reference、`#:` 属性注释和继承文档，不能当最终完整 source bundle。完整发布文档应从固定源码解析全部必要引用，并检查条件/例外的同窗或可追溯跨窗连接。全 changelog 也不宜不加区分与当前契约混成一个来源：旧版本条件是规则内容，不能误合并。

格式适配（JSON/HTML/RST→Markdown、引用解析、source spans）可在 A2S 外完成；若必须改官方抽取提示、合并逻辑或注册机制才能生成有用 Skill，就不再声称使用原版。生成可能拆成多个 Skill，应冻结完整包，保持文件hash与规范注册过程，不人为挑选“最正确的一个”作为唯一结果。

对 CQA 的判断不变：知识政策可以被重述成 Markdown，但是否产生可复用决策流程仍需测，不能从格式合法推断 Skill价值。Flask契约可指导执行中的配置、类型分派和检查，更具操作性；仍可能只是知识重述，必须通过复用与干预确认。

## 9. 当前测评工作可借鉴什么：直接回应“太简单就不需要Skill”

|研究|其任务选择/对照|借鉴与不可照搬|
|---|---|---|
|SkillGenBench（前轮已读）|task-conditioned与task-agnostic、Code/Doc来源|借task-agnostic隔离；不能照搬必须读取Skill或暴露测试文档的协议|
|SkillsBench（前轮已读）|真实工作产物、NoSkill/withSkill、调用观察|看自然发现和真实终态；专家Skill增益不等于A2S编译质量|
|GDPevo|同环境5train/5test，规则重组；self/fewshot/反馈分别比较|按规则族分割与跨任务迁移；不能混用训练gold/反馈到我们的task-agnostic生成源|
|MAGE §实验|真实手册、原任务、无RAP、旧/删减手册与不同检索质量|必须有无文档/无Skill基线；任务相关计划不是冻结Skill复用；其GUI成功率不可直接外推Terminus|
|GitChameleon|版本固定、隐藏与可见测试区分，允许合法替代实现|把功能正确与API命中分开；旧模型baseline不能证明当前模型仍需文档|
|ExploraCoder|多API、多步探索、旧模型API-untrained比较|按语义依赖选任务；8–14 API并不保证Oracle全面或当前模型unseen|
|WildSkills [原文§3.3](https://arxiv.org/abs/2610.18927)|49个可执行任务围绕确证缺陷，NoSkill/Original/Fixed；刻意让绕过Skill手工重算成本更高|借局部修复、确定性verifier、暴露后行为分类；不能把工程化高暴露率当自然采用率。部分修复改脚本，我们只修规则时必须保持脚本和工具不变|
|SkillScriptBench|Clean/Doc/Script/Joint；修复与保持分开|借sham/保真与代码错误分离；原对象是Skill包，不能替代源文档退化实验|

**不是越难越好，而是困难要来自被研究的外部规则。** 对每簇先作无模型静态审查，再经用户授权后做小规模能力校准：NoSkill、DirectDoc-clean、Skill-clean，统一模型、预算、环境、任务事实。随后再进入 clean/degraded、局部修补/反向破坏。

建议预注册的操作性门槛（研究设计，不是已测结果）：pilot 每来源至少2个规则簇，每簇2依赖＋1负对照，各重复3次；若 NoSkill 达90%以上且 clean 来源没有可见的正确性/成本或行为帮助，标为基线饱和层，不将其用于证明Skill收益；主能力实验优先扩展真实工作需求或替换；若 clean DirectDoc 也低于40%，先定位环境/题目/Oracle/任务过难，而非把失败归因于Skill。小样本阈值只是决策启发，不能当显著性检验；正式阈值、成本尺度和可接受差异须在看正式结果前锁定。

还应预注册保留一个小型基线饱和层：模型本来会做，却采纳错误Skill而做错，也可能是有效的负面传播机制。因此不能要求clean Skill必须先有正收益，才能研究错误Skill；但不能看过正式退化效应后再筛选这类题。若在各资源条件下始终不读取、不采用且行为无变化，它对完整传播链的识别力才弱。任务难度与Skill必要性必须分开报告。

不以NoSkill“必须失败”筛正式数据，不按退化效应大小挑题；应先用独立pilot选择难度层，再冻结规则簇和全量报告。保留强模型合法纠错/绕过路径，解释它为何阻断传播。若Skill正确但不读取，归于发现/可用性；若读取但未采用，归于决策；若采用错误却成功，要查冗余、恢复和Oracle；这些都是研究结果，不应抹掉。

## 10. 框架复用、建设成本、统计单位

现有 Harbor＋Terminus-2 可复用：任务包、文件挂载、canonical包完整性校验、读取观察、执行轨迹、separate verifier、请求记录。Git restore Gold 已成功9断言但正文未读、A0/A1未运行的事实，不能证明新数据Skill有效。当前Git-specific fixture/Oracle/预算门禁不能直接挪用为通用规则验收。

主方案最少新增：source/version/许可及span清单；规则—任务manifest；每任务环境锁定与starter隔离；仅给Agent安全字段；输出收集接口；隐藏功能测试＋副作用反例；DirectDoc/Skill等条件挂载与索引；采用事件编码。格式与协议在适配层实现，官方A2S不改。

初始工程与标注估计（人日，非承诺、未实做）：单一Flask簇的隔离运行与Oracle3–5；通用source-map/文档包1–2；逐规则双人审查及边界/负对照1–2；无模型验收1–2，合计约6–11人日。扩展至3个软件来源、每源4规则簇、每簇2+1共36任务，预计再需10–20人日，取决于版本依赖和人工任务重构。Agent-Diff复杂规则备选约8–15人日另估，不能沿用Box简组4–8日预算承诺。

为何有限自建是必要的：原生短代码补全缺跨任务工作流强度；多步执行集缺自然同源规则或可靠Oracle；政策集常为合成；长自然手册集缺原生规则簇。建设只补这些已核实缺口，保留原任务ID、source版本和新旧字段；不从生成Skill或退化后答案反推题目。规则标注者与任务/Oracle作者尽量独立，至少互盲复核。

独立单位是**软件来源/版本域与语义规则簇**，任务和重复嵌套其中。207 URLs不是207独立来源；3个库也不足以做宽泛自然文档泛化。正式目标可拟定≥6独立软件项目、≥24规则簇、≥72任务；这是需验证的建设目标，不是本轮已拥有数量。用来源/规则簇层级bootstrap或层级模型报告配对效应，分别重复生成和执行，保留模型/版本层。不要将来自CQA与SOP的两个总体成功率拼为同一传播链证据。

## 11. 下一步与验收、停止规则

**先做主方案一个规则簇的无模型资格包，不先批量生成Skill。** 待用户审核后再实施：144/164/168的固定环境，完整源文档包，source-map，独立测试及空交付/错注册/错对象/额外副作用反例。标准实现全过，至少目标规则错误实现使两依赖任务失败而负对照不变；该检查是Oracle和依赖敏感性验证，不是模型传播证据。

随后才申请运行 NoSkill、DirectDoc-clean、原版A2S Skill-clean 的有限pilot。生成看不到任务/答案，执行看不到隐藏测试；source文件只在DirectDoc条件可见，Skill条件只挂冻结完整Skill包，其余合法环境信息保持一致。不能先要求读取Skill来让实验成功。

正式退化实施条件：源转换无关键语义丢失；原版生成窗口覆盖；Skill确实提取为可复用操作/决策规则；两个依赖任务＋负对照通过人工和无模型干预检查；Oracle能拒绝错误和副作用；主能力pilot避免整体饱和/地板且有文档使用空间；预注册的基线饱和机制层另行分析。任一条件不成立则停在对应层，不宣称完整链路。

最关键三个阻断：**(1) 多任务真实共享规则＋自然知识效应尚未证明；(2) 确定性评分器仍需系统反例与副作用验证；(3) 原版A2S完整生成和Agent自然采用尚未测。** 本轮已有证据支持选择建设方向，但不能替代这三项验证。

## 12. 可复核证据与限制

本报告的统计/反例/加载结果分别在 A 下 `raw_statistics.json`、`oracle_probes.json`、`a2s/probe_results.json`；脚本为 `summarize_raw.py`、`oracle_probes.py`、`a2s_probe.py`。`gitchameleon_candidate_raw.json` 是原始任务的直接筛选副本，未翻译改字段。`extra/manifest.json` 固定官方文档与论文快照的URL/哈希。

旧证据入口：`D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/DATASET_FINAL_SELECTION_AND_FRAMEWORK_FIT_REVIEW_2026-10-20.md`；其原始文件根为 `C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/`。新旧结论冲突时，以本报告明确更新的选型优先级为准，不重写旧事实。

未验证：新方案的版本化容器执行、完整数据访问/许可证覆盖、全部规则簇、A2S模型生成、自然读取采用、统计功效、长期成本。少数候选只有论文/README证据已标注U。没有声称已经建立一个满足所有条件的公开Benchmark，也没有运行付费实验。

## 附录 A：原始样本及新增核查记录

以下 JSON 均由保存的原始文件按字段直接投影，未编写示意字段、翻译字段值或补造标准答案。为缩短篇幅省略的字段在每段说明；完整原件仍可读取。它们是审计材料，**不是批准发送给生成器或执行 Agent 的输入包**。

### A.1 GitChameleon：实际代码任务记录

来源：[GitChameleonBenchmark/dataset/dataset.jsonl](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/dataset/dataset.jsonl>)，按 `example_id=144` 定位。下列字段值完整；仅省略 problem/test/solution，正文已说明任务要求。注意 functional/webdev 原本是字符串，不能改成研究者猜测的布尔字段。

```json
{
  "example_id": "144",
  "python_version": "3.10",
  "library": "flask",
  "version": "3.0.0",
  "starting_code": "import flask\n\napp = flask.Flask('test')\n@app.route('/data')\ndef data(num_set):\n    return flask.jsonify({'numbers':num_set})\n\ndef eval(app, data_fn, num_set):\n    with app.test_request_context():\n        response = data_fn(num_set)\n        return response.get_data(as_text=True)\n\ndef app_set_up(app: flask.Flask) -> None: \n    ",
  "type_of_change": "argument or attribute change",
  "name_of_class_or_func": "app.json_encoder",
  "additional_dependencies": "",
  "functional": "1",
  "webdev": "1",
  "solution_api_call": true,
  "api_calls": [
    "default",
    "isinstance",
    "sorted",
    "super",
    "app.json_provider_class",
    "list",
    "MyCustomJSONHandler"
  ],
  "release_date": "2023-09",
  "docs": [
    "https://tedboy.github.io/flask/interface_api.json_support.html",
    "https://flask.palletsprojects.com/en/stable/changes/"
  ]
}
```


`starting_code` 是待补全程序，含已经创建的 app；它不是自然文档。`name_of_class_or_func` 在该条仍写旧 `app.json_encoder`，属于变更元数据，不能当 Flask3 的正确操作。`functional`/`webdev` 是原数据标记；官方 Example 模型未使用所有元数据，不能据名称重新定义任务。`api_calls` 是参考实现元数据，不是实际 Agent 工具轨迹。`docs` 是链接而非文档内容，需另行按版本保存来源。`test`/`solution` 在完整原件存在，但须留在审核/验证端。

对应源码证据：[extra/flask_3.0.0_provider.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/extra/flask_3.0.0_provider.py:27>)、[extra/flask_3.0.0_sansio_app.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/extra/flask_3.0.0_sansio_app.py:327>)。这里最小关键初始化代码为：

```python
self.json: JSONProvider = self.json_provider_class(self)
```

它说明实例在构造时确定；之后改变 class 属性不等于替换已构造实例。文档完整原文与 source spans 保存在 [a2s/source_map.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/a2s/source_map.json>)。这个推论应由固定环境的敏感性测试再验证，本轮没有将静态推论伪装成运行结果。

### A.2 τ-Knowledge：任务包含用户模拟、gold 动作和文档 ID

来源：[tau2-bench/data/tau2/domains/banking_knowledge/tasks.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/tau2-bench/data/tau2/domains/banking_knowledge/tasks.json:3>)。省略 description/user_scenario/annotations；保留以下字段原值。

```json
{
  "id": "task_001",
  "initial_state": null,
  "evaluation_criteria": {
    "actions": [
      {
        "name": "apply_for_credit_card",
        "arguments": {
          "card_type": "Gold Rewards Card",
          "customer_name": "Sarah Bosch",
          "annual_income": 100000,
          "rho_bank_subscription": true
        },
        "requestor": "user",
        "action_id": "001_0"
      }
    ],
    "communicate_info": [],
    "reward_basis": [
      "DB"
    ]
  },
  "user_tools": [
    "apply_for_credit_card"
  ],
  "required_documents": [
    "doc_credit_cards_gold_rewards_card_001",
    "doc_credit_cards_silver_rewards_card_001",
    "doc_credit_cards_bronze_rewards_card_001",
    "doc_credit_cards_platinum_rewards_card_001"
  ]
}
```


`initial_state=null` 并非没有数据库，而是任务未提供覆盖基础环境的状态；不能把空字段当空世界。`actions` 是评分端 gold，`requestor=user` 明确这一步由模拟用户完成；`reward_basis` 选择 DB 比较。`required_documents` 是作者提供的来源候选标注，并未精确到规则/span。另一个实际文档文件 [tau2-bench/data/tau2/domains/banking_knowledge/documents/doc_credit_cards_gold_rewards_card_001.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/tau2-bench/data/tau2/domains/banking_knowledge/documents/doc_credit_cards_gold_rewards_card_001.json>) 只有 `id/title/content` 三个字段，content 保存 Markdown；它不包含任务 ID 或标准动作。可从 tasks 与 document ID 建图，但仍须逐规则人工核实。

### A.3 MAGE/OSWorld：配置环境并检查交付物

来源：[MAGE/osworld/evaluation_examples/examples/libreoffice_calc/4f07fbe9-70de-4927-a4d5-bb28bc12c52c.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/MAGE/osworld/evaluation_examples/examples/libreoffice_calc/4f07fbe9-70de-4927-a4d5-bb28bc12c52c.json>)。省略 instruction/config/trajectory/related_apps 和 evaluator.expected/postconfig 等字段；嵌套保留字段值未修改。

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


`source` 是原用户问题来源，不是手册证据链接；`snapshot` 是软件环境。`result` 收集 xlsx 和导出的 CSV，`options.rules` 选择 sheet_print 比较，`expected` 在完整原件指定独立 gold 文件。`config` 准备输入，`postconfig` 保存并导出；这些不是 Agent 已执行的轨迹。手册另在 [MAGE/components/Task_generator/Libreoffice/calc/section.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/MAGE/components/Task_generator/Libreoffice/calc/section.json>)，两者没有现成目标规则ID联结。没有下载输入/gold xlsx 并执行完整验收，因此只确认判据配置，不宣称端到端通过。

### A.4 PBT-Bench：性质测试任务的可见与隐藏边界

来源：[PBTbench/libraries/bidict/problems/BIDC-002/problem.yaml](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/PBTbench/libraries/bidict/problems/BIDC-002/problem.yaml:4>)。以下是原始 YAML 的连续片段，省略注释与后续 bugs 列表；未把 YAML 伪称 JSON。

```yaml
id: BIDC-002
library: bidict
library_version: "0.23.1"
library_module: bidict
difficulty: L2
num_bugs: 2
bug_types:
  - missing_condition
  - missing_assignment
scope:
  - bidict/_base.py
  - bidict/_orderedbidict.py
docs_provided:
  - docs/bidict_official.md
existing_tests:
  - existing_tests/test_basic.py
ground_truth: ground_truth/pbt_test.py
```


`scope` 定义目标库文件，`docs_provided` 指文档包，`existing_tests` 是既有可见测试，`ground_truth` 是审计/评分参考。`bugs` 的函数、触发条件和修复 patch 明确描述缺陷，不能当任务无关的 A2S 来源。`num_bugs` 与不同缺陷不代表不同共享语义规则。本轮只读取这些文件，没有应用 patch 或运行 Agent。文档错误位置：[PBTbench/libraries/bidict/problems/BIDC-002/docs/bidict_official.md](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/PBTbench/libraries/bidict/problems/BIDC-002/docs/bidict_official.md:164>)。

### A.5 实际探针输出及范围

[oracle_probes.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/oracle_probes.json>)（两项均为无需模型的局部反例）：

```json
[
  {
    "project": "ExploraCoder",
    "task_id": "task_2",
    "probe": "constant fake pipe; never reads JSON files, no content, no shuffle/cache",
    "original_test_pass": true
  },
  {
    "project": "HANDBOOK.md",
    "rubric_id": "71217907-7deb-40e9-9093-420a3711b96c",
    "probe": "all required department and campus values blank",
    "result": {
      "pass": true,
      "score": 1.0,
      "feedback": "All three employees (Yoon/Marketing/West, Kapoor/Finance/Main, Webb/IT/Main) found with valid employee_ids"
    },
    "scope": "one criterion only; not claiming complete task pass"
  }
]
```


完整复现代码 [oracle_probes.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/oracle_probes.py>)。探针只执行已读过的测试字符串/单个 rubric 函数；没有执行第三方项目安装脚本、Agent 入口或完整评测。两个反例足以否定相应判据的可靠性，不能据此估计全数据集的错误率。

### A.6 固定版本与代码定位

以下提交从第一方仓库元数据/Git 树取得；源文档自身另由 extra/manifest.json 保存内容哈希。Flask 标签解析值未经额外 peeled-commit 核验，因此保守记为标签解析标识，不与所有上游资源版本混同。

|资源|固定标识|
|---|---|
|mrcabbage972/GitChameleonBenchmark|`3a1b6045a6b2a276bd24d715589cb041f8eccb93`|
|ku-autoai/MAGE|`eeebb0136524efae905469e6fe72de84d368aeb4`|
|sierra-research/tau2-bench|`57e54143025bec219b5726884651c98eede202e2`|
|surge-ai/handbook|`374bc876ba008169e0dc30c1a751859d525cedc4`|
|Prism-Shadow/GDPevo|`56d60ae4ae5e067d1ec0ee1f850622e69f422179`|
|actava-ai/chi-bench|`4444a07fa68a4f1623f841a292a54e284fc8e7f7`|
|greenlight2000/ExploraCoder|`2d869352cf72bb05858b69d8d67f446d97a07263`|
|HKUST-KnowComp/SkillScriptBench|`92cc92baea279d412fcfb1f8b1ef5a2238ff3b45`|
|ElliotXinqiWang/PBTbench|`cef1aa4b8205c91ad7f0b3c5274b37304ff88765`|
|Flask 3.0.0 标签|`735a4701d6d5e848241e7d7535db898efb62d400`|


|重要结论|本地原始位置|
|---|---|
|候选执行结果取 pytest returncode|[GitChameleonBenchmark/gitchameleon/eval_sample.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/gitchameleon/eval_sample.py:98>)|
|官方任务解析器字段|[GitChameleonBenchmark/gitchameleon/data_model.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GitChameleonBenchmark/gitchameleon/data_model.py:8>)|
|Flask provider 替换规则|[extra/flask_3.0.0_provider.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/extra/flask_3.0.0_provider.py:27>)|
|Flask provider 实例初始化及属性文档|[extra/flask_3.0.0_sansio_app.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/extra/flask_3.0.0_sansio_app.py:327>)|
|独立 gold 环境与 DB 比较|[tau2-bench/src/tau2/evaluator/evaluator_env.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/tau2-bench/src/tau2/evaluator/evaluator_env.py:96>)|
|GUI 表格产物比较|[MAGE/osworld/desktop_env/evaluators/metrics/table.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/MAGE/osworld/desktop_env/evaluators/metrics/table.py:260>)|
|HR 空子串反例所在 rubric|[handbook/tasks/hr_crestwood_university_79786c46/tests/rubrics.json](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/handbook/tasks/hr_crestwood_university_79786c46/tests/rubrics.json:6>)|
|GDPevo 只读环境|[GDPevo/data/task_groups/task_group_001/task_group.yaml](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/GDPevo/data/task_groups/task_group_001/task_group.yaml:16>)|
|Torchdata 首条 task_2 原测试|[ExploraCoder/datasets/Torchdata_Manual.jsonl](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/ExploraCoder/datasets/Torchdata_Manual.jsonl:1>)|
|PBT 简入口 F→P|[PBTbench/eval/run_eval.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/PBTbench/eval/run_eval.py:50>)|
|PBT 正式批量逐函数/逐 bug 评分|[PBTbench/eval/run_pbt.py](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_open_world_2026-10-21/PBTbench/eval/run_pbt.py:992>)|


这些代码位置支持正文具体判断，不等于已执行对应环境。固定仓库中的 LICENSE、LICENSE-DATA、ASSET_ATTRIBUTION 和 README 分别保存许可证据；许可判断仅用于访问/再分发规划，没有把未核权限视为已授权。

### A.7 规模口径与实际可用比例

|资源|原始规模/本地已核|规则簇与可信任务比例|
|---|---|---|
|GitChameleon|328题、26库、207 docs URL|10个非空同实体候选组27题，占8.23%；静态核实1组2依赖＋1负对照；完整运行合格率未测|
|MAGE Calc|47原任务、536抽取section|1个拟2+1因证据不足被拒；合格规则簇未证；47题不等于47独立来源|
|τ-Knowledge|97题、698文档；90题有assistant gold动作，占92.78%|215被引文档中156被多题引；真实共享规则数未知，自然来源准入0|
|HANDBOOK公开|3题、51判据|只公开3/65论文题数；三题异公司，公开同规则簇0；1条判据假阳性不推算整体比例|
|GDPevo|24组240题，group001十题已读|已审组是只读计划；其余组的写状态/自然来源比例未知，不能将10/240当全体结论|
|PBT-Bench|Git树100 problem.yaml、40库、125 docs文件|仅bidict四任务定点核验；docs文件数含重复整理稿，不能当125自然来源；规则簇及可靠Oracle比例未测|
|Agent-Diff（前轮）|224题，4服务域|Box真实2+1静态可用但评分需增强；复杂规则正式可用比例未知|
|ConditionalQA（前轮）|652文档；train/dev共2623条有标签任务|613含条件，23.37%；173来源有至少2条件任务，仍须逐规则；纯执行主集比例0|
|SOPBench（前轮）|830题、7份程序SOP|75符合默认SOP约束，9.04%；再固定默认参数62，7.47%；原Oracle未达到主执行可信条件|

“未测/未知”不填成0，也不能填成全部可用。上表的0只用于明确不满足的定义（如自然来源、纯执行），不表示模型成功率。完整通过十门槛的任务/候选还未获得证明；工程资格组不是正式论文样本。

### A.8 冻结与复核记录

本地证据清单 `evidence_manifest.json` 记录本轮原始文件、脚本及报告 SHA256；`integrity_check.json` 记录旧报告证据是否被改动。下载失败清单保留，不以目录存在推定文件齐全。项目 Git 状态复核以 `project_status_before.txt/project_status_after.txt` 为准，本轮只应新增本报告。
