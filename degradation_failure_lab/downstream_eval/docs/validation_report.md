> 后续 Docker 实机验收已完成：见 [2026-10-18 实机报告](docker_validation_2026-10-18.md)。下文保留首次离线阶段记录。

# P0 实际验收报告（2026-10-18）

结论：宿主零模型 Skill 检查和独立 Git Oracle 已通过；完整 Harbor 安装、容器内技能接入及 separate verifier 运行仍为 BLOCKED。真实 Terminus-2 模型冒烟尚不具备条件。完整回归测试仍有一个原有失败，不能称全部测试通过。

最终证据目录：`runs/downstream/git-restore-explicit-source-both-v1/p0-acceptance-002/`。每个阶段有独立 JSON；完整矩阵见 `oracle.json`，原始控制台输出见 `command.stdout.log` 和 `unittest.log`。早期 `p0-validation-001`、`p0-validation-final`、`p0-acceptance-001` 保留为本轮调试记录，不覆盖或混入正式判定。

## 1. 环境与固定身份

- Git 根：`D:/AS/AutoSkill-main`；分支 `master`；HEAD `ace65737e8d0be08eda1c47d5a8e62f119989ded`。
- 宿主 Windows。`wsl --list --quiet` 返回未安装 WSL 的说明；未启动 Linux 发行版或 Docker 容器。
- 官方固定源码版本为 Harbor `0.24.0` / `2de4605b9404eada7d341388291e6e469c90330b`，不是 Harbor latest。完整依赖应以该提交的 `uv.lock` 为准；本机只有经过认证的源码子集和离线解析所需 PyYAML。

| 检查 | 状态 | 实际依据/原因 |
|---|---|---|
| python | PASS | 3.13.9 / packaged by Anaconda, Inc. / (main, Oct 21 2025, 19:09:58) [MSC v.1929 64 bit (AMD64)] |
| git | PASS | git version 2.53.0.windows.3 |
| docker | BLOCKED | Executable not found on host PATH |
| harbor | BLOCKED | Executable not found on host PATH |
| docker_linux_daemon | BLOCKED | Docker absent; containers not executed |
| pinned_source_subset | PASS | D:\AS\AutoSkill-main\degradation_failure_lab\.external\harbor-2de4605; method-only probes, package not installed |
| PyYAML | PASS | 6.0.3; expected 6.0.3 |
| installed_harbor_identity | BLOCKED | No installed Harbor distribution |
| host_platform | PASS | win32; not a Linux/Docker runtime |

固定文件的 Git blob SHA-1 与 SHA-256 逐项验证，身份清单见 `configs/runner.lock.json` 和 `.external/harbor-2de4605/provenance.json`。离线探针实际执行官方方法 AST，而非重写 frontmatter/索引算法；完整 Harbor import、TaskConfig 实例化和容器生命周期尚未通过。

### 下载与安装尝试

| 操作 | 实际结果 |
|---|---|
| 旧 partial Git clone 读取固定 pyproject blob | 触发 promisor fetch；连接 127.0.0.1 代理失败；旧缓存保持原样 |
| 普通进程直连 raw.githubusercontent.com | DNS getaddrinfo 失败 |
| 提权进程无代理直连同一固定文件 | WinError 10060 超时 |
| web 读取三个固定 raw URL | Cache miss |
| GitHub 只读连接器读取固定源码 | 成功；保存选定文件，核对服务器 blob SHA；没有创建远程资源 |
| pip download --no-deps --timeout 8 --retries 0 harbor==0.24.0 | 配置的清华镜像返回 no matching distribution；未安装 Harbor，不将版本号 wheel 等同固定 commit |

这不能笼统表述为“网络完全不可用”：GitHub 只读连接器可用，宿主 Git/HTTP/pip 的依赖取得路径未打通。完整 uv.lock 仅核得 blob 身份 `c4522d5d4c6d1b16a9a6c397c535bb565be27b91`，没有下载和执行 frozen 安装。

Dockerfile 配置了 `python:3.13.9-slim-bookworm` 和 `git=1:2.39.5-0+deb12u2`。这是待构建验证的版本约束；该 apt 包在当前源的可获取性、基础镜像 digest、实际 Linux Git/Python 版本均未验证，不能称完整容器依赖已冻结成功。

## 2. 现有 canonical 与来源复核

| 真实生成运行 | canonical 数量 | 字节换行复核 |
|---|---:|---|
| `runs/case001_qsv_select/clean/raecd75e08b34` | 4 | 全部普通 CRLF |
| `runs/case002_qsv_sort/clean/rd9ced750fa54` | 3 | 全部普通 CRLF |
| `runs/case003_docker_cp/clean/rab9a070dfa59` | 2 | 全部普通 CRLF |
| `runs/case004_git_restore/clean/r18307cee4f4c` | 14 | 全部普通 CRLF |
| `runs/case005_ripgrep_guide/clean/r64cee24fae18` | 24 | 全部普通 CRLF |

现有 canonical 合计 47 份，全量按 `read_bytes()` 计数重新核实为普通 CRLF；没有 CRCRLF 文件。早期终端打印出现的双 CR 来自输出转换，未作为磁盘事实写入结果。仅安装 Git 来源的 14 份；没有挑选已知正确技能，没有再生成 47 份技能。

Git 来源 ID：`git-restore-a52a24e03c8c`；来源提交 `a52a24e03c8c711f1d5e252fba78f9276908129b`；冻结原文 SHA-256 `2afb2f9183ad599a490c32fd174df66b0532abbe252887bc5c8b57d82a60f468`。

来源原文沿用 `data/manifests/git_restore.json` 指向的 `data/raw_sources/git/<commit>/git-restore.txt`。官方测试语义参照同一 Git 提交的 [t/t2070-restore.sh](https://github.com/git/git/blob/a52a24e03c8c711f1d5e252fba78f9276908129b/t/t2070-restore.sh)：分别检查 worktree/index/both 和默认 HEAD。取得文件 SHA-256 为 `441dd784ed3e27cc7997b7881c70a57a7e23ec986d90f3ace465115eae0b2b7d`。这是源码语义证据；没有运行 Git 上游完整 test-lib 测试套件。

### 无损安装、解析、索引

- 注册 ID、现有导出目录、canonical ID 集合交叉匹配；每个资源文件对照生成时保存的冻结哈希。
- 14 个独立 UUID 目录全部 staged 和 installed，所有文件字节、必要资产与 SHA 一致。实际 14 个包均只包含 SKILL.md；另以合成资源包测试 scripts/assets 的无损复制。
- 官方未修补 parser 对这 14 个 CRLF 文件均返回 None；内存换行兼容后全部解析，中文 name/description 正确。
- 官方 resolver 和官方 find/cat/索引方法实际执行，XML 中 14 个 location 对应完整 ID 集合，无覆盖、无丢失。
- `skills.json` 中 original/staged/installed 均是以研究目录为根的宿主相对路径；容器目标配置为 `/harbor/skills`，尚未在容器验证。

| Skill ID | 原始 SHA-256 | installed SHA-256 | 解析/发现 |
|---|---|---|---|
| `3810431b-3f7d-505a-86e2-a7fde1141964` | `610b8c7be02ad1cb6e9475458e67aa2d8ec26acdc194f54c2c059205b2b1e449` | `610b8c7be02ad1cb6e9475458e67aa2d8ec26acdc194f54c2c059205b2b1e449` | PASS / PASS |
| `44058e52-2d84-5119-a5fe-e2d4811e07a7` | `e0fbf829a46057efdca0cd8f229915147950512ee4a85bedc751fc8669ca517c` | `e0fbf829a46057efdca0cd8f229915147950512ee4a85bedc751fc8669ca517c` | PASS / PASS |
| `68365646-cd43-5640-9a09-7e236fcf0774` | `38360ba9f167a2ae94d4e3c95699c5607105a4e520d37e28f314a67e297a5f07` | `38360ba9f167a2ae94d4e3c95699c5607105a4e520d37e28f314a67e297a5f07` | PASS / PASS |
| `7147c9f5-6f4f-59d7-8f71-203e58032ac1` | `4514457e2c442403f07aa2a504149532b80d0fc234a42e819d2482ef1c147308` | `4514457e2c442403f07aa2a504149532b80d0fc234a42e819d2482ef1c147308` | PASS / PASS |
| `7b96215d-c31b-5095-aed4-9eaca3b18ffb` | `fc67e2fe66d008657fe9849bf1fc8f02cb9a072ca64ebf9f5976172f0394f873` | `fc67e2fe66d008657fe9849bf1fc8f02cb9a072ca64ebf9f5976172f0394f873` | PASS / PASS |
| `7dca97c1-ee41-5695-a22a-13c36e81bc3d` | `38adc6b00998ef1ccea758d5e1b453000718b550f791a8e62b2937b64455896d` | `38adc6b00998ef1ccea758d5e1b453000718b550f791a8e62b2937b64455896d` | PASS / PASS |
| `918e0187-7a71-5a49-9ff9-5352d0eb6e89` | `339257e7efb285e469d8bcf34e079d697ce22269d988d24ac9fc79c440e9b422` | `339257e7efb285e469d8bcf34e079d697ce22269d988d24ac9fc79c440e9b422` | PASS / PASS |
| `99f59c6f-5528-5ce9-9d2b-69222702e8d1` | `17090bd98aa140c0f26a5aa52e1391dfbb104f189ef428a9f18b27d86dafc876` | `17090bd98aa140c0f26a5aa52e1391dfbb104f189ef428a9f18b27d86dafc876` | PASS / PASS |
| `a2921234-8368-5718-a917-fb40db95ccd1` | `6647e2efee9f8dff2aef976b8d926d986754ddcfec4644a0855ec08b1a0b4c61` | `6647e2efee9f8dff2aef976b8d926d986754ddcfec4644a0855ec08b1a0b4c61` | PASS / PASS |
| `c0045ec2-f265-563d-a6ca-764403b3cef9` | `144850530c983aaa71f1b634b3c0db08769c4b08b153694c95bd980ea4ee2697` | `144850530c983aaa71f1b634b3c0db08769c4b08b153694c95bd980ea4ee2697` | PASS / PASS |
| `d472e6a7-8895-56cb-9014-cb75cc3540b3` | `7cc0cdfada01e52ce3687eba05bc8d5ec6b9948ec768a7cec25138d2bb6f6bf3` | `7cc0cdfada01e52ce3687eba05bc8d5ec6b9948ec768a7cec25138d2bb6f6bf3` | PASS / PASS |
| `ea0c6b32-c72a-5688-a8c1-26f398a892fc` | `eb6f99b0ffd85b43a2871779fd0ca3cc8ee2a0caccccf6761dc5629758c5f71e` | `eb6f99b0ffd85b43a2871779fd0ca3cc8ee2a0caccccf6761dc5629758c5f71e` | PASS / PASS |
| `fd6ef816-81a2-5586-afb6-35aa6f45c10c` | `58c608355c4151024bc23409b6d6ce7672fe97a4d4a65b092be6563aaf15ea7d` | `58c608355c4151024bc23409b6d6ce7672fe97a4d4a65b092be6563aaf15ea7d` | PASS / PASS |
| `feccf35d-9c79-5b75-90e3-6707ce898884` | `9ba93bb1fea5b65ef5fc06598de5ed7a4819e055a1ea9f59f77be422af14362f` | `9ba93bb1fea5b65ef5fc06598de5ed7a4819e055a1ea9f59f77be422af14362f` | PASS / PASS |

每条完整的 `source_id, skill_id, original_path, staged_path, installed_path, original_sha256, installed_sha256, frontmatter_status, discovery_status` 记录均保存在 `skills.json`，同时保存原始 metadata、换行计数和逐资产哈希。

兼容修补的影响范围仅是官方 parser 接收到的内存文本：`Terminus2._parse_skill_frontmatter(content.replace("\r\n", "\n").replace("\r", "\n"))`。原始文件和上游依赖源码未改写；LF/CRLF/CRCRLF、中文和额外 YAML 字段均有测试。额外字段不会被官方索引呈现，但完整原文件仍保留这些字段。格式拒绝没有记为生成质量错误。

| 验证层次 | 本轮结果 |
|---|---|
| 宿主文件无损安装 | PASS |
| 官方加载器方法解析 | PASS（加入内存换行兼容） |
| 官方方法生成完整可发现索引 | PASS（宿主真实 Bash find/cat） |
| 完整 Harbor 进程/容器内安装、Agent 初始 prompt 交付 | BLOCKED |
| 模型主动读取正文 | 未运行 |
| 模型遵循技能规则 | 未运行 |

## 3. 唯一 Git fixture 与独立 Oracle

任务 ID 为 `git-restore-explicit-source-both-v1`。环境是新建的隔离仓库，目标 `target.txt`，另有已修改 tracked 文件 `unrelated.txt` 和 untracked 哨兵 `sentinel.txt`。固定 Git 环境和空 template；使用 Git plumbing 构建，不继承用户 hooks、filter、凭证或 signing。

| 位置 | 内容 |
|---|---|
| 提交 A | `V1: old committed content\n` |
| 当前 HEAD | `V2: current HEAD content\n` |
| index | `V3: staged content\n` |
| worktree | `V4: working content\n` |

最终样本 commit A 为 `b789daa9d14180466bee09d946deae9606dbef1e`，HEAD 为 `58186d6c4cec6947c1942ee3ad312e9f7d50d444`。四版本 SHA 集合大小为 4，并在每次 fixture 构造时用实际 Git 内容断言。可信初态完整哈希为 `33bed85b1a1b107ced36f7a23bab36d4d1522f14a88162d223e3dd02dcb1626a`。

instruction 只提供目标、合法 commit ID 和最终状态要求，不含正确命令。正确命令只出现于测试操作与 host 生成的原生 oracle Agent solution 脚本，不会写入未来 Agent instruction 或 agent 镜像。

Oracle 直接解析 index v2，检查 SHA-1 校验和、路径/flags/padding、mode/blob/stage；逐文件检查最终 worktree 和除 index 外所有 `.git` 元数据。判分不调用 Git，因此不会读取或执行 Agent 的 Git 配置、hooks 或 filter。可信预期在 Agent repo 外保存，separate verifier 从自身可信代码重建。

### 正反例实际结果（每例均重建 fixture，重复 2 次）

| 操作 | 应判定 | 实际 Oracle（2次） | 测试状态 |
|---|---|---|---|
| 从 A 同时恢复工作区和暂存区 | PASS | PASS / PASS | PASS |
| 错误地从 HEAD 恢复两处 | FAIL | FAIL / FAIL | PASS |
| 仅恢复工作区 | FAIL | FAIL / FAIL | PASS |
| 仅恢复暂存区 | FAIL | FAIL / FAIL | PASS |
| 恢复错误文件 | FAIL | FAIL / FAIL | PASS |
| 正确恢复后移动 HEAD | FAIL | FAIL / FAIL | PASS |
| 破坏无关 tracked 工作区 | FAIL | FAIL / FAIL | PASS |
| 删除 untracked 哨兵 | FAIL | FAIL / FAIL | PASS |
| 修改 untracked 哨兵 | FAIL | FAIL / FAIL | PASS |
| 未执行有效操作 | FAIL | FAIL / FAIL | PASS |
| 额外提交并移动 ref | FAIL | FAIL / FAIL | PASS |
| 新增不允许文件 | FAIL | FAIL / FAIL | PASS |
| 破坏无关 tracked index | FAIL | FAIL / FAIL | PASS |
| 错误目标 index mode | FAIL | FAIL / FAIL | PASS |
| 篡改 Git fsmonitor 配置 | FAIL | FAIL / FAIL | PASS |
| 植入 expected.json 和 reward.txt | FAIL | FAIL / FAIL | PASS |
| 破坏 index 格式 | FAIL | FAIL / FAIL | PASS |
| 设置 assume-unchanged 标志 | FAIL | FAIL / FAIL | PASS |

36 次判定全部符合预期；每个最终状态再次判分的结果也完全一致。负例来自真实 Git 操作或真实字节修改，没有给 Oracle 传入 expected=False；`expected_success` 只用于测试框架比较 Oracle 的实际输出。

### 每一条断言的实际结果（第 1 轮；第 2 轮一致）

列含义：W=目标工作区字节/执行位，I=目标 index blob/mode/stage，R=HEAD/refs，UW=无关工作区，UI=无关 index，S=哨兵，ALLW=完整工作区集合，ALLI=完整 index 集合，G=全部非 index Git 元数据。T/F 是状态断言，负例中的 F 是预期检出。

| 案例 | W | I | R | UW | UI | S | ALLW | ALLI | G |
|---|---|---|---|---|---|---|---|---|---|
| 从 A 同时恢复工作区和暂存区 | T | T | T | T | T | T | T | T | T |
| 错误地从 HEAD 恢复两处 | F | F | T | T | T | T | F | F | T |
| 仅恢复工作区 | T | F | T | T | T | T | T | F | T |
| 仅恢复暂存区 | F | T | T | T | T | T | F | T | T |
| 恢复错误文件 | F | F | T | F | T | T | F | F | T |
| 正确恢复后移动 HEAD | T | T | F | T | T | T | T | T | F |
| 破坏无关 tracked 工作区 | T | T | T | F | T | T | F | T | T |
| 删除 untracked 哨兵 | T | T | T | T | T | F | F | T | T |
| 修改 untracked 哨兵 | T | T | T | T | T | F | F | T | T |
| 未执行有效操作 | F | F | T | T | T | T | F | F | T |
| 额外提交并移动 ref | T | T | F | T | T | T | T | T | F |
| 新增不允许文件 | T | T | T | T | T | T | F | T | T |
| 破坏无关 tracked index | T | T | T | T | F | T | T | F | T |
| 错误目标 index mode | T | F | T | T | T | T | T | F | T |
| 篡改 Git fsmonitor 配置 | T | T | T | T | T | T | T | T | F |
| 植入 expected.json 和 reward.txt | T | T | T | T | T | T | F | T | T |
| 破坏 index 格式 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 |
| 设置 assume-unchanged 标志 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 | 未执行 |

损坏 index 与 assume-unchanged 在结构校验阶段已判 FAIL，因此后续细粒度断言未执行，不能填 T。详细原因见对应 `oracle-result.json`。

## 4. Harbor separate verifier 与 artifact

独立 Oracle：PASS。Harbor separate verifier 集成：BLOCKED，未执行。TaskConfig 官方运行时解析也因 Harbor 未安装而 BLOCKED；不能用 TOML 静态可读代替官方接口成功。

已提供原生 task.toml、独立环境/判分 Dockerfile、tests/test.sh/verify.py 和完整 repo artifact 声明。官方 artifact 目录上传前会清空目标；判分镜像初始没有 `/work/repo`，避免删除文件被基准镜像残留补回。判分源自单独的可信 `/tests`，Agent 镜像不包含 Oracle 或判分答案文件。

任务 TOML 语法和固定源码 NetworkMode 枚举的离线检查为 PASS。配置使用官方的 `no-network`；错误值 `none` 的负例会被拒绝。此检查不冒称完整 TaskConfig 实例化。

本机实际通过的传输探针是 tar 打包/解包整个仓库，再用同一独立 Oracle 检查 index、隐藏 .git、refs 和文件状态。它仅证明状态导出契约在本机 tar 往返成立；没有运行 Harbor 的 download/upload、容器隔离、奖励收集和远程 Skill tar 安装。

当前环境恢复后，`--section harbor` 会先核验固定安装身份及官方 TaskConfig，再用 `harbor trials start --agent oracle --env docker` 运行正确 solution 和 no-op 两个原生无模型探针；预期 reward 分别为 1 和 0。该分支当前未执行，因此 reward 结果均无记录，不虚构 PASS。

Windows 测试已实测 index 文件模式的负例；POSIX worktree 执行位、symlink 和容器内 Git 元数据对齐仍需要 Linux Docker 核验。

## 5. 自动化测试与未通过项

| 测试组 | 实际结果 |
|---|---|
| 新增 11 个测试 | 10 PASS，1 BLOCKED（Windows symlink privilege WinError 1314） |
| 原有 18 个回归测试 | 17 PASS，1 FAIL（真实案例已从1个增加为5个，旧测试仍断言只有 case001） |
| 完整 unittest | 29 运行，27 PASS，1 FAIL，1 skip/BLOCKED；0 errors |
| 14 Skill 集合及逐文件哈希 | PASS |
| 18 类 Oracle × 2轮 | PASS，36 个实际状态判断 |
| 265 个官方文件 + 2020 个受保护研究文件 | PASS，全部未变 |
| 统一检查退出码 | 2，infra_status=BLOCKED |

失败的旧测试是 `test_framework.Framework.test_actual_case001_and_original_rules_unchanged`。其原有断言为 `manager.list_cases()==["case001_qsv_select"]`，实际五个案例在本轮前已存在，文件哈希与修改前一致。未改动断言或删除案例。

第一次直接 unittest 另有官方源码不在 PYTHONPATH、Windows 临时路径达 250 字符的三个 errors。最终通过添加官方源码路径、选择短临时目录消除了这三个环境错误，没有改生产代码或旧测试来绕过路径保护。

最终实际运行命令：

```text
python p0_validate.py <真实仓库根> p0-acceptance-002
  → python -B <lab>/scripts/lab.py downstream-check --section all --run-id p0-acceptance-002
  → unittest discovery tests/，PYTHONPATH 含官方源码/lab/lab-src，tempfile 父目录选仓库根
```

该执行助手仅用于本轮保存 stdout/退出码/回归日志。后续从研究目录复现完整回归可用以下 PowerShell 命令（环境变量只作用于当前会话）：

```powershell
$env:PYTHONPATH = "../AutoSkill-main;src;."
$env:TEMP = (Resolve-Path "..").Path
$env:TMP = $env:TEMP
python -B -m unittest discover -s tests -v
python -B scripts/lab.py downstream-check --section all
```

### 本轮修正的实现问题

- 测试部署前先保存真实树和哈希；部署助手曾拒绝暂存根说明文件，移除该本轮临时文件后部署，未触碰用户文件。
- 原始换行判断改用字节计数，避免把 stdout 转换误认为 CRCRLF 原件。
- index 校验补齐 checksum、flags/path length、padding、mode/stage 和边界，拒绝损坏或 assume-unchanged 结果。
- 明确 separate verifier 的空目录/完整 artifact 契约，并新增独立可信判分镜像，杜绝基准残留掩盖删除副作用。
- 子项缺文件/缺依赖明确 BLOCKED；不以 Python 单测通过替代 Harbor runtime。

- 最终固定源码复核纠正了 network_mode 从 none 到 no-network；增加真实官方枚举的静态正反例校验，并重新完整验收。

## 6. 统一结果字段

| 字段 | 定义与本轮值 |
|---|---|
| source_id/source_version/source_hash | 已有 Git manifest 身份、固定提交和冻结原文 SHA |
| generator_run_id/skill_manifest | 真实生成运行 r18307cee4f4c 与既有导出清单引用 |
| task_id/task_version | 唯一 Git task，版本1 |
| runner_version | 固定 Harbor commit；版本声明及补丁另见 lock |
| model_config | null，没有运行模型 |
| fixture_hash | 可信初态完整 JSON 的确定性 SHA-256 |
| condition | clean |
| installed_skill_ids/discovered_skill_ids | 宿主已验证的完整14 ID集合；不表示容器已安装 |
| read_events/tool_events | null，没有模型正文读取或模型工具轨迹；Oracle 测试命令另记 commands |
| verifier_version | git-state-v1 |
| assertion_results | 正确样本逐断言结果；完整正反例另见 oracle.json |
| success | null，不产生模型任务成功率；各 Oracle 记录独立保存 success |
| infra_status | BLOCKED；完整回归的既有 FAIL 另见 unittest.json |

## 7. 下一阶段准备判断

已满足：真实目录/来源/生成运行可追溯；14 Skill 字节完整；官方方法可解析和发现；UUID 映射；单个 Git fixture；独立确定性 Oracle 及正反例；无模型入口和日志；官方 separate verifier 配置和判分代码。

剩余阻断：完整固定 Harbor/uv.lock 依赖未安装；Linux Docker 不可用；镜像及精确 Git 包未构建/校验 digest；容器 Skill 上传与索引未测；官方 TaskConfig、artifact 和 separate verifier 未实际运行；symlink/POSIX模式路径未测。旧回归仍有案例数断言失败。模型配置未指定，且本轮明确禁止调用模型。

**唯一建议的下一阶段操作：补齐可联网的固定 Harbor + Linux Docker 环境，重跑同一零模型入口，完成原生 separate verifier 及容器 Skill 验证。** 在这些阻断解除前，不启动真实 Terminus-2 Agent 冒烟。即使这些检查全部通过，也仍需在下一阶段另行验证模型是否主动读取和遵循 Skill。
