---
id: "1c367e1d-c7f3-5cc3-a526-ae75a40a061a"
name: "未交付货物延迟计分规则"
description: "在场景结束时，对仍未交付的货物按统一公式计算延迟量，用于结算服务评分。适用于场景收尾结算阶段，需要为每个未交付货物给出延迟数值时使用。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "场景结算"
  - "延迟计分"
  - "未交付货物"
  - "服务评分"
  - "场景收尾"
triggers:
  - "场景到达最终 tick 需要结算未交付货物"
  - "需要计算货物延迟以汇总服务评分"
  - "需要计算网络服务评分中的延迟惩罚"
examples:
  - input: "场景到达最终 tick，某货物 DueTime 早于 FinalTick + 1 且仍未交付"
    output: "该货物延迟 = FinalTick + 1 − DueTime，为正数"
    notes: "延迟量用于服务评分结算"
  - input: "场景结束，FinalTick=100，某未交付货物 DueTime=90"
    output: "lateness = (100 + 1) - 90 = 11"
---

# 未交付货物延迟计分规则

在场景结束时，对仍未交付的货物按统一公式计算延迟量，用于结算服务评分。适用于场景收尾结算阶段，需要为每个未交付货物给出延迟数值时使用。

## Prompt

当场景到达最终 tick 并需要结算未交付货物时，逐一识别仍未交付的货物，按公式 lateness = (FinalTick + 1 − DueTime) 计算每个货物的延迟量，并输出每个未交付货物的延迟数值。不要对已交付货物计算延迟，也不要在场景结束前使用本规则。

## Objective

按统一公式计算场景结束时未交付货物的延迟量
## Applicable Signals

- 场景已到达最终 tick
- 存在仍未交付的货物
- 需要为服务评分提供延迟数据
- 仿真已到达最终 tick
- 存在未交付的货物

## Contraindications

- 货物已在场景内交付
- 场景尚未结束
- 货物已在场景内交付完成

## Intervention Moves

- 识别场景结束时仍未交付的货物
- 对每个未交付货物应用公式 lateness = (FinalTick + 1 − DueTime)
- 输出每个未交付货物的延迟数值
- 识别所有未交付货物
- 对每个未交付货物应用公式 (FinalTick + 1 - DueTime)
- 汇总延迟数值用于服务评分

## Workflow Steps

- 确认场景已到达最终 tick
- 筛选出仍未交付的货物
- 对每个未交付货物计算 (FinalTick + 1 − DueTime)
- 汇总并输出每个未交付货物的延迟数值
- 筛选出所有未交付货物
- 对每个未交付货物计算 lateness = (FinalTick + 1) - DueTime
- 逐项记录延迟数值并汇总

## Constraints

- 仅对场景结束时仍未交付的货物计算延迟
- 延迟公式固定为 (FinalTick + 1 − DueTime)
- 仅对未交付货物应用该公式
- 公式固定为 (FinalTick + 1 - DueTime)，不得改动

## Cautions

- 不要在场景结束前提前结算
- 不要对已交付货物重复计算延迟
- 已交付货物不参与此延迟计算
- 场景未结束时不应提前结算

## Output Contract

- 每个未交付货物的延迟数值列表，可用于汇总服务评分
- 每个未交付货物的延迟数值及汇总

## Example Therapist Responses

### Example 1

- Client/Input: 场景到达最终 tick，某货物 DueTime 早于 FinalTick + 1 且仍未交付
- Therapist/Output: 该货物延迟 = FinalTick + 1 − DueTime，为正数
- Notes: 延迟量用于服务评分结算

### Example 2

- Client/Input: 场景结束，FinalTick=100，某未交付货物 DueTime=90
- Therapist/Output: lateness = (100 + 1) - 90 = 11

## Triggers

- 场景到达最终 tick 需要结算未交付货物
- 需要计算货物延迟以汇总服务评分
- 需要计算网络服务评分中的延迟惩罚

## Examples

### Example 1

Input:

  场景到达最终 tick，某货物 DueTime 早于 FinalTick + 1 且仍未交付

Output:

  该货物延迟 = FinalTick + 1 − DueTime，为正数

Notes:

  延迟量用于服务评分结算

### Example 2

Input:

  场景结束，FinalTick=100，某未交付货物 DueTime=90

Output:

  lateness = (100 + 1) - 90 = 11
