# S0.2：BeautifulSoup Task-037 提交证据与判分信任边界

日期：2026-10-24。项目：D:\AS\AutoSkill-main。状态：**BLOCKED_NEEDS_FIX**。

本设计承接 R3 与 S0；本轮只实现协议、静态计划和离线夹具测试。没有执行候选程序、Oracle、判分进程、Harbor Trial、模型、网络或 Docker。不得把本文中的期望结果理解为实测结果。

## 1. 当前实现与停止决定

| 部分 | 实际完成 | 未完成与边界 |
|---|---|---|
| 提交收据 | v2 协议、会话认证、精确路径/条目、Trial/配置/代码/大小/SHA 绑定；显式 fixture 签发 | 没有真实 Harbor 观察钩子；没有真实导出收据；真实模式初始化即拒绝 |
| 判分请求 | 新外部目录计划、只读输入、独立输出、原始资产身份、完整输出要求、request SHA | 不创建运行环境，不执行命令；配置字段不是预检证明 |
| 结果证据 | fixture 认证、请求/收据/候选绑定；四类输出大小/SHA、完整 JUnit/reward 校验；分类超时与基础设施异常 | 不证明结果来自可信 Oracle；真实输出回收与超时终止未实现 |
| 原始评分 | 原 Oracle 原字节与身份保留；只解析原 15 项证据 | 同进程候选导入仍不安全；没有实测基准分 |
| 行为评分 | bs37-behavior-v1-draft，独立通道、检查清单与正负样例设计 | DESIGN_ONLY / NOT_IMPLEMENTED；没有执行器，没有行为正确率 |
| 工程记录 | 保留 S0 零模型探针与统计拒绝保护，代码身份加入新协议模块 | 没有新的真实运行时记录 |

**停止实现真实判分执行部分。** 在原 eval.py 不变、任意 Python 候选与真实 bs4.Tag 在同进程直接交互的前提下，本轮无法建立已证明的可信隔离。继续接上 subprocess、Docker 或普通独立目录，只会把未解决的信任问题包装成可执行后端。因此 execute_scoring 与 grade_export 的运行拒绝继续保留，不能通过 preflight_required 或 separate 字段解除。

## 2. 实际 Harbor 导出链与可信签发位置

固定 Harbor 为 0.24.0，提交 2de4605b9404eada7d341388291e6e469c90330b。

实际链为 SingleStepTrial._collect_artifacts → Trial._collect_artifacts_phased → ArtifactHandler.download_artifacts → _download_artifact / _write_manifest。

- ArtifactManifest.to_json_data() 返回条目列表，不是以 entries 为键的对象。
- 每条包含 source、destination、type、status、service、exclude；不含候选哈希、文件大小或远程不存在证明。
- 任务源路径是 /workspace/agent_output.py；显式任务目标是 workspace/agent_output.py。
- 原 Handler 写入 manifest 的 destination 是 **artifacts/workspace/agent_output.py**；host 实物为 trial.artifacts_dir/workspace/agent_output.py。两种 destination 不可混淆。
- 下载失败被 best-effort 记录为 failed；不能据此推断 Agent 未提交。
- Trial._collect_artifacts_phased 当前等待 download_artifacts，但没有向上返回其 ArtifactManifest；只在事后读取磁盘 manifest，不能恢复独立的真实观察证明。

未来可信签发者应是**控制端的任务专属导出协调器**，在官方下载调用返回后取得返回元数据，与控制端写盘 manifest 逐项对照，再冻结字节并签发。它必须先绑定可信 Trial.config.trial_name、Task 配置身份、允许的服务与源路径，且控制目录和密钥不可挂载进 Agent 或候选环境。不得依赖候选写出的 JSON、publish 文件或 stdout 声明成功。

后续需单独审查如何在不修改官方 Harbor 的情况下包装 ArtifactHandler 调用并捕获返回值，如何排除后台进程在下载期间改写文件，以及必要的源端/导出端身份核对。本轮未安装该钩子、未进行传输。

证据源码：
- [.external/harbor-full/src/harbor/models/trial/artifact_manifest.py](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/models/trial/artifact_manifest.py)
- [.external/harbor-full/src/harbor/trial/artifact_handler.py](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/artifact_handler.py)
- [.external/harbor-full/src/harbor/trial/trial.py](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py)

## 3. 收据 v2 与当前认证的真实含义

beautifulsoup_exports.ExportController 只能以 fixture=True 创建；fixture=False 在读取文件或初始化运行时之前拒绝。capture_fixture 要求显式传入模拟“返回元数据”，对照实际夹具 manifest 后计算候选字节身份，全部签发 evidence_kind=offline_fixture。没有可切换为真实模式的布尔开关。

收据绑定：

- schema_version、evidence_kind、authority_id、Task ID、Trial ID；
- 精确 source/destination、manifest_entry_index、完整对应条目及 manifest SHA；
- exported / download_failed / source_absent / origin_unknown；
- 候选大小与 SHA（失败时允许保留部分文件身份，不能据此评分）；
- 任务配置路径与 SHA、控制端 artifacts 根；
- 当前适用代码文件 SHA、Harbor 版本/提交、导出组件、合成观察标识与 source_state；
- receipt_id（规范 JSON 的 SHA256）与会话 HMAC。

HMAC 使用控制器内存中的随机密钥；候选不能仅改字段、重新算 SHA 就得到有效认证。验证方必须由可信调用方提供原控制器对象与期望 Trial ID，不能从候选输入反序列化“可信控制器”。会话认证只证明此控制器签发过这一夹具，**不证明传输真实发生、控制主机安全、Oracle 独立或评分正确**。

密钥不写文件、不打印。控制器退出后没有跨进程的持久信任存储，本轮不声称持久收据可独立重新认证。真实控制端密钥持久化、权限、轮换和复验来源仍需另行设计，不使用模型凭据或研究账本替代。

collect_export 拒绝未认证字典、错误 Trial/配置/路径、重复文件、非法条目、大小或 SHA 不符。仅有受认证的独立 source_absent 观察且没有导出文件时，才可区分确证未提交；本轮这种观察也只是显式夹具。没有该观察时 failed 始终是下载失败，不是答错。

## 4. 请求与结果的证据链

路径为：

控制器上下文 → 收据 receipt_id → scoring_plan.export_receipt_id / Trial / task_config_sha256 → request_sha256 → 结果的相同身份与输出清单。

输入包括候选、原 eval.py 和原 test.sh；只读角色与输出目录互斥，输出计划必须是仓库外全新目录。收据的候选哈希必须与请求头和输入身份清单一致。无收据的 scoring_plan 只允许作为未绑定静态计划，不能成为 inspect_result 的评分证据。

结果协议要求：

- 明确 execution_status、整数 returncode、error_type；
- Task、Trial、receipt_id、request_sha256、候选与原始资产 SHA；
- junit_xml、reward、stdout、stderr 四项完整原始 bytes；
- 四个唯一输出条目及各自大小和 SHA。

fixture 结果由 seal_result_fixture 显式标为 synthetic_fixture_backend，并认证元数据；它不是生产判分签名器。inspect_result 对照认证元数据与输出字节，拒绝未知来源、重复条目、缺项、截断、候选/manifest 改变、缺失/重复 JUnit case 和 reward 不一致。原 shell 恒 exit 0，所以不能只看 shell 退出码；缺完整 15 项 JUnit 或只出现 CTRF 1/1 时不可成功。

超时、未执行、基础设施异常与任务断言失败分开记录；保留日志 bytes 的 base64 与 SHA。即使夹具格式和 15 项结果均有效，也始终 trusted_score=false、runtime_isolation_verified=false、real_agent_outcome=false、task_success=null，正式统计入口拒绝这类记录。

## 5. 五个信任域与未解决的隔离

| 域 | 应有权限 | 当前证据 |
|---|---|---|
| Agent 环境 | 题面、必要依赖、本条件 Skill；不能读原文旁路、隐藏测试、控制器、其他运行 | 只有静态派生；没有运行时访问验证 |
| 候选导出 | 单一候选文件，收集后冻结；不能声明来源或修改收据 | 已有夹具级身份与防伪协议；无真实传输证明 |
| 可信 Oracle/测试 | 控制器持有原字节；Agent 阶段不可见 | 原始身份核验；没有运行时验权 |
| 判分执行环境 | 与 Agent 分开、无网络、只读候选输入；可信断言应不受候选影响 | 未实现可信执行后端 |
| 结果与日志 | 由可信控制端回收、控制端独占写入、按请求绑定 | 只实现合成证据协议与解析 |

原 eval.py 直接 import agent_output，随后在同一 Python 进程创建 Tag、调用候选并断言。若按原计划运行，候选可以读取同进程可访问的测试、观察或污染 sys.modules/pytest/bs4、访问可写结果目录。只读测试挂载只能防磁盘改写，不能防读取、猴子补丁或伪造结果。容器 UID、目录、separate 名称都不能独自解决同进程 Python 信任。

把 HTML/Tag 序列化到另一个进程再读回，会生成不同对象，不能证明 result is original_tag，也无法无损替代真实 Tag 的别名关系和父子对象语义。代理 Tag、受限 Python、RPC 操作桥会改变执行 API 或依赖语义，需要新的、经审查的 scorer 定义。本轮没有实现这些替代物。

在候选进程里加入“可信测量函数”也不自动可信：同一 Python 解释器中的任意候选仍可能检查或污染它。进程输出的布尔值与签名后的传输只能证明谁报告了值，不证明断言没有被影响。

可讨论的后续方案是带独立可信观测根的隔离执行设计，或在明确威胁模型下报告“非对抗基准对照”。两者都需要新的审查与运行时证据；后者不能冒充隐藏测试隔离已完成。当前无法保证保留语义的可信隔离，因此停止真实后端实现。

## 6. 原始基准分与行为正确率

原 Oracle SHA256：c7ee6d37d069c02aa9c6059ed6dcc28857ad44dcdd002d73642fa4838a4c7e6c。
原 test.sh SHA256：2ad84cb7df6840331626a506a5e106ddb79de898da1737bf21471f1d3b8d472a。
原文件不修改，不“修复”哈希。

**原始基准分**：原 15 项测试及原 reward 的观测结果，包含 test_uses_tag_name_assignment 对完整源码的 .name 和正则 \.name\s*= 限制。它同时衡量这些行为样例和该源码写法约束，不等价于纯行为正确率；注释匹配也不能证明该语句实际执行。

**行为方案 bs37-behavior-v1-draft**：单独版本、DESIGN_ONLY；保留原 14 项行为检查的目标与真实 bs4.Tag 输入、同对象返回、属性/内容保留、文档树位置要求，排除上述唯一的源码文本限制。test_assigns_to_tag_name 名称虽有 assignment，其现有断言检查改名和对象身份，仍保留。不得从原分数简单减去语法失败就宣称行为通过。

记录采用 score_channels.original_benchmark 与 score_channels.behavior。前者可以保存带 OFFLINE_FIXTURE_REVIEW 标记的解析观测；后者在执行器缺失时保持 NOT_IMPLEMENTED 和 trusted_score=null。原始结果永不被行为结果覆盖；两者共用候选、Trial、导出收据、请求和版本身份。

本轮没有改变函数签名、真实 Tag 类型、身份或树语义。任何未来为隔离而改用代理、复制对象或仅比较序列化 HTML 的方案，都会改变这些语义，必须停止并先报告差异。

### 受控样例矩阵（全部为设计预期，未执行）

| 样例 | 原始基准预期 | 行为方案预期 | 目的 |
|---|---|---|---|
| tag.name = new_name; return tag | 预期 15/15，待运行验证 | 预期通过，待验证 | 正确直接赋值 |
| setattr(tag, 'name', new_name); return tag | 预期源码限制拒绝，具体完整结果待验证 | 预期通过，待验证 | 等价写法假阴性 |
| 直接 return tag，不改名 | 至少改名检查失败 | 失败 | 错误名称 |
| 改名但清空 attrs | 至少属性检查失败 | 失败 | 业务负例 |
| 创建新 Tag 返回 | 至少身份检查失败 | 失败 | 身份语义负例 |
| 脱离/重插并改变位置或破坏 children | 至少位置/内容检查失败 | 失败 | 后续树语义校准样例 |

离线测试只解析候选源码字符串的 AST/源码模式、检查样例元数据与协议；没有导入或调用这些函数，没有执行原测试。真实正负校准仍被阻断。

## 7. 无模型运行时验证前的最小条件

1. 审查并实现控制端真实导出观察钩子、收集期间源文件冻结策略，以及真实 Trial/配置/来源绑定；不能把 fixture 标签改成 runtime。
2. 建立真实收据的持久认证与目录权限边界；证明 Agent、候选及共享 mounts 不能访问控制器密钥、收据和输出。
3. 对 Oracle 的直接导入问题给出可接受且保留语义的设计，或明确另行批准的有限非对抗对照口径；未解决前不得开启可信评分或正式成功率评估。
4. 之后才单独授权无模型环境/传输测试；镜像、依赖、Skill 可见性、网络、实际回收和超时终止仍须实测，缺任何条件即停。
5. 行为方案继续作为独立草案；不得以它覆盖原始基准或历史记录。

当前只满足更严格的离线证据协议准备，**不满足完整判分 smoke 或真实成功率评估的代码前置条件**。环境-only smoke 也需要单独授权和相应运行时适配。本轮结束即停止，不启动下一阶段。

本轮修改范围为必要的 BeautifulSoup Python 模块、相关离线测试及本设计新文件；公共 runner.py、Scrapy 入口、Offline Agent、原始快照/Oracle、历史 runs/results、预算、锁文件、.gitattributes 不修改。原有未提交工作保留。
