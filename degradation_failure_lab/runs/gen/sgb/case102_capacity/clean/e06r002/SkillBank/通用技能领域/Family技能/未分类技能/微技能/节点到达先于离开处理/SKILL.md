---
id: "9cdfb7b3-4b4f-5977-ad7c-600102ad33ad"
name: "节点到达先于离开处理"
description: "在同一tick内车辆到达与离开同一节点发生冲突时，规定先处理到达、再处理离开，以保证离散时间步内事件处理顺序一致。适用于每tick状态更新时存在到达/离开冲突的节点事件排序。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "事件排序"
  - "离散时间步"
  - "节点更新"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "同一tick内既有车辆到达又有车辆尝试离开同一节点"
  - "需要确定离散时间步内节点事件的处理顺序"
---

# 节点到达先于离开处理

在同一tick内车辆到达与离开同一节点发生冲突时，规定先处理到达、再处理离开，以保证离散时间步内事件处理顺序一致。适用于每tick状态更新时存在到达/离开冲突的节点事件排序。

## Prompt

当同一tick内既有车辆到达某节点、又有车辆尝试离开该节点时，按固定优先级处理：先处理所有到达事件，再处理离开事件。仅调整事件处理顺序，不改变信号、容量或装载逻辑。若该tick内无到达或离开冲突，则无需应用此排序。

## Objective

在同一tick内按到达优先顺序处理节点事件
## Applicable Signals

- 同一tick内既有车辆到达又有车辆尝试离开同一节点

## Contraindications

- tick内无到达或离开冲突

## Intervention Moves

- 识别该tick内到达与离开冲突的节点
- 先处理该节点的所有到达事件
- 再处理该节点的离开事件

## Workflow Steps

- 识别同一tick内同时存在到达与离开的节点
- 先处理到达事件
- 再处理离开事件
- 按到达先、离开后的顺序完成该tick节点事件处理

## Constraints

- 仅规定事件处理顺序，不涉及信号或容量逻辑
- 到达必须先于离开处理

## Cautions

- 仅在存在到达/离开冲突时应用，避免对无冲突节点施加多余排序

## Output Contract

- 按到达先、离开后的顺序完成该tick节点事件处理

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 同一tick内既有车辆到达又有车辆尝试离开同一节点
- 需要确定离散时间步内节点事件的处理顺序
