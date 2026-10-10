# case002：三种条件 × 三次运行的实际接口示例

这是未来操作说明，本轮未创建正式 case002 或退化文档。
为具体说明来源共用能力，以 `case002_qsv_select_options` 为例：仍引用已存在的真实 qsv 文档，
评价重点只用原 R7（Common Options），不是虚构新来源。若改为其他真实文档，
先按 schemas/source.schema.json 保存其固定原文和清单，再将清单加入 data/catalog.json。
不用改动公共 Python 文件。以下命令均在实验根目录执行，`$py` 为现有 Python 路径。

## 新增案例定义（未来执行）

文件 `cases/case002_qsv_select_options/case.json`：

```json
{
  "schema_version": 1,
  "case_id": "case002_qsv_select_options",
  "dataset_id": "qsv",
  "title": "qsv select Common Options 的保留情况",
  "source_ids": ["qsv-select-257ae7b38738"],
  "generation_config": "configs/generation/deepseek_flash.json",
  "pipeline_overrides": {"domain":"qsv", "domain_type":"qsv", "family_name":"qsv-select-options"}
}
```

文件 `rules.json` 逐字保留既有 R7 内容，并引用同一原始规则文件：

```json
{
  "schema_version": 1,
  "case_id": "case002_qsv_select_options",
  "classification": "CUSTOM_TEST_DATA",
  "provenance": {},
  "rules": [{
    "rule_id": "R7",
    "text": "--no-headers treats first row as data; --delimiter is one character; --output writes a file rather than stdout.",
    "source_evidence": [{"source_id":"qsv-select-257ae7b38738", "lines":[173,174,175]}],
    "rule_type": "command_behavior",
    "annotation_status": "analyst_checklist"
  }]
}
```

若这份新 rules 是原检查表的直接派生，可在 provenance 填入原检查表路径与真实 SHA-256。
现有 case001 原检查表及判断均不变；在不同案例中 R7 通过 case_id 区分。

文件 `conditions.json`：下面 operator 名称只是未来已物化输入的算子记录，框架不执行它们。

```json
{
  "schema_version": 1,
  "case_id": "case002_qsv_select_options",
  "conditions": [
    {"condition_id":"ocr_low", "kind":"degraded", "operator":"ocr_noise", "parameters":{"strength":0.1}, "input_manifest":"cases/case002_qsv_select_options/inputs/ocr_low.json"},
    {"condition_id":"layout_medium", "kind":"degraded", "operator":"layout_loss", "parameters":{"strength":0.2}, "input_manifest":"cases/case002_qsv_select_options/inputs/layout_medium.json"},
    {"condition_id":"char_high", "kind":"degraded", "operator":"character_loss", "parameters":{"strength":0.3}, "input_manifest":"cases/case002_qsv_select_options/inputs/char_high.json"}
  ]
}
```

## 三份输入及三份清单

由下一阶段的方法生成并审核真实退化输入，保存为：

```text
data/condition_inputs/case002_qsv_select_options/ocr_low/select.md
data/condition_inputs/case002_qsv_select_options/layout_medium/select.md
data/condition_inputs/case002_qsv_select_options/char_high/select.md
```

现在不能复制 clean 原文冒充退化，验证器也会拒绝相同字节。
输入准备完成后，用以下 PowerShell 生成三份真实哈希清单（没有退化算法）：

```powershell
$py = 'D:\anoconda1\envs\autoskill\python.exe'
$case = 'case002_qsv_select_options'
$source = Get-Content 'data\manifests\qsv_select_canonical.json' -Raw | ConvertFrom-Json
$conditions = @('ocr_low','layout_medium','char_high')
New-Item -ItemType Directory -Force -Path "cases\$case\inputs" | Out-Null
foreach ($condition in $conditions) {
    $path = "data/condition_inputs/$case/$condition/select.md"
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $manifest = @{
        schema_version = 1; case_id = $case; condition_id = $condition
        inputs = @(@{
            input_id = 'input001'; source_id = $source.source_id
            source_sha256 = $source.sha256; path = $path; sha256 = $hash
        })
    }
    $json = $manifest | ConvertTo-Json -Depth 10
    [IO.File]::WriteAllText((Join-Path (Get-Location) "cases\$case\inputs\$condition.json"), $json, [Text.UTF8Encoding]::new($false))
}
```

共新增：三份案例 JSON、三份输入 JSON、三份真实退化文档；复用现有 Source 与公共配置。
正式注册由 cases/*/case.json 自动发现，不需要修改注册 Python。
若需 Clean 对照，还须在 conditions.json 增加 clean（operator=null、parameters={}）和对应清单，
直接引用 source.local_path/source.sha256；此时另加三次 Clean 是 12 次运行，不能算入上述九次。

## 预检、执行、产物与汇总

```powershell
& $py -B scripts\lab.py validate
& $py -B scripts\lab.py plan --case case002_qsv_select_options --condition ocr_low layout_medium char_high --repeat 3

# 以下会执行九次真实模型调用流程；本轮未执行。先设置公共配置指定的密钥环境变量。
& $py -B scripts\lab.py run --case case002_qsv_select_options --condition ocr_low layout_medium char_high --repeat 3
```

每种条件下自动产生三个不同 run_id，互不读取 SkillBank：

```text
runs/case002_qsv_select_options/ocr_low/<run_id_1..3>/
runs/case002_qsv_select_options/layout_medium/<run_id_4..6>/
runs/case002_qsv_select_options/char_high/<run_id_7..9>/
```

每个目录有 inputs/、input_manifest.json、sources.json、config.json、wrapper_snapshot/、
upstream_before/after.json、status.json、execution.json、http/、官方 SkillBank 与中间产物。
正式技能路径取官方注册结果，不假定每次只生成一个技能。

从轻量 ledger 取得该案例的运行 ID，批量验证、初始化未审核记录：

```powershell
$entries = Get-Content 'results\run_index.jsonl' | ForEach-Object { $_ | ConvertFrom-Json } |
    Where-Object { $_.case_id -eq 'case002_qsv_select_options' }
foreach ($entry in $entries) {
    & $py -B scripts\lab.py verify --run $entry.run_id --out "results/exports/$($entry.run_id)"
    & $py -B scripts\lab.py evaluation-init --run $entry.run_id --evaluation-id review001
}
```

审核文件位于 `evaluations/case002_qsv_select_options/<condition>/<run_id>/review001.json`。
逐条填写原 R7 是否保留、生成 skill_ids、trace_refs 和 SKILL.md 行号；没有判断的记录保持 unreviewed。
可把同一条规则映射到多个技能，或在遗漏时保留空 skill_ids，不伪造关联。

```powershell
& $py -B scripts\lab.py evaluation-validate --file evaluations/<case>/<condition>/<run>/review001.json
& $py -B scripts\lab.py aggregate --case case002_qsv_select_options --out results/aggregates/case002
```

输出 runs.json、rule_results.json、rule_results.csv。每行含 case、condition、run、rule、
审核范围、判断、skill_ids 和错误类型；未审核记录不会因为有 SKILL.md 而变成正确。
以上入口已用临时 fixture 测试，九次是真实执行时的计划；没有冒称本轮已执行九次模型。
