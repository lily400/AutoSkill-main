# Scrapy024 s24m003：修复预处理后零候选的事后根因分析

日期：2026-10-23（Asia/Shanghai）。**本轮模型API调用0次。没有执行lab.py run、重发历史请求、运行生成流程或修改Anything2Skill源码。**

**结论：预处理修复实际生效，完整FTP目标规则已进入HTTP019的真实Plan输入；该请求及其他20次Plan的API原始返回都是合法空数组。零候选在返回内容层已经存在，未发现非空候选被本地解析/验证过滤为零。尚未找到模型为什么选择空数组的完整根因，不能据此认定算法设计有缺陷。**

qsv历史成功记录证实相同Plan模板曾对软件文档生成非空候选；两次的文档内容、领域标识、日期及system_fingerprint不同，不能作为消除了这些混杂因素的对照。

## 1. 范围、标签与完整性

- 本次S：D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m003。
- 历史Q：D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34。
- 当前源码U：D:\AS\AutoSkill-main\AutoSkill-main。
- 本报告/证据A：D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003。

本文以**已证实**标记文件直接支持或由确定代码分支推出的结论；以**证据支持但未证实**标记有机制/差异依据但未确认因果的解释；以**未知**标记缺乏足够信息的问题。

S的135个原运行文件、Q的170个文件分析前后逐文件SHA一致，当前源码清单166项也未改变。artifact_manifest和wrapper_manifest全部通过。不存在模型响应的补造。

## 2. 实际运行的代码

**已证实：本次使用原路径U下已原地替换的lab-preprocess-v1。** S/environment.json明确指向U；invocation.json记录scripts/lab.py run、case024_scrapy、clean、s24m003。

upstream_before.json与upstream_after.json一致，166项均匹配当前U。与Q的164项共同文件比较，仅两个预处理文件不同，且精确匹配上一轮修复清单；新增两项是文件旁的.official-94c47ca.bak，不是新可执行模块。

| 文件 | s24m003/当前SHA-256 | 原版备份/Q记录SHA-256 |
|---|---|---|
| AutoSkill4Doc/ingest.py | b9b1f0ac8a7096ae41567902dbd4e031439a784f780eb269e46b9f66148730b2 | 4bf23bba2b6eaab39dd3aa39b1cb33dc9f60528d9b6a577c2fdb28e2a389925f |
| AutoSkill4Doc/document/windowing.py | 5542cf56ac5e99bea393c754f40dc69c9a361f5a72fa11b28593f792c290f855 | a4431d5bc5a06c4e6a101a530f90fdcd9ab7466107e64c006873dc6ba1df1ec2 |

实际修复位置：

- [ingest.py:109](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/ingest.py:109) 的_looks_like_front_matter_heading；120行忽略判定用preview中的代码/URI，530行决定整节是否跳过。
- [windowing.py:115](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/document/windowing.py:115) 的列表正则使用MULTILINE；260、284行仍执行process/长度筛选。
- [windowing.py:473](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/document/windowing.py:473) 的窗口身份加入位置与正文SHA。

HTTP001/event.stack真实指向U/AutoSkill4Doc/ingest.py，包含修复后行号_outline_matches_from_llm:747、_parse_sections_with_fallback:1025、_build_record:1200。official_call_trace也记录U下ingest_document:1234和Plan:857。

历史观察器没有单独记录build_windows_for_record/_window_from_blocks调用帧，不能声称存在完整逐分支遥测。但**路径、源码指纹、修复内容、实际36 sections/21 windows，以及21个窗口正文全部与先前修复副本相同**，共同支持修复接入，而非只凭计数。

本次21个窗口正文和ID各有21个唯一值，FTP section实际存在，无旧的8/18窗ID冲突。证据见evidence/code_version_comparison.json、scrapy_window_request_map.csv及S的ingest/result.json。

方法是官方基准94c47ca488d4ba4117d20272e66d49b9877e68cf加预处理修复，不能称为未修改的端到端官方基线。**prompts.py、stages/extractor.py、core/llm_utils.py、autoskill/utils/json.py和taxonomy.py与Q的记录完全一致。**

## 3. 目标规则是否进入真实Plan请求

### 3.1 对应关系

**已证实：窗口18作为HTTP019发送，user.excerpt完整保留主目标块。**

源文S/inputs/input001/feed-exports.md的原始SHA-256：

a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d

它来自SkillGenBench固定提交5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d的task-curated发布材料，不是最新官方手册的完整保真认证。

| 对象 | 值 |
|---|---|
| 窗口序号 | 18（从1开始） |
| window_id | a7b664a6-1df3-5873-aee8-bddbb8e523aa |
| 实际调用 | HTTP019；HTTP001为Outline |
| excerpt字符数 | 1552 |
| 正文SHA-256 | 50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07 |
| 请求文件SHA-256 | 670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb |
| 响应文件SHA-256 | 5cee685f54c03ddeeb30af4800d6ead22d7f862d7c20a897770eb1132ff07c2a |

实际文件：[HTTP019请求](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m003/http/019/request.json)、[原始响应](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m003/http/019/response.json)。

对21份保存请求逐项解析user JSON，以excerpt+section.span匹配实际窗口，每项恰好匹配一个窗口；HTTP002–022对应窗口1–21。全部实际含正文，正文哈希均不同。不是根据窗口文件倒推发送内容。

### 3.2 定义、默认值、显式False和例外

| 规则内容 | 源文位置 | 实际HTTP019输入 |
|---|---|---|
| accepted keys及未设置时fallback说明 | 420–421 | 保留 |
| overwrite=True覆盖、False追加 | 438–439，所在段435–439 | 完整保留 |
| 默认值按backend变化；Local=False、FTP=True | 441–443 | 完整保留 |
| 部分FTP服务器可能不支持APPE追加 | 445–446，所在段445–452 | 完整保留 |
| S3/GCS不追加、stdout不覆盖的独立限制 | 447–449 | 完整保留且作用域次序不变 |

HTTP019完整包含原文438–449块。语义应是“未显式设置时FTP默认覆盖；显式False表示追加，但部分FTP服务器可能不支持APPE”，不能改写为“FTP永远不能追加”或“所有FTP都支持追加”。

section.heading是较宽的Feed exports；subsection_headings包含FTP、Settings、FEEDS，context_snippets为空。**FEEDS标题没有紧贴目标块，但excerpt中的参数名、后端归属、默认表和例外连续完整，足以定位局部规则。** 这不等于整份文档标题/上下文完美保真，也不证明模型正确理解。

目标窗8段均唯一匹配源文420–421、423、425–430、432–433、435–439、441–443、445–452、454行。21窗合计88个段落出现次数，80个唯一匹配、8个多候选、0个无法匹配。内部span是规划文本坐标，不普遍等于源文件偏移；原文映射保留歧义，见scrapy_source_mapping.json、target_window_source_map.json。

FTP重复支持136–137已回到sections；其他后端存在同句，不能仅凭文字命中认定另一个窗口保留FTP语境。本次保真结论依据HTTP019的完整主规则，不依赖重复位置。

## 4. 候选为空发生在哪一层

### 4.1 已证实的路径

21份Plan原始choice.message.content逐字都是：

~~~json
{"skills": []}
~~~

均HTTP成功、finish_reason=stop、completion_tokens=5，无额外choice或reasoning_content解释原因。HTTP019使用3969输入tokens、5输出tokens，共3974。content不是空字符串，能直接用标准JSON解析为空数组。

| 层级 | 代码位置（相对U/AutoSkill4Doc） | 对应行为 |
|---|---|---|
| 请求构造 | stages/extractor.py:756–795 _build_unit_payload | user含document、section、excerpt、max_candidates=4及taxonomy |
| 调用/解析 | core/llm_utils.py:17–40 llm_complete_json；U/autoskill/utils/json.py:23 | 合法JSON直接成功，无需repair |
| Plan准入 | stages/extractor.py:857–894 _plan_unit_skills，877–883 | raw_skills=[]，循环没有候选 |
| Expand门口 | stages/extractor.py:951–994 _extract_unit_skills，978–979 | if not planned直接return []，不Expand |
| support/draft验证 | stages/extractor.py:996–1023 _build_support_and_draft | 本次没有候选到达必填字段/执行内容检查 |
| compile/register | S/official_call_trace及对应result.json | 接口执行本地空收尾，无额外模型调用 |

所以，**直接失败层是模型API返回的Plan内容层，先于本地候选后处理。** 这只能证明提供方返回内容为空计划，不能直接观察模型内部推理，也不能排除未记录的提供方内部处理。

### 4.2 提示词与候选定义

实际模板是[prompts.py:39](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/prompts.py:39)的build_offline_extract_prompt，实际全文保存在evidence/scrapy_plan_system_prompt.txt。

**已证实**：

- 59–66行要求保守识别可复用、可调用、足够operational的资产；允许没有资产时返回空数组。
- 69–79行偏向method/policy/workflow/intervention，保留硬约束及输出检查，也含therapist/session/treatment措辞。
- 71行明确允许knowledge_reference，并非只允许多步骤操作。
- 84–96行约定最多4项及name、description、asset_type、granularity、objective、路由字段、confidence等。HTTP没有强制非空的response_format/JSON Schema。
- 107–108行允许主导语言不明时为空；没有证据表明模型实际选择了这个理由。
- Plan本地检查列表、dict和非空name，取前4项；没有confidence硬阈值把本次候选过滤为零。
- 后续1010–1023行要求基本字段及workflow/intervention/constraints/cautions任一内容；代码没有一概禁止约束型参考资产。本次没有触发这些检查。

**证据支持但未证实**：模型可能认为参数定义/默认值不够可调用；保守政策、默认领域身份、较宽章节标题或治疗领域措辞可能影响选择。

**未知**：模型是否实际据其中任何一条选空、各因素贡献、单独调整哪项能否产出合格候选。没有拒绝理由或解释，不能倒推内部判断。

## 5. 与qsv历史成功案例比较

Q运行于2026-10-11，S运行于2026-10-23。以下比较基于原始请求和响应，而非单看supports/drafts计数。

| 项目 | qsv历史Q | Scrapy s24m003 | 等级 |
|---|---|---|---|
| Plan请求/响应模型名 | deepseek-flash | deepseek-flash | 已证实：相同别名 |
| endpoint | api.deepseek.com/v1/chat/completions | 相同 | 已证实 |
| Plan参数 | temperature0、streamfalse、max_tokens16384、thinking disabled | 相同 | 已证实 |
| Plan核心源码 | prompts/extractor/parser/taxonomy指纹 | 相同 | 已证实 |
| 完整Plan system | domain type=qsv | domain type=default | 已证实：仅一行不同 |
| user.document.domain | qsv | 空字符串 | 已证实 |
| taxonomy JSON | taxonomy_id/domain_type=qsv | 两项均default | 已证实：其余字段、asset_types/tree相同 |
| pipeline领域配置 | domain=qsv、domain_type=qsv、family_name=qsv-select | 无上述覆盖 | 已证实；非控制实验 |
| 文档/窗口性质 | 命令用法、大量可执行qsv select示例 | feed说明；目标窗为参数/默认值/例外参考块 | 文本差异已证实，因果未知 |
| 典型窗口 | 首个非空窗2362字符，有console代码 | 目标窗1552字符，无代码围栏 | 已证实 |
| Plan结果 | 两窗分别4项、0项 | 21窗全0 | 已证实 |
| 后续计数 | Expand4，supports/drafts/specs/upserts各4 | Expand0，各类产物0 | 已证实：流程计数非质量金标准 |
| system_fingerprint | aeb56401ca74e127821c4f9126dcb669 | e72d3c7f663d3e1383b00b3884cb4501 | 标识不同已证实，含义未知 |
| 预处理 | 原版两个文件 | lab-preprocess-v1 | 已证实 |
| 总量上限 | 32次HTTP/200000已观察tokens | 150次/450000 | 已证实；均未触发 |

system SHA：

- Scrapy：295ee9cd6633d30897b2028a7a53a4e9b06a399c40c29b78d99413f515629be6。
- qsv：572a28771d6c510d52ee1c458bbd3ce66d8efa011408ffd8ba55ad7fa70eb37c。

准确字符串diff只涉及“Domain type is externally provided as”这一行，其值从default变为qsv。其余模板逐字相同，见plan_system_prompt.diff。

taxonomy.py:845–864的load_skill_taxonomy加载默认体系再覆盖领域身份；保存payload仅taxonomy_id/domain_type不同。**不能说qsv使用另一套已经验证的技术专用准入算法。**

Q全部18个响应返回同一旧fingerprint，S全部22个返回另一fingerprint。只能确认指纹不同，**不能仅凭它认定权重更换或服务端退化**；也不能因model别名相同，就宣称底层模型条件完全一致。

### 5.1 qsv确有真实非空候选

Q/http/002/response.json的Plan原始JSON包含：

1. CSV列选择与重排：session_skill。
2. 正则表达式列选择：micro_skill。
3. 列排序与随机打乱：micro_skill。
4. 列名冲突引用：micro_skill。

evidence_span_hint能关联列选择、regex、sort、quote原文示例。HTTP003–006为4次Expand；HTTP007返回空数组；随后4次compile和7次注册/层级模型调用，最终4个supports/drafts/specs/upserts。

它能反驳“这个模板从来不能处理软件文档”的绝对说法；**不能证明所有参考型API规则都适配，也不能证明Scrapy失败必由某一行prompt造成。**

Q/http/012–015注册决策另有finish_reason=length、max_tokens=256，原始文本不是完整严格JSON。它们发生在非空Plan/Expand/compile之后，与本次完整空Plan不同。原版有容错JSON提取，本轮不重放注册分支，不能据严格JSON失败断言具体fallback路径。因此“exit0、4个Skill”不等于生成质量/下游表现全部已独立验证。

两组Plan响应中的U+FFFD均0；终端中文显示乱码不是原始响应编码损坏证据。

**最关键的可验证差异是命令示例与参数参考块的内容差异，以及相同模型别名跨日期返回不同指纹。** domain身份也确有差异，但目前不能按因果重要性排序。

## 6. 调用量、继续扫描与退出原因

| s24m003阶段 | 已有HTTP | 输入tokens | 输出tokens | 总tokens |
|---|---:|---:|---:|---:|
| Outline | 1 | 6290 | 510 | 6800 |
| Plan | 21 | 77107 | 105 | 77212 |
| Expand/compile/register模型 | 0 | 0 | 0 | 0 |
| **合计** | **22** | **83397** | **615** | **84012** |

逐响应usage加总匹配execution.json。22次事件均成功、attempt_index=1、retry_of=null；无重试、Plan截断、HTTP429或预算耗尽证据。人民币账单未知。本轮新增调用与API token消耗均0。

合法空数组不抛异常。max_units_per_document=0未限窗，pipeline.py:1153起继续遍历，所以扫描完21个不同输入。它们不是重复发送同一个窗口，现有记录也不支持token/请求次数限制导致失败。

本次快照S/wrapper_snapshot/degradation_lab/adapter.py:140判断：只有total_skill_specs>0、errors为空且status=completed才记0，否则记2。实际status=completed、errors=[]、specs=0，故适配器exit_code=2。

Expand未执行；compile/register接口执行过空收尾，无额外模型调用。不是异常或注册器拒绝了非空候选。导航SKILL.md不是canonical提取结果。保存的2是适配器结果，没有历史shell记录不能声称shell码必然也是2。

## 7. 已证实、待验证与未知

| 解释/问题 | 标签 | 判断 |
|---|---|---|
| 仍导入旧预处理 | 已证实可排除 | 指纹匹配修复，真实输入恢复主目标块 |
| 未把正文发给模型 | 已证实可排除 | HTTP019的实际excerpt与窗口逐字一致 |
| 规则完整进入输入 | 已证实 | 定义、默认值、显式False、APPE例外均在同一请求 |
| 非空候选被本地筛掉 | 已证实可排除（本次Plan） | 返回本来为[]，无候选进入验证 |
| HTTP/JSON失败导致为空 | 已证实可排除（记录范围） | 成功、合法JSON、stop、每次5输出tokens |
| 模型认为参数参考不够operational | 证据支持但未证实 | 内容与保守政策有张力，没有拒绝理由 |
| therapist措辞导致全部为空 | 证据支持但未证实 | 相同措辞曾对qsv成功，不是已证实唯一原因 |
| domain/taxonomy身份影响选择 | 证据支持但未证实 | 与文档、日期/指纹同时变化 |
| 模型/部署条件变化影响输出 | 证据支持但未证实 | 指纹不同已证实，变化内容及因果未知 |
| 输入修复保证提取成功 | 已证实不成立 | 输入层修复后实际仍0候选 |
| 官方算法设计存在缺陷 | 未知/证据不足 | 合法空Plan与算法缺陷不能等同 |
| 模型内部为什么选择空数组 | 未知 | 无解释，文件不能恢复内部理由 |

**已定位直接失败层，完整因果根因仍未确认。**

## 8. 下一步最小诊断实验：本轮不执行

HTTP019已经提供“完整输入仍为空”的真实观察，**无需原样重发Scrapy来再次证明此事**。

建议下一轮另行批准后，只对qsv历史成功的HTTP002窗口做**一次Plan正对照探针**。本轮不发送，也不重跑case001完整流程。

理由是历史比较尚未对齐不同日期/指纹的服务条件。先改Scrapy prompt、domain或候选定义会引入新因素；一个曾产生4候选的成功窗口只需一次Plan，能低成本检查当前条件下历史正例是否仍有效。

实施前应零调用冻结原成功请求system/user、模型参数与窗口/请求SHA，另用新probe身份；最多一次HTTP，无Outline、重试、repair、Expand、compile、register。保存当前model、fingerprint、usage、原始content和候选判定。现有单窗口工具原先固定Scrapy输入，必须先离线核对输入绑定和次数上限，不能用完整lab.py run代替。

Q/http/002历史为4102输入、957输出tokens，仅作规模参考，不能编造未来精确费用。

| 后续正对照结果 | 能支持什么 | 不能证明什么 |
|---|---|---|
| 非空，指纹与s24m003一致 | 当前条件下模板仍能处理该命令文档，可进一步聚焦Scrapy内容/元数据 | 不能证明domain或prompt是唯一根因 |
| 空数组，指纹与s24m003一致 | 历史成功不能直接复现到当前条件，应调查服务/运行稳定性 | 一次失败不能证明权重更换或提供方故障 |
| 指纹又变、传输/JSON异常 | 条件仍未对齐，应分别记录后停止 | 不能归为Scrapy候选准入失败 |

单次temperature0探针不是统计性因果证明。后续若区分领域身份与参考型内容，应预注册单因素对照；修改技术文档prompt/准入须另立方法版本，不能冒充官方基线。不要同时换模型、改prompt、改输入再猜测原因。

若后续仍禁止qsv单请求探针，就保留日期/指纹缺口。本报告不构成模型调用授权。

## 9. 证据索引与执行边界

所有新增材料集中在本目录evidence下：

| 文件 | 内容 |
|---|---|
| summary.json、integrity.json | 阶段计数、usage、结果与只读完整性 |
| code_version_comparison.json | 当前/历史源码SHA及两个备份项 |
| scrapy_window_request_map.csv | 21窗ID、正文/请求/响应SHA和候选数 |
| scrapy_http_analysis.json | 22次已有调用的配置、content、JSON、usage |
| scrapy_source_mapping.json | 实际请求正文的原文映射与歧义 |
| target_http019_request.json、target_http019_response.json | 目标请求/响应逐字节派生副本 |
| target_window_18.txt、target_window_source_map.json、target_request_summary.json | 目标正文、位置和调用关联 |
| qsv_http_analysis.json、qsv_source_mapping.json | 历史18次调用与2个Plan输入 |
| qsv_comparison.json、plan_system_prompt.diff | 精确模板/taxonomy差异、4候选及注册截断 |
| provider_fingerprints.json | 两次全部响应指纹及编号 |
| *_run_inventory_before.json | 原运行逐文件SHA |

分析仅用标准库读取JSON、计算SHA和原文匹配；audit hook禁止网络/子进程及审计目录外写入。没有执行SDK、原生生成/注册流程或新的模型测试。

首轮汇总对qsv所有阶段都作严格JSON解析，遇012–015注册截断后停止；随后按阶段记录事实，未重试模型、补造响应或改源数据。所有原始记录仍以原run为准。

**只读事后分析完成。完整根因未确认；停止，等待下一轮明确指令。**
