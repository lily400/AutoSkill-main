# SGB 迁移实施结果

日期：2026-10-23。实际安装位置：`D:/AS/AutoSkill-main/degradation_failure_lab`。本轮新增真实模型请求 0、真实 Agent 运行 0。

**已落地全量登记、来源迁移、静态审核、目录兼容及统一准备/汇总入口。187 题的逐题语义审核与环境/评分准入仍按明确队列推进，未将静态导入冒充全体可执行。**

## 实际交付

- 固定 SGB 发布快照 `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`：2,602 个文件按原字节冻结在 `.external/skillgenbench/5a8bd61d/`，原任务和 Oracle 不修改。
- 全量 187 题登记：Code Repo 123、Code Doc 28、Domain Knowledge Doc 36。每题记录原身份、来源包、提交/输出契约、原任务资产 hash、审核维度、阻断原因及历史证据。
- 注册 211 份来源实例、99 种不同内容，按内容 hash 缓存；旧 6 个数据集登记与来源 ID 原样保留。新数据归类为发布数据集快照，不宣称已经验证论文实际实验快照。
- 导入原 64 题审核及规则映射，检查引用文件与来源 hash；Code Repo 的规则—任务—Oracle 连接明确标为待审核。
- 建立 `data/{raw_sources,manifests,condition_inputs}/sgb`、`cases/sgb`、`downstream_eval/tasks/sgb/<type>/<original_task_id>`、`results/sgb/{audits,analyses}`。
- 任务目录只保留薄适配记录，不为每题复制 pytest 等依赖，不自动把隐藏测试或源文档挂给 Agent。
- 新增一个 namespaced Scrapy 生成示例 `case024_sgb`；其新执行门禁保持 BLOCKED。旧 `case024_scrapy`、`s24r005`、`s24d001` 原位保留并显式关联。
- 新生成记录使用 `runs/gen/sgb` 和较短的新默认运行 ID，以通过当前 Windows 的中间产物路径预检。旧 case/run 发现、导出及恢复保持兼容。

## 已运行验证

| 验证 | 结果 |
| --- | --- |
| 新增 SGB 单元测试 | 17/17 通过，包含边界、漂移、兼容和无模型门禁 |
| 原恢复测试 | 11/11 通过；修复了验证期间发现的恢复路径兼容问题 |
| Linux Scrapy 冻结/SDK 假传输测试 | 7/7 通过 |
| Linux 请求预算/SDK 假传输测试 | 11/11 通过 |
| 原 Oracle 正例 | 19/19，通过 FTP 专项 |
| 原 Oracle FTP 定向反例 | 18/19，唯一目标规则失败 |
| 全项目 validate | VALID；9 个案例、219 个来源条目 |
| 历史保护 | 1,356 个旧案例/生成/校准/评分文件 hash 无变化 |
| 原数据登记 | 原 6 个数据集条目保持一致 |
| Git diff --check | 通过 |

Windows 原 framework 的 18 项测试中，迁移前后均为 15 项通过、1 项旧断言失败、2 项旧路径预检错误；没有新增失败。旧断言仍假设项目只有 case001，两个旧 fixture 的长路径触发已有保护。这些原有问题未在本次迁移中顺带修改。Windows SDK 依赖缺口在既有固定 Linux 环境中完成了实际假传输验收。

## 审核队列

- 169 题有经 hash 校验的 task-local 文档；18 个 Code Repo 任务没有这一位置的文档，仍须确认其他来源路径，未永久排除。
- 187 个源端 task.json 均通过严格限定的内存尾逗号兼容读取；引号内文本、原文件字节不变，重复键及其他非法语法拒绝。
- 67 题 descriptor 与 task.toml 存在字段差异，逐项记录，未擅自裁决。
- 31 题评分 Python 在本轮 Python 3.13.9 的静态语法检查中失败，需结合原环境复核。没有执行这些未知评分代码。
- 原 64 题语义审计继续保留各自准入结论；123 个 Code Repo 的语义审核仍待完成。
- 新批次可执行任务数量为 0：尚未完成逐题环境、Oracle 正负验证及实验冻结。Scrapy 的旧六次真实校准作为独立历史证据引用。

以上问题集合可能重叠，不能相加作为不合格任务总数。

## 使用

在实际研究根目录运行，以下均无模型调用：

```powershell
python -B scripts/lab.py sgb audit
python -B scripts/lab.py sgb list --task scrapy-task-024
python -B scripts/lab.py sgb plan --task scrapy-task-024
python -B scripts/lab.py sgb prepare --preparation-id prepare-002
python -B scripts/lab.py sgb aggregate --analysis-id analysis-002
```

准备与分析 ID 使用全新值；已完成的原始运行及预算数据库不覆盖、不清空。

当前统一汇总已准确读取原六次校准：NoSkill 0/3、CleanSkill 2/3，按每次 trial 统计，未以任一次成功代替均值。其他 186 题明确记为无已登记观察结果。

## 入口

- [SGB 操作与目录说明](D:/AS/AutoSkill-main/degradation_failure_lab/docs/sgb/README.md)
- [全量任务登记](D:/AS/AutoSkill-main/degradation_failure_lab/data/manifests/sgb/tasks.jsonl)
- [逐题审核队列](D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/migration-20261023-001/review_queue.csv)
- [导入与静态审核结果](D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/migration-20261023-001/import_result.json)
- [全量无模型准备结果](D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/prepare-20261023-001/preparation.json)
- [Linux 测试及原 Oracle 验收](D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/verification-20261023-001/result.json)
- [历史结果统一汇总](D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/migration-20261023-001/summary.json)

后续按审核队列补齐规则连接、契约裁决和环境/评分证据，再建立新的明确预算批次。当前实现没有启动大规模付费生成，也没有改写原评分来消除审核问题。
