**五题生成与下游均已执行完，请勿重复运行付费命令。** 正式统计已采用批准的Scrapy050观察v2；原7/8仍在原分析中。现阶段只需查看EXECUTION.md、downstream-results.json与正式汇总。

# 五任务执行命令

更新：2026-10-28。当前聊天已获授权开始上游提取；请先看 upstream-results.json / 实际run目录，避免重复启动已经开始的run。Capacity006 的 e06f003 已完成，等待条件已满足。五题上游已完成，Referee 正式来源为 r09g002；r09g001 失败批次单独保留。不要重复运行 generate。本文件用于复核命令，不授权自动重跑。

```powershell
$run = 'D:\AS\AutoSkill-main\degradation_failure_lab\scripts\sgb\Invoke-CleanTask.ps1'
```

不带 -Approve 的generate仅预览预算与配置SHA。执行命令中的 -Approve 表示批准对应阶段的精确任务和预算；不能把它当作无费用预览。初始每题提取最多600次HTTP、240万observed-token停止阈值；Referee 基础设施有界重提取配置为100次/30万，已完成；下游每配对最多12次HTTP。

## pydantic-task-001

```powershell
& $run -Task pydantic-task-001 -Phase generate -Approve
# 生成完成、且Capacity006配对结束后再执行：
& $run -Task pydantic-task-001 -Phase evaluate -Approve
```

## scrapy-task-050

```powershell
& $run -Task scrapy-task-050 -Phase generate -Approve
# 生成完成、且Capacity006配对结束后再执行：
& $run -Task scrapy-task-050 -Phase evaluate -Approve
```

## pydantic-task-004

```powershell
& $run -Task pydantic-task-004 -Phase generate -Approve
# 生成完成、且Capacity006配对结束后再执行：
& $run -Task pydantic-task-004 -Phase evaluate -Approve
```

## reviews_csv_conformance_validator_007

```powershell
& $run -Task reviews_csv_conformance_validator_007 -Phase generate -Approve
# 生成完成、且Capacity006配对结束后再执行：
& $run -Task reviews_csv_conformance_validator_007 -Phase evaluate -Approve
```

## referee_attempt_decision_router_009

```powershell
& $run -Task referee_attempt_decision_router_009 -Phase generate -Approve
# 生成完成、且Capacity006配对结束后再执行：
& $run -Task referee_attempt_decision_router_009 -Phase evaluate -Approve
```

evaluate依次调用现有下游授权、原样冻结/最终零模型prepare、一次NoSkill/CleanSkill配对、Verifier、分析和正式汇总。无需手工改JSON。若已存在实验身份会拒绝重新创建预算；发生停止时只检查状态/分析，不再次运行付费命令。

```powershell
& $run -Task pydantic-task-001 -Phase status
& $run -Task pydantic-task-001 -Phase analyze
```

其他任务替换Task即可。生成失败可用 `python -B D:\AS\AutoSkill-main\degradation_failure_lab\scripts\lab.py verify --run <实际run-id>` 检查保留证据；该命令不发送模型请求。没有自动resume或自动加额。
