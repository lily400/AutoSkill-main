# Harbor / Terminus-2：P0 接入与 P1 真实 Agent 准备

本模块建立“冻结来源 → 已有 canonical Skill → 下游环境 → 确定性判分”的测量基础设施。技能生成仍由现有 `degradation_lab` 调用原版 Anything2Skill；这里不重新生成技能，也不修改官方算法。

唯一任务是 `git-restore-explicit-source-both-v1`。P0 检查继续禁止模型执行；P1 已完成 A0/A1/Gold 的真实初始化与请求前停止探针，付费推理仍等待用户批准。

P1 最终零模型验收 `p1-ready-008` 三组 PASS：A1 首次请求包含全部 14 份索引，受控终端读取 14/14，三组使用同一实测镜像 ID。受控读取不代表模型自主读取。详见 [P1 准备报告、成本与待批准命令](docs/p1_preparation_report.md)。

```powershell
# 仅做零模型准备；使用新的唯一 run-id，不会调用付费模型。
docker exec harbor-p0-control-20261018 python -B scripts/lab.py downstream-prepare --run-id p1-<unique-id>
```

该入口生成官方 Harbor TrialConfig 并复用原生 Trial；批准后才用官方 `harbor trials start --config` 各执行一次。P1 模型/预算见 `configs/p1_smoke.json`，不改变 `runner.lock.json` 的 P0 禁推理设置。

当前 Docker 实机验收已通过：Harbor 0.24.0 固定提交、92 个冻结依赖、14 份 Skill 容器加载与发现、6 个原生 separate verifier 正反例。Windows 原生依赖安装受 MSVC 缺失影响，已改用 Linux 控制容器。详见 [完整实机报告和命令](docs/docker_validation_2026-10-18.md)。

在当前 Windows 主机复用已安装环境：

```powershell
docker exec harbor-p0-control-20261018 python -B scripts/lab.py downstream-check --section all
```

## 运行

在研究主目录 `degradation_failure_lab/` 下使用 Python >=3.12：

```powershell
python -B scripts/lab.py downstream-check --section all
python -B scripts/lab.py downstream-check --section skills
python -B scripts/lab.py downstream-check --section oracle
python -B scripts/lab.py downstream-check --section harbor
```

每次创建新的 `runs/downstream/git-restore-explicit-source-both-v1/p0-<id>/`，不覆盖历史运行。`--run-id p0-<unique-id>` 可显式命名。返回码：0=PASS，1=FAIL，2=BLOCKED。检查某一子项时仍记录环境检查；子项 PASS 不会消除环境 BLOCKED。

查看 `result.json`、`preflight.json`、`skills.json`、`available_skills.xml`、`oracle.json` 和各案例的 `oracle-result.json`。`success=null` 表示本轮没有模型任务成功率；正反例的成功状态在各 Oracle 记录内单独保存。

## 版本及来源

- Harbor 固定提交 `2de4605b9404eada7d341388291e6e469c90330b`，该源码声明版本 `0.24.0`、Python >=3.12。
- Terminus-2 使用该提交的官方方法；离线方法探针的 PyYAML 固定为 `6.0.3`。
- 配置和依赖文件 SHA 位于 `configs/runner.lock.json`。外部文件放在研究目录的 `.external/harbor-full/`，不进入研究源码目录，也不提交整个 Harbor 仓库。
- 现有 Git 生成运行为 `r18307cee4f4c`。直接读取它的注册结果、冻结哈希和 14 个 canonical 目录；不复制来源文档，不生成替代技能。

完整固定源码和依赖现已安装在 Linux 控制环境；安装身份、源码和 uv.lock 均已核验。宿主方法探针仍使用 `official_probe_class`，容器检查则导入真实 Harbor 包，调用官方 `DockerEnvironment` 和 Terminus-2 发现方法。模型客户端不初始化。

## 换行与文件完整性

原文件保持原始字节。`terminus_compat.CompatibleTerminus2` 仅在调用官方 frontmatter 解析器之前，对内存文本执行 `replace('\r\n', '\n').replace('\r', '\n')`。LF、CRLF、CRCRLF 都有测试，额外 frontmatter 字段、中文、正文和磁盘文件不改写。

安装目录使用 canonical Skill UUID；映射保存在 `skills.json`。每个文件逐项对照生成运行的冻结清单，随后核对 staged/installed 文件集合及哈希，最后核对完整发现 ID 集合。不会用数量相同代替身份校验。远程安装函数使用官方 `upload_file` 传 tar，再解包和复核，以绕开 Windows `upload_dir` 对脚本换行的转换；该远程路径已由真实 Docker 安装和逐文件 SHA-256 检查验证。

## Git Oracle

fixture 使用独立新目录、空 Git template、白名单进程环境和固定提交时间。A、HEAD、index、worktree 的目标内容分别为 V1/V2/V3/V4；另有一个已修改 tracked 文件及 untracked 哨兵。

Oracle 直接读取最终 worktree、Git index v2 和 `.git` 元数据，比较目标字节/blob/mode、所有 refs、无关文件和额外副作用。它不在 Agent 仓库运行 Git，不执行配置、hooks 或脚本。可信初态保存在仓库之外；separate verifier 从自己的可信代码重新构建基准，不读取 Agent 自报 reward 或 expected 文件。

Harbor 原生 artifact 声明传递完整 `/work/repo`，包含隐藏 `.git`。单机 tar 往返测试不等于 Harbor artifact 传输测试。原生 separate verifier 的正解、错误来源、仅工作树、仅索引、删除哨兵和空操作探针，在固定安装身份与 Linux Docker 均通过时才会运行；此分支使用官方 `oracle` Agent 执行参考脚本，不涉及模型。

## 补齐完整运行环境

以下为固定源码的部署方式；本轮已在 Linux 控制容器执行冻结安装，实际 Docker 命令见实机报告：

```bash
# 从研究主目录执行，保留现有 .external 源码子集；使用新的完整 checkout 目录。
git clone https://github.com/harbor-framework/harbor .external/harbor-full
git -C .external/harbor-full checkout 2de4605b9404eada7d341388291e6e469c90330b
# 在 checkout 内用 uv 依据同提交的 uv.lock 建立独立环境。
cd .external/harbor-full
uv sync --frozen --no-dev
```

在该环境中调用研究入口，并保证 Harbor 安装的 `direct_url.json` 或 editable checkout 身份能对应固定提交。Docker 镜像 digest、固定 Git 包、真实容器 Skill 检查及 separate verifier 已验证。再次运行须使用新的运行 ID。

## 测试和报告

下游测试在 `../tests/test_downstream.py`，Linux 12/12 通过。完整回归命令为 `python -B -m unittest discover -s tests -v`。旧测试依赖官方源码路径和较短的 Windows 临时目录；最终记录的运行器已设置这两项，但保留了旧测试中的案例数量断言失败。Windows 跳过的符号链接测试已在 Linux 实测通过。

详见 [架构与目录审计](docs/architecture.md)、[实际验收报告](docs/validation_report.md)、[逐文件变更清单](docs/change_list.md)。下一数据集只应增加任务环境、任务适配和专用 Oracle，继续复用现有来源管理、Skill 安装、Harbor 调度与日志协议。
