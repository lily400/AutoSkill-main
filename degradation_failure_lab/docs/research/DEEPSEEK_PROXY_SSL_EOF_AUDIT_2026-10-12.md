# DeepSeek 预算修改与代理 SSL EOF 审计

任务指定文件名保留 `2026-10-12`；审计开始于 2026-10-12，继续核查及交付日期为 2026-10-13（Asia/Shanghai）。所有网络测量均标实际时间，不将第二天的环境快照倒填为历史运行现场。

## 1. 结论与执行边界

建议选择 **C：代理转发路径的间歇性故障与默认 Extract 的 EOF 重试覆盖缺口同时存在**。这里的“代理问题”不是已经证明代理设置错误或某个境外节点失效：本轮目标流量实际命中 `GeoIP(cn) → DIRECT`，即通过本地代理后仍由代理进程直连 DeepSeek。

已确认的核心结果：

- 只修改共享配置的 `max_http_calls: 100 → 150`、`max_observed_total_tokens: 200000 → 450000`。其余字段、CRLF 换行、历史配置均未改。五个案例的 `resolve` 和 `plan` 均可解析。
- 真实网络探测仅使用 DNS、TCP、验证证书的 TLS、无认证的首页 HEAD，未调用 Chat Completions。三组探测中，第二组代理路径两项均失败，而同时测试的显式直连成功；第三组代理恢复成功。
- 第二组的手工 CONNECT 已通过，随后 TLS 握手抛出 `SSLEOFError`；urllib 抛 `URLError(reason=SSLEOFError)`。同一时间代理日志记录两次到 DeepSeek 两个解析地址的 `dial tcp ...: i/o timeout`。
- 这强烈支持“本地代理转发路径的上游 TCP 拨号超时，导致下游客户端在 TLS 握手时看到 EOF”。但未记录探针源端口用于一一匹配，仍按有证据支持的推断而非完整链路因果证明处理；为什么代理拨号超时仍是 UNKNOWN。
- 官方 Extract 仍未匹配 SSL/TLS/EOF。离线注入中，`extract_retries=1` 和 `3` 都只调用一次。现有未提交包装层已经提供类型化传输重试，但共享配置未启用，默认 `transport_retries=0`。
- 现存 Case005 `r0c7bea4cc4ac` 是 Token 预算停止：43 次 HTTP 全成功、202146 观测 Token、28 Draft、2 Spec、0 最终 SKILL.md、27 条预算错误。不能将它称为 SSL 失败或技能生成语义失败。

本轮不实施网络修复、不增加任何配置字段、不调整重试、不重跑 Case005、不修改官方源码／已有包装层／测试断言／历史运行／旧报告。采用最小改动审计方法，报告依照用户提供的结构区分事实与推断，没有另造网络客户端或恢复功能。

## 2. 项目版本、工作区与证据范围

绝对目录缩写：

- ROOT = `D:\AS\AutoSkill-main`
- LAB = `D:\AS\AutoSkill-main\degradation_failure_lab`
- UP = `D:\AS\AutoSkill-main\AutoSkill-main`
- PY = `D:\anoconda1\envs\autoskill\python.exe`
- R5 = `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r0c7bea4cc4ac`
- PROXYLOG = `C:\Users\lily\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\logs\sidecar\sidecar_2026-10-12_22-46-46.log`

### 2.1 Git 状态

当前 ROOT 的 HEAD：`b28dbd238364007ee764a6774753441fbe26f3a2`；提交时间 `2026-10-12T21:56:56+08:00`；标题“检查为啥网络请求失败”。这是本地项目提交，不等于 DeepSeek 固定模型权重版本或来源文档的 commit。

开始时已有三处未提交修改，属于用户工作区，原样保留：

| 已有文件（LAB 下） | 原有 diff 的增加／删除行数 |
|---|---:|
| `src/degradation_lab/adapter.py` | 70 / 36 |
| `src/degradation_lab/provider_adapter.py` | 65 / 7 |
| `src/degradation_lab/runner.py` | 11 / 1 |

因此不能要求最终整个工作区“只出现一个 M”，也不能把这三处改动归为本轮实施。最初受限环境的 Git status 无法正常读取工作树；获准只读检查后成功。未改 Git 配置、索引或提交。

### 2.2 四个指定运行的真实可用性

| 运行 ID | 当前原始目录 | 可核验范围 | 当前可得结论 |
|---|---|---|---|
| `ra960b6759d7c`，Git reset | 不存在；当前 `runs/case004_git_reset` 也不存在 | 旧 SSL 审计及 `results/run_index.jsonl`；不是原始 event 重读 | 旧报告记录 Extract W4 Plan/H8、EOF、8 尝试/7 成功、31638 Token、exit=2；本轮不能复核原始字节、原因链和现场代理 |
| `r03836c5bdb9d`，Git restore | 不存在 | 台账确认 case_id、exit=2、结束 2026-10-12 21:13:17.888812+08 | 原始失败类型、预算、HTTP 事件、配置 UNKNOWN |
| `r1ce70c065fb7`，ripgrep | 不存在 | 台账确认 exit=2、结束 2026-10-12 21:36:56.414110+08 | 不能依据用户背景代替日志认定它是预算还是 SSL 失败；UNKNOWN |
| `r0c7bea4cc4ac`，ripgrep | 存在 | 实际 pipeline.log、43 个 model_calls、execution/config/invocation/official_result、HTTP 事件／末次 usage、包装层快照、artifact manifest | 确认 Token 预算停止，无失败 HTTP event；exception.json 不存在 |

不存在的三组目录没有被恢复、拼接或重新生成。没有仅因缺失就推断删除原因。旧审计 `LAB\docs\research\CASE004_GIT_RESET_SSL_FAILURE_AND_RECOVERY_AUDIT.md` 已读取；第 38–135 行是当时 Git reset 时间线，第 137–217 行是调用链、重试和旧环境，第 315–375 行是旧离线测试。其“32 次预算”“未见监听”“包装层没有传输重试”等内容都是当时快照，不能直接套用于当前配置和未提交代码。

当前其他 Clean 目录的 `execution.json` 均为 exit=0：Case001 `raecd75e08b34`（18 次、57472 Token）、Case002 `rd9ced750fa54`（13 次、29885）、Case003 `rab9a070dfa59`（9 次、28979）、Case004 Git restore `r18307cee4f4c`（67 次、197674）。这里只确认完成记录，不宣称本轮重新进行了四案完整语义审计。

## 3. 预算精确修改与真实含义

目标：`LAB\configs\generation\deepseek_flash.json`，第 17–18 行。

```diff
-  "max_http_calls": 100,
-  "max_observed_total_tokens": 200000,
+  "max_http_calls": 150,
+  "max_observed_total_tokens": 450000,
```

原文件 SHA-256：`3f3a767aad26ad475741fc801b7b8f417c87927d06ca92d61125459926a61dc2`。修改后：`bc6aa761c7bff47fdb3cb8d360b2377578a00bd2046bc294bf42fd9823feeccf`。

JSON 逐字段比较只有这两个差异；将这两处数字反向替换后，完整字节哈希回到原哈希。36 个 CRLF 保持不变。模型、thinking、max_tokens、max_input_chars、timeout、embedding、pipeline 和说明字段未动。temperature 原先不作为该配置的独立字段；官方 JSON 调用仍使用 0.0（UP\AutoSkill4Doc\core\llm_utils.py:28）。没有添加 proxy_mode、transport_retries 等字段。

`LAB\src\degradation_lab\runner.py:58–66` 每次 resolve 读取当前共享文件、校验、合并 pipeline overrides；`:78–104` 的 prepare 从 resolve 得到配置并写新快照。五案 clean resolve 实测均返回 150/450000；没有为验证而调用 prepare 或 run。`plan` 本身只输出摘要，不打印预算，因此不能只凭 plan 的输出声称数值已核验；数值来自直接 resolve 断言。

`LAB\src\degradation_lab\adapter.py:74–91` 在每次真实 HTTP 尝试前检查既有尝试数和已收到 usage 的 Token 总和。预算的边界：

- 150 限制当前执行器记录的 HTTP 尝试；失败尝试也计数，预算拒绝发生在发送前，不另生成 HTTP event。
- 450000 是已观察到的 Token 阈值，不是下一次响应的长度预留或人民币费用硬上限。单次响应可以跨线；失败但服务端已处理的 usage／费用可能未知。
- 当前 workers=1；若未来提高并发，还应单独审计在途响应与预算检查的竞态。本轮没有更改 workers。
- 新阈值不保证长文档一次完成，也不修复 SSL。价格、缓存折扣、失败计费和最终人民币金额 UNKNOWN，未虚构报价。

### 3.1 Case005 预算停止的直接证据

R5\execution.json：43 尝试、43 成功，prompt=172090、completion=30056、total=202146、exit=2；billed_cost=null。

R5\http\043\event.json / response.json：本次 usage=3285（prompt 2421 / completion 864）。此前累计 **198861**，低于旧 200000；因此 H43 获准发送，完成后累计跨到 202146。下一次调用在发送前被拒绝，**没有 H44 失败 event**。不是 100 次调用数耗尽。

R5\pipeline.log:73–98 为 26 个 Compile group 预算错误，`:101` 为 Register document 预算错误；R5\official_result.json 的 errors 数为 27，status=failed、Documents=1、Windows=12、Draft=28、Spec=2；实际 SkillBank 下 SKILL.md 数为 0。预算错误已经被阶段转为 result.errors，因此不存在 exception.json 不等于没有失败证据（当前 observer 的顶层异常写出见 adapter.py:141–144；历史 R5 包装层是旧版）。

R5 的 182 个 artifact manifest 项目均存在且哈希匹配。当前修改没有重写其 config.json；旧预算和成本记录原样保留。

## 4. 当前实际 HTTP 请求链与历史差异

```text
共享 DeepSeek 配置
→ ExperimentRunner.resolve / prepare 的配置读取与快照
→ adapter.execute 的 AutoSkillConfig / AutoSkill
→ autoskill.llm.factory.build_llm 的 connector_factory
→ degradation_lab.provider_adapter.build
→ ConfiguredOpenAIChatLLM（继承 OpenAIChatLLM）
→ complete → adapter.observed → limited_transport_retry（当前 retries=0）
→ ConfiguredOpenAIChatLLM._post_json
→ urllib.request.urlopen → ProxyHandler
→ http.client.HTTPSConnection → 本地代理 CONNECT → ssl TLS
→ DeepSeek HTTP 服务
```

源码定位：

| 环节 | 文件／函数／行号 | 事实 |
|---|---|---|
| 验证与载入 | LAB\src\degradation_lab\runner.py，validate_config:10–50；resolve:58–66 | 当前允许可选传输字段，但这次未增加／启用 |
| SDK 配置 | LAB\src\degradation_lab\adapter.py，execute:35–37 | key 只在真实运行的内存配置；本轮未调用 execute |
| 工厂 | UP\autoskill\llm\factory.py，build_llm:224–231；_build_openai:113–122 | connector_factory 走本地自定义构建，基础类仍官方 OpenAIChatLLM |
| DeepSeek 子类 | LAB\src\degradation_lab\provider_adapter.py，build:68–84；_build_payload:48–51 | 增加 thinking；proxy_mode 缺省 system |
| 请求观测／重试 | LAB\src\degradation_lab\adapter.py，observed:69–118；monkeypatch:128–129 | 两个类均被观测；每个 send_once 单独计预算和 event；缺省 transport_retries=0 |
| 实际发送 | LAB\src\degradation_lab\provider_adapter.py，_post_json:53–65 | system 分支调用 urllib.urlopen；direct 分支已有但当前未选，不是本轮新增 |
| 官方基础类 | UP\autoskill\llm\openai.py，complete:127–139；_build_request:237–250；_post_json:252–260 | POST JSON；只处理 HTTPError；URLError 继续传播 |
| 标准库代理 | PY 所在目录\lib\urllib\request.py，ProxyHandler:795–821；getproxies:2738–2745 | 无环境代理时读取 Windows HKCU 代理；不是 requests/httpx |
| CONNECT 与 TLS | 同一 request.py:1336–1355；lib\http\client.py，HTTPSConnection.connect | 代理隧道后用目标主机 SNI；TLS 校验未关闭 |

R5\wrapper_snapshot\degradation_lab\adapter.py:50、96、115 只挂接官方基础类；对应 provider_adapter 快照没有当前的 _post_json 覆写或传输重试。这说明当前三处未提交改动与历史执行代码不同。不能说历史运行已经享受当前重试，也不能用当前源码替换其 frozen wrapper 作为原始证据。

代理决策主要由标准库默认 opener/ProxyHandler 决定；Windows WinHTTP 配置不是这条 urllib 的代理来源。官方 request.py:1333 使用 `Connection: close`，此链没有 requests/httpx 连接池，也没有证据支持“复用了过期 keep-alive socket”。

## 5. Windows、Python 与代理状态

网络探测时快照为 2026-10-12 22:46:48+08；继续任务后于 **2026-10-13 13:57:34+08** 再做只读快照，以下代理解析字段仍一致。第二天没有重新执行网络探测。

| 项目 | 实测结果 | 限制 |
|---|---|---|
| Python / OpenSSL | PY，3.10.21 / OpenSSL 3.6.4（25 Aug 2026） | 不代表历史各次环境完全相同 |
| HTTP_PROXY / HTTPS_PROXY / ALL_PROXY（含小写） | 均无；NO_PROXY/no_proxy 无 | 没有环境变量不等于不走代理 |
| urllib.getproxies() | http、https、ftp 均 http://127.0.0.1:7897；无代理凭证 | 仅暴露 scheme/host/port 与凭证存在布尔值 |
| proxy_bypass("api.deepseek.com") | false | 本次默认 urllib 走代理 |
| HKCU Internet Settings | ProxyEnable=1，ProxyServer=127.0.0.1:7897；ProxyOverride 有，AutoConfigURL 无，AutoDetect 未读到 | 未输出 bypass 全列表、PAC URL 或注册表其他内容 |
| WinHTTP | `Direct access (no proxy server)` | 与 urllib 采用 HKCU 代理并不矛盾 |
| 7897 监听 | 10-12 为 127.0.0.1:7897，PID 32956，verge-mihomo；10-13 为 PID 21612 | 进程已经变化；旧报告未见监听不能作为当前事实 |
| 代理软件 | Clash Verge；相关核心路径 D:\Program Files (x86)\Clash Verge\verge-mihomo.exe | 未打印完整命令行、订阅、节点凭证、控制器 secret |
| 启动配置 | -f 指向 C:\Users\lily\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\clash-verge.yaml；line 1 mode: rule，line 2 mixed-port: 7897；tun.enable: false（line 21） | 文件值不等于核验了所有运行时 API 覆盖；日志另证当次实际规则 |
| TLS 校验 | check_hostname=true、CERT_REQUIRED、最低 TLSv1.2 | 未使用 unverified context |
| 证书环境 | SSL_CERT_FILE 存在；其余三个相关变量无 | 未输出文件路径或证书环境值；历史 CA 状态 UNKNOWN |

规则模式可以将目标命中 DIRECT 或代理组；全局模式通常会改变所选出口；TUN 若开启，可以拦截不使用 urllib 代理的 socket。这里没有切换任何模式。所谓“显式直连”只保证诊断客户端不使用环境／HKCU 的应用代理，不保证排除所有其他网络设备、系统级拦截；启动配置 tun.enable=false 仅减小本软件 TUN 混杂，未全面审计其他软件。FlClashHelperService 进程曾可见，但没有证据证明它影响本次路由。

此前“端口未监听”若真实发生，可以解释代理连接拒绝／无法访问；单独不能直接解释已建立 CONNECT 后的 TLS EOF。当前已确认监听，且失败发生在代理上游拨号／客户端握手阶段，而非简单的本地端口不存在。

## 6. 安全网络探测与代理日志对应

仅访问 `api.deepseek.com:443`，无 API Key、Authorization、Cookie、Proxy-Authorization；HTTP 为 `HEAD https://api.deepseek.com/`，不是推理端点。没有发送任何模型 Prompt。每项 socket/HTTP timeout=10 秒；各组最多四项并行，无自动重试。保持证书和主机名验证，未改系统代理、环境、注册表、路由或 TLS 设置。

DNS 当时解析为 `113.240.66.218`、`175.12.122.167`；这是当时 getaddrinfo 快照，不是永久地址或新增配置。三组共 12 个网络探测动作；各 HEAD 自身的库内 DNS/建联不另当独立统计样本。

| 时间（UTC+08） | 显式直连 TCP/TLS | 默认 urllib 系统代理 HEAD | 显式直连 HEAD | 代理 TCP/CONNECT/TLS |
|---|---|---|---|---|
| 10-12 22:46:48 | 成功，0.062s；TLSv1.3 | HTTP 401，0.359s | HTTP 401，0.187s | 成功，0.250s；TLSv1.3 |
| 10-12 22:47:57 | 成功，0.062s；TLSv1.3 | URLError.reason=SSLEOFError，5.140s | HTTP 401，1.156s | CONNECT 200 后握手 SSLEOFError，5.125s |
| 10-12 22:48:09 | 成功，0.062s；TLSv1.3 | HTTP 401，1.359s | HTTP 401，3.187s | 成功，0.235s；TLSv1.3 |

TLS 成功时使用 TLS_AES_256_GCM_SHA384；直连／代理成功样本证书 DER SHA-256 均为 `30d82529d19c5da6175a80db1c5522ac3ba5b42589212405cdc8783a1bf047fa`，并通过当前默认信任与主机名验证。这没有证明所有时间都无证书问题，也没有全面排除网络拦截。

三种场景的边界：

- **代理开启**：实际测了，默认 urllib 不 bypass，路径有成功也有 EOF。
- **显式直连**：实际测了，urllib 用临时 ProxyHandler({})；TLS 探针直接创建到目标的 socket。只影响临时诊断进程，没有强制实验程序改走直连。
- **系统代理关闭**：未实际测试；禁止任务之外切换开关。不能把显式直连的成功冒充“关闭代理后主机整体已验证”。

401 在这里说明无认证 HEAD 得到了 HTTP 响应，不等于合法 Key 有问题，更不等于 Chat Completions 健康或完整生成成功。样本少且探针不同于长 POST，不能将“代理某项 1/3 失败”当未来生成的概率估计。

### 6.1 异常抛出层

手工代理探针的失败堆栈实际到达：`ssl.py:513 wrap_socket → :1104 _create → :1375 do_handshake`。代码只有在 CONNECT 状态 200 后才进入 wrap_socket；失败发生在握手阶段，尚未发送目标 HEAD 或模型正文。

默认 urllib 的失败调用栈为：`request.py:216 urlopen → :519 open → :536 _open → :496 _call_chain → :1391 https_open → :1351 do_open`。该行用 `URLError(err)` 包装 h.request 的 OSError，reason 类型实际为 SSLEOFError。历史 Git reset 的 event 只存请求前应用 stack，不能直接替代这种真实异常堆栈。

### 6.2 代理日志的额外证据

仅筛查与 api.deepseek.com 有关的日志行，不提交其他流量或代理认证数据。

| PROXYLOG 行号／时间 | 实际记录 | 解释 |
|---|---|---|
| 67、69 / 22:46:48.746 | `[TCP] ... api.deepseek.com:443 match GeoIP(cn) using DIRECT` | 第一组成功时流量进入代理，由代理选择直连 |
| 693、695 / 22:48:02.786 | `[TCP] dial DIRECT (match GeoIP/cn) ... api.deepseek.com:443 error: dial tcp ...: i/o timeout`；每行列出 113.240.66.218:443 与 175.12.122.167:443 | 与第二组两个代理失败结束时刻及约 5s 时长吻合；失败是代理自己的上游 TCP 拨号，而客户端观察为 SSL EOF |
| 795 / 22:48:10.185；813 / 22:48:11.205 | 同目标 `GeoIP(cn) using DIRECT` | 第三组恢复；不支持永久断网解释 |

两条失败各自尝试两个目标 IP；日志有 DIRECT，不支持“本次必然走某个远端代理节点”。没有保存探针本地源端口，也未抓包，不能唯一映射每条代理连接到每个探针或证明具体是谁发了 FIN/RST。此证据仍显著强于只有 EOF 字符串。

## 7. 根因假设的证据分级

| 命题 | 级别 | 支持与剩余不确定性 |
|---|---|---|
| urllib 读取 Windows 代理，即使无 HTTPS_PROXY | 已确认事实 | 当前 Python 标准库源码＋两次快照＋代理目标日志 |
| 当前 7897 不监听 | 已被当前检查否定 | 获准的主机检查确认监听；旧受限／旧时刻观察不能沿用 |
| 代理路径存在间歇性故障 | 已确认事实 | 第二组代理 TLS/HEAD 失败、直连成功、第三组代理成功 |
| 本次 EOF 由代理上游 TCP 拨号超时导致 | 有证据支持的强推断 | 两次 DIRECT 拨号超时与两个 EOF 时间吻合；缺源端口/抓包一一关联 |
| 为什么代理进程到同目标两 IP 超时，而 Python 当轮直连成功 | UNKNOWN | 进程级路由／防火墙／DNS拨号策略／短时链路差异均未定位；不选择其中一个当事实 |
| Windows 代理配置错误、代理节点错误或 TUN 导致 | UNKNOWN | 端口/CONNECT 工作、日志为 DIRECT、启动文件 TUN 关闭；未证明设置错误或远端节点参与 |
| 证书校验失败导致本次 EOF | 未获支持 | 成功连接证书可验证；失败字面不是 CERTIFICATE_VERIFY_FAILED，代理日志是 TCP timeout；历史情况仍 UNKNOWN |
| 应用 timeout_s=180 不够 | 未获支持 | 约 5.1s 即 EOF；本轮安全探针 timeout=10s；代理自身拨号超时不同于官方 180s |
| Git/ripgrep 请求体太大或文档触发模型拒绝 | 本次复现已表明不是必要条件 | 无正文的 TLS/HEAD 也能复现；旧 Git 报告 H1 比 H8 大且成功；历史长 POST 仍未完整排除其他内容相关限制 |
| DeepSeek HTTP/模型服务断开导致所有历史故障 | UNKNOWN | 本次没有完成 TLS，代理日志在 TCP 拨号；服务端／网络参与者无法唯一定位，三组成功也不能证明服务长期正常 |
| SSL EOF 说明模型 Skill 语义质量差 | 不成立的评价合并 | 传输可靠性与技能质量是不同结果；本轮没有做模型语义比较 |
| 所有三个缺失历史 run 均同本次根因 | UNKNOWN | 只有其中一个有旧报告；现场证据及原始 event 不在 |

因此 C 的准确含义是“已观察到代理路径中断，加上默认客户端恢复保障不足”；不是已完成所有历史网络事故的唯一根因证明。对代理拨号超时的底层原因，仍保留 D 所需的进一步诊断。

## 8. Extract 与其他阶段的重试差异

| 层 | 源码定位 | 当前 EOF 行为 |
|---|---|---|
| 官方 Extract 独立判定 | UP\AutoSkill4Doc\stages\extractor.py:137–168 | 字符串表没有 ssl/tls/eof，因此 false |
| 单次 Plan/Expand 重试循环 | 同文件 _complete_extract_json:828–854 | :841 判定 false 后立即抛，不受提高次数影响 |
| 外层 Window/Document 提取重试 | 同文件 _extract_document_with_retries:1318–1341 | :1328 用同一判定；同样不补救 EOF |
| 速率包装层 | UP\AutoSkill4Doc\core\rate_limit.py:99–113 | 记录错误和 cooldown 后 raise，不是重新提交循环 |
| 公共 LLM 判定及循环 | 同文件:219–246；core\llm_utils.py:43–76 | 包含 ssl/tls/eof；缺省 max_retries=2，可重试至 3 次 |
| Compile / Register | UP\AutoSkill4Doc\stages\compiler.py:348；store\versioning.py:1371、1544 | 使用公共 helper，与 Extract 不同 |
| 当前已有 lab 传输白名单 | LAB\src\degradation_lab\provider_adapter.py:13–40；adapter.py:116–118 | 能识别 URLError.reason=SSLEOFError，排除证书及 HTTPError，但当前 retries=0，实际不重试 |

离线注入得到：

| 异常 | Extract | 公共 helper | 现有传输白名单 |
|---|---|---|---|
| URLError(SSLEOFError) | false | true | true |
| TimeoutError | true | true | true |
| 带 SSL 前缀的 SSLCertVerificationError | false | true | false |
| 标准 RemoteDisconnected 消息 | false | false | true |

“只把 extract_retries 从 1 提高到 3”对本次 EOF **无效**：两个设置都实际只有 1 次 complete。对已经识别的 timeout 等，则单操作与外层重试可能叠加：retries=1 时至多 2×2；提高为 3 时至多 4×4 次单操作尝试（还不含 JSON repair），且外层可能重做同一窗口已成功的 Plan/Expand。不能把 retries=3 简化为“最多多请求三次”。

现有传输重试的离线 fail-once 测试可在 retries=1 时调用 [1,2] 并成功，但这只证明函数行为，不证明现场网络或付费生成恢复。若未来启用最多 1 次传输重试，Extract 的纯 EOF 两次后仍停止；Compile/Register 的公共重试可能与之叠加到 2×3 次；timeout 在 Extract 多层叠加还可能更多。需统一预算和逐尝试日志，不能无限 retry。

现有 logical_call_id 只在一次 observed 调用内关联传输尝试；官方再次调用 observed 会得到新 logical ID，不能误以为已跨所有层统一识别了同一语义请求。传输尝试发生在速率 wrapper 的一次 complete 内，可能未再次 acquire 官方 limiter；若启用，要另核查真实请求速率。这些均仅记录，不修改。

## 9. 最小补救建议、风险与费用

仅建议，未实施；不以本报告替代下一轮授权。

1. **先稳定并解释网络路径。** 当前不是“先启动一个不存在的端口”问题。优先在用户可见代理软件中核查 DeepSeek 的 DIRECT 规则、核心版本、进程路由／防火墙和目标 IP 拨号；可批准一个有限的、无认证的配对复测，增加本地源端口、实际目标 IP、CONNECT 状态及代理日志关联。对代理软件或网络修复措施分别审批，不自动切全局、换节点、改注册表或关闭证书校验。
2. **不要重新实现已有包装层。** 若批准，先审阅当前三处未提交改动及其离线测试，再选择是否启用现有小白名单的一次额外传输重试。当前任务不新增对应配置字段。保持官方模型／Prompt／解析逻辑不变，并标记为“官方生成逻辑＋受控传输策略”，不混同旧执行策略。
3. **完善可归因日志，限制范围。** 当前已增加 reason_type，但未保存足够异常 cause/traceback、握手阶段／连接关联信息。下一轮仅补必要无敏感诊断及跨层尝试上限测试；不能记录 Authorization、真实 Key、代理 userinfo、控制器 secret 或其他用户流量。
4. **付费复测仍需批准。** 网络准入、现有改动审核、每尝试计数／预算停止／失败传播测试完成后，才请求一次隔离的新 Case005 Clean 运行。当前 lab 普通 run 创建新 store，不是安全续跑；不要直接在旧目录执行恢复或承诺重用已有 28 Draft 一定省费。

POST 交付失败时服务端是否处理／计费可能 UNKNOWN。此次无模型 TLS 探测没有推理费用，但历史 EOF 不能因此认为免费；传输重试可能重复处理／收费。新 150/450000 仍只是观察预算，不是金额承诺。

基于 R5 的已见结构，下一轮**规模规划**可采用：1 outline + 12 Window Plan + N Expand + G Compile + S Register + H hierarchy + R repair/retry。R5 的 N=28、已见 Compile 28 组，只完成 2 组；若后续新生成仍为 N/G/S=28 且无额外 hierarchy/repair/retry，参考基础量为 1+12+28+28+28=97 次。该数字是条件性计划，**不是已验证调用数或严谨上界**；新候选、合并、Register 分支和随机输出均可改变规模，完整 Token/人民币费用 UNKNOWN。150 次给出的余量不可替代停止规则，也不保证一次完成。

## 10. 离线验证、失败分类与修改保护

使用 PY、`-B`；验证脚本为当前可写工作区的临时文件，结束后删除，不进入 lab 源码。测试期间阻断 urllib.urlopen、OpenerDirector.open、socket.create_connection；虚拟模型只抛内存异常，没有读取 Key 或发模型请求。

| 检查 | 结果 | 归因／边界 |
|---|---|---|
| JSON 两个阈值与字段差异 | PASS | 正整数 150/450000；无新增传输参数 |
| 实际 validate_config | PASS | runner.py:45–46 校验；8 个非法预算值（0/-1/bool/float × 两字段）全部拒绝 |
| 五案 clean resolve | PASS | 全部读取新预算，来源/案例合法性与输入 hash 校验无误 |
| `scripts/lab.py plan` 五案 clean | PASS，exit=0 | 未 prepare/run；输出仍为独立运行模式；plan 摘要不含预算 |
| Extract EOF retries=1/3 注入 | PASS | 均 1 次；复现缺口，不是修复验证 |
| 白名单排除证书；传输 fail-once | PASS | retries=1 时 [1,2]；未启用真实配置 |
| 六个选定现有 framework tests，首次 | 4 PASS / 1 FAIL / 1 ERROR | 下述已有断言与环境问题；不能称全通过 |
| 路径测试单独复核，默认短临时目录 | 1 PASS | 未改测试断言／系统永久环境 |
| git diff --check | PASS | 本轮预算 diff 为 2 增加/2 删除 |

首次 FAIL：`LAB\tests\test_framework.py:93–105` 的 test_actual_case001_and_original_rules_unchanged，`:94` 仍断言全部案例列表只有 Case001。五案现状导致失败；`:104–105` 还存在单一 source_manifest 假设但本次未走到该断言。它是已有测试协议滞后，不是预算修改引起；未改断言、未宣称 Case001 后续未执行断言已验证。

首次 ERROR：同文件 `test_windows_path_guard_before_paid_call:130–136`，在本轮较长可写临时根下，“short”路径仍被计算为 279 字符，正确触发 io.py:78 的保护。随后仅将这个测试的进程临时目录恢复为系统默认短目录并重跑，PASS；真实 D:\AS 案例的 plan 路径检查已通过。未将首次 ERROR 隐藏或改成 PASS。

首次临时验证脚本末尾的预期结果断言也因此非零；同一工具输出后的 plan 为零，不能用工具最终 exit=0 掩盖前一个测试失败。完整 framework／官方全套测试未运行。旧 SSL 报告的六个官方测试结果只作为旧记录，本轮没有重新验证其断言失败是否仍出现。

其他环境限制：继续任务后受限进程启动 PY 返回 1 且无诊断；第一次外部只读验证的权限审查超时，按提示仅重试一次后获准成功。受限 netsh 子命令亦无法读取，获准主机只读检查取得 WinHTTP 状态。最初尝试读代理 YAML 的 PyYAML 不可用（ModuleNotFoundError）；未安装依赖，改用限定键的行级只读提取，并以流量日志补证。以上不是本轮预算回归或 API 失败。

### 10.1 文件保护校验

开始前与交付前分组文件清单哈希完全一致（路径→文件 SHA-256 的排序 JSON 再取 SHA-256；与原工程 inventory 格式不同，不与旧报告的清单哈希直接对比）：

| 保护范围 | 文件数 | 清单 SHA-256 |
|---|---:|---|
| 官方目录 UP，全部文件 | 265 | b104c7e570c982d9b876368d3003a040e07b8d1a9103674c7d0468c5f0e7fec7 |
| 当前 lab src（含原有三处改动） | 10 | cf735d168b4921dc4813a8f24f29dd2e8bd0e01e4410842514246be4a3fdf0f4 |
| 历史 runs 全部文件 | 1081 | 0aa8373e98e393740308e00165d11bc7f1206b2579bbbe0314248cd1d33fa77a |
| lab 其余文件，排除 src/runs、本次配置与本报告 | 102 | 35f410e74d25479d2242538eafc5cf74d916755c7eb0431e063f619b7799f238 |

配置通过反向替换字节哈希核验只有两个值变更。报告以新文件保存、拒绝覆盖既有同名文件。未修改任何历史 config、日志、SKILL.md、原始来源、清单、测试、官方或已有包装层；未提交／推送／清理用户文件。

## 11. 下一步与停止条件

本轮完成预算修改和此报告后停止。建议下次明确批准的任务是：**审阅现有三处网络包装层改动，做有限无认证配对诊断并关联代理 DIRECT 拨号日志；补必要的跨层重试上限与预算计数离线测试**。不先改官方 Extract，不先提高 extract_retries，不立即重跑第五篇。

对选项的明确回答：

- A 单独“代理配置错误”：目前不足以这样定性；端口和规则有效，但代理路径确有间歇性拨号失败。
- B 单独“重试缺陷”：不足以解释第一次 TLS 为什么断开；但解释默认 Extract 为什么不恢复。
- **C：当前最适合的行动结论**，网络路径可靠性和客户端恢复保障分别处理；优先复用已有未提交包装层，不另建机制，任何启用或代码修复等待批准。
- D：对更底层的拨号超时原因及缺失历史运行的归因仍适用，需要源端口/目标 IP/代理日志关联、进程路由和防火墙的安全证据；不凭猜测选择一个根因。

未运行付费实验或实施网络修复。小样本探测不能保证长 POST 或完整 Case005 成功，后续实际费用及失败请求计费均 UNKNOWN。
