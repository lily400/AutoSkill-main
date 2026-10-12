# Anything2Skill 多案例 Clean 生成结果审计

审计日期：2026-10-12（Asia/Shanghai）  
研究对象：面向退化文档的高质量 Agent Skill 生成；本批仅为 Clean 基线。  
本报告是 Codex 初步科研审计，不是独立人工金标准，不是执行成功率实验。逐规则证据、完整 ID 和路径见同目录新报告《CLEAN_MULTI_CASE_RULE_TRACE.md》。

## 1. 执行摘要与边界

实际发现五个案例各一次 Clean 运行，没有发现需要择优选择的重复 Clean 运行。Case001、Case002、Case003 完成了正式注册，合计 9 个正式技能；Case004 因 TLS/SSL EOF 在 Extract 中断；Case005 因包装层 32 次 HTTP 调用上限中断，保留 20 个 Draft，但未生成 Spec 或正式技能。

三个基线问题不能合并为一个“效果分数”：

1. **输入规则保真**：qsv select 与 qsv sort 的参数表丢失在实际 Window／Extract 输入中复现；Docker 的核心嵌套复制分支保留，但全局前置条件丢失；Git 的十组 EXAMPLES 被过滤，状态表仍部分保留；ripgrep 出现错误标题识别、解释与例外条件丢失。
2. **生成语义一致性**：select 的正则排除步骤与“输出匹配列”契约冲突已保留到正式技能。Docker 路径技能把仅适用于源文件的末尾斜杠错误条件写成无条件 Caution。ripgrep 类型排除与“仅返回指定类型”契约冲突出现在 Plan／Draft，但因运行未完成，不能称为最终技能错误。
3. **注册决策有效性**：三个完成案例的 9 个成功 Register 回答全部在 256 completion tokens 截断。离线执行官方纯解析函数得到 list=[]，再被转成 {}，实际默认 CREATE。没有观察到有效完整 CREATE 或 DISCARD 决策；不能据此认定这九个技能本来都应 DISCARD。

额外发现重要的数据完整性问题：Case002–005 的现有导出目录，每个目录的 11 个文件全部与 Case001 同名导出文件 SHA-256 相同，包含 Case001 的 ID／验证结果。不能将这些导出用于新案例评价。本轮未修复、覆盖或重新导出；所有语义结论从各 run 的官方原始阶段产物和 HTTP 记录重新建立。

五份 Clean 文档不是五个完整质量样本：只有三个完成样本可比较最终技能；Git／ripgrep 仅参与已观察阶段的诊断。既没有施加文档退化，也没有重复采样，不能声称“退化导致这些问题”“系统总体错误率”或“某种结构因果地导致更差质量”。

## 2. 已实际审计的资料及证据优先级

项目：D:\AS\AutoSkill-main；实验目录：D:\AS\AutoSkill-main\degradation_failure_lab；官方代码：D:\AS\AutoSkill-main\AutoSkill-main。

读取并核对：

- 当前五个 cases 的 case.json、conditions.json、rules.json、inputs/clean.json；data/catalog.json、对应 data/manifests/*.json；五份冻结原文的完整正文。
- 全部五个实际运行的 invocation.json、input_manifest.json、sources.json、config.json、execution.json、official_result.json、model_calls.json、official_call_trace.json、pipeline.log、status 与 intermediate status／result 文件。
- 5 个 Document、全部 36 个 Window；全部 29 个持久化 Draft 和 29 个 Extract Support；全部 9 个 Spec／正式 canonical SKILL.md；9 份技能 Evidence Manifest。
- 78 个已保存 HTTP 请求；72 个成功原始响应；6 个调用失败记录。失败调用没有成功响应，不补造响应。
- 当前与 wrapper_snapshot 对应的 lab 源码；官方 ingest、windowing、extractor、compiler、versioning、llm_utils、宽松 JSON 解析与相关模板代码。README 不作为代码行为证据。
- 五个现有 results/exports/<run_id>/ 的同名文件和哈希；只读运行现有 verify 命令（输出只保留在当前审计上下文，未写回历史目录）。
- 对保存的 DocumentRecord 做无模型窗口重放，Case002–005 的 Window ID 和正文与实际记录一致；对九个 Register 原始 content 做官方纯 JSON 解析重放，没有调用生成接口。

证据优先级：冻结原文／输入哈希 → 本 run 原始 HTTP 与官方阶段产物 → canonical 正式技能／manifest → 只读重新计算的工程检查。现有跨案例错配导出被排除。窗口 span、关联 ID、confidence 均不能替代句子级语义证据。

## 3. 所有实际运行及完整性

下表 Draft／Support 指 Extract 的持久化产物，不是 HTTP 中仅返回、未落盘的内容。每个运行只有 1 个 Document，条件全部 clean。

| Case | Run ID | 官方状态／退出码 | Windows | Drafts | Specs | Registered Skills | HTTP 尝试／成功 | 总 Tokens | 完整性结论 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Case001 select | raecd75e08b34 | completed / 0 | 2 | 4 | 4 | 4 | 18 / 18 | 57,472 | 四阶段完成；只读工程 PASS 24 项；语义仍有问题 |
| Case002 sort | rd9ced750fa54 | completed / 0 | 1 | 3 | 3 | 3 | 13 / 10 | 29,885 | 正式产物完整；outline 失败后规则回退；工程 PARTIAL 仅 model_stage_ingest=false |
| Case003 Docker cp | rab9a070dfa59 | completed / 0 | 1 | 2 | 2 | 2 | 9 / 8 | 28,979 | 四阶段完成；只读工程 PASS 24 项 |
| Case004 Git reset | rfad98180a468 | failed / 2 | 9 | 0 | 0 | 0 | 6 / 5 | 23,282 | Extract 第二次 Expand TLS EOF；不能评价最终技能 |
| Case005 ripgrep | r8ac019d9b468 | failed / 2 | 23 | 20 | 0 | 0 | 32 / 31 | 140,773 | Extract 部分完成；HTTP 次数预算停止，不是 Token 阈值停止 |
| 合计（仅计运行量） | 五次独立运行 | 完成 3／未完成 2 | 36 | 29 | 9 | 9 | 78 / 72 | 280,391 | 不是质量准确率分母 |

### 3.1 时间和错误

以下执行时间全部为 2026-10-11、UTC+08:00。pipeline.log 的 +00:00 时间需加八小时，不能据此误判为不同运行。

| Case | invocation.started_at → execution.ended_at | Extract Support / Compile Support | 独立异常和恢复 |
|---|---|---|---|
| C1 | 15:33:31.252676 → 15:34:52.784354 | 4 / 4 | 没有 HTTP 失败；Register 回答截断未成为官方 errors |
| C2 | 22:22:40.050089 → 22:23:53.448282 | 3 / 3 | H1 outline TLS EOF；规则回退；H8 Compile→H9 同请求重试成功；H10 Register→H11 同请求重试成功 |
| C3 | 22:25:16.763840 → 22:25:51.420030 | 2 / 2 | H8 Register→H9 同请求重试成功 |
| C4 | 22:30:20.280625 → 22:30:38.998930 | 0 / 0 | H6 Expand TLS EOF，记录 retryable=false，没有重试；pipeline.log 第 15 行 |
| C5 | 22:30:53.908932 → 22:34:05.818540 | 20 / 0 | H1 outline TLS EOF 后规则回退；第 32 次调用后下一次请求被预算保护拒绝；pipeline.log 第 58 行 |

Git 的 H4 为三个候选，H5 返回第一个技能；H6 失败使整个 W3 的候选展开未返回，因此没有对应 Draft 落盘。官方 extractor.py 972–994 先完成窗口所有 Expand，再在 1146–1183 构建 Support／Draft。这是可观察的窗口级检查点限制，不是“模型一个技能都没有生成”。

Git 和 ripgrep 的 completed_stages 只有 ingest，但 current_stage 显示 register_completed，目录也有空 Compile／Register result.json。文件存在或 current_stage 不能证明该阶段实际调用模型、成功生成或注册。两者都没有 Compile／Register HTTP 调用。

### 3.2 模型、配置、版本与成本

所有实际 HTTP 请求：OpenAI-compatible DeepSeek endpoint https://api.deepseek.com，model=deepseek-flash，temperature=0.0，thinking.type=disabled，stream=false。这是请求／返回标签，不是可复现的固定模型权重版本；确切服务端权重与更新历史 UNKNOWN。

共有配置：全局 max_tokens=16384、max_input_chars=100000、timeout_s=180；hashing embedding dims=256；recommended Extract、outline llm、每 Window 最多 4 个候选、max_units_per_document=0、workers=1、extract_retries=1、backoff=1.0；max_chars_per_chunk=6000、overlap=300、max_section_chars=10000；retrieval threshold=0.3；10 requests/60s；max_documents=1。案例特定 domain／domain_type／family_name 不同，不能说全部提示与领域上下文完全相同。

实际 Window 构建默认 max_window_chars=2400（windowing.py 633 起）；Ingest 调用没有传入 max_chars_per_chunk=6000（ingest.py 1117–1121）。不能把 6000 当作实际 Window 上限。Register hits0 分支被官方配置为 256 Token，hierarchy 为 128；全局 16384 不覆盖这个阶段上限。

运行记录的 Python 为 D:\anoconda1\envs\autoskill\python.exe，3.10.21（Anaconda）。五次 upstream_before.json／after.json 均覆盖同一 164 文件哈希清单，清单文件 SHA-256 为：
CD94ECC03C7DE739E64621DC7B5AD6DB29A0CD13B56B4F50FB602E17E8614918。
五次包装层 10 文件 wrapper_manifest.json 一致，清单 SHA-256：
22BC3CA15280E9F22D103D4ECF6C76E5EBBE9AE9E4C1AA1C8B9EF0583D66BEAB。
只读检查与当前受清单覆盖源码一致。运行时完整 Git commit、工作树状态及清单以外文件的版本没有完整记录，标为 UNKNOWN；文件指纹不能冒充完整仓库 commit。

| Case | Outline / Plan / Expand / Compile / Register / Hierarchy 尝试数 | prompt Tokens | completion Tokens | 网络重试 / JSON repair |
|---|---|---:|---:|---|
| C1 | 1 / 2 / 4 / 4 / 4 / 3 | 49,171 | 8,301 | 0 / 0 观察到 |
| C2 | 1 / 1 / 3 / 4 / 4 / 0 | 24,846 | 5,039 | 2 / 0 观察到 |
| C3 | 1 / 1 / 2 / 2 / 3 / 0 | 24,081 | 4,898 | 1 / 0 观察到 |
| C4 | 1 / 3 / 2 / 0 / 0 / 0 | 21,672 | 1,610 | 0 / 0 观察到 |
| C5 | 1 / 11 / 20 / 0 / 0 / 0 | 121,475 | 19,298 | 0 / 0 观察到 |

除九个 Register length 回答外，63 个成功回答都 finish_reason=stop 且是完整 JSON。官方 repair 只在宽松解析抛异常后触发；九个截断回答被内部 []“解析成功”，故没有 JSON repair。三次重试是相同请求的网络恢复，不是语义修复。

每 run 上限 32 HTTP 尝试，Token 软阈值 200,000；失败尝试也消耗次数。C5 累计 140,773<200,000，明确是次数触顶。保护在下一次请求之前检查，可能允许单次响应使 Token 超过阈值；未返回 usage 的失败调用不等于服务商没有收费。保存的 usage 总量是观测值，不是完整账单。billed_cost=null；真实金额 UNKNOWN，不虚构金额。本轮审计新增付费调用为 0。

## 4. 首先隔离导出错配和包装层计数问题

### 4.1 四个新案例的导出不能用于比较

D:\AS\AutoSkill-main\degradation_failure_lab\results\exports\ 下的 rd9ced750fa54、rab9a070dfa59、rfad98180a468、r8ac019d9b468 各 11 文件，逐个与 raecd75e08b34 下对应文件字节哈希相同：

documents.json、registration.json、skill_drafts.json、skill_files.json、skill_specs.json、support_records.json、text_units.json、traceability.json、verification.json、window_source_alignment.json、windows.json。

例如新运行导出 verification.json 仍写 case001_qsv_select／raecd75e08b34 和 4 个注册技能；而真实 sort 只有 3 个、Git／ripgrep 为 0。这是 44 个错配 sidecar，不是 44 次独立生成失败。产生错配的具体操作、人员、时间和原因 UNKNOWN；没有证据说明官方生成器制造了这些文件。lab 导出关联未充分防止这种使用错误，需后续单独检查，但本轮未执行 export 或改写任何导出。

### 4.2 ripgrep Support 的 0 是读取问题，不是实际没有证据

lab src/degradation_lab/artifacts.py 第 52 行：
comp.get('support_records', ext.get('support_records', []))。
Compile result 存在且 support_records=[] 时，空数组覆盖 Extract 的 20 条记录。因此只读 verify 的 supports=0 不能直接用作本例 Extract 产物计数。本报告按阶段分别计数。evaluation.py 验证的是人工填写记录的 Schema、规则／ID、来源引用和文件行号；没有自动执行技能或判定语义正确，不能将其当完整语义验证器或 Agent 执行评价系统。

## 5. Ingest：保留原文不等于保留模型可见规则

五个 Document.raw_text 都与运行输入文本 strip 后相同，输入快照／原始来源哈希检查通过；没有观察到原文正文被 DocumentRecord 截短。损失主要发生在 Section／Window 选择，而不是输入快照被实验退化。

| Case | Sections | Document 字符 / Window 字符之和 | 已确认保留 | 已确认损失／结构问题 |
|---|---:|---:|---|---|
| C1 | 7 | 4,738 / 2,828 | 主选择示例、正则否定、列排序／随机、列名引用 | 参数表不进入窗口；seed 整数类型及 output／no-headers／delimiter 丢失 |
| C2 | 6 | 5,274 / 1,277 | 排序类型概述、内存要求、extsort 提示和 Usage | 三张参数表整体过滤；R1–R6 操作约束全部缺失 |
| C3 | 6 | 6,005 / 1,542 | 文件／目录源、目标存在／类型、/. 分支、local symlink 默认与 -L | 运行／停止容器、路径根、ownership、缺失父目录、tar 条件及 options 表未进入窗口 |
| C4 | 7 | 19,124 / 5,866 | 正式 outline 识别 AsciiDoc 主章节；pathspec、mixed、hard、merge／keep 条件、状态表文本 | 十组 EXAMPLES 全被过滤只余 8 字符下划线；soft 描述块和默认模式说明缺失；表格 A/B/C/D 图例缺失 |
| C5 | 35 | 40,688 / 18,801 | 若干搜索／过滤／类型／替换步骤；后半部分仍有 encoding 规则 | 编号正文和代码 # 注释误当标题，代码／解释分离；config 环境变量、glob 顺序例外、部分编码／二进制例外缺失 |

字符比只是筛选诊断，不是规则覆盖率：窗口可能含冗余、标题元数据也能携带规则；未调用的窗口仍不能算模型已见。

源码解释和离线重放一致：

- windowing.py 143–157 按空行分段；270–284 对无 process／anchor 的长段只保留 len<=320。
- _BULLET_RE 第 114 行仅匹配段落开头，未用 MULTILINE；Markdown 表格以“|”开头，Git AsciiDoc 示例块以标题文字开头，故即使后面含多个操作也可能整体被丢弃。
- _has_process_signal 第 257–261 行使用预置领域词；部分心理／流程词不适合通用 CLI 文档。“stage”碰巧命中 Git staged／unstaged，产生不均匀保留。
- 稀疏回退（403–449）仍使用已经过滤的 blocks，不能恢复原始规则；后续 group／range 选择还可能丢掉已保留的短 block，如 ripgrep --no-config 的 317 字符段落。
- ingest.py 226–238 逐行识别标题，没有代码围栏状态保护。ripgrep outline H1 失败后使用规则回退，把 config 代码中的 #... 误作章节；不是 LLM outline 成功后识别出的结构。
- 实际 Plan／Expand 的 payload.excerpt 与对应 Window 正文一致；context_snippets=[]。同时检查 section_heading、sibling_headings 等元数据，尤其 ripgrep 的短窗口：某些 flag 语义在标题中仍可见，不能仅因正文短就说全部规则消失。
- span 可覆盖非常大的原文区间，而 excerpt 是不连续筛选后的正文。比如 sort span 7–5249 并不表示这整个原文区间被提供给模型。

这是 Clean 结构处理失真，不是人工施加的“文档退化条件”。

## 6. Extract／Compile／最终技能的质量

### 6.1 三个完成案例逐技能结论

| Case / 技能 | 做得好的部分 | 主要风险与最早可观察阶段 | Compile／Final |
|---|---|---|---|
| C1 列选择与重排 | 第一／第四列、末列、反序、正则排除示例正确 | 范围、重复同名第三列仅保留语法未充分解释；共同选项缺失来自 Ingest；引用转义需执行环境确认 | 整理结构；没有补回缺失参数 |
| C1 正则列选择 | /pattern/ 与 !/pattern/ 操作都表达正确 | H2 Plan success_artifact、H4 Expand 输出契约只写“输出匹配正则的列”，与排除分支相反 | H9 Compile 保留冲突；正式 SKILL.md 34 与 80 行 |
| C1 列排序／随机 | 明确按列名字节排序而非列内容；指定 seed 可复现的来源行为 | seed 整数类型缺失；同模型／软件版本以外的复现保证 UNKNOWN | H10 保留；有模板残留 |
| C1 引用冲突列名 | 正确识别应引用完整列名的需求 | 原文反斜杠与生成命令差异；shell／选择器解析未验证，不判命令已错误 | H11 改名／描述较清晰；未观察到语义修复 |
| C2 内存排序 | 保留必须读入所有 CSV 数据及过大文件转 extsort | 没有排序参数、优先级和异常条件；“调用并指定方式”不等于可完整执行的参数技能 | H6 描述精炼，结构规则照旧 |
| C2 外存排序切换 | 内存不足时路由正确，有意义的独立技能 | 把建议变成“仅在内存受限才允许外存排序”，原文未禁止小文件 extsort；H2 Plan 已出现排他适用条件 | H7 保留未经来源支持的限制 |
| C2 排序校验 | 与实际排序职责分开有意义 | 源文档仅“also see sortcheck”；H5 推广为可校验唯一／随机等全部模式，无本文件支持；真实 sortcheck 能力 UNKNOWN | H9 保留；不能冒充已核验校验器 |
| C3 路径语义判定 | 几乎完整保留核心嵌套分支与目录 /. 区分 | H3 Expand cautions[0] 丢掉“源为文件”条件；与 prompt 目录→不存在目标可创建冲突；全局父目录条件被 Ingest 丢掉 | H5 保留；正式 33–42 与 86 行出现不一致 |
| C3 符号链接策略 | 明确仅 local SRC_PATH symlink，默认链接本身／-L 目标两分支正确 | 不涵盖归档权限、父目录和所有实际复制前置条件；不应按全面 Docker cp 执行技能评价 | H6 保留，未见该局部规则相反语义 |

Case001 正则技能的禁止“需要精确指定列”及隐私数据全覆盖提醒、Case002 外存排他性等属于额外规范化建议；是否会在真实任务造成失败尚未验证。“没有本来源证据”与“工具实际行为已被反例证伪”必须分开。

### 6.2 未完成案例与全部 Draft 审核

Git：仅 H5 的原始展开可分析，不能赋予落盘 Draft／最终技能身份。它根据只有 SYNOPSIS 的输入给出 soft／mixed／hard 等细节；全原文有相应信息，但本次可见证据没有完整定义，模型已有知识或推断的来源 UNKNOWN。示例把 pathspec reset 称为默认 --mixed，可能混淆不同命令形式，标 UNCERTAIN，不当作已注册技能错误。

ripgrep：逐个阅读 20 个实际 Draft，全部 ID／调用映射见规则报告。有效能力包括 -F 字面量、明确 -t 与 -T 的不同方向、临时 --type-add、替换只改输出不改文件、隐藏文件开关、查看 type 列表等。它不是“没有成功提取技能”。

重点异常：

- D19 文件类型过滤：H25 Plan 描述允许包含／排除，success_artifact 却要求“仅返回指定类型”；H27 Expand 正确步骤与相反契约并存。与 C1 同类，但仅 Draft 级观测。
- D16 持久配置：H29 Plan 假定后续所有命令生效；H31 Expand 未包含 RIPGREP_CONFIG_PATH 启用前提，cautions 又称“对所有 ripgrep 命令全局生效”，遗漏 --no-config 例外。启用前提此前已被 Ingest 丢掉；无条件表述最早在 Plan 出现。
- D11 --no-ignore：从“取消过滤”变成“输出必包含原本被忽略的文件”，遗漏文件确有匹配及其他过滤仍可能生效的条件；最早 H17 success_artifact。没有执行样本，实际任务失败 UNKNOWN。
- D7 binary safety：从“注意控制字符风险”扩成必须重定向／安全终端后才允许执行，H20 Plan 先引入，H21 保留。标 UNSUPPORTED 额外强制限制，不否认一般安全建议的价值。
- D14 手动 glob 缺具体 -g 参数，例子 rg clap 明示未过滤；D18 则有正确 -g 例子。前者存在可执行细节缺口，但不能把未过滤示例误称成执行了错误 glob。
- 4 个忽略优先级相关 Draft、2 个 glob Draft 和类型定义／过滤 Draft 有职责重叠，部分拆分有真实区别。Compile 未执行，不能声称最终去重一定失败。
- 无结果排障把“最可能因忽略”作为通用目标、默认过滤范围未充分区分递归与显式文件等为进一步人工审查项，当前不升级为已证实的全工具行为错误。

Plan 真正为空的窗口：C1 W2（Usage／链接／导航）、Git W1／W2（标题／NAME）、ripgrep W4／W6（短而被标题分割的片段）。没有证据证明某个包含完整丰富操作链的窗口被模型无故空规划。空计划、窗口构建已损失内容、模型没有调用三者不可混算。

### 6.3 Compile 没有充当语义修复器

九个 Spec 都有一对一 source_draft_ids，未发生本批多 Draft 合并；关键 workflow、constraints、cautions、output_contract 与 Draft 对照没有观察到对上述错误的修复。部分名称／description 更清楚，但不等于纠正操作规则。Spec.skill_body 前部保留 Draft.metadata.prompt，再附结构化字段。

正式九个 canonical SKILL.md 保留对应 Spec body，均为 0.1.0。这证明落盘保真，不证明生成正确。可见技能树、family 总技能和导航文件不当作额外独立程序型技能。

“Example Therapist Responses／Client／Therapist”出现在 C1 4/4、C2 1/3、C3 2/2，共 7/9 正式技能。最直接来源是官方 compiler.py 126–170 的本地 renderer；不能将这个残留一概归为 Extract 模型的领域幻觉。某些原始提取模板也带 intervention 词，但内容错误与字段命名应分别审计。

## 7. Support 和 Register：可追踪性与准入并不是语义验证

### 7.1 支持记录

29 个 Extract Support 的 excerpt 均等于各自整个 Window；分布为 C1 4 条／1 个窗口、C2 3／1、C3 2／1、C5 20／9。每个 Draft 通常仅 1 条 support，本批并未出现单技能很高 support_count 的实证；但跨技能累计数量不能视为独立证据数。

九份正式 evidence_manifest.json 正确保留 Support ID、源文件、quote、span 和 confidence，quote 仍是整 Window。它们能验证来源链接，不能逐句支持所有 Workflow／Caution／Contract。例如 Docker 的同一个完整条件窗口既支持正确步骤，又被模型写出错误的无条件 Caution；“有支持记录”没有排除矛盾。

confidence 0.75–0.90 为模型输出值／裁剪后的字段；未看到人工校准、可执行 Oracle 或独立语义检查依据。support_summary.conflict=0 反映记录 relation_type，不是已经审查技能内部无冲突。

### 7.2 注册重放结论

| Case | 成功 Register 回答 | max_tokens / completion_tokens | finish_reason | strict JSON | 官方纯解析→dict | 最终动作 |
|---|---|---|---|---|---|---|
| C1 | H12–H15，共 4 | 各 256 / 256 | length | 全部失败 | []→{} | 4 默认 CREATE |
| C2 | H11–H13，共 3 | 各 256 / 256 | length | 全部失败 | []→{} | 3 默认 CREATE |
| C3 | H7、H9，共 2 | 各 256 / 256 | length | 全部失败 | []→{} | 2 默认 CREATE |
| C4／C5 | 0 | 不适用 | 不适用 | NOT_EVALUABLE | 未调用 | 无注册 |

实际链路：autoskill/utils/json.py 的 json_from_llm_text 从完整根 JSON 失败后选择内部可解析片段，九次均选到 target_skill_ids 的 []；llm_utils.py 167–170 maybe_json_dict 返回 {}；versioning.py 1378–1384 将非法／空 action 设 create，resolved_skill 回退输入 Spec，reason 回退为 create。官方 decisions／change_logs 的 action=create、reason 或 summary=create 与此一致。

九份原始回答都出现部分 create 理由，有些声称“互补、无重复／冲突”；它们是截断回答中的可见判断，不是可接受的完整注册决策。没有证据说未截断时会改为 DISCARD，也没有有效 DISCARD／merge／revise 等观测；现有库为空，只有 hits0 分支，不能评价已有库的版本合并能力。

新发现：versioning.py 711–739 的实际紧凑请求不包含 output_contract、完整 prompt 和 examples；support 摘录只截前 180 字符（696–707），C1 摘录停留在引言／导航而非关键规则。这进一步限制注册语义审查，但即便增加信息是否会修复冲突需要新实验，不能推断模型“看到了契约却故意放行”。

## 8. 跨案例比较与最大瓶颈

| 问题 | 本批可复核的复现范围 | 不能声称的结论 |
|---|---|---|
| 长参数表／前置规则丢失 | C1、C2 同类表格；C3 全局前提；C4 示例块；C5 长解释／例外 | 五种文档均必然同样丢失，或已经证明格式的因果影响 |
| 操作方向与契约不一致 | C1 正式 Skill，C5 Plan／Draft；C3 条件压缩导致 Caution 与步骤不一致 | C5 最终技能也错误，或所有否定操作都反转 |
| 无依据额外限制／范围扩大 | C2 外存专用限制和 sortcheck 能力扩展；C5 配置全局保证／安全强制前提 | 工具实际实现均被证伪；没有源码／执行反例的规则标 UNSUPPORTED |
| 证据粒度偏粗 | 全部 29 个持久化 Draft 的 Support 引整个窗口 | 全部 29 个技能都错误或单技能 evidence_count 很高 |
| 注册截断默认 CREATE | 全部 9 次可观察成功决策；来自 3 个完成案例 | 其他两个案例也发生注册截断；CREATE 内容本来一定错误 |
| therapist 模板 | 7/9 正式技能；可定位 Compile 本地 renderer | 提取模型内在推理的普遍心理领域污染 |
| 导出错配／计数误读 | 新案例 44 份 sidecar 错配；C5 Verify Support 被空 Compile 覆盖 | 官方生成模型导致了复制错误 |

输入结构与窗口构建是本批最广泛可直接复核的保真瓶颈：即使后续步骤正确，也无法保证恢复模型从未看到的来源规则。Extract 是高严重性瓶颈：同一个正确可见窗口仍生成自相矛盾的技能，C1／C3 的错误实际进入正式技能。Register 则是完整性／准入可信度瓶颈：本批没有有效决策根对象，不能作为质量门。Compile 没有观察到修复能力，并有确定 renderer 残留，但本批没有充分证据证明其普遍新造更严重操作错误或合并失败。

因此不将瓶颈排成未经定义的数值“贡献率”。先隔离记录完整性及注册解析，再改进输入保真与条件一致性，是工程／研究可复核性优先级，不是已估计的效应大小。

值得肯定的能力：原始 Document 保留、官方阶段记录和 HTTP 可追溯性较好；正确拆分 qsv 操作与 Docker symlink 微技能；Docker 主体嵌套分支和 local 限定有真实保留；ripgrep 已产生若干正确操作规则；Compile 能组织可读结构、部分描述更明确；九个 Spec 落盘保真。没有有效完整注册判断可作为正面实例，应如实说未观察到，不编造一个“成功裁决”。

## 9. 已确认事实、初步判断和 UNKNOWN

已确认事实：真实运行数／阶段产物；原始输入及代码清单哈希；实际请求预算／Token／失败；参数与例外的窗口缺失；上述可直接对照的内部冲突；九次截断 []→{}→CREATE；导出错配。

初步判断：粒度重叠程度、未经来源支持的排他限制是否有害、引用命令是否可执行、某些缺失条件对实际任务的影响、哪个改动提高总体技能质量。这些需要人工复审或预先冻结的可执行试例。

UNKNOWN：服务端固定权重版本、运行 Git commit 的完整 provenance、真实收费、TLS 具体根因、导出错配产生过程、Git／ripgrep 完成后的最终质量、真正 DISCARD／合并决策、各工具任务成功率、条件遗漏的因果效应、跨文档总体发生率。相同代码和模型标签只控制部分变量；长度、表格、教程风格、语言、工具领域、outline 是否回退、网络状态和预算截尾共同变化。

## 10. 对后续退化研究的启发与工作优先级

研究轴应是“文档→Skill 的规则保真、内部一致性、有效准入”，可执行规则测试是辅助外部验证，不将 DirectDoc/FrozenSkill 对比强行设为本项目核心。

A. 原版／包装层工程问题：截断根 JSON 被内部片段接受、默认 CREATE、断窗部分结果未持久化、错误导出身份、阶段／Support 计数歧义。  
B. Clean 语义保真问题：结构过滤、条件压缩、肯定／否定契约冲突、来源外建议。  
C. 潜在被退化放大的候选：表格条件／例外、否定符号、优先级、相隔的前提和输出、编码／配置边界。只是待检验假设。  
D. 必须受控实验的问题：错误是否随具体退化增加、阶段错因和效果大小、修复组件的贡献、跨领域泛化。

建议按顺序提交下一轮任务，批准后才能执行：

1. 建立无模型审计数据防混用检查：run／case／condition 身份、阶段特定数量、导出与原产物交叉核对；保留历史错配文件，不覆盖基线。
2. 建立 Register 离线回归测试与严格决策有效性标记，复现这九个截断回答；是否改变官方框架另行授权，原版对照保持冻结。
3. 对本报告原子规则做独立人工复审并冻结来源锚点、条件／例外、支持粒度及矛盾判据；完善而不反向修改原历史 rules。
4. 用无模型局部对照评估 Window 规则保留，分别覆盖表格、嵌套条件、AsciiDoc 示例／状态表、长教程；不要把 Code 结构改善与模型能力变化混为一谈。
5. 为 Git／ripgrep 制定可批准的完整 Clean 补充运行计划，预先给出分阶段调用规模、预算和成本 UNKNOWN 的处理，再设计 Clean／受控退化／局部修复试验；未完成样本单列。

暂不建议继续无审计地扩展更多数据集或直接批量退化生成。现有五来源适合作为结构差异试点，但正式比较需要完整运行、规则级真值与有效准入记录。现有验证器能检查哈希／Schema／阶段关联；未来专门执行器可以验证有限明确规则，无法自动证明整份自由文本 Skill 的所有语义都正确。

## 11. 审计方法参考及停止声明

本报告使用科学批判性审查的方法约束：区分观察与解释、记录选择与缺失机制、避免把相关性当因果、同时记录有效能力。本方法库参考不是 Anything2Skill 的外部性能证据：

Kassis T., Agarwal V., He Y., Patel D., Brueckner A. M. (2026). Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065（核验到 v2，2026-09-02）。https://doi.org/10.48550/arXiv.2609.00065

本轮只新增两份研究报告；未调用付费模型、未运行 lab.py run、未安装工具、未执行 Git reset／Docker cp，未改官方代码、源文档、规则、历史产物或导出。本轮到报告交付为止，不进入下一阶段开发或实验。

