# SkillGenBench 单任务完整实验操作手册

> **适用项目**：`D:\AS\AutoSkill-main\degradation_failure_lab`  
> **更新时间**：2026-10-27  
> **当前研究阶段**：Clean 文档 → Anything2Skill 生成 Skill → Terminus-2 执行 NoSkill / CleanSkill → 独立 Verifier 评分。**暂不做文档退化，也不做多次重复。**  
> **核对依据**：GitHub `lily400/AutoSkill-main` 的 `master` 分支真实入口代码，以及本次提供的 `DELIVERY.md` / 审计报告。**我不能直接读取你电脑 `D:` 盘当前未提交的修改**；执行前应以本地代码、冻结清单和 Codex 的只读检查为准。

---

## 0. 先记住：一个任务，其实分成两次不同的运行

```text
      [SkillGenBench 任务：源文档 + 题面 + 官方测试]
                            │
             第 0 步：Codex 审核任务是否合格
                            │
                            ▼
      [case_id / 原文快照 / 生成配置 / 生成授权]
                            │
       第 1 步：Anything2Skill 生成（gen run ID）
                            │
            第 2 步：verify 核验生成产物
                            │
               第 3 步：freeze 冻结 Skill
                            │
      [下游准备 / 两臂协议 / 独立评分 / 下游授权]
                            │
          第 4 步：prepare 零模型准备与检查
                            │
          第 5 步：run 下游实验（experiment ID）
                            │
                 ┌──────────┴─────────┐
                 ▼                    ▼
            NoSkill1              CleanSkill1
           不安装 Skill           安装冻结 Skill
                 │                    │
                 └──────────┬─────────┘
                            ▼
                   独立评分器评分
                            │
          第 6 步：status / analyze / cohort
                            │
          第 7 步：Codex 审核结果与失败原因
```

**最重要的区别：**

- **`case_id`**：生成案例，例如 `case101_monitor`；决定喂给 Anything2Skill 的源文档、条件和配置。
- **`generation run ID`**：一次 Skill 生成的唯一编号，例如 `m01g001`。一个生成 run 会有自己的输入快照和独立 SkillBank。
- **`task ID`**：SGB 的下游任务标识，例如 `monitoring_gap_brief_classifier_001`；不是 `case_id`。
- **`experiment ID`**：一次下游 **NoSkill1 + CleanSkill1** 配对的编号，例如 `m01f001`；与生成 ID 不同。
- **`verify`**：只检查 **A2S 生成链与证据产物**，**不是**检查 Agent 下游任务是否成功。
- **`analyze`**：看一次下游配对的两臂结果、Skill 使用和失败类型。
- **`cohort`**：把多个任务汇总成正式实验队列；不是生成 Skill，也不会自动运行 Agent。

**Codex 不是运行器**：它主要做准入审核、定位配置/哈希/契约问题、检查产物和写报告。既已准入、已配置、已授权且预检通过的任务，直接运行 Python / PowerShell 命令即可；**不需要每次让 Codex 在中间“点头”**。但所有模型调用仍必须经过原有授权与预算门禁。

---

## 1. 第一次做某个任务：先让 Codex 审核哪些内容？

这是**新增一个 SGB 任务时的一次性审核**，不是每运行一条命令都做一遍。

| 要审核什么 | 为什么要审核 | 通过标准（摘要） |
|---|---|---|
| **1. 源文档** | A2S 必须有合法输入，且能追溯 | 源文档真实存在、固定版本、哈希准确；明确是 SGB 任务配套快照 |
| **2. 任务—文档依赖** | 防止 Agent 不看文档也可直接从题面得到答案 | 至少指出任务依赖原文的具体规则 / API / 限制条件 |
| **3. 题面及 Verifier** | 防止评分本身有歧义 | 验证器能评价题目承诺的能力，不引入未说明的任意答案约束 |
| **4. 运行环境** | 防止两组比较混入环境差异 | Docker 镜像、依赖、观察桥、禁网、时限可以落地 |
| **5. A2S 案例配置** | 确定究竟用哪些原文生成 | `case_id`、输入清单、`clean`、配置、预算、gate 明确 |
| **6. 下游任务绑定** | 确定如何将生成的 Skill 接给 Agent | `pilot_config`、`task_id`、评分适配器、冻结版协议一致 |
| **7. 安全与预算** | 不重复计费、不意外绕门禁 | 生成与下游分别有明确的授权身份、调用上限和阻断策略 |

Codex 应输出 **`READY` / `NEEDS_WORK` / `REJECTED`**。只有 `READY` 才进入正式运行队列。它还应告诉你：这个任务是否已有可复用生成包；是否需要新生成；用什么 `case_id`、`generation run ID` 和 `experiment ID`；接下来执行哪些命令。

### 1.1 给 Codex 的一次性审核提示词（复制粘贴）

```text
请对 degradation_failure_lab 中的 SkillGenBench 任务 <任务ID> 做正式实验准入审计。
本轮只读，不调用付费模型，不改动 Skill、不修改原始题面/测试、不改变授权门禁。

请实际阅读本地代码与资产，逐项确认：
1. SGB 原始源文档、固定版本、SHA；文档中的哪些具体规则为任务所需。
2. 官方任务 instruction / eval / tests / reference 是否一致；有没有额外隐藏输出常量、无来源约束或会误杀等价实现的评分问题。
3. A2S 输入白名单、case / conditions / input manifest、生成配置、max_http_calls / max_observed_total_tokens、gate。
4. 下游 pilot_config、观察/评分桥、依赖镜像、Harbor / Terminus-2 版本、禁网、两臂共同提示词与模型预算。
5. 原有生成 run 是否 completed 且 verify PASS；最终 Skill 是否由 A2S 真实产生、没有人工补写。
6. 是否存在现有正式配对可以复用；若不能复用说明协议或哈希差异。
7. 如果新增任务，优先复用现有 JSON 或对象观察适配；不要每题重做 Agent 与框架。

输出：
- READY / NEEDS_WORK / REJECTED 及证据文件和行号；
- task_id、case_id、生成 run ID、下游 experiment ID；
- A2S 已有 / 待生成；是否需要 register 任务；
- 精确预算与授权状态（注意 READY 不等于已授权）；
- 从 plan / run / verify / freeze / prepare / run / analyze / cohort 的准确命令；
- 哪些命令是零模型，哪些会收费；
- 若需要修改代码，先说明是否影响已冻结实验的哈希与准备身份。

不要自动运行付费步骤；不要为了凑 10 题降低 Verifier 准入标准。
```

**什么时候不需要再叫 Codex？** 同一个任务的审核已通过、绑定与授权没变、代码未改、Skill 已生成且冻结、`prepare` 已通过时，执行正式 `run`、`status`、`analyze` 不需要反复手工审计。

---

## 2. 公共准备（每次新打开 PowerShell）

在 **Anaconda PowerShell** 内执行，所有相对路径都以 `degradation_failure_lab` 为起点：

```powershell
conda activate autoskill
cd D:\AS\AutoSkill-main\degradation_failure_lab
python --version
python -c "import sys; print(sys.executable)"
python -c "import tomllib; print('tomllib OK')"
```

如 Python 版本低于 3.11，`tomllib` 可能报错；需先把环境兼容性处理好（例如 `tomli` 兼容导入），**在修复后重新核验冻结哈希/执行准备，不能盲目重试付费任务**。本项目的运行脚本与 Docker 控制容器也可能使用不同的 Python 解释器，必要时分别检查。

接着做**零模型**检查：

```powershell
python scripts/lab.py validate
python scripts/lab.py sgb audit
python scripts/lab.py sgb list --task scrapy-task-024
```

这些命令的含义依次是：本地案例与配置是否合法、SGB 冻结登记是否仍匹配、任务的当前登记情况。

如果要检查已经配置好的下游凭据是否可读取（**不发送模型请求**）：

```powershell
.\scripts\Invoke-ProjectCredential.ps1 -CheckOnly
```

**提醒：** A2S 生成使用生成配置中的凭据变量（目前通常是 `DEEPSEEK_API_KEY`）；下游使用 `ZHIZENGZENG_API_KEY`，项目 Windows 凭据包装器负责加载已保存的下游凭据。**不要把 API Key 写入命令、文档、GitHub 或 gate。**

> 命令示例不强制写 `-B`。`python -B` 的作用只是禁止生成 Python 字节码缓存，不会改变实验算法、生成结果定义或模型参数。若项目的冻结/隔离要求采用 `-B`，可统一加上；尤其不要在同一冻结运行中随意改变执行配置。

---

# A 路线：该任务尚未生成 Skill（完整从零走一遍）

这里以真实已准入的 **`monitoring_gap_brief_classifier_001`** 为例。它的登记关系为：

| 角色 | 本例的真实标识 |
|---|---|
| SGB 下游 `task_id` | `monitoring_gap_brief_classifier_001` |
| A2S `case_id` | `case101_monitor` |
| 生成 `run ID` | `m01g001`（**当前规划 ID，未生成**） |
| 下游 `experiment ID` | `m01f001`（**当前规划 ID，未运行**） |
| 生成条件 | `clean` |
| 预计下游两臂 | `NoSkill1`、`CleanSkill1`（各一次） |

### A0. Codex 任务准入通过，再确认生成 gate 授权

目前交付报告中的该任务为技术 `READY`，**但生成 gate 仍为 `BLOCKED`**。先按审核结果完成 **精确的生成授权**，它应绑定：`case101_monitor / clean / m01g001`、配置文件 SHA、HTTP 预算和 token 阈值。

**当前没有已核实的通用 `python ... authorize` 命令。** `READY`、`plan`、有 API Key、甚至收到一份授权“提案”，都不等于 `AUTHORIZED`。此步须按仓库现有 gate 流程由你明确批准后处理；不允许删掉 gate 或直接将 `BLOCKED` 改成 `PASS` 来跳过配置审核。

### A1. 查看生成计划（零模型）

```powershell
python scripts/lab.py plan --case case101_monitor --condition clean --repeat 1
```

检查返回的案例、输入文档数、实际生成模型、生成目录模板。如果它们不是 Codex 审核批准的内容，停止。

### A2. 真正生成 Skill（付费；只执行一次）

**确认生成 gate 已经对本 run 精确授权、生成 API Key 可用之后：**

```powershell
python scripts/lab.py run --case case101_monitor --condition clean --repeat 1 --run-id m01g001
```

程序实际做的事：

1. 将登记的源文档复制到新的 `runs/gen/sgb/.../m01g001/inputs/`，记录哈希；
2. 建立空 SkillBank；
3. 调用官方 Anything2Skill 公共入口；
4. 依次形成 **Ingest → Extract → Compile → Register** 产物；
5. 保存最终 Skill、模型请求和响应、预算消耗、执行状态。

**生成一次 ≠ 生成一个 Skill**：一个任务的原始文档可能生成 0、1 或多个 Skill。也**不是**手动挑选其中“最好”的几个 Skill 给下游：正式条件应保留本次生成及注册得到的冻结包。

如果出现中断，**不要直接再次运行相同 `--run-id`**。`resume` 是另一个明确的有条件恢复流程，需要新 run ID、检查点和累计预算审计；失败请求计费未知时不能擅自续跑。

### A3. 工程验证和导出证据（零模型）

```powershell
python scripts/lab.py verify --run m01g001
python scripts/lab.py verify --run m01g001 --out results/exports/m01g001
```

查看：

```text
results/exports/m01g001/verification.json
results/exports/m01g001/windows.json
results/exports/m01g001/support_records.json
results/exports/m01g001/skill_drafts.json
results/exports/m01g001/skill_specs.json
results/exports/m01g001/registration.json
results/exports/m01g001/traceability.json
```

应检查 `status`、`registered_skills`、四阶段内容、来源哈希、调用记录。**`verify PASS` 只证明生成过程与证据链在工程上可核验，不证明关键规则没被遗漏，也不证明下游会成功。**

若为 `PARTIAL`、未注册任何 Skill 或运行未 `completed`，先分析原因，不进入正式下游。

### A4. 冻结最终 Skill（零模型）

使用下游任务 ID（不是 case ID）：

```powershell
python scripts/sgb/pilot.py freeze --task monitoring_gap_brief_classifier_001 --generator-run m01g001 --output results/sgb/skill-freezes/m01g001
```

冻结输出应记录每个注册 Skill 的正文及元数据，与生成的 run/hash 对应。**不能在冻结后手工修订 SKILL.md**；后续一切实验均使用这份冻结内容。

### A5. 检查下游配对计划（零模型）

```powershell
python scripts/sgb/pilot.py plan --task monitoring_gap_brief_classifier_001 --generator-run m01g001 --experiment m01f001
```

本步确认：同一个 `generator-run` 和 `task ID` 被绑定到同一个下游配对；两个条件分别安装 0 包与冻结的 Skill 包；任务已完成 pilot 注册。**`plan` 是打印计划，不会建立正式可执行的配对目录。**

### A6. 准备下游授权与执行快照（零模型）

新的 JSON 任务不仅需要 A2S 生成授权，还需要独立的 **下游精确授权**：应绑定 `generator_run_id=m01g001`、`experiment_id=m01f001`、实际 `task_config_sha256`、本配对的 HTTP 上限等。

**注意顺序**：报告指出新 JSON 任务的 gate 也被包含在执行冻结清单中，**不可先完成最终 prepare，再修改 gate 进行授权**。应先由 Codex 核对准许的身份和 SHA，确认 gate 处于已授权状态，然后进行最终 `prepare`：

```powershell
python scripts/sgb/pilot.py prepare --task monitoring_gap_brief_classifier_001 --generator-run m01g001 --experiment m01f001
```

`prepare` 会核验原始任务与评分资产、冻结/安装 Skill、校验运行镜像和两臂协议、用固定正反例执行 **零模型探针**、生成 `readiness.json`、`fairness.json`、冻结清单及持久化预算账本。

必须得到 **`READY` / `readiness PASS`** 才能执行付费 `run`；如果 gate 改动造成 SHA 变化，需按现有机制**创建新的准备身份**，不要覆盖旧清单或直接改哈希。

### A7. 执行下游 Agent 两臂（付费；只执行一次）

**本步是例外：推荐使用项目提供的 PowerShell 包装器，而不是裸 `python ... run`。** 原因是 Windows 下它为该次运行加载临时下游凭据，并检查退出状态；Python 入口仍然是 `scripts/sgb/pilot.py`。

```powershell
.\scripts\sgb\Invoke-Pilot.ps1 -Phase run -Task monitoring_gap_brief_classifier_001 -Experiment m01f001
```

本次会执行两臂：

- `NoSkill1`：Agent 无 Skill 安装，完成同一 SGB 任务；
- `CleanSkill1`：Agent 安装由 `m01g001` 冻结的 Skill，完成同一 SGB 任务。

模型、题面、共同阅读说明、环境、预算与 Verifier 保持一致；当前正式协议为 `clean-pair-v1`。下游使用请求名 `openai/gpt-5.4-mini-2026-03-17`，每臂最多 6 次 HTTP 尝试（两臂共最多 12 次），temperature=0、reasoning=none。**每臂只运行一次，不等于内部只发一次模型请求。**

> 如果坚持看 Python 形式，真正被包装器调用的是：`python scripts/sgb/pilot.py run --task monitoring_gap_brief_classifier_001 --experiment m01f001`。**不要把这条裸 Python 命令当作 Windows 下的推荐付费启动方式**；凭据加载和控制容器转发依赖现有包装流程。

### A8. 查看状态（零模型，可在出错后执行）

```powershell
python scripts/sgb/pilot.py status --task monitoring_gap_brief_classifier_001 --experiment m01f001
```

`PREPARED` 是已准备但未启动；`RUNNING` 是已开始；`COMPLETED` 是两臂运行结束；`STOPPED` 代表流程停止。**COMPLETED 不等于两臂都成功完成任务。**

如果下游报错，先执行 `status`；**不要直接再敲一遍 `run`**。应同时检查 `batch_stop.json`、逐臂 outcome、`budget.sqlite3` 等，再判断是 Python 导入/冻结问题、Agent 失败还是实际 HTTP 已产生。

### A9. 下游分析（零模型）

```powershell
python scripts/sgb/pilot.py analyze --task monitoring_gap_brief_classifier_001 --experiment m01f001 --output results/sgb/analyses/m01f001
```

重点查看：

```text
results/sgb/analyses/m01f001/report.md
results/sgb/analyses/m01f001/analysis.json
results/sgb/analyses/m01f001/skills.md
results/sgb/analyses/m01f001/NoSkill1-skill-usage.json
results/sgb/analyses/m01f001/CleanSkill1-skill-usage.json
```

分析时先看每臂 `task_success`（整题通过/失败），再看各测试用例通过数量、`failure_kind`、`infra_ok`、是否读取 Skill 正文、模型请求中是否包含相关规则。**Agent 读过 Skill 不能单独证明它依赖了 Skill。**

### A10. 将任务纳入 10 题正式队列（零模型）

```powershell
python scripts/lab.py sgb cohort --config configs/sgb/clean10.json --output results/sgb/analyses/clean10-after-monitoring-001
```

输出新目录，勿覆盖既有汇总。`cohort` 会查看登记的正式任务与配对身份，区分完成、未执行、单臂停止、失败与不可评分；它不会自动补跑缺失实验。

### A11. 这时再让 Codex 做一次**结果审计**（不是重新准入）

把本任务的 `verification.json`、Skill、`analysis.json`、Agent 轨迹、Oracle/JUnit 和预算账本交给 Codex，要求它回答：

- 原文的关键规则哪些进入了最终 Skill，哪些在切分、提取、合并时丢失或改变；
- Skill 是否安装、是否被 Agent 读取、相关规则是否进入成功模型请求；
- NoSkill 和 CleanSkill 的真正整题结果是什么；具体失败测试是什么；
- 是否为 `task_failure`、`budget_exhausted` 或 `infrastructure_failure`；
- 结果是否可比；是“可能与 Skill 有关”还是有完整规则—行为证据。

**这步不允许通过事后改 Skill / 改 Oracle 让 CleanSkill 变成功。** 审计结论才是我们的科研数据。

---

# B 路线：该任务已经生成过 Skill（不用重跑 A2S）

以已经就绪的 **Scrapy024** 为例：

| 字段 | 实际登记 |
|---|---|
| `task_id` | `scrapy-task-024` |
| `case_id` | `case024_sgb` |
| 已有生成 ID | `s24a001` |
| 正式下游配对 ID | `c24f002` |

**已经有成功的生成 run 时，不应为了做同一个下游对照而重新提取 Skill。** 先验证旧生成、再查看配对状态。

```powershell
python scripts/lab.py verify --run s24a001 --out results/exports/s24a001-check
python scripts/sgb/pilot.py status --task scrapy-task-024 --experiment c24f002
```

如果该 `experiment ID` 的配对准备已完成、确实尚未启动、源码/冻结哈希匹配且付费授权有效，则可以直接进入下游执行。**不要对一个已经启动过的配对再次 `run`。**

下面是 **“还没 prepare 的新实验”** 时才需要的步骤（示范命令，不能覆盖现有 `c24f002`）：

```powershell
python scripts/sgb/pilot.py plan --task scrapy-task-024 --generator-run s24a001 --experiment <全新实验ID>
python scripts/sgb/pilot.py prepare --task scrapy-task-024 --generator-run s24a001 --experiment <全新实验ID>
```

预检完成、精确授权通过后执行（**把占位符换成真正新 ID**）：

```powershell
.\scripts\sgb\Invoke-Pilot.ps1 -Phase run -Task scrapy-task-024 -Experiment <全新实验ID>
python scripts/sgb/pilot.py status --task scrapy-task-024 --experiment <全新实验ID>
python scripts/sgb/pilot.py analyze --task scrapy-task-024 --experiment <全新实验ID> --output results/sgb/analyses/<全新实验ID>
```

**特别提醒：你的 `c24f002` 曾经因 `ModuleNotFoundError: No module named 'tomllib'` 在本地导入阶段退出。** 目前不能据此断言 HTTP 已产生，也不能直接断言冻结哈希必然失效。**先修 Python 兼容、用 status + 预算账本 + execution_manifest 做只读检查**。若满足原 run 从未启动、账本无未知请求、执行文件仍匹配的条件，才由现有门禁允许使用它；若发生冻结失配，需要重新 `prepare` 和新实验身份，不是简单重发原 `run`。

同理，**Scrapy041** 是：

```powershell
python scripts/lab.py verify --run s41r003 --out results/exports/s41r003-check
python scripts/sgb/pilot.py status --task scrapy-task-041 --experiment c41f002
```

`c41f002` 尚未真正付费启动时，其余流程与 Scrapy024 相同，只要确认授权和冻结有效即可。Scrapy041 的 `allow_offsite` 规则提取遗漏应如实保留，不手写补齐。

---

## 3. 什么情况下需要 `register` 新任务？

只有任务尚未绑定到通用下游入口时，Codex 才需要先准备配置（**不是每次生成 Skill 都要注册**）。入口确实支持：

```powershell
python scripts/sgb/pilot.py register --task <实际SGB任务ID> --config <已审核的项目相对任务配置路径>
```

它做的是写入 SGB registry 的 `pilot_config` 绑定、核验任务/配置/资产身份；**不执行 Agent，也不自动授予生成或下游预算。**

你已经在 `configs/sgb/clean10.json` 内登记的 `READY` 项，先检查是否有现成 `pilot_config`，不要重复注册或自行猜一个配置路径。如果接口、Adapter 或 Oracle 仍不满足准入条件，应先让 Codex 解决，而不是拿一个可运行的空配置凑数。

---

## 4. 常用命令总表（最适合直接查）

**所有命令均在项目根目录执行，`<>` 表示要替换的占位符，不是 PowerShell 的真实参数。**

| 目的 | 命令 | 模型调用？ |
|---|---|---|
| 检查全部 A2S 案例 | `python scripts/lab.py list` | 否 |
| 校验项目案例 | `python scripts/lab.py validate` | 否 |
| 核验 SGB 注册表 | `python scripts/lab.py sgb audit` | 否 |
| 查看任务记录 | `python scripts/lab.py sgb list --task <task_id>` | 否 |
| 规划 A2S 生成 | `python scripts/lab.py plan --case <case_id> --condition clean --repeat 1` | 否 |
| **真正生成 Skill** | `python scripts/lab.py run --case <case_id> --condition clean --repeat 1 --run-id <gen_id>` | **是** |
| 检查 Skill 生成 | `python scripts/lab.py verify --run <gen_id>` | 否 |
| 导出生成链证据 | `python scripts/lab.py verify --run <gen_id> --out results/exports/<gen_id>` | 否 |
| 下游冻结 Skill | `python scripts/sgb/pilot.py freeze --task <task_id> --generator-run <gen_id> --output results/sgb/skill-freezes/<gen_id>` | 否 |
| 规划下游配对 | `python scripts/sgb/pilot.py plan --task <task_id> --generator-run <gen_id> --experiment <exp_id>` | 否 |
| **下游预检 / 正式 prepare** | `python scripts/sgb/pilot.py prepare --task <task_id> --generator-run <gen_id> --experiment <exp_id>` | 否（但用 Docker） |
| **下游两臂运行** | `.\scripts\sgb\Invoke-Pilot.ps1 -Phase run -Task <task_id> -Experiment <exp_id>` | **是** |
| 查看下游状态 | `python scripts/sgb/pilot.py status --task <task_id> --experiment <exp_id>` | 否 |
| 分析下游结果 | `python scripts/sgb/pilot.py analyze --task <task_id> --experiment <exp_id> --output results/sgb/analyses/<exp_id>` | 否 |
| 汇总 10 个任务 | `python scripts/lab.py sgb cohort --config configs/sgb/clean10.json --output results/sgb/analyses/<新汇总目录>` | 否 |

**为什么有两次 `run`？** `lab.py run` 花钱让 **Anything2Skill 生成 Skill**；`pilot.py run` 花钱让 **Terminus-2 使用或不使用 Skill 做任务**。你研究的就是这两次运行之间，知识被如何“编译”和使用。

---

## 5. 各步骤的文件到底在哪里？

| 阶段 | 关键文件（相对 `degradation_failure_lab`） | 说明 |
|---|---|---|
| 固定源文与任务 | `data/raw_sources/sgb/`、`.external/skillgenbench/`、`data/manifests/sgb/tasks.jsonl` | 源文、原题面/测试与登记 SHA |
| A2S 案例 | `cases/sgb/<case_id>/` 或由 CaseManager 实际找到的 case 目录 | `case.json`、`conditions.json`、输入清单 |
| A2S 生成器 | `scripts/lab.py` → `src/degradation_lab/cli.py` → `runner.py` → `adapter.py` | 调用 Anything2Skill 公共入口 |
| 生成产物 | `runs/gen/sgb/<case_id>/clean/<gen_id>/` | `official_result.json`、`SkillBank/`、`execution.json`、中间四阶段 |
| 生成校验导出 | `results/exports/<gen_id>/` | windows / support / drafts / specs / traceability |
| 正式配对协议 | `configs/sgb/clean_pair_protocol.json` | 两臂条件、模型、预算、共同阅读指令 |
| SGB 下游配置/适配 | `downstream_eval/sgb/` | `pilot.py`、`runner.py`、Adapter 与评分 |
| 下游 Trial | `runs/eval/sgb/<task_id>/<exp_id>/` | `profile.json`、`readiness.json`、`execution_manifest.json`、`budget.sqlite3`、`trials/`、`outcomes/` |
| 单任务下游分析 | `results/sgb/analyses/<exp_id>/` | `analysis.json`、`report.md`、使用证据 |
| 正式 10 题索引 | `configs/sgb/clean10.json` | 一个 task ID 只选一个正式配对；历史另存 |

> 不同版本、历史任务的生成目录可能不同。**具体位置以 `python scripts/lab.py verify --run <id>`、`plan` 和 `run` 输出的真实路径为准**，不要通过目录名猜测已经完成或已经成功。

---

## 6. 评分怎么看才不会搞混？

本研究目前是**10 个不同任务，每个任务各一次 NoSkill / CleanSkill**：

- **主指标**：`task_success`，一个任务整体通过记 `1`，否则记 `0`（基础设施不可评分单独标记）。
- **辅助指标**：比如 `13/19` 或 `19/19`，是该任务通过的 **pytest 测试用例数**，**不是 19 次独立任务成功率，也不一定是 19 条原始 assert**。
- **配对四种结果**：两臂都成功、仅 CleanSkill 成功、仅 NoSkill 成功、两臂都失败；另记录配对不完整。
- **失败要分类**：`task_failure`、`budget_exhausted`、`infrastructure_failure`，不能把没提交的 Agent 失败随意排除使成功率虚高。
- **生成质量要另看**：哪些原始关键规则进入最终 Skill，哪些丢失、扭曲或发生合并失真。
- **Skill 使用要另看**：已安装、索引可见、正文被读、相关正文在成功模型请求中出现、最终行为是否有可追溯证据，不能混为一谈。

**我们要得到的是“Clean 阶段的问题地图”**，不是证明 CleanSkill 在每题都胜利。CleanSkill 失败、两臂都成功、甚至两臂都失败，只要准入与执行证据有效，就可能是有价值的研究观察。

---

## 7. 常见报错，第一反应应该是什么？

| 现象 | 优先检查 | 不该怎么做 |
|---|---|---|
| `No module named tomllib` | 本地 Python 版本、解释器，及是否已做兼容导入；再检查冻结 SHA | 不要直接再次点 `run` |
| `BLOCKED` | 生成 gate 或下游精确授权，case/run/config SHA/预算是否对上 | 不删除 gate、不伪造 PASS |
| `Pilot stopped. Preserve its ledger` | `python scripts/sgb/pilot.py status --task ... --experiment ...`；`budget.sqlite3`、`batch_stop.json` | 不删 SQLite、不自动重试 |
| `Frozen execution file changed` | 实际本地文件与 `execution_manifest.json`；可能要新准备身份 | 不手工把 SHA 改成新值来绕过 |
| `Task binding changed` | 任务注册配置和哈希是否被改过 | 不直接用旧 ID 强行启动 |
| `NOT_PREPARED` | 是否真的执行 `prepare` 且成功 | 不把 `plan` 当 `prepare` |
| `COMPLETED` 但任务失败 | `analyze` 与 Verifier/JUnit，确认真实代码/规则失败 | 不把 completed 当整题 PASS |
| 部分条件完成、另一臂未启动 | 逐臂 outcome 与账本，是否有 infra stop | 不给未启动臂记 0 分，也不偷偷补跑 |

如果不确定是不是已经付费或有没有发出请求，**先保存终端完整报错，做只读状态/账本审计**；在没有确认前不要再次启动同一个付费 run。

---

## 8. 当前已登记的五个 READY 任务：应该走 A 还是 B？

下面是 **2026-10-27 交付时** 的状态；不代表后来已经获得授权或执行成功。

| SGB 任务 | `case_id` | 生成 run | 下游实验 | 推荐路线 |
|---|---|---|---|---|
| Sanctuary002 | `case003_san` | `sn3r001` | `sn3e001` | **已有正式配对**：复用，直接做结果分析 |
| Scrapy024 | `case024_sgb` | `s24a001` | `c24f002` | **B：无需生成**；先处理你遇到的 Python 导入/冻结/账本问题，再决定能否用已准备的 run |
| Scrapy041 | `case041_scrapy` | `s41r003` | `c41f002` | **B：无需生成**；核验预检和授权后执行 |
| Monitoring001 | `case101_monitor` | `m01g001` | `m01f001` | **A：先生成**；当前需生成与下游分别授权 |
| Capacity006 | `case102_capacity` | `e06g001` | `e06f001` | **A：先生成**；当前需生成与下游分别授权 |

其余 Pydantic001、Scrapy050、Pydantic004、Ops、Shark 在交付时是 `NEEDS_WORK`，先完成语义/观察桥准入，不要用假命令直接做正式收费实验。

**给你自己的最短记忆版：**

> **第一次新任务：Codex 准入 → 生成授权 → `lab.py plan` → `lab.py run` → `lab.py verify` → `pilot.py freeze` → `pilot.py plan` → 下游授权 → `pilot.py prepare` → 包装器执行 `run` → `pilot.py status` → `pilot.py analyze` → `lab.py sgb cohort` → Codex 诊断。**
>
> **已有生成 Skill：跳过生成阶段；若正式 `prepare` 也已通过，可以只做授权/冻结状态确认 → 下游 `run` → `status` → `analyze` → `cohort`。**

---

## 9. 用来核对命令的原始代码（GitHub master）

- [生成入口 `scripts/lab.py`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/scripts/lab.py)
- [生成命令定义 `src/degradation_lab/cli.py`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/src/degradation_lab/cli.py)
- [生成 gate / 配置 / 运行记录 `runner.py`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/src/degradation_lab/runner.py)
- [生成 `verify` 的工程检查 `artifacts.py`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/src/degradation_lab/artifacts.py)
- [下游 Python CLI `scripts/sgb/pilot.py`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/scripts/sgb/pilot.py)
- [下游 prepare / status / analyze `downstream_eval/sgb/pilot.py`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/downstream_eval/sgb/pilot.py)
- [统一正式协议 `clean_pair_protocol.json`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/configs/sgb/clean_pair_protocol.json)
- [Windows 运行包装器 `Invoke-Pilot.ps1`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/scripts/sgb/Invoke-Pilot.ps1)
- [正式十任务名单 `clean10.json`](https://github.com/lily400/AutoSkill-main/blob/master/degradation_failure_lab/configs/sgb/clean10.json)
- 本地交付审计：`results/sgb/audits/clean-cohort-20261027-001/DELIVERY.md`

**边界声明**：这份文件是“如何执行当前已实现的完整链条”的操作手册，不是宣称所有 SGB 任务已经即插即用，也不代表自动执行了任何付费模型。每一次正式模型调用仍必须遵守现有门禁、冻结身份和预算账本。
