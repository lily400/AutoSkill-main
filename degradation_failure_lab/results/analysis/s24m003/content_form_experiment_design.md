# Scrapy文档内容呈现形式对照：离线设计

日期：2026-10-23（Asia/Shanghai）。工作树：D:/AS/AutoSkill-main。

**决策：GO——可以进入另行授权的最小内容形式对照，仅限检验本冻结窗口、scrapy外部身份条件下的“呈现方式整体效应”。本轮模型API调用0次，没有执行Plan或任何其他模型阶段。**

**已确认的是设计前置证据**：规则有源文支持，A原始excerpt与B表格变体保留同一组规则信息，完整逻辑diff只含user.excerpt；10项离线校验通过，5种错误变体被拒绝。**尚未确认的是实验效果**：没有任何本设计的A/B新响应，不能声称表格提升候选生成或规则保真。

表格同时改变了长度、段落组织、条件邻近关系及与保留span长度的关系。因此本设计不能识别“单独表格排版”的纯因果效应，亦非正式Clean/Relevant Degradation/Irrelevant Degradation实验。

## 1. 历史证据与本次范围

已读取四份报告和实际请求/响应，而非重新执行历史实验：

- [零候选根因报告](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/s24m003_zero_candidate_root_cause.md)
- [qsv正对照报告](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/followup_qsv_probe_report.md)
- [领域身份对照报告](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_report.md)
- [反序复核报告](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_report.md)

本轮直接读取原始HTTP019、源文、qsv探针原始响应以及身份对照/复核两轮的原始响应。历史证据准确路径、哈希、原始content和指纹见[historical_evidence_index.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/historical_evidence_index.json)；四份报告哈希见[source_manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/source_manifest.json)。只作文件解析，没有调用原版Plan解析方法或重放请求。

已知两对身份对照为default各0候选、scrapy各3候选，同指纹；这是领域身份相关性的有限复核，不能作为唯一根因证明。scrapy的两次候选都未完整表达目标规则，反序轮还将FTP与S3/GCS合并为“不支持追加”。因此这次将候选存在性和语义正确性分开测量。

## 2. 原文、引用与语义边界

源文件：[feed-exports.md](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m003/inputs/input001/feed-exports.md)。
原始SHA-256：a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d。
版本：SkillGenBench固定发布提交5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d的task-curated材料；不是最新官方手册完整保真的认证。

原始请求：[HTTP019/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m003/http/019/request.json)，SHA-256=670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb。

| 规则 | 需要保留的语义 | 源文证据 | 证据性质/限制 |
|---|---|---|---|
| R1 | FTP默认True/覆盖 | 定义438–439 + 默认范围441 + FTP行443；136–137与FTP标题124–126作重复旁证 | 直接默认值与参数定义组合 |
| R2 | FTP显式False选择追加，受服务器能力条件约束 | 定义438–439 + FTP行443 + APPE条件445–446 | 证据组合；不存在逐字同时包含FTP+显式False的一句，不补写成功保证 |
| R3 | 部分FTP服务器可能不支持APPE追加 | 445–446 | 保留Some/may的限定 |
| R4 | 不能据此称所有FTP都不支持追加 | 445–446 | 作用域守卫；不是额外正面事实，不推导具体服务器必然支持 |
| R5 | S3/GCS默认True且不支持追加，各自限制与FTP分开 | 443、445–448 | 两行后端限制及FTP条件独立 |
| R6 | 本地False；stdout False且不支持覆盖，保持各自边界 | 438–439、442、449 | 未给本地增加能力保证 |

R2中的False表示参数选择的追加行为，不能改写为“每个FTP服务器都能成功追加”。原文没有支持某具体服务器的能力保证、额外执行步骤或新的API行为。R4是禁止无根据泛化的范围约束，**不因Some就证明一定存在支持APPE的具体服务器**。不存在需要人工补造的目标事实。

完整逐项引用、行号、源文件字节区间、原始引用SHA及规范化引用SHA均保存在[source_quotes.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/source_quotes.json)；规则与多段引用的组合关系见[rule_source_map.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/rule_source_map.json)。

| 引用ID | 源文件行号 | 原始引用字节SHA-256 |
|---|---|---|
| definition | 438–439 | 106acfb111e0817fb42242227352a32d88aaff840293cfa74604c4c170c08ac5 |
| default_scope | 441–441 | a7076c76a48a3ad5c70c641e715afbe01cdc4a3d29d363784b4eeb0d39611a27 |
| local | 442–442 | f47ede724d7be24936c70b2d5c568cc51d5d92222dff3ba0b505468ee8e6414d |
| ftp | 443–443 | e05ead8ed2c6d928751c328bd591db995a23c1675ac3d856eae40a129d7428ae |
| appe | 445–446 | 6dffb6c3c7e50360e6d148734a8be22039c3d5a5e173eb181b2ca6a1de1297ef |
| s3 | 447–447 | 531f2797a93d93ecbbe634779ca0a01913b3570df0b6512cd3b7b9e775f83f0c |
| gcs | 448–448 | 389842c29227b58781d5145ca69779045c1de4a2b6b2f3364d23fec1b7316e28 |
| stdout | 449–449 | c4c67fec66dbcb0fe0b1feadbd27861452127f7d92484f271da3b21e8fa1da49 |
| ftp_repeat | 136–137 | 1f00abce85a4d9721ddc493ad4270c78df043594c39aa00cccb5e601c65000ba |
| ftp_context | 124–126 | 194c70fdb369b9bac093b6326724e59700af5cf27d8ded57f3867cc9c3d042ea |

源文件原始行尾为CRLF，请求excerpt为LF。引用SHA按源文件真实CRLF字节计算；匹配excerpt时只显式归一化行尾并去掉引用外围空白，不改源文件或其哈希。另存的规范化引用SHA使用明确的空白折叠规则；不能将两种哈希混用。最初离线映射因未处理行尾差异报错，已改为上述显式匹配，**未更改已冻结的A/B输入**。

136–137的重复支持已结合124–126的FTP上下文冻结，只作旁证，不插入两臂输入。

## 3. 两臂输入及唯一变更

### A：原始参数参考块，固定scrapy身份

**本设计A不是前轮的default身份A。** 它逐字节复用前轮领域身份实验的live/B/request.json，即scrapy身份下、仍使用HTTP019原始excerpt的真实请求。否则会同时改变身份和呈现形式。

A请求来源：D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_ablation_001\live\B\request.json。
本次A副本：[A/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/A/request.json)；原始excerpt：[A/excerpt.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/A/excerpt.md)。

### B：将后端默认值与限制改排为表格

本次B：[B/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/B/request.json)、[B/excerpt.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/B/excerpt.md)。外部清单明确标为人工构造的诊断呈现变体，**不是原始Clean文档，也不是正式退化条件**。

仅替换A excerpt字符区间[983,1329)；B对应区间[983,1420)。替换前后的prefix与suffix逐字相同，overwrite的True/False定义也完全保留。其他format、encoding、fields、item_filter、postprocessing等配置项及所有链接均未改。

替换块全文：

~~~markdown
The default value depends on the storage backend:

| Storage backend | Default value | Backend-specific limitation |
|---|---|---|
| Local filesystem | `False` |  |
| FTP | `True` | Some FTP servers may not support appending to files (the `APPE` FTP command). |
| S3 | `True` | appending is not supported |
| Google Cloud Storage (GCS) | `True` | appending is not supported |
| Standard output | `False` | overwriting is not supported |
~~~

具体变化是列表转表格；APPE原句合并物理换行并置于FTP一行；S3/GCS/stdout限制各入各自单元；增加组织性列名和表格后的一个空行。没有新例子、步骤、命令操作、输出要求或“必须生成技能”等模型指令。

本地后端限制单元为空，仅表示没有从源文复制额外限制句，**不是“本地后端没有任何限制”的新事实**。表头本身是组织标签，不是新增API知识。表格不新增显式FTP False示例，False关系仍来自两臂完全相同的共享参数定义。

### 固定项、构造器与哈希

已通过纯函数load_skill_taxonomy(domain_type=scrapy)和maybe_offline_prompt(kind=extract_plan)验证：冻结system和taxonomy与现有构造器输出逐字/逐字段相同。这里只构造并比较字符串，不执行Plan。

prompts.py、taxonomy.py和stages/extractor.py的SHA已存入source_manifest；没有修改它们。A/B共用相同system、taxonomy类型树、document、section、max_candidates=4及所有其他消息/元数据。

| 项目 | A | B |
|---|---|---|
| request SHA-256 | edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c | 3d5193a46be9999e0e6c13745dcf2cecf970c8e168c5419721c9e3fea023dabf |
| excerpt SHA-256 | 50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07 | 895ca2e7f30a7caae8beb9c8a8faaf583eba668db2b71680f000ac1f933cefda |
| system SHA-256 | d32195e344f8cf116404920393e420ddef8129a57b1f854ba5e4ade2d47927dd | d32195e344f8cf116404920393e420ddef8129a57b1f854ba5e4ade2d47927dd |

endpoint=https://api.deepseek.com/v1/chat/completions；model=deepseek-flash；temperature=0.0；stream=false；max_tokens=16384；thinking={"type":"disabled"}；未来客户端超时180秒。

document.domain仍为空；metadata中原有default身份字段及family_name全部保留，只有system/taxonomy外部身份固定为scrapy。这与历史scrapy臂一致，不能声称整个document元数据已变为scrapy。

实际wire JSON只改变/messages/1/content这个字符串；将该字符串解析为user对象后，**唯一逻辑diff是/messages/1/content/excerpt**。完整新旧值见[wire_field_diff.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/wire_field_diff.json)、[field_diff.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/field_diff.json)，逐行diff见[request_body.diff](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/request_body.diff)、[excerpt.diff](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/excerpt.diff)。

模型可见source路径、源文哈希和section.span均保持原值，表示原始证据来源；变体身份和新哈希记在外部清单，不能用旧metadata哈希声称B是未经改写的源文。

## 4. 离线语义等价审查

[presentation_map.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/presentation_map.json)保存共享定义及每个后端在A/B的字符区间、行号、源引用和表格单元。[semantic_equivalence_audit.csv](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/semantic_equivalence_audit.csv)逐项给出R1–R6的原文依据、A/B含义及适用范围，六项均为PASS_OFFLINE_MANUAL_AND_LITERAL_ATOMS。

本次等价判据是：共享True/False定义不变；五个后端名称和默认值不变；FTP的Some/may/APPE原句不变且仅归于FTP；S3/GCS和stdout限制语句不变且归属不变；所有非目标前后文不变；没有额外事实或指令。

这是**人工语义审查加确定性文本原子/作用域核对**，不是对所有可能读者或模型解释的形式化证明。模型是否更容易理解这些关系正是待测问题；等价审查不预设B会更好。

10项本地校验全部通过，包含原始字节/引用偏移/哈希、唯一字段diff、未改前后文、后端表格原子、现有构造器匹配、指标与额度、长度关系及历史完整性。5个内存负例分别改错FTP默认值、将条件改成所有FTP、删除APPE、改错FTP后端名称、加入模型指令，均被拒绝；没有运行提取器或模型。

结果：[validation_results.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/validation_results.json)、[validation.log](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/validation.log)。脚本[verify_design.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/verify_design.py)自带禁网/禁子进程audit hook，没有模型执行入口；原版Plan解析本轮也未执行。

## 5. 调用前冻结的评价标准

完整标准见[preregistered_metrics.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/preregistered_metrics.json)。这些是测量标准，**不修改官方候选准入定义**，也不回填重算历史报告。

| 指标 | 预注册判据 |
|---|---|
| 候选生成 | 完整严格JSON对象的skills为非空列表；单独记录原始数量，不能据此判规则成功 |
| Plan接受 | 未来仅对保存响应使用原版Plan本地解析，记录接受数量与原始数量差异；不得repair或Expand |
| 默认行为保真 | 实际候选明确FTP默认True/覆盖；允许正确同义表达，不要求字面True |
| 显式参数保真 | 实际候选明确FTP显式False选择追加语义并受服务器能力约束；只说本地False或泛称追加不通过 |
| 例外保真 | 实际候选保留FTP服务器/APPE能力的条件或部分范围，不声称所有FTP都不能或一定能追加 |
| 后端范围保真 | 不将S3/GCS禁止追加、stdout禁止覆盖或本地默认值错误移植到FTP，也不把FTP条件推广至所有后端 |
| 完整规则表达 | 至少一个原版Plan接受的候选同时满足默认值、显式False、APPE条件与正确作用域；且其他接受候选无目标冲突断言 |

逐候选逐字段读实际语义并引用证据，不能只用名称、关键词或evidence_span_hint。不要把不同候选片段拼成一个完整契约；跨候选覆盖作为次要描述另记。完整FTP候选无需枚举所有无关后端，但若谈及其他后端，必须保持其范围正确；省略和错误分开。

结果分类：

- 完整表达：上述完整规则标准通过；仍仅指Plan候选，不等于最终Skill成功。
- 非空但错误：存在明确错误目标关系或作用域，即使另一候选正确也记录冲突，不算运行级完整成功。
- 非空但部分：没有明确错误，却遗漏必要关系；不得从源文或假想Expand补足。
- 非空但无关：存在候选，但未表达FTP规则。
- 合法空列表：没有候选，规则未表达；不是异常，也不是模型作了错误断言。
- 原始非空但未被Plan接受：独立记录为接受失败，不混为零生成。
- 无法判断：HTTP/传输失败、截断、非法严格JSON/schema或语义本身确实含混；保留可见计数，不能编码为合法空列表。

所有结果均保存HTTP状态、原始响应、严格JSON状态、原始/接受计数、全部候选字段、指纹、finish_reason、实际usage/缓存、时间、顺序和完整请求/响应哈希。不得额外调用评审模型。

## 6. 可识别性与混杂因素

| 观测量 | A | B |
|---|---:|---:|
| excerpt字符/UTF-8字节 | 1552 | 1643 |
| 物理行数 | 35 | 36 |
| 按空行分隔的文本块（机械计数） | 8 | 9 |
| 按空白分词数（不是模型token） | 215 | 241 |
| 竖线字符数 | 0 | 28 |
| 完整request UTF-8字节 | 15737 | 15830 |
| system+user字符串字符数 | 14212 | 14304 |

excerpt增加91字符（约5.86%）；request增加93字节。精确模型输入token未知，没有用模型API或未经核实的分词器求取。历史scrapy身份原始输入3972 tokens只作历史规模参考，不是B的预测用量。

1. 固定scrapy身份消除了两臂已知system/taxonomy身份差异；并未证明身份因素普遍无影响。剩余default元数据相同，效应只能条件化于此固定配置。
2. 只有excerpt这一逻辑字段变化，其余输入和提示词相同，能够比较这一具体呈现组合与原形式。
3. 表格、列标签、行尾/标点、段落划分、例外邻近性和长度同时改变。**只能解释为呈现方式的整体效应，不能分解为某个排版特征的独立作用。**
4. section.span仍是15603–17155，跨度1552；B长度1643，二者不再相等。该span保留原窗口的来源位置，不是B的新坐标。模型可见的“文本长度与元数据一致性”关系也随呈现改变，必须作为整体效应中的残余限制。没有为了修正这一点而暗改section，亦未用填充字符强行配长。
5. 一组同期A→B只能提供探索性描述。温度0或相同指纹不能保证相同内部条件；未来须记录日期、路由可见字段、缓存和顺序，反序复核需另外授权。
6. 同一窗口、同一模型别名上的结果不能回答旧21窗全空的唯一根因，不能推及所有文档、最终Skill或Agent任务表现。

详见[text_statistics.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/text_statistics.json)、[identifiability_analysis.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/identifiability_analysis.json)。对于上述**整体呈现组合**问题，没有必须先补造的源规则证据缺口；若研究要求隔离纯表格/纯长度效应，则当前两臂设计不够，需另立更细的设计，不能借本实验作该因果宣称。

## 7. 后续执行边界与停止条件

本轮额度严格为**0**。后续计划详见[future_execution_plan.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/future_execution_plan.json)，仅供新任务授权后使用：

- 最小单元：同期内容形式A、B各一次，预定A→B，总计最多2次真实HTTP模型请求，每臂最多1次；旧响应不能替代同期A。
- 直接读取本次冻结的A/B请求字节；不重新构造、不更新模型可见run ID或metadata。发送前复核全部哈希、唯一excerpt diff及语义审计。
- 复用既有单请求传输器和持久两次门控，但新任务须先核对新输入绑定及A/B命名；不能直接运行仍绑定default/scrapy旧输入的身份实验入口。
- 关闭重试、重定向和repair，失败消耗该臂额度；另臂至多完成其一次。不得借超时、截断或非法JSON再发请求。
- 不调用Outline、Expand、compile、register、Agent或完整lab.py run，不修补输出或更换模型。
- 任一输入/代码指纹/diff/语义审查不匹配、缺新授权/凭据，或无法证明两次上限时，零调用停止。
- 两次额度用完即停止；指纹不同或缺失作为混杂记录，不补发以求对齐；非空但错误按错误记录，不追加搜索变体。
- 如观察到差异，反序及更多预注册重复需新的任务授权；一组不能给稳定因果定论。无差异也不能证明任何呈现形式都无影响。

本目录没有可发送模型的执行入口。未来阶段必须先通过其单请求/总次数门控检查再执行；本报告的GO不构成调用授权。

## 8. 完整性与最终决策

已核对587项受保护文件及5个完整目录清单，当前166项源码/备份、源文、s24m003历史运行、qsv历史、身份实验及反序复核、四份报告和原证据均未变。未修改全局领域身份或正式生成算法。保留当前已有预处理修复状态，不能称端到端源码完全未改。

本轮新增材料仅在本报告与同级content_form_design_001目录。完整哈希清单见[manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/manifest.json)；所有新输入仅为冻结的诊断候选，不代表已执行结果。

复核命令仅离线，不发送请求：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\content_form_design_001\verify_design.py"
~~~

**GO：源规则证据和限定范围的两臂设计已具备，可在新任务授权后进行最多两次的探索性内容形式对照。当前效应与候选质量仍未知。本轮模型API=0、Plan及其他模型阶段=0，完成后停止。**
