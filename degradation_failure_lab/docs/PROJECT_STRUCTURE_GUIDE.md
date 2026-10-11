# 从 select.md 到 SKILL.md：唯一正式流程

现行案例为 `case001_qsv_select`。下面标明源码职责；不是声称 P0.3 已运行新一轮付费模型。

| 顺序 | 文件 / 模块 | 类型 | 职责 |
|---|---|---|---|
| 1 | `data/raw_sources/qsv/<commit>/select.md` | 官方来源快照 | 固定的 qsv select Markdown 原文 |
| 2 | `data/manifests/qsv_select.json` | 本项目元数据 | 来源、Git commit、哈希、路径 |
| 3 | `data/catalog.json` | 本项目元数据 | 注册 dataset/source |
| 4 | `cases/case001_qsv_select/case.json` | 本项目配置 | 案例、来源 ID、模型配置引用 |
| 5 | `cases/case001_qsv_select/conditions.json` | 本项目配置 | 当前只有 clean |
| 6 | `cases/case001_qsv_select/inputs/clean.json` | 本项目配置 | Clean 输入引用原文，不复制文档 |
| 7 | `cases/case001_qsv_select/rules.json` | 本项目评价定义 | R1–R7 原文规则，**不传入生成模型** |
| 8 | `scripts/lab.py` → `src/degradation_lab/cli.py` | 本项目入口 | list / validate / plan / run / verify / evaluation / aggregate |
| 9 | `catalog.py`、`schema.py` | 本项目实现 | 校验来源、案例、条件、原始哈希 |
| 10 | `runner.py` | 本项目实现 | 准备 `runs/<case>/<condition>/<run_id>`、输入快照、隔离 SkillBank |
| 11 | `adapter.py`、`provider_adapter.py` | 本项目实现 | 接入官方公共 API，记录调用、状态、阶段证据 |
| 12 | `AutoSkill4Doc` 的 Ingest | **官方** | TextUnit、DocumentRecord、StrictWindow |
| 13 | `AutoSkill4Doc` 的 Extract | **官方** | SupportRecord、SkillDraft |
| 14 | `AutoSkill4Doc` 的 Compile | **官方** | SkillSpec |
| 15 | `AutoSkill4Doc` 的 Register | **官方** | create/discard/版本决定、正式 SKILL.md |
| 16 | `runs/.../SkillBank/` | 官方运行产物 | 中间 JSON、注册表、正式技能、可见树 |
| 17 | `artifacts.py` | 本项目分析 | 只读检查与来源 → 窗口 → Support → Draft → Spec → SKILL.md 导出 |
| 18 | `evaluation.py` | 本项目分析 | 规则级审核记录与跨运行汇总 |

单次新运行的所有完整输入、配置、模型调用和官方产物都在它自己的 run 目录里。旧 P0 扁平 run 不再作为现行入口的一部分。

## 新增 case002

若复用已登记的来源，不要复制文档，只需新建 `cases/case002_<name>/` 内的 `case.json`、`rules.json`、`conditions.json`、`inputs/clean.json`，然后使用相同的 `lab.py validate` 和 `lab.py plan`。如有新文档，增加 `data/raw_sources/` 原文和 `data/manifests/` 来源清单并注册到 `data/catalog.json`。

当前没有正式 case002、没有已物化的 Degraded 文档，也没有下游 Agent 评测。旧 P0 真实技能和研究证据从 [完整历史归档分支](https://github.com/lily400/AutoSkill-main/tree/archive/p0-p02-full-20261011) 获取。
