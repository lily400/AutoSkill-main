# Case004 Git reset：SSL 中断与安全恢复审计

审计日期：2026-10-12。角色：科研代码审计／实验运行可靠性分析。  
研究边界：只处理 Case004 的运行可靠性；不评价“网络失败说明模型语义能力差”，不运行生成，不修改源码／配置／历史产物。

## 1. 执行摘要

本轮能确定的是**为何 SSL EOF 没有被当前 Extract 自动重试**，不能确定**最初为何发生 TLS 连接中断**。

- 第二次 ra960b6759d7c：1 Document、7 Sections、9 Windows；H1–H7 成功；W3 的三次 Expand 和 3 个 Support／Draft 已真正落盘；H8 在 W4 的 **Plan** 失败，exception_type=URLError，约 5.125 秒，retryable=false；没有 Spec 或正式技能，exit_code=2。
- 第一次 rfad98180a468：用户本轮明确确认已经删除。原始目录及请求／响应／event 已不可重新审计。本报告只引用现存旧审计报告与 run_index.jsonl，不能提供两次原始请求的完整字节对比或完整异常堆栈比较，也不恢复／拼接历史数据。
- 官方 Extract 使用独立字符串重试判断，未覆盖 ssl／tls／eof；Compile／Register 使用公共判断，覆盖这些词。同类异常在不同阶段有不同重试待遇，已通过当前源码、其他案例事件和离线模拟核验。
- 官方实际上有自动匹配 unfinished intermediate run、跳过完成 Window 的恢复能力；但 lab 每次创建新 run、要求空 SkillBank，没有可直接用于当前历史 run 的恢复入口。不能说“官方完全没有 checkpoint/resume”，也不能直接执行会改写历史的原位 resume。
- 当前 Python 没有 HTTP_PROXY／HTTPS_PROXY／ALL_PROXY 环境变量，却从 Windows 系统设置得到 http://127.0.0.1:7897 代理，api.deepseek.com 当前不绕过代理；两种只读检查未见该端口监听。它是**当前复测准入风险**，不是历史两次 EOF 的已证实根因。
- 6 个纯离线行为断言通过；6 个现有针对性测试在可写临时目录中为 4 通过／2 断言失败。两个失败分别是并发结果顺序与注册中断传播预期；不改测试，不把失败隐藏，不宣称真实网络已修复。
- 建议现在暂停 Case004 付费重跑，先确认网络入口和离线日志／重试保障。若批准改动，优先最小包装层诊断与受控传输重试；断点恢复优先适配官方已有能力，而不是新造完整恢复系统。

## 2. 证据来源与缺失说明

项目：D:\AS\AutoSkill-main  
LAB：D:\AS\AutoSkill-main\degradation_failure_lab  
UP：D:\AS\AutoSkill-main\AutoSkill-main  
RUN2：D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_reset\clean\ra960b6759d7c  
MID2：D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_reset\clean\ra960b6759d7c\SkillBank\.runtime\intermediate_runs\20261012T192819_1d834a91

下文 LAB／UP／RUN2／MID2 都是这些绝对目录的缩写。Hn 文件为 RUN2\http\三位编号\request.json、response.json、event.json；失败 H8 没有 response.json。

本轮实际读取 invocation.json、execution.json、config.json、input_manifest.json、pipeline.log、model_calls.json、official_call_trace.json、全部 8 请求／event 和 7 成功响应；官方 ingest／extract／compile／register 结果与 status、Window 检查点、文档检查点；官方／包装层调用链及选定测试源码。现存 RUN2 artifact_manifest 的 68 个文件哈希均匹配，164 个官方源码及 10 个包装层快照文件与当前源码匹配。

第一次的资料只有：

- LAB\results\run_index.jsonl 仍保留 rfad98180a468、exit_code=2、登记结束时间 2026-10-11T22:30:39.012770+08:00。登记时间略晚于旧报告中的 execution.ended_at，不应混用。
- LAB\docs\research\CLEAN_MULTI_CASE_GENERATION_AUDIT.md 第 46、59、62、68–85 行。
- LAB\docs\research\CLEAN_MULTI_CASE_RULE_TRACE.md 第 98–120 行。

上述是残存台账／前次分析记录，不是本轮重新读取的第一次原始响应。用户确认删除是本轮可信事实；删除发生前的完整 payload、异常类型／reason、耗时细节和每个原始文件校验无法当前复核，标 UNKNOWN。旧报告中的原路径仅为历史定位，现已不存在。

## 3. 两次运行时间线与差异

### 3.1 第一次：历史记录层时间线，非当前原始日志重放

旧审计记录：2026-10-11 22:30:20.280625 → 22:30:38.998930（UTC+08:00）。

| 顺序 | 旧记录所述操作 | 结果与证据层次 |
|---|---|---|
| H1 | Ingest outline | 成功；7 Sections／9 Windows；旧报告 |
| H2 | W1，标题 25 字符，Plan | 空计划；旧规则报告 108 行 |
| H3 | W2，NAME 58 字符，Plan | 空计划；旧规则报告 109 行 |
| H4 | W3，SYNOPSIS 288 字符，Plan | 3 候选；旧规则报告 110 行 |
| H5 | W3 第一个候选 Expand | 回答已返回，但未形成持久化 Draft |
| H6 | W3 第二个候选 Expand | SSL EOF，retryable=false，无后续恢复；旧主报告 59、62 行 |
| 后续 | W3 尚未完成；W4–W9 未执行 | 0 持久化 Support／Draft；0 Spec／注册 Skill；完整窗口内所有 Expand 结束后才构建 Draft |

历史 W3 ID：2c23c001-8504-5d7b-b535-ab3c493169fc；Document ID：eb088018-f583-5cbe-a0ad-6c06ee86e16c。这些由旧报告保留，不是假定本轮仍有相应 JSON。

### 3.2 第二次：本轮原始记录时间线

invocation.started_at=2026-10-12T19:28:18.879453+08:00；execution.ended_at=2026-10-12T19:28:46.944122+08:00。pipeline.log 用 UTC，需加 8 小时。下表请求时间来自 event.started_at；seconds 是包装层 original _post_json 的用时，不包含前置速率等待，也不是服务端推理耗时。

| HTTP | 开始（UTC+08:00） | Stage / Window / 动作 | 用时秒 | prompt / completion Tokens | 请求 JSON 文件字节 | 结果 |
|---|---|---|---:|---:|---:|---|
| H1 | 19:28:19.338788+08:00 | Ingest outline | 2.641 | 8079 / 90 | 30463 | 6 主标题，之后形成 7 Sections／9 Windows |
| H2 | 19:28:22.059523+08:00 | Extract W1 Plan | 0.813 | 3309 / 5 | 13342 | 完整 JSON，skills=[] |
| H3 | 19:28:22.953095+08:00 | Extract W2 Plan | 1.312 | 3308 / 5 | 13358 | 完整 JSON，skills=[] |
| H4 | 19:28:24.3003+08:00 | Extract W3 Plan | 5.079 | 3416 / 800 | 13606 | 3 候选 |
| H5 | 19:28:29.413416+08:00 | Extract W3 Expand slot 1 | 4.797 | 3584 / 673 | 14311 | 返回对应 skill；W3 全部结束后一起落盘 |
| H6 | 19:28:34.247667+08:00 | Extract W3 Expand slot 2 | 4.156 | 3545 / 757 | 14122 | 返回对应 skill；W3 全部结束后一起落盘 |
| H7 | 19:28:38.456623+08:00 | Extract W3 Expand slot 3 | 3.063 | 3554 / 513 | 14123 | 返回对应 skill；W3 全部结束后一起落盘 |
| H8 | 19:28:41.630707+08:00 | Extract W4 Plan | 5.125 | UNKNOWN / UNKNOWN | 14762 | URLError／SSL EOF；无成功响应 |

保存文件字节数不是线上 HTTP Content-Length：request.json 是包装层格式化记录，不含 Authorization／Cookie 等头。H8 system／user 文本分别 5926／7378 字符，合计 13304；UTF-8 文本分别 5986／7604 字节；excerpt 为 1377 字符。实际完整线上 wire bytes 未记录，不虚构。

H8 的文件哈希：
99F2FF461DE59845E4C00BA8679DFC309A22216A76BC93DB962D87261FBF4D56。

比 H8 更大的 H1（30,463 字节保存体）已成功；H4 成功约 5.079 秒，H8 失败约 5.125 秒。不能据此证明固定正文大小／Token／180 秒客户端超时造成失败。H8 没有 response ID、HTTP 状态码、响应 Token、部分响应体或底层 exception.reason 快照；UNKNOWN 不等于零。

### 3.3 差异表与不能比较的项目

| 项目 | 第一次（残存旧报告） | 第二次（原始记录） | 结论 |
|---|---|---|---|
| 实际记录状态 | 原始目录被用户删除 | 完整目录现存 | 两次证据等级不同 |
| 日期 | 2026-10-11 | 2026-10-12 | 不是同一时间／网络现场 |
| 出错 Stage | Extract | Extract | 同阶段 |
| Window | W3 SYNOPSIS | W4 DESCRIPTION | 不同窗口／处理位置 |
| 操作 | 第二个候选 Expand，H6 | Plan，H8 | 不同逻辑请求；不能说固定同一请求总是失败 |
| 失败前成功 HTTP | 5 | 7 | 第二次走过了此前 Expand 障碍，但请求元数据／候选可能不同 |
| 持久化 Support / Draft | 0 / 0 | 3 / 3 | 返回结果与落盘结果区别已确认 |
| 未完成窗口 | W3–W9 | W4–W9 | 第二次有 3 个 complete Window |
| Spec／正式 Skill | 0 / 0 | 0 / 0 | 不能评价最终语义质量 |
| HTTP 尝试／成功 | 6 / 5 | 8 / 7 | 单独记录，不合并为一次完整 run |
| prompt／completion／总 Token | 21,672 / 1,610 / 23,282 | 28,795 / 2,843 / 31,638 | 第一次来自旧报告；都不是完整费用账单 |
| 生成配置 | 旧报告记录相同共享模型／阶段配置及 git domain | 当前 config 可完整核查 | 记录层一致，第一次原 JSON 逐字段／字节比较 UNKNOWN |
| 输入 SHA-256 | 旧规则报告 104 行 | 当前 input_manifest＋源文件均匹配 | 记录层一致；第一次实际文件已无法再次哈希 |
| 源码版本 | 旧报告保留清单指纹 | 当前清单指纹相同 | 覆盖文件指纹一致；运行 Git commit／清单外文件 UNKNOWN |
| 异常字面 | SSL EOF，retryable=false | URLError 包含同类 SSL EOF，retryable=false | 完整底层堆栈是否相同 UNKNOWN |
| 失败请求大小／耗时／Prompt SHA | 原始文件缺失，UNKNOWN | H8 有保存体、message 字符、5.125 秒 | 不能补写第一次数值来完成比较 |
| 自动重试次数 | 旧记录未发生 | 实际 H8 后无 H9 | “配置有 retries”不证明覆盖 EOF |

两次记录的源输入 SHA-256：
372b401b153142441c139098f9de714351ab4f5c13efbac69ca7cd80989092cd，
来源固定 Git commit a52a24e03c8c711f1d5e252fba78f9276908129b；
当前源／输入为 19,125 字节。Document.raw_text 等于输入 strip 后正文。

当前使用 D:\anoconda1\envs\autoskill\python.exe，Python 3.10.21。模型 deepseek-flash，temperature=0.0，thinking disabled，stream=false；endpoint https://api.deepseek.com/v1/chat/completions，timeout_s=180，max_tokens=16384，max_input_chars=100000，hashing 256。Extract recommended／每单元最多 4 候选／workers=1／extract_retries=1／backoff=1.0／10 requests per 60s。每 run 32 HTTP、200,000 观测 Token 上限；第二次 8 次／31,638 Token，未触发任一预算限制。

官方 164 文件 before／after 清单 SHA-256：
CD94ECC03C7DE739E64621DC7B5AD6DB29A0CD13B56B4F50FB602E17E8614918。
包装层 10 文件清单 SHA-256：
22BC3CA15280E9F22D103D4ECF6C76E5EBBE9AE9E4C1AA1C8B9EF0583D66BEAB。
当前源码与第二次快照没有差异；这两清单也与旧报告的记录一致。模型 alias 不等于固定权重版本，服务端版本 UNKNOWN。

## 4. SSL EOF 的实际调用链与证据精度

### 4.1 第二次记录下来的应用调用链

RUN2\http\008\event.json 的 stack 是 lab 在进入请求前收集的**应用调用栈**，不是包含 Python ssl／socket 的实际 exception traceback：

extract.py:438 extract_from_doc  
→ pipeline.py:588 build  
→ pipeline.py:1156 _resume_or_extract  
→ extractor.py:1572 extract_skills  
→ extractor.py:1447 extract  
→ extractor.py:1320 _extract_document_with_retries  
→ extractor.py:1295 _extract_document  
→ extractor.py:1146 _extract_from_windows  
→ extractor.py:972 _extract_unit_skills  
→ extractor.py:867 _plan_unit_skills  
→ extractor.py:830 _complete_extract_json  
→ core/llm_utils.py:28 llm_complete_json  
→ core/rate_limit.py:108 RateLimitedLLM.complete  
→ autoskill/llm/openai.py:139 OpenAIChatLLM.complete  
→ lab adapter.py:52–86 observed  
→ autoskill/llm/openai.py:251–261 _post_json  
→ urllib.request.urlopen（官方第 256 行）。

所有官方路径均位于 UP。实际网络客户端是 Python 标准库 urllib＋http.client＋ssl，不是 requests 或 httpx。provider_adapter.py 只添加 thinking 参数，没有另建网络客户端、代理策略或重试机制。

### 4.2 URLError 与底层 TLS 错误

官方 _post_json 只捕获 urllib.error.HTTPError，并包装 RuntimeError（openai.py 258–261）；它不捕获 URLError，因此本次 URLError 原样进入 lab observed，lab 用 raise 继续传播，没有把它转换成另一通用异常。

当前解释器标准库：
D:\anoconda1\envs\autoskill\lib\urllib\request.py 1346–1355 在 h.request（包括隐式建联／代理 CONNECT／TLS 等）的 OSError 路径中 raise URLError(err)，随后关闭连接并继续抛出。实际错误对象 .reason 可以保留 SSLEOFError；离线注入验证官方 _post_json 保留同一个 URLError 及 reason 类型。

但历史 event 只保存顶层类型和 str(e)，没有 reason 类型、异常 cause 链、真实失败 traceback／握手状态。故只能说：

- 已确认：Python HTTP/TLS 调用失败，客户端没有得到完整响应；顶层是 URLError，消息含 SSL UNEXPECTED_EOF_WHILE_READING。
- 与 urllib 将 TLS OSError 包成 URLError 的路径相符；具体是握手、发送、代理链的哪个边界，不能由当前 stack 唯一定位。
- 服务商、代理上游、网络设备、本地代理、TLS 兼容性等哪个参与者断开，UNKNOWN。
- “WHILE_READING”不能解释成模型读 Git 文档失败或模型语义能力不足。
- 不能证明服务端完全没收到／没处理请求，也不能认定已有重复计费。

### 4.3 为什么没有 exception.json 及为什么 exit_code=2

Extract.extract 在 extractor.py 1392–1456 将异常转换成 result.errors；pipeline.py 1163–1181 写失败 Window，1219–1252 写失败文档、后续未完成 ID。框架最终返回 failed result，而不是向 lab 顶层抛异常。

lab adapter.py 106–110 只有顶层异常才写 exception.json；107 行把未完成／有 errors 的返回值判 exit_code=2。因此本次 exception.json 不存在是该控制流的结果，不是“完全没有异常记录”。失败信息保存在 event、model_calls、pipeline.log 和官方错误产物中。continue_on_error=False 也没有阻止这条内部转 errors 的路径。

current_stage=register_completed 只说明经过后续空／skipped 阶段记录，不表示注册成功。真正 status=failed，completed_stages=["ingest"]，unresolved_doc_ids 非空；本次没有任何 Compile／Register HTTP。

## 5. 网络重试机制：核心原因不是 retries 数字太小

| 层次 | 源码位置（UP 或 LAB） | 实际功能 | 本次 EOF |
|---|---|---|---|
| 官方 urllib _post_json | UP\autoskill\llm\openai.py 251–261 | 一次 POST；HTTPError 包装；无传输重试循环 | URLError 原样抛出 |
| lab HTTP observer | LAB\src\degradation_lab\adapter.py 52–86 | 每次真实尝试计数／留请求响应事件；无自动重试 | 记录第 8 次失败并 re-raise |
| RateLimitedLLM | UP\AutoSkill4Doc\core\rate_limit.py 104–113、219–246 | 限速与错误 cooldown；不是重新调用请求的循环 | SSL 文本会设置 cooldown，但没有下一次 retry 来恢复 |
| Extract 单操作 | UP\AutoSkill4Doc\stages\extractor.py 137–168、828–854 | Plan／Expand 各自按 extract_retries 重试被识别的瞬时异常 | 字符串表没有 ssl/tls/eof，立即抛出 |
| Extract 外层 | 同文件 1318–1341、1392–1456 | 被判可重试时重做本次 document extraction；窗口调用路径实际上针对当前单个 Window | 同一分类函数仍返回 false |
| JSON repair | UP\AutoSkill4Doc\core\llm_utils.py 27–39 | complete 返回后解析失败可另调一次 JSON 修复 | 网络异常发生在进入解析 try 之前；不是 repair 适用情形 |
| Compile／Register | compiler.py 348；versioning.py 1371；core/llm_utils.py 41–77 | 公共 llm_complete_json_with_retries，默认最多 2 次额外重试 | 公共文本表含 ssl/tls/eof，识别为瞬时错误 |

Extract retries 并非只重试内容生成失败；它可重试 429、超时、connection reset 等网络／服务异常。但它的分类和公共 LLM retry 分类不同。只把 extract_retries 从 1 改大，EOF 依然判 false，不会解决这个缺口。本轮没有改配置。

本例配置=1，在单操作层对已识别异常最多 2 次 complete；加外层窗口／document retry，最坏同一个失败操作可被调用到 4 次，并且窗口先前成功的 Plan／Expand 可能重新付费。多 worker 的额外 fallback 不适用于当前 workers=1，不能混算。本轮已离线验证“单操作 EOF 仅 1 次；Timeout 最多 2 次”；嵌套整体上限的具体预算应在下一阶段再用故障注入测试，不宣称已测试所有组合。

### 5.1 与其他案例成功重试的当前证据

只读核对 Case002 H8→H9（Compile）、H10→H11（Register），Case003 H8→H9（Register）的 event.json：

- 失败均为相同字面 URLError／SSL EOF。
- 其 stack 包含 llm_complete_json_with_retries。
- Case004 H8 的 stack 不包含该公共 retry helper，而走 _complete_extract_json。
- 首次失败后对应下一次重试成功；不是 lab observer 自动重试，也不是“Git 模型能力比 sort 差”。

准确路径示例：
LAB\runs\case002_qsv_sort\clean\rd9ced750fa54\http\008\event.json，
LAB\runs\case002_qsv_sort\clean\rd9ced750fa54\http\009\event.json。
Case003 对应 rab9a070dfa59\http\008、009。没有为这些案例开展新实验。

### 5.2 异常包装并未被证实丢掉原始类型

urllib.URLError.reason 可保留底层对象；官方 _post_json／observer 没有转换此次错误。主要缺口是 Extract **只按字符串做不同的判定**，不是已经证明 reason 丢失。日志只保留 exception_type／error，确实使事后诊断丢失细节，应将“运行时对象信息”和“保存的诊断字段”区分。

额外边界：标准 RemoteDisconnected 的消息“Remote end closed connection without response”在两套字符串表里都可能不匹配；而包含字面“remote disconnected”的人工消息却能匹配。带 [SSL: CERTIFICATE_VERIFY_FAILED] 的证书验证异常可能被公共宽泛 ssl 匹配标可重试。未来受控重试必须显式排除证书失败、认证失败、错误输入；不能简单把所有 SSLError 都无限重试，更不能关闭 SSL 验证。

## 6. 代理／TLS 环境检查：当前事实与历史 UNKNOWN

本轮在同一 autoskill Python 可执行文件中只读取配置、构建默认 SSL context；未建立到 DeepSeek 的真实连接，未发送 API 请求。未输出 API Key、Authorization、Cookie、代理 userinfo／password 或环境变量原始敏感值。

| 检查 | 当前读到的状态 | 能说明／不能说明 |
|---|---|---|
| HTTP_PROXY／HTTPS_PROXY／ALL_PROXY 及小写形式 | 全部不存在 | 不等于 urllib 不走代理 |
| NO_PROXY／no_proxy | 不存在 | 当前没有环境显式 bypass 配置 |
| urllib.request.getproxies() | http／https／ftp 指向 http://127.0.0.1:7897；未带凭证 | Windows getproxies_environment() 为空时回退 getproxies_registry() |
| proxy_bypass(api.deepseek.com) | false | 在当前默认 opener 设置下该主机走代理 |
| 7897 本地监听 | Get-NetTCPConnection 和 netstat -ano -p tcp 本轮均未发现 | 当前 proxy endpoint 需由用户终端确认；查询受当前进程／权限可见性限制，不证明历史 19:28 时也没监听 |
| SSL_CERT_FILE | 存在（只记录是否存在） | 不能证明历史 CA／证书配置相同或正确 |
| 默认 context | check_hostname=true，CERT_REQUIRED，最低 TLSv1.2 | 未关闭校验 |
| 当前 OpenSSL | 3.6.4（2026-08-25） | 运行时 OpenSSL／代理状态没有在两次历史日志完整冻结 |

标准库依据：D:\anoconda1\envs\autoskill\lib\urllib\request.py 791–813 默认 ProxyHandler 使用 getproxies；2738–2745 的 Windows 分支从环境或注册表获取。客户端没有显式 ProxyHandler({})、自定义 SSL context 或 requests/httpx 代理继承设置。

urllib 标准 do_open 在 1333 行强制 Connection: close，单请求连接不是持久连接池；因此没有代码证据支持“复用了过期 keep-alive 连接”这个根因。这里共享的是 opener／handler，不是 HTTP keep-alive socket。更多重复调用仍可能重复建 TLS 连接；是否这增加现场中断概率需要实测，不能直接当因果结论。

H8 的 5.125 秒失败远短于配置 180 秒，不能据此诊断为官方请求超时。代理可能有自己的超时／路由，但其运行时日志、CONNECT 状态、服务端状态、链路抓包均没有，不确认根因。当前网络环境是**本次 Codex 进程快照**，未必等于用户当时终端环境。

## 7. 第二次三个 Draft 的持久化与恢复前提

### 7.1 实际检查点

Document ID：3b5e3356-6161-5ef7-8716-85033771e833。

| Window | ID | 状态 | Support / Draft | 实际情况 |
|---|---|---|---|---|
| W1 | 7d22a9bc-98a7-5407-b37c-053c5d4fca69 | complete=true、failed=false | 0 / 0 | 空计划是已完成窗口，不能重复误判未完成 |
| W2 | a125002a-0a77-5fb6-b71c-f6f4d41eb6c8 | complete=true、failed=false | 0 / 0 | 同上 |
| W3 | 92aa55e1-30be-591a-9f02-b59a1a9349e1 | complete=true、failed=false | 3 / 3 | H4 Plan、H5–7 Expand 均结束并落盘 |
| W4 | ce9321d7-eaca-58ba-994f-a79ec0d68ba4 | complete=false、failed=true | 0 / 0 | H8 Plan 失败，不能记 empty plan |
| W5–W9 | 97d82050-26dd-50ad-a4f3-bb17650e756c；9e6efc5e-6a5e-58db-9a21-f17b6be10971；ba3983b5-e2ae-5296-834f-01f5681e180b；ab532d02-ea14-59e8-89b2-fe73d36e6b3f；3ed3385d-aa8d-5281-9282-8ffcfd9f69bc | 没有成功检查点，列在 unresolved | 0 / 0 | 尚未执行，不是模型拒绝提取 |

检查点文件模板：
MID2\extract\windows\3b5e3356-6161-5ef7-8716-85033771e833\<window_id>.json。
W3 三个 Draft 在该窗口文件与 MID2\extract\result.json 中均有实际记录，不是仅终端打印名称。

| 名称 | Draft ID | Support ID | 所属 Window / HTTP |
|---|---|---|---|
| git reset 模式选择与执行 | d526e71d-906a-5091-abd6-f23dbfaf0027 | 7259312f-1007-5be3-9c05-c3c872a38ab6 | W3／H5 |
| 按路径重置暂存区 | fc5c1fae-2e22-5361-81bc-b69a7e2c427f | 4758fbcf-a312-574b-8ff1-134cc671bdbf | W3／H6 |
| 交互式补丁重置 | 6407b134-548d-5f6e-8160-ef452536ccdf | e627a1af-c721-5a1d-b1e5-434502309e89 | W3／H7 |

每条 Support.excerpt 都等于 W3 的 288 字符 SYNOPSIS；ID／doc_id／window_id／source_file 链接一致，support_ids 可解析。这里的“完整”指记录结构与引用完整，不表示 SYNOPSIS 足以句子级支持所有模式细节。三个 Draft 也不等于三个已经通过语义审查的技能。

MID2\extract\documents\<doc_id>.json：
processed_window_ids 是 W1/W2/W3，unresolved 是 W4–W9，failed=true、complete=false。Spec=0、注册=0。状态文件中 progress_counts 有旧／不同作用域的零值，不能覆盖阶段产物实际 3 条计数；Compile 的空 Support 也不能覆盖 Extract 3 条。现有 lab artifacts.py 52 行的空 Compile 优先读取问题仍需后续独立处理，本轮不改。

### 7.2 官方已有窗口级 resume，但不是任意 HTTP 缓存复用

源码：

- UP\AutoSkill4Doc\pipeline.py 501–526：计算 resume_key，在同一个 store_root 寻找 unfinished run，构造 resume_existing writer。
- UP\AutoSkill4Doc\store\intermediate.py 77–105：匹配 resume_key，排除 completed，选择最新未完成状态。
- pipeline.py 531–547：已完成 Ingest 则加载，不再调用 outline。
- intermediate.py 613–623：只把 complete 且非 failed 的窗口算已处理。
- pipeline.py 1009–1041：跳过完成／非 unresolved 窗口，记录 reused_nodes；1153–1187：只处理未完成窗口并写新检查点。
- extractor.py 972–994、1146–1183：一个窗口全体 Expand 完成后才产生 Support／Draft；没有每个 HTTP／每个 Expand 的原生独立 checkpoint。

本轮只调用只读 find_intermediate_run_by_resume_key：确实找到 failed 的 20261012T192819_1d834a91，key 为
f50b76dfbed9420fb3ccbb16937e467ded5c373ca632f46fb52c91e11adbc6bb。
没有构造历史 store 的 resume writer：其 __init__（intermediate.py 140–150）会马上将 status 改 running 并写回，违反本轮历史保护。

因此，满足身份约束时，官方技术上可跳过 Ingest 和 W1–W3，复用三条 Draft，只补 W4–W9。但当前 lab.py run 不会这样做：runner.py prepare 生成新 UUID、新输入绝对路径与独立 SkillBank；adapter.py 14 行拒绝非空 SkillBank；cli.py 没有 resume 命令。重复普通 run 是全新付费生成，不是继续本次。

### 7.3 Compile／Register 与失败快照

当前 MID2\compile\documents\<doc_id>.json 和 register\documents\<doc_id>.json 均 skipped=true；aggregate 空结果文件存在不表示实际模型调用成功。

pipeline.py 1341–1342、1369–1377 对 failed 或不 complete 的文档 Extract 跳过编译。本例只有一份文档，因此完整正式生成需要先完成该文档的 Extract；不能直接将三个 Draft 冒充全篇完整结果。框架的 stage-only compile_skills 可单独接受 Draft（406–424 行），但那是另一种部分产物实验，仍要模型调用且不能称完整原版 baseline；本轮未执行。

resume 时 pipeline.py 1319–1327、1463–1471 排除 skipped 的 Compile／Register 文档快照，理论上不会把本次空结果当成功缓存。这一具体历史 run 的完整恢复尚未执行，不能把一般代码能力等同于实测成功。

### 7.4 身份核验不足与安全复用要求

现有 resume_key 不等于完整科研指纹：

- pipeline.py 736–760 文件签名用绝对路径、size、mtime_ns，不用实际内容 SHA-256。
- 501–513 只显式纳入部分模型／提取字段；metadata 含 lab_run_id、input_manifest 和路径，迁移新 run 会改变 key。
- 没有把完整源码指纹、全部阶段配置、endpoint、thinking、温度、Prompt／taxonomy 文件指纹和已有响应哈希全部作为强制匹配项。
- intermediate.py 1375–1412 是直接写 JSON，不能假定其 checkpoint 天然具有崩溃时的原子性；本例可读且 68 文件哈希匹配，但任意损坏恢复要拒绝而非静默补全。

若批准设计新的恢复包装层，至少核验输入 SHA-256／原始来源 commit、全部配置、官方／包装层文件清单、原始 Document／Section／Window 正文及 ID、Prompt／taxonomy／完整规范化请求体 SHA、模型请求与返回标签、全部复用响应与产物哈希、Support／Draft 引用、成功 complete 状态、未解决节点、累计调用／Token 预算。精确权重版本仍 UNKNOWN，要披露。

不能通过修改历史 metadata／resume_key、移动 JSON、重编号 IDs 或拼接另一个 run 来强行匹配。应在**新派生执行记录**中保存 parent_run_id、复用文件哈希、父逻辑身份和新 execution ID；历史 store 只读，所有后续写入隔离副本。是否采用完整 store 克隆／安全路径迁移／冻结父输入路径，要先在无 API 测试中验证，否则拒绝恢复。它是“官方原生 checkpoint＋新增隔离包装策略”，不是目前 lab 天然支持的完整功能，也不是新独立重复样本。

## 8. 四种补救方案比较

| 方案 | 可行性／现成实现 | 拟涉及代码 | 是否改变生成语义／是否原版基线 | 重复付费风险 | 可复现性／复杂度 | 条件与停止规则 |
|---|---|---|---|---|---|---|
| A：网络核查后全新完整 run | 运行入口现成；网络稳定未验证 | 生成代码无需改；网络检查只读 | 官方模型／Prompt／窗口／编译逻辑保持；可作为新原版 Clean 运行 | 再做 outline、前两空 Plan、W3 Plan/Expand；参考本次 7 成功调用，但新响应／候选不保证相同 | 最低开发量；全新 run，历史不覆写；网络样本与模型时间不同 | 代理／TLS 准入、预算计划先批准；最多一次批准的复测，任一同类故障停止，不自动连续重跑 |
| B：包装层受控网络重试＋诊断 | 当前无此 transport retry；已有 observer 可复用 | LAB\src\degradation_lab\adapter.py＋tests/test_framework.py；若新增配置字段再明确 runner／schema，未经批准不动 | 不改官方算法／Prompt／结果；但重试选择／预算策略不同，标“原版逻辑＋受控传输重试”，不能无标记混作原有执行策略 | EOF 是非幂等 POST 的不确定交付；重复提交可能重复收费；官方外层重试还可能叠加 | 低至中；需区分 logical_call_id／attempt_id，按真实尝试计数与统一上限 | 类型化分类且排除证书／认证失败；每逻辑调用先建议最多 1 次额外重试；累计预算／连续失败／身份异常即停 |
| C：隔离检查点恢复 | 官方窗口 resume 已有；lab 安全入口未有；本例 3 Draft 可作为可核验父产物 | 原则上复用官方 pipeline/intermediate；仅拟改 lab runner/adapter 与派生运行记录／测试，不新造模型恢复算法 | 生成逻辑不改；复用旧随机结果改变抽样与成本，必须独立标记 resumed/derived；不是新的独立 baseline 重复 | 可避开 7 个已成功 HTTP 的重做；W4 失败请求交付未知；未完成窗／Compile／Register仍付费；收益不保证高于开发成本 | 中等以上；身份、路径、预算、历史只读与恢复失败均需测试；当前不能直接用 | 原生恢复、部分失败状态测试和指纹全通过；任何 key／hash／ID 不符即拒绝，不篡改 key；不原位写历史 |
| D：暂停 Case004 付费，已有三完成案例继续分析 | 立即可行，零新增调用；本轮推荐当前状态 | 无 | 不是 Case004 成功 baseline；失败／缺失单列，不剔除来美化质量 | 无新增费用；已有费用金额 UNKNOWN | 最低风险；仍有领域／结构缺失和样本量局限 | 等网络准入、离线测试及预算获批；不借机重跑 Case005或新增案例 |

方案 B 的最小设计不是在 original 调用内部悄悄多试几次：必须让每次真实 POST 都进入 observer 的编号／预算／request/event 记录。保持原 payload、SSL 校验和完整返回体，不做内容修复替代真实结果。

建议记录 logical_call_id=阶段＋doc/window＋candidate slot＋规范化完整 payload hash；attempt_id／retry_of／attempt_index／错误 reason 类型／异常链／计费状态 UNKNOWN。单一逻辑上限要覆盖包装层和官方外层的再次调用，避免 2×3 或 2×2 叠加；请求修复是另一个 payload，单独标记。当前日志能数真实 HTTP 和按 stack／相同请求比对部分 retry，但没有原生稳定 logical_call_id，不能保证自动识别所有重试层级。

## 9. API 调用规模、预算与停止成本

真实费用都 UNKNOWN。只有成功响应的 usage 被加总；失败无 usage 不等于免费，cache_hit_tokens 不等于未收费。本例观察到 31,638 Tokens；已有第一次的 23,282 仅旧报告观测值，不是完整账单或可恢复原始请求。

恢复策略若正确跳过 Ingest＋W1–W3，可避免重新请求本次 7 个成功响应；不是“节省 7 次调用等额费用”或“复用一定更便宜”。

调用规模需先按符号量规划，而非虚构精确调用数：

- A 新完整 run：1 次 outline＋9 次 Window Plan＋N 次 Expand＋G 次 Compile＋S 次 Register＋H 次 hierarchy＋R 次 retry/repair。N/G/S/H 未生成前 UNKNOWN；每 Window 最多 4 候选不是总调用上限。
- C 从当前检查点继续：6 次未完成 Window Plan＋N_remaining 次 Expand＋G/S/H＋R；现有 W3 三 Draft 必须纳入后续编译。仅 6 个窗口在极端各 4 候选时就是 30 次新 Extract 请求，尚不含 Compile／Register；不能保证 32 次原 run 总上限足够。
- 当前已 8 次尝试。如设派生链累计仍为 32，则只有 24 次余量；如单独批准续段预算，必须同时记录历史／新增／整链费用，不能悄悄重置计数或更改本轮配置。
- 现代码 _audit_document_extract 在 pipeline.py 857 起有定义，但当前模块未见调用位置，不将这个未观察到执行的函数固定算作额外付费步骤。下一轮仍应据实际调用日志核验。
- 现有 max_http_calls=32／max_observed_total_tokens=200000 原样保留。任何增预算、续段预算、模型调用与策略变更都先由用户批准；没有足够完成预算时应预测为可能再次预算停止，而不是承诺“一次必跑通”。

同一 POST 服务端可能已经处理、客户端未收到响应；当前没有 idempotency key 支持证据／服务端查询记录。不要擅自添加“幂等头即可免重复收费”的承诺，也不要用一次重试成功断定前一次未收费。

## 10. 离线验证与回归设计

### 10.1 已执行：不访问真实网络

使用 autoskill Python、-B，真实网络入口由 urllib.request.urlopen／socket.create_connection 的 OFFLINE_NETWORK_GUARD 阻断；传输测试用嵌套 fake 替换，provider 为纯 mock／内存对象，dummy key 不是环境中的真实 Key。没有调用 DeepSeek，没有新运行目录，没有改任何源码或阶段数据。

| 注入／检查 | Extract 判定 | 公共判定／实际结果 | 解释 |
|---|---|---|---|
| SSLEOFError，含真实 EOF 字面 | false | true | 重试判定差异复现 |
| URLError(reason=SSLEOFError) | false | true | 包装没有让公共判定失效 |
| TimeoutError / URLError(timeout) | true | true | 明确 timeout 被覆盖 |
| RemoteDisconnected，标准“Remote end closed connection without response” | false | false | 类型未直接参与判断，字符串表缺口 |
| 字面 remote disconnected | true | true | 同类含义依赖不同报错文本 |
| ConnectionResetError | true | true | 已覆盖 reset |
| certificate verify failed（无 SSL 前缀） | false | false | 人工消息可不触发公共判断 |
| 带 [SSL: CERTIFICATE_VERIFY_FAILED] 的 URLError | false | true | 公共宽泛 SSL 匹配可能误把证书问题当瞬时异常；不能照搬为安全 retry 白名单 |
| JSON parse ValueError | false | false | 不当作传输 retry；repair 是另一机制 |

6 个行为断言全部通过：

1. Extract extract_retries=1，持续 EOF 只有 1 次 complete，抛 URLError。
2. 单操作持续 timeout 2 次 complete 后停止。
3. 单操作一次 timeout 后恢复：恰好 2 次 complete。
4. 公共 helper max_retries=2，持续 EOF 恰好 3 次 complete，autoskill_retryable=true、retry_attempts=2。
5. 官方 _post_json 原样抛同一注入 URLError，reason 仍为 SSLEOFError。
6. fake 服务端先记处理成功再断响应：客户端失败但 fake_server_completed=1；证明这种交付状态在逻辑上可能，未证明真实 H8 已处理或重复收费。

第 6 项不是 Mock 证明真实网络已解决，也不对应一张真实费用单。

### 10.2 已执行：六个官方现有测试，不隐藏失败

源码统一为 UP\tests\test_document_pipeline.py，类 DocumentPipelineTest。

| 测试 | 源码起始行 | 本轮可写临时目录结果 |
|---|---:|---|
| test_shared_llm_rate_limiter_auto_cools_down_after_retryable_error | 437 | PASS |
| test_parallel_document_extraction_retries_transient_rate_limit_errors | 954 | FAIL：期望 A/B 顺序，实际 B/A；两 Draft 都产生 |
| test_build_records_failed_document_without_aborting_batch | 1272 | PASS |
| test_resume_does_not_skip_failed_document_snapshots | 1346 | PASS |
| test_build_resumes_failed_run_without_reextracting | 1775 | PASS：一般编译中断恢复未重复提取 |
| test_build_resumes_streamed_register_without_recompiling_processed_documents | 1803 | FAIL：assertRaises(RuntimeError) 未发生；当前 pipeline 捕获阶段异常的行为与测试预期不一致，是否因阶段异常被捕获或调用次数改变仍需另案确认，不能当本例 SSL 根因 |

首次在默认沙箱临时路径运行：2 PASS／4 PermissionError，主要是临时目录 vectors／.runtime 写入及清理受限，不解释成框架断言失败。仅在测试进程把 tempfile.tempdir 指到当前可写 workspace 后重试：4 PASS／2 assertion FAIL／0 ERROR。未改系统 TMP／TEMP、代理、代码或生成配置。失败作为恢复准入未满足的证据保留，不为本任务修 unrelated tests。

本轮对实际历史产物的只读核验：8 事件含 1 次失败；末次失败仍消耗第 8 次 HTTP 配额；status=failed／exit_code=2；原始 artifact 68 文件哈希匹配；Extract 3 Support／3 Draft 与 Compile 0／0 分层计数。

### 10.3 未实现、下一轮需要批准的最小测试

| 测试项 | 最小设计与通过条件 |
|---|---|
| lab observer 失败尝试计数 | 使用 TemporaryDirectory 的测试 fixture，不指向 RUN2；fake urllib POST 失败／成功序列；每次独立 event 和编号，失败也计数，预算达到时无下一次真实 POST |
| B 总重试上限 | 包装层＋官方 helper＋整窗 retry 故障注入；同逻辑调用所有层合计不超批准上限，payload SHA 不变；证书／401／403／400不重试 |
| 完成标记可靠 | 注入 failure 后 lab 退出非零、status 非 completed、unresolved 非空，不能用 current_stage 注册完成字符串当成功 |
| 原生窗口恢复 | 临时 clone 或人工 fixture：W1/W2 空计划成功，W3 3 Draft，W4 failed；再次 build 只运行 W4–W9，不重做 H1–H7，三个旧 Draft ID／hash 不变 |
| 无身份匹配时拒绝 | 改源 hash、配置／Prompt／taxonomy／model／Window text 或响应 hash 中任一项，拒绝复用，不静默强改 resume_key |
| skipped 阶段重做 | Extract 完成后旧 skipped Compile／Register 不被误算为成功完成，能够真正产生新 Spec／注册结果 |
| 不覆盖历史 | 给父 run 只读访问，所有写在新隔离根；父 68 文件／配置／台账哈希不变；发生非法写即测试失败 |
| 模型已处理但响应丢失 | fake 服务端计数独立于客户端成功；重试会增加处理计数，计费 UNKNOWN 标记完整；无假幂等保证 |
| 检查点损坏／崩溃 | 缺 JSON、截断写、hash 不符不能当 complete；不将已有 valid Draft 自动清空；拒绝或等待人工，不拼接新模型结果 |

这些设计没有新增测试文件或恢复功能。本轮已有测试不足以宣布安全隔离恢复入口 ready。

## 11. 推荐下一步、准入、停止与 UNKNOWN

### 11.1 最低风险顺序

当前执行 D：暂停新的 Case004 付费生成，保留 ra960b6759d7c，勿再删除它。不是停止研究，也不是用三完成案例证明 Git 类文档成功。

下一轮建议先批准**无 API 的 B 诊断／受控传输重试回归范围**：明确 attempt 与 logical_call、reason／cause 链、保密处理和统一上限；保留原版对照，不改官方源码。并由用户确认系统代理当前是否可用；如需真实 TCP／TLS 检查，另外明确允许范围，只检查连接，不调用生成端点、不改证书验证。

网络准入满足后再选：

- 更重视原版独立 baseline、接受重复费用：A 一次新完整 run；
- 更重视保留当前 3 Draft、减少重复请求：C 先通过隔离／指纹／失败状态测试，再做明确标记的派生续跑。
- 不能确定网络或总预算足够：继续 D，不连续盲目重跑。

不建议为了 3 个 Draft 立即建设一个大恢复系统；原生能力存在，先用最小适配验证收益／风险，开发成本与节省费用均 UNKNOWN。

### 11.2 付费复测准入

全部满足才能请求一次生成批准：

1. 明确当前 proxy 来源／监听／可用性，真实连接验证如获授权需保持 TLS 校验；现有非监听快照不满足此项。
2. EOF、超时、交付不明、证书错误的离线分类和全层 attempt 上限测试通过；两个现有失败的适用性已解释或恢复路线被验证。
3. A/B/C 标签、父 run（若有）、输入／源码／完整配置／Prompt 等身份核验冻结；不强改历史 key。
4. 模型规模／阶段调用范围／HTTP 与 Token 预算／重试预算明确；真实金额 UNKNOWN 由用户知情接受；当前 32 上限不能被默认为足够。
5. 新输出位置不存在、父历史只读、Token/HTTP 包含失败尝试、费用不明状态有标记。
6. 用户明确批准修改范围及实际 API 调用；本报告不构成执行授权。

### 11.3 停止规则

- 当前任何历史产物 hash／ID 不符，立刻停止复用；不重造。
- 同一逻辑调用达到批准的 attempt cap／任一累计预算触顶，停止付费请求并保留 failed/partial；不扩大预算续试。
- 证书校验、认证、请求格式错误直接停止检查；不关闭验证。
- 一次批准 A 若再出现同类未恢复故障，不自动第三／第四次重跑。
- C 不允许原位改旧 run；隔离恢复测试不通过就不续跑。
- 运行 completed 只定义阶段完成与产物存在，不冒充 Skill 语义正确；既有 Register 截断等质量风险仍须独立审计，本轮不修。
- 报告提交后停止，等待用户选择。

### 11.4 UNKNOWN 清单

TLS 中断的网络责任点、历史代理状态／监听／CA、真实 ssl/socket 失败 traceback、服务端是否已处理 H8、失败收费、固定模型权重版本、第一次已删除请求的体积／耗时／完整栈、第一次配置文件逐字段同一性、实际后续 Draft／Spec／调用数及32预算是否够、当前历史 run 的完整安全 resume 成功率。

本轮已明确的“未恢复原因”是 Extract 分类差异＋当前 lab fresh-run 约束，不等于已定位导致 TLS EOF 的网络根因。

## 12. 五个问题的通俗回答（含依据）

**一：为什么连续两次出现 SSL EOF，能确定根因吗？**  
这表示客户端的加密连接被异常中断，不表示 Git 文档让模型“读不懂”。两次发生在不同窗口／请求；第一次原始记录已删，第二次又没有底层 traceback／代理现场，不能确定是哪一段网络导致。当前系统代理没有监听是新复测风险，不是历史根因证明。依据：第 3–4、6 节；RUN2\http\008\event.json。

**二：为什么其他案例能重试，Git reset 没有？**  
不是工具名触发区别，而是出错阶段走了不同的重试判断。Compile/Register 认 SSL/EOF 为可重试，Extract 的列表不认，立即失败；仅加大 retries 无效。依据：UP\AutoSkill4Doc\stages\extractor.py 137–168、828–854；core/rate_limit.py 219–246；第 5、10 节。

**三：三个 Draft 能直接复用吗？**  
文件确实保存了，官方能在匹配的同一 store 中跳过已完成窗口；但当前 lab 没有安全续跑入口。不能直接贴到新 run、注册成全篇完成结果，或原位恢复改写旧 run。获批后可设计校验过的隔离派生恢复；尚未实测完整跑通。依据：第 7 节；MID2\extract\windows\...\92aa55e1-30be-591a-9f02-b59a1a9349e1.json；pipeline.py 1009–1041。

**四：怎样尽量不浪费 API 费用而完整跑通？**  
先不花钱做网络准入和离线测试；再选择一次完整重跑，或通过严格验证的断点恢复以避免重做现有 7 个成功请求。限制每逻辑请求及整链的重试／预算。重试 POST 可能重复计费，32 次预算未必够完成后续，金额 UNKNOWN；不能承诺“续跑一定更便宜／一定成功”。依据：第 8–10 节；lab adapter.py 53–85。

**五：现在最应该做什么？**  
保留当前 run，暂停付费，确认当前系统代理入口；若你批准下一轮开发，仅做包装层无 API 的受控重试／诊断回归，待测试、网络、预算都过关再申请一次生成。不要立即重新 run，也不要删三个 Draft。依据：第 11 节；adapter.py 14、runner.py prepare 的 fresh-run 约束。

## 13. 交付与操作边界

本轮代码审计采用最小改动原则：只读取与本任务相关的源码、记录和非敏感配置，使用现成测试和内存故障注入；没有为“恢复”扩建系统，没有修改官方代码、lab 代码、任何生成配置／预算／代理／证书设置、历史 run、Draft／Spec／Skill 或旧研究报告。

唯一新增的项目交付为本报告；测试临时资料不作为实验产物。未调用付费 API、未重新执行 lab.py run、未安装依赖、未运行 Git reset 或其他会改动真实仓库的命令。报告完成后停止。

## 附录 A：本轮离线探针复现代码

以下仅为报告内复现记录，不是新增模块或恢复系统。使用 autoskill Python，以 -B 执行；现有测试只写临时目录，网络入口被阻断。结尾断言在本轮两个官方现有测试失败时预期产生非零退出码；不要把这个退出码解释为真实 API 失败。

```python
import json,sys,ssl,socket,urllib.error,urllib.request,http.client,unittest
from unittest.mock import patch
import tempfile
tempfile.tempdir=r'C:\Users\lily\Documents\ChatGPT\回归解决退化文档'
sys.path.insert(0,r'D:\AS\AutoSkill-main\AutoSkill-main')
from AutoSkill4Doc.core.rate_limit import is_retryable_llm_error
from AutoSkill4Doc.stages.extractor import _is_retryable_extract_error,LLMDocumentSkillExtractor
from AutoSkill4Doc.core.llm_utils import llm_complete_json_with_retries
from AutoSkill4Doc.models import DocumentRecord
from autoskill.llm.openai import OpenAIChatLLM
rows=[]
def add(label,**value): rows.append(dict(test=label,**value))
factories=[
('ssl_eof',lambda:ssl.SSLEOFError(8,'[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol')),
('url_ssl_eof',lambda:urllib.error.URLError(ssl.SSLEOFError(8,'[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol'))),
('connect_timeout',lambda:TimeoutError('connection timed out')),
('url_timeout',lambda:urllib.error.URLError(TimeoutError('connection timed out'))),
('receive_before_response',lambda:http.client.RemoteDisconnected('Remote end closed connection without response')),
('remote_disconnected_named',lambda:ConnectionError('remote disconnected')),
('reset',lambda:ConnectionResetError('connection reset by peer')),
('certificate_verify',lambda:ssl.SSLCertVerificationError(1,'certificate verify failed')),
('json_error',lambda:ValueError('failed to parse JSON from LLM output'))]
for label,factory in factories:
 e=factory();add(label,exception_type=type(e).__name__,extract_retryable=_is_retryable_extract_error(e),common_retryable=is_retryable_llm_error(e),url_reason_type=type(e.reason).__name__ if isinstance(e,urllib.error.URLError) else None)
class SequenceLLM:
 def __init__(self,factory,failures):self.factory=factory;self.failures=failures;self.calls=0
 def complete(self,**kwargs):
  self.calls+=1
  if self.calls<=self.failures:raise self.factory()
  return '{"skills":[]}'
record=DocumentRecord(doc_id='offline-doc',source_type='document',title='Offline',domain='git',raw_text='Offline test',content_hash='offline-only')
def probe(factory,failures):
 llm=SequenceLLM(factory,failures)
 extractor=LLMDocumentSkillExtractor(llm=llm,extract_retries=1,extract_retry_backoff_s=0,llm_rate_limit_requests=0,llm_rate_limit_window_s=0,domain_type='git')
 try:
  extractor._complete_extract_json(payload={'offline':True},kind='extract_plan',repair_kind='extract_plan_repair',max_candidates=4,record=record,section_heading='Offline');outcome='returned'
 except Exception as e:outcome=type(e).__name__
 return dict(calls=llm.calls,outcome=outcome)
with patch('urllib.request.urlopen',side_effect=AssertionError('OFFLINE_NETWORK_GUARD')),patch('socket.create_connection',side_effect=AssertionError('OFFLINE_NETWORK_GUARD')):
 eof=probe(factories[1][1],99);assert eof==dict(calls=1,outcome='URLError');add('extract_eof_attempt_cap',**eof)
 timeout=probe(factories[2][1],99);assert timeout==dict(calls=2,outcome='TimeoutError');add('extract_timeout_local_cap',**timeout)
 recovered=probe(factories[2][1],1);assert recovered==dict(calls=2,outcome='returned');add('extract_timeout_one_retry_success',**recovered)
 llm=SequenceLLM(factories[1][1],99)
 with patch('AutoSkill4Doc.core.llm_utils.time.sleep',return_value=None):
  try:llm_complete_json_with_retries(llm=llm,system='offline',payload={},max_retries=2)
  except urllib.error.URLError as e:attrs=dict(autoskill_retryable=e.autoskill_retryable,autoskill_retry_attempts=e.autoskill_retry_attempts)
 assert llm.calls==3 and attrs['autoskill_retryable'];add('common_eof_cap',calls=llm.calls,**attrs)
 client=OpenAIChatLLM(api_key='offline-dummy',base_url='https://offline.invalid',timeout_s=180)
 injected=factories[1][1]()
 with patch('urllib.request.urlopen',side_effect=injected) as mock_open:
  try:client._post_json(payload={'model':'offline','messages':[]},stream=False)
  except urllib.error.URLError as received:same=received is injected;reason=type(received.reason).__name__
 assert same and reason=='SSLEOFError';add('transport_preserves_url_error',same_exception=same,reason_type=reason,calls=mock_open.call_count)
 processed=dict(server_completed=0)
 def ambiguous(req,**kwargs):
  processed['server_completed']+=1;raise urllib.error.URLError(ssl.SSLEOFError(8,'EOF after processing'))
 with patch('urllib.request.urlopen',side_effect=ambiguous):
  try:client._post_json(payload={'model':'offline','messages':[]},stream=False)
  except urllib.error.URLError:pass
 assert processed['server_completed']==1;add('server_processed_reply_lost',server_completed=1,client_success=False,billing='UNKNOWN')
 from tests.test_document_pipeline import DocumentPipelineTest
 names=['test_shared_llm_rate_limiter_auto_cools_down_after_retryable_error','test_parallel_document_extraction_retries_transient_rate_limit_errors','test_build_records_failed_document_without_aborting_batch','test_resume_does_not_skip_failed_document_snapshots','test_build_resumes_failed_run_without_reextracting','test_build_resumes_streamed_register_without_recompiling_processed_documents']
 result=unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(DocumentPipelineTest(name) for name in names))
 add('existing_offline_suite',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),names=names)
 print(json.dumps(rows,ensure_ascii=False))
 assert result.wasSuccessful()

```

另行执行过带 `[SSL: CERTIFICATE_VERIFY_FAILED]` 前缀的分类探针，结果 Extract=false、公共=true；执行过官方只读 resume-key 查询，找到当前 failed run。没有在真实 RUN2 上构造会写状态的 IntermediateRunWriter。

