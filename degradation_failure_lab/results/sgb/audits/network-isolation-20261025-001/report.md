# 公共 Agent 网络隔离修复与零模型验收

- 日期：2026-10-25
- 基线：AutoSkill-main / master / e00abbf8f28a0f47a352968783889904d9545c2a
- 工作区：D:/AS/AutoSkill-main/degradation_failure_lab
- 结论：**NETWORK ADMISSION PASS**，限本报告的 Linux Docker 运行时、镜像与公共入口。
- 修改已保留在本地工作树，未提交、未推送。
- **没有启动 Agent、没有调用模型 API、没有生成 Skill、没有执行下游任务、没有修改 Anything2Skill。**
- 可以开始 Scrapy041 的任务适配；本报告不代表其任务环境或 Oracle 已经接入完成。

## 真实调用链与修复位置

当前公共入口：
`downstream_eval/sgb/runner.py::trial_config`
→ Harbor `TrialConfig.environment.extra_docker_compose`
→ `Trial 的环境初始化 / EnvironmentFactory.create_environment_from_config`
→ `DockerEnvironment._user_compose_paths / _egress_controlled_service_names`
→ Docker Compose 的真实 main 容器配置。

Harbor 尊重显式设置的 `network_mode`，不再把 main 放入 sidecar 的网络命名空间。保留固定 Harbor 上游代码不变。

运行前检查：
`ScrapyTerminus2.setup`
→ `P1ObservationMixin.setup`
→ **公共 verify_environment_network 检查**
→ 检查通过后才调用原生 setup。测试同时覆盖失败时禁止进入原生 setup。

仅修改四个已有文件：
1. `downstream_eval/sgb/runner.py`：公共环境配置加入隔离 overlay。
2. `downstream_eval/integration/p1_observer.py`：在原生 setup 前执行真实网络准入并记录证据。
3. `downstream_eval/sgb/scrapy_agent.py`：删除旧的 sidecar TCP 文本判定，保留任务文件隔离检查。
4. `tests/test_sgb_runner.py`：验证公共配置包含统一隔离策略。

新增五个直接相关文件：
- `downstream_eval/integration/network-none.yaml`
- `downstream_eval/integration/network_isolation.py`
- `downstream_eval/integration/network_probe.py`
- `scripts/sgb/verify_network_isolation.py`
- `tests/test_network_isolation.py`

## 修复内容

main 容器固定：
- Docker `network_mode: none`，没有外部网卡、地址或路由；
- DNS 明确配置到本容器 `127.0.0.1`；
- 丢弃 NET_ADMIN、NET_RAW、SYS_ADMIN；
- 设置 no-new-privileges；
- 不改 sidecar 上游规则。sidecar 仍可由 Harbor 创建，但 main 与它不共享网络命名空间。

准入不仅检查设置名称：
- Docker inspect 的实际网络、网关、权限；
- 容器内真实接口、IPv4/IPv6 路由、resolver；
- CapEff、CapPrm、CapBnd、NoNewPrivs；
- 实际双栈 TCP、UDP、DNS/53、ICMP、raw socket；
- 本地 DNS 和 Docker 内置 DNS 地址 127.0.0.11 的 TCP/UDP；
- packet 和 vsock 套接字；
- 本地 loopback 正对照。

外部目标的超时不算通过，必须得到内核拒绝。DNS loopback 的超时/拒绝只有与无外部接口、无路由、无网络管理权限等结构证据共同成立才接受。异常、缺失证据、未知错误均不能得到 PASS。

## 固定运行环境

- Docker Engine 29.8.2，Docker Desktop 4.95.0；
- Linux 内核：6.18.54.1-microsoft-standard-WSL2；
- Python 3.13.9，项目已有 Harbor 运行时；
- 运行时镜像：harbor-p0-control:2de4605-uv0824-py3139；
- 工作负载镜像：scrapy024-agent:s24r005；
- 工作负载实际 image ID：sha256:c928e232c35008c42b22727ecd2fe39ed79fe9cb36ebddca669daef309d6b4e4；
- Harbor 固定源码及网络策略哈希记录于 code-manifest.json，未修改 .external 上游。
- 历史控制容器没有启动。本轮使用新建的、无网络控制容器；只读挂载源码和 venv，只有本次证据目录可写。
- Docker socket 仅提供给可信验收控制器，未提供给 main 探针容器。

## 验收结果

最终有效尝试：`attempt-002`，**PASS**。

验收直接调用 Harbor 的 EnvironmentFactory，使用与公共 runner 相同的 environment_config；没有导入或构造 Agent，也没有调用 Trial/模型 SDK。导入保护器拒绝 harbor.agents、harbor.trial.trial、openai 和 litellm。

| 通道 | 正对照 | 隔离容器实测 |
|---|---|---|
| IPv4 TCP/8080、TCP/53、UDP/53、UDP/33434 | 内部回显服务均成功 | ENETUNREACH |
| IPv6 TCP/8080、TCP/53、UDP/53、UDP/33434 | 内部回显服务均成功 | ENETUNREACH |
| ICMP、ICMPv6 datagram | 内部目标均收到 Echo 响应 | ENETUNREACH |
| IPv4/IPv6 raw socket | 权限限制独立验证 | EPERM |
| Docker DNS 127.0.0.11 TCP/UDP | 已连接内部网络的对照均可访问 | TCP 拒绝，UDP 无响应；同时确认只有 lo 且无外部路由 |
| 本地 DNS 127.0.0.1 TCP/UDP | 无服务，不作为远程正对照 | TCP 拒绝，UDP 无响应 |
| AF_PACKET / AF_VSOCK | 不需要向宿主发送数据 | 创建套接字即 EPERM |
| 本容器 loopback | 成功 | 成功，保留本地进程通信 |

正对照网络使用 Docker `--internal` 双栈网络，目标为 198.18.25.2 与 fd7b:abc:25::2，不依赖互联网服务是否在线。DNS/53 远程正对照验证传输通道；Docker 内置 DNS 另使用合法查询探针。

三个检查阶段均通过：
1. main 启动后；
2. 将 Harbor sidecar 策略暂时切换为 public 后；
3. 恢复 no-network 后。

因此，sidecar 的策略切换不能重新连接 main。已连接内部网络的正对照容器被同一准入检查正确拒绝。

所有本轮临时工作负载、回显服务、控制容器及网络已清理。未清理或改变历史容器、镜像、网络和运行记录。

## 测试和失败记录

- 最终相关测试：**50 项，通过；0 失败、0 错误、0 跳过**。
- 范围：网络准入、公共 runner、任务契约、Scrapy024 的非 Agent SDK 测试。
- 特意排除会实例化 Agent 的 SDK 测试，遵守本轮不启动 Agent 的边界。
- `git diff --check`：通过。

保留的中间失败：
- Windows Python 运行公共测试时缺少 tomllib，两个测试模块导入失败；切换到项目固定 Linux Python 3.13 后通过，没有修改项目兼容逻辑。
- attempt-001：网络负例均阻断，但 Docker inspect 返回 CAP_NET_ADMIN 等带 CAP_ 前缀的名称，检查器保守拒绝。规范化名称并增加回归测试后重新验收；没有将首次失败改成 PASS。

## 历史保护

`history-before.json` 冻结 runs 下的历史记录及 AutoSkill4Doc Python 源码。
`history-proof.json` 最终复核：
- 保护文件数 12878；
- 12878 个哈希完全一致；
- 0 修改、0 丢失、0 新增保护目录文件。

Git 状态也未显示历史任务、Oracle、Skill、报告或上游生成算法发生变化。旧六次试验的隔离结论不会因为本轮修复而被追溯改写。

## 证据导航

- 最终判定：attempt-002/result.json
- 真实负例与内核状态：attempt-002/isolated-network.json
- 双栈正对照：attempt-002/positive-control.json
- 正对照应拒绝证明：attempt-002/connected-control-rejection.json
- 实际 Compose 合并结果：attempt-002/effective-compose-network.json
- sidecar 改为 public 后：attempt-002/after-sidecar-public.json
- 恢复策略后：attempt-002/after-sidecar-restore.json
- 最终 50 项测试：unit-tests-linux-verified.log
- 历史不变证明：history-proof.json
- 代码与依赖哈希：code-manifest.json
- Docker 版本：docker-version.json
- 原始失败：unit-tests.log、attempt-001/result.json、attempt-001/failed-network.json

## 准入范围和下一步

当前公共入口在上述固定 Linux Docker 镜像/运行时下，已通过正式实验的**网络隔离这一项**准入条件。不是对所有 Docker 版本或未来任务镜像的无限外推；更换镜像、运行时、compose 或 Agent 接入路径时须重新验收，每次 P1 setup 也会再次执行准入检查。

该结论不覆盖内核/容器运行时漏洞、可信宿主主动修改容器、其他文件隔离或 Oracle 的任务适配；本轮未发现仍可用的被测出站通道。未用启动 Agent 或模型实验补充证明，也不声称历史运行已经无泄露。

**下一步可以开始 Scrapy041 的任务适配，仍须完成它自身的环境与独立 Oracle 验收。本轮到此停止。**
