---
id: "272c6898-fbc4-5677-abfc-bc4e991d997c"
name: "事故容量折减计算"
description: "在事故生效区间内，按 CapacityMultiplier 对受影响边的基础最大车辆数做向下取整折减，得到有效 MaxVehicles，用于事故期间更新边容量约束。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "事故影响建模"
  - "容量折减"
  - "容量乘子"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "存在活动事故且带 CapacityMultiplier"
  - "需要更新受影响边的容量上限"
examples:
  - input: "E9 基础 LaneCount = 2，CapacityPerLane = 2，事故 I1 的 CapacityMultiplier = 0.5，生效区间为 ticks 4-15。"
    output: "基础 MaxVehicles = 4；事故期间有效 MaxVehicles = floor(4 × 0.5) = 2。"
    notes: "仅在 ticks 4-15 内使用有效值 2。"
---

# 事故容量折减计算

在事故生效区间内，按 CapacityMultiplier 对受影响边的基础最大车辆数做向下取整折减，得到有效 MaxVehicles，用于事故期间更新边容量约束。

## Prompt

当存在活动事故且该事故带有 CapacityMultiplier 时，对受影响边执行容量折减：先取该边的基础 MaxVehicles（由 LaneCount × CapacityPerLane 得到），再乘以 CapacityMultiplier，最后向下取整，得到事故期间的有效 MaxVehicles。仅在事故生效区间内应用该折减值；事故未生效或已结束时，使用基础容量。

## Objective

计算事故期间边的有效最大车辆数
## Applicable Signals

- 事故处于生效区间内
- 事故参数包含 CapacityMultiplier
- 需要确定受影响边的容量上限

## Contraindications

- 事故未生效或已结束
- 需要判定信号相位通行

## Intervention Moves

- 取受影响边的基础 MaxVehicles
- 将基础 MaxVehicles 乘以 CapacityMultiplier
- 对乘积向下取整得到有效 MaxVehicles

## Workflow Steps

- 确认事故处于生效区间内且带有 CapacityMultiplier。
- 确定受影响边的基础 MaxVehicles（LaneCount × CapacityPerLane）。
- 计算有效 MaxVehicles = floor(基础 MaxVehicles × CapacityMultiplier)。
- 在事故生效区间内以有效 MaxVehicles 作为该边的容量上限。

## Constraints

- 折减结果必须向下取整。
- 仅在事故生效区间内应用折减值。
- 基础 MaxVehicles 由 LaneCount × CapacityPerLane 得出。

## Cautions

- 事故结束后应恢复基础容量。
- 本技能只处理容量数值折减，不判定信号相位通行。

## Output Contract

- 输出受影响边的有效 MaxVehicles 值。

## Example Therapist Responses

### Example 1

- Client/Input: E9 基础 LaneCount = 2，CapacityPerLane = 2，事故 I1 的 CapacityMultiplier = 0.5，生效区间为 ticks 4-15。
- Therapist/Output: 基础 MaxVehicles = 4；事故期间有效 MaxVehicles = floor(4 × 0.5) = 2。
- Notes: 仅在 ticks 4-15 内使用有效值 2。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 存在活动事故且带 CapacityMultiplier
- 需要更新受影响边的容量上限

## Examples

### Example 1

Input:

  E9 基础 LaneCount = 2，CapacityPerLane = 2，事故 I1 的 CapacityMultiplier = 0.5，生效区间为 ticks 4-15。

Output:

  基础 MaxVehicles = 4；事故期间有效 MaxVehicles = floor(4 × 0.5) = 2。

Notes:

  仅在 ticks 4-15 内使用有效值 2。
