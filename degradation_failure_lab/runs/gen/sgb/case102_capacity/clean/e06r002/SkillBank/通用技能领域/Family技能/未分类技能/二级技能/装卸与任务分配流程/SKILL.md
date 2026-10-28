---
id: "f2918fa1-b55b-5c3a-b164-564a5eb75670"
name: "装卸与任务分配流程"
description: "依据车辆容量、当前位置与货物起点终点，将 PENDING_AT_ORIGIN 货物分配给合适车辆，并执行装卸与状态更新。适用于存在待分配货物且有空闲车辆位于货物起点的仿真装卸阶段。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "物流任务分配"
  - "装卸"
  - "容量匹配"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "存在状态为 PENDING_AT_ORIGIN 的待分配货物"
  - "存在空闲车辆且位于货物起点"
examples:
  - input: "货物 C1 位于 N1，尺寸 3，状态 PENDING_AT_ORIGIN；车辆 V1 位于 N1，容量 12，空闲"
    output: "C1 分配给 V1，V1 载货更新，C1 状态更新为已分配"
    notes: "容量与位置均满足"
---

# 装卸与任务分配流程

依据车辆容量、当前位置与货物起点终点，将 PENDING_AT_ORIGIN 货物分配给合适车辆，并执行装卸与状态更新。适用于存在待分配货物且有空闲车辆位于货物起点的仿真装卸阶段。

## Prompt

在仿真装卸阶段，遍历 PENDING_AT_ORIGIN 货物，检查空闲车辆是否位于货物起点且容量足够，完成分配并更新车辆载货与货物状态；容量不足或位置不符时跳过该车辆。

## Objective

完成货物到车辆的分配与装卸状态更新
## Applicable Signals

- 货物状态为 PENDING_AT_ORIGIN 且无分配车辆
- 车辆状态为空闲且位于货物起点
- 车辆剩余容量满足货物尺寸

## Contraindications

- 货物已分配或已送达
- 车辆容量不足以装载货物
- 车辆不在货物起点

## Intervention Moves

- 按货物优先级或释放时间筛选待分配货物
- 匹配位于货物起点且容量足够的空闲车辆
- 将货物分配给车辆并更新车辆载货与货物状态

## Workflow Steps

- 识别状态为 PENDING_AT_ORIGIN 且无分配车辆的货物
- 筛选位于货物起点且空闲的车辆
- 校验车辆剩余容量是否满足货物尺寸
- 将货物分配给满足条件的车辆
- 更新车辆载货状态与货物状态

## Constraints

- 仅分配 PENDING_AT_ORIGIN 状态的货物
- 车辆必须位于货物起点
- 车辆剩余容量必须不小于货物尺寸

## Cautions

- 容量不足或位置不符的车辆应跳过，不得强行分配

## Output Contract

- 更新后的车辆载货状态与货物状态（已分配/已装载）

## Example Therapist Responses

### Example 1

- Client/Input: 货物 C1 位于 N1，尺寸 3，状态 PENDING_AT_ORIGIN；车辆 V1 位于 N1，容量 12，空闲
- Therapist/Output: C1 分配给 V1，V1 载货更新，C1 状态更新为已分配
- Notes: 容量与位置均满足

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 存在状态为 PENDING_AT_ORIGIN 的待分配货物
- 存在空闲车辆且位于货物起点

## Examples

### Example 1

Input:

  货物 C1 位于 N1，尺寸 3，状态 PENDING_AT_ORIGIN；车辆 V1 位于 N1，容量 12，空闲

Output:

  C1 分配给 V1，V1 载货更新，C1 状态更新为已分配

Notes:

  容量与位置均满足
