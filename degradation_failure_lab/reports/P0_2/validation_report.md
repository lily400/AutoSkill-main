# P0.2 验证报告

验证日期：2026-10-11。所有命令均在 `D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab` 执行，Python 为 `D:\anoconda1\envs\autoskill\python.exe`。本轮未执行 `lab.py run`，没有付费模型调用。

## 命令结果

| 检查 | 命令 | 结果 |
|---|---|---|
| 案例列表 | `python -B scripts/lab.py list` | exit 0；仅 `case001_qsv_select`，仅 source `qsv-select-257ae7b38738` |
| 全配置验证 | `python -B scripts/lab.py validate` | exit 0；`status=VALID` |
| 离线计划 | `python -B scripts/lab.py plan --case case001_qsv_select --condition clean --repeat 1` | exit 0；1 个输入，输出模式为分层 run 目录 |
| P0 成功运行复验 | `python -B scripts/lab.py verify --run p0_qsv_select_clean_002` | exit 0；`PASS`；2 个注册技能，全部工程检查为 true |
| P0 失败运行复验 | `python -B scripts/lab.py verify --run p0_qsv_select_clean_001` | exit 1（预期）；`PARTIAL`；官方状态 `failed`，0 个注册技能，保留 `empty LLM output` 错误 |
| 评价验证 | `python -B scripts/lab.py evaluation-validate --file evaluations/.../p0_initial_review.json` | exit 0；`VALID` |
| 聚合 | `python -B scripts/lab.py aggregate --out results/aggregates/P0_2_validation` | exit 0；2 个历史运行、15 条规则审核记录 |
| 正式命令存在性 | `lab.py run --help`、`lab.py evaluation-init --help` | 均 exit 0；未创建运行或评价 |
| 旧薄入口 | `run_clean.py --help`、`verify_run.py --help` | 均 exit 0，并转发到现行 CLI |
| 离线测试 | `python -B -m unittest discover -s tests -v` | 18/18 通过 |
| 补丁检查 | `git diff --check` | 无 whitespace error；仅显示本机 `core.autocrlf=true` 对普通文本的提示 |

## 验收项

1. **现行来源、Clean 输入与 SHA-256 一致：通过。** `data/manifests/qsv_select.json` 与 `clean.json` 指向同一 `data/raw_sources/.../select.md`；记录值与实际值均为 `74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。
2. **当前正式来源只有一个权威清单和路径：通过。** `data/manifests/` 只有 `qsv_select.json`；catalog 只注册该清单。
3. **现行代码使用统一入口：通过。** 正式入口为 `scripts/lab.py`；两个旧脚本只做 deprecated 参数转发，公共逻辑均在 `src/degradation_lab/`。
4. **P0 成功运行完整验证：通过。** `002` 为 `PASS`，1 document、2 windows、4 supports、4 drafts、4 specs、2 registered skills。
5. **P0 失败运行保持真实失败：通过。** `001` 仍为 `PARTIAL/failed`，包含原错误，未被改写为成功。
6. **P0 中间证据、SKILL.md 与注册记录不变：通过。** 单元测试按 P0.1 `project_before.json` 和 artifact manifests 校验原字节；只读复验所有 `saved_artifact_hashes=true`。
7. **P0.1 多案例测试：通过。** 18 项全部通过。
8. **临时 case002 可配置注册：通过。** 测试在临时目录注册 case002、四个条件和九个隔离运行，不写正式 catalog。
9. **新增案例无需改公共 Python：通过。** fixture case001/case002 共用同一 SourceManager、CaseManager、Runner 和 Adapter；指南给出纯配置新增步骤。
10. **无现行无效路径或隐式旧版本引用：通过。** 对 catalog、现行 manifests、cases、configs、catalog/runner/adapter/cli 的扫描结果为 `NONE`；历史读取仅在 `artifacts.py`、`evaluation.py` 中显式兼容。
11. **官方 Anything2Skill 源码不变：通过。** 164 个官方代码/测试/配置文件的 inventory 与 P0.1 保存值完全相同；当前 inventory 摘要 SHA-256 为 `57dcb8eedea0157eb90ff98d48a96fa7e613a3b91d6313aac6cbac5685343352`。
12. **Git 检出后的原始字节稳定：通过。** raw source 的 Git 属性为 `text: unset`（`-text`）；`git hash-object` 的 filtered/raw blob 均为 `1fb480611b98b1b741a948043fee12358ee7701c`。

## 三种状态必须分开

- **工程配置通过：是。** `validate`、`plan` 和 18 项离线测试通过。
- **历史运行验证通过：是。** 成功运行保持 PASS，失败运行保持真实失败状态。
- **新框架真实模型端到端运行通过：未验证。** 本轮按任务要求没有调用付费模型，不能宣称这一项已通过。

## 首轮测试发现与修复

第一次运行 18 项测试时有 2 项因历史评价仍引用迁移前的 `reports/quality_review.md` 而报 `FileNotFoundError`。没有修改历史评价 JSON，也没有复制报告；`evaluation.py` 只对该已知旧路径映射到 `reports/P0/quality_review.md`。第二次完整测试 18/18 通过。
