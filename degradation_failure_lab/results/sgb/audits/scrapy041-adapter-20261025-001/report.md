# Scrapy041 任务适配与零模型验收

结论：**READY FOR CLEAN RUN**。这里表示任务适配和零模型验收已经通过，可以进入下一阶段的 Clean 实验准备与执行；本轮没有启动真实 Agent、调用模型 API、生成 Skill 或开展退化实验。

日期：2026-10-25。仓库基线为 master / e00abbf8f28a0f47a352968783889904d9545c2a。沿用上轮尚未提交的公共网络隔离修复，本轮代码也保留在本地工作树，未提交、未推送。

## 1. 真实资产与初始状态

任务键 t-8d3bed6236cf；源文档包 b-083578378ffb0792；SkillGenBench 固定提交 5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d。

| 源文件 | 原始 SHA-256 |
|---|---|
| offsite.md | dad43df16d07e2c3550978ddc3baffafb5721dc23e060fdd58028e4d8a0216b8 |
| downloader-middleware.md | 491f737b9d4743ec7b0e943f5be719969f0bb390aac55f25d9ada1d37060b10c |
| request-response.md | 9f6d99ec9d95647cc3e949c54791022b33f4409787063b1e8be292561aa949b4 |
| spider-middleware.md | 3772c49ba00a9fe46b78d1092b9fb2b47d0589c80296a04a7e407757eaa8e04a |

四份源文件、对应来源清单和 11 项官方任务资产逐一核验通过，见 asset-verification.json。原始指令与 eval.py 已按原始字节复制到任务目录：

- instruction.md：983cf756f028efbed1c6c84f62358f2fe404fd5a71d54d60370ebd2aa02cf27e；
- scorer/oracle/eval.py：6b3c519e661c41f3650bb8fa33b64edbd709592a42b1f75b577f7ac4fc64c44b。

初始 adapter.json 确实为 METADATA_ONLY，没有将注册元数据或离线夹具当作真实运行。目标规则为：保持 allowed_domains=["example.com"]，目标请求使用 meta["allow_offsite"]=True；dont_filter=True 虽能影响 Scrapy 中间件，但不满足本任务的 metadata 限定。

## 2. 复用范围与新增文件

直接复用：
- downstream_eval/sgb/runner.py：ExecutionConfig、原生配置、批次协调、提交查找及冻结检查；
- downstream_eval/integration/request_budget.py：持久预算 Ledger 和计量机制；
- CompatibleTerminus2 / P1ObservationMixin：原生 Agent 循环、技能安装/读取观察、请求计量及运行前网络准入；
- network-none.yaml、network_isolation.py、network_probe.py：已验收的公共网络隔离；
- scrapy024.native_trial、scrapy024.body_exposure：未来真实运行入口及正文暴露分析；本轮没有调用 native_trial；
- Scrapy024 原有 preflight.py 中的 Docker 工具类：只复用容器执行工具，以私有模块实例指定 041 评分镜像；没有调用 024 的布尔评分桥接，也没有修改其文件；
- Harbor EnvironmentFactory、upload_file、download_file：本轮真实环境和真实提交传输。

新增的任务专用实现：
- downstream_eval/sgb/task_adapters/scrapy041/{adapter.py,agent.py,scoring.py,__init__.py}
- downstream_eval/tasks/sgb/code_doc/scrapy-task-041 下的 instruction.md、task.original.toml、task.toml、runtime-note.md、runtime.lock.json、environment/Dockerfile
- 同目录 scorer/{worker.py,oracle_bridge.py,source_manifest.json,Dockerfile,requirements.lock,oracle/eval.py,oracle/test.original.sh}
- scripts/sgb/verify_scrapy041.py
- tests/test_scrapy041.py
- tests/fixtures/sgb/scrapy-task-041/candidates.json

修改已有文件仅涉及 041 adapter.json、tasks.jsonl 的 041 单行、configs/datasets/sgb.json 的注册表校验和。其他 186 行保持原始字节一致。没有新增公共抽象，没有修改生成算法，也没有改动上轮公共网络修复。

## 3. 运行时版本差异及必要处理

发现官方 Dockerfile.claude 指定 Scrapy 2.12.0，但其 OffsiteMiddleware 源码没有处理 allow_offsite；发布材料中的 offsite.md 包含这一分支。

041 专用候选/评分运行时因此固定为 **Scrapy 2.13.0**，核实其源码支持该键，再实际运行直接中间件方法检查。原始 10 项 Oracle 测试不变。该变化是本任务的依赖适配，不能称为完全复现原始 2.12.0 容器。

- 38 个 wheel 的版本和 SHA-256 已固定；依赖来自 PyPI，镜像构建使用 --network none 和 --require-hashes。
- Python 3.13.9、pytest 8.4.1。
- 评分镜像：sgb-scrapy041-scorer:20261025-001-compatible。
- 镜像 ID：sha256:0e2250218ed7fa4b8d56bdd47309278547f63b47d48c678ea27eaeea3523d310。
- Agent 工作负载沿用原冻结镜像 sha256:c928e232c35008c42b22727ecd2fe39ed79fe9cb36ebddca669daef309d6b4e4，没有安装 Scrapy，因此 Agent 无法直接读取其实现源码。
- 构建 wheel 缓存在 .external/scrapy041-runtime-20261025-001-compatible，是本地忽略目录；可复核的锁文件在任务目录，下载和构建日志在本审计目录。

原始 instruction.md 保持不变。runtime-note.md 仅补充实际目录、私有测试不可用、Skill 索引路径及评分依赖版本；未来两种实验条件使用同一说明，没有补充目标 metadata 键。

## 4. 原始 Oracle 如何独立执行

1. 通过真实 Harbor 文件传输导出 /workspace/agent_output.py，控制器核对导出前后哈希。
2. 控制器在新评分目录冻结提交；只将该文件及通用对象采集 worker.py 挂载到候选容器。
3. 候选容器使用真实 Scrapy。为原 Oracle 的每次模块加载收集独立对象观测，区分仅导入、类发现、allowed_domains 与请求采集。
4. 候选容器不能访问 Oracle、桥接插件、观测结果目录、评分输出、隐藏测试、Docker socket 或源文档。容器非 root、根文件系统只读、无网络，提交和 worker 文件也只读。
5. 候选容器停止后，控制器创建绑定 candidate_sha256 与 oracle_sha256 的 JSON 观测包。
6. 另一个可信容器执行原始 eval.py 的 10 个测试。桥接仅替换 load_agent_module，重建数据代理；保留原始 find_spiders、collect_requests、全部断言以及针对真实提交字节的源码检查。
7. 可信评分进程不导入候选文件。数据使用有限 JSON 类型，不采用 pickle 或对候选内容执行 eval。
8. 最终同时检查 JUnit、完整测试数、桥接调用序列、候选/Oracle 哈希和“候选模块未被评分进程导入”。无效输出、缺失提交、哈希不符、超时等不会变成成功。

保留了关键区别：bool True 与字符串/数字不混同；tuple 与 list 不混同；构造异常不会被掩盖；生成器中途抛异常时保留原 Oracle 丢弃部分列表的行为；多个目标请求全部需要满足原有逐请求断言。

容器交互、stdout/stderr、超时、挂载、网络检查、JSON 观测、JUnit 和结果均位于各 scores/<候选名>/ 目录，可按候选哈希追溯。源码只读与答案不可访问分别验证，没有把只读当作访问隔离。

## 5. 真实零模型验收结果

有效运行：attempt-001/acceptance.json，**PASS**。17 项检查均符合预期：

| 候选或错误场景 | 原始 Oracle 得分/状态 | 验证内容 |
|---|---|---|
| correct | 10/10 | 正确 Spider、域名列表、目标 URL 和布尔 metadata |
| missing_meta | 8/10 | 缺失目标 metadata 被两项断言拒绝 |
| dont_filter_only | 8/10 | 不能用 dont_filter 替代 metadata |
| wrong_domains | 9/10 | 擅自加入 other.com 被拒绝 |
| middleware_modified | 9/10 | 原始 AST 中间件限制生效 |
| string_true | 8/10 | 字符串 "True" 不能冒充布尔 True |
| boundary_attempts | 10/10 | 候选断言 Oracle/评分目录不可见，写 worker 和 Oracle 失败，然后正常完成任务 |
| syntax_error | 2/10 | 语法错误不会成功 |
| import_exception | 3/10 | 导入异常按原始断言失败 |
| constructor_exception | 6/10 | 构造异常导致请求相关断言失败 |
| partial_generator_error | 7/10 | 保留原始 collect_requests 的异常处理语义 |
| mixed_request_metadata | 9/10 | 不能只保留一个正确请求而漏掉同 URL 的错误请求 |
| timeout | candidate_timeout | 真实候选进程超时，非成功、非正常任务得分 |
| invalid_stdout | candidate_protocol_error | 额外低层输出破坏协议时拒绝 |
| hash_mismatch | submission_hash_mismatch | 哈希不一致在候选执行前拒绝 |
| missing_file | invalid_submission | 缺失候选拒绝 |
| scorer_timeout | scorer_timeout | 真实评分器截止时间触发，不误判成功 |

语法/导入/构造错误是候选问题；超时、协议错误和绑定失败单独记录，不能冒充有效的模型效果样本。

正确候选会在其执行容器写入 /tmp/scrapy041-candidate-marker。可信评分容器检查该标记不可见，且候选模块未被导入；boundary_attempts 也经过同一个独立评分路径。

## 6. 网络、测试与中间件边界

- 共 **30 份真实容器网络检查，全部 PASS**，包括 041 的 Harbor 工作区、候选、评分器及直接中间件诊断容器。
- 实际检查主机网络配置、接口、路由、resolver、能力权限及连通性负例。并非只检查 no-network 文本。
- IPv4/IPv6 TCP、UDP、DNS、ICMP/ICMPv6 以及 raw/packet/vsock 通道受阻；本地 loopback 正对照正常。
- 全部临时验收容器已清理。
- **60 项相关离线回归测试通过，0 失败、0 错误、0 跳过**；包括 041、公共网络、runner、任务契约及 024 非 Agent SDK 测试。会实例化 Agent 的 SDK 测试明确排除。
- 完整 187 条数据注册校验 PASS。
- git diff --check 通过。

单独的真实 Scrapy 中间件方法诊断：
- meta["allow_offsite"]=True：ALLOWED；
- 缺失该 metadata：REJECTED；
- dont_filter=True：ALLOWED，但仍被官方任务 Oracle 拒绝，因为任务指定 metadata 机制。

该诊断调用真实 OffsiteMiddleware.process_request，没有发起网络请求，没有运行爬虫引擎；**真实爬取与网络拦截行为为 UNKNOWN**。诊断结果没有加入或替换官方 10 项得分。

## 7. 历史保护与可追溯性

history-proof.json：**13375 个受保护文件全部哈希一致，0 修改、0 丢失**。范围包括历史 runs、完整 024 任务包、上轮网络审计和 AutoSkill4Doc 文件。上轮网络修复的 code-manifest 也逐项匹配，没有变化。

code-manifest.json 记录本轮 23 个任务/代码/注册文件的最终指纹。容器验收后仅清理了控制器代码中的未使用导入；任务执行资产（原始 Oracle、worker、bridge、镜像锁等）没有变化，最终回归测试随后通过。

保留的初始测试问题：第一次在评分专用镜像导入控制器适配测试，因该镜像没有 httpx 而失败。改用已有 Harbor 控制器运行时测试后通过；没有为评分镜像添加无关控制器依赖。详见 unit-tests-initial.log 与 unit-tests-controller.log。

注册层区分：
- adapter_readiness：READY_FOR_CLEAN_RUN；
- runtime：ZERO_MODEL_CONTAINER_VERIFIED；
- Oracle：ISOLATED_ORIGINAL_TESTS_VERIFIED；
- calibration：ZERO_MODEL_ONLY；
- 真实 Agent 和 Skill 生成：NOT_RUN；
- execution_status：READY_FOR_CLEAN_PREPARATION；
- 保留 experiment_not_frozen 门槛，避免把零模型配置当成正式模型运行授权。

attempt-001/configuration 内的 NO_MODEL_ZERO_CALLS / 零预算配置仅供本次验收，不能直接充当真实模型实验配置。

## 8. 尚未验证与下一阶段

**UNKNOWN / NOT_RUN**：
- 真实 Agent 在 041 上的表现；
- 真实生成的 Clean Skill 质量、安装后的模型正文读取与效果；
- 真实爬取和网络拦截；
- 任意自省代码、依赖跨测试进程全局状态程序的完整等价性；本次对象桥接验证覆盖普通 Spider/Request 数据接口及上表边界，不宣称通用 Python 程序等价证明。

原 Oracle 本身的范围仍有限：中间件禁止检查主要依赖特定 AST 字符串；域名匹配、请求匹配等断言也没有证明完整爬虫行为。本轮没有擅自增强、降低或替换这些评分断言。

**下一阶段可以开始 Scrapy041 Clean 实验**：按新实验 ID 冻结模型、预算、源文档映射、实际生成的 Skill 包及执行清单，再依据用户指令运行。这里属于正式实验的常规准备，不是尚未解决的任务适配整改。

本轮已停止，没有自动调用 paid_batch、真实 Agent、模型 API 或 Skill 生成。

## 证据导航

- attempt-001/acceptance.json：总验收与全部结果；
- attempt-001/scores/<名称>/：候选快照、命令、网络和挂载检查、观测、JUnit、评分；
- attempt-001/exports/<名称>/receipt.json：Harbor 导出哈希；
- attempt-001/agent-environment-{network,boundary,mounts}.json：工作区隔离；
- attempt-001/middleware-diagnostic/result.json：独立的中间件方法诊断；
- unit-tests-final.log / unit-test-summary.json：60 项测试；
- registry-audit.json / registry-update.json：注册完整性及只改 041 的证明；
- asset-verification.json：19 项来源/任务文件核验；
- history-proof.json：历史和上轮网络代码未变；
- runtime-version-decision.json / compatible-wheel-manifest.json：版本差异与固定依赖；
- code-manifest.json：最终本轮源码与注册指纹。
