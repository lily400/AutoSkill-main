---
id: "d3e1cf4c-29a0-51ad-a791-f42d7e30c644"
name: "边容量准入校验"
description: "在离散 tick 仿真的容量与冲突检查阶段，对车辆 ENTER_EDGE 请求做准入判定：若目标边当前车辆数已达 MaxVehicles，则拒绝请求并让车辆在该节点执行 WAIT。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "容量检查"
  - "准入判定"
  - "ENTER_EDGE"
  - "离散tick"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆在节点请求 ENTER_EDGE 进入某条边"
  - "需要判断目标边是否已达 MaxVehicles 上限"
examples:
  - input: "tick 5，E9 上已有 2 辆车，MaxVehicles = 2，N4 处第三辆车请求 ENTER_EDGE(E9)"
    output: "拒绝该请求；该车辆在本 tick 于 N4 执行 WAIT"
    notes: "批准将超过 MaxVehicles = 2"
---

# 边容量准入校验

在离散 tick 仿真的容量与冲突检查阶段，对车辆 ENTER_EDGE 请求做准入判定：若目标边当前车辆数已达 MaxVehicles，则拒绝请求并让车辆在该节点执行 WAIT。

## Prompt

在容量与冲突检查阶段处理每个 ENTER_EDGE 请求：读取目标边当前车辆数与 MaxVehicles 上限；若批准后车辆数将超过上限，则拒绝该请求，并令该车辆在本 tick 于当前节点执行 WAIT；否则批准进入。逐请求给出批准或拒绝结果。

## Objective

在容量与冲突检查阶段正确批准或拒绝车辆进入边的请求，避免超出边容量上限
## Applicable Signals

- 车辆在节点请求 ENTER_EDGE 进入某条边
- 目标边已有车辆数接近或达到 MaxVehicles

## Contraindications

- 请求不是进入边而是其他动作（如 WAIT、装卸）
- 目标边不存在或未定义容量

## Intervention Moves

- 读取目标边当前车辆数与 MaxVehicles 上限
- 比较批准后车辆数是否超过上限
- 超限则拒绝请求并令车辆在本 tick 于当前节点执行 WAIT
- 未超限则批准进入

## Workflow Steps

- 识别当前 tick 的 ENTER_EDGE 请求及其目标边
- 读取目标边当前车辆数与 MaxVehicles 上限
- 判断批准后车辆数是否超过 MaxVehicles
- 若超过则拒绝请求，并令车辆在本 tick 于当前节点执行 WAIT
- 若未超过则批准进入
- 输出每个请求的批准或拒绝结果

## Constraints

- 判定须在容量与冲突检查阶段完成
- 不得批准导致目标边车辆数超过 MaxVehicles 的请求

## Cautions

- 被拒绝的车辆须在本 tick 执行 WAIT，而非静默丢弃请求

## Output Contract

- 对每个 ENTER_EDGE 请求给出批准或拒绝结果；被拒绝车辆在该 tick 执行 WAIT。

## Example Therapist Responses

### Example 1

- Client/Input: tick 5，E9 上已有 2 辆车，MaxVehicles = 2，N4 处第三辆车请求 ENTER_EDGE(E9)
- Therapist/Output: 拒绝该请求；该车辆在本 tick 于 N4 执行 WAIT
- Notes: 批准将超过 MaxVehicles = 2

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆在节点请求 ENTER_EDGE 进入某条边
- 需要判断目标边是否已达 MaxVehicles 上限

## Examples

### Example 1

Input:

  tick 5，E9 上已有 2 辆车，MaxVehicles = 2，N4 处第三辆车请求 ENTER_EDGE(E9)

Output:

  拒绝该请求；该车辆在本 tick 于 N4 执行 WAIT

Notes:

  批准将超过 MaxVehicles = 2
