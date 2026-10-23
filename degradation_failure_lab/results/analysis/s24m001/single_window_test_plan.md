# Scrapy024 一次受控 Plan 调用计划（尚未执行）

日期：2026-10-23。**当前 execution_authorized=false；本轮模型调用0。以下付费命令只供用户随后批准一次调用后执行。**

目标只回答：在完整目标块进入请求后，**原版Plan prompt+同名模型配置**是否返回与FTP默认规则有关的候选。方法标记 `lab-preprocess-v1 + unchanged official Plan`；不冒充未经修改的官方端到端结果。不改prompt、taxonomy、模型或候选定义；不Expand、不compile、不register、不运行Agent。

## 1. 已冻结的配置与输入

审计目录：`D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m001`。

- `round2/patched_ok/single_window_config.json`：唯一probe ID `s24-single-window-preprocess-v1`；本轮未授权执行。
- `single_window_request.json`：准确HTTP请求体，system与历史一致；user由原版 `_build_unit_payload` 构造，仅换成修复的window/record内容。
- `single_window.txt` 与 `single_window_source_map.json`：窗口18、1552字符、8段唯一原文映射；完整438–449目标块通过门禁。
- window SHA：`50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07`。
- request SHA：`a3265af49b00d88538f90c49f56c71a88aec0ba87e1cf79da7d83d4ff1de81f1`。
- prompt SHA：`295ee9cd6633d30897b2028a7a53a4e9b06a399c40c29b78d99413f515629be6`。

原版固定提交：`94c47ca488d4ba4117d20272e66d49b9877e68cf`。模型`deepseek-flash`，endpoint `https://api.deepseek.com/v1/chat/completions`，temperature=0、stream=false、thinking=disabled、max_tokens=16384、timeout=180秒，全部继承历史传输参数。该名称是**别名**，没有可验证不可变版本；同名不保证服务端权重跨日期不变，必须保存响应model。凭据仅在获批执行时从`DEEPSEEK_API_KEY`读取，不写入证据，不在本轮加载。

文档metadata中的s24m001是输入来源标识，另用新probe ID标记执行。不得覆盖/续跑旧run。执行前再次核验源文、窗口、请求、prompt和164项官方源码哈希；若不一致就不发请求。

## 2. 一次请求约束

`round2/single_window_probe.py` 默认只做离线校验。获批后显式`--execute`才允许进入唯一POST调用点；使用标准库直接传输冻结请求，没有SDK自动重试、redirect跟随、JSON repair或全窗口循环。代理环境不自动继承，连接失败即记录失败，不自动换端点。

执行目录排他创建；写attempt.json（预留一个尝试）后才发送。相同目录第二次运行立即拒绝，即使第一次超时或失败。输出目录与原run、官方源码、冻结bundle分离。每次运行只存在一个传输调用，HTTP错误、空计划、解析失败都停止；不向模型追问失败原因。

这保证**本工具单次执行、同一输出目录至多一次HTTP尝试**；不能阻止人工另选目录重复启动。后续批准仅限本计划的一次，失败后须停止并重新决策。TCP内部重传不等于额外模型API请求，超时是否已在服务端计费不能由客户端单独确定；不要因未知结果自动重发。

`test_single_window_probe.py` 9项fake transport测试通过，socket/subprocess在测试进程中被拒绝。这验证的是调用/记录合同，不证明真实提供方接受请求或模型成功提取。

## 3. 输出schema、准入与规则核查

使用原prompt的`{"skills": [...]}`，允许空数组，最多4个轻量Plan资产。字段包括slot、name、description、asset_type、granularity、objective、domain/task_family/method_family/stage、why_distinct、confidence及可选路由/evidence_span_hint。无服务端response_format/强制JSON Schema。本工具另记录顶层schema合规，不把它伪装为原版所有字段验证。

响应先原样保存`response.raw.json`，随后以官方`json_from_llm_text`解析，再把这个**已保存解析值**交给未修改的`_plan_unit_skills`候选过滤函数；不调用它的真实LLM/repair入口。

分别记录三层判断：

1. **原版候选层**：有没有非空named candidate；原生接受/丢弃数量和parsed原值都保存。非空不等于合格SKILL.md。
2. **目标关联层（独立审计）**：是否明确涉及FEEDS的FTP `overwrite`，默认True是否正确；若只写泛泛“storage”，记“目标未证明”，不人工补规则，不修改原生候选计数。
3. **语义上下文层（独立审计）**：True覆盖/False追加、未指定值时的backend默认、显式False与APPE支持例外是否正确区分；不能把S3/GCS不支持追加泛化到所有FTP。轻量Plan可能省略这些细节，记录“未表达/待Expand核验”；不能将省略冒称完全保真，也不能偷偷升级原版准入门槛。不得为了测试通过要求模型增加schema之外的完整Skill正文。

## 4. 结果分类与失败定位

| 状态/证据 | 如何解释及下一步 |
|---|---|
| 本地hash/目标块门禁失败 | 输入/配置问题，HTTP=0，先修复证据链；不调用模型 |
| HTTP_ERROR/TRANSPORT_ERROR | 提供方/传输失败，保存HTTP码和原错误体或错误类型；不是提取失败；不重试 |
| RESPONSE_ENVELOPE_ERROR | choice/content封装异常，与模型JSON语法分开 |
| JSON_PARSE_FAILURE | 原始文本无法被官方解析器解析；保留原始输出，离线判断格式/解析器覆盖问题，不请求JSON修复 |
| INCOMPLETE_RESPONSE | finish_reason非stop（如length）；保留parsed_state，不能当作完整Plan结论 |
| SCHEMA_MISMATCH | 可解析但顶层/数量不符合prompt；同时保存官方parser实际产物，避免将schema审计冒充原生拒绝 |
| EMPTY_PLAN | 模型明确输出合法空列表。此时已排除已知输入丢失，但**单个观察仍不能区分提示词保守性与模型能力/判断**；没有解释就继续标未知，不猜测因果 |
| CANDIDATE_FILTERED | raw非空而原版Plan无候选；离线定位非dict/无name等原生分支，不与空列表混为一谈 |
| NONEMPTY_PLAN_TARGET_REVIEW_REQUIRED | 有候选，只做上面独立规则审核；即使正确也停在Plan，未证明Expand、canonical或Agent成功 |

要进一步拆分prompt与模型影响，后续必须单独批准、预注册改变因素的对照；本次一次请求不能同时证明两者因果。改变prompt/准入必须另立方法版本，不覆盖官方基线或本诊断。

## 5. 输入规模与成本边界

冻结system+user共13,987 Unicode字符，窗口正文1552字符。按历史18个Plan的`prompt_tokens/(system+user字符数)`最小/最大比例估算，本次输入约**3,860–3,974 tokens**。这是经验代理值，不是提供方分词器结果、置信区间或保证上界。

只有1次HTTP；输出保留原上限16,384 tokens。历史空数组只用5输出tokens，但不能假设未来也如此；即使输出到上限，总量也只能以“约输入估算+16,384”做量级参考。输入/缓存/输出单价与账单未可靠核实，**人民币费用未知，不编造精确费用**。失败重试预算为0；Outline/Expand/compile/register额外模型调用预算均为0。

保留原高输出上限是为了不暗改模型配置；若要降低输出上限，必须先记录为另一传输配置并重新冻结请求，不能静默修改本文件。真实usage、响应model、elapsed、重试数及失败阶段写入result.json；价格未知时cost保持UNKNOWN。

## 6. 复现命令与停止点

**现在可执行的零调用检查：**

```powershell
Set-Location 'D:\AS\AutoSkill-main\degradation_failure_lab'
python -B results/analysis/s24m001/round2/single_window_probe.py --bundle results/analysis/s24m001/round2/patched_ok
```

预期`OFFLINE_READY, model_calls=0`。本轮已执行等价C盘命令并通过。

**后续经用户明确批准一次调用后才执行：** 保持已有安全凭据入口，将密钥加载到进程环境，不粘贴到命令行；下面没有密钥文本。

```powershell
Set-Location 'D:\AS\AutoSkill-main\degradation_failure_lab'
python -B results/analysis/s24m001/round2/single_window_probe.py `
  --bundle results/analysis/s24m001/round2/patched_ok `
  --out results/analysis/s24m001/round2/single_window_live_001 `
  --execute
```

本轮没有运行带`--execute`的命令。执行后无论何种结果都停止；原始请求/响应、attempt和result独立留存。最省钱、最能回答当前问题的下一步就是这**一个已有保真证据的窗口、一次原版Plan**，而不是重跑18/21窗或开始六次Agent校准。
