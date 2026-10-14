# 五个 Clean Case 的完整规则级 Skill 质量审计

审计日期：2026-10-13。研究目标：面向退化文档的高质量 Agent Skill 生成。本报告为 Codex 的独立初步分析，不是人工金标准、工具行为认证或论文结论。

## 1. 结论先行

五个案例各找到且独立核验了一个真正完成的 Clean 运行，共 5 个 Document、26 个 Window、53 个 SupportRecord、53 个 Draft、53 个 Spec、47 个正式 canonical Skill。所有 47 份 canonical `SKILL.md` 均完整阅读，不能用 104 个物理 `SKILL.md` 文件计数代替：其中还包括 47 份可见树副本和 10 份导航文件。正式集合含 12 个 `knowledge_reference`，不是 47 个均可直接执行的程序。

原版 Anything2Skill **可以保留为冻结的、未修补的比较基线（CONDITIONAL GO）**，但不能称为质量合格的 Clean 技能库。主要发现不是单一问题：

1. 输入快照到 `DocumentRecord.raw_text` 完整保留；执行关键规则在 Section→Window 的筛选/分组阶段损失。五份文档都有此现象，不能把它归因于人为退化。
2. Extract 不仅漏信息，还引入条件和输出语义错误。例如 select 排除列却承诺输出匹配列、Docker 文件源限定丢失、Git 显式 source 被 staged 默认覆盖、ripgrep 替换被误说成可能修改文件及 auto 被误说成通用编码推断。
3. 对全部 53 对 Draft→Spec 的操作字段比较，未观察到针对上述问题的实质性语义修复；Register 保存的内容和 Spec 相同；47 份 canonical 正文均包含对应 Spec 的完整正文。
4. **47 次 CREATE 全部通过截断响应的默认创建路径。** 成功返回的分类请求共 53 次，47 次 `finish_reason=length`、完整 JSON 无效、官方容错解析器返回内部 `[]`，随后默认 CREATE；另外 6 次完整 JSON 为 DISCARD。不是“模型完全没判断”，而是应用没有获得完整有效的准入判定。
5. Git 的两个 `--patch` 候选互相视为重复而双双丢弃；最终留下语法/旁注，却没有专门的交互式 hunk 操作技能。17→14 和 27→24 的减少均为 DISCARD，不是合并或产物失踪。
6. Case002–Case005 现有导出目录的 **11 份 JSON 均与 Case001 对应文件逐字节相同**，连 `PASS` 标记也相同。它们不可信。本审计未采用这些导出来判断技能质量，也未修改它们；错误发生时间、操作者或具体复制机制为 UNKNOWN。

有明确的正面结果：列位置选择/反转、Docker 目录 `/.` 分支和本地符号链接规则、Git 默认源与目标区分及唯一 merge-base、ripgrep 类型定义的命令局部性、二进制三模式等均有正确保留。正确技能与矛盾技能同时存在时，不以正确条目抵消错误条目。

## 2. 范围、证据和统计约定

### 2.1 真实读取范围与证据优先级

根目录：`D:\AS\AutoSkill-main`；实验目录简称 LAB=`D:\AS\AutoSkill-main\degradation_failure_lab`；官方源码简称 UP=`D:\AS\AutoSkill-main\AutoSkill-main`。下文的相对路径均明确相对 LAB 或 UP。

本次重新读取：五个现行 `cases/*/{case.json,conditions.json,rules.json,inputs/clean.json}`、`data/catalog.json`、对应来源 manifests、五份原文全文；13 行运行账本及 6 个现存运行目录身份/状态；5 个成功运行的 invocation、execution、status、official_result、config、inputs、input_manifest、sources、model_calls、原始 HTTP 请求/响应、pipeline 日志、四阶段 result 及 decisions；全部 47 份 canonical 正文和关联 evidence manifests；现有五个导出目录的原始文件。原始 Plan 的 26 个返回、全部 53 个 Draft/Spec 字段及 53 个注册决策都纳入检查，而非只读最终名称。

优先级：固定来源及哈希 → 运行输入快照 → 官方原始阶段/HTTP → canonical 文件 → 派生导出。旧研究报告不作为本次事实依据。每份正式文件和原始证据路径在机器表中，`protected_evidence_hashes.json` 保存交付前证据哈希用于只读性复核。

所有选中运行输入 SHA256 与当前固定来源、输入清单、sources 一致；`raw_text` 等于输入 UTF-8 解码后 `.strip()`；官方 before/after 哈希相同且匹配当前被记录源码；5 份产物清单合计 1,643 项哈希核验无不一致。这证明这些检查覆盖内的身份与文件一致，**不证明采集前历史或未纳入清单的文件没有变化**。

|案例|固定来源文件|Commit|字节/行|
|---|---|---|---|
|Case001|qsv `select.md`|257ae7b38738688138dc430c2ccb4eef8766f3fc|4,795 / 179|
|Case002|qsv `sort.md`|同上|5,381 / 72|
|Case003|Docker CLI `container_cp.md`|e4078058de0a9f4d5cb65f946f4b8a090e19fffe|6,006 / 131|
|Case004|Git `git-restore.txt`|a52a24e03c8c711f1d5e252fba78f9276908129b|7,082 / 222|
|Case005|ripgrep `GUIDE.md`|4649aa9700619f94cf9c66876e9549d83420e16c|40,701 / 1,022|

官方 URL、来源 SHA、原始本地路径完整保存在 `run_inventory.json`。所有来源声明 `RECONSTRUCTED_OFFICIAL_SOURCE`、`paper_snapshot_verified=false`；这是本地固定重建来源，不冒称论文原始数据快照。本轮未重新下载文档或做许可证法律判断。

### 2.2 运行选择及历史限制

选择规则先于语义评价：case/condition/run/input 身份一致、exit_code=0、state=COMPLETED、official status=completed、无阶段错误；如果多个满足则按 execution.ended_at 最早选主审计，其余列为重复。当前每案只有一个现存成功记录，未按技能质量择优。

账本 13 行中 6 个目录现存，7 个目录缺失；缺失历史仅保留账本声明，失败原因/内容 UNKNOWN。两条 `case004_git_reset` 不是 `case004_git_restore` 的同源重复。现存 Case005 `r0c7bea4cc4ac` 明确失败：43 次 HTTP 成功、观察到 202,146 token，后续被外部预算限制拦截，官方错误包括 `P0 external observation budget exhausted`；不纳入成功生成质量分母。所选 Case005 为 `r64cee24fae18`。

Case002 的 13 次尝试中 3 次传输失败，Case003 的 9 次中 1 次失败；Case002 首次 outline 调用失败后使用规则解析，另有 Compile/Register 重试；Case003 有 Register 重试。成功不是全程无异常。具体时间和错误见 run inventory，未重新诊断 SSL。

### 2.3 判断与分母

- CONFIRMED：文件、原文和/或离线代码解析能直接证明该文本/工程断言；不自动等于 CLI 已运行证伪。
- INFERRED：组织冗余、逐步命令构造可能误执行等合理风险，尚欠执行证据。
- UNKNOWN：引用转义的 shell 等价性、运行环境默认行号、历史丢失细节、模型内部推理等无法确认。
- NOT_ERROR：父子技能适当共享规则、Docker“按上述规则存在”的限定、安全提醒等复核后不作为错误。

E1 来源规则遗漏；E2 条件/范围失真；E3 否定/例外/分支；E4 动作/输出或内部矛盾；E5 无来源支持的附加规则；E6 参数/执行细节；E7 拆分重叠；E8 证据/身份；E9 准入与解析；E10 模板/组织标签。

规则表区分 Window FULL/PARTIAL/ABSENT，以及最终集合 correct/partial/omitted/mixed/uncertain。`partial` 包括概念存在但执行选项、条件或例外不足；不能用关键词命中改判 correct。缺少一项非职责规则是集合覆盖不足，不自动给所有微技能判错。来源不支持的保守建议与来源不支持的强制禁用条件分别对待。

原有 35 个研究者检查项全部复核，`checklist_review.csv` 保留原文、来源准确性和拆分映射。补充单元来自完整来源而非从生成结果倒造金标准。一些相互绑定的参数/条件仍为复合操作单元；目前没有独立人工复核、一致性系数或严格全量原子分母。因此报告描述性计数，不给“原文全部规则错误率”。F断言、O规则缺口、S系统机制、G重叠组可关联，不把它们加总成统一效果分数。

5 个文档是目的性样本，qsv 两案还来自同一工具；47 个技能、规则单元和 203 次请求均嵌套其中。无显著性检验、总体失败率推断或“长文档必然更差”的因果结论。生成质量、下游执行成功率、错误传播因果机制是三种不同测量；本轮只提供第一种及部分工程机制证据，后两者未测量。

## 3. 各案例质量分析

### 3.1 Case001 qsv select

来源示例清楚区分 `1,4`（27–30）与 `1-4`（33–36），正式 S01 保留；末列 `_`、反转 `_-1`、列重排重复也保留。R2 原本把排除和同名列索引合为一项，现拆分：`Foo[2]` 在来源明确为第三个同名列（57–60），Skill 仅留下命令/索引名称，解释不足。R4 同时包含正则排除和排序，必须拆开审核。

主要矛盾：正则 S04 的操作说明包含 `!/pattern/` 排除，但 L80 输出契约为“输出匹配正则的列”。正确需求应是排除这些列后的结果，不能要求它们出现在输出中。Plan HTTP002 已在该候选 success_artifact 给出这一方向，Draft→Spec→Final 保留；不是 Compile 首次引入。此为来源/内部文本 CONFIRMED，尚未执行错误命令。

R7 的 no-headers、delimiter 单字符、output 全部在原文参数表却未进入窗口；按名称选择需要表头（16–20）的 342 字符段落也被预筛剔除。seed 整数约束丢失。S03 把“冲突时需要引用”改成“仅在冲突时才使用引用”，是无依据收窄；来源示例反斜杠在最终命令缺少，具体 shell 等价性 UNKNOWN，不宣称已经执行失败。

两个窗口并非有一个失败：W02 主要为 Usage/help/navigation，Plan HTTP007 明确返回 `{"skills":[]}`，因此没有 Support/Draft，阶段 errors 为空。没有可复用程序候选本身可以合理，不能仅按数量认定故障；关键缺口是进入两个窗口之前的规则筛选。

### 3.2 Case002 qsv sort

三个技能为内存排序路由、外存切换、结果校验。来源表中的 natural 优先 numeric、ignore-case 生效条件、unique 比较一致性、random/unique/reverse 交互、faster 不稳定性、no-headers 首行规则均未被完整保留。最终“自然序、数值序”等名词不能替代对应标志和组合约束。原检查项没有覆盖 seed/rng/jobs/memcheck，本次补入。

来源 16–18 说数据可能无法放入内存时考虑 extsort，S02 则禁止能放入内存时使用它，Plan 已将单向建议变成必要条件。S03 仅凭介绍中 `sortcheck` 名称，补出可校验自然/数字/逆序/唯一/随机等顺序的接口能力；这是本来源未支持，不能冒称运行时均不支持，后者 UNKNOWN。

Sort Options 合并段落 1,269 字符且没有所需过程信号，被 320 字符阈值路径剔除。故“工程完成、三个技能”不意味着完成参数规则编译。表格比例和首次 outline 传输失败后的规则回退同时存在，不能从这一个案例分离它们的质量效应。

### 3.3 Case003 docker cp

目录源/目标类型分支以及本地符号链接 default/-L 很多内容保留良好。两个技能分别是知识参考和微技能，不能因为没有全流程命令就认定参考技能失效。

关键矛盾在路径参考 S02：Prompt L34 正确限定“文件源且目标不存在且以 / 结尾时报错”；Prompt L38 又正确允许“目录源→不存在目标，创建目录”。但 Cautions L86 只写目标不存在且以 `/` 结尾就报错，删除文件源前提。该偏差最早在 Draft，可由同一 Skill 内部两种分支直接证明。

“SRC_PATH 与 DEST_PATH 需按上述规则存在”有上下文限定，不能读成两者必须预先存在，本次列 NOT_ERROR。未保留的集合规则包括运行/停止容器、容器根/本地cwd、所有权和 `-a`、不创建目标父目录、冒号路径、tar 流及特殊路径限制。旧 R6 简写 `/.`，必须补上目录源与现存目录目标的条件；旧 R7 的 `-L` 必须限本地来源符号链接。

### 3.4 Case004 git restore

正确保留默认来源、恢复目标、唯一 merge-base 和最多省略一方、progress 强制显示、merge 的 index→worktree 限定、source 不可与 ours/theirs 或 merge 并用等。多个微技能分别覆盖不同目标，不能仅因名字都含 restore 就算重复。

三个重要问题：

- 显式 tree S03 L27/L58 声称“若同时给出 --staged，则从 HEAD 恢复内容”，而同一 Prompt L28 仍执行 `--source=<tree>`，来源 35–42 的默认 HEAD 必须在没有显式 source 时解释。正确源规则已入窗口，Plan HTTP011 未含该错误分支，Draft HTTP012 首次明确引入。
- ours/theirs S10 把 index 的未合并状态限定成工作树已有冲突标记，Plan HTTP020 的禁用条件已有此收窄。该等同关系没有来源支持；不通过“名称含冲突”推定正确。
- quiet S14 L56 绝对说无法看到进度，遗漏来源 70–75 明确的 `--progress` 覆盖。S07 同时正确表达覆盖，构成跨技能不一致，说明不能只看工作流主动作。

两个专门 patch Spec `4f818099-0f3d-5f99-83e5-df551a9bf486` 和 `eb09b547-e592-5aab-9788-a88cbf862adb` 在 HTTP054/055 各指对方为重复，被同时 DISCARD。第三个 discarded 为联合目标候选 `039a48d6-70fe-5e3c-907c-4903bf7d77f0`，已有保留的联合目标技能，不等同前两者的功能丢失。S01/S02 仍有 patch 语法/旁注，所以结论仅为专门操作候选双丢，不说 patch 的每个字都消失。

窗口缺少 overlay、ignore-unmerged、稀疏匹配、子模块条件/破坏性副作用、pathspec 文件分隔语义等。部分 OPTIONS 段落短且通过预筛，仍因围绕 `stage` 等锚点分组而未入最终窗口；所以不是统一的长段落截断。`--pathspec-file-nul` 的原文是“Only meaningful with”，不推定不带 from-file 必然运行报错。几个“先执行再追加 source”的步骤暂列 INFERRED，因为也可能是在描述命令构造。

### 3.5 Case005 ripgrep GUIDE

这是多主题教程而非短命令帮助。正确部分包括 -F、无路径/指定目录、四类默认过滤和单独开关、类型定义的命令局部性、配置行格式、编码的详细参考 S17、三种二进制模式 S02、mmap 检测差异 S03。这些正面结果不能被严重问题遮蔽。

关键错误及阶段：

|来源|生成矛盾|最早证据|
|---|---|---|
|536–538：`will never modify your files`|S09 L66“替换操作可能修改文件内容”；S10/S11又正确说不改文件|明确断言在 Draft HTTP011；Plan HTTP007 已有文件修改主题暗示，不能把暗示当完整断言|
|642–667：ASCII兼容假设、UTF-16 BOM 特例|S12 把 auto 泛化为未知编码自动推断，并保证无需指定仍返回匹配；与S17冲突|Plan HTTP029：只有编码介绍、还没给下面的行为列表的窗口产生此候选|
|547–550：RIPGREP_CONFIG_PATH 启用|S16 L16/L86 保存后默认生效，没提供变量前提|启用段先从Window缺失；Draft 又新增“保存后生效”的不充分操作|
|474–503：replace改匹配部分，-o控制输出片段|S08 L26/L52 把-o写成替换范围开关|Draft；同一约束L61又正确描述replace|
|662–684：none关闭所有编码含BOM|S21 L59 无条件继承“除非文件带BOM”例外|Draft 分支合并|
|176–202：hidden/text扩大搜索范围|S19 L73“成功搜索到…匹配内容”不接受合法零命中|Plan；启用范围不能保证模式存在|

此外 S10 禁用整行替换却又提供整行工作流，S11 以替换或配置为入口却排除无需持久化的预览需求，S04 声称限单文件但给无路径递归命令。较高优先级 ignore 的白名单示例被 S06 改成白名单生效的必要条件。源文档只有单目录例子，不支持 S23 禁用多个不相关根的限制；是否 CLI 支持多根本轮不外查也不实测。

Source 的 never 段只有 185 字符，通过段落筛选，但窗口分组没提供；配置启用段 416 字符在预筛阶段被丢弃。命名捕获、no-config、预处理器 `--pre`/参数/stdin/PATH/透传/`--pre-glob` 等关键执行接口不足。反之，常用选项完整列表进入 W12，Plan/扩展只留下 i/S/c 三个例子，其余 FULL→omitted 属 Extract 覆盖缺口。S24 是预处理概念技能，不能凭“正确执行预处理”的输出承诺就认为接口可执行。

共有 27 Specs，3 DISCARD：手动过滤复合候选、另一 glob 候选、另一整行替换候选。Final 24，非随机漏文件。多个主题来自窗口上下文的全局小节标题，正文证据却没有相应细节；这为“借助标题/模型先验补写”提供线索，但模型内部原因仍 UNKNOWN。

## 4. 阶段传播与代码证据

### 4.1 Window：不是原文丢失，也不只是表格问题

UP `AutoSkill4Doc/document/windowing.py:270–285` 把段落按 dialogue、过程/锚点信号、长度≤320 过滤；没有专门 `if markdown_table` 剔除语句。其默认锚点/优先标记（43–108）包含治疗/会谈词和 `stage`。随后 `_group_indices`、邻近段合并、边缘裁剪及 fallback 决定最终窗口。

UP `AutoSkill4Doc/ingest.py:1117` 调用 `build_windows_for_record` 时只传 strategy 和 max_section_chars；该函数 `windowing.py:633–639` 的 `max_chars` 默认 **2400**。不能把 LAB 配置中的 `max_chars_per_chunk=6000` 直接当实际 strict window 大小。2400 也不是每个窗口绝不会超过的硬截断保证。段落合并/过滤产生的 span 不能当逐句对齐。

本轮只在内存中以存档 DocumentRecord、原版纯函数、recommended、max_section_chars=10000 复算窗口；5/5 与原始 Window 全对象一致。没有调用 Ingest pipeline、模型或写回窗口。`window_paragraph_diagnostics.csv` 保存全段落筛选诊断，字符串包含只用于解释代码路径，不用于自动判定规则语义。

### 4.2 Extract：已有证据仍会错误归纳

有两种不同现象：(a) Window 没提供规则，之后缺失/凭标题补写；(b) 正确限定已经提供，Plan/Draft 仍改坏。Docker 源类型、Git source 优先级、select 正则排除属于后者，不能统称全部由窗口造成。某个 Source 在其他 Window 存在，也不等于生成当前候选的 Window 已提供。

SupportRecord 在 `extractor.py:1105` 使用整个 unit_text 作 excerpt。同一窗口多个技能分别有支持 ID，但共享整段摘录；本轮核对 47 个 Evidence Manifest 的 skill/support/doc ID 及 quote 与 SupportRecord 一致。该关联不是句子级 entailment，0.9 confidence 不是人工裁定正确率。尤其 ripgrep 配置启用条件不在相应窗口时，一个完整 ID 链仍无法支持“保存就生效”。

### 4.3 Compile 与 Final：规范化不等于纠错

`stage_field_changes.json` 对 53 个 Spec 与来源 Draft 比较；主要变更是名称、description，另有一个 objective 的命名表述及一个 prompt 的措辞变化。workflow/constraints/cautions/examples/output_contract 等操作字段未变；未发现把上述错误修复的实例。此结论限本批记录，不声称 Compile 永远不能改语义。

53 份 decision.skill 与 Spec 的非metadata字段一致；47 份 canonical 完整包含对应 skill_body，因而不能把错误都推给最终文件渲染。模板标题 `Example Therapist Responses` 和 `Therapist/Output` 来自 `compiler.py:131/136`，39/47 存在（各案4/4、1/3、2/2、12/14、20/24），是确定性领域模板残留；无示例的8份没有这个标题。不等于其中命令自动错误，更没有证明它降低下游准确率。

### 4.4 Register：容量、解析与准入问题分开

UP `store/versioning.py:68–76,101–117` 为阶段复制 client 预算：无 hits 分类 256、一般分类 768、层级 128。本批 53 次成功分类请求均实际 `max_tokens=256`，不能用全局 16384 否定截断。47 次截断中，严格 JSON 解析失败，原版 `autoskill/utils/json.py:23–99` 容错解析完整内部数组为 `[]`；它不抛异常，JSON repair 不触发。`versioning.py:1378–1384` 将非字典转空字典、非法action默认 create、reason回退为action。离线对原始响应逐条重放该解析，47 次与磁盘 create/reason=create 一致。

注册 prompt 确实要求核查证据/冲突，也提供部分候选及同组 peers；不能写“完全没有检查指令”。但完整准入结果没有被成功消费，且 no-hits/局部peer并不构成对全库逐规则一致性的保证。截断可能影响拒绝/合并判断，但本轮不能证明某项语义错必然由它造成：这些错早在 Extract 存在，也不能知道完整未截断输出会是什么。

Git patch 双弃是另一个问题：它的 HTTP054/055 均完整可解析，不归因于256截断；是各候选局部冗余判定缺少最终覆盖检查。`register_decision_audit.csv` 保留全部53行，避免只看成功保存的47个产生幸存者偏差。

## 5. 跨案例比较与风险界限

|维度|重复观察|允许的结论|不允许的推断|
|---|---|---|---|
|Window筛选|5案都有来源操作信息未完整提供|当前规则驱动输入选择与CLI文档不完全匹配|所有表格都会失败；领域偏差已被因果实验确认|
|条件/否定|select排除、Docker源类型、Git默认/覆盖、rg不改文件/编码例外|错误类型跨多个案例出现，值得研究条件保持|可外推为一般发生率，或均由同一原因造成|
|Compile|53对操作字段保持|本批没观察到实质性修复|模型绝无修复能力|
|Register|47默认创建、6有效丢弃|完成状态不能代替有效准入|47个技能语义全错；截断必然造成每个内容错误|
|结构差异|qsv参数表、Docker嵌套分支、Git选项手册、rg长教程不同缺口|可设计后续机制假设|长度、领域、时间、主题数、预算、网络回退已被独立控制|
|证据/模板|5案共享粗粒度支持与治疗模板|工程追踪可用，但不是语义验证|存在ID或0.9 confidence就已被证据支持|

五案均完成、输入和中间产物保留、命令多样性及部分复杂条件正确，是原版框架作为可观测基线的优势。缺点是输入保真、候选归纳、条件约束、准入各层都存在失效；没有独立且严格的比较分母，不能用一个分数判“最主要问题占比”。

工程层可修复项：导出身份校验、准入 schema/截断处理、默认创建策略、确定性模板、候选双弃后的覆盖检查、证据精确定位。方法研究层：局部窗口如何保留跨段条件、正确动作与约束共同编译、未知信息如何拒绝补全、局部正确与跨技能一致性。更改工程层仍须单独版本化，不能静默替换原始基线。

未来退化可能放大长段落/表格损失、否定句丢失和条件跨窗问题，这只是待检验假设。初期不宜用已严重丢失的 qsv sort 组合参数、Docker 全局路径/所有权、Git overlay/submodule、rg 配置启用/预处理接口作为“退化增量损失”主终点，存在地板效应。

适合后续从Clean保留完好的局部规则中挑选：select `1,4` vs `1-4`、Docker 本地链接 default/-L（锁定适用范围）、Git 唯一merge-base、rg type-add命令局部性。首个退化方向建议是**对可定位、Clean已通过审核的参数/条件短句做局部删除或邻接破坏**，另配同长度无关段落对照；不能直接删除已漏掉的内容，再把无变化解释成鲁棒。本轮只提出方向，不创建退化文本、不设计/实现算法、不运行实验。

独立“文档→Skill”基线值得在下一轮批准后加入，用同一源、条件、模型、预算协议和来源规则验证；作用是区分框架特有输入/准入缺陷与生成难题。不以 DirectDoc vs FrozenSkill 下游对照替代当前核心研究问题。

## 6. 成本、配置与未知项

五个选中成功run合计203次HTTP尝试、199次成功，成功响应记录的token总计638,946。此为历史已观察usage，不是本次调用，也不是账户全成本；失败调用可能存在未观察计费。金额接口未提供，**UNKNOWN**。现存失败run和已删除历史没有纳入这一分母。没有再次调用付费API。

五案共同配置记录 model=`deepseek-flash`、OpenAI兼容适配层、thinking disabled、timeout180、全局 max_tokens16384/input_chars100000、hashing256、recommended实际strict、workers1/retries1、每unit最多4候选、无max_units上限、section10000；预算依次32/200000、32/200000、32/200000、100/200000、150/450000。register阶段覆盖预算见上节。封装器 snapshot/manifest 和全部 request 实际预算保留在run inventory，不将当前公共config冒充全部历史配置。模型名称是响应标识，不足以证明跨日期供应商后端权重完全一致。

尚未验证：CLI二进制与固定文档版本一致性；引用/平台差异；全部技能的实际执行率；检索选中哪个冲突技能；模型内部致错原因；7个缺失运行原始内容；来源是否论文原始快照；真实账单；错误随人为退化增加多少；任何修复方案是否有效。当前审计不能给这些填数。

## 7. 唯一优先的下一阶段任务

**任务：建立并人工复核一个小型、版本固定的来源原子规则验证集，完成 Clean 基线准入校准。**

原因：目前最大研究风险不是缺少更多生成数量，而是把工程PASS、粗粒度引用和未原子化清单当成质量真值。先校准测量，可以同时保留正确能力、定位已错边界，并避免后续退化实验的地板效应和误判。本报告CSV是待审计材料，不直接成为真值。

建议该任务的验收标准（需用户另行批准实施）：从五案各选至少4个操作边界单元，覆盖正确、遗漏、条件/否定冲突；每条保留精确来源行、输入状态/前提、动作、预期输出或副作用、反例边界；由人工复核并记录分歧，不把本报告自动标签作最终裁决。对能执行的规则，先确认固定版本工具，在隔离临时目录中以无模型测试建立确定性反例；不能执行者标UNVERIFIED并排除运行正确率分母。至少保留两条Clean完整正确且可执行的退化目标；分别汇总文档覆盖、技能一致性和执行结果，不合成总分。

停止条件：交付该小型验证集、人工审核记录和无模型验证结果/明确不可验证项后停止；不改原版、不要生成新Skill、不要启动大批量退化。若工具/版本不可得或人工审查未完成，保持条件性状态，不把未知项判成功。**本轮到本报告及审计表交付即停止，以上任务尚未实施。**

## 8. 交付文件、复核方法及辅助工具说明

主报告：`docs/research/FIVE_CASE_CLEAN_SKILL_QUALITY_AUDIT.md`。

分析目录：`results/analysis/five_case_clean_audit/`，其中：

- `run_inventory.json`：全部账本历史、选中运行、身份/来源/配置/调用。
- `skill_inventory.csv`：47条正式技能，ID、路径、类型、Draft/Support、全文判断。
- `rule_preservation.csv`：逐来源操作单元与原文摘录、Window/技能保留情况。
- `error_traceability.csv`：语义断言、覆盖缺口、系统与组织问题的阶段证据。
- `cross_case_summary.json`：明确统计分母和限定的描述性汇总。
- `register_decision_audit.csv`：53次分类的实际预算、完整JSON/官方解析、最终动作。
- `stage_field_changes.json`：全部53对Draft/Spec及注册字段差异。
- `window_audit.csv`、`window_paragraph_diagnostics.csv`：26窗口及段落只读复算。
- `evidence_integrity.json`：canonical、副本、导航、manifest和旧导出身份比较。
- `checklist_review.csv`、`skill_overlap_review.csv`：原35项复核及条件/动作/输出重叠审查。
- `protected_evidence_hashes.json`：基线证据哈希；JSON/CSV中嵌套字段以JSON文本编码，读取时须再次解析。

复核顺序：先在run inventory定位原始run，再按技能ID到compile/result和register/decisions，按source_draft_ids/support_ids/window_id回溯。源行号按原始本地文件1开始；附录B中行号按canonical文件1开始。`span`和ID只作位置提示，不代替语义检查。

现有 LAB `src/degradation_lab/evaluation.py` 读取人工评价记录、校验规则/来源/技能/trace ID与行号、再聚合；没有自动判定生成规则是否正确，也没有下游Agent执行器。此处CSV为独立研究审计格式，没有导入原有evaluation目录或修改rules；不能直接把X补充规则写进旧schema冒称已由其验证。复核已有代码可以检查身份链和字段有效性，操作语义仍需人工或另行批准的确定性执行验证。

交付前离线校验：47条技能记录、156个规则单元、35个旧检查项、53个注册决策、26个窗口无缺项；CSV/JSON均可解析，规则/错误关联的正式技能ID均有效，所有规则至少有来源Section行锚点。1,899个受保护证据文件哈希复查未变化。156个单元中47个显式标为仍需进一步原子化的复合单元，109个为条件原子候选；两类均尚未人工裁定，不混报为156个已验证原子规则。

本报告结论边界检查使用本地 `scientific-critical-thinking` 技能（1.3），帮助区分观察/解释、非独立样本、相关/因果和未知项；未借该技能运行模型或生成图片。方法辅助库引用：Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)。作者/版本信息已核对[arXiv记录](https://arxiv.org/abs/2609.00065)（访问2026-10-13，页面当前v2）；它不是五案审计事实的证据来源。


## 附录 A：运行、调用与类型统计

| 案例 | 成功run | W/S/D/Spec/Final | HTTP尝试/成功 | 已观察Token | 预算 calls/tokens |
|---|---|---|---|---|---|
| case001_qsv_select | raecd75e08b34 | 2/4/4/4/4 | 18/18 | 57472 | 32/200000 |
| case002_qsv_sort | rd9ced750fa54 | 1/3/3/3/3 | 13/10 | 29885 | 32/200000 |
| case003_docker_cp | rab9a070dfa59 | 1/2/2/2/2 | 9/8 | 28979 | 32/200000 |
| case004_git_restore | r18307cee4f4c | 10/17/17/17/14 | 67/67 | 197674 | 100/200000 |
| case005_ripgrep_guide | r64cee24fae18 | 12/27/27/27/24 | 96/96 | 324936 | 150/450000 |

审计统计（只作描述，不作独立样本推断）：

```json
{
  "audit_date": "2026-10-13",
  "method": "Independent full-source/full-canonical-file analyst review plus offline artifact checks; not human gold",
  "document_cases": 5,
  "successful_runs": 5,
  "history_ledger_rows": 13,
  "missing_history_directories": 7,
  "unindexed_directories": [],
  "windows": 26,
  "support_records": 53,
  "drafts": 53,
  "specs": 53,
  "canonical_skills": 47,
  "physical_skill_files": 104,
  "asset_types": {
    "session_skill": 15,
    "micro_skill": 18,
    "knowledge_reference": 12,
    "macro_protocol": 1,
    "safety_rule": 1
  },
  "existing_checklist_parents": 35,
  "review_rule_units": 156,
  "rule_unit_definition": "Source-first operational rule/branch audit units; some are coupled constraints, NOT all strictly atomic and NOT exhaustive human gold",
  "rule_status_counts": {
    "correct": 53,
    "partial": 29,
    "mixed": 14,
    "omitted": 59,
    "uncertain": 1
  },
  "rule_status_by_case": {
    "case001_qsv_select": {
      "correct": 9,
      "partial": 4,
      "mixed": 1,
      "omitted": 6
    },
    "case002_qsv_sort": {
      "omitted": 13,
      "partial": 6,
      "correct": 1
    },
    "case003_docker_cp": {
      "omitted": 11,
      "mixed": 2,
      "correct": 8
    },
    "case004_git_restore": {
      "mixed": 5,
      "correct": 10,
      "partial": 7,
      "omitted": 10
    },
    "case005_ripgrep_guide": {
      "correct": 25,
      "mixed": 6,
      "omitted": 19,
      "uncertain": 1,
      "partial": 12
    }
  },
  "window_coverage_by_case": {
    "case001_qsv_select": {
      "FULL": 13,
      "ABSENT": 5,
      "PARTIAL": 2
    },
    "case002_qsv_sort": {
      "ABSENT": 18,
      "FULL": 2
    },
    "case003_docker_cp": {
      "ABSENT": 11,
      "FULL": 10
    },
    "case004_git_restore": {
      "FULL": 16,
      "ABSENT": 11,
      "PARTIAL": 5
    },
    "case005_ripgrep_guide": {
      "FULL": 37,
      "PARTIAL": 11,
      "ABSENT": 15
    }
  },
  "http_attempts": 203,
  "http_successes": 199,
  "observed_total_tokens": 638946,
  "billed_cost": "UNKNOWN",
  "register_decisions": 53,
  "register_default_create": 47,
  "register_discard": 6,
  "final_body_equal_specs": 47,
  "therapist_heading_count": 39,
  "error_record_counts_by_status": {
    "CONFIRMED": 129,
    "UNKNOWN": 3,
    "NOT_ERROR": 2,
    "INFERRED": 5
  },
  "error_record_counts_by_type": {
    "E4": 5,
    "E5": 8,
    "E6": 3,
    "E2": 6,
    "E3": 5,
    "E9": 6,
    "E1": 88,
    "E8": 9,
    "E10": 5,
    "E7": 4
  },
  "counting_warning": "F语义断言/O规则缺口/S系统机制/G组织组为不同层级，禁止相加后除以技能数或文档数作为错误率。",
  "runtime_counterexamples": 0,
  "paid_model_calls_this_audit": 0,
  "downstream_tasks_executed_this_audit": 0,
  "readiness": "CONDITIONAL GO as frozen unmodified baseline; NOT quality-approved skills and NOT degradation causal evidence",
  "highest_priority_next_task": "人工复核并原子化小型来源规则验证集，校准Clean准入；随后才申请受控退化生成"
}
```

## 附录 B：47 份 canonical SKILL.md 全量审查

以下 S序号只在各Case内使用；不是按质量排序。每项均审查完整正文及对应结构化字段。各项共同存在的准入和模板问题不在每句中重复。


### case001_qsv_select


#### S01 CSV 列选择与重排

- ID：`f4c4df75-6ea6-5d4d-b30c-d7e825084300`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/csv-列选择与重排/SKILL.md>)。
- Draft：`def5f116-bce7-54b1-afcd-cbfb3db8c337`；Support：`819cec2f-0f64-5faa-baec-06919fde83af`。
- Window：`245afa09-be7e-56de-9a7a-f895fd5aa81a`；Register：CREATE，截断默认路径。
- 全文审核：正确：离散/连续选择、排除、末列、反转、重排重复（52-63）。缺：Foo[2]第三次同名解释、header前提和通用参数；非CSV/不改内容边界与任务一致。与微技能重叠但可有合理层级。

#### S02 列排序与随机打乱

- ID：`500c276a-5f59-5af9-86f5-4c0fbf4ad1be`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/列排序与随机打乱/SKILL.md>)。
- Draft：`89f8089b-9739-5ad3-ae4e-f2298dd209c8`；Support：`df120f38-3d43-51b7-a677-74f37e20013f`。
- Window：`245afa09-be7e-56de-9a7a-f895fd5aa81a`；Register：CREATE，截断默认路径。
- 全文审核：正确：按列名字节值排序而非数据值；random选择列而非行（31,61-62）。缺seed整数类型；相同seed跨版本复现未验证。

#### S03 引用冲突列名进行 qsv select

- ID：`b0592fe3-a3d5-539a-af63-d33035c20003`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/引用冲突列名进行-qsv-select/SKILL.md>)。
- Draft：`1bb58b76-1f3a-555d-ae51-b3173a8dcbc6`；Support：`01b26d5a-543b-550f-9b28-34d3399135f3`。
- Window：`245afa09-be7e-56de-9a7a-f895fd5aa81a`；Register：CREATE，截断默认路径。
- 全文审核：引用冲突名称的目标与完整名称包裹正确（28,57）；56将条件改为“仅在”属来源未支持的限制。引用示例去掉原文反斜杠，shell语义未验证。

#### S04 正则表达式列选择

- ID：`bd72bc3b-8c84-59c2-9fd4-5caba1a5350b`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/正则表达式列选择/SKILL.md>)。
- Draft：`0e55a3de-b1dc-50cf-93fb-2259c51f7403`；Support：`76983d71-789e-5f48-b781-ff2ec59ba71b`。
- Window：`245afa09-be7e-56de-9a7a-f895fd5aa81a`；Register：CREATE，截断默认路径。
- 全文审核：包含/排除命令正确（33-34），但80输出契约只有“匹配正则的列”，与排除路径相反；52把精确指定列当禁用条件未获来源支持。

### case002_qsv_sort


#### S01 CSV 内存排序执行

- ID：`353ba11e-1351-58c3-bb24-f91c7e24da8d`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case002_qsv_sort/clean/rd9ced750fa54/SkillBank/Users/docskill/csv-内存排序执行/SKILL.md>)。
- Draft：`3e450260-60ae-5f6e-9f31-b68874db4af9`；Support：`e3a9b88d-57eb-556f-b008-f905272777f7`。
- Window：`939e2088-3c3a-5b52-a18d-6e50ca62de2b`；Register：CREATE，截断默认路径。
- 全文审核：内存约束与大文件切换正确（24,54-55）；核心参数、比较模式组合和表头语义遗漏，49只有模式名称而非可执行参数。

#### S02 大文件外存排序切换

- ID：`cc5a002d-6830-5192-b841-d8233e6ce4e3`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case002_qsv_sort/clean/rd9ced750fa54/SkillBank/Users/docskill/大文件外存排序切换/SKILL.md>)。
- Draft：`740004e0-dbb4-5493-95b1-f06253756552`；Support：`3afebf9e-2810-5f4f-ac21-11e1a450191a`。
- Window：`939e2088-3c3a-5b52-a18d-6e50ca62de2b`；Register：CREATE，截断默认路径。
- 全文审核：可能内存不足时转extsort正确（29）；42,59-64将单向建议强化为小文件不得用外存排序，来源未支持。正文没有extsort具体参数，属于路由而非完整排序器。

#### S03 排序结果校验

- ID：`7ab97840-0c8c-5685-88d2-36bdb1faefea`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case002_qsv_sort/clean/rd9ced750fa54/SkillBank/Users/docskill/排序结果校验/SKILL.md>)。
- Draft：`542ae1df-a500-5424-b9cf-f43c219fc254`；Support：`fc70e9a3-1dcd-5a3f-aebb-9f7a9f0dfb78`。
- Window：`939e2088-3c3a-5b52-a18d-6e50ca62de2b`；Register：CREATE，截断默认路径。
- 全文审核：独立校验与排序区分合理，但来源只列sortcheck名称，27将自然/数字/逆序/唯一/随机都列为可校验顺序没有接口证据；运行正确性UNKNOWN。

### case003_docker_cp


#### S01 docker cp 符号链接复制策略选择

- ID：`23370d93-9d3f-5142-bfed-e6ff22cb9b36`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case003_docker_cp/clean/rab9a070dfa59/SkillBank/Users/docskill/docker-cp-符号链接复制策略选择/SKILL.md>)。
- Draft：`d9e1ef03-59a6-5d0c-a0fd-bfddb5ca00d7`；Support：`baeb1e83-f43b-50f7-a46d-a0c734012431`。
- Window：`770febe2-ee74-5a3f-bcaf-4fe54846c365`；Register：CREATE，截断默认路径。
- 全文审核：本地来源符号链接默认复制自身、-L复制目标完整一致（30,53-61）。与路径判定技能分工合理；不是完整docker cp端到端执行器。

#### S02 docker cp 路径语义判定

- ID：`0be52a4b-b68d-5166-a0c1-668834d1f64a`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case003_docker_cp/clean/rab9a070dfa59/SkillBank/Users/docskill/docker-cp-路径语义判定/SKILL.md>)。
- Draft：`94ede446-63eb-59cd-8484-f6be4a4e6055`；Support：`49d718ba-5350-5ed1-9b11-565cd8657fbd`。
- Window：`770febe2-ee74-5a3f-bcaf-4fe54846c365`；Register：CREATE，截断默认路径。
- 全文审核：Prompt32-42保留文件/目录及/.分支；Cautions86把文件源限定删掉，泛化不存在且以/结尾一律报错。81“按上述规则存在”不等于要求目标必存在，勿误报。缺父目录/所有权/根路径/tar。

### case004_git_restore


#### S01 git restore 命令语法与选项查阅

- ID：`3810431b-3f7d-505a-86e2-a7fde1141964`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/git-restore-命令语法与选项查阅/SKILL.md>)。
- Draft：`fc4e9920-f580-59c6-9041-cd700442f5d5`；Support：`d8e4482b-ce54-5e96-af2f-53aa3083650c`。
- Window：`ce07e23b-073a-5ed2-953d-d918a8b89c5c`；Register：CREATE，截断默认路径。
- 全文审核：三种语法形式与查阅型定位一致（23-26），无执行器能力；pathspec文件/NUL只保留名字，没有分隔语义。

#### S02 Git Restore 默认恢复源解析

- ID：`7b96215d-c31b-5095-aed4-9eaca3b18ffb`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/git-restore-默认恢复源解析/SKILL.md>)。
- Draft：`620c1e69-2d64-5ce6-a4e8-b02664f0d4cf`；Support：`31dcf2ab-0b04-57ef-aa7e-75df88a94f14`。
- Window：`0f0b837e-e400-5aa2-9764-1e63dd60ad30`；Register：CREATE，截断默认路径。
- 全文审核：默认源以未指定source为前提、staged/非staged两个分支准确（31,53-60）；65 patch旁注保留但不能替代操作技能。

#### S03 从指定 tree 恢复工作区文件

- ID：`d472e6a7-8895-56cb-9014-cb75cc3540b3`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/从指定-tree-恢复工作区文件/SKILL.md>)。
- Draft：`c8f5869c-7a3e-56d5-b5a9-7dbac725b3e4`；Support：`2da7e481-6e59-5046-94c7-4fd7d9142474`。
- Window：`0f0b837e-e400-5aa2-9764-1e63dd60ad30`；Register：CREATE，截断默认路径。
- 全文审核：明确source操作和merge-base条件正确（28,33），但27,58说同时staged就从HEAD，违反source覆盖，且与75目标契约冲突。64“必须commit/branch/tag”比来源common措辞更强。

#### S04 从指定源恢复工作区路径

- ID：`99f59c6f-5528-5ce9-9d2b-69222702e8d1`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/从指定源恢复工作区路径/SKILL.md>)。
- Draft：`289eb9d5-64f8-516e-96d4-e74da173962d`；Support：`11230e47-4e47-56ba-8444-4e2b87d69e05`。
- Window：`a139b2af-09e5-5296-b88d-078b00382049`；Register：CREATE，截断默认路径。
- 全文审核：默认index和指定source均有正确例子（83,89）；31→32/60→61命令骨架未携source，逐步执行可能丢参数，记INFERRED。删除规则无overlay例外。

#### S05 合并基快捷语法解析

- ID：`7147c9f5-6f4f-59d7-8f71-203e58032ac1`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/合并基快捷语法解析/SKILL.md>)。
- Draft：`e110b8bf-400b-50dc-8a74-0b97f5290727`；Support：`9e2a83b1-77fb-5c23-844f-ef5783d14395`。
- Window：`0f0b837e-e400-5aa2-9764-1e63dd60ad30`；Register：CREATE，截断默认路径。
- 全文审核：唯一merge-base、最多省略一方、默认HEAD准确（31-33,65-66）。46括号只举多基，不否定零基亦无唯一条件，故不判错误。

#### S06 同时恢复工作区与索引

- ID：`c0045ec2-f265-563d-a6ca-764403b3cef9`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/同时恢复工作区与索引/SKILL.md>)。
- Draft：`449359b8-cd56-55ae-9480-38c0ce2829ff`；Support：`236a8e39-3581-5e93-945c-dc400b9b0e9f`。
- Window：`a139b2af-09e5-5296-b88d-078b00382049`；Register：CREATE，截断默认路径。
- 全文审核：两目标/HEAD默认/source覆盖正确（26,57）；50执行在51追加source之前，顺序有歧义，INFERRED，不据文字认定真的执行了两次。

#### S07 强制启用 git restore 进度报告

- ID：`44058e52-2d84-5119-a5fe-e2d4811e07a7`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/强制启用-git-restore-进度报告/SKILL.md>)。
- Draft：`b0602199-a204-5ae8-a157-71fd8840a3a3`；Support：`c86ffe13-a880-5ecd-bfcb-938c583eee45`。
- Window：`763da6d6-7704-52e7-8a0e-655de8cf8da5`；Register：CREATE，截断默认路径。
- 全文审核：stderr进度、非终端和quiet覆盖条件完整（26,54,58）；与静默技能的绝对断言冲突不由本技能引入。

#### S08 恢复时重建冲突合并标记

- ID：`a2921234-8368-5718-a917-fb40db95ccd1`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/恢复时重建冲突合并标记/SKILL.md>)。
- Draft：`364487f8-70d9-5d15-9f5d-a6eb24cb2ace`；Support：`2565b998-c709-50c6-b4b8-9a767120feec`。
- Window：`763da6d6-7704-52e7-8a0e-655de8cf8da5`；Register：CREATE，截断默认路径。
- 全文审核：未合并/index到工作区/source禁用全部保留（26,48-56）；不把ours/theirs选择与重建标记混为一谈；rebase提醒虽旁支但来源存在。

#### S09 恢复暂存区文件至 HEAD 版本

- ID：`feccf35d-9c79-5b75-90e3-6707ce898884`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/恢复暂存区文件至-head-版本/SKILL.md>)。
- Draft：`884cccca-2651-525a-bbc2-6178d96d74aa`；Support：`fa343b04-822b-5321-b6c3-70d2005d816f`。
- Window：`35ea93d5-b53f-5fa0-a924-57e00c09ddc3`；Register：CREATE，截断默认路径。
- 全文审核：staged回HEAD且不改worktree正确（27,54）；与索引恢复技能在HEAD子域重叠，非全等重复。reset等价必须限该路径取消暂存语境。

#### S10 恢复未合并路径时选择 ours/theirs 阶段

- ID：`918e0187-7a71-5a49-9ff9-5352d0eb6e89`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/恢复未合并路径时选择-ours-theirs-阶段/SKILL.md>)。
- Draft：`7b76ed8e-54ec-52a8-acb5-2353ea065f91`；Support：`2089092a-77b2-5843-bb1f-ab072544e4f2`。
- Window：`763da6d6-7704-52e7-8a0e-655de8cf8da5`；Register：CREATE，截断默认路径。
- 全文审核：stage2/3、不能source、rebase提醒正确（37,74,78）；35,54把未合并状态等同现存冲突标记，来源未支持这种必要条件。

#### S11 恢复索引内容

- ID：`ea0c6b32-c72a-5688-a8c1-26f398a892fc`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/恢复索引内容/SKILL.md>)。
- Draft：`8a0900b8-3bf6-5821-814a-8571c64ba38a`；Support：`2e8e8476-aa71-558d-be70-a178db57a620`。
- Window：`a139b2af-09e5-5296-b88d-078b00382049`；Register：CREATE，截断默认路径。
- 全文审核：HEAD默认/自定义source/可附worktree正确（30,62-63）；55-57先执行后加选项的序列歧义，INFERRED；与9为包含关系。

#### S12 指定 git restore 恢复位置

- ID：`fd6ef816-81a2-5586-afb6-35aa6f45c10c`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/指定-git-restore-恢复位置/SKILL.md>)。
- Draft：`1ba9e5fe-e1f2-5fe9-a769-dfdfd38d036e`；Support：`5bca33af-8e6e-58e0-9032-490c46672cff`。
- Window：`7065d033-23bf-54c2-ad44-8f748912f88a`；Register：CREATE，截断默认路径。
- 全文审核：默认worktree、staged只index、两者联合正确（32-35）。输出契约比“选择位置”更强，但说明最后执行，与技能任务一致。

#### S13 指定恢复源提交

- ID：`68365646-cd43-5640-9a09-7e236fcf0774`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/指定恢复源提交/SKILL.md>)。
- Draft：`63121563-50e0-5fe2-9c1c-65f165bd5867`；Support：`ba9c7399-f1a7-5a7a-8ec8-12c0d07e8327`。
- Window：`a139b2af-09e5-5296-b88d-078b00382049`；Register：CREATE，截断默认路径。
- 全文审核：source命令及目标一致（25,50）；37,56“只有默认不满足才使用”是额外路由限制，不是Git禁止用source=HEAD的证据。

#### S14 静默恢复模式

- ID：`7dca97c1-ee41-5695-a22a-13c36e81bc3d`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/静默恢复模式/SKILL.md>)。
- Draft：`34724b88-31c6-5da4-b6e4-343436dd112d`；Support：`f51edffa-7219-59ab-bb44-28483d9607cb`。
- Window：`7065d033-23bf-54c2-ad44-8f748912f88a`；Register：CREATE，截断默认路径。
- 全文审核：quiet基本语义正确（26,52），56无条件“无法看到进度”遗漏--progress例外；该例外在另一窗口/技能明确存在。

### case005_ripgrep_guide


#### S01 Glob 过滤与覆盖顺序

- ID：`acf646a2-93f9-50a5-a034-031b4f7252f9`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/glob-过滤与覆盖顺序/SKILL.md>)。
- Draft：`78cdc380-dfa7-582f-9c3d-9c5cbe3205d2`；Support：`18e9d04e-7b94-52db-bb7f-fcc7f190313e`。
- Window：`5373afc5-80db-5942-9c1f-45700b1bbdf2`；Register：CREATE，截断默认路径。
- 全文审核：-g包含/!排除、后者覆盖正确（27,45,59）；缺正glob至少匹配一条的门槛。58沿用来源“同gitignore”但未讲!方向区别，不能把它单独算幻觉。

#### S02 ripgrep 二进制文件搜索模式选择

- ID：`20e03fce-9b17-54bb-9332-a5e81eb3289a`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-二进制文件搜索模式选择/SKILL.md>)。
- Draft：`076b6073-9b68-59c9-b5d0-58927cc0cd61`；Support：`fc20f247-76e1-5f7e-b559-104db971bb4c`。
- Window：`a63d4665-a308-5e71-9d77-2564880d45db`；Register：CREATE，截断默认路径。
- 全文审核：三种二进制模式、递归/显式路径差异、提前停止、内存风险完整（32-34,68-75）。no matches断言在binary模式内有原文支持，不误报。

#### S03 ripgrep 二进制检测行为解释

- ID：`ce28cd7a-282f-5d3d-9737-8380eaadabae`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-二进制检测行为解释/SKILL.md>)。
- Draft：`c7acbe7c-6f84-5cfb-a2a0-fea75bbe2dc3`；Support：`77175127-9319-5e65-8746-37dcab3d7da3`。
- Window：`54659e52-f1dd-56e8-908f-02789e173e39`；Register：CREATE，截断默认路径。
- 全文审核：mmap与非mmap检测范围正确（22,46-47）；缺--no-mmap干预选项。其声明不提供搜索命令是参考技能定位，不判执行失败。

#### S04 ripgrep 基础行匹配搜索

- ID：`d58844fa-d303-523d-8af5-08eb4651beab`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-基础行匹配搜索/SKILL.md>)。
- Draft：`0d5f89c9-119a-5880-8fc5-90ac5a63e630`；Support：`66e8b7a0-7029-5c5e-8bf8-8b12f7f62bcb`。
- Window：`ac2ea4f5-c2c3-51bf-be25-7a9265205354`；Register：CREATE，截断默认路径。
- 全文审核：逐行匹配与量词例子正确；仅单文件约束63与无路径递归示例20/85矛盾。默认行号泛化超出终端示例，未实测环境故UNKNOWN。

#### S05 ripgrep 常用选项速查

- ID：`262411b4-5c65-5347-81a7-550c08e3fc3f`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-常用选项速查/SKILL.md>)。
- Draft：`50d2a592-44f6-5125-9f82-3bac7ac83cf6`；Support：`d4b2919f-2f86-566d-9054-d6fcbc9ef28a`。
- Window：`537a599f-098a-5369-b93c-b2655d520cc7`；Register：CREATE，截断默认路径。
- 全文审核：i/S/c三个例子正确；标称常用选项清单但只列三项，w/U/z/C/files/sort path等已入Window却未保留。

#### S06 ripgrep 忽略文件优先级与白名单配置

- ID：`91670e33-04d0-5a4a-9215-cd36a2391b00`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-忽略文件优先级与白名单配置/SKILL.md>)。
- Draft：`dcc7a2bf-1b09-5521-8f83-49ade836f32f`；Support：`db079c79-b1a8-5144-84c8-7907556efea0`。
- Window：`f15da809-9edd-5c18-9f4c-1a6455bb9883`；Register：CREATE，截断默认路径。
- 全文审核：优先级、相对位置、忽略大小写代价正确（30,32-33）；31“在需要覆盖的目录中”位置表述有歧义，65将示例机制升级成白名单必要条件，来源不支持。

#### S07 ripgrep 忽略规则与过滤控制

- ID：`5ba99044-a58d-58cf-bed4-9b314c6ed9f0`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-忽略规则与过滤控制/SKILL.md>)。
- Draft：`8ba5855f-2db8-5f36-a738-462cdf71ff7f`；Support：`3cd910d7-08b2-5aa5-9e77-6b517ac88ffc`。
- Window：`6efdeaf9-32ee-56f9-8f00-e158f1b28760`；Register：CREATE，截断默认路径。
- 全文审核：no-ignore/hidden/text/follow和全局ignore说明准确（34-39）。先用最小调整是合理附加建议，不认作功能幻觉；与19/18存在父子覆盖。

#### S08 ripgrep 捕获组替换引用

- ID：`73f7abc9-4725-56f2-93a2-0493fac9b3ba`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-捕获组替换引用/SKILL.md>)。
- Draft：`a35ea6d8-f2df-571e-9bfd-cfaf0fd31d8e`；Support：`8f77514f-27ca-5fca-a7b9-73f2df513adc`。
- Window：`0cd51647-dd75-58c3-88af-08e530de2205`；Register：CREATE，截断默认路径。
- 全文审核：$1引用和输出不改文件方向合理（26,65），但26,52把-o描述成让替换仅作用于匹配部分，与61“replace本来只替换匹配部分”混淆；命名组/$0缺失。

#### S09 ripgrep 替换与配置预处理流程

- ID：`a4245429-7e5f-5215-b208-20f621b76667`；类型：`macro_protocol`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-替换与配置预处理流程/SKILL.md>)。
- Draft：`3a0e9055-0af5-570d-8653-24963ff63c9a`；Support：`9a7e358c-0a14-50a6-abab-32dfc6a5d1d2`。
- Window：`4a5c4fa0-dd82-511b-999e-01fcf1c1ae5e`；Register：CREATE，截断默认路径。
- 全文审核：广泛合并替换/配置/编码/二进制/预处理（24-29）；66声称可能改文件与原文never直接冲突。关联Window2只有递归/自动过滤和标题上下文，不足以支持该复合技能。

#### S10 ripgrep 替换匹配文本

- ID：`81628702-defb-59fc-857a-998b747f9977`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-替换匹配文本/SKILL.md>)。
- Draft：`e397a770-cfdc-5fc0-b37a-bf95cf65cc7e`；Support：`dd0746f8-6597-5845-90df-936efec951e1`。
- Window：`0cd51647-dd75-58c3-88af-08e530de2205`；Register：CREATE，截断默认路径。
- 全文审核：replace只改输出正确（32,61）；44禁止整行需求与57整行操作、18-20例子内部冲突。-o整行效果仅按来源给定例子，不外推多次匹配总是等价。

#### S11 ripgrep 替换预览与配置持久化

- ID：`2921cff6-f52c-582e-a935-672d57441537`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-替换预览与配置持久化/SKILL.md>)。
- Draft：`1cc2eabc-5f7c-5989-822a-435f796171b5`；Support：`882862eb-68c1-5e9f-a613-240d416d6ce7`。
- Window：`ac2ea4f5-c2c3-51bf-be25-7a9265205354`；Register：CREATE，截断默认路径。
- 全文审核：替换不改原文件正确（29,58）；42“不需要持久化就禁用”与纯替换预览入口冲突。无配置启用变量/格式细则，替换和配置被合并。

#### S12 ripgrep 自动编码处理

- ID：`2c814928-5d5a-5b76-b753-698a489a180e`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-自动编码处理/SKILL.md>)。
- Draft：`cf57ec96-dbbb-5e6a-983e-0c10befa56f3`；Support：`85232dc1-72f6-51ec-8fb2-bff9ce702df7`。
- Window：`fb0b641f-ba01-5692-9f68-0d0b47be787a`；Register：CREATE，截断默认路径。
- 全文审核：24/42/49将auto说成未知编码自动推断，65保证无需指定编码仍有匹配；实际来源只支持ASCII兼容假设和UTF16 BOM特例。与17相冲突。

#### S13 ripgrep 自动过滤规则说明

- ID：`d90ef9b1-ea8c-53b5-8b8d-9d4b724a1f48`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-自动过滤规则说明/SKILL.md>)。
- Draft：`24e07896-590b-5f68-ab5f-2e8f4687624d`；Support：`7961048b-2b22-514c-91be-7e03f0e30e4d`。
- Window：`4a5c4fa0-dd82-511b-999e-01fcf1c1ae5e`；Register：CREATE，截断默认路径。
- 全文审核：默认四过滤、优先级及目录前提正确（35-40）；遗漏no-require-git例外、二进制逐步检测细节；这些不由“名称”补足。

#### S14 ripgrep 自定义文件类型临时定义

- ID：`db337ffa-3819-5740-a11c-d8374160a702`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-自定义文件类型临时定义/SKILL.md>)。
- Draft：`d57c3850-dc80-54b5-a358-f8cd654bad53`；Support：`108e7982-df04-5df9-ab9b-06951a2a41fb`。
- Window：`5373afc5-80db-5942-9c1f-45700b1bbdf2`；Register：CREATE，截断默认路径。
- 全文审核：当前命令局部性和完整验证例子正确（31,62,84）；58若只运行type-list会误解，但例子携定义，标记轻微表述风险而非已确认语义错误。

#### S15 ripgrep 递归搜索与自动过滤

- ID：`dc2d24fe-1569-5c3e-8e82-7e165fcb1c61`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-递归搜索与自动过滤/SKILL.md>)。
- Draft：`2d8ce94c-629c-5f1f-8e17-279e2ab05b94`；Support：`db11eb6b-648e-5753-a1eb-8d9026514f55`。
- Window：`ac2ea4f5-c2c3-51bf-be25-7a9265205354`；Register：CREATE，截断默认路径。
- 全文审核：目录递归和默认过滤正确（27,52-54）；在已过滤窗口中补出部分正文未出现的主题，句级证据不足。debug作为排查建议而非无匹配唯一原因，不误报。

#### S16 ripgrep 配置文件默认选项设置

- ID：`556e78e5-fde6-567c-a379-e2b65df28a06`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-配置文件默认选项设置/SKILL.md>)。
- Draft：`5366f3c0-cc42-5928-8b47-6f75d9b7bc73`；Support：`e945be3f-8a59-508d-8056-edebb41ebe70`。
- Window：`70484645-df40-5401-aa60-cb9ad440fb18`；Register：CREATE，截断默认路径。
- 全文审核：每行参数/注释/无转义准确（33-35）；遗漏RIPGREP_CONFIG_PATH并称保存默认生效（16,86），使执行前提不完整。

#### S17 ripgrep 默认编码行为与漏匹配风险判断

- ID：`17838585-2c20-5ed4-9773-850b706e45b4`；类型：`knowledge_reference`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/ripgrep-默认编码行为与漏匹配风险判断/SKILL.md>)。
- Draft：`62530ab4-8ffe-5608-a4d1-f5a4a976789f`；Support：`04cc5ab6-6dd3-5191-a144-97716df3fdc3`。
- Window：`0bd66aa5-b88a-5f80-8440-b4ee811d1978`；Register：CREATE，截断默认路径。
- 全文审核：ASCII兼容/UTF8限制/UTF16 BOM/无效码元/显式编码BOM例外准确（29,61-69）。正确技能并未消除12的相反断言；示例notes的无BOM范围需限该UTF16场景。

#### S18 二进制搜索安全警告

- ID：`333103a1-0dae-5e40-b77d-50779da67cef`；类型：`safety_rule`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/二进制搜索安全警告/SKILL.md>)。
- Draft：`3c06cc35-719b-51a4-b28a-e5df80302e2d`；Support：`f92b7dc7-57b0-5693-b0ea-686d8b577dfa`。
- Window：`6efdeaf9-32ee-56f9-8f00-e158f1b28760`；Register：CREATE，截断默认路径。
- 全文审核：text二进制控制字符风险有来源支持（25,60）；51加入先确认/预防是保守操作建议，NOT_ERROR，不当作工具本身强制条件。

#### S19 启用隐藏文件与二进制搜索

- ID：`088793ac-d485-536e-ad5b-2089c759e532`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/启用隐藏文件与二进制搜索/SKILL.md>)。
- Draft：`84930482-299c-5d9c-9805-88099786de3b`；Support：`fa0c4b9d-3a4d-56fa-97e3-f407bb7746db`。
- Window：`6efdeaf9-32ee-56f9-8f00-e158f1b28760`；Register：CREATE，截断默认路径。
- 全文审核：hidden/text标志及风险正确（31-33）；73保证成功命中，但启用范围不保证模式存在，且其他ignore约束仍可生效。

#### S20 手动过滤：glob 与文件类型

- ID：`53070b07-3563-58f9-b86e-13f7ccdf58ba`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/手动过滤-glob-与文件类型/SKILL.md>)。
- Draft：`e8073478-12eb-5d89-918d-288d6e933fc3`；Support：`82eca346-9473-5eb3-b134-0db81c27d267`。
- Window：`4a5c4fa0-dd82-511b-999e-01fcf1c1ae5e`；Register：CREATE，截断默认路径。
- 全文审核：-t/-T形式正确（36,59）；all仅被命名没有已知类型并集边界，61“覆盖默认类型过滤”含义不足。动作以缩小范围未证明能解开所有自动过滤。

#### S21 指定编码搜索非 UTF-8 文件

- ID：`1efdc8b0-83a3-5986-bbce-022f17e507e2`；类型：`micro_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/指定编码搜索非-utf-8-文件/SKILL.md>)。
- Draft：`0609fc8f-d69a-5e56-ad26-8772dabf4c59`；Support：`516c1a0f-8581-5cbf-8932-e346cc70919a`。
- Window：`0bd66aa5-b88a-5f80-8440-b4ee811d1978`；Register：CREATE，截断默认路径。
- 全文审核：原始字节示例与-E none、(?-u)组合存在于来源（17）；59无条件BOM例外却未说明none完全禁BOM，分支被合并。-a不是所有非UTF8搜索的普遍必需条件。

#### S22 按文件类型过滤搜索

- ID：`67355610-8f2e-500b-9ff9-3fd12fe37c8e`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/按文件类型过滤搜索/SKILL.md>)。
- Draft：`1209aba0-f298-56b9-88c6-ff30f3eabf1a`；Support：`153a8645-c613-5498-9f37-22e541c0100d`。
- Window：`5373afc5-80db-5942-9c1f-45700b1bbdf2`；Register：CREATE，截断默认路径。
- 全文审核：类型包含/排除、定义应用、局部性、alias/配置路由准确（37-40,73-74）；与14为工作流—微技能包含关系，不直接定为重复错误。

#### S23 递归搜索与路径限定

- ID：`bc7ca9e9-ff78-5700-9df3-2ff04282a3d9`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/递归搜索与路径限定/SKILL.md>)。
- Draft：`bc0e05ab-e3cd-5afb-b18d-e6d12e05188e`；Support：`a5bf2d64-b15e-5df6-bd07-be35db502226`。
- Window：`4a5c4fa0-dd82-511b-999e-01fcf1c1ae5e`；Register：CREATE，截断默认路径。
- 全文审核：无路径当前目录/显式目录/F字面正确（37-39）；54禁用多根需求无本来源明确支持。输出行号依赖运行环境，本轮未实测。

#### S24 预处理器配置与使用流程

- ID：`2776509a-ba61-5ae0-b356-5714fc16123e`；类型：`session_skill`；[正式技能](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/case005_ripgrep_guide/clean/r64cee24fae18/SkillBank/Users/docskill/预处理器配置与使用流程/SKILL.md>)。
- Draft：`0fb955dd-dbd5-5b55-8333-2ebe36fef339`；Support：`7689cc9a-bb99-5152-aec5-ffebeac3f067`。
- Window：`54659e52-f1dd-56e8-908f-02789e173e39`；Register：CREATE，截断默认路径。
- 全文审核：预处理先转换再搜索的概念正确（22,57）；没有--pre、路径参数/stdin接口、可执行脚本、非PDF分支和pre-glob，不能据61契约认定可执行完成。

## 附录 C：来源规则保留矩阵

本表是分析员操作规则/分支清单，不是假装已裁定的全量原子金标准。R沿用原检查项，.a等为拆分，X为来源优先补充。FULL/PARTIAL/ABSENT仅指Window提供程度；correct/partial/omitted/mixed/uncertain指正式技能集合。`mixed`表示正确表达与错误表达共存，不能被正确技能“抵消”。条件绑定的一些单元尚须再原子化，不能据总单元数宣称工具规则总体错误率。完整原文摘录及阶段路径在CSV。


### case001_qsv_select

来源：[select.md](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md>)。技能S编号见附录B。

| ID / 来源行 | 文档要求 | Window | 集合保留 | 证据及限制 |
|---|---|---|---|---|
| R1.a / 27-30 | 1,4 选择第一和第四列而非连续四列 | FULL | correct | 技能1:19-20,52；命令及例子对应 |
| R1.b / 33-36 | 1-4 选择前四列 | FULL | correct | 技能1:53；与离散选择不同 |
| R2.a / 51-54 | !1-2 排除前两列 | FULL | correct | 技能1:55 保留排除方向 |
| R2.b / 57-60 | Foo[2] 指第三个同名 Foo 列 | FULL | partial | 技能1:33,62 仅称重复名称索引，未解释第三个/从零计数 |
| R3.a / 63-66 | _ 指最后一列；1,_ 为第一及最后列 | FULL | correct | 技能1:33,56 |
| R3.b / 69-72 | _-1 反转列顺序 | FULL | correct | 技能1:23-24,57 |
| R4.a / 87-90 | !/pattern/ 排除正则匹配列 | FULL | mixed | 技能4:34 正确，80 输出匹配列与排除支路冲突；技能1:59 正确 |
| R4.b / 93-102 | --sort 按列名的字节值字典序排列选定列 | FULL | correct | 技能2:31,61；区别按数据内容排序 |
| R5.a / 105-120 | --random 随机打乱选定列；可选 seed 重复该随机配置 | FULL | correct | 技能2:49-56；复现限相同输入/工具环境，不承诺跨版本 |
| R5.b / 162-163 | --seed 的参数类型为整数 | ABSENT | omitted | 最终只有示例42，未给整数约束 |
| R6 / 129-132,154 | 选择器冲突列名或含空格名称需引用；示例展示双层引用 | PARTIAL | partial | 技能1:63、3:72 去掉来源示例中的反斜杠；平台引用等价性 UNKNOWN；仅在冲突时可引用的限制超出来源 |
| R7.a / 174 | --no-headers 不把首行当表头 | ABSENT | omitted | 四份正式技能均未说明 |
| R7.b / 175 | --delimiter 必须为单字符，默认逗号 | ABSENT | omitted | 四份正式技能均未说明 |
| R7.c / 173 | --output 写文件代替标准输出 | ABSENT | omitted | 四份正式技能均未说明 |
| X01 / 16-20 | 按名称定位以存在表头为条件 | ABSENT | omitted | 技能声称名称/正则选择，缺少 header 前提 |
| X02 / 45-48 | 3- 选择第三列至末列 | FULL | partial | 技能1:53 有命令，但没有明确开放区间的端点含义 |
| X03 / 75-84 | /pattern/ 按列名正则选择；例如前缀a或包含数字 | FULL | correct | 技能4:32-34,70；不匹配单元格内容 |
| X04 / 123-126 | 组合选择器允许重排和重复列 | FULL | correct | 技能1:62,69 完整组合例子 |
| X05 / 143-145 | selection 必需，input 可选，-- 可终止选项解析 | FULL | partial | 正式技能给具体选择器，但未保留可选输入与--的调用约定 |
| X06 / 172 | --help 输出帮助 | PARTIAL | omitted | Window 有 qsv select --help 但最终不保留 |

### case002_qsv_sort

来源：[sort.md](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/sort.md>)。技能S编号见附录B。

| ID / 来源行 | 文档要求 | Window | 集合保留 | 证据及限制 |
|---|---|---|---|---|
| R1 / 40-41 | 同时给 --natural 和 --numeric 时 natural 优先 | ABSENT | omitted | 最终仅列模式名称，无组合优先级 |
| R2 / 43 | --ignore-case 在 numeric 且未 natural 时无效 | ABSENT | omitted | 最终缺少选项及条件 |
| R3 / 44 | --unique 过滤相同的连续值，使用排序相同的比较规则 | ABSENT | omitted | 最终只有去重名称，无相等关系 |
| R4.a / 52 | --random 打乱行，不是列 | ABSENT | partial | 最终称随机排序，没有行级实现/标志 |
| R4.b / 52 | random 与 unique 共用时 numeric/natural/ignore-case 仍决定 unique 比较 | ABSENT | omitted | 组合规则缺失 |
| R4.c / 52 | random 忽略 reverse；reverse 不影响 unique 的相等判断 | ABSENT | omitted | 组合规则缺失 |
| R5 / 56 | --faster 为不稳定原地排序，不保证相等项原顺序 | ABSENT | omitted | 未出现 --faster |
| R6 / 66 | --no-headers 将首行参与排序；否则首行表头留在首位 | ABSENT | omitted | 无表头分支缺失 |
| X01 / 16-18 | sort 需将整个 CSV 读入内存；可能放不下时用 extsort | FULL | correct | 技能1:54-55；技能2:29 正确条件路由，逆向禁用另记错误 |
| X02 / 39 | --select 指定参与排序的列子集，格式参考select帮助 | ABSENT | omitted | 未给排序键选项；原段未明确缺省选择全部列，不补全该默认行为 |
| X03 / 40 | --numeric 按数值而非字典序比较 | ABSENT | partial | 只有数值模式名称，不足以配置 |
| X04 / 41 | --natural 对混合文字与数字按自然顺序比较 | ABSENT | partial | 只有自然序名称 |
| X05 / 42 | --reverse 反转排序顺序 | ABSENT | partial | 仅逆序名称，无标志 |
| X06 / 53 | --seed 为整数且仅 random 时使用 | ABSENT | omitted | 缺少种子及条件 |
| X07 / 54 | --rng 在 random 时选择生成器，默认 standard | ABSENT | omitted | 未给 rng |
| X08 / 55 | --jobs 未指定时默认检测到的 CPU 数 | ABSENT | omitted | 未给 jobs；原文未限定物理或逻辑CPU，不自行补全 |
| X09 / 65 | --output 写文件而非 stdout | ABSENT | partial | 技能1:64 提到输出或文件，未给选项 |
| X10 / 67 | --delimiter 单字符，默认逗号 | ABSENT | omitted | 未给 delimiter |
| X11 / 68 | --memcheck 在 random 或 faster 时被忽略 | ABSENT | omitted | 未给条件 |
| X12 / 29-30,64 | qsv sort [options] [input]；--help 可查帮助 | FULL | partial | 只给 qsv sort 名称，非完整用法 |

### case003_docker_cp

来源：[container_cp.md](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/docker/e4078058de0a9f4d5cb65f946f4b8a090e19fffe/container_cp.md>)。技能S编号见附录B。

| ID / 来源行 | 文档要求 | Window | 集合保留 | 证据及限制 |
|---|---|---|---|---|
| R1 / 28-33 | docker cp 可操作运行中或已停止容器 | ABSENT | omitted | 两技能仅路径判定/链接策略 |
| R2 / 35-38 | 容器路径相对容器根，前导/可省略 | ABSENT | omitted | 没有路径根的定义 |
| R3 / 43-49 | 默认所有者为目标侧用户；-a 保留来源 UID/GID | ABSENT | omitted | 无所有权分支 |
| R4 / 50-52 | 不自动建立缺失的目标父目录 | ABSENT | omitted | 技能2:38 仅创建目标目录，未区分父目录 |
| R5 / 57-61 | 文件源且目标不存在且以/结尾时报错 | FULL | mixed | Prompt34 正确但 Cautions86 丢失文件源条件 |
| R6.a / 67-76 | 目录源且目标为现存目录，源不以/.结尾时复制目录本身 | FULL | correct | 技能2:37-41 条件完整 |
| R6.b / 74-78 | 目录源且目标为现存目录，源以/.结尾时复制内容 | FULL | correct | 技能2:37-42；rules旧74行仅前提，需延伸76-78 |
| R7.a / 80-83 | 本地来源符号链接默认复制链接本身 | FULL | correct | 技能1:30,61；技能2:44,88 |
| R7.b / 80-83 | 本地来源符号链接使用 -L 复制链接目标 | FULL | correct | 技能1:49,55；限定子能力合理 |
| X01 / 39-41 | 本地相对路径相对当前工作目录 | ABSENT | omitted | 未定义本地根 |
| X02 / 43-45 | 目录递归复制且在可能时保留权限 | ABSENT | omitted | 路径判定不能替代权限承诺 |
| X03 / 57-59 | 文件源、目标不存在时创建目标文件（受后续/例外限制） | FULL | correct | 技能2:32-34 保留基准和例外，不能当互斥四类 |
| X04 / 62-63 | 文件源覆盖已存在目标文件 | FULL | correct | 技能2:35 |
| X05 / 64-66 | 文件源复制进现存目录，使用来源 basename | FULL | correct | 技能2:36 |
| X06 / 67-70 | 目录源、目标不存在，创建目标目录并复制内容 | FULL | mixed | 技能2:38 正确，但86 泛化报错，见R5 |
| X07 / 71-72 | 目录不能复制到已存在的文件目标 | FULL | correct | 技能2:39,87 |
| X08 / 85-90 | 本地路径含冒号需显式./或绝对路径以免被误作容器路径 | ABSENT | omitted | 缺少路径歧义处理 |
| X09 / 6-9,128-131 | SRC=- 时从stdin读tar；目标必须目录 | ABSENT | omitted | 没有 tar 输入分支 |
| X10 / 6-9,128-131 | DEST=- 时向stdout输出tar | ABSENT | omitted | 没有 tar 输出分支 |
| X11 / 114-125 | 部分/proc/sys/dev/tmpfs及用户挂载内容不能直接cp，示例用exec+tar替代 | ABSENT | omitted | 环境限制和替代操作缺失；不能推广所有挂载路径一律不可复制 |
| X12 / 19-21 | --quiet 抑制进度，非终端时自动抑制 | ABSENT | omitted | 未保留选项 |

### case004_git_restore

来源：[git-restore.txt](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/git/a52a24e03c8c711f1d5e252fba78f9276908129b/git-restore.txt>)。技能S编号见附录B。

| ID / 来源行 | 文档要求 | Window | 集合保留 | 证据及限制 |
|---|---|---|---|---|
| R1.a / 24-26,40-42 | 未显式source且给staged时恢复源默认HEAD | FULL | mixed | 2:31正确；3:27,58 在已有source时仍改成HEAD |
| R1.b / 24-26,40-42 | 未显式source且不带staged时默认index | FULL | correct | 2:31及4:31 |
| R1.c / 24-26,35-42 | --source 明确覆盖默认恢复源 | FULL | mixed | 6:26和11:30正确；3:27与其自身28冲突 |
| R2.a / 58-64 | 未指定staged/worktree时恢复工作树 | FULL | correct | 12:32 |
| R2.b / 58-64 | 只带staged只恢复索引 | FULL | correct | 9:27,54；12:33 |
| R2.c / 58-64 | staged和worktree同时出现时两处都恢复 | FULL | correct | 6:26,57；12:34 |
| R3.a / 44-46 | A...B 仅当唯一merge base时可用 | FULL | correct | 5:31,65 |
| R3.b / 44-46 | A/B最多省略一方，省略者为HEAD | FULL | correct | 5:33,66 |
| R4.a / 48-52 | patch 交互选择恢复源和恢复位置差异中的hunk | FULL | partial | 17份Spec有两个完整候选但互相discard；最终1:25,48仅语法/概念 |
| R4.b / 54-56 | patch 可不带pathspec并提示恢复全部修改路径 | FULL | partial | 2:65保留旁注；专门操作候选被互相丢弃 |
| R5.a / 77-82 | ours/theirs 从index恢复工作树未合并路径，分别stage2/3 | FULL | mixed | 10:37正确；35,54把未合并误收窄为必须有冲突标记 |
| R5.b / 81-82 | ours/theirs 不可与source同时用 | FULL | correct | 10:36,74 |
| R6.a / 125-128 | overlay 模式绝不移除文件 | ABSENT | omitted | 默认删除被描述，overlay例外没有保留 |
| R6.b / 128-130,17-19 | 默认no-overlay移除源中不存在的已跟踪文件 | PARTIAL | correct | 4:33,72明确；未保留模式名但默认行为正确 |
| R7.a / 132-138 | pathspec-from-file 以LF/CRLF分隔，-为stdin，按quotePath引用 | PARTIAL | partial | 1:24仅命令骨架，无分隔/引用/stdin细则 |
| R7.b / 140-143 | pathspec-file-nul 仅结合from-file有意义，NUL分隔其他字符字面处理 | PARTIAL | partial | 1:24仅并列可选项；语义遗漏，不宣称任何组合必然CLI报错 |
| R8.a / 114-121 | 只有目标含工作树且pathspec指定活动子模块并recurse时才恢复子模块 | ABSENT | omitted | 缺少全部条件 |
| R8.b / 118-123 | recurse覆盖子模块本地修改并使子模块HEAD游离 | ABSENT | omitted | 危险副作用未保留 |
| R8.c / 118-121 | 无recurse或no-recurse时不更新子模块工作树 | ABSENT | omitted | 否定分支缺失 |
| R9 / 101-105 | index到worktree遇未合并路径且无ours/theirs/merge/conflict时，ignore-unmerged不报错并保留这些路径 | ABSENT | omitted | 不能将未合并等同冲突标记 |
| X01 / 84-86 | rebase/pull--rebase下ours/theirs角色可能看似交换 | FULL | correct | 10:40,78 |
| X02 / 88-93 | merge仅index到worktree未合并路径重建冲突，不能source | FULL | correct | 8:26,55-56 |
| X03 / 95-99 | conflict=merge/diff3/zdiff3覆盖配置且隐含merge | ABSENT | omitted | 无样式控制 |
| X04 / 107-112 | 稀疏恢复默认同时满足pathspec和稀疏规则，ignore-skip-worktree-bits可忽略后者 | ABSENT | omitted | 无稀疏边界 |
| X05 / 66-68 | quiet抑制反馈并隐含no-progress | FULL | mixed | 14:56绝对声称无法见进度，遗漏progress覆盖 |
| X06 / 70-75 | progress强制stderr进度，非终端或quiet也可启用 | FULL | mixed | 7完整；14:56相反的无条件断言 |
| X07 / 145-149 | -- 终止选项解析，pathspec限定路径 | PARTIAL | partial | 有--语法但无解释 |
| X08 / 170-180 | 引用'*.c'让Git匹配索引而非shell，包含工作树已删除路径 | ABSENT | omitted | 被忽略的示例包含关键语义 |
| X09 / 182-192 | .限当前目录；:/可从任意子目录恢复全工作树 | ABSENT | omitted | 范围差异未保留 |
| X10 / 156-168 | 已删除的跟踪文件可从索引恢复 | ABSENT | partial | 一般恢复描述但没有已删除场景示例 |
| X11 / 207-212 | --source=HEAD --staged --worktree短写-s@ -SW | PARTIAL | partial | 长式正确；短式丢失 |
| X12 / 31 | 文档称命令实验性、行为可能变化 | ABSENT | omitted | 最终未保留版本风险提示 |

### case005_ripgrep_guide

来源：[GUIDE.md](<D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/GUIDE.md>)。技能S编号见附录B。

| ID / 来源行 | 文档要求 | Window | 集合保留 | 证据及限制 |
|---|---|---|---|---|
| R1 / 148-151,1003-1004 | -F 按字面字符串而不是正则匹配 | FULL | correct | 23:39,61；不能由速查技能名称推断覆盖 |
| R2 / 412-421 | type-add 仅当前命令有效，跨命令需alias或配置 | FULL | correct | 14:31,62,84与22:40,73；验证命令需同时携带定义 |
| R3 / 536-538,442-443 | replace只改输出，绝不改原文件 | PARTIAL | mixed | 9:66说可能改文件；10:32,61和11:58正确；明确never段未入Window |
| R4 / 547-550 | 不自动搜预定配置目录，需RIPGREP_CONFIG_PATH指向配置 | ABSENT | omitted | 16:16,36声称保存即生效，无环境变量 |
| R5 / 554-559 | 配置去首尾空白后一行一个参数，无转义 | FULL | correct | 16:33-35,68-70 |
| R6 / 621-625 | no-config 禁用环境配置读取 | ABSENT | omitted | 最终未出现 |
| X01 / 28-31 | 逐行搜索，仅输出匹配行 | FULL | correct | 4:31,50；示例范围冲突另记 |
| X02 / 67-70 | 该终端例子默认显示行号；未给所有输出环境的保证 | FULL | uncertain | 4:31泛化默认行号；未查询当前CLI默认或实测重定向，不判已证伪 |
| X03 / 86-93 | 正则\w+要求至少一个word字符 | PARTIAL | partial | 列出量词，但未解释+与*差异 |
| X04 / 106-111 | 正则\w*允许零个word字符 | FULL | partial | 仅举量词，不说明零次 |
| X05 / 153-171 | 无路径时递归当前目录；给目录限定根 | FULL | correct | 23:37-38；与单文件不同 |
| X06 / 176-192 | 目录默认忽略gitignore/ignore/rgignore、隐藏、二进制、不跟随链接 | FULL | correct | 13:35-40保留四类及目录前提 |
| X07 / 181-189 | .rgignore优先.ignore优先gitignore；git父目录同仓库条件及no-require-git例外 | FULL | partial | 优先级正确；no-require-git例外遗漏 |
| X08 / 196 | --no-ignore关闭ignore相关过滤，不等于关闭全部过滤 | FULL | correct | 7:34措辞准确 |
| X09 / 197-198 | --hidden包含隐藏文件和目录 | FULL | correct | 7:35、19:31；不保证一定有命中 |
| X10 / 199-201 | -a/--text关闭二进制过滤，但控制字符可影响终端 | FULL | correct | 19:32-33；安全警告合理 |
| X11 / 202 | --follow/-L递归时跟随符号链接 | FULL | correct | 7:37,61 |
| X12 / 204-212 | -u/-uu/-uuu逐层关闭ignore/hidden/binary过滤；debug排查 | ABSENT | omitted | 保留单独开关但组合别名未保留 |
| X13 / 214-218 | ignore还含info/exclude和core.excludesFile全局规则 | FULL | correct | 7:39 |
| X14 / 220-247 | 较高优先级ignore中的!log/可覆盖gitignore；相对该ignore目录 | PARTIAL | partial | 6:30,32正确；65把高优先级示例变为白名单生效必要条件 |
| X15 / 249-252 | ignore-file-case-insensitive默认关且有性能代价 | FULL | correct | 6:33,69 |
| X16 / 285-308 | -g正模式包含、!排除，引用防shell展开 | PARTIAL | correct | 1:27,45及例子；特殊!与gitignore相反的说明未保留 |
| X17 / 310-322 | 后glob覆盖前glob，存在正glob必须至少匹配一个正glob | PARTIAL | partial | 1:59保留顺序，遗漏正glob门槛及反向顺序空集例子 |
| X18 / 348-377 | -t按类型包含，-T按类型排除 | PARTIAL | correct | 22:38,74 |
| X19 / 379-410 | type-list列类型及glob；type-add定义name:glob后-t应用 | FULL | correct | 14:18,21,49-51；22:37-39 |
| X20 / 426-438 | type all是已知类型glob的并集，不是任意文件；无扩展文件例外 | ABSENT | partial | 20:37,61只称all覆盖类型，未解释边界；不能认定全文件覆盖 |
| X21 / 474-485 | replace只替换匹配片段；整行替换需模式覆盖整行 | FULL | mixed | 10:32,57正确；44却禁用整行需求 |
| X22 / 487-503 | -o与replace组合只输出替换匹配片段 | FULL | mixed | 10例子保留；8:26,52错把-o说成控制替换范围 |
| X23 / 506-524 | $1为首个显式捕获组，$0为完整匹配 | PARTIAL | partial | $1正确但$0及索引解释丢失 |
| X24 / 526-533 | 命名捕获组可在replace中用$word引用 | ABSENT | omitted | 仅数字引用 |
| X25 / 554-556,603-604 | 配置#注释行忽略且允许空行 | PARTIAL | partial | 注释正确，空行未明示 |
| X26 / 592-601 | 带值配置用--flag=value或两行；不可同一行空格分隔 | ABSENT | partial | 一行一参数原则保留，无关键反例和合法两种形式 |
| X27 / 606-614 | 配置参数前置到CLI，多数后出现显式标志覆盖配置 | ABSENT | omitted | 无覆盖优先级；75“不适合临时覆盖”只是技能路由不判工具禁止 |
| X28 / 616-619 | --debug可查看加载的配置及参数 | PARTIAL | omitted | 保留debug过滤排查，未保留配置诊断 |
| X29 / 642-653 | auto默认假定ASCII兼容，Unicode正则依赖UTF8；非UTF8会漏匹配 | FULL | mixed | 17:29正确；12:24声称任意自动推断/无需手动编码 |
| X30 / 654-661 | UTF16 BOM触发转UTF8；无效码元用替换字符且有性能开销 | FULL | mixed | 17:29,69正确；12缺BOM限制且泛化 |
| X31 / 662-667 | -E显式编码用于各搜索文件，除非文件含BOM | FULL | correct | 17:64、21:59（none特例另列） |
| X32 / 669-675 | 默认可搜任意字节，不要求全文件UTF8；非ASCII兼容可能无匹配 | ABSENT | partial | 只说Unicode模式漏匹配，未解释可搜混合字节 |
| X33 / 677-684 | -E none关闭所有编码逻辑含BOM，按原始字节搜索 | PARTIAL | mixed | 21:17命令正确；59无条件BOM例外与none冲突 |
| X34 / 694-709 | (?-u)局部/全部禁Unicode让.或\w按字节/ASCII匹配 | ABSENT | partial | 21:28有关闭Unicode建议，但局部组合细节未保留 |
| X35 / 724-727 | 二进制启发式为内容含NUL | PARTIAL | correct | 13:39；实际何时检测见后续规则 |
| X36 / 738-748 | 默认二进制排除仅递归路径；显式文件自动binary模式 | FULL | correct | 2:32,68-69完整 |
| X37 / 749-759 | binary模式搜索至EOF或已见匹配；无命中时可确定无匹配 | FULL | correct | 2:33,75；不等于输出全部匹配 |
| X38 / 760-765 | text关闭二进制检测，大二进制可能耗大量内存 | FULL | correct | 2:34,70 |
| X39 / 771-774 | mmap只查前几KB和匹配行，非mmap检查全部搜索字节 | FULL | correct | 3:22,46-47 |
| X40 / 776-780 | --no-mmap提高二进制检测一致性但有性能代价 | ABSENT | omitted | 只解释差异，未保留控制方法 |
| X41 / 785-788 | 预处理器先转换每个文件输入再搜索 | FULL | correct | 24:22,57抽象含义正确，但执行接口另列 |
| X42 / 824-843 | --pre调用命令，每文件路径为唯一参数且内容进stdin，输出供搜索 | ABSENT | omitted | 没有--pre或入出流接口 |
| X43 / 852-854 | 预处理命令需可解析，如PATH或绝对路径 | ABSENT | partial | 仅要求命令可用，未给路径约定 |
| X44 / 884-917 | PDF预处理需处理非PDF/空文件，用cat透传 | ABSENT | omitted | 异常分支缺失 |
| X45 / 920-948 | 可用file识别压缩内容并调用解压器，其余透传 | ABSENT | omitted | 扩展示例缺失 |
| X46 / 950-958,974 | --pre-glob仅为匹配路径启动预处理以减少进程开销 | ABSENT | omitted | 缺少有条件执行和开销控制 |
| X47 / 998-999 | -i忽略大小写 | FULL | correct | 5:16,73 |
| X48 / 1000-1002 | -S在模式含大写时取消smart忽略大小写 | FULL | correct | 5:18,78 |
| X49 / 1008 | -c计匹配行数而非匹配次数 | FULL | correct | 5:20,83 |
| X50 / 1009-1010 | --files仅列将搜索的文件，不实际搜索 | FULL | omitted | 速查只有三条示例，未列此选项 |
| X51 / 1012 | -U允许跨行匹配 | FULL | omitted | 速查未保留 |
| X52 / 1013-1014 | -z搜索列举压缩类型，默认关闭 | FULL | omitted | 速查未保留 |
| X53 / 1015 | -C显示匹配周围行 | FULL | omitted | 速查未保留 |
| X54 / 1016-1017 | --sort path按文件名排序并关闭并行 | FULL | omitted | 速查未保留 |
| X55 / 1019 | -M限制输出行长度 | FULL | omitted | 速查未保留 |
| X56 / 1005-1007 | -w要求词边界 | FULL | omitted | 速查未保留 |
| X57 / 995-997 | -h精简帮助，--help完整帮助 | FULL | omitted | 速查未保留 |

## 附录 D：关键断言与系统问题索引

详细 Source→Window→Plan→Draft→Spec→Register→Final 证据在 `error_traceability.csv` 的 supporting_artifact JSON 中。未找到逐句匹配时保留空数组/UNKNOWN，不伪造支持关系。O前缀为来源集合缺口，已在附录C逐条展示；下表列F/S/G，不将它们加总为统一错误率。

| ID | 案例 | 分类/状态 | 首次可观察阶段 | 具体判断 |
|---|---|---|---|---|
| F1-01 | case001_qsv_select | E4/CONFIRMED | Extract.Plan | 排除操作却承诺输出匹配列，契约与动作方向相反 |
| F1-02 | case001_qsv_select | E5/CONFIRMED | Extract.Draft | 来源要求冲突时引用，不支持禁止正常名称引用 |
| F1-03 | case001_qsv_select | E6/UNKNOWN | Extract.Draft | 来源示例包含反斜杠转义而生成命令未含；没有shell实测不能判语义等价或错误 |
| F1-04 | case001_qsv_select | E5/CONFIRMED | Extract.Plan | 来源未禁止用正则精确指定列，技能路由新增排除条件 |
| F2-05 | case002_qsv_sort | E2/CONFIRMED | Extract.Plan | 单向大文件建议被变成外存排序只可用于内存放不下的必要条件 |
| F2-06 | case002_qsv_sort | E5/CONFIRMED | Extract.Draft | 仅由sortcheck名称推导完整多排序模式/随机顺序校验能力，来源未给接口支持 |
| F3-07 | case003_docker_cp | E2/CONFIRMED | Extract.Draft | Cautions删除文件源前提，泛化目标不存在且以/结尾总是错误 |
| F3-08 | case003_docker_cp | E3/NOT_ERROR | NONE | 按上述规则存在不等于源目标必须预先存在；正文保留创建分支 |
| F4-09 | case004_git_restore | E3/CONFIRMED | Extract.Draft | 显式source场景仍声称staged使来源变HEAD，与自身指定tree结果冲突 |
| F4-10 | case004_git_restore | E5/CONFIRMED | Extract.Draft | 来源说常见使用commit/branch/tag，生成改成必须，只是来源未支持而非已证工具不接受 |
| F4-11 | case004_git_restore | E2/CONFIRMED | Extract.Plan | 把索引未合并状态收窄为工作树必须有冲突标记 |
| F4-12 | case004_git_restore | E3/CONFIRMED | Extract.Draft | quiet后绝对无进度断言遗漏显式progress覆盖例外 |
| F4-13 | case004_git_restore | E5/CONFIRMED | Extract.Plan | 指定source的合法选择被加上默认源不满足才可用的路由条件 |
| F4-14 | case004_git_restore | E6/INFERRED | Extract.Draft | 工作流先执行基本命令再追加source/worktree，可能被逐步执行者误解；也可能仅是命令构造说明 |
| F4-15 | case004_git_restore | E9/CONFIRMED | Register | 两个正确patch候选互相指认冗余并双双discard；丢失专门操作而非完全失去patch字样 |
| F5-16 | case005_ripgrep_guide | E3/CONFIRMED | Extract.Draft | replace被说成可能修改文件，与来源never直接冲突；Plan已有修改文件主题暗示，但明确断言最早Draft |
| F5-17 | case005_ripgrep_guide | E2/CONFIRMED | Extract.Plan | auto从有限BOM/ASCII兼容策略扩大成通用未知编码推断并保证返回匹配 |
| F5-18 | case005_ripgrep_guide | E2/CONFIRMED | Extract.Draft | 缺环境变量前提却声称配置保存后默认生效 |
| F5-19 | case005_ripgrep_guide | E6/CONFIRMED | Extract.Draft | -o控制输出粒度被写成控制替换作用范围，replace本来就只替换匹配部分 |
| F5-20 | case005_ripgrep_guide | E4/CONFIRMED | Extract.Draft | Contraindications拒绝整行替换但工作流和示例又提供该操作 |
| F5-21 | case005_ripgrep_guide | E4/CONFIRMED | Extract.Plan | 替换或配置的OR入口与不需持久化就禁用冲突，排除了纯预览任务 |
| F5-22 | case005_ripgrep_guide | E3/CONFIRMED | Extract.Draft | none分支关闭BOM却继承通用编码的BOM例外，约束未分支 |
| F5-23 | case005_ripgrep_guide | E4/CONFIRMED | Extract.Draft | 技能限定单文件且拒绝递归，却给不带路径的递归示例 |
| F5-24 | case005_ripgrep_guide | E5/CONFIRMED | Extract.Draft | 把较高优先级白名单例子泛化为所有白名单的必要条件 |
| F5-25 | case005_ripgrep_guide | E4/CONFIRMED | Extract.Plan | 启用隐藏/二进制搜索不保证有匹配，输出契约不接受合法零匹配 |
| F5-26 | case005_ripgrep_guide | E5/CONFIRMED | Extract.Plan | 单目录示例被加成禁用多不相关根目录的条件；是否工具支持多根本轮UNKNOWN |
| F5-27 | case005_ripgrep_guide | E2/UNKNOWN | UNKNOWN | 终端例子的行号默认被泛化；本轮无重定向执行证据，不判工具运行错误 |
| F5-28 | case005_ripgrep_guide | E5/NOT_ERROR | NONE | 执行前风险提醒和确认属于保守建议，非伪造工具硬性前提 |
| S1-REG | case001_qsv_select | E9/CONFIRMED | Register | 所有CREATE响应被截断，官方解析返回[]，非法action默认create；47条细项在register_decision_audit.csv。 |
| S1-EVID | case001_qsv_select | E8/CONFIRMED | Extract.SupportRecord | 支持记录/manifest绑定窗口与ID，无逐句生成断言对齐；confidence=0.9不是校准的语义支持概率。 |
| S1-TMPL | case001_qsv_select | E10/CONFIRMED | Compile.Render | 最终示例标题Example Therapist Responses来自compiler.py:131，不符合CLI领域。 |
| S2-REG | case002_qsv_sort | E9/CONFIRMED | Register | 所有CREATE响应被截断，官方解析返回[]，非法action默认create；47条细项在register_decision_audit.csv。 |
| S2-EVID | case002_qsv_sort | E8/CONFIRMED | Extract.SupportRecord | 支持记录/manifest绑定窗口与ID，无逐句生成断言对齐；confidence=0.9不是校准的语义支持概率。 |
| S2-TMPL | case002_qsv_sort | E10/CONFIRMED | Compile.Render | 最终示例标题Example Therapist Responses来自compiler.py:131，不符合CLI领域。 |
| S2-EXPORT | case002_qsv_sort | E8/CONFIRMED | Lab.Export.UNKNOWN | 该run目录下11份导出JSON与Case001逐字节相同，且宣称PASS；跨案例身份错误。何时/由谁复制UNKNOWN。 |
| S3-REG | case003_docker_cp | E9/CONFIRMED | Register | 所有CREATE响应被截断，官方解析返回[]，非法action默认create；47条细项在register_decision_audit.csv。 |
| S3-EVID | case003_docker_cp | E8/CONFIRMED | Extract.SupportRecord | 支持记录/manifest绑定窗口与ID，无逐句生成断言对齐；confidence=0.9不是校准的语义支持概率。 |
| S3-TMPL | case003_docker_cp | E10/CONFIRMED | Compile.Render | 最终示例标题Example Therapist Responses来自compiler.py:131，不符合CLI领域。 |
| S3-EXPORT | case003_docker_cp | E8/CONFIRMED | Lab.Export.UNKNOWN | 该run目录下11份导出JSON与Case001逐字节相同，且宣称PASS；跨案例身份错误。何时/由谁复制UNKNOWN。 |
| S4-REG | case004_git_restore | E9/CONFIRMED | Register | 所有CREATE响应被截断，官方解析返回[]，非法action默认create；47条细项在register_decision_audit.csv。 |
| S4-EVID | case004_git_restore | E8/CONFIRMED | Extract.SupportRecord | 支持记录/manifest绑定窗口与ID，无逐句生成断言对齐；confidence=0.9不是校准的语义支持概率。 |
| S4-TMPL | case004_git_restore | E10/CONFIRMED | Compile.Render | 最终示例标题Example Therapist Responses来自compiler.py:131，不符合CLI领域。 |
| S4-EXPORT | case004_git_restore | E8/CONFIRMED | Lab.Export.UNKNOWN | 该run目录下11份导出JSON与Case001逐字节相同，且宣称PASS；跨案例身份错误。何时/由谁复制UNKNOWN。 |
| S5-REG | case005_ripgrep_guide | E9/CONFIRMED | Register | 所有CREATE响应被截断，官方解析返回[]，非法action默认create；47条细项在register_decision_audit.csv。 |
| S5-EVID | case005_ripgrep_guide | E8/CONFIRMED | Extract.SupportRecord | 支持记录/manifest绑定窗口与ID，无逐句生成断言对齐；confidence=0.9不是校准的语义支持概率。 |
| S5-TMPL | case005_ripgrep_guide | E10/CONFIRMED | Compile.Render | 最终示例标题Example Therapist Responses来自compiler.py:131，不符合CLI领域。 |
| S5-EXPORT | case005_ripgrep_guide | E8/CONFIRMED | Lab.Export.UNKNOWN | 该run目录下11份导出JSON与Case001逐字节相同，且宣称PASS；跨案例身份错误。何时/由谁复制UNKNOWN。 |
| G4-05 | case004_git_restore | E7/INFERRED | Extract.CandidatePartition | 显式source+工作树子域、git restore --source动作、指定tree输出同质；4还覆盖默认/删除，3覆盖tree命名/merge-base，13更窄。属重叠而非全等重复，检索混乱未实测。 |
| G4-06 | case004_git_restore | E7/INFERRED | Extract.CandidatePartition | HEAD取消暂存子域的前提、staged命令、不改worktree输出相同；11另支持source与worktree。重复子域可复核但不据此判所有拆分无用。 |
| G5-09 | case005_ripgrep_guide | E7/INFERRED | Extract.CandidatePartition | 替换/配置复合流程互相覆盖，又和独立配置技能覆盖；9混入多个无共同前提主题，11预览与持久化是不同目标。E7组织风险，文件修改错误另计。 |
| G5-11 | case005_ripgrep_guide | E7/INFERRED | Extract.CandidatePartition | 目录搜索前提、递归rg动作、跨文件结果重叠；23增加路径/F说明，15强调过滤。功能包含而非已证性能损害。 |

## 附录 E：条件—动作—输出的重叠审查

| ID | 案例 | 状态 | 对比 |
|---|---|---|---|
| G1-01 | case001_qsv_select | NOT_ERROR | CSV且按列名模式选择/排除；相同qsv regex命令与CSV结果，但总选择工作流涵盖更多选择器，允许父子层次。正则输出契约冲突单独计。 |
| G1-02 | case001_qsv_select | NOT_ERROR | 已选列排序/打乱是总体选择工作流的子操作；输入列集合、sort/random动作、重排列输出重合，粒度分层本身不是错误。 |
| G1-03 | case001_qsv_select | NOT_ERROR | 特殊名称引用是选择器构建子动作；可合理复用，未证明检索或执行重复成本。 |
| G3-04 | case003_docker_cp | NOT_ERROR | 同源链接规则有交集，但路径行为判定明确将-L决策交给独立技能，输出分别为行为判定与复制对象决策。 |
| G4-05 | case004_git_restore | INFERRED | 显式source+工作树子域、git restore --source动作、指定tree输出同质；4还覆盖默认/删除，3覆盖tree命名/merge-base，13更窄。属重叠而非全等重复，检索混乱未实测。 |
| G4-06 | case004_git_restore | INFERRED | HEAD取消暂存子域的前提、staged命令、不改worktree输出相同；11另支持source与worktree。重复子域可复核但不据此判所有拆分无用。 |
| G5-07 | case005_ripgrep_guide | NOT_ERROR | 临时定义类型是按类型搜索工作流子步骤，定义+应用+当前命令限制重复但可合理分层。 |
| G5-08 | case005_ripgrep_guide | NOT_ERROR | 过滤总流程包含启用hidden/text与风险提醒；安全规则有不同交付物，不能按名称或共享flags判重复错误。 |
| G5-09 | case005_ripgrep_guide | INFERRED | 替换/配置复合流程互相覆盖，又和独立配置技能覆盖；9混入多个无共同前提主题，11预览与持久化是不同目标。E7组织风险，文件修改错误另计。 |
| G5-10 | case005_ripgrep_guide | CONFIRMED | 均以未知或非UTF8编码/default auto为入口，给自动处理/风险判断；12保证自动推断，17限定BOM并警告漏匹配。存在跨技能冲突，但不是名称重复。 |
| G5-11 | case005_ripgrep_guide | INFERRED | 目录搜索前提、递归rg动作、跨文件结果重叠；23增加路径/F说明，15强调过滤。功能包含而非已证性能损害。 |
