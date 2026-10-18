# P1 零模型准备报告（2026-10-18）

**结论：三组工程准备通过；真实付费 Agent 冒烟测试尚未执行。** 最终验收运行是 `p1-ready-008`，A0/A1/Gold 均 PASS，模型 API 调用数为 0。原生 Harbor 工厂已完整实例化 `CompatibleTerminus2`，完成 tmux 初始化、技能注入、首个模型请求组装、工具执行、artifact 传递及 separate verifier。请求在真正访问模型之前停止，没有伪造模型回复。

这不能证明模型已经自主读取或遵循技能，也不是三组任务成功率。批准后才验证这些行为。

## 1. 工程与版本审查

工作树以 `D:/AS/AutoSkill-main` 为准，准备开始时 HEAD 为 `3080ee9fb80492f2a254b56382928b9e8c8e3f95`。继续使用现有 `degradation_failure_lab/downstream_eval/`、`scripts/lab.py`、原生 Harbor `Trial` 和唯一任务 `git-restore-explicit-source-both-v1`。没有新建 Runner。最后 git status 另出现 `.idea/vcs.xml` 的外部改动，本次没有编辑或还原它。

- Harbor：`0.24.0`，固定提交 `2de4605b9404eada7d341388291e6e469c90330b`。
- Terminus-2：上述提交的官方实现，版本 `2.0.0`；兼容层保留原生 agent loop。
- Linux 控制容器：`harbor-p0-control-20261018`；Python `3.13.9`、Git `2.39.5`、Docker `29.8.2`、PyYAML `6.0.3`。
- 继续使用原 `runner.lock.json` 和同提交 `uv.lock` 的冻结安装。未安装 latest，也未修改该锁文件中的 P0 禁止推理设置。
- 任务镜像补齐真实 Terminus 初始化所需的 tmux `3.3a-3` 和观测所需的 inotify-tools `3.22.6.0-4`。P0 的发现方法探针不经过完整构造与 tmux 初始化，所以不能替代本次检查。

最终三组实际运行镜像均为：

```text
sha256:1ae9dd6f9f9ec4217770c1fdf6bdf84dfa34e3d21705382de9fb0d6ffdf075a6
```

保留标签为 `harbor-p1-task:sha256-1ae9dd6f9f9ec4217770c1fdf6bdf84dfa34e3d21705382de9fb0d6ffdf075a6`。A0 探针取得镜像后，准备出的 task.toml 固定此标签；后续每组实际镜像 ID 必须相同。付费模式没有已验证 ID 或发现不一致即停止。

`environment.delete=false` 在这个固定 Harbor Docker 实现中执行 `compose down`：删除容器和网络，保留镜像，三组仍从独立新容器启动。验收后三组容器均已删除，冻结镜像仍可 inspect。没有保留运行后仓库作为下一组初态。

## 2. 文件变更及作用

| 文件（相对研究目录） | 作用 |
|---|---|
| `src/degradation_lab/cli.py` | 现有入口新增零模型 `downstream-prepare` 子命令 |
| `downstream_eval/p1.py` | 生成原生 TrialConfig、A0/A1/Gold 清单、Gold 工程检查和公平性记录，运行请求前停止探针；付费执行仍用官方 Harbor CLI |
| `downstream_eval/integration/p1_observer.py` | 在官方生命周期外侧记录索引、真实终端动作、内核 ACCESS、可见正文、请求/响应/用量；实现批准和预算门禁 |
| `downstream_eval/integration/terminus_compat.py` | 为原有兼容类增加显式 P1 观测参数；非 P1 模式沿用原行为 |
| `downstream_eval/integration/skill_install.py` | 提取既有远程哈希核验以复用，避免第二套安装逻辑 |
| `downstream_eval/checks.py` | 物化 P1 任务时省略参考 solution；P0 默认仍保留原行为 |
| `downstream_eval/configs/p1_smoke.json` | 固定模型快照、API、预算、时限、终端、单价和待批准状态 |
| `downstream_eval/gold/SKILL.md` | 独立通用 Git 规则，仅供 Gold 执行能力诊断；人工签核仍待用户确认 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/environment/Dockerfile` | 固定安装 tmux/inotify-tools，支持真实 Agent 和读文件观测 |
| `tests/test_p1.py` | 10 项无模型测试，覆盖工厂构造、SDK 前边界、门禁、公平性、Gold、隔离和读取证据 |
| `downstream_eval/README.md`、`downstream_eval/docs/change_list.md`、本报告 | 说明 P0/P1 边界、实际结果和复现命令 |

官方 Anything2Skill、原始 canonical SKILL.md、任务 instruction/fixture/Oracle/verifier 源码均未修改。Gold 是新增独立文件，不覆盖生成结果。原始 Git 生成运行的 473 个文件以及官方源码 265 个文件通过前后字节保护检查；详情见审计目录中的 `protected-after.json`。

## 3. 三组公平性与答案隔离

| 组 | 提供内容 | 安装/发现数 | 首次请求输入估算（含 256 token 保留） | 零模型受控正文读取 |
|---|---|---:|---:|---:|
| A0 | 无 Skill | 0 | 1041 | 0 |
| A1 | `r18307cee4f4c` 的全部原版生成 Git Skill | 14 | 2896 | 14/14 |
| Gold | 通用人工规则草案，经相同 Skill 路径安装 | 1 | 1136 | 1/1 |

A1 按 canonical UUID 集合逐项核验 14 个 ID、metadata、完整文件集和 SHA-256，不挑选最相关的一份。Gold 与 A1 使用同一复制、原生注入、发现和终端读取路径。

三个原生配置仅允许 Skill treatment、manifest 路径和输出身份不同。移除这些字段后的配置 SHA-256 均为 `6eec1b775e11cb86da97b94a90acabe7f9ef91f4ee398629d59fc1b9536c76b8`。任务指令、初态 fixture、模型/工具/预算/时限/终端和 verifier 相同。Skill 长度造成的实际输入 token 差异保留，不补虚假文本；实际用量逐组记录。温度为 0 也不能保证服务端绝对确定性。

Agent 仅挂载各自 `/logs/agent`、`/logs/verifier`、`/logs/artifacts` 的精确宿主目录，没有研究根目录或 Docker socket。setup 实测 `/tests`、`/solution`、`/environment`、构建 fixture 脚本均不可见。P1 物化任务完全没有 `solution/solve.sh`。Oracle、可信初态和 Gold 源文件留在控制侧；只有 Gold 组获得 Gold Skill。API key 留在 Harbor 控制进程，不注入终端容器。

独立 verifier 在 Agent 执行结束后取得 `/work/repo` 完整 artifact（含 `.git`），运行原有可信 Oracle；不信任 Agent 的 reward 或 expected 文件。本次三组均完成原生 separate verifier，9 条断言输出结构有效，无 Oracle 异常。因为受控探针只读技能、没有修复仓库，三组 reward 均应为 0；这是预期空操作结果，不能解释为生成质量或 Gold 失败。

Gold 工程验证把通用命令中的占位符代入独立 fixture，原 Oracle 全部 9 条断言通过。规则没有具体 commit、目标文件名、目标字节或测试答案：

```bash
git restore --source=<commit> --staged --worktree -- <path>
```

Gold SHA-256：`2aa353220e15b5931d5f8e4a2bc382ef2814336c0d6965ee409fbf7faa364f55`。目前标记 **`PENDING_USER_REVIEW`**，不能将工程检查冒充人工签核。

## 4. 如何证明实际读取

四种状态分别记录：

1. **已安装**：原生 Harbor 注入后，容器内完整文件集合及 SHA-256 与 staged/canonical 一致。
2. **已发现**：官方 `_build_skills_section` 生成 XML；核对 UUID、路径、名称和描述。A1 的全部 XML 原文实际出现在首个待发送请求中。
3. **已读取**：基础设施哈希/索引检查完成后才启动 inotify。将 `ACCESS` 事件与真实 Terminus tmux 工具动作、Skill ID、绝对路径、时间、原始终端输出和模型可见输出关联。只 OPEN、不认识的 ID、越界路径均不算。原生 ATIF、pane、消息记录继续保留。
4. **是否遵循**：需在批准后的真实模型轨迹中检查读到的规则、实际 Git 动作与最终 Oracle 断言；既不由“已安装”推断，也不采用模型自述作为读取证据。单次成功也不能证明由 Skill 导致。

本次 `controlled_probe_read_ids` 是请求前停止后由测试代码执行的真实 `cat`，actor 明确为 `zero_model_probe`；`model_read_ids` 三组均为空。付费模式不执行这些受控 cat，只记录模型自己产生的工具动作。

结构化观测在 trial 的 `p1-observer/`，位于 Agent 挂载目录之外。包括 `p1-installation.jsonl`、`p1-skill-index.xml`、`p1-model-requests.jsonl`、`p1-model-dispatch.jsonl`、`p1-model-responses.jsonl`、`p1-model-errors.jsonl`、`p1-tool-actions.jsonl`、`p1-terminal-frames.jsonl`、`p1-skill-reads.jsonl`、`p1-isolation.jsonl` 和 `p1-summary.json`。未发生的事件文件不会伪造填充。

读取证据有明确限度：ACCESS 证明文件被访问，不证明模型理解；tmux 软换行、CRLF 和 ANSI 序列影响显示比较，所以“全文可见”检查只忽略这些终端差异，磁盘无损另由 SHA 保证。原生单次 observation 保持 10,000 UTF-8 字节上限，截断前/后内容及字节数都记录。本次 14 份逐文件读取均能看到完整正文；未来若模型一次输出过多或分块读取，要依据具体轨迹判断，不能默认全文已见。原始 inotify 日志仍在 Agent 可写日志挂载内；控制侧检查已捕获前缀是否被改写，但它不是对恶意 Agent 的防篡改证明。

## 5. 零模型测试与实际命令

以下命令已执行，工作目录为 `D:/AS/AutoSkill-main/degradation_failure_lab`：

```powershell
docker exec harbor-p0-control-20261018 python -B scripts/lab.py downstream-prepare --run-id p1-ready-008
docker exec harbor-p0-control-20261018 python -B -m unittest discover -s tests -p test_p1.py -v
docker exec harbor-p0-control-20261018 python -B -m unittest discover -s tests -p test_downstream.py -v
docker exec harbor-p0-control-20261018 python -B scripts/lab.py downstream-check --section skills --run-id p0-p1-compat-001
```

最终 P1 测试 **10/10 PASS**；既有 Linux 下游测试 **12/12 PASS**；原 P0 技能容器检查 PASS。新增测试让真实 LiteLLM 参数校验走到 OpenAI SDK 创建前，并用停止异常阻断，确认 `max_retries=0`，没有假 API key、假 completion 或 HTTP 请求。完整初始化探针另在 `litellm.acompletion/aresponses` 放置零调用断言。

全库回归没有全绿，原样保留记录：Windows 当时 39 项，34 通过、1 旧断言失败、1 临时目录清理错误、3 跳过；后来只增加了一个 SDK 前边界测试并在 Linux 10 项中通过。旧 `test_framework.py:94` 仍硬编码只有 case001，而当前已有 5 个案例；未削弱断言。Windows Git fixture 的 WinError 32/5 发生于 TemporaryDirectory 清理；对应 Oracle 测试在 Linux 通过。Windows 跳过符号链接权限与两项 Linux Harbor 测试，已在 Linux 单独覆盖。额外尝试全库 Linux 回归时，控制容器没有挂载官方 Anything2Skill 源目录，导致 13 项旧框架路径检查错误；不属于本次 Agent 链路失败。没有为了这些旧测试扩大 Agent 挂载或复制含凭据的官方 `.env`。

准备调试历史全部保留：`001` 凭据选择器过早校验，`002` artifacts 精确挂载路径断言错误，`003` A0 空 stdout，`004` 三组基础链路通过；`005` 镜像标签清理/拉取失败，`006` 重建镜像 ID 不同。已修正后 `007` 三组、私有证据与同镜像复用同时通过；`008` 在关闭隐式重试后再次全部通过，作为最终待批准配置。不能只保留成功结果，也不将这些基础设施失败计入方法性能。

## 6. 待批准的模型、API、预算和命令

拟用模型快照 `openai/gpt-5.4-mini-2026-03-17`；API `https://api.openai.com/v1`，Chat Completions；Harbor 格式值 `openai_chat_completions`。不采用浮动 latest/alias。官方文档列出该快照、接口、推理选项及标准 token 单价，核验日期为 2026-10-18：[OpenAI GPT-5.4 Mini 文档](https://developers.openai.com/api/docs/models/gpt-5.4-mini)。账户权限与实际服务端参数接受情况尚未调用验证。

| 每组冻结参数 | 值 |
|---|---:|
| Agent 请求上限 / 单次输出上限 | 8 / 2048 token |
| 单次 / 累计输入估算上限（请求前保留 256 token） | 20,000 / 100,000 token |
| temperature / reasoning_effort | 0 / none |
| SDK 重试 / 原生方法外层 Tenacity 重试 | 0 / 0 |
| 单请求 / Agent / setup / verifier 时限 | 45 / 300 / 90 / 60 秒 |
| 输入 / 缓存输入 / 输出单价（USD/百万 token） | 0.75 / 0.075 / 4.50 |

不用缓存折扣，三组预算估算：`3 × (100000 × 0.75 + 8 × 2048 × 4.50) / 1000000 = USD 0.446184`。建议审批 **USD 0.60**。这是 token 预算估算，不是供应商账户账单硬上限；输入 tokenizer 估算、错误请求未返回的 usage、供应商特殊重试及税费均不能冒充精确账单。日志保留已返回的 prompt/completion/cache token、Harbor cost 和按冻结单价计算的费用；错误请求标记 usage 未报告，不记成零成本。

批准范围是 **A0/A1/Gold 各一次完整 Agent 运行，最多合计 24 个 Agent 请求**，不是仅三个 completion。P1 使用冻结官方方法的原始函数体，关闭其外层 Tenacity 自动重试；异常回归证实一次逻辑请求失败只触达一次 provider 边界。SDK `max_retries=0` 另有独立边界验证。不开启总结或额外模型辅助，不批量正式评估。请求派发还必须存在 `P1_ALLOW_PAID=1`，代码不会在准备阶段设置它。

以下三条为**拟执行，尚未执行**。仅在用户批准、审核 Gold 并把 OPENAI_API_KEY 放入调用终端环境后运行；不要把 key 写进文件、命令参数或聊天。Docker `--env OPENAI_API_KEY` 只复制环境变量给控制进程。

```powershell
docker exec --env OPENAI_API_KEY --env P1_ALLOW_PAID=1 harbor-p0-control-20261018 harbor trials start --config /run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-ready-008/configs/A0.json
docker exec --env OPENAI_API_KEY --env P1_ALLOW_PAID=1 harbor-p0-control-20261018 harbor trials start --config /run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-ready-008/configs/A1.json
docker exec --env OPENAI_API_KEY --env P1_ALLOW_PAID=1 harbor-p0-control-20261018 harbor trials start --config /run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-ready-008/configs/Gold.json
```

付费配置显式选择 OPENAI_API_KEY。零模型探针仅去掉该凭据选择器、切换 probe mode 和输出身份，其余模型/工具/预算保持一致；因此本次没有验证账户身份、余额、限流、真实响应 JSON 或模型工具行为。

## 7. 证据位置与剩余阻断

- 最终验收：`D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-ready-008/result.json`。
- 原生三组配置、profile、fairness、Gold 工程检查、Skill manifest、zero_model_trials 和私有观测均在同目录。
- 完整执行命令、起止时间、返回码、stdout/stderr、回归与前后保护检查：同级 `p1-prepare-20261018/`，入口 `commands.md`。

当前阻断是用户尚未批准付费推理、Gold 尚待人工签核，以及控制进程没有 OPENAI_API_KEY。若更换模型或预算，应重新冻结并做零模型校验，不能静默替换。Docker 缓存或冻结镜像被删时，应先恢复并复验镜像，不能带着不同环境付费运行。

真实运行时若 Gold 失败，先审查启动、规则注入、读取、工具和任务；Oracle/环境故障单列为基础设施异常。三组单次差异只能用于工程诊断，不作稳定性能结论。当前未构造退化文档、未生成新技能、未执行任何付费模型调用。
