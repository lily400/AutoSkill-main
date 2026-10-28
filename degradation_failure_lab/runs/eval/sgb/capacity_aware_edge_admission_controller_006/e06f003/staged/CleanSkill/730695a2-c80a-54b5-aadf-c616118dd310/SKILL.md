---
id: "730695a2-c80a-54b5-aadf-c616118dd310"
name: "Tick 处理与快照生成流程"
description: "按固定阶段顺序处理一个仿真 tick（事件→移动承诺→容量与冲突→移动执行→装卸→指标），并输出该 tick 的状态快照。适用于需要推进离散时间步并记录全局与实体状态时。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "离散时间步"
  - "tick处理"
  - "状态快照"
triggers:
  - "需要从当前状态推进到下一 tick"
  - "需要生成 GLOBAL/NODES/EDGES/VEHICLES 等快照"
examples:
  - input: "tick 0，控制器选择 V1: START_LOADING([C1])，C1 SizeUnits=3，TRUCK HandlingRate=4"
    output: "tick 1 快照：V1 已完成装载 C1 并在 N1 空闲，C1 在车上；GLOBAL TimeTick: 1, ScoreSoFar: 0"
    notes: "WorkUnits=3 小于 HandlingRate=4，作业在单 tick 内完成"
---

# Tick 处理与快照生成流程

按固定阶段顺序处理一个仿真 tick（事件→移动承诺→容量与冲突→移动执行→装卸→指标），并输出该 tick 的状态快照。适用于需要推进离散时间步并记录全局与实体状态时。

## Prompt

从当前状态出发，按固定阶段顺序推进一个 tick：1) 处理事件/事故；2) 收集移动承诺；3) 解决容量与冲突；4) 执行移动；5) 执行装卸阶段；6) 计算指标。随后输出该 tick 的状态快照，包含 GLOBAL（TimeTick、ScoreSoFar）及各实体（NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE）状态。严格按阶段顺序执行，不跳步、不合并阶段。

## Objective

按规定的阶段顺序推进一个 tick 并产出可核对的状态快照
## Applicable Signals

- 需要从当前状态推进到下一 tick
- 需要生成 GLOBAL/NODES/EDGES/VEHICLES 等快照

## Contraindications

- 需要跨多 tick 的完整场景规划
- 仅需查询静态规则说明

## Intervention Moves

- 按事件→移动承诺→容量与冲突→移动执行→装卸→指标的顺序逐阶段处理
- 在装卸阶段依据 SizeUnits 与 HandlingRate 判定作业是否在单 tick 内完成
- 生成包含 TimeTick、ScoreSoFar 及各实体状态的快照

## Workflow Steps

- 阶段1：处理事件/事故（无事故则跳过）
- 阶段2：收集移动承诺（未请求移动的车辆无承诺）
- 阶段3：解决容量与冲突（无冲突则跳过）
- 阶段4：执行移动（无承诺则无车辆移动）
- 阶段5：执行装卸阶段，按 SizeUnits 与 HandlingRate 判定作业完成情况
- 阶段6：计算指标
- 输出该 tick 的状态快照（GLOBAL 及各实体状态）

## Constraints

- 必须严格按固定阶段顺序执行，不跳步、不合并阶段
- 快照须包含 TimeTick 与 ScoreSoFar

## Cautions

- 装卸作业是否在单 tick 内完成取决于 SizeUnits 与 HandlingRate 的比较

## Output Contract

- 包含 TimeTick、ScoreSoFar 及各实体状态的 tick 快照

## Example Therapist Responses

### Example 1

- Client/Input: tick 0，控制器选择 V1: START_LOADING([C1])，C1 SizeUnits=3，TRUCK HandlingRate=4
- Therapist/Output: tick 1 快照：V1 已完成装载 C1 并在 N1 空闲，C1 在车上；GLOBAL TimeTick: 1, ScoreSoFar: 0
- Notes: WorkUnits=3 小于 HandlingRate=4，作业在单 tick 内完成

## Triggers

- 需要从当前状态推进到下一 tick
- 需要生成 GLOBAL/NODES/EDGES/VEHICLES 等快照

## Examples

### Example 1

Input:

  tick 0，控制器选择 V1: START_LOADING([C1])，C1 SizeUnits=3，TRUCK HandlingRate=4

Output:

  tick 1 快照：V1 已完成装载 C1 并在 N1 空闲，C1 在车上；GLOBAL TimeTick: 1, ScoreSoFar: 0

Notes:

  WorkUnits=3 小于 HandlingRate=4，作业在单 tick 内完成
