---
id: "39e7d25f-9e64-51ec-825a-7c8a0f328095"
name: "AFN 单 tick 合法动作执行"
description: "在 AFN 离散时间仿真中推进单个 tick：依据时间与更新顺序规则，对车辆执行合法动作（移动、装卸、等待等），并处理边容量、队列与冲突，产出更新后的状态快照与动作执行记录。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "离散时间步"
  - "单步执行"
  - "状态更新"
  - "边容量"
triggers:
  - "需要推进一个 tick 并更新车辆与边状态"
  - "需要处理边容量、队列或冲突"
  - "需要按合法动作定义裁决本 tick 的车辆行为"
---

# AFN 单 tick 合法动作执行

在 AFN 离散时间仿真中推进单个 tick：依据时间与更新顺序规则，对车辆执行合法动作（移动、装卸、等待等），并处理边容量、队列与冲突，产出更新后的状态快照与动作执行记录。

## Prompt

按以下步骤推进一个 tick：
1. 读取当前状态快照（GLOBAL、NODES、EDGES、VEHICLES、CONSIGNMENTS、INCIDENTS_ACTIVE），确认 TimeTick 与 ScenarioName。
2. 依据时间与更新顺序规则确定本 tick 的处理次序。
3. 对每辆车枚举合法动作（移动、装卸、等待等），排除不合法动作。
4. 应用边容量、队列与冲突规则裁决竞争性动作，处理 CLOSED 边与占用（Occupancy 中的 RemainingTravelTime）。
5. 更新节点 PackagesAtNode/ParkingVehicles、边 Occupancy、车辆与货物状态，推进 TimeTick。
6. 输出更新后的状态快照与动作执行记录。

## Objective

在单个 tick 内正确执行合法动作并更新状态
## Applicable Signals

- 存在当前 tick 的状态快照
- 有车辆待处理动作
- 边存在占用或容量约束
- 存在活跃事件或道路关闭

## Contraindications

- 需要跨多阶段规划整体控制策略
- 缺少合法动作定义或更新顺序规则

## Intervention Moves

- 读取并校验状态快照各分区
- 按更新顺序确定处理次序
- 枚举并筛选合法动作
- 按容量/队列/冲突规则裁决
- 更新状态并推进 TimeTick

## Workflow Steps

- 读取当前状态快照并确认 TimeTick 与 ScenarioName
- 依据时间与更新顺序规则确定本 tick 处理次序
- 对每辆车枚举合法动作并排除不合法动作
- 应用边容量、队列与冲突规则裁决竞争性动作，处理 CLOSED 边与占用
- 更新节点、边、车辆与货物状态并推进 TimeTick
- 输出更新后的状态快照与动作执行记录

## Constraints

- 必须遵循时间与更新顺序规则
- 动作必须属于合法动作集合
- 边容量、队列与冲突须按规则裁决
- CLOSED 边不可通行

## Cautions

- ScoreSoFar 可能为暂定值，不应视为最终得分
- 规则冲突或未定义行为需按规则冲突处理约定处理

## Output Contract

- 更新后的 tick 状态快照（含 GLOBAL、NODES、EDGES、VEHICLES、CONSIGNMENTS、INCIDENTS_ACTIVE）与动作执行记录

## Triggers

- 需要推进一个 tick 并更新车辆与边状态
- 需要处理边容量、队列或冲突
- 需要按合法动作定义裁决本 tick 的车辆行为
