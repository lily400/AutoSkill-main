# degradation_failure_lab — 当前多案例实验框架

研究固定程序文档的退化如何影响官方 Anything2Skill 的技能提取、编译及质量。**正式工作树只有一套运行系统**；历史 P0/P0.1/P0.2 的完整提交保存在 [归档分支](https://github.com/lily400/AutoSkill-main/tree/archive/p0-p02-full-20261011)，本分支不再保存两次历史运行的完整文件。

## 当前目录

| 目录 | 职责 |
|---|---|
| `data/raw_sources/` | 官方原始文档，commit 固定且字节哈希固定 |
| `data/manifests/` + `data/catalog.json` | 唯一来源目录与来源标识 |
| `cases/case001_qsv_select/` | 案例定义、规则清单与 Clean 条件输入 |
| `configs/` | 官方源码路径、模型和预算 |
| `src/degradation_lab/` | 公共运行器、官方适配器、追踪与评价 |
| `scripts/lab.py` | 唯一命令入口 |
| `schemas/` | 案例、来源、条件、规则、评价的数据协议 |
| `runs/<case>/<condition>/<run_id>/` | 新实验独立 SkillBank 和中间产物，默认不提交 Git |
| `evaluations/` | **新**运行的人工/自动规则评价 |
| `results/` | 导出、聚合和运行索引，按需要留存 |

## 命令

在 `degradation_failure_lab` 下执行（Windows PowerShell）：

```powershell
$py = 'D:\anoconda1\envs\autoskill\python.exe'
& $py -B scripts\lab.py list
& $py -B scripts\lab.py validate
& $py -B scripts\lab.py plan --case case001_qsv_select --condition clean --repeat 1
& $py -B -m unittest discover -s tests -v
```

以下命令会实际调用付费模型，尚未完成新框架的真实端到端验收：

```powershell
& $py -B scripts\lab.py run --case case001_qsv_select --condition clean --repeat 1
```

真实运行完成后可执行 `lab.py verify --run <run_id>`，然后 `evaluation-init`、`evaluation-validate` 和 `aggregate`。未审核的规则不会自动计为正确。

**边界**：仍采用官方 `AutoSkill4Doc.extract_from_doc`；没有修改上游生成器、提示词或注册算法。已实现多案例配置、顺序批次、输入哈希、独立 store、阶段导出和评价合同；尚未实现文档退化算子及下游 Agent 任务执行。

## 历史恢复

历史 P0 成功运行 `p0_qsv_select_clean_002`、失败运行 `p0_qsv_select_clean_001`、旧数据/脚本/审计/规则审核均位于归档分支；**归档是 Git 服务器上的完整提交快照，不等于已在本地恢复并通过独立复验**。详见 [归档指南](docs/HISTORY_ARCHIVE.md)。清理分支不承诺 `verify --run p0_...` 可用。

项目结构与案例逐步教程参见 [PROJECT_STRUCTURE_GUIDE.md](docs/PROJECT_STRUCTURE_GUIDE.md)。
