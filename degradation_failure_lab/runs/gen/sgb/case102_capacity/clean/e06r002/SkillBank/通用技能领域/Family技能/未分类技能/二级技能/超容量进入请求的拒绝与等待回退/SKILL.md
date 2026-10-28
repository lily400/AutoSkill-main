---
id: "d954539f-c4e1-500a-b366-90101b10e80b"
name: "超容量进入请求的拒绝与等待回退"
description: "在容量与冲突检查阶段，当批准 ENTER_EDGE 请求会使目标边车辆数超过有效 MaxVehicles 时，拒绝该请求并令车辆在源节点执行 WAIT 一个 tick，从而守住边容量上限并给出确定的回退行为。"
version: "0.1.0"
tags:
  - "容量约束"
  - "准入拒绝"
  - "等待回退"
  - "交通仿真"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆在源节点发起 ENTER_EDGE 请求"
  - "目标边存在容量乘数或容量缩减事件"
  - "批准进入请求可能使边车辆数超过有效 MaxVehicles"
examples:
  - input: "边 E9 基线 MaxVehicles=4，事件容量乘数 0.5，有效 MaxVehicles=2；tick 5 时 E9 已有 2 辆车，源节点车辆请求 ENTER_EDGE(E9)"
    output: "请求被拒绝，车辆在源节点执行 WAIT 一个 tick"
    notes: "批准将超过有效 MaxVehicles=2"
---

# 超容量进入请求的拒绝与等待回退

在容量与冲突检查阶段，当批准 ENTER_EDGE 请求会使目标边车辆数超过有效 MaxVehicles 时，拒绝该请求并令车辆在源节点执行 WAIT 一个 tick，从而守住边容量上限并给出确定的回退行为。

## Prompt

在容量与冲突检查阶段处理 ENTER_EDGE 请求时：先取目标边的有效 MaxVehicles（含事件容量乘数影响），再判断批准后边车辆数是否会超过该上限。若会超过，则拒绝该请求，并将车辆状态更新为在源节点 WAIT 一个 tick；若未超过，则不应拒绝。

## Objective

防止边容量被突破并保证被拒车辆有确定的回退行为
## Applicable Signals

- 批准进入请求将导致边车辆数超过有效容量
- 边当前车辆数已达到有效 MaxVehicles

## Contraindications

- 边仍有剩余容量时不应拒绝
- 不得在未计算有效容量前直接拒绝

## Intervention Moves

- 计算目标边的有效 MaxVehicles
- 比较批准后车辆数与有效 MaxVehicles
- 超限时拒绝请求并将车辆置为源节点 WAIT 一个 tick

## Workflow Steps

- 确定目标边的有效 MaxVehicles（考虑容量乘数等影响）
- 判断批准 ENTER_EDGE 后边车辆数是否超过有效 MaxVehicles
- 若超过，则拒绝该请求
- 将被拒车辆状态更新为在源节点 WAIT 一个 tick
- 若未超过，则不应拒绝

## Constraints

- 拒绝判定必须以有效 MaxVehicles 为准
- 被拒车辆必须有确定的回退行为（源节点 WAIT）

## Cautions

- 有效容量可能因事件容量乘数而低于基线，需先计算再判定

## Output Contract

- 请求被标记为拒绝，车辆状态更新为在源节点 WAIT

## Example Therapist Responses

### Example 1

- Client/Input: 边 E9 基线 MaxVehicles=4，事件容量乘数 0.5，有效 MaxVehicles=2；tick 5 时 E9 已有 2 辆车，源节点车辆请求 ENTER_EDGE(E9)
- Therapist/Output: 请求被拒绝，车辆在源节点执行 WAIT 一个 tick
- Notes: 批准将超过有效 MaxVehicles=2

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆在源节点发起 ENTER_EDGE 请求
- 目标边存在容量乘数或容量缩减事件
- 批准进入请求可能使边车辆数超过有效 MaxVehicles

## Examples

### Example 1

Input:

  边 E9 基线 MaxVehicles=4，事件容量乘数 0.5，有效 MaxVehicles=2；tick 5 时 E9 已有 2 辆车，源节点车辆请求 ENTER_EDGE(E9)

Output:

  请求被拒绝，车辆在源节点执行 WAIT 一个 tick

Notes:

  批准将超过有效 MaxVehicles=2
