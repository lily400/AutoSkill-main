# degradation_failure_lab — P0.2 统一实验入口

本目录研究文档退化如何影响官方 Anything2Skill 的提取、编译与技能质量。P0.2 只整理工程结构：不修改官方源码、算法或提示词，不调用付费模型，不创建退化文档，也不新增正式 case。

当前唯一正式案例是 `case001_qsv_select`。完整流程和文件职责见 [项目结构指南](docs/PROJECT_STRUCTURE_GUIDE.md)，P0.2 的实际迁移与验证证据见 [reports/P0_2](reports/P0_2/validation_report.md)。

## 唯一现行路径

| 职责 | 现行位置 |
|---|---|
| 原始文档 | `data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md` |
| 来源清单 | `data/manifests/qsv_select.json` |
| 数据集目录 | `data/catalog.json` |
| 案例定义 | `cases/case001_qsv_select/` |
| 环境配置 | `configs/environment.json` |
| 生成配置 | `configs/generation/deepseek_flash.json` |
| 公共实现 | `src/degradation_lab/` |
| 正式入口 | `scripts/lab.py` |
| 新运行 | `runs/<case_id>/<condition_id>/<run_id>/` |
| 人工评价 | `evaluations/<case_id>/<condition_id>/<run_id>/` |
| 派生结果 | `results/` |

现行调用链只有一条：

```text
scripts/lab.py
  → degradation_lab.cli
  → degradation_lab.catalog（来源、案例与条件校验）
  → degradation_lab.runner（计划、快照与运行隔离）
  → degradation_lab.adapter（透明调用）
  → 官方 Anything2Skill
```

`src/degradation_lab/provider_adapter.py` 是唯一现行 provider adapter。它只向官方 OpenAI 兼容请求增加配置指定的 `thinking` 参数，不复制生成流程。

## 命令

```powershell
Set-Location 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab'
$py = 'D:\anoconda1\envs\autoskill\python.exe'

& $py -B scripts\lab.py list
& $py -B scripts\lab.py validate
& $py -B scripts\lab.py plan --case case001_qsv_select --condition clean --repeat 1
& $py -B scripts\lab.py verify --run p0_qsv_select_clean_002
& $py -B scripts\lab.py evaluation-init --run <run_id> --evaluation-id review001
& $py -B scripts\lab.py evaluation-validate --file evaluations\<case>\<condition>\<run>\review001.json
& $py -B scripts\lab.py aggregate --out results\aggregates\current
& $py -B -m unittest discover -s tests -v
```

以下命令会调用真实模型并产生费用，本轮未执行：

```powershell
& $py -B scripts\lab.py run --case case001_qsv_select --condition clean --repeat 1
```

`scripts/run_clean.py` 和 `scripts/verify_run.py` 只为旧命令保留薄转发，并会输出弃用提示；它们不包含第二套运行或验证逻辑。新工作一律使用 `scripts/lab.py`。

## 来源与条件约束

- 非测试来源必须位于 `data/raw_sources/`；`SourceManager` 会拒绝把 Legacy 路径注册为现行来源。
- Clean 输入必须直接引用来源清单中的同一文件，并匹配同一 SHA-256。
- Degraded 输入必须位于 `data/condition_inputs/`，必须与父来源字节不同，并记录 operator 与参数。
- `.gitattributes` 对 `raw_sources`、`condition_inputs` 和新运行快照使用 `-text`，避免 Git 在 Windows 检出时改写换行。
- `case001_qsv_select` 的正式 `select.md` SHA-256 是 `74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。

## 历史隔离

- `runs/p0_qsv_select_clean_001`：P0 真实失败运行，保持失败状态和全部证据。
- `runs/p0_qsv_select_clean_002`：P0 真实成功运行，保持正式 SKILL.md、注册记录和中间产物。
- `data/sources/`：P0 运行清单仍引用的 CRLF 历史检出副本，禁止用于新案例。
- `data/legacy_bytes/`：P0/P0.1 验证旧清单哈希所需的 Git 原字节副本，禁止用于新案例。
- `legacy/P0/`：P0 配置、来源调查清单和一次性脚本。
- `legacy/P0_1/`：P0.1 一次性实施工具。
- `reports/P0/`、`reports/P0_1/`、`reports/P0_2/`：三个阶段的报告分开保存。

历史文件保留不代表仍是现行输入；`data/catalog.json` 是现行来源注册的唯一入口，`runs/legacy_index.json` 是旧运行定位的唯一兼容索引。

## 当前验证边界

P0.2 验证覆盖现行配置、来源哈希、临时 case002 注册、P0 成功/失败运行的只读复验、官方源码哈希不变及离线单元测试。没有执行新的真实模型端到端运行，不能把这些工程验证表述成新的模型实验结果。
