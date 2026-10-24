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

完整上游校验继续使用 `python -B scripts/lab.py validate`。新 namespaced 示例为 `case024_sgb`，可用 `python -B scripts/lab.py plan --case case024_sgb --condition clean` 检查生成计划；新 case 的执行门禁保持 BLOCKED，待新的实验与环境/评分绑定完成。原 `case024_scrapy`、`s24r005`、`s24d001` 仍在旧位置，不能用新 ID 绕过旧预算或重发请求。

## 数据与目录

| 位置 | 内容 |
| --- | --- |
| `.external/skillgenbench/5a8bd61d/` | 原始发布快照及逐文件 hash，禁止修改 |
| `data/manifests/sgb/tasks.jsonl` | 全量任务登记表，包含来源、协议、原任务、差异、审核证据及历史运行引用 |
| `data/manifests/sgb/sources/` | 211 份任务来源实例的清单；来源类别是 PUBLISHED_DATASET_SNAPSHOT，不冒称论文实验快照已验证 |
| `data/raw_sources/sgb/5a8bd61d/` | 按内容 hash 缓存的原字节文档，共 99 种内容；保留各自来源身份 |
| `data/condition_inputs/sgb/` | 未来的退化输入；导入不会自动生成退化条件 |
| `cases/sgb/<case_id>/` | 新生成案例；当前仅有已建立规则连接的 Scrapy024 示例 |
| `downstream_eval/tasks/sgb/<type>/<original_task_id>/adapter.json` | 薄任务记录，引用原始资产；不复制第三方依赖，不将隐藏测试发给 Agent |
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

工程测试：`python -B -m unittest discover -s tests -p test_sgb.py -v`。原有案例与运行格式继续可读；不迁移、覆盖原 SkillBank、任务、Oracle、预算数据库或运行记录。
