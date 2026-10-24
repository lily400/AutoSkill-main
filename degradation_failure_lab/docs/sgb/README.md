# SGB 主线：登记、审核与迁移

研究根目录：`D:/AS/AutoSkill-main/degradation_failure_lab`。固定发布版本：`5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。

本次已接入全量 187 题的身份、来源、任务资产和审核队列，包括 Code Repo 123、Code Doc 28、Domain Knowledge Doc 36。统一入口不会在导入、审核、准备或汇总时加载模型或执行任务代码。

## 常用命令

在研究根目录运行；以下命令均不调用模型。

```powershell
python -B scripts/lab.py sgb audit
python -B scripts/lab.py sgb list --task scrapy-task-024
python -B scripts/lab.py sgb plan --task scrapy-task-024
python -B scripts/lab.py sgb prepare --preparation-id prepare-002
python -B scripts/lab.py sgb aggregate --analysis-id analysis-002
```

prepare 默认检查全部任务；可用 `--task <原始task_id或task_key> ...` 限定范围。准备/分析 ID 必须全新，不覆盖已有证据。prepare 产出元数据和完整性检查结果，**不是一次 Harbor Trial，也不表示环境及评分已经验收**。aggregate 只汇总已登记的历史执行，未运行任务不补零、不补成功；不可判分单列。

完整上游校验继续使用 `python -B scripts/lab.py validate`。新 namespaced 示例为 `case024_sgb`，可用 `python -B scripts/lab.py plan --case case024_sgb --condition clean` 检查生成计划；新 case 的执行门禁保持 BLOCKED，待新的实验与环境/评分绑定完成。原 `case024_scrapy`、`s24r005`、`s24d001` 已全部归入 SGB；逻辑 ID 和原始运行字节保留，旧路径由 relocations.json 解析，不能用新目录绕过旧预算或重发请求。

## 数据与目录

| 位置 | 内容 |
| --- | --- |
| `.external/skillgenbench/5a8bd61d/` | 原始发布快照及逐文件 hash，禁止修改 |
| `data/manifests/sgb/tasks.jsonl` | 全量任务登记表，包含来源、协议、原任务、差异、审核证据及历史运行引用 |
| `data/manifests/sgb/sources/` | 211 份任务来源实例的清单；来源类别是 PUBLISHED_DATASET_SNAPSHOT，不冒称论文实验快照已验证 |
| `data/raw_sources/sgb/5a8bd61d/` | 按内容 hash 缓存的原字节文档，共 99 种内容；保留各自来源身份 |
| `data/condition_inputs/sgb/` | 未来的退化输入；导入不会自动生成退化条件 |
| `cases/sgb/<case_id>/` | 新生成案例；当前有 Scrapy024，以及新接入的 Pydantic001 工程示范 |
| `downstream_eval/tasks/sgb/<type>/<original_task_id>/` | 全量薄任务记录；Scrapy024 与 Pydantic001 有完整任务/评分资产，其他题仍为元数据记录 |
| `downstream_eval/sgb/` | 通用 SGB 准备/汇总、Scrapy024 运行器与 Pydantic001 无模型工程验收 |
| `scripts/sgb/` | SGB 专用启动脚本，凭据仍复用公共入口 |
| `runs/eval/sgb/<original_task_id>/<experiment>/` | 新下游校准运行；旧 ID 不可跨目录复用 |
| `runs/gen/sgb/<case>/<condition>/<run>/` | 新上游运行路径；缩短 gen 和新默认 ID 是为兼容 Windows 路径限制 |
| `results/sgb/audits/<audit_id>/` | 导入结果、逐题 review_queue.csv、原 64 题审核证据、准备记录 |
| `results/sgb/analyses/<analysis_id>/` | 逐 trial 结果和汇总；与不可覆盖的原始运行分离 |

`task_key` 是稳定内部身份，完整语义身份为 revision/source_type/collection/original_task_id。多个任务可关联相同来源内容；这不使它们成为独立来源，也不会自动把独立生成重复合并。

## 当前准入状态

导入核对文件和契约，尚未给 187 个任务生成新的可付费执行许可。记录中应分别查看 source_status、research_fit、oracle_status、runtime_status、calibration_status 和 blockers：

- 169 题有已校验的 task-local 文档，18 个 Code Repo 任务需继续确认其他来源路径，不能直接永久排除。
- 187 个源 descriptor 通过只在内存中处理末尾逗号的专用读取器解析。引号内文本保持不变，重复键和其他非法 JSON 拒绝；原 descriptor 不改写。
- 67 题的 descriptor 与 task.toml 字段不同，具体字段在登记表及 CSV 中保留，不能静默选择一份。
- 31 题的评分 Python 在本次 Python 解释器下语法解析失败，需要结合原运行环境核查。没有执行这些评分脚本。
- 原 64 题研究审计原样引用；123 个 Code Repo 的规则—任务—Oracle 语义审核仍待完成。
- Scrapy024 原六次校准已关联，NoSkill 0/3、CleanSkill 2/3；它是历史真实结果，不是本次新增请求，也不代表其他题已校准。

下一步按 review_queue.csv 逐项补齐规则连接、契约裁决、原 Oracle 正负验证和运行环境。修改 Oracle 时另存版本及差异，原版始终保留。Task-024 的布尔桥接器不作为其他任务的默认评分实现。

## 冻结与可追溯性

`sgb audit` 验证完整快照、登记表、来源清单、源文本、原任务资产、引用的旧审核与旧结果的 hash。正式更改审核或适配时应创建有证据的新版本，不通过手改 hash 来隐藏变化。

`configs/experiments/sgb/template.json` 是未填模型和预算的草稿，不会启动实验。全部 187 题按四条件、每条件三次即 2,244 个 Agent trial，必须先确定资源和预算，再执行明确批次。

工程测试：`python -B -m unittest discover -s tests -p test_sgb.py -v`。原有案例与运行格式继续可读；历史 SkillBank、预算数据库和运行记录已按 SGB 归档，原始运行文件保持原字节。活动任务与代码可迁入 SGB；此次 Scrapy024 的指令、Oracle 和全部 scorer 文件逐项校验不变。

Scrapy024 的活动目录整理见 [2026-10-24 迁移记录](layout_20261024.md)。历史 execution_manifest 仍保存原路径；迁移审计中的 `before.zip` 保存迁移前文件，`historical_execution_verification.json` 记录原路径经存档解析后的逐项验证，不改写旧清单。

新任务逐文件接入示范：[Pydantic001 源文与任务接入](add_task_walkthrough.md)。正反例工程验收不等于真实 Skill/Agent 闭环。

完整归档规则及迁移结果见 [Scrapy 全量归档](archive_20261024.md)。历史清单中的旧路径保留为证据，不通过符号链接或旧目录维持第二套活动文件。
