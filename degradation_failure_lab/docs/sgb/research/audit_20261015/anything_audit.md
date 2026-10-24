# Anything2Skill 本地实现与 Clean5 独立证据备忘录

审计日期：2026-10-15；只读目标：`D:/AS/AutoSkill-main`。本文件是主报告的分项证据，不是新实验结果。未修改官方源码、已有 run 或任何 canonical SKILL.md；未调用模型。所有新增文件均在聊天工作区 `audit_2026-10-15/`。

## 1. 身份、版本和证据范围

- 外层研究仓库 `D:/AS/AutoSkill-main/.git/HEAD` 指向 `master`；实际读取并用只读 `git --git-dir=... log -1` 交叉确认 HEAD 为 `ace65737e8d0be08eda1c47d5a8e62f119989ded`，提交时间 `2026-10-14T22:12:44+08:00`，标题 `case005`。remote 为 `https://github.com/lily400/AutoSkill-main.git`，不是官方 ECNU 仓库。
- 实现实际位于嵌套目录 `UP = D:/AS/AutoSkill-main/AutoSkill-main`；实验位于 `LAB = D:/AS/AutoSkill-main/degradation_failure_lab`。该嵌套目录没有独立 `.git`。不能把外层 HEAD 当作官方上游 SHA。
- 官方仓库已独立完整clone到本审计目录`AutoSkill-official-94c47ca/`，实际HEAD为`94c47ca488d4ba4117d20272e66d49b9877e68cf`，提交时间`2026-05-10T15:40:17+08:00`，checkout无改动。历史run清单的164个文件在官方均存在，且164/164与本地UP及历史SHA-256逐字节一致；其中149个Python AST也一致。`AutoSkill4Doc/`与`autoskill/management/`完整核心路径集合均为66文件，无差异且全部含在164清单。故本文对应核心代码结论适用于此固定官方版本；未比较的其它仓库文件不作等同声明。证据为`official_autoskill_comparison.json`，下载代码未执行。
- 本分项沙箱中的git status受访问限制；根代理随后以获批只读git核实：HEAD同上，无tracked dirty，仅用户指定两份既有报告未跟踪（`CLEAN5_REAUDIT_AND_NEXT_STEP_2026-10-14.md`与`DOWNSTREAM_AGENT_READINESS_AND_MINIMAL_PILOT_PLAN_2026-10-15.md`）。这是新增主报告落盘前的状态。
- 搜索未找到 `D:/AGENTS.md`、`D:/AS/AGENTS.md`、目标根 AGENTS.md 或其子目录 AGENTS.md；遵守本会话用户指令。
- 读取用户指定两份报告作为索引，并独立核验原始 runs、输入、manifest、阶段 JSON、注册响应以及 47 个 canonical 文件。报告中的旧结论不当作新的实测成功率。
- 论文实读版本为 [Anything2Skill arXiv v3](https://arxiv.org/html/2606.09316v3)，修订 2026-06-19；方法范围为从异质知识记录编译可复用程序性知识。它有 Base、RAG、Skill-only、Skill+RAG 四配置；不要误写成只有 RAG+Skill。本文没有报告退化鲁棒性或局部规则反事实实验。

## 2. 输入边界：可读、可生成、受支持、相关、能执行是五个不同门槛

### 2.1 工程读入

`UP/AutoSkill4Doc/document/file_loader.py:84-146` 接受单文件或目录，目录递归排序，逐文件形成一个 text unit；`ingest.py:1057-1123` 逐 unit 建 DocumentRecord、章节和窗口。不是将整个目录无损合成一个跨文件推理上下文。

- 文本/Markdown/JSON/JSONL 可按文本读取。文件 JSON 并不必然语义解析；结构化内存 `data` 则经 `ingest.py:873-907` 另一路规范化。把任务元数据 JSON 当作正文读入不等于其内容适合技能提取。
- **PDF、图像、音频、视频、压缩包、二进制文件明确跳过**：`file_loader.py:21-53,185-209`。没有原生 PDF 页面布局分析、OCR 或图表读取。SkillGenBench 若只提供 PDF，不能直接交入并声称已处理。
- `.doc/.docx` 尝试 `textutil`、`antiword`、`catdoc`（`:238-252`）；工具可用性不保证 DOCX 转换质量。Windows 没有自动配置这些工具。
- 对 UTF-8 正常文本 `f.read()` 没有 8 MB 硬上限；8,000,000 字节仅是解码失败后的二进制回退读取上限（`:185-215`），不要误报“所有文件最大8 MB”。
- 目录会排除隐藏目录和 `.git/.runtime/node_modules/.venv` 等、生成的 skill-tree 导航产物（`:54-81,115-169`）；`max_files` 是候选文件计数上限，随后不可读文件会被跳过。有限 `max_documents` 不保证取得同样数量可读文档。
- 空文件/纯不支持二进制产生 no readable text 错误（`ingest.py:1065-1079`）。纯HTML可能被作为原始文本读入，但没有专门 DOM 清理/链接爬取；源码文件可读也不意味着实现了代码仓库语义分析。

### 2.2 内容适用性

`prompts.py:61-80` 明确只规划可操作、可复用的 method/policy/workflow/intervention，主要是叙事、结果、综述、元数据时应返回空；`prompts.py:181-196` 要求证据不足返回 null。五种 asset type 包括 `knowledge_reference`、`safety_rule`，因此不是只支持完整步骤流程。

| 材料 | 判定 | 边界依据 |
|---|---|---|
| 明确操作手册、CLI/API用法及条件例外 | 最适配，但仍需验证window保留与规则正确 | 流程/动作/约束可映射至结构字段 |
| 条件规则、禁止事项、领域判断 | 条件适配，可成为规则或知识参考 | `stages/extractor.py:1022` 只要求workflow、moves、constraints、cautions之一非空，不要求全部具备 |
| 概念/背景知识 | 部分可读但未必有可调用知识；不应强制产Skill | taxonomy 有 knowledge_reference，但操作性过滤仍适用 |
| 纯任务说明、目标/答案格式，无执行知识 | 可能仅复述目标、输出契约；补步骤会依赖模型先验 | 不具备来源支持的完成方法，不能把“写出了SKILL”视为获取知识 |
| 带图布局复杂PDF | 原始接口不适配；先独立冻结转换文本与对齐映射 | 当前文件loader跳过PDF；转换误差是额外因素 |
| 多文件文档、交叉引用集合 | 可逐文件输入；跨文件依赖不保证恢复 | window来自单record，compile键含doc_id；跨文档整合推迟到registry检索/合并 |

**方法层面**要求来源中存在可迁移的动作、约束或判断知识；没有此信息的输入不是靠“Anything”名字就能解决。**实现层面**还受文本读取、章节识别、段落筛选、taxonomy、上下文/候选预算限制。理论上丰富的文档也可能因工程筛选失去关键条件。

### 2.3 长度和结构

`windowing.py:143-157` 以空行拆段；`:270-284` 保留带过程/锚点信号的段，或不超过320字符的普通段。因此长表格/纯说明可能被整个筛掉；这不是模型上下文总长度问题。`:633-638` 默认窗口目标2400字符、section上限10000；`ingest.py:1116-1121` 只传section上限，没有把配置中的chunk=6000传作window上限。2400不是严格保证：单个保留段可超过预算。回退仍使用已筛选的blocks，不会恢复原文中已丢失段落（`:660-706`）。

## 3. 全调用链、任务条件化和 provenance

调用链为 `file/data → text units → DocumentRecord/sections → evidence windows → Plan → Expand → SkillDraft+SupportRecord → document-level compile → SkillSpec → registry reconciliation → canonical Users/docskill/<skill>/SKILL.md → visible tree`。

### 3.1 原方法是生成阶段任务无关

`stages/extractor.py:756-795` 给模型的payload是record标题、domain、source type、metadata、section、heading path、siblings、context snippets、excerpt、taxonomy、max_candidates。`:857-928` 先规划候选，再单独展开候选。没有必须传入具体下游 task instruction 的参数；`task_family` 是生成的能力分类，不等于看到评测题。领域/taxonomy先验也不等于任务无条件：它可显著影响输出，必须冻结并报告。

- **A2S-agnostic**：同一来源组固定文档集生成一次完整canonical bundle，冻结后供该来源各任务复用；生成时看不到任务instruction、verifier、答案或人工gold skill。无语义的文本转换、路径改写、manifest均可外部适配。
- **A2S-conditioned**：显式把任务instruction加入提取payload/提示、任务导向检索或候选选择；必须单独命名、记录新增信息，和同样条件化的baseline比较。不是与原始无任务生成同一个基线。依据测试答案人工删选“最有用”Skill更不是透明格式适配。
- 固定原始生成器但为任务检索已有冻结Skill，是**推理阶段选择**；不得和生成时看到任务混为一谈。检索配置/候选数量也是独立的执行条件。

### 3.2 编译、注册、存储

`stages/compiler.py:185-204` 分组键包括doc_id和能力身份，因此单文档内去重是第一层；`:244-341` 把草稿及supports送入编译提示；`:498-514` 至少有程序性字段与support ID即可保留，缺support会从组内草稿补。ID关联和自报confidence不是逐断言蕴含验证。

`store/versioning.py:2403-2453` 在注册前加载已有库并检索，批内peers也可见；先搜集决策，后应用（`:2484,2602`）。支持 create/strengthen/revise/merge/split/unchanged/discard，更新、合并、弃置会改变可见能力集合。需要对每个来源×文档条件使用独立空SkillBank，冻结所有产物；否则Clean生成过的知识可能泄漏进Degraded，且输入顺序/旧库状态可能成为混杂。

`autoskill/management/artifacts.py:17-33` 导出SKILL或目录文件map；`management/formats/agent_skill.py:192-235` 输出name/description/version等frontmatter及正文；可附safe相对路径resources/files。实际本批47个canonical目录只有SKILL.md，visible tree的references/evidence是另一个投影层；复制整个SkillBank递归扫SKILL.md会同时带入canonical、投影副本与导航父技能，不能混算数量。

### 3.3 provenance强项与实测限制

`models.py:618-662` SupportRecord保存doc_id/source_file/section/span/excerpt/relation/confidence；校验是非空、span范围、confidence取值，不验证每条规则由excerpt推出。`extractor.py:1099-1105` 直接以整个unit文本作为support excerpt。`windowing.py:459-484` 将筛选后blocks用空行拼接，却以最小start/最大end形成包围span。因此span内可以有未曝光段，不能只看span包围目标就认定规则进入模型。

本轮对全部53个support逐项读源：21个excerpt是Document.raw_text连续子串，17个与raw_text[start:end].strip()精确相等；其余不自动判“伪造”，主要符合拼接/空白规范化机制，但说明单一span不足以恢复实际曝光字节。完整window payload、block级映射和每条原子规则的证据位置仍需额外审计。详见JSON的support_checks。

schema没有独立原子rule ID → claim → action映射；不能把53个support等价为53条已验证规则，也不能把47个active等价为47个正确能力。

## 4. Clean5 全量身份、哈希和阶段复算

所有数量均从真实run阶段数组与canonical目录复算，另单独检查当前exports身份；不盲从旧报告的exports叙述。

| case / run | Documents / Sections / Windows | Support / Draft / Spec | CREATE / DISCARD / Final |
|---|---:|---:|---:|
| case001_qsv_select / raecd75e08b34 | 1 / 7 / 2 | 4 / 4 / 4 | 4 / 0 / 4 |
| case002_qsv_sort / rd9ced750fa54 | 1 / 6 / 1 | 3 / 3 / 3 | 3 / 0 / 3 |
| case003_docker_cp / rab9a070dfa59 | 1 / 6 / 1 | 2 / 2 / 2 | 2 / 0 / 2 |
| case004_git_restore / r18307cee4f4c | 1 / 8 / 10 | 17 / 17 / 17 | 14 / 3 / 14 |
| case005_ripgrep_guide / r64cee24fae18 | 1 / 16 / 12 | 27 / 27 / 27 | 24 / 3 / 24 |
| 合计 | 5 / 43 / 26 | 53 / 53 / 53 | 47 / 6 / 47 |

每个`LAB/runs/<case>/clean/<run>/official_result.json`状态completed，execution exit_code=0。五个input实体与input_manifest所列hash、raw_source实体hash完全一致。五run的upstream_before/after相等，且每run记录的164个当前实现文件hash全部匹配。artifact_manifest实际逐文件核对分别169、137、116、472、749条，共1643条，未发现missing/hash mismatch。这证明落盘产物和声明清单一致，不证明所有历史模型上下文或源码版本均完整可追溯。

53个Spec的`metadata.source_draft_ids`全部长度1，没有本批多草稿合并样本。39/47 canonical含“Example Therapist Responses”；`compiler.py:126-139`有固定therapist渲染，prompts中也有治疗术语（`:72-78,192-196`），是可定位实现偏置，不应据此直接判断下游失败。

**与旧报告不同，本轮实际exports没有复现44个副本错配。** 五个verification的case_id/run_id均正确；四个非Case001目录各11个JSON与Case001同名文件无一字节或解析后语义相同。五个skill_files.json哈希也各异（详见原文件和inventory）。因此旧CLEAN5报告的“当前导出错配”已经不符合本轮读取状态，不能继续把它列为当前阻塞。修复何时、由谁发生未在本分项追查。Case001/003/004/005当前export verification=PASS；Case002=PARTIAL，唯一false check为model_stage_ingest，实际official_result仍completed且全部产物哈希通过。应将“缺少成功的ingest模型阶段标记”与“生成未完成”分开，不重启网络排障，不据PARTIAL计算技能质量失败。

输入文本长度（Python统一换行后的字符数/原始字节）分别为4738/4795、5271/5381、6006/6006、7082/7082、40689/40701。长度不等于可用规则数，尤其qsv表格规则可能在进入模型前被过滤。

本批是5篇文档，但qsv select与sort共属qsv来源生态；作为扩展集统计，至少同时报告“5文档 / 4工具来源组”，不能默认5个相互独立生态。源文件均为重建固定官方来源，历史manifest表明`paper_snapshot_verified=false`，不要称论文原始数据快照。

## 5. 已独立复核的典型Clean错误与注册质量门

### 5.1 语义/证据错误

| 案例 | 可直接核验的来源/产物差异 | 证据性质与限制 |
|---|---|---|
| qsv select | `正则表达式列选择/SKILL.md:33-34,57-58`分别有选择/排除，但`:80`统一输出契约为输出匹配列 | Final内部矛盾；不是已执行负迁移 |
| qsv sort | 原`sort.md:40-44,52`有numeric/natural优先级、ignore-case例外、unique与shuffle交互；现1个Window没有这些完整规则 | Clean前端曝光失败；不适合把此规则当正确Clean后再测退化增量 |
| Docker cp | 原`container_cp.md:57-61`的目标不存在且尾斜线错误在“源为文件”分支；`docker-cp-路径语义判定/SKILL.md:86`脱落这一条件；`:34`局部正文仍有条件 | 同一技能正文正确、Cautions过概括并存；应以原子命题判分 |
| git restore | 原`git-restore.txt:25-26,36-42`明确source缺省时才由staged决定HEAD；`从指定-tree-恢复工作区文件/SKILL.md:27,58`在显式source技能内写staged从HEAD恢复 | 可设计v1/v2 final-state反事实；本轮未运行agent，不称因果成立 |
| ripgrep | 原`GUIDE.md:536-538`明确replace只改输出不改文件；`ripgrep-替换与配置预处理流程/SKILL.md:66`说可能修改文件，`:41`也暗含修改文件用途 | 无支持的副作用表述；同run还有正确替换技能，不得合并成整体“通过” |

上表 canonical 完整路径统一为`LAB/runs/<case>/clean/<run>/SkillBank/Users/docskill/<文件夹>/SKILL.md`。`clean5_canonical_texts.md`保存全部47份读取文本及每份原始行号，`clean5_inventory.json`保存绝对路径和SHA。仅对上表代表规则进行独立语义核对，不把先前报告129个错误数冒充本轮复标数量。

### 5.2 注册返回的离线确定性重放

本轮从model_calls stack定位全部53个成功register模型响应；47个响应`finish_reason=length`且标准`json.loads`失败，对应47个CREATE；6个响应是完整JSON、action=discard，对应6个DISCARD。对53条内容运行当前官方`autoskill/utils/json.py:23-78`解析函数：前47条均返回**内部list**，后6条返回含action的root dict。

`AutoSkill4Doc/store/versioning.py:1378-1384`将parsed送入maybe_json_dict；没有合法action时默认create。因此这里存在可实证的“语法截断 → 内部数组抢救 → 缺root decision → 默认CREATE”路径。**active状态不能当成LLM质量审核通过**。本轮没有修解析器；修复需另名A2S变体，不能静默覆写B0。

`clean5_register_response_audit.json`逐条存response_path、HTTP call编号、finish_reason、strict JSON结果、官方parser输出类型/action，便于不调用模型复验。

## 6. 加载能力与外部执行器对接的边界

本轮以`python -B`在只读原目录调用官方`load_agent_skill_dir(..., user_id='docskill', include_files=False)`，47/47成功。加载后的SKILL全文与换行规范化后的原文件一致；原文件有CRLF，不能用Python规范化字符串的hash与原始字节hash不等就误报内容被改。调用只在内存产生对象，没有LocalSkillStore实例化、没有写回文件。

**重要差异**：`agent_skill.py:301-310,574-591`只将`## Prompt`到下一`# / ##`标题前文本提取为Skill.instructions；本批47份instructions均不含后续`## Workflow Steps`等结构章节。`autoskill/render.py:83-117`只把name/description/triggers/resources路径与instructions注入上下文，并可按预算截断。那些章节的内容有时已重复在Prompt里，但不能未经对照就说全部结构规则已送达Agent。

所以“用AutoSkill官方chat loader注入Prompt”和“把原样SKILL.md目录安装给Claude原生技能发现”是不同加载协议。对SkillGenBench应优先保留全部canonical文件字节及结构，外加不可见manifest；不要为了沿用AutoSkill loader而裁剪其它章节。规则缺失若由裁剪导致，应归为适配/加载错误，而不是原始生成文本缺失。

`LocalSkillStore`加载会创建索引、可能规范化目录/ID/usage持久化（`stores/local.py:279-299,967-1080,1102-1150`），**不要直接把冻结run作为可写store打开**。它识别Users/<user_id>与Common，不会自动把docskill技能变成默认u1用户技能。

当前interactive执行只调用文本`complete/stream_complete`（`interactive/session.py:1200-1265`）；`llm/base.py:4-39`协议就是system+user→text。已有实验工程根目录没有downstream_pilot、任务fixture或final-state verifier；两份先前报告中的trial/Oracle只是计划。生成exit_code=0、47文件可解析、甚至检索命中，均不是下游执行成功。

## 7. 为什么保留这个生成基线，何时更换

**保留为主要被审生成器，条件是不要把它当Gold或最佳方法。** 它的window、plan、expand、draft、spec、registration日志提供比一次性Doc-to-SKILL更细的错误定位；中间规则字段和来源指针适合研究条件/否定/例外丢失。Clean现有错误反而要求先证明测量链的区分能力。

成本与混杂也明显：多轮模型调用、taxonomy/语言偏置、window选择偏差、compile和register的二次改写/弃置、技能粒度与检索竞争、全库状态和顺序效应。不能把“多阶段复杂”当效果优势。

最低比较集应包含同一生成模型/资料/预算下的task-agnostic直接Doc-to-SKILL；再加正确标注条件化的naive_prompt及一个可复现的公开Doc-to-Skill方法。知识/短规范/概念材料上，简单保真压缩可能优于A2S；是否更换只能基于预注册Clean可支持规则覆盖、错误类型和下游正控制，而不是只看总体成功率或已有投入。

本分项不声称另一公开方法更优；其代码接线及数据条件由SkillGenBench审计分项比较。若A2S在Clean已无法提取目标规则，而简单直接生成/DirectDoc能，则该来源不能用于“Clean正确→退化错误”主分析；可以保留为前端失败诊断层，不得选择性隐去。

## 8. 对主研究方案的约束和停止规则

1. 原方法接线使用来源组冻结bundle，不随task重新生成或按答案删选。为防跨条件污染，各条件独立空SkillBank，记录所有候选、discard、最终技能，而不是只保存通过者。
2. **读取文件 ≠ 语义支持 ≠ 规则正确 ≠ 与任务相关 ≠ 执行器实际采用**。任何环节失败先记对应层原因，不能直接下降到生成质量。
3. shared rule研究需至少2个真依赖任务+1个非依赖任务，Clean5当前没有已建立独立Oracle的这类任务集；已有规则清单`analyst_checklist`不是独立金标准。可作补充研究开发集，不是已完成的下游benchmark。
4. 首个低成本可证伪假设：当明确正确的目标知识/动作由同一加载路径送入固定执行器后，Oracle能稳定区分正确与特定错误动作；随后才比较Original/Corrected。若正确提交物/动作都无法过Oracle，停止，不运行付费P4。
5. 对已有Clean技能最清楚的诊断候选仍为git restore显式source+staged（目标规则决定恢复v1或HEAD v2），但它是独立Clean5扩展任务，不能算SkillGenBench官方成绩。任何新任务、局部修正版与反向破坏版均另存，保持原47份哈希。
6. 对纯PDF/OCR布局退化研究，先冻结并审计转换器，否则测到的可能是PDF不被读取或解析器失败；对“信息全部删除不可恢复”单列不可辨识条件，不当作生成器鲁棒性失败。

分项裁决：**Anything2Skill作为规则退化研究起点与受评生成器为CONDITIONAL PASS；现存Clean5已成功下游执行为FAIL/未有证据；provenance可用于追踪但不足以自动证明语义为CONDITIONAL PASS。** 是否进入SkillGenBench需结合其数据、安装、执行与Oracle审计，不能由47份文件存在推断已接通。

机器文件：`clean5_inventory.json`（47份文件与全部输入/阶段/hash）、`clean5_register_response_audit.json`（53个注册响应离线解析）、`clean5_canonical_texts.md`（原文件逐行只读文本镜像）、`inspect_clean5.py`与`inspect_clean5_loader_register.py`（离线复核）、`official_autoskill_comparison.json`及`compare_official_autoskill.py`（官方固定版本164文件比对）。所有检查均不运行模型。
