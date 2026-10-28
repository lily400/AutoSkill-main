---
id: "15dc5310-2210-53f1-a5fe-b75dd3ad5173"
name: "容量削减事件下的边容量与准入判定"
description: "在容量削减事件生效期间，按基线车道容量乘以事件容量系数并向下取整计算边的有效最大车辆数，并在容量与冲突检查阶段据此批准或拒绝 ENTER_EDGE 请求。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "容量裁决"
  - "容量乘子"
  - "准入控制"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "某条边存在生效中的容量削减事件"
  - "车辆请求 ENTER_EDGE 且需判断是否超出有效容量"
examples:
  - input: "事件 I1 覆盖 E9（N4 到 N9），CapacityMultiplier = 0.5；E9 基线 LaneCount = 2，CapacityPerLane = 2；tick 5 时 E9 已有 2 辆车，N4 处第三辆车请求 ENTER_EDGE(E9)"
    output: "基线 MaxVehicles = 4，有效 MaxVehicles = floor(4 × 0.5) = 2；批准将超出 2，故拒绝请求，该车在 N4 执行 WAIT"
    notes: "事件区间为 ticks 4-15 含首尾"
---

# 容量削减事件下的边容量与准入判定

在容量削减事件生效期间，按基线车道容量乘以事件容量系数并向下取整计算边的有效最大车辆数，并在容量与冲突检查阶段据此批准或拒绝 ENTER_EDGE 请求。

## Prompt

当某条边存在生效中的容量削减事件且车辆请求 ENTER_EDGE 时：1) 确认事件覆盖当前 tick；2) 计算基线 MaxVehicles = LaneCount × CapacityPerLane；3) 有效 MaxVehicles = floor(基线 MaxVehicles × CapacityMultiplier)；4) 在容量与冲突检查阶段比较当前边内车辆数与有效 MaxVehicles，若批准将超出则拒绝请求，车辆在该 tick 执行 WAIT；5) 输出有效 MaxVehicles 数值与批准/拒绝结论。

## Objective

在容量削减事件生效期间正确计算边有效容量并据此裁决车辆进入请求
## Applicable Signals

- 边存在生效中的容量削减事件
- 事件覆盖当前 tick
- 车辆在相邻节点请求 ENTER_EDGE

## Contraindications

- 无生效事件时不应套用容量乘子
- 事件未覆盖当前 tick 时按基线容量处理

## Intervention Moves

- 确认事件生效区间覆盖当前 tick
- 计算基线 MaxVehicles = LaneCount × CapacityPerLane
- 有效 MaxVehicles = floor(基线 MaxVehicles × CapacityMultiplier)
- 在容量与冲突检查阶段比较当前车辆数与有效 MaxVehicles
- 超出则拒绝请求并令车辆该 tick 执行 WAIT

## Workflow Steps

- 确认目标边存在生效中的容量削减事件且覆盖当前 tick
- 计算基线 MaxVehicles = LaneCount × CapacityPerLane
- 计算有效 MaxVehicles = floor(基线 MaxVehicles × CapacityMultiplier)
- 在容量与冲突检查阶段比较当前边内车辆数与有效 MaxVehicles
- 若批准将超出有效 MaxVehicles 则拒绝 ENTER_EDGE 请求
- 被拒车辆在该 tick 执行 WAIT

## Constraints

- 有效容量必须向下取整
- 仅在事件覆盖的 tick 内应用容量乘子
- 准入裁决须在容量与冲突检查阶段进行

## Cautions

- 事件区间边界（含首尾 tick）需确认是否包含当前 tick
- 无事件时不得套用容量乘子

## Output Contract

- 给出有效 MaxVehicles 数值及批准/拒绝结论，被拒车辆在该 tick 执行 WAIT

## Example Therapist Responses

### Example 1

- Client/Input: 事件 I1 覆盖 E9（N4 到 N9），CapacityMultiplier = 0.5；E9 基线 LaneCount = 2，CapacityPerLane = 2；tick 5 时 E9 已有 2 辆车，N4 处第三辆车请求 ENTER_EDGE(E9)
- Therapist/Output: 基线 MaxVehicles = 4，有效 MaxVehicles = floor(4 × 0.5) = 2；批准将超出 2，故拒绝请求，该车在 N4 执行 WAIT
- Notes: 事件区间为 ticks 4-15 含首尾

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 某条边存在生效中的容量削减事件
- 车辆请求 ENTER_EDGE 且需判断是否超出有效容量

## Examples

### Example 1

Input:

  事件 I1 覆盖 E9（N4 到 N9），CapacityMultiplier = 0.5；E9 基线 LaneCount = 2，CapacityPerLane = 2；tick 5 时 E9 已有 2 辆车，N4 处第三辆车请求 ENTER_EDGE(E9)

Output:

  基线 MaxVehicles = 4，有效 MaxVehicles = floor(4 × 0.5) = 2；批准将超出 2，故拒绝请求，该车在 N4 执行 WAIT

Notes:

  事件区间为 ticks 4-15 含首尾
