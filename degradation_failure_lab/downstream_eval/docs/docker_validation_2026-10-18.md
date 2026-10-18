# Docker 实机验收（2026-10-18）

本轮请求的零模型容器验收已完成，最终 `p0-docker-acceptance-003/result.json` 的 `infra_status=PASS`。
Harbor 安装在 Linux 控制容器中，继续使用现有 `scripts/lab.py downstream-check`、Skill 安装器、任务和 Oracle；没有重新创建 Runner，也没有修改原版 Anything2Skill。没有调用大模型或生成退化文档。

## 实际结果

| 项目 | 结果 | 证据 |
|---|---|---|
| Docker Desktop / Engine | PASS：4.95.0 / 29.8.2，linux/amd64 | `docker-version.stdout.log` |
| WSL2 | PASS：docker-desktop、WSL 3.0.3、内核 6.18.54.1-microsoft-standard-WSL2 | `wsl-list-final.stdout.log`、`wsl-uname.stdout.log` |
| Linux 容器 | PASS：固定 Python 3.13.9 镜像，断网冒烟实际运行 | `linux-smoke.stdout.log` |
| Harbor / Terminus-2 | PASS：0.24.0，提交 `2de4605b9404eada7d341388291e6e469c90330b` | `installation.json` |
| 冻结依赖 | PASS：92 个已安装包的版本均属于同提交 uv.lock，uv pip check 通过 | `installation.json`、`dependency-check.stderr.log` |
| Git Skill | PASS：14/14，原始/staged/容器文件集合和 SHA-256 一致，解析与发现 ID、name、description 全一致 | 最终运行 `skills.json`、`container_available_skills.xml` |
| 独立 Oracle | PASS：18 类状态重复 2 次，共 36/36 符合预期 | 最终运行 `oracle.json` |
| Harbor separate verifier | PASS：下表六例；每例存在完整 9 项断言、隐藏 .git 传输和原生 separate 记录 | 最终运行 `harbor.json`、`harbor_trials/*/*/result.json` |
| Linux 下游测试 | PASS：12/12，包含符号链接拒绝 | `linux-downstream-tests.stderr.log` |
| Windows 完整回归 | 28/30 通过，1 个既有失败、1 个权限跳过，无新错误 | `regression-final.json` |
| 原始文件保护 | PASS：265 个官方文件、473 个 Git 生成运行文件、2019 个旧研究文件哈希不变 | `protected-after.json` |

## 原生 separate verifier 正反例

| 操作 | 实际 reward | 测试结果 |
|---|---|---|
| correct | 1.0 | PASS |
| from_head | 0.0 | PASS |
| worktree_only | 0.0 | PASS |
| index_only | 0.0 | PASS |
| delete_sentinel | 0.0 | PASS |
| noop | 0.0 | PASS |

`correct` 的 9 项状态断言全真。错误来源、仅工作树、仅索引分别触发预期目标断言；删除哨兵触发 `untracked_sentinel_preserved=false`，证明删除经过实际 artifact 传输仍能被发现。五个错误案例的 Oracle `success=false`，不是基础设施异常导致的伪零分；每例 `exception_info=null`、原生 `verifier_environment_mode=separate`。

## 固定版本与无损性

完整 checkout 位于 `.external/harbor-full/`，HEAD 和全部已取样的 12 个源码 blob 与原锁一致；`uv.lock` Git blob 为 `c4522d5d4c6d1b16a9a6c397c535bb565be27b91`，SHA-256 为 `e7be66e217ac57a396775d8954d1ca69dbd4e00e33dd56cfd36d60cf9d59f7f5`。执行 `uv sync --frozen --no-dev`，没有解析或安装 Harbor latest。uv 固定 0.8.24。

基础镜像固定 `python:3.13.9-slim-bookworm@sha256:b685a4fa58bb19d1814d78a1ec0f0208f351452724f78b20212c984d6e124a34`；Git deb 固定 `1:2.39.5-0+deb12u2`。Docker CLI、uv、官方内核探针及网络 sidecar 的基础镜像 digest 已记入 `runner.lock.json`。本机控制镜像固定标签 `harbor-p0-control:2de4605-uv0824-py3139`，镜像 ID 也写入锁。

Skill 包来自现有运行 `r18307cee4f4c`，使用 UUID 目录。通过官方 `DockerEnvironment.upload_file` 上传 tar，容器解包后逐文件校验。实际发现执行已安装官方 `Terminus2._build_skills_section`；兼容类仅在内存中归一化换行。Terminus-2 构造器和模型客户端没有初始化；索引通过不表示大模型读取或遵循了 Skill。

## 真实失败及修复

1. Windows 原生冻结安装进入 `litellm==1.93.0` Rust 构建，失败于缺少 MSVC `link.exe`。未换依赖版本，改用 Linux wheel；该失败日志完整保留。
2. 首次 apt HTTP 下载返回 502。两个任务 Dockerfile 只改用 HTTPS 和有限重试，固定 Git 包保持不变，镜像已成功构建。
3. 历史生成路径使用 Windows 分隔符，Linux 读取注册结果失败。共享 `artifacts.load_run` 仅增加分隔符归一化后取 basename，仍使用已有路径边界检查。新增回归先失败、后通过。
4. Harbor 内核能力探针第一次拉取镜像超过其 30 秒限时，误判 no-network 不可用。显式拉取同一官方 digest 后，真实探针输出 `CONFIG_NFT_FIB_INET=m`；保持任务 `network_mode=no-network`，未放宽网络策略或修改 Harbor 源码。

历史运行 `p0-docker-acceptance-001/002` 的失败保留；最终判断使用 `003`。

## 实际命令与复用入口

完整执行 argv、工作目录、返回码及 stdout/stderr：

- [可读命令清单](../../runs/downstream/git-restore-explicit-source-both-v1/p0-docker-20261018/commands.md)
- [机器可读命令日志](../../runs/downstream/git-restore-explicit-source-both-v1/p0-docker-20261018/commands.jsonl)
- [最终验收结果](../../runs/downstream/git-restore-explicit-source-both-v1/p0-docker-acceptance-003/result.json)

本轮实际入口：

```powershell
docker exec harbor-p0-control-20261018 python -B scripts/lab.py downstream-check --section all --run-id p0-docker-acceptance-003
docker exec harbor-p0-control-20261018 uv pip check --python /opt/harbor-venv/bin/python
docker exec harbor-p0-control-20261018 python -B -m unittest discover -s tests -p test_downstream.py -v
```

再次检查时去掉 `--run-id` 或使用新的 ID，避免覆盖证据。控制容器及独立依赖卷保留，可直接复用；若已停止，先 `docker start harbor-p0-control-20261018`。研究目录按 Docker Desktop 的 Linux 宿主路径挂载，以使原生 sibling 容器能正确读写 artifact 和日志，挂载已实际验证。

## 剩余问题与范围

本轮要求的 Linux 零模型检查无剩余阻断。Windows 原生安装仍缺 MSVC；已安装的 Linux 环境不受此项影响。旧 `tests/test_framework.py:94` 仍只允许一个案例，而实际已有五个，故全量回归保留该失败，未改旧断言。Windows 符号链接权限跳过已由 Linux 对应测试通过补齐。

模型调用数为 0；没有运行技能生成、A0/A1/Gold、退化文档构造或模型成功率评测。
