# Scrapy领域身份差异的反序复核

日期：2026-10-23（Asia/Shanghai）。固定工作树：D:/AS/AutoSkill-main。

**已证实：按B→A顺序完成本任务新授权的2次真实模型HTTP请求，各1次。逐字节复用上一轮live请求，B再次产生3个候选且原版Plan接受3个，A再次为0；两组及上一轮返回相同模型服务指纹。候选存在性差异在反序下得到复核。**

**已证实：目标FTP规则仍未完整表达，而且本次B候选2错误地将FTP与S3/GCS一并写为“不支持追加”，丢失“部分FTP服务器可能不支持APPE”的条件。非空复核成功不等于规则提取成功。证据支持但未证实：外部领域身份配置影响本窗口候选生成的假设获得进一步支持。未知：稳定因果、唯一根因及最终Skill/Agent效果。**

本轮输入7941、输出899、合计8840 tokens；重试/重定向/修复及其他模型阶段均0。额外调用额度为0，已停止。

## 1. 来源与离线预检

已阅读[上一轮领域身份报告](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_report.md)，并直接检查其实际live/A、live/B请求及原始响应，没有根据报告重建请求。

| 臂 | 直接复用的实际请求文件 | SHA-256 |
|---|---|---|
| B：scrapy | D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_ablation_001\live\B\request.json | edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c |
| A：default | D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_ablation_001\live\A\request.json | 670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb |

上轮完整manifest的36项证据及报告哈希全部核验通过。本轮冻结输入通过read_bytes直接复制，发送时也直接传递这些bytes；**没有调用提示词/taxonomy构造器，没有修改、重新格式化或重新序列化请求体**。

冻结副本：[B/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/B/request.json)、[A/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/A/request.json)。
绑定与预检：[replication_spec.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/replication_spec.json)、[preflight.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/preflight.json)。
原始上轮结果索引：[previous_results.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/previous_results.json)，其中保存准确来源、请求/响应SHA、原始content与结果，未改写原件。

参数逐项核对：

| 项目 | 两臂保持的实际设置 |
|---|---|
| endpoint | https://api.deepseek.com/v1/chat/completions |
| model | deepseek-flash |
| temperature / stream | 0.0 / false |
| max_tokens | 16384 |
| thinking | {"type":"disabled"} |
| 客户端超时 | 180秒 |
| max_candidates | 4 |
| excerpt | 1552字符，SHA-256=50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07 |

每臂完整参数与本臂上轮实际请求完全一致；正文、section、document.domain及全部document.metadata也随原始bytes保持不变。A/B之间仍仅是上一轮预注册的system身份行、taxonomy.domain_type和taxonomy.taxonomy_id三处差异。document.domain依旧为空，metadata中的default身份及family_name未同步修改。因此仍检验这三处身份字段的组合配置效应，不是完整pipeline所有领域元数据变化的效应。

两臂实际excerpt仍含overwrite=True覆盖、False追加定义、FTP默认True和部分FTP服务器APPE例外。本轮没有重新运行预处理或用窗口重建请求。

## 2. 调用上限与执行顺序

新增目录只有D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001及本同级报告。复用既有qsv_probe_001/probe.py的post_once、execute_once和保存响应后的本地Plan解析；新[replication.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/replication.py)只增加原字节校验、固定B→A顺序和新额度门控。

- 默认入口只做离线validate；只有显式--execute进入本次执行。
- 全局live目录排他创建，先写2次预算占用标记；每臂另有一次性排他目录。即使失败也不能续跑、重启重发。
- 固定仅遍历B、A各一次；原urllib传输器每臂只有一次opener.open；未使用SDK自动重试。
- NoRedirect禁止重定向；超时、HTTP失败、截断、非法JSON都不重试、不repair。
- 真实body先保存，原始响应字节先保存后解析。Plan接受数由原版_plan_unit_skills接收已保存响应stub计算，不连接模型，不运行Expand。

[test_replication.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/test_replication.py)的**5项本地合同测试全部通过**，测试进程audit hook禁止网络和子进程：原字节/参数/元数据；真实传输函数在fake opener下严格B后A且拒绝重定向、拒绝重复启动；超时和HTTP错误各占一次额度；非法JSON无修复；缺凭据零请求。记录见[contract_tests.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/contract_tests.json)、[contract_tests.log](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/contract_tests.log)。没有重跑旧Windows Oracle、原有框架测试或完整case。

实际客户端事件见[live/events.jsonl](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/events.jsonl)：

| 事件 | UTC |
|---|---|
| B开始唯一尝试 | 2026-10-23T10:44:34.884926+00:00 |
| B结束：NONEMPTY_PLAN | 2026-10-23T10:44:40.289866+00:00 |
| A开始唯一尝试 | 2026-10-23T10:44:40.290477+00:00 |
| A结束：EMPTY_PLAN | 2026-10-23T10:44:41.042076+00:00 |

因此本轮确为B完成后再发A，不是仅在报告中调换显示顺序。调用前零模型预检和脚本/输入/指标哈希已经保存，不依赖事后描述证明预检。

## 3. 两次真实响应

| 指标 | B：本轮先执行 | A：本轮后执行 |
|---|---|---|
| HTTP请求尝试 / 成功响应 | 1 / 1 | 1 / 1 |
| HTTP状态 | 200 | 200 |
| 严格JSON | 合法 | 合法 |
| 原始skills数量 | 3 | 0 |
| 原版Plan实际接受 | 3 | 0 |
| 状态 | NONEMPTY_PLAN | EMPTY_PLAN |
| 请求/响应模型 | deepseek-flash / deepseek-flash | deepseek-flash / deepseek-flash |
| finish_reason | stop | stop |
| system_fingerprint | e72d3c7f663d3e1383b00b3884cb4501 | e72d3c7f663d3e1383b00b3884cb4501 |
| 输入 / 输出 / 总tokens | 3972 / 894 / 4866 | 3969 / 5 / 3974 |
| 输入缓存命中 / 未命中tokens | 3838 / 134 | 3835 / 134 |
| 客户端耗时 | 5.403秒 | 0.750秒 |

本轮实际usage合计：输入7941、输出899、总8840，缓存已包含在输入中，不重复相加。上述数值来自本次响应，不以历史用量代替；人民币账单金额未核验。上轮8996 tokens不计入本轮8840。

| 对象 | 本轮SHA-256 |
|---|---|
| B实际发送请求 | edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c |
| B原始响应 | 7f01e6fff554097658d6746ab0705f7ccfba5e3e95ba1d94fff0b43bcdf92b4b |
| A实际发送请求 | 670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb |
| A原始响应 | a1d7e3be8e9053e19a7c7cc7b9c44f5651fcc9f7b5478f0269f8aeb3c92c5c3a |

对应原始文件：

- [live/B/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/B/request.json)、[live/B/response.raw.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/B/response.raw.json)、[live/B/result.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/B/result.json)。
- [live/A/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/A/request.json)、[live/A/response.raw.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/A/response.raw.json)、[live/A/result.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/A/result.json)。

两臂wire响应SHA与保存响应SHA均相同，没有回显凭据导致的脱敏。A的原始content逐字为{"skills": []}，是正常合法空计划；B的3个候选已经在原始content中出现，不是本地后处理补造。原版Plan接受属于列表/name/数量等轻量检查，不是规则语义验证或完整Skill验证。

## 4. 候选及FTP规则语义

A没有候选，目标语义均未表达；不对空候选推断错误断言。

B候选的实际名称、类型及description如下，完整其他字段保存在原始响应和result中：

| slot | 名称 | 资产类型 | 实际description |
|---:|---|---|---|
| 1 | 配置 Feed 导出定义 | session_skill | 为 Scrapy feed 导出配置一个或多个 feed 定义，按 format、encoding、fields、overwrite、store_empty、postprocessing 等键组装导出参数，并回退到对应全局设置。适用于需要把抓取到的 item 输出到文件、FTP、S3、GCS 或标准输出时。 |
| 2 | 按存储后端设置 overwrite 策略 | micro_skill | 根据目标存储后端选择 overwrite 默认值：本地文件系统与标准输出默认不覆盖，FTP/S3/GCS 默认覆盖且不支持追加。适用于配置导出目标时避免意外覆盖或追加失败。 |
| 3 | Feed 导出键与回退设置参考 | knowledge_reference | 列出 feed 定义可接受的键及其回退的全局设置，包括 format 为必填无回退、batch_item_count、encoding、fields、item_classes、item_filter、indent、item_export_kwargs、overwrite、store_empty、uri_params、postprocessing。适用于查阅导出配置项含义与默认值。 |

候选2的关键原文：

> 根据目标存储后端选择 overwrite 默认值：本地文件系统与标准输出默认不覆盖，FTP/S3/GCS 默认覆盖且不支持追加。适用于配置导出目标时避免意外覆盖或追加失败。

逐字段阅读了全部候选，其他字段及候选1/3都没有补足FTP显式False与APPE条件。评价沿用上一轮冻结指标，见[metrics.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/metrics.json)；语义证据指针和逐候选判断见[semantic_assessment.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/semantic_assessment.json)。

| 语义指标 | B判定 | 依据 |
|---|---|---|
| 明确FTP默认overwrite=True | **是，语义正确** | description明确FTP“默认覆盖”；按参数含义即True。虽未写字面True，但不是只凭标题或关键词判定 |
| 明确FTP显式overwrite=False时追加 | **否，并有冲突断言** | 没写显式False的映射，且把FTP一并说成“不支持追加”，不能当作仅压缩省略 |
| 保留部分FTP服务器不支持APPE例外 | **否** | “部分服务器”“可能”及APPE条件没有被保留，改成FTP无条件不支持追加 |
| 后端能力范围 | **存在错误泛化** | 把S3/GCS不支持追加的限制合并到FTP；不能从FTP默认覆盖推出FTP不能追加 |
| 完整目标规则表达 | **未通过** | 正确默认值不足以抵消追加行为与适用条件错误 |

这些判断来自候选实际description及全部字段，不从源文替候选补写规则。候选2的错误已在Plan原始响应中存在、且被Plan接受；不等于已证明后续Expand必然保留或修复该错误，因为本轮没有执行Expand。

## 5. 与上一轮比较

| 观测 | 上轮A→B | 本轮B→A |
|---|---|---|
| A原始 / Plan接受 | 0 / 0 | 0 / 0 |
| B原始 / Plan接受 | 3 / 3 | 3 / 3 |
| A/B服务指纹 | 均e72d3c7f663d3e1383b00b3884cb4501 | 同一指纹，且与上轮一致 |
| B默认FTP覆盖 | 正确明确 | 正确明确 |
| B显式FTP False追加 | 未明确 | 未明确，且追加能力被错误否定 |
| B APPE例外 | 保留部分FTP服务器条件 | 丢失，并泛化为FTP均不能追加 |
| B完整目标语义 | 未通过 | 未通过 |
| B候选文本/类型组成 | 配置、overwrite、后处理三项 | 配置、overwrite、配置参考三项 |

**复现的是候选存在性差异，不是相同候选文本或规则质量。** 当前有两对四次新诊断观察、每个身份2次，均来自同一冻结窗口；不将旧运行21个窗口算作21个重复任务或Agent实验。

B在先执行时仍非空、A后执行仍为空，进一步削弱“B仅因为总在第二个位置才非空”的简单解释，但不能排除更复杂的顺序/历史状态影响。两臂未观察到指纹差异混杂；相同指纹仍不证明所有服务端内部条件完全相同。缓存用量如实记录，没有把缓存机制认定为原因。

## 6. 分级结论

**已证实**

1. 两臂请求逐字节与上一轮实际live请求一致，所有参数保持不变，实际调用顺序反转为B→A。
2. 新增HTTP模型请求恰好2次，各臂一次，无重试、重定向、repair或其他模型阶段。
3. B=3、A=0再次出现，原始响应与Plan接受计数一致，两轮同指纹。
4. 输入中完整规则仍在；本轮B输出却将FTP追加能力错误泛化，完整目标语义未通过。
5. 相同B请求两次输出的候选文本与语义不同，即候选数量复现不等于内容精确复现。

**证据支持但未证实**

- 外部领域身份配置影响本窗口候选生成的假设获得进一步支持，已经不只是一对A后B的观察。
- 材料形式及其与身份配置的交互仍值得调查；本轮没有改变材料形式，所以不能给该因素定性。
- 默认值、显式参数分支和后端例外在概括候选时可能被压缩/混淆；本轮有具体输出错误证据，但没有模型内部机制证据。

**未知**

- 稳定效应大小、统计因果、外推到其他窗口/任务的范围；每臂2次不足以证明稳定因果或领域身份是唯一根因。
- 三处身份字段各自的作用，以及仍为default的document.metadata身份字段是否存在交互。
- 服务路由、内部状态、数值非确定性或其他不可见因素是否参与结果差异；不能仅凭输出变化认定模型权重变化或提供方故障。
- 旧21次全空的完整根因；本轮只复核HTTP019窗口。
- 最终SKILL.md质量、Agent正文读取、任务表现；没有执行相关阶段。

## 7. 下一步应否开展文档内容性质对照

**CONDITIONAL GO：值得在新的任务授权下进入文档内容性质对照的离线设计，仍不支持修改官方提示词、类型树或候选准入逻辑，也不支持直接开始正式退化/Agent实验。**

理由：身份配置对候选存在性的差异在反序下再次出现，而规则完整性两轮均未通过，本轮还出现了明确追加能力错误。下一阶段应以规则语义保真为主要观测，不能只追求非空候选。

最小单因素方向是固定一个身份条件（建议B）、相同模型/参数/提示词/section及其他字段，只对原始参数参考块与保持同等规则信息的另一种呈现形式作对照。首先离线核对True默认、显式False追加、部分服务器APPE例外及其他后端范围全部保留；不得加入源文没有的信息，不得将人工重述材料冒充原始Clean基线。再预注册输入diff、语义指标及明确调用额度。

这是后续建议，**本轮未构造文档变体、未启动内容对照，也未为其发送请求**。下一阶段必须有新的任务授权；本报告不自动延续调用预算。

## 8. 完整性、复现与停止

[protected_before.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/protected_before.json)及[final_integrity.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/final_integrity.json)核对**557项受保护文件、4个完整目录成员清单，全部不变**。包含当前166项冻结源码/备份文件、Scrapy s24m003历史135个文件、qsv历史170个文件、此前qsv探针、上一轮领域身份实验整个目录及所有前置报告/证据。当前源码原先已有预处理修复，本轮保留既有状态；没有修改生产源码、Plan提示词、taxonomy类型树或准入代码。

新增材料均在本复核目录及本报告。没有覆盖历史运行、请求、响应或测试记录；没有调用完整lab.py run。Authorization仅在内存构造，不保存请求头或密钥；新增证据和报告进行真实凭据字节无泄露检查，结果见credential_safety_check.json。

离线核验命令（不发模型请求）：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_replication_001\replication.py"
~~~

新增5项本地合同测试：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_replication_001\test_replication.py"
~~~

两次真实请求已占用live排他门控，不可续跑；禁止更换目录追加复发。原始响应、判定、实际usage及顺序见[live/summary.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/live/summary.json)、[post_replication_summary.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/post_replication_summary.json)；全部新增证据及报告的SHA见[manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_replication_001/manifest.json)。

**本轮完成：候选存在性差异复核成功；完整FTP规则表达失败。保持算法冻结，实际2次HTTP、8840 tokens。已停止，等待新的任务授权。**
