# degradation_failure_lab — 文档退化与技能生成实验手册

> **README 草稿 v1（2026-10-11）**。建议作为仓库中 `degradation_failure_lab/README.md` 的新版本。本版依据当前 `master` 的命令和代码整理；本文件尚未覆盖 GitHub 原文件。

## 1. 项目目标与当前边界

本项目在**固定来源文档、固定生成配置和独立 SkillBank** 的条件下，调用官方 Anything2Skill (`AutoSkill4Doc.extract_from_doc`)，记录从文档输入到技能生成的完整过程，为后续研究**文档退化 → 错误技能 → 下游任务表现**提供可追溯的数据。

当前已具备：多案例定义、来源和输入哈希校验、Clean 真实技能生成、模型调用记录、Ingest/Extract/Compile/Register 四阶段产物、导出与规则级评价表。**尚未实现**自动退化算子、DirectDoc 与 Skill 的下游双路径执行及自动任务成功率评价。`verify` 通过不代表技能语义正确。

### 1.1 目录一览

```text
AutoSkill-main/                         # Git 仓库根目录（示例 D:\AS\AutoSkill-main）
├── AutoSkill-main/                     # 官方 Anything2Skill，不修改其生成算法
└── degradation_failure_lab/           # 本实验项目；以下所有命令在此运行
    ├── README.md                      # 本实验手册
    ├── cases/case001_qsv_select/      # case.json / conditions.json / rules.json / inputs/clean.json
    ├── configs/                        # 路径及模型、预算配置
    ├── data/                           # 来源文档、来源清单、数据目录
    ├── schemas/                        # 输入/评价等 JSON 协议
    ├── scripts/lab.py                 # 唯一命令入口
    ├── src/degradation_lab/           # 运行器、官方适配器、导出器和评价器
    ├── tests/                          # 不调用真实模型的单元测试
    ├── runs/<case>/<condition>/<run_id>/ # 每次独立运行的原始记录（本地生成）
    ├── results/exports/<run_id>/      # 对已有运行的分析导出（本地生成）
    ├── results/aggregates/            # 多运行汇总（本地生成）
    └── evaluations/                    # 规则级人工审核文件（本地生成）
```

`runs/` 与 `results/exports/`、`results/aggregates/` 是不同用途的目录：**`run` 负责生成原始产物；`verify --out` 负责分析导出；`aggregate` 负责评价汇总。** 禁止把导出文件直接写入原始运行目录。

## 2. 运行前准备（Windows PowerShell）

### 2.1 进入实验目录并确认 Python 环境

```powershell
conda activate autoskill
cd D:\AS\AutoSkill-main\degradation_failure_lab
python --version
```

使用当前 `autoskill` 环境的 `python`；无需在 README 中写死某台机器的解释器路径。

### 2.2 确认官方代码路径

`configs/environment.json` 使用项目相对路径：

```json
{"upstream_path": "../AutoSkill-main"}
```

官方代码与实验目录需要是**同级**。如果官方代码不在默认位置，可在当前 PowerShell 会话临时设置：

```powershell
$env:ANYTHING2SKILL_SOURCE = 'D:\其他位置\AutoSkill-main'
```

环境变量优先于配置文件。每次运行仍会把**实际解析后的绝对路径**写入该次 `runs/.../environment.json`，供日后复核。

### 2.3 模型密钥（仅真实运行需要）

当前 `configs/generation/deepseek_flash.json` 中的凭证变量名为 `DEEPSEEK_API_KEY`。**只在当前终端或系统环境变量中配置，不要把真实密钥写入 JSON 或提交到 GitHub。** 运行前确认：

```powershell
if ([string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) {
    Write-Host 'DEEPSEEK_API_KEY 尚未设置；只能执行离线命令。'
}
```

`run` 和 `resume` 会调用付费 API。`run` 使用当前生成配置及案例覆盖；`resume` 沿用中断运行冻结的配置，并继承累计额度。具体费用不能仅凭 Token 数量推算。

## 3. 命令速查：要做什么，用哪条？

| 目的                           | 命令                                                         | 会调用付费模型吗？ |
| ------------------------------ | ------------------------------------------------------------ | ------------------ |
| 查看已有案例                   | `python scripts/lab.py list`                                 | 否                 |
| 校验案例、输入、来源与已有评价 | `python scripts/lab.py validate`                             | 否                 |
| 检查运行计划                   | `python scripts/lab.py plan --case case001_qsv_select --condition clean --repeat 1` | 否                 |
| 运行离线单元测试               | `python -m unittest discover -s tests -v`                    | 否                 |
| **真正生成技能**               | `python scripts/lab.py run --case case001_qsv_select --condition clean --repeat 1` | **是**             |
| **Scrapy 完整重跑** | `python -B scripts/lab.py run --case case024_scrapy --condition clean --repeat 1 --run-id s24n001` | **是，从头调用** |
| **Scrapy 断点恢复** | `python -B scripts/lab.py resume --run s24m005 --run-id s24r005` | **是，仅继续未完成部分** |
| 检查已有运行                   | `python scripts/lab.py verify --run <run_id>`                | 否                 |
| **导出 4 阶段分析数据**        | `python scripts/lab.py verify --run <run_id> --out results/exports/<run_id>` | 否                 |
| 创建待审核的规则评价文件       | `python scripts/lab.py evaluation-init --run <run_id> --evaluation-id review001` | 否                 |
| 校验人工填写的评价文件         | `python scripts/lab.py evaluation-validate --file evaluations/<case>/<condition>/<run_id>/review001.json` | 否                 |
| 汇总运行与规则审核             | `python scripts/lab.py aggregate --case case001_qsv_select --out results/aggregates/case001_review` | 否                 |

说明：`--case` 和 `--condition` 可接收多个值，`--repeat N` 可重复运行，每次创建新的独立 SkillBank；这也意味着多次 API 消耗。`--run-id` 只适用于单个案例、单个条件、一次重复。

### 3.1 Scrapy：完整重跑与断点恢复

**SSL 中断后优先使用断点恢复。** 完整重跑会再次处理已经完成的窗口，并产生重复 API 消耗；两种命令不能混用。

以下命令在实验室根目录执行，沿用已配置的模型凭据：

~~~powershell
cd D:\AS\AutoSkill-main\degradation_failure_lab
~~~

#### 断点恢复：继续 s24m005（推荐）

~~~powershell
python -B scripts/lab.py resume --run s24m005 --run-id s24r005
~~~

- `--run` 是已经中断的运行 ID；`--run-id` 是本次恢复使用的全新 ID。
- 将检查点复制到 `runs/case024_scrapy/clean/s24r005/`，保留原来的 `s24m005`，不覆盖历史请求、响应和草稿。
- 对 s24m005，跳过 Outline 和前 7 个已完成窗口，保留 7 个草稿及 support，从第 8 个窗口的 Plan 继续；剩余提取完成后仍会执行编译和注册。
- 沿用中断运行冻结的模型、提示词、领域配置和输入身份；继承已消耗的 HTTP/Token 额度。新 HTTP 日志从 001 编号，父运行和累计预算记录在 `resume.json`、`execution.json`。
- 校验源码、输入、历史产物哈希和检查点身份；不匹配就停止，**不会自动退回全量重跑**。

若 s24r005 再次中断，并且仍符合完整窗口断点的恢复条件，应从最近一次运行继续，另取一个新 ID：

~~~powershell
python -B scripts/lab.py resume --run s24r005 --run-id s24r006
~~~

当前只支持单文档提取阶段、完整窗口之间的断点。若窗口内部已经成功调用 Plan/Expand，却没有完整窗口检查点，入口会拒绝自动恢复，避免重发这些成功请求。失败 POST 是否已被服务端处理或计费未知，恢复失败的那一条仍可能重复服务端工作。**断点恢复没有修复 SSL 连接本身，也不保证最终 Skill 生成成功。**

#### 完整重跑：明确需要从头生成时使用

~~~powershell
python -B scripts/lab.py run --case case024_scrapy --condition clean --repeat 1 --run-id s24n001
~~~

该命令使用当前案例与生成配置，创建全新的空 SkillBank，从 Outline 和第 1 个窗口开始。它不复用 s24m005 的 7 个草稿或检查点，已成功的模型请求也会重新调用，预算按新运行单独计算。只有确实需要一轮独立完整运行时才使用。

所有示例新 ID 都必须尚未存在；若已存在，改用另一个短 ID，不要删除或覆盖已有目录。本节只提供命令，更新 README 不会执行这些命令。

### 3.2 Scrapy Task-024：NoSkill / CleanSkill 各三次校准

**工程接入已通过；以下命令才会启动真实 Agent 并调用付费模型。** 本次使用 `s24r005` 的全部 **15 个注册 Skill 包**，不是日志中某个 `skills=2` 暂存分组。未人工挑选或修补 Skill。

~~~powershell
cd D:\AS\AutoSkill-main\degradation_failure_lab
docker start harbor-p0-control-20261018
& .\scripts\Invoke-Scrapy024Calibration.ps1 -Experiment s24d001
~~~

唯一批次顺序为 `NoSkill1 → CleanSkill1 → NoSkill2 → CleanSkill2 → NoSkill3 → CleanSkill3`。两种条件使用同一原始 Task-024 指令、Agent、模型、工具权限、禁网环境、独立 Oracle 和预算；NoSkill 安装 0 包，CleanSkill 安装冻结的 15 个完整包。

- 模型：`openai/gpt-5.4-mini-2026-03-17`，智增增端点，temperature=0，reasoning_effort=none。
- 每任务最多 6 个模型 HTTP 请求，总计最多 36 个；单请求输出最多 2048 tokens，输入估计预留每请求最多 20,000、每任务累计最多 100,000 tokens；禁止自动重试和重定向。
- 账户实际单价未知；以上为调用及 Token 控制，**不是人民币金额硬上限**。凭据复用已有 Windows DPAPI 入口，不在命令或文件中填写明文密钥。
- 结果位于 `runs/downstream/scrapy-task-024/s24d001/`：`outcomes/` 保存逐次任务与规则判分、正文曝光、Token、耗时和失败类别；`trials/` 保存原生轨迹和工具日志；`budget.sqlite3` 记录持久化调用额度。
- 批次是一次性的。中断或重复执行时会拒绝重发；保留原记录，不要删除 `batch.started`、预算数据库或换 ID 绕过限制。环境、传输或预算失败时停止；普通任务答错仍作为校准结果记录。
- 本轮预检中的正例19/19、FTP反例18/19，以及受控正文读取，都是**无模型工程证据**，不是 Agent 对照结果。真实正文曝光需要内核读取事件与实际成功模型请求中的正文共同确认，不能从安装成功推断。

只核验已经准备好的冻结文件、不调用模型：

~~~powershell
python -B scripts/scrapy024.py prepare --experiment s24d001
~~~

就绪报告：`results/analysis/scrapy_task024_downstream_readiness.md`。本批次只是 Clean 校准，不构成正式文档退化实验。

## 4. 完整示例：从 `case001_qsv_select` 的 Clean 文档生成并分析技能

下面的操作顺序以已成功运行的案例为教学样本。你也可以用相同命令新跑一次；**新运行的 ID 应以终端返回的 `RUN_DIRECTORY` 为准，不要沿用下面的历史示例 ID。**

### Step 0 — 先理解输入（不跑模型）

打开：

1. `data/raw_sources/qsv/<commit>/select.md`：固定的 qsv select 原始文档。
2. `data/manifests/qsv_select.json` 和 `data/catalog.json`：来源、Commit、SHA-256 和数据集登记。
3. `cases/case001_qsv_select/case.json`：案例、来源及生成配置引用。
4. `cases/case001_qsv_select/conditions.json`、`inputs/clean.json`：当前实验条件和具体输入路径。
5. `cases/case001_qsv_select/rules.json`：研究人员整理的 R1–R7 检查表，**不作为额外提示传入生成模型**，也不是官方论文提供的黄金标注。

要回答：**我到底使用哪份原文？哪一个条件？哪些规则用于后续人工评价？**

### Step 1 — 校验环境与实验计划（不跑模型）

```powershell
python scripts/lab.py list
python scripts/lab.py validate
python -m unittest discover -s tests -v
python scripts/lab.py plan --case case001_qsv_select --condition clean --repeat 1
```

重点检查 `validate` 的 `status`、`upstream_path`，以及 `plan` 的 `case_id`、`condition_id`、`input_count`、`model`、`output_pattern`。Windows 下运行前还有已知深层路径长度预检。

### Step 2 — 真实生成（付费；只在确认配置后执行）

```powershell
python scripts/lab.py run --case case001_qsv_select --condition clean --repeat 1
```

预期过程：**Ingest（读文档）→ Extract（证据与技能草稿）→ Compile（技能规范）→ Register（正式注册并写入 SkillBank）**。

示例已成功运行：

- Case：`case001_qsv_select`；Condition：`clean`。
- Run ID：`raecd75e08b34`。
- 日志显示：**2 个窗口、4 条 SupportRecord、4 个 SkillDraft、4 个编译技能、4 个正式注册技能，18 次成功 HTTP 调用**。
- 最终终端返回 `exit_code: 0`。这代表程序成功结束，**不代表四个技能都正确**。

新运行一定会产生新的 Run ID。运行记录位于：

```text
runs/case001_qsv_select/clean/<run_id>/
```

### Step 3 — 先看原始运行记录（不跑模型）

以下使用成功案例 `raecd75e08b34`，如换新运行请修改变量：

```powershell
$runId = 'raecd75e08b34'
$run = ".\runs\case001_qsv_select\clean\$runId"
```

按顺序查看：

| 查看什么       | 打开的位置                                                  | 应该回答的问题                        |
| -------------- | ----------------------------------------------------------- | ------------------------------------- |
| 实际输入       | `$run\inputs\input001\select.md`                            | 运行时读入的是哪一份文档？            |
| 输入身份与哈希 | `$run\input_manifest.json`                                  | 是否与原文对应，是否被改动？          |
| 实际模型与预算 | `$run\config.json`                                          | 使用了什么生成配置？                  |
| 官方总结果     | `$run\official_result.json`                                 | 官方返回 completed 吗？包含几个技能？ |
| 过程日志       | `$run\pipeline.log`                                         | 四阶段分别做了什么、是否报错？        |
| 调用量         | `$run\execution.json`、`$run\model_calls.json`              | 调用了几次模型、Token 消耗多少？      |
| 每次请求和响应 | `$run\http\001\request.json`、`response.json`、`event.json` | 有疑问时，模型具体收到和返回了什么？  |

**原始生成过程的四阶段结果**存于官方 SkillBank 目录：

```powershell
Get-ChildItem "$run\SkillBank\.runtime\intermediate_runs" -Recurse -Filter result.json |
    Select-Object -ExpandProperty FullName
```

应重点识别这些文件（中间还有一个官方生成的独立中间运行 ID）：

```text
SkillBank/.runtime/intermediate_runs/<intermediate_id>/
├── ingest/result.json      # DocumentRecord、TextUnit、Window
├── extract/result.json     # SupportRecord、SkillDraft
├── compile/result.json     # SkillSpec
└── register/result.json    # 版本决策及注册结果
```

**查看最终正式存储的程序技能：**

```powershell
Get-ChildItem "$run\SkillBank\Users" -Recurse -Filter SKILL.md |
    Select-Object -ExpandProperty FullName
```

注意：`SkillBank` 的可见导航层可能有额外的父级或导航 `SKILL.md`；**不要按整个文件夹里 `SKILL.md` 的物理个数计算独立注册技能数**。

### Step 4 — 验证并导出（不跑模型）

先看工程检查：

```powershell
python scripts/lab.py verify --run raecd75e08b34
```

关注 `status`（`PASS` / `PARTIAL`）、`checks`、`counts`、`missing_states`、`quality_status`。工程检查报告中的 `PASS` 只能表明当前定义的可追溯性、文件和阶段等校验通过，**不能证明 SKILL.md 的规则内容正确**。`PARTIAL` 会使 CLI 返回非零退出码，需要看具体失败的 `checks`，不要擅自把它当成技能质量分数。

如果需要导出分析文件：

```powershell
python scripts/lab.py verify --run raecd75e08b34 --out results/exports/raecd75e08b34
```

导出由本项目的 `artifacts.py` 读取已有记录生成，**不再次调用模型**；原始 `runs/` 不会因此重新生成技能。

```text
results/exports/raecd75e08b34/
├── verification.json              # 工程校验报告
├── documents.json                 # 文档记录
├── text_units.json                # 解析出的文本单元
├── windows.json                   # 内容窗口
├── window_source_alignment.json   # 窗口文本与源文档行的近似匹配
├── support_records.json           # 支持证据记录
├── skill_drafts.json              # 初始技能草稿
├── skill_specs.json               # 编译后的技能规范
├── registration.json              # 版本注册结果
├── traceability.json              # 来源/窗口/证据/草稿/规范/技能 ID 关联
└── skill_files.json               # 正式程序技能路径和物理文件数量
```

推荐第一次按此顺序阅读：

`inputs/select.md → windows.json → support_records.json → skill_drafts.json → skill_specs.json → registration.json → 最终 SKILL.md → traceability.json`。

提醒：`window_source_alignment.json` 是文本匹配辅助信息，`traceability.json` 是记录 ID 的关联；**它们不自动验证规则语义正确，也不是人工金标准**。

### Step 5 — 追踪一条具体规则（不跑模型）

以 `rules.json` 的 **R1** 为例：原文区分 `1,4`（第 1 和第 4 列）与 `1-4`（前四列）。

1. 打开输入 `select.md`，对照 R1 中记录的原文证据行号。
2. 打开 `windows.json`，检查该规则是否进入了官方窗口。
3. 打开 `support_records.json`，检查证据摘录有没有正确包含该语义。
4. 打开 `skill_drafts.json`，检查草稿是否遗漏或改写出错。
5. 打开 `skill_specs.json` 和最终 `SKILL.md`，检查是否把 `1,4` 错写成了 `1-4` 等。
6. 利用 `traceability.json` 提供的 ID 路径回溯；如仍不确定，可打开对应的 `http/<序号>/request.json` 和 `response.json` 排查模型输出。

**不是每条规则都一定会被提取成单独的技能。** 规则可以映射到同一技能，也可能未被保留。必须把“没有映射”“语义错误”“没有人工审核”区分开。

### Step 6 — 生成并填写人工审核表（不跑模型）

```powershell
python scripts/lab.py evaluation-init --run raecd75e08b34 --evaluation-id review001
```

这条命令只创建**待审核**的文件：

```text
evaluations/case001_qsv_select/clean/raecd75e08b34/review001.json
```

随后人工打开 `review001.json`，逐条查看 R1–R7，并按证据填写：

- `status`：`unreviewed`、`correct`、`incorrect` 或 `uncertain`；不能把未审自动算作正确。
- `skill_ids`：被评价规则对应的真实注册 Skill ID，从 `traceability.json` 查找；无法映射时保留空数组。
- `trace_refs`：实际存在且属于对应技能关联链的窗口/证据/草稿/规范/技能 ID。
- `generated_evidence`：最终 SKILL.md 中支持该判断的真实行号。
- `error_types`：只填写协议允许的类别，如 `rule_omission`、`parameter_mismatch`、`unsupported_addition` 等。
- `notes`：说明根据哪些原文与生成文本作出判断。

所有字段必须与 `schemas/evaluation.schema.json` 对应。**不要通过命令自动改成 `correct`；必须实读原文和技能内容。** 同一个 `evaluation_id` 不允许覆盖已存在的文件，需要新审核版本时使用新 ID。

编辑完成后执行：

```powershell
python scripts/lab.py evaluation-validate --file evaluations/case001_qsv_select/clean/raecd75e08b34/review001.json
```

该命令检验格式、ID 关联、证据行号等一致性，**不代替人工语义审查**。

### Step 7 — 汇总规则审核（不跑模型）

```powershell
python scripts/lab.py aggregate --case case001_qsv_select --out results/aggregates/case001_review
```

查看输出：

- `results/aggregates/case001_review/runs.json`：工程级各运行结果。
- `results/aggregates/case001_review/rule_results.json`：各运行的规则审核明细。
- `results/aggregates/case001_review/rule_results.csv`：供 Excel / pandas 分析的表格。

`aggregate` 不会自动生成准确率，也不会把尚未审核的规则当成正确。以后增加不同条件、多次重复运行时可以继续汇总，但必须明确哪些评估已经完成人工审核。

## 5. 常见问题及处理

| 现象                                                         | 常见原因与检查顺序                                           |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `Official code inventory is empty` / `Official Anything2Skill source not found` | 检查 `configs/environment.json` 的 `../AutoSkill-main`、两个目录是否同级，以及是否设置了错误的 `ANYTHING2SKILL_SOURCE`。先运行 `validate`。 |
| Windows 的 `FileNotFoundError` 指向很深的 `SkillBank/.runtime/.../extract/windows/*.json` | 可能是 Windows 路径长度限制；使用短路径仓库，先运行 `plan`，避免重新付费后再报错。 |
| `BLOCKED: set environment variable DEEPSEEK_API_KEY`         | 真实运行前缺少 API 凭证；不会因为这个错误完成技能生成。      |
| `run` 返回非零退出码                                         | 保留该次运行，检查 `exception.json`（如有）、`execution.json`、`pipeline.log`、HTTP 事件；不要直接删除重跑。 |
| `verify` 是 `PARTIAL`                                        | 查看 `verification.json` 的具体 `checks`，这不等于自动判定生成技能不正确。 |
| `evaluation-init` 报文件已存在                               | 已有相同 `evaluation_id`；继续编辑旧文件或新建 `review002` 等版本，不覆盖历史审核。 |
| `aggregate` 中仍是 `unreviewed`                              | 尚未完成审核是正常情况，不能据此得出生成质量结论。           |

## 6. 新案例如何复用框架？

当前真正登记的案例是 `case001_qsv_select`。增加 `case002` 时通常需要：

1. 若是新的来源文档，先在 `data/raw_sources/` 保存原始快照、在 `data/manifests/` 声明来源信息，并登记到 `data/catalog.json`。
2. 新建 `cases/case002_<name>/`，按现有模式填写 `case.json`、`conditions.json`、`rules.json`、`inputs/clean.json`。目前没有可用的自动 `init-case` 命令。
3. 运行 `validate → plan → run → verify --out → evaluation-init → evaluation-validate → aggregate`。不用为每个案例重新编写一套导出程序。
4. 若以后加入 `degraded` 条件，必须先**实际生成退化输入文档**、注册条件和输入哈希，不能仅通过把条件名字写成 `degraded` 就认为实验已完成退化处理。

## 7. 实验记录原则及历史说明

- 每次 `run` 都创建独立的输入快照和空 SkillBank；不要在原始 `runs/<...>/` 下直接编辑生成结果。
- `results/exports/` 是可再生的分析视图；`runs/` 是原始证据，应优先保留。
- `rules.json` 是分析者的审核清单，不是给生成模型的提示，也不应被表述为官方论文的金标准。
- 已证明 Clean 技能生成流程真实跑通，但**尚未证明文档退化导致任务风险变化，更未完成 DirectDoc vs Skill 下游实验**。
- 历史 P0/P0.1/P0.2 提交保留在 [`archive/p0-p02-full-20261011`](https://github.com/lily400/AutoSkill-main/tree/archive/p0-p02-full-20261011)；归档只保证已有 Git 提交保留，不承诺旧格式 run 可直接在新框架验证。
- 代码层次进一步说明见 [`docs/PROJECT_STRUCTURE_GUIDE.md`](docs/PROJECT_STRUCTURE_GUIDE.md)；项目中唯一正式的实验命令入口为 `scripts/lab.py`。

---

**一次标准运行的检查清单**：

- [ ] `validate`、单元测试、`plan` 通过。
- [ ] 明确本次付费模型配置，记录新 `run_id`。
- [ ] 查看 `pipeline.log` 与 `official_result.json`。
- [ ] 查看四阶段 `result.json` 与真实 `SKILL.md`。
- [ ] 执行 `verify --out` 并检查 `verification.json`。
- [ ] 人工审查 R1–R7，填写并验证 `evaluation` 文件。
- [ ] 执行 `aggregate`，明确尚未审核的记录。

## P0 下游零模型验证

运行 `python scripts/lab.py downstream-check --section all`。实现、固定版本和未验证边界见 [downstream_eval/README.md](downstream_eval/README.md)。返回码 2 表示 BLOCKED，不能视为通过。该命令不会调用生成模型或 Agent 模型。


## GitChameleon 144/164 接入（2026-10-22）

仅新增两个原题及三条件配置。完整题库、答案和测试在 `.external/gitchameleon/`；Agent只接收选题公开投影。入口、目录职责与验收状态见 `docs/research/gitchameleon_import_2026-10-22/gitchameleon_import_report.md`。`case144_gch`、`case164_gch` 的付费运行受 `configs/gitchameleon_pilot/gates.json` 保护；所有前置验收通过前不会运行。


### 固定的API凭证读取入口

凭证配置统一保存在 `configs/credentials.json`。智增增密钥仍使用已存在的Windows CurrentUser DPAPI加密文件，不写入JSON或永久明文环境变量。新终端无需重新输入。

零请求检查：`& .\scripts\Invoke-ProjectCredential.ps1 -CheckOnly`

经授权的命令：`& .\scripts\Invoke-ProjectCredential.ps1 -Action { <运行已验收的命令> }`。入口在内存中设置子进程所需环境变量，结束后恢复；不会自行调用API。生成器与Agent仍受各自验收门和预算约束。

本轮固定试跑入口：`& .\scripts\Invoke-GitChameleonPilot.ps1`；`-CheckOnly`只验证凭证。入口自动加载凭证并保留单次锁，已运行的批次不会被默默重发。
