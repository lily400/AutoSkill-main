# Scrapy文档内容呈现形式A/B探索性实验

日期：2026-10-23（Asia/Shanghai）。固定工作树：D:/AS/AutoSkill-main。

**已证实：按A→B各执行1次真实模型HTTP请求，总计2次。A原始参考形式、B表格形式均返回3个原始候选，原版Plan均接受3个；HTTP200、严格JSON合法、finish_reason=stop，两组服务指纹相同。两组均明确FTP默认覆盖，但均未明确表达FTP显式overwrite=False追加，也均遗漏部分FTP服务器可能不支持APPE的条件。按预注册标准，两组均为“非空但部分”，完整规则表达均未通过。**

**证据支持但未证实：本次冻结输入对没有显示表格组合在主要指标上的改善。未知：该结果能否复现、呈现形式的稳定效应及各组成因素贡献。不能由一次无改善证明呈现无影响，也不能据此修改官方算法。**

本轮实际usage：输入7964、输出1662、合计9626 tokens。重试、重定向、repair、Outline、Expand、compile、register、Agent和额外语义评审模型调用均0。两次额度已用完，停止。

## 1. 冻结设计与执行前核验

设计报告：[content_form_experiment_design.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_experiment_design.md)。
冻结设计目录：D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001。
本轮新增证据集中在D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001，没有改写设计目录或历史记录。

按任务要求先运行：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\content_form_design_001\verify_design.py"
~~~

离线设计10项检查全部通过，5种错误变体被拒绝；全设计manifest的23份证据和报告SHA均匹配。该验证器写回的验证文件与原冻结字节相同，完整设计清单仍通过。此时模型调用0次。

核对内容包括：原文规则/位置/引用SHA、语义等价审计、仅excerpt逻辑diff、未改前后文、五个后端事实/作用域、构造器字符串匹配、预注册指标、长度/span关系和已有文件完整性。既有验证记录见[validation_results.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/validation_results.json)。

本轮另外增加4项**仅针对新输入绑定**的禁网合同测试，全部通过；没有重跑旧框架或Windows Oracle测试。测试验证直接字节读取、正确A/B身份和冻结span；复用的实际post函数在fake opener中恰好open两次且拒绝重定向；失败/非法JSON不重试或repair；重复/增加换行的请求在post前拒绝。证据见[test_binding.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/test_binding.py)、[contract_tests.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/contract_tests.json)、[contract_tests.log](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/contract_tests.log)。

最终调用前预检：[preflight.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/preflight.json)。记录当时调用数0、四项测试通过、设计指标SHA、脚本SHA及612项历史文件不变。

## 2. 实际输入与参数

本轮A是**固定scrapy身份下的原始excerpt**，不是先前default身份的A。B是同一scrapy身份下的人工表格变体，不能当成原始Clean或正式退化文档。

| 臂 | 冻结请求路径 | 本轮实际发送请求SHA-256 |
|---|---|---|
| A | D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\content_form_design_001\A\request.json | edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c |
| B | D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\content_form_design_001\B\request.json | 3d5193a46be9999e0e6c13745dcf2cecf970c8e168c5419721c9e3fea023dabf |

两组实际发送文件live/A/request.json、live/B/request.json均与上述冻结文件逐字节相同，匹配用户给定SHA。**只用read_bytes读取，不重新构造、格式化或序列化请求体**。

固定参数：endpoint=https://api.deepseek.com/v1/chat/completions；model=deepseek-flash；temperature=0.0；stream=false；max_tokens=16384；thinking={"type":"disabled"}；客户端超时180秒；max_candidates=4。system、taxonomy、其他元数据、工具定义和消息结构均未增加或改写。

A/B唯一逻辑diff仍为/messages/1/content/excerpt。document.domain为空，metadata保留历史default字段，system/taxonomy外部身份为scrapy；两组这一组合完全相同，没有修改全局领域配置。

**已知限制原样保留**：A excerpt1552字符，B1643字符；两组section.span均为15603–17155，跨度1552。没有改span、添加配长填充或重写任何输入。

## 3. 两次上限、顺序及失败保护

本轮[execute_content_form.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/execute_content_form.py)只负责新输入绑定和记录，复用domain_identity_ablation_001/ablation.py的原A→B两次门控，以及qsv_probe_001/probe.py的单次urllib传输/保存响应/原版Plan本地解析。没有调用旧实验main/validate/build_arms，避免旧default/scrapy绑定或重建输入。

- 全局live目录先排他创建并占用两次预算，每臂目录再排他创建；失败也不可重启续发。
- 固定A→B各一次，单请求传输器没有SDK重试或重定向；NoRedirect拒绝跳转。
- 新wrapper还对两个已知请求SHA分别设置一次消耗标记，任何重复或修改字节均在HTTP前拒绝。每次wrapper只调用一次原post函数，无retry/repair分支。
- 原始body先落盘；原始响应字节先落盘，随后作严格JSON和原版Plan本地解析。后者用保存响应stub，不连接模型、不执行Expand。
- Authorization仅在内存用于本次授权，不保存请求头或秘密值。

实际事件见[live/events.jsonl](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/events.jsonl)：

| 客户端事件 | UTC |
|---|---|
| A唯一HTTP尝试开始 | 2026-10-23T11:36:35.568399+00:00 |
| A传输返回 | 2026-10-23T11:36:40.095104+00:00 |
| B唯一HTTP尝试开始 | 2026-10-23T11:36:40.379903+00:00 |
| B传输返回 | 2026-10-23T11:36:45.609662+00:00 |

因此顺序确为A完成后再B。实际模型HTTP计数2，每臂1；原版Plan对两份保存响应的本地解析不构成额外HTTP调用。合同测试的模拟传输也不计模型请求。

## 4. 原始响应及实际用量

| 指标 | A：原始形式 | B：表格形式 |
|---|---|---|
| 尝试 / 成功响应 | 1 / 1 | 1 / 1 |
| HTTP状态 | 200 | 200 |
| 严格JSON / finish_reason | 合法 / stop | 合法 / stop |
| 原始候选数 | 3 | 3 |
| 原版Plan接受数 | 3 | 3 |
| 调用/解析状态 | NONEMPTY_PLAN | NONEMPTY_PLAN |
| 请求/响应model | deepseek-flash / deepseek-flash | deepseek-flash / deepseek-flash |
| system_fingerprint | e72d3c7f663d3e1383b00b3884cb4501 | e72d3c7f663d3e1383b00b3884cb4501 |
| 输入 / 输出 / 总tokens | 3972 / 804 / 4776 | 3992 / 858 / 4850 |
| 输入缓存命中 / 未命中tokens | 3838 / 134 | 2432 / 1560 |
| 执行记录耗时（含本地解析） | 4.810秒 | 5.234秒 |
| 原始响应SHA-256 | 8fd50ac8681e8e7327dca3851f074e6fed23dbfbca4d26595c191edcf1871d1b | 0d0247a64645d36da6e56e9e68d793df23bbafeac1aabb0d3f236483849026e8 |

B比A实际多20个输入tokens；这是本次usage观察，不是预估。缓存命中已包含在输入内，不重复相加。合计9626 tokens，未取得人民币账单，不编造金额。

原始证据：

- A：[live/A/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/A/request.json)、[live/A/response.raw.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/A/response.raw.json)、[live/A/result.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/A/result.json)、[live/A/candidates.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/A/candidates.json)。
- B：[live/B/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/B/request.json)、[live/B/response.raw.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/B/response.raw.json)、[live/B/result.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/B/result.json)、[live/B/candidates.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/live/B/candidates.json)。

各臂content.txt另存原始message.content便于阅读。完整原始envelope保留model、created、finish_reason、指纹和usage。wire响应SHA与保存SHA一致，没有脱敏造成的内容变化。

两组非空都直接来自模型原始响应；没有本地补写候选或非空被全部过滤。原版Plan接受是其轻量列表/name/数量等处理的结果，不是规则语义或完整Skill验证。

## 5. 逐候选审查

评价严格沿用设计中的[preregistered_metrics.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_design_001/preregistered_metrics.json)，SHA-256=265501955ab311f6446b4d651cddf12f1af3a9178cb62a1e47672e4aec94f80d。没有临时更改候选定义、放松False/APPE要求或追加评审模型。

全部6个候选的所有字段均已阅读；原始全部字段及逐字段证据指针保存在[semantic_assessment.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/semantic_assessment.json)和各臂candidates.json。表中“无关”仅指没有具体FTP目标规则表达，不否定该候选对其他用途的价值。

| 臂 | slot | 名称 | 类型 | 实际description | 相对FTP目标的分类 |
|---|---:|---|---|---|---|
| A | 1 | 配置 Scrapy Feed 导出 | session_skill | 根据目标格式、存储后端与覆盖策略，为每个 feed 定义填写必填与回退键，完成 Scrapy 数据导出配置。适用于需要把抓取到的 item 输出到文件、FTP、S3、GCS 或标准输出的场景。 | 与FTP目标规则无关 |
| A | 2 | 选择 Feed 覆盖与追加策略 | micro_skill | 依据存储后端决定 overwrite 取值：本地文件默认追加、FTP 默认覆盖、S3/GCS 默认覆盖且不支持追加、标准输出不支持覆盖。用于避免导出时意外覆盖或追加失败。 | 非空但部分 |
| A | 3 | Feed 导出键与回退设置参考 | knowledge_reference | 列出 feed 定义可接受的键及其对应回退设置（如 batch_item_count、encoding、fields、item_filter、postprocessing 等），供配置时查阅。 | 与FTP目标规则无关 |
| B | 1 | 配置 Feed 导出定义 | session_skill | 按 FEEDS 字典为每个导出目标声明 format、存储 URI、字段、编码、覆盖策略等键，并依据回退设置补齐缺省值。用于需要把抓取到的 item 导出到文件、FTP、S3、GCS 或标准输出的场景。 | 与FTP目标规则无关 |
| B | 2 | 选择覆盖与追加策略 | micro_skill | 根据存储后端决定 overwrite 取值：本地文件系统与标准输出默认 False，FTP/S3/GCS 默认 True，并注意 S3/GCS 不支持追加、标准输出不支持覆盖的限制。用于配置导出目标时避免数据被意外覆盖或追加失败。 | 非空但部分 |
| B | 3 | 配置导出后处理插件链 | micro_skill | 通过 postprocessing 键按列表顺序声明后处理插件，插件将按传入顺序依次执行。用于需要在 item 导出前后做过滤或转换的场景。 | 与FTP目标规则无关 |

### 5.1 A候选2的具体证据

> 依据存储后端决定 overwrite 取值：本地文件默认追加、FTP 默认覆盖、S3/GCS 默认覆盖且不支持追加、标准输出不支持覆盖。用于避免导出时意外覆盖或追加失败。

“FTP 默认覆盖”明确满足默认行为。其“本地文件默认追加”不能代替FTP显式False分支；标题“覆盖与追加策略”也不足以证明参数关系。全部字段没有Some/may/APPE等服务器追加条件。S3/GCS“不支持追加”只修饰S3/GCS，没有把该限制断言为FTP限制。

### 5.2 B候选2的具体证据

> 根据存储后端决定 overwrite 取值：本地文件系统与标准输出默认 False，FTP/S3/GCS 默认 True，并注意 S3/GCS 不支持追加、标准输出不支持覆盖的限制。用于配置导出目标时避免数据被意外覆盖或追加失败。

“FTP/S3/GCS 默认True”正确表达共同默认值；随后的不支持追加限制明确归于S3/GCS，**不能因为FTP出现在前一组共同默认值中，就误判为错误泛化**。但本地/stdout默认False并未表达FTP显式False追加，泛称“规避后端限制”也没有保留具体APPE条件。

候选1/3及其他字段均没有补足上述缺失关系。没有将候选片段跨项拼接，也没有从输入源文或假想Expand推断模型实际表达了规则。

| 预注册语义指标 | A | B |
|---|---|---|
| FTP默认True/覆盖 | 正确明确：候选2 | 正确明确：候选2 |
| FTP显式False选择追加 | 遗漏 | 遗漏 |
| 部分FTP服务器可能不支持APPE | 遗漏 | 遗漏 |
| 一概称所有FTP不支持追加 | 未观察到该断言 | 未观察到该断言 |
| 保证所有FTP都能成功追加 | 未观察到该断言 | 未观察到该断言 |
| S3/GCS、本地、stdout规则错移到FTP | 未观察到明确错移 | 未观察到明确错移 |
| 单个完整候选数 | 0 | 0 |
| 接受候选之间的目标冲突 | 未观察到 | 未观察到 |
| 运行级完整目标表达 | 未通过 | 未通过 |
| 最终分类 | **非空但部分** | **非空但部分** |

这是明确的省略模式，**不能把遗漏等同于错误断言，也不能把没有观察到FTP目标错误等同于全部非目标内容正确**。辅助差异是B明确列出本地/stdout默认False，A对stdout只提不能覆盖；这不补足FTP分支或APPE条件，不改变主要结论。

## 6. 分级结论

### 已证实

1. 两个实际请求均匹配用户预期SHA，与冻结文件逐字节一致，只有已预注册的excerpt呈现差异。
2. A→B各1次HTTP，均200、严格JSON合法、stop；无重试、重定向、repair或其他模型调用。
3. 两组均3原始候选/3接受候选；相同指纹，没有本对指纹差异混杂。
4. 两组均保留FTP默认覆盖，均遗漏FTP显式False追加与APPE条件；完整规则标准均未通过。
5. 本对主要观测——候选生成、接受数、完整表达、明确目标错误——未显示B优于A。

### 证据支持但未证实

- 对这个冻结窗口，两种呈现都出现将参数默认值保留、将显式分支和条件省略的结果，值得作为可复核的省略模式记录。
- 本次表格化没有显示预期语义收益，不能把表格直接作为已验证修复。
- 同一原始请求历史候选曾部分保留或错误泛化FTP条件，而本次遗漏；输出内容可变，因此数量相同不能代表语义稳定。该历史事实不是新实验，也不用于替代本次同期A。

### 未知

- 无改善是否可重复，真实效应大小或稳定因果。一次A/B无差异不证明呈现形式普遍无影响。
- 表格、长度、条件邻近关系及span一致性分别起多大作用。
- 相同指纹下不可见路由、内部状态、数值非确定性、调用顺序或缓存是否参与差异。没有证据为它们指定因果责任。
- 旧21窗全空的唯一根因；本实验不能推及全部Scrapy窗口、其他文档或模型。
- 最终Skill、Expand可能保留/改变的语义、Agent正文读取与任务表现；本轮没有执行这些阶段。

没有将合法空数组当程序异常，也没有把非空当作规则提取成功。本次两组实际上均非空，不能声称重现了零候选失败。

## 7. 已知混杂因素原样保留

本实验是呈现方式**整体效应**探索，不是纯表格排版因果实验：

- excerpt长度1552→1643，物理行35→36，空行分隔文本块8→9；完整请求15737→15830字节。本次模型实际输入3972→3992 tokens。
- 表格列名、段落组织、标点、APPE句子合并换行、例外与FTP行的邻近关系和后续空行同时变化。
- B仍保留原section.span=15603–17155（1552），与B1643字符不一致；没有更新span或填充。此来源元数据/文本长度关系可影响模型，不能从表格组织作用中分离。
- document元数据仍有default身份字段，两组均保持固定scrapy外部system/taxonomy身份，结论条件化于这套冻结组合。
- 固定顺序A→B，一臂一次；缓存命中量不同。相同model别名和指纹不代表所有服务条件相同。

因此不能以本对结果证明某个单独排版特征有效或无效，也不能据此开始正式三条件文档退化实验。

## 8. 下一步与算法冻结

**继续冻结官方提示词、taxonomy类型树和候选准入代码。** 本轮没有支持算法修改的新因果证据，也没有产生可判为完整目标规则的候选。没有手工补写False/APPE、改输入重试或把B输出登记为正式Skill。

独立复核有有限价值：如果下一步仍要判断这个具体组合的省略模式是否稳定，可另行预注册一次B→A、各一次的独立复核，沿用同一请求和指标。这是稳定性检查，不是为了反复抽样直到出现正结果；本次没有观察到主要指标收益，不建议直接扩大为多轮或多窗口表格化实验。

本报告不授权任何新请求。复核、其他文档形式、prompt修改、Expand或Agent都需要新任务授权。当前2次额度已全部使用，停止；不自动执行反序或重复。

## 9. 完整性与复核入口

[protected_before.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/protected_before.json)与[final_integrity.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/final_integrity.json)复核**612项受保护文件、6个完整目录清单，全部不变**：包含当前166项冻结源码/备份、源文、原s24m003/qsv运行、先前探针、领域身份实验/复核、全部前置报告，以及整个content_form_design_001目录和其报告。

保持源码原先已有预处理修复状态，本轮无新生产源码修改；不能称整个端到端源码是从未改过的官方原版。没有更新全局身份配置或改动官方提取方法。

真实凭据仅在内存用于授权，新增证据和报告作真实秘密字节无泄露检查，见credential_safety_check.json；没有保存Authorization头。完整新证据和报告SHA见[manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/manifest.json)。

离线复核命令，不发送请求：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\content_form_ablation_001\execute_content_form.py"
~~~

本轮正式执行已占用live永久门控，不可换目录续发。actual usage及状态汇总见[post_experiment_summary.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/content_form_ablation_001/post_experiment_summary.json)。

**完成：2次真实HTTP，9626 tokens；A=3/3、B=3/3，两组均非空但部分，完整FTP表达均未通过。原始证据保留，官方算法继续冻结，本轮停止。**
