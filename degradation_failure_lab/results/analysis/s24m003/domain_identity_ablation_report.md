# Scrapy s24m003：领域身份受控对照实验

日期：2026-10-23（Asia/Shanghai）。

**已证实：完成本任务新授权的2次HTTP模型请求，A、B各1次，无重试或其他模型调用。A原始default身份返回0候选；B仅改变构造器生成的身份配置后返回3候选，原版Plan本地接受3个；两组指纹相同。B候选2明确表达FTP默认覆盖与部分服务器不支持APPE追加，但未明确表达“FTP显式overwrite=False时追加”，因此未达到预注册的完整目标规则表达标准。**

**证据支持但未证实：外部领域身份配置可能影响这个Scrapy窗口的候选生成。未知：该效应是否稳定、具体哪个身份字段起作用、旧运行21窗全空的完整因果根因，以及最终Skill/Agent质量。保持当前官方Plan提示词及准入逻辑冻结；本轮不修改算法，也不将非空候选视为完整提取成功。**

## 1. 范围、路径与实际执行

固定工作树D:/AS/AutoSkill-main；源码D:/AS/AutoSkill-main/AutoSkill-main；实验目录D:/AS/AutoSkill-main/degradation_failure_lab。本任务描述中的degradation_lab/results引用不存在，实际两份前置报告均位于degradation_failure_lab/results/analysis/s24m003，本轮使用实际文件，没有创建重复目录。

前置报告：

- [s24m003_zero_candidate_root_cause.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/s24m003_zero_candidate_root_cause.md)
- [followup_qsv_probe_report.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/followup_qsv_probe_report.md)

全部新增脚本、冻结输入、差异、测试和本次响应集中在D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001。本报告是唯一新增的同级总报告，历史数据未覆盖。

实际顺序：读取原始证据 → 禁网离线调用现有构造器 → 冻结A/B与指标 → 7项本地合同测试 → 保存preflight → 新授权A、B各一次 → 本地解析/语义审查/完整性复核 → 停止。没有执行lab.py run、Outline、Expand、compile、register或Agent。此前qsv探针的1次额度没有被复用，本任务新额度2次已用完。

## 2. 原始证据的直接核对

| 对象 | 准确来源 | 请求SHA-256 | 响应SHA-256 | 原始候选数 |
|---|---|---|---|---:|
| Scrapy目标窗 | runs/case024_scrapy/clean/s24m003/http/019/request.json和response.json | 670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb | 5cee685f54c03ddeeb30af4800d6ead22d7f862d7c20a897770eb1132ff07c2a | 0 |
| qsv历史成功 | runs/case001_qsv_select/clean/raecd75e08b34/http/002/request.json和response.json | e346e5e435b94d0c92e0fb3b1705281e31996a4d0399c9c7b7ec702dce65c2fe | 778fe551dc895de75f56bd8aa57da1ec5c74234eefd4c513ce2d2f4b10147773 | 4 |
| qsv当前正对照 | results/analysis/s24m003/qsv_probe_001/live_001/request.json和response.raw.json | e346e5e435b94d0c92e0fb3b1705281e31996a4d0399c9c7b7ec702dce65c2fe | a96c71b46dcbafddc44484a61373d9e3ac43b431c11f03c76ebf235fb75c2b33 | 3 |

上表路径均相对实验目录。完整绝对路径、参数、原始content、usage与指纹见[historical_evidence.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/historical_evidence.json)；不是根据报告手工重建请求。

Scrapy原请求绝对路径：D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m003\http\019\request.json。
A冻结字节与该文件完全相同，SHA-256为670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb。

HTTP019实际excerpt为1552字符，SHA-256为50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07。源文为s24m003/inputs/input001/feed-exports.md，SHA-256为a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d；来自SkillGenBench固定发布材料，未将其描述为最新官方完整手册。

本轮再次直接读取请求，确认overwrite含义、FTP默认True、False追加定义及部分FTP服务器不支持APPE都在同一excerpt。源文438–449及原映射见前置报告/evidence/target_window_source_map.json。本轮无需再次预处理、Outline或全量扫描。

历史qsv和当前qsv输入相同；qsv当前正对照与Scrapy旧运行均返回指纹e72d3c7f663d3e1383b00b3884cb4501。该事实只建立有用正对照，不证明所有服务内部条件完全一致。

## 3. 构造器行为及预注册字段级diff

调用当前未修改的现有函数：

- AutoSkill4Doc/taxonomy.py:845–885，load_skill_taxonomy；先载default，尝试领域覆盖，再设置身份字段。
- 同文件:678–683，prompt_guidance；向system写入外部领域身份行。
- 同文件:780–831，to_dict；序列化taxonomy。
- AutoSkill4Doc/prompts.py:39–109及332–350，build_offline_extract_prompt / maybe_offline_prompt(kind=extract_plan)。
- AutoSkill4Doc/stages/extractor.py:756–795，_build_unit_payload；taxonomy与document是分开的字段。本轮冻结原user，仅用现有taxonomy构造器替换taxonomy；不重跑整条文档元数据流水线。

已离线验证：default构造出的system与真实HTTP019逐字相同，taxonomy字典完全相同，user用原序列化方式重建也逐字相同。B调用同一构造器，仅外部domain_type传scrapy。

内置taxonomy只有chemistry、default、psychology，没有scrapy.yaml。因此本次scrapy走FileNotFoundError后的空overlay分支，沿用default的所有类型/树/标签；没有创建Scrapy专用树或暗改候选定义。

| 完整字段路径（user的JSON字符串展开后） | A | B |
|---|---|---|
| /messages/0/content内唯一身份行 | Domain type is externally provided as default（原文带代码引号） | 同一行的default改scrapy |
| /messages/1/content/taxonomy/domain_type | default | scrapy |
| /messages/1/content/taxonomy/taxonomy_id | default | scrapy |

完整system字符串只允许这一行变化，其他任何字符变化均拒绝。其余全部字段相等；不是只检查上述三个键而忽略新增/删除字段。

完整字段diff：[field_diff.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/field_diff.json)；system逐行diff：[system_prompt.diff](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/system_prompt.diff)；完整序列化请求diff：[request_body.diff](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/request_body.diff)。

明确保持不变：

- document.domain仍为空字符串；document及其所有metadata逐字段相同。
- metadata中的domain_type、taxonomy_id、profile_id、domain_root_id和family_name保留历史值；family_name仍为“未分类技能”，没有隐式重分类。原lab_run_id/source路径也保持不变，本次探针ID只写外部日志。
- excerpt、section及标题/上下文、max_candidates=4完全相同；两臂excerpt哈希相同。
- taxonomy的asset_types、asset_tree、domain_root、family候选、显示标签等全部相同。
- model=deepseek-flash；endpoint=https://api.deepseek.com/v1/chat/completions；temperature=0.0；stream=false；max_tokens=16384；thinking={"type":"disabled"}；超时180秒。没有添加response_format、额外消息或其他参数。

**解释范围**：操纵的是预注册的“外部身份配置所产生的system行+taxonomy两个身份字段”的组合效应，不是单独一个序列化字段的效应，也不是重跑完整pipeline后所有领域元数据的总效应。保留的default文档元数据是控制要求，不应暗中同步为scrapy。

## 4. 请求上限与离线验收

复用qsv_probe_001/probe.py的post_once、execute_once和本地原版Plan解析，不重写客户端/提取器。新入口[ablation.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/ablation.py)只实现固定A/B和全局两次门控：

1. validate在调用前重新校验历史请求、构造器输出、字段diff、全部请求参数、脚本SHA及受保护历史文件。
2. live目录排他创建并持久写reservation.json；不能续跑或重新发送任何一臂。每臂又由原execute_once排他创建目录。
3. 固定遍历A、B，各调用一次唯一urllib opener.open；无SDK、无循环重试、无JSON repair、无重定向。失败也占用该臂的一次额度。
4. 保存准备发送的真实body字节；响应原始字节先保存，随后才解析。
5. native Plan使用已保存响应stub，调用原版_plan_unit_skills本地分支；不实例化联网客户端、不触发Expand。

[test_ablation.py](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/test_ablation.py)的**7项新增合同测试全部通过**，测试进程audit hook禁止socket/子进程。覆盖：原始字节与三处diff；拒绝excerpt/document/section/候选上限/temperature/类型树/额外system指令变化；成功后拒绝重跑；超时不重试；HTTP错误不重试；真实post_once在fake opener下两臂各open一次且NoRedirect拒绝跳转；缺凭据零调用。结果见[contract_tests.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/contract_tests.json)和[contract_tests.log](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/contract_tests.log)。

没有重跑旧Windows任务Oracle或Git专属框架测试。上述模拟调用不计真实模型请求；旧qsv探针的11项合同测试只复用既有证据。

阶段A结束的零调用预检记录：[preflight.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/preflight.json)。预注册指标在发送前冻结于[preregistered_metrics.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/preregistered_metrics.json)，其哈希已写入preflight。真实调用前两臂请求SHA和脚本SHA亦已冻结。

## 5. 两次真实请求及原始结果

| 指标 | A：default原输入 | B：scrapy外部身份 |
|---|---|---|
| 模型HTTP尝试 | 1 | 1 |
| HTTP / finish_reason | 200 / stop | 200 / stop |
| 严格JSON | 合法 | 合法 |
| 原始候选数 / 原版Plan接受数 | 0 / 0 | 3 / 3 |
| 状态 | EMPTY_PLAN | NONEMPTY_PLAN |
| 请求/响应model | deepseek-flash / deepseek-flash | deepseek-flash / deepseek-flash |
| system_fingerprint | e72d3c7f663d3e1383b00b3884cb4501 | e72d3c7f663d3e1383b00b3884cb4501 |
| 服务响应created换算北京时间 | 2026-10-23T18:28:46+08:00 | 2026-10-23T18:28:47+08:00 |
| 记录耗时 | 1.159秒 | 6.338秒 |
| 输入 / 输出 / 总tokens | 3969 / 5 / 3974 | 3972 / 1050 / 5022 |
| 缓存命中输入tokens（已包含在输入中） | 3835 | 256 |

A原始content逐字为{"skills": []}，不是空字符串、格式错误或本地过滤掉候选。B原始skills为3个dict，原版Plan也接受3个，不存在非空变零。原版Plan接受只指该阶段的name/list/数量等轻量检查，不代表详细Expand验证或canonical Skill成功。

两臂共**2次真实模型请求，输入7941、输出1055、合计8996 tokens**。重试0，重定向0，repair0，Outline/Expand/compile/register/Agent调用0。使用原始响应usage，不重复加缓存token；未取得可靠人民币账单，金额未知。

请求：[live/A/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/live/A/request.json)；[live/B/request.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/live/B/request.json)。
响应：[live/A/response.raw.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/live/A/response.raw.json)；[live/B/response.raw.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/live/B/response.raw.json)。
原始content另存各臂content.txt便于审查；原始envelope保持字节不变。

| 对象 | SHA-256 |
|---|---|
| A实际请求 | 670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb |
| A原始响应 | e12c3654cef1e05b6c8e95d7d0114dbfe50ff83cb2ff6a71b9c93792cfdd064d |
| B实际请求 | edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c |
| B原始响应 | c6b68a7987a1ea81572f6d9bd01759ad32f611939e626e5820b90edfb2b2368e |

wire响应SHA与保存响应SHA一致，无脱敏导致的响应变化。每臂attempt.json/result.json及全局live/reservation.json、live/summary.json保存调用门控、参数绑定及结果。

## 6. 目标FTP规则语义审查

逐一检查全部3候选的所有实际字段，不以标题或evidence_span_hint关键词判定。完整逐候选记录与原文证据指针见[semantic_assessment.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/semantic_assessment.json)。

| B候选 | 资产类型 | 可见evidence_span_hint | FTP目标规则覆盖 |
|---|---|---|---|
| 配置 Feed 导出定义 | session_skill | The following is a list of the accepted keys and the setting that is used as a fallback value | 提及overwrite及FTP，但不表达目标默认值、显式False或APPE关系 |
| 按存储后端确定 overwrite 语义 | micro_skill | overwrite: whether to overwrite the file if it already exists | 默认True与APPE例外明确；FTP显式False关系未明确 |
| 配置导出后处理插件链 | micro_skill | postprocessing: list of plugins to use for post-processing | 没有目标规则表达 |

候选2的实际description是：

> 根据所选存储后端决定 overwrite 取值：本地文件系统默认 False（追加），FTP 默认 True（覆盖，但部分服务器不支持 APPE 追加），S3 与 GCS 默认 True 且不支持追加，标准输出默认 False 且不支持覆盖。用于避免因追加/覆盖语义不符导致数据丢失或写入失败。

| 预注册语义指标 | A | B |
|---|---|---|
| 明确FTP默认overwrite=True | 无候选，未表达 | **正确明确**：候选2的FTP默认True（覆盖） |
| 正确区分FTP显式overwrite=False时追加 | 无候选，未表达 | **未明确表达**：False（追加）只直接用于本地默认值；不得替候选补写FTP参数映射 |
| 保留部分FTP服务器不支持APPE例外 | 无候选，未表达 | **正确明确**：候选2保留“部分服务器”，非一律不能追加 |
| 错误泛化到其他后端 | 无候选，不适用 | **未观察到该项明确错误**：分别列Local=False、FTP=True、S3/GCS=True不追加、stdout=False不覆盖；APPE例外局限FTP |
| 完整目标规则表达 | **未证明** | **未达到预注册完整表达标准** |

这是缺少显式关系，**不是候选声称FTP不能追加，也不是原版Plan schema拒绝**。Plan本来是概括性规划，不能将其压缩省略直接等同于最终Skill必然缺失；本轮禁止Expand，最终规则保真仍未知。B非空、包含相关语义均为事实，但不能将其报告成完整目标规则提取成功。

## 7. 根因判断与证据边界

### 已证实

- 同一真实Scrapy excerpt，在同期两臂中出现A空、B非空；仅三处预注册身份变化，正文与其他元数据不变。
- 两组model/endpoint/参数及返回指纹相同；和旧Scrapy、当前qsv正对照指纹也一致。
- 非空候选已存在于B原始响应，不是本地合成、修补或解析器制造。
- 本次B输出反驳“该原始材料在所有身份条件下都只能返回空”的绝对解释。不能据此推及所有窗口、所有运行或正式Skill。
- B部分恢复FTP语义，未完整表达显式False的对应关系。

### 证据支持但未证实

- 外部domain_type配置可能影响候选生成，值得作为诊断因素继续验证；本次比跨文档qsv/Scrapy比较更直接。
- 领域身份与材料形式的交互可能存在，但本次没有操纵材料形式，不能判定交互。
- 保守prompt/材料操作性仍是可能因素，但当前证据不足以修改提示词、候选定义或准入逻辑。

### 未知

- 一次A/B是否可重复，以及效应大小或统计因果；temperature=0不保证服务端严格确定性。
- 三处身份字段各自的作用；document.metadata中仍为default的身份字段是否调节结果。
- 相同system_fingerprint无法控制所有内部路由、批处理/数值非确定性等条件；没有记录内部推理。
- 执行顺序固定A后B，缓存命中量也不同；这些差异已经记录，不能据此声称缓存或顺序导致结果。
- 为什么旧运行其余20窗为空；本轮只检验目标窗，不外推全部21次的唯一根因。
- 最终Skill的完整性与下游Agent表现。本次候选数不等于Skill质量或任务成功率。

合法空数组仍是允许输出，不能把A空等同程序异常，也不能从这对观察直接给算法缺陷定性。

## 8. 下一步决策与停止条件

**CONDITIONAL GO：支持继续最小诊断，不支持立即改算法或启动正式退化/Agent实验。**

文档内容性质对照仍值得做，但**不应排在身份效应复核之前**。本次已经用相同原始正文得到候选；眼下最省成本、最有解释力的下一步是另行批准后复核这一对身份输入（例如反转B/A顺序，各一次，仍使用冻结请求及相同语义指标），先判断差异能否再次出现。该建议不构成新调用授权，也不能仅凭再一对就声称稳定因果。

如后续确需材料性质对照，应固定领域身份和所有其他字段，只预注册改变excerpt的一种呈现形式，并保持规则信息量和例外不变，另立诊断输入版本；不得把人工操作化后的材料冒充原始Clean发布文档。先离线列出语义保真与字段diff，再申请具体调用额度。不能同时修改prompt、taxonomy树、模型和正文。

**继续冻结官方Plan提示词、taxonomy类型树及候选准入代码。** 本轮不改全局domain_type、不创建scrapy.yaml、不修补候选、不生成正式Skill。当前源码原先已有lab-preprocess-v1的两处修复，本轮只是保持这一既有状态；不能将整个端到端流程称为完全未修改的官方基线。

停止条件：本任务2次模型请求额度已用完；任何额外请求、重复、Expand或Agent都需新的明确任务/授权。若后续输入hash/diff/调用上限不满足，必须在零调用阶段停止。失败/截断/非法JSON都独立记录，不自动重试。本轮已完成并停止。

## 9. 完整性、凭据与复核入口

[protected_before.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/protected_before.json)与[final_integrity.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/final_integrity.json)核对519项受保护文件和3个完整目录成员清单，全部不变：

- 当前166项已冻结源码/备份文件不变，保留既有预处理修复。
- s24m003历史135个文件、qsv历史170个文件及此前qsv_probe_001整个目录不变。
- 两份前置报告、已有s24m003证据和复用解析helper不变。

没有把Authorization写入磁盘或输出环境秘密。凭据仅通过既有DEEPSEEK_API_KEY进程变量在内存用于授权；新增证据及报告已通过真实秘密字节无泄露检查，不输出秘密值；记录见domain_identity_ablation_001/credential_safety_check.json。

以下命令**仅离线校验，不发送模型请求**：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_ablation_001\ablation.py"
~~~

合同测试命令也仅本地模拟网络：

~~~powershell
python -B "D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m003\domain_identity_ablation_001\test_ablation.py"
~~~

正式执行入口本次已经执行并占用live排他门控，禁止换目录重发。全部输入、判定、门控和报告哈希见[manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/manifest.json)；实际用量汇总见[post_probe_summary.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/domain_identity_ablation_001/post_probe_summary.json)。

**验收：输入边界与两次上限通过；真实A=0、B=3且同指纹；目标语义部分保留、完整表达未通过；官方算法及历史数据未变。本轮停止。**
