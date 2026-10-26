# Task003：Sanctuary Clean 全流程 PowerShell 执行手册

本手册针对已经选定的真实任务 `sanctuary_endgame_scheduler_002`，配套[准入审计](task003-clean-admission.md)。项目根目录为 `D:\AS\AutoSkill-main\degradation_failure_lab`。命令依据当前代码、CLI help 和零模型运行验证，日期 2026-10-26。

**当前交付停在零模型验收。阶段 3 的真实生成和阶段 5 的付费下游均未获授权，门禁为 BLOCKED。** 本手册给出获批之后的实际命令；不要把“下面有命令”理解成预算已经批准。没有获得批准时执行授权检查会停止，这是预期结果。不要手动把 gate 改为 PASS 来排错。

## 固定身份、协议与目录

| 项目 | 本手册固定值 |
|---|---|
| task_id / task_key | `sanctuary_endgame_scheduler_002` / `t-febd929cffec` |
| case / condition | `case003_san` / `clean` |
| 唯一源文 | `data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md` |
| 原文及 clean 输入 SHA-256 | `7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c` |
| 生成运行 | `sn3g001`，一次；目录 `runs/gen/sgb/case003_san/clean/sn3g001/` |
| 下游批次 | `sn3e001`，NoSkill1 一次，然后 CleanSkill1 一次 |
| 下游根目录 | `runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/` |
| Skill 质量审核 | `evaluations/case003_san/clean/sn3g001/pre_downstream.json` |
| pilot 分析 | `results/sgb/analyses/sn3e001/` |
| 差分归因报告 | `results/sgb/attributions/sn3e001-v1/` |
| 最终基线报告 | `results/sgb/baselines/sn3e001/baseline.md` |

两组采用**相同的条件式正文读取说明**：存在相关 Skill 时必须在实现前读完相关 SKILL.md；没有 Skill 时按题目求解。NoSkill 的 Skill 列表与目录为空，不能向其额外提供本轮源文、规则检查表或 Skill。此批属于要求正文读取的配对协议，不能与早期自主读取结果直接拼接。

同一 runtime-note 还明确 `end_trigger.conditions_met` 按已公开的条件编号 1、2、3 升序输出，解决原指令未规定列表顺序、Oracle 却逐项比较的问题；不透露 4／10／5 常量。这份接口澄清与正文读取要求均属于两组共同冻结的输入。

公共 pilot 当前一次运行固定一对条件，不支持独立重启某一组。因此阶段 5 的唯一付费运行命令会依次执行 **NoSkill1 → CleanSkill1**；阶段 6 检查已执行的 CleanSkill，绝不再次运行 `run`。重复次数一组一次；这只是首个 pilot，不估计稳定成功率或显著性。

报告 schema_version=2 将四类状态分开：

| 字段 | 含义 |
|---|---|
| `experiment_execution_status` | `completed/partial/not_started`，依据两组真实 trial 结束、提交绑定和原 Oracle 有效评分，不要求任务成功、读正文或机制证据齐全 |
| `skill_usage_status` | 每组复用原 usage 状态；仅索引、正文确认、日志未知分别保留，不能从缺日志断言未读 |
| `task_success` | 每组真实有效 Oracle 评分为 true/false；没有有效评分为 null，不补造失败分数 |
| `attribution_status` | `pending_review/insufficient_evidence/reviewed/not_comparable`；七阶段名称齐全但证据 unknown 仍是不足，reviewed 也不等于已验证因果 |

`comparability` 独立保留 eligible/ineligible/unknown。两组执行完成而控制变量不一致时，执行可 completed、比较仍 ineligible。任务失败不代表归因完成，正文读取也不自动证明理解或遵循。只有真实受控干预及差分证据满足原验证契约，才能使用 intervention_supported。

首次执行按编号推进；所有 `$LASTEXITCODE` 检查必须保留。目录已经存在时先判断是否已执行到该步骤，继续读取已有证据；不要删除目录、重置 ledger、换 ID 自动补跑或覆盖报告。新 ID 和新增调用需要新方案及明确授权。

## 阶段 0：运行前检查

### 0A — 进入真实目录并固定 Windows Python

- **当前目标**：使用已验证的 Conda base Python 3.13.9；消除 PATH 误选。
- **执行位置**：任意 PowerShell，命令会切到研究根目录。
- **完整命令**：

```powershell
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
Set-Location -LiteralPath 'D:\AS\AutoSkill-main\degradation_failure_lab'
& 'D:\anoconda1\shell\condabin\conda-hook.ps1'
conda activate base
$Task003Python = 'D:\anoconda1\python.exe'
Get-Location
$env:CONDA_DEFAULT_ENV
& $Task003Python -B -c "import pathlib,sys,tomllib,numpy,httpx,pydantic; assert pathlib.Path(sys.executable).resolve()==pathlib.Path(r'D:\anoconda1\python.exe').resolve(); assert sys.version_info[:2]==(3,13); print(sys.executable); print(sys.version)"
if ($LASTEXITCODE -ne 0) { throw '0A Python preflight failed' }
python -B -c "import sys; assert sys.executable.lower()==r'D:\anoconda1\python.exe'.lower(); print('PowerShell wrapper Python: PASS')"
if ($LASTEXITCODE -ne 0) { throw '0A PATH differs from the validated interpreter' }
```

- **预期结果**：工作目录正确、Conda 为 base，两次 Python 身份检查通过。
- **成功标准**：两个退出码为 0。Linux Harbor 使用另一份既有 `/opt/harbor-venv/bin/python`，由公共启动器管理。
- **失败处理**：停止。`autoskill` 环境本轮实测缺少 `tomllib`，不能直接替代；不要靠忽略异常继续。若本机环境已变，先重新验证依赖和 Python 身份。
- **下一步**：0B。后续命令在同一 PowerShell 会话运行，沿用 `$Task003Python`。

### 0B — 检查工作树、ID 冲突并保存历史保护快照

- **当前目标**：保留已有修改和历史产物；验证预留 ID 尚未被使用。
- **执行位置**：`D:\AS\AutoSkill-main\degradation_failure_lab`。
- **完整命令**：

```powershell
git -C 'D:\AS\AutoSkill-main' status --short
if ($LASTEXITCODE -ne 0) { throw '0B Git status failed' }
@(
  'runs/gen/sgb/case003_san/clean/sn3g001',
  'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001',
  'results/sgb/analyses/sn3e001',
  'results/sgb/attributions/sn3e001-v1',
  'results/sgb/baselines/sn3e001'
) | ForEach-Object { if (Test-Path -LiteralPath $_) { throw "Existing target; inspect before continuing: $_" } }
& $Task003Python -B scripts/sgb/sanctuary002.py history-start --audit-id task003-preflight-sn3g001
if ($LASTEXITCODE -ne 0) { throw '0B history snapshot failed' }
```

- **预期结果**：Git 展示真实已有变更；新增 `results/sgb/audits/task003-preflight-sn3g001/history.json`，状态 SNAPSHOT。
- **成功标准**：没有目标冲突，快照列出 runs/results/evaluations 已有文件哈希。不会要求工作树全净，也不会 reset 用户改动。
- **失败处理**：若已有目标，不运行后面的生成／run；先读取其 status。若历史快照已存在，保留并使用 `history-check`，不要重建它。Git 中本来已有的历史文件修改不属于本轮可清理范围。
- **下一步**：0C。

### 0C — 核对控制环境、任务门禁和凭据可用性

- **当前目标**：确认任务配置、固定镜像和当前预算状态；只检查凭据是否存在。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
$Task003ControlRunning = docker inspect harbor-p0-control-20261018 --format '{{.State.Running}}'
if ($LASTEXITCODE -ne 0 -or $Task003ControlRunning.Trim() -ne 'true') { throw '0C control environment unavailable or stopped' }
Write-Output $Task003ControlRunning
docker image inspect sha256:c928e232c35008c42b22727ecd2fe39ed79fe9cb36ebddca669daef309d6b4e4 sha256:b1c9205374a4ac830bef05b2715185845097c3457ab5f216d437381735c9c1c9 --format '{{.Id}} {{.Os}}/{{.Architecture}}'
if ($LASTEXITCODE -ne 0) { throw '0C pinned image unavailable' }
Get-Content -LiteralPath configs/tasks/sgb/sanctuary_endgame_scheduler_002.json -Raw
Get-Content -LiteralPath data/manifests/sgb/gates/t-febd929cffec.json -Raw
& $Task003Python -B scripts/sgb/pilot.py status --task sanctuary_endgame_scheduler_002 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '0C budget status failed' }
& scripts/Invoke-ProjectCredential.ps1 -CheckOnly
if (-not (Test-Path Env:DEEPSEEK_API_KEY)) {
  $env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User')
}
[ordered]@{ DeepSeekCredentialAvailable = -not [string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY) } | ConvertTo-Json
```

- **预期结果**：控制容器 true、镜像身份与上表一致；初次状态 NOT_PREPARED；gate BLOCKED；凭据检查只输出可用性。
- **成功标准**：静态／Docker 环境可读，无新 ledger 或模型请求。BLOCKED 本身不阻止阶段 1–2。
- **失败处理**：控制容器 false／镜像缺失时停止接入验收，先恢复既有环境；不能临时换镜像。没有凭据时先核查 `configs/credentials.json` 中指定的安全加载方式，不打印 key。DeepSeek 检查为 false 时必须在阶段 3 前解决。
- **下一步**：1A。当前没有任务三授权余额，不能直接进入付费步骤。

## 阶段 1：任务准入审核

### 1A — 验证源文、任务绑定与规则位置

- **当前目标**：确认真正输入和选题依据，防止把 task.json 或参考答案当作文档。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py audit
if ($LASTEXITCODE -ne 0) { throw '1A asset/source binding failed' }
Get-Content -LiteralPath docs/sgb/task003-clean-admission.md -Encoding UTF8
Get-Content -LiteralPath cases/sgb/case003_san/inputs/clean.json -Raw
Get-FileHash -Algorithm SHA256 -LiteralPath data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md
$Task003Source = Get-Content -LiteralPath data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md -Encoding UTF8
38,94,95,162,233,308 | ForEach-Object { '{0}: {1}' -f $_,$Task003Source[$_ - 1] }
Get-Content -LiteralPath downstream_eval/tasks/sgb/audited/sanctuary_endgame_scheduler_002/instruction.md -Encoding UTF8
```

- **预期结果**：audit PASS、1 个 clean 输入、原文 SHA 与固定值一致；源文给出 4／10／5、顺时针额外回合及立即结束条件。
- **成功标准**：审核者认可准入报告对源文、任务和 Oracle 范围的判断，尤其 trigger-turn-only 的洗牌字段定义。
- **失败处理**：哈希异常、source/task 不一致或对范围存在实质异议时停止，不能修改源文或预期结果凑通过。审核报告在 `docs/sgb/task003-clean-admission.md`，机器全量筛选在 `results/sgb/audits/task003-clean-20261026-001/candidate-screen.json`。
- **下一步**：1B。

### 1B — 阅读原 Oracle 与独立 expected-output 审核表

- **当前目标**：核实评分只使用 8 个确定性原始用例，没有 LLM judge 或自由解释文本匹配问题。
- **执行位置**：研究根目录；这是研究者审核，不在 Agent 容器中执行。
- **完整命令**：

```powershell
Get-Content -LiteralPath downstream_eval/tasks/sgb/audited/sanctuary_endgame_scheduler_002/task.original.toml -Raw
Get-Content -LiteralPath downstream_eval/tasks/sgb/audited/sanctuary_endgame_scheduler_002/oracle/eval.py -Encoding UTF8
& $Task003Python -B -c "import json,pathlib; b=json.loads(pathlib.Path('downstream_eval/tasks/sgb/audited/sanctuary_endgame_scheduler_002/oracle/testcases.json').read_text(encoding='utf-8')); print('cases=',len(b['test_cases'])); print('setup=',b['setup_code']); print(b['solution_code']); [print(i,c['input'],c['expected_output']) for i,c in enumerate(b['test_cases'],1)]"
if ($LASTEXITCODE -ne 0) { throw '1B bundle inspection failed' }
Get-Content -LiteralPath tests/test_sgb_sanctuary002.py -Encoding UTF8
```

- **预期结果**：原比较器递归检查精确结构和玩家字符串，数字使用原容差；8 个完整输出与独立人工表一致。
- **成功标准**：每个目标常量能映射到预期输出；没有将参考自洽性冒充独立正确性。原 task.toml 的 `light` 只是发布标签，本地 runtime.lock 固定真实镜像。
- **失败处理**：若发现契约冲突或预期输出错误，撤回 GO 并停止。不要执行 `original_eval.py`、原生成辅助程序或未经审查的原 shell runner；它们不用于本地评分。
- **下一步**：2A。

## 阶段 2：接入与零模型验收

### 2A — 执行确定性任务／对照／门禁测试

- **当前目标**：验证资产绑定、源文篡改拒绝、原用例表、两组附加指令相同及未授权执行阻断。
- **执行位置**：研究根目录；命令在既有 Linux 控制环境运行 Python 测试。
- **完整命令**：

```powershell
docker exec --env 'PYTHONPATH=/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab:/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/src' --env LITELLM_LOCAL_MODEL_COST_MAP=True harbor-p0-control-20261018 /opt/harbor-venv/bin/python -B -m unittest discover -s /run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/tests -p test_sgb_sanctuary002.py -v
if ($LASTEXITCODE -ne 0) { throw '2A deterministic tests failed' }
& $Task003Python -B scripts/lab.py plan --case case003_san --condition clean --repeat 1
if ($LASTEXITCODE -ne 0) { throw '2A upstream plan/path guard failed' }
```

- **预期结果**：测试 OK；plan 显示 1 个输入、`deepseek-flash`、正确输出模式，模型调用为零。
- **成功标准**：当前任务测试全部通过，Windows 路径门禁通过。此前长案例名与 `autoskill` Python 的失败已在当前命令中解决。
- **失败处理**：保存错误并停止；不能跳过 Windows 路径保护或换未审核 Python。
- **下一步**：2B。

### 2B — 执行 Oracle 正负例、网络及数据边界验收

- **当前目标**：运行纯工程候选，验证原断言敏感性与可信评分隔离。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py acceptance --audit-id task003-sanctuary-zero-user001
if ($LASTEXITCODE -ne 0) { throw '2B isolated acceptance failed' }
Get-Content -LiteralPath results/sgb/audits/task003-sanctuary-zero-user001/acceptance.json -Raw
Get-ChildItem -LiteralPath results/sgb/audits/task003-sanctuary-zero-user001 -Filter '*-network.json' -Recurse | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }
```

- **预期结果**：correct 8/8；wrong_objective_threshold 1/8；wrong_trigger_marker 1/8；wrong_last_marker 3/8；最终 PASS、model_calls=0、real_agent_outcome=false。candidate 和 scorer 各自网络探针 PASS。
- **成功标准**：逐个失败的 pytest 名称与夹具声明一致；提交／Oracle 哈希绑定成立，bridge 声明不导入候选。保存 `commands.json`、`envelope.json`、`verdict/junit.xml`。
- **失败处理**：目录已存在就读取已有结果，不能覆盖；失败查看该夹具 `result.json`、`pytest.stdout.txt`、network 报告及 commands。任何隔离失败都阻断真实执行。
- **下一步**：2C。

### 2C — 核验注册表及预算仍未被启用

- **当前目标**：确认接入未产生真实 trial 或新的付费授权。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/lab.py sgb audit
if ($LASTEXITCODE -ne 0) { throw '2C registry integrity failed' }
& $Task003Python -B scripts/sgb/pilot.py status --task sanctuary_endgame_scheduler_002 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '2C status failed' }
& $Task003Python -B scripts/sgb/sanctuary002.py history-check --audit-id task003-preflight-sn3g001
if ($LASTEXITCODE -ne 0) { throw '2C historical files changed' }
```

- **预期结果**：注册表完整性 PASS，初次下游 NOT_PREPARED，历史检查 PASS。
- **成功标准**：明确这只代表工程接入通过；尚未真实提取 Skill，尚未执行 Agent，更不能说 NoSkill/CleanSkill 已成功。
- **失败处理**：任何历史文件变化先查明，不恢复、覆盖或重新初始化预算。
- **下一步**：在获得**生成预算明确批准**后执行 3A；未批准就停在这里。

## 阶段 3：Anything2Skill 正式提取（付费，当前阻断）

### 3A — 核对本次生成授权与凭据

- **当前目标**：核对 `sn3g001` 的生成预算、配置哈希及批准来源。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py authorization --authorization-phase generation --generator-run sn3g001
if ($LASTEXITCODE -ne 0) { throw 'STOP: Task003 generation is not authorized' }
if ([string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) { throw 'STOP: configured DeepSeek credential is unavailable' }
if (Test-Path -LiteralPath runs/gen/sgb/case003_san/clean/sn3g001) { throw 'STOP: generation ID already exists' }
```

- **预期结果**：当前交付时为 BLOCKED 并停止；获批后为 AUTHORIZED。
- **成功标准**：批准记录明确本次 case/clean/run-id、生成配置哈希、一次生成的 HTTP／token 上限，并以 gate 的 `requested_generation.approval_evidence.file/sha256` 绑定可追溯人工批准记录。该记录由审批后另行维护，不由本手册自动创建。
- **失败处理**：不要把配置中的 150 HTTP／450000 观测 token 当作批准。批准不足、配置漂移、ID 冲突均停止，重新提交具体额度审核；不能自动增加 budget 或 resume。
- **下一步**：3B。

### 3B — 一次正式入口完成生成管线

- **当前目标**：只从 clean 原文生成 Skill。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py authorization --authorization-phase generation --generator-run sn3g001
if ($LASTEXITCODE -ne 0) { throw 'STOP: generation gate failed' }
& $Task003Python -B scripts/lab.py run --case case003_san --condition clean --repeat 1 --run-id sn3g001
if ($LASTEXITCODE -ne 0) { throw 'Generation stopped; preserve sn3g001 and inspect 3C' }
```

- **预期结果**：`runs/gen/sgb/case003_san/clean/sn3g001/` 出现 input/config/upstream 快照、SkillBank、中间产物、HTTP 请求响应、pipeline.log、official_result.json、status.json、execution.json 和 artifact_manifest.json。
- **成功标准**：官方管线内部完成 ingest→extract→compile→register；只有 1 个 `context.md` 输入，原字节保持。没有独立 `ingest`、`extract`、`compile` 或 `register` CLI 命令。
- **失败处理**：不重跑此命令，不修改同一个 run。supports=0／drafts=0：看 ingest/result 与 extract/windows、pipeline.log，作为生成失败保留；编译／注册失败：看相邻阶段和 HTTP 响应。请求中断、预算停止、使用量未知：停止，保留执行记录，另行审核恢复方案与累计预算。本手册没有授权 resume。
- **下一步**：无论成功或中止先执行 3C；只有生成工程链完整且有可用包，才能进入阶段 4；语义质量另行如实记录。

本题是单文档，使用 `cases/sgb/case003_san/inputs/clean.json` 指定的完整 108565-byte 原文，不按问题拆分或去重。窗口筛选由当前 Anything2Skill 配置决定。公共框架虽支持多文档，但本任务不使用；增加文档会改变条件、配置和预算，必须另审。

### 3C — 检查结束状态和调用账目

- **当前目标**：区分正式完成、内容空缺和中途退出。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
Get-Content -LiteralPath runs/gen/sgb/case003_san/clean/sn3g001/status.json -Raw
Get-Content -LiteralPath runs/gen/sgb/case003_san/clean/sn3g001/execution.json -Raw
Get-Content -LiteralPath runs/gen/sgb/case003_san/clean/sn3g001/pipeline.log -Tail 70
& $Task003Python -B scripts/lab.py verify --run sn3g001
if ($LASTEXITCODE -ne 0) { throw 'STOP: generation is partial or invalid; do not run downstream' }
```

- **预期结果**：verify PASS；`recorded_official_status=completed`，windows/supports/drafts/compiled_specs/registered_skills 非零；关键模型阶段和实体链接检查通过；execution 保留实际 HTTP／usage_totals。
- **成功标准**：工程链完整，没有 errors 或中断；保存的 token 是观测使用量，不是已批准余额或准确货币成本。
- **失败处理**：文件缺失或 verify PARTIAL 时停止；读取 exception.json（若存在）、execution.json、HTTP 状态、预算阈值。不把失败当作可用 CleanSkill。
- **下一步**：4A。verify PASS 仍不代表规则内容正确。

## 阶段 4：注册、冻结和上游质量审查

### 4A — 导出各阶段证据，核对正式注册

- **当前目标**：保留规则追踪所需材料，避免在不可变生成目录内添加分析文件。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
if (Test-Path -LiteralPath results/sgb/upstream/sn3g001/exports) { throw 'Exports exist; inspect instead of overwriting' }
& $Task003Python -B scripts/lab.py verify --run sn3g001 --out results/sgb/upstream/sn3g001/exports
if ($LASTEXITCODE -ne 0) { throw '4A generation evidence export failed' }
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/traceability.json -Raw
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/registration.json -Raw
& $Task003Python -B scripts/lab.py evaluation-init --run sn3g001 --evaluation-id pre_downstream
if ($LASTEXITCODE -ne 0) { throw '4A review already exists or initialization failed' }
```

- **预期结果**：生成 verification/documents/text_units/windows/support_records/skill_drafts/skill_specs/registration/traceability/window_source_alignment 等 JSON，以及 4 条未审核目标规则记录。
- **成功标准**：正式注册已在生成过程中完成；导出的是最终活动版本。不要额外手工注册或重新调用模型“补全”这个 run。
- **失败处理**：如最终活动 document_registry 与 register 导出不一致，freeze 会阻断，先审计；不能悄悄选择一个旧正文继续。
- **下一步**：4B。

### 4B — 人工审核源文到最终正文的规则保留

- **当前目标**：审查 4／10／5、顺序、条件与例外，记录规则缺失和无依据内容。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/windows.json -Raw
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/support_records.json -Raw
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/skill_drafts.json -Raw
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/skill_specs.json -Raw
Get-Content -LiteralPath results/sgb/upstream/sn3g001/exports/skill_files.json -Raw
Get-ChildItem -LiteralPath runs/gen/sgb/case003_san/clean/sn3g001/SkillBank/Users -Filter SKILL.md -Recurse | ForEach-Object { $_.FullName; Get-Content -LiteralPath $_.FullName -Encoding UTF8 }
Get-ChildItem -LiteralPath runs/gen/sgb/case003_san/clean/sn3g001/SkillBank/Users -File -Recurse | Get-FileHash -Algorithm SHA256 | Select-Object Path,@{Name='sha256';Expression={$_.Hash.ToLowerInvariant()}}
notepad.exe results/sgb/upstream/sn3g001/manual-quality-audit.md
Get-FileHash -Algorithm SHA256 -LiteralPath results/sgb/upstream/sn3g001/manual-quality-audit.md | Select-Object Path,@{Name='sha256';Expression={$_.Hash.ToLowerInvariant()}}
notepad.exe evaluations/case003_san/clean/sn3g001/pre_downstream.json
```

- **预期结果**：实际窗口、support、draft、最终正文可逐项比对；人工保存真实审核结果。
- **成功标准**：4 条目标 rule_preservation 均完成真实审核，不能删记录回避缺陷。现有合法状态为 correct/incorrect/uncertain/unreviewed；确认遗漏使用 `incorrect + error_types=["rule_omission"]`，不新增 omitted 枚举。有正文的正确或错误结论填写真实 skill_ids、trace_refs、generated_evidence；uncertain 可无确定正文锚点，但要说明不确定原因。确认遗漏不强求不存在的正文锚点，必须在 manual-quality-audit.md 写明来源规则、检查过的全部最终包文件及哈希、检查范围和遗漏证据，并把这个报告相对路径及实际小写哈希填入审核 JSON 的 provenance.file/sha256。审核顶层填写真实 reviewer，每条记录填写非空证据说明 notes；generated_addition 的错误也照实保留。结构 VALID 不代表语义 correct。
- **失败处理**：语义错误、遗漏和不确定均是要测量的结果，审核完成且工程、安全、授权条件满足时可进入下游，不因非 correct 自动停止。真正 unreviewed、目标规则未覆盖、来源/引用/哈希不可信、遗漏没有检查范围证据时停止补齐审核；没有可用包或包不安全则停止，不能造 Skill。不得人工修补正文后仍称本次原始 CleanSkill，修复需单列干预版本。notepad 打开成功不等于审核完成。
- **下一步**：4C。

### 4C — 验证质量审核并冻结最终包

- **当前目标**：在下游启动前固定已审核 Skill 的身份。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/lab.py evaluation-validate --file evaluations/case003_san/clean/sn3g001/pre_downstream.json
if ($LASTEXITCODE -ne 0) { throw '4C review schema/entity validation failed' }
& $Task003Python -B scripts/sgb/sanctuary002.py quality --generator-run sn3g001
if ($LASTEXITCODE -ne 0) { throw 'STOP: required review is incomplete or its evidence is invalid' }
& $Task003Python -B scripts/sgb/pilot.py plan --task sanctuary_endgame_scheduler_002 --generator-run sn3g001 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '4C completed generation or fresh experiment check failed' }
& $Task003Python -B scripts/sgb/pilot.py freeze --task sanctuary_endgame_scheduler_002 --generator-run sn3g001 --output runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001
if ($LASTEXITCODE -ne 0) { throw '4C freeze failed; preserve evidence' }
Get-Content -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/skill_freeze.json -Raw
```

- **预期结果**：quality 输出 review_status=reviewed、原样 semantic_findings 和审核哈希，plan 给出固定模型／预算／两组，freeze 为 FROZEN；生成 skills/、skills_manifest.json、skill_freeze.json 和 canonical_files.json。
- **成功标准**：最终活动版本、源链、逐文件 SHA 和实际包副本通过校验。先 plan 后 freeze，因为 plan 拒绝已经存在的下游目录。
- **失败处理**：包不一致、空包、不安全或审核未完成就停止；语义缺陷不是冻结拒绝条件；不要重新注册或覆盖包。冻结成功后不要再改源 run、Skill 或审核文件。
- **下一步**：获得这**一对下游运行**明确授权后，执行 5A。

## 阶段 5：NoSkill 基线与配对批次启动

### 5A — 核对下游授权并完成真实包的零模型 prepare

- **当前目标**：在付费前验证同一包、两组条件、预算和 native 导出／评分全链路。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py authorization --authorization-phase downstream --generator-run sn3g001 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw 'STOP: paired downstream execution has not been authorized' }
& $Task003Python -B scripts/sgb/pilot.py prepare --task sanctuary_endgame_scheduler_002 --generator-run sn3g001 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '5A preparation failed; inspect engineering attempt and do not run' }
```

- **预期结果**：READY、model_calls=0；readiness.json PASS；两组受控 probe 导出正确／错误夹具并评分；创建一次 budget.sqlite3 和 execution_manifest.json。
- **成功标准**：下游批准绑定 `sn3e001`／`sn3g001`、同一 profile 哈希、一组一次、总 12 HTTP 上限；绑定的是完成且可追溯的审核，而非全部 correct 的审核，并包含 `approval_evidence.file/sha256` 与 4C 返回的 `quality_review_sha256`。**必须在 prepare 前完成批准和 gate 更新**，之后 gate 也属于冻结文件。
- **失败处理**：当前交付时此步仍会 BLOCKED。不得只设置环境变量绕过 gate。若已创建 ledger，不重做 prepare；现有代码明确禁止重置预算。失败看 engineering/attempt-*/failure.json、report.json、network 日志和原 score。
- **下一步**：5B。受控 probe 的读取不能算真实 Agent 读取。

### 5B — 检查公平性、NoSkill 空目录和零消耗账本

- **当前目标**：确保 NoSkill 未获得文档／Skill，条件差异只限预声明 Skill 处理。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
Get-Content -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/fairness.json -Raw
Get-Content -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/profile.json -Raw
& $Task003Python -B -c "import json,pathlib; p=pathlib.Path('runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001'); f=json.loads((p/'fairness.json').read_text()); assert f['status']=='PASS' and len(set(f['configuration_hashes'].values()))==1; n=json.loads((p/'configs/NoSkill1.json').read_text()); c=json.loads((p/'configs/CleanSkill1.json').read_text()); assert n['agent']['skills']==[]; assert n['extra_instruction_paths']==c['extra_instruction_paths']; assert not any((p/'staged/NoSkill').rglob('*')); print('Fairness, same instruction, empty NoSkill: PASS')"
if ($LASTEXITCODE -ne 0) { throw '5B fairness or NoSkill isolation failed' }
& $Task003Python -B scripts/sgb/pilot.py status --task sanctuary_endgame_scheduler_002 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '5B ledger status failed' }
```

- **预期结果**：两个 fairness hash 相同；NoSkill 没有 skills、索引或文件；状态 PREPARED，http_attempts=0，两组均 NEW。
- **成功标准**：模型、原任务、输入、Agent、工具、镜像、Oracle、相同附加说明、预算及无重试策略可比。不得向 NoSkill 手工追加源文或规则常量。
- **失败处理**：任一差异停止，查 profile/config/manifest 和 freeze；不能在冻结后手改配置继续。
- **下一步**：5C，唯一一次付费批次命令。

### 5C — 执行一对 NoSkill → CleanSkill

- **当前目标**：运行受同一 ledger 管理的正式配对；NoSkill 先执行。
- **执行位置**：研究根目录，须已通过 5A–5B。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py authorization --authorization-phase downstream --generator-run sn3g001 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw 'STOP: downstream authorization failed' }
if (Test-Path -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/batch.started) { throw 'STOP: this batch has already started; use status/analyze' }
& scripts/sgb/Invoke-Pilot.ps1 -Phase run -Task sanctuary_endgame_scheduler_002 -Experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw 'Pilot stopped; preserve ledger and continue with read-only inspection' }
```

- **预期结果**：NoSkill1 先运行、原生导出单个 `/workspace/agent_output.py`、独立 Oracle 评分；随后 CleanSkill1 运行。每组最多 6 HTTP，整个批次最多 12；不重试请求。
- **成功标准**：两个条件的真实 outcomes/、trials/、原始 model requests/http、token_usage 与 ledger 完整保存。整题成功要求原 8 项全通过且 infra_ok=true；评分完整且 infra_ok=true 的 0–7/8 是普通功能失败，不能称整题成功。
- **失败处理**：异常／预算停止可能使后组未启动，保留原状态；不要重启 run 或换 ID 追加重复。HTTP 未知、候选／scorer timeout、导出失败、Oracle 不完整均不得伪造为 0/8 普通失败。按阶段 6–7 汇总为未完成／unresolved。
- **下一步**：6A。**不要再次运行 5C 来“执行 CleanSkill”。**

## 阶段 6：CleanSkill 执行证据和 Oracle 检查

### 6A — 读取批次进度与两组正式评分

- **当前目标**：确认公共批次已执行到 CleanSkill；检查原断言和异常。
- **执行位置**：研究根目录；另开终端时先完成 0A。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/pilot.py status --task sanctuary_endgame_scheduler_002 --experiment sn3e001 --watch
if ($LASTEXITCODE -ne 0) { throw '6A status failed' }
@('NoSkill1','CleanSkill1') | ForEach-Object {
  $Task003Outcome = "runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/outcomes/$_/result.json"
  if (Test-Path -LiteralPath $Task003Outcome) { Get-Content -LiteralPath $Task003Outcome -Raw }
  else { Write-Output "MISSING outcome: $_; keep as incomplete" }
}
Get-ChildItem -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/outcomes -Filter junit.xml -Recurse | ForEach-Object { $_.FullName; Get-Content -LiteralPath $_.FullName -Raw }
```

- **预期结果**：正常为 COMPLETED；两组 `oracle.task_result.tests=8`、errors=skipped=0，候选绑定已验证；保留失败项原名 `test_cl_case[1-case0]` 至 `[8-case7]`。
- **成功标准**：每个提交和 Oracle 身份可追溯，NoSkill 与 CleanSkill 各 0/1 的整题结果单独记录；不能把用例通过比例当重复试验成功率。
- **失败处理**：STOPPED／缺组／infra_ok=false 时转入阶段 7 做未完成报告，不追加调用；运行仍在进行时勿分析为最终结果。watch 在 PREPARED 时也会返回，不能误当完成。
- **下一步**：6B。

### 6B — 核对正文读取、请求和实现先后顺序

- **当前目标**：检验正文读取要求是否真正执行，建立规则到行为的候选证据链。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
$Task003Observer = 'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/trials/audit-cleanskill1/p1-observer'
Get-Content -LiteralPath "$Task003Observer/p1-summary.json" -Raw
Get-Content -LiteralPath "$Task003Observer/p1-skill-reads.jsonl"
Get-Content -LiteralPath "$Task003Observer/p1-tool-actions.jsonl"
Get-Content -LiteralPath "$Task003Observer/p1-model-http.jsonl"
Get-Content -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/outcomes/CleanSkill1/oracle/score/agent_output.py -Encoding UTF8
```

- **预期结果**：mode=paid；model_read_ids 与受控 probe IDs 分开；工具动作、成功 HTTP 请求和真实提交可核对。
- **成功标准**：后续 7A 的 usage 报告确认相关完整正文进入成功请求；人工从 `p1-model-requests.jsonl`、tool-actions 的步骤确认规则在相关实现动作之前。仅索引、访问文件或模型声称“我已读过”均不足；`behavioral_use` 仍为 UNKNOWN，除非另有规则／动作证据。
- **失败处理**：日志或文件缺失时保留 unknown。只读到索引、读正文失败、截断或读入发生在实现后，分别记录，不能自动归因为错误理解。不要额外要求模型补读；需要新机制干预与新授权。
- **下一步**：7A。

## 阶段 7：汇总、逐断言差分和失败归因

### 7A — 生成配对分析与上游规则汇总

- **当前目标**：复用现有汇总器，保留原日志和评分。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
if (Test-Path -LiteralPath results/sgb/analyses/sn3e001) { throw 'Analysis exists; inspect it instead of overwriting' }
$Task003AnalysisInputs = @(
  'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/profile.json',
  'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/configs/NoSkill1.json',
  'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/configs/CleanSkill1.json'
)
if (@($Task003AnalysisInputs | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0) {
  & $Task003Python -B scripts/sgb/pilot.py analyze --task sanctuary_endgame_scheduler_002 --experiment sn3e001 --output results/sgb/analyses/sn3e001
  if ($LASTEXITCODE -ne 0) { throw '7A downstream analysis failed' }
} else { Write-Output 'Analysis inputs missing; use the partial report command in 7D without starting anything' }
if (Test-Path -LiteralPath results/sgb/upstream/sn3g001/aggregate) { throw 'Aggregate exists; inspect it instead of overwriting' }
& $Task003Python -B scripts/lab.py aggregate --case case003_san --out results/sgb/upstream/sn3g001/aggregate
if ($LASTEXITCODE -ne 0) { throw '7A upstream aggregation failed' }
Get-Content -LiteralPath results/sgb/analyses/sn3e001/CleanSkill1-skill-usage.json -Raw
Get-Content -LiteralPath results/sgb/analyses/sn3e001/NoSkill1-skill-usage.json -Raw
```

- **预期结果**：analysis.json、report.md、skills.md、两组 skill-usage.json；上游 runs.json、rule_results.json/csv。
- **成功标准**：读取证据分层，受控 probe 不被算为真实 Agent；tokens／HTTP 从原 outcomes 和 observer 读取。当前 provider 真实价格未验证，货币成本必须保留 null／unknown，不能套官方参考价当实际账单。
- **失败处理**：已有目录保留；不完整运行按缺失证据处理。若还未 prepare 或缺少分析输入，可直接用 7D 的 report 生成 not_started/partial 报告；不要为输出报告启动实验。上游 aggregate 依赖真实生成，未产生该运行时不执行它。
- **下一步**：7B。

### 7B — 自动审查配对资格和逐项 Oracle 差分

- **当前目标**：先判定比较是否成立，再判定结果差分。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/attribution.py --spec configs/attribution/sn3e001.json
if ($LASTEXITCODE -ne 0) { throw '7B attribution identity/evidence validation failed' }
```

- **预期结果**：输出 comparability、control_checks、task_difference、8 项 assertion_differences、暴露与生成身份；未完成时显示 unknown／unresolved。
- **成功标准**：仅 eligible 才解释 NoSkill→CleanSkill：FAIL→PASS possible_help；PASS→FAIL possible_harm；PASS→PASS both_passed；FAIL→FAIL both_failed；异常／缺组 unresolved。两组均失败时仍可以检查某一原用例改善或退步，但不能称整题新增失败。
- **失败处理**：不同配置、协议、模型、Oracle 或环境身份使比较 ineligible；身份未知保持 unknown，不用历史 NoSkill 补组。不要把“有 Skill 仍失败”直接写成 Skill 导致失败。
- **下一步**：7C，补充语义审核后再输出正式归因报告。

### 7C — 人工连接规则、动作和失败，导出归因报告

- **当前目标**：补充自动分析不能代替的源规则传递和行为机制审核。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
Get-Content -LiteralPath docs/sgb/attribution.md -Encoding UTF8
Get-ChildItem -LiteralPath results/sgb/upstream/sn3g001/exports -Filter '*.json' -File | Get-FileHash -Algorithm SHA256 | Select-Object Path,@{Name='sha256';Expression={$_.Hash.ToLowerInvariant()}}
Get-ChildItem -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/skills -Filter SKILL.md -Recurse | ForEach-Object {
  $_.FullName
  (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
  $Task003SkillLine = 0
  Get-Content -LiteralPath $_.FullName -Encoding UTF8 | ForEach-Object { $Task003SkillLine++; '{0}: {1}' -f $Task003SkillLine,$_ }
}
$Task003ActionLine = 0
Get-Content -LiteralPath runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/trials/audit-cleanskill1/p1-observer/p1-tool-actions.jsonl | ForEach-Object { $Task003ActionLine++; '{0}: {1}' -f $Task003ActionLine,$_ }
notepad.exe configs/attribution/sn3e001.json
```

- **预期结果**：审核者根据真实产物编辑 spec。初始 spec 的空审核集合明确表示尚未发生真实生成／行为审核；不是默认无规则损失，也没有虚构生成实体或行号。
- **成功标准**：按 `cases/sgb/case003_san/rules.json` 的 4 个稳定 ID，增加 rules、evidence、必要 claims。每条 rule 记录 parent_rule_id（对应现有规则 ID）、generator_run_id=`sn3g001`、真实 reviewer、review_status=`reviewed`，以及 source/window/support/draft/spec/registered/skill 各阶段 preserved/altered/omitted/ambiguous/unknown。证据引用使用实际仓库相对路径、小写 SHA-256、实体 ID、定位器，依据 4A 导出文件填写 JSON pointer／行号。下游 links 写 target/reference、原 pytest 名、skill_id／正文行、真实工具动作事件，说明正文是否在动作前进入成功请求。`action_event` 是 tool-actions JSONL 的 **1 基行号**，该行必须是 stage=submitted、actor=model_tool；不是模型文本中自述的步骤号。正文行必须在 YAML frontmatter 之后。没有证据就写 unknown 和缺失原因，不造 ID。
- **失败处理**：人工无法确定时允许 `insufficient_evidence`，不能自动补成理解错误。候选原因使用现有八类：source_missing_or_ambiguous、window_selection_loss、evidence_or_draft_loss、compile_or_register_change、skill_delivery_failure、agent_rule_misapplication、environment_tool_or_oracle、insufficient_evidence。下游功能分类采用 APM、EM.BDR、EM.ESM、TIF.OWG、TIF.IRF、TIF.RRO、AM；允许不确定。事实 observed、推断 inferred、待干预 hypothesis 分开；本轮未实施干预，不得填 intervention_supported。
- **下一步**：保存并关闭编辑器后执行 7D。完整字段与校验规则见现有 `docs/sgb/attribution.md`，本手册不提供不存在的自动语义分类命令。

### 7D — 保存正式归因与最终基线报告

- **当前目标**：输出可复核报告及证据清单。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
if (Test-Path -LiteralPath configs/attribution/sn3e001.json) {
  if (-not (Test-Path -LiteralPath results/sgb/attributions/sn3e001-v1)) {
    & $Task003Python -B scripts/sgb/attribution.py --spec configs/attribution/sn3e001.json --output results/sgb/attributions/sn3e001-v1
    if ($LASTEXITCODE -ne 0) { throw '7D attribution export failed; preserve the existing report if present' }
  } else { Write-Output 'Preserving existing attribution export; report will verify its spec digest' }
} else { Write-Output 'Attribution review spec missing; report will record missing evidence' }
& $Task003Python -B scripts/sgb/sanctuary002.py report --generator-run sn3g001 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '7D baseline identity/frozen ledger validation failed' }
Get-Content -LiteralPath results/sgb/baselines/sn3e001/baseline.md -Encoding UTF8
```

- **预期结果**：归因 report.json/md；最终 baseline.json/md 和 evidence-manifest.json。源文哈希、模型／预算绑定、整题及逐项结果、正文读取、tokens 和成本未知状态可追溯。
- **成功标准**：执行、使用、任务结果及归因四字段分别记录。两组实际执行和原 Oracle 评分均完整即 execution=completed；未读正文、任务失败、规则链不完整不改变该事实。仅阶段名称齐全、证据全 unknown 只能 attribution=insufficient_evidence。未审核则 pending_review，不具备可比性则 not_comparable。reviewed 表示证据审核完成，不证明因果。review、analysis 或归因文件缺失时尽可能生成带 missing_evidence 的报告；若 spec 和已导出的 v1 报告同时存在，二者摘要仍须匹配。哈希冲突、跨运行引用等完整性错误继续拒绝。
- **失败处理**：已存在的报告不覆盖。若要修订语义审核，保留 v1，另审新的分析版本；不要修改历史 trial。环境异常和缺组保存 partial/not_started 及 null 评分；不得为了完成报告补造数据。不要为了让报告“完成”新增模型请求。
- **下一步**：8A。

## 阶段 8：最终验收

阶段 8 的完整执行验收适用于已经有冻结包和运行记录的情况。not_started/partial 报告本身是可交付的真实状态，但不能冒充执行完成；缺包时保留失败/阻断报告，不强行执行冻结包存在性断言。

### 8A — 重查身份、冻结包、账本和历史保护

- **当前目标**：核实所有关键证据仍是原字节，账本没有重置。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B scripts/sgb/sanctuary002.py audit
if ($LASTEXITCODE -ne 0) { throw '8A identity changed' }
& $Task003Python -B scripts/sgb/pilot.py status --task sanctuary_endgame_scheduler_002 --experiment sn3e001
if ($LASTEXITCODE -ne 0) { throw '8A ledger status failed' }
& $Task003Python -B scripts/sgb/sanctuary002.py history-check --audit-id task003-preflight-sn3g001
if ($LASTEXITCODE -ne 0) { throw '8A historical artifact preservation failed' }
& $Task003Python -B -c "import json,hashlib,pathlib; r=pathlib.Path('.'); p=r/'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001'; h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); f=json.loads((p/'skill_freeze.json').read_text()); actual={x.relative_to(p/'skills').as_posix():h(x) for x in (p/'skills').rglob('*') if x.is_file()}; assert actual==f['files']; assert h(p/'skills_manifest.json')==f['manifest_sha256']; m=json.loads((r/'results/sgb/baselines/sn3e001/evidence-manifest.json').read_text()); assert all(h(r/n)==v for n,v in m.items()); print('Frozen Skill and report evidence: PASS')"
if ($LASTEXITCODE -ne 0) { throw '8A frozen/report evidence changed' }
git -C 'D:\AS\AutoSkill-main' status --short
```

- **预期结果**：身份、包和证据哈希 PASS；ledger 两组 DONE、总 HTTP 不超过 12；历史文件全保持，`results/run_index.jsonl` 仅允许原前缀不变的追加。
- **成功标准**：历史源／结果／ledger 没有覆盖，所有引用均可读取；report 命令已核对冻结清单和 ledger policy，不能用仅存在文件代替该检查。
- **失败处理**：任何漂移保留现场，停止宣告结果；明确指出文件、异常和影响范围，不重跑掩盖。
- **下一步**：8B。

### 8B — 检查完成口径

- **当前目标**：区分实验链完成与 Agent 功能成功。
- **执行位置**：研究根目录。
- **完整命令**：

```powershell
& $Task003Python -B -c "import json,pathlib; b=json.loads(pathlib.Path('results/sgb/baselines/sn3e001/baseline.json').read_text()); print('execution=',b['experiment_execution_status']); print('usage=',b['skill_usage_status']); print('task_success=',b['task_success']); print('attribution=',b['attribution_status']); print('comparability=',b['comparability']); print('difference=',b['task_difference']); assert b['experiment_execution_status']=='completed'; assert b['ledger']['http_attempts']<=12; assert all(v is not None for v in b['task_success'].values()); print('Execution/scoring complete; inspect comparability and attribution separately')"
if ($LASTEXITCODE -ne 0) { throw 'Task003 execution/scoring is not complete; preserve partial results' }
```

- **预期结果**：execution=completed，两组原始 8 项评分完整且预算一致；使用、功能成败、归因和比较资格分别展示，不预设为正面结果。
- **成功标准**：源文、真实生成、工程有效且质量已记录的冻结包、两组真实执行、绑定提交和原 Oracle 有效评分均完成，可说“执行与评分全流程已跑通”。eligible 才能作正式配对差分；若控制变量不一致，执行仍可 completed，但不得宣称对照成立。CleanSkill 8/8 且评分有效才是任务成功；规则归因可保留未决，不要求为了完成实验把未知改成已证实。
- **失败处理**：未读正文是使用/协议观察，归因不足或待审核不会抹去已完成执行；缺实际组、未结束或缺有效评分才是 partial/not_started。无有效对照标 not_comparable，差分 unresolved。不得当作 Skill 伤害或任务通过。下一次尝试、规则修复、增加重复、换模型或预算扩展都需要单独批准。
- **下一步**：停止执行，审核报告。不自动进入 Degraded 条件或启动新试验。

## 当前预算与尚未执行的步骤

| 阶段 | 当前授权／完成状态 | 所需下一项 |
|---|---|---|
| 选题、静态审核、确定性测试、隔离 Oracle 夹具 | 本轮授权且已执行；详见 admission 和 validation 记录 | 研究者审核本手册 |
| `sn3g001` 正式 Anything2Skill | **NOT_AUTHORIZED**；未调用 | 明确批准一次生成的额度及配置，保留批准来源哈希 |
| 上游语义审核与真实包冻结 | 等待真实生成；不能提前宣称通过 | 人工完成全部目标规则审核，保留 correct/incorrect/uncertain/omission；工程包必须有效 |
| 真实包 native prepare | 等待生成与下游批准；当前只做了资产／评分器验收 | 按 5A 验收真实包、冻结 gate、创建一次 ledger |
| `sn3e001` 两组真实执行 | **NOT_AUTHORIZED**；未启动 | 明确批准一对、每组一次、6+6 HTTP 及完整 profile 预算；绑定质量审核哈希 |
| 稳定收益、因果干预、额外重复、退化 | 未授权、未执行 | 另立方案；不属于本手册执行范围 |

上游 450000 是响应后的观测阈值，不能保证最后一次响应后严格不超 token；下游输入为预算预留估计并保留实际 usage。请求错误或超时仍可能计费；使用量未知须保留，不能按零成本处理。准确货币成本需要提供商账单或已核验单价；当前结果以实际请求数及 token 为准。

批准交接时，生成批准记录建议保存为 `results/sgb/authorizations/task003-generation-sn3g001.md`，下游批准记录保存为 `results/sgb/authorizations/task003-downstream-sn3e001.md`，内容必须来自研究者真实批准，不能把预算提案复制为批准。授权维护者用记录的实际 SHA-256 填入 gate 对应 `approval_evidence`，把获批的 `authorization_status` 设为 AUTHORIZED；生成获批后顶层 status 才能 PASS，下游另外获批后 downstream.status 才能 PASS。下游还要填入 4C 的真实 quality_review_sha256。金额、次数或配置若与本手册提案不同，先调整方案并重新审核，不能修改批准数字使检查通过。没有批准记录时，3A／5A 的 STOP 就是最终停止点。

本手册已同步 Task003 状态解耦修复。旧验收属于历史版本，不被覆盖；本次修复与回归记录见 `results/sgb/audits/task003-semantics-fix-20261026-001/validation.json`。report 仍拒绝覆盖既有目录，需定稿后执行一次；状态轮询使用 status，不为更新报告重跑实验。
