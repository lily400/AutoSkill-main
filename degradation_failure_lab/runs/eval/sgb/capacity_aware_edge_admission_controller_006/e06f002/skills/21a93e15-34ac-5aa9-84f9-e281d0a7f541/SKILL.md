---
id: "21a93e15-34ac-5aa9-84f9-e281d0a7f541"
name: "装卸作业工作量推进结算"
description: "按车辆 HandlingRate 逐 tick 递减装卸作业的 WorkUnits，并在归零时结算货物状态（装载转 ON_VEHICLE，卸载转 DELIVERED 或 PENDING_AT_ORIGIN）。用于模拟车辆执行 START_LOADING/START_UNLOADING 后的多 tick 装卸过程。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "装卸结算"
  - "WorkUnits"
  - "HandlingRate"
  - "货物状态"
triggers:
  - "车辆已进入 LOADING 或 UNLOADING 状态"
  - "需要计算作业剩余 WorkUnits 或判定完成"
examples:
  - input: "VAN 车辆处于 LOADING 状态，作业 WorkUnits=5，当前 tick 执行 Loading/Unloading Phase"
    output: "WorkUnits 减至 3，作业未完成，车辆保持 LOADING 且不可移动"
    notes: "VAN HandlingRate=2"
  - input: "VAN 车辆处于 LOADING 状态，作业 WorkUnits=2，当前 tick 执行 Loading/Unloading Phase"
    output: "WorkUnits 减至 0，作业在该 tick 结束时完成，货物状态置为 ON_VEHICLE"
    notes: "归零即完成"
---

# 装卸作业工作量推进结算

按车辆 HandlingRate 逐 tick 递减装卸作业的 WorkUnits，并在归零时结算货物状态（装载转 ON_VEHICLE，卸载转 DELIVERED 或 PENDING_AT_ORIGIN）。用于模拟车辆执行 START_LOADING/START_UNLOADING 后的多 tick 装卸过程。

## Prompt

当车辆已进入 LOADING 或 UNLOADING 状态时，在每个 Loading/Unloading Phase 按该车辆类型的 HandlingRate 递减作业的 WorkUnits；当 WorkUnits 降至 0 或以下时，在该 tick 结束时完成作业并更新相关货物状态：装载作业将货物状态置为 ON_VEHICLE，卸载作业将货物状态置为 DELIVERED，或在转移节点按场景规定置为 PENDING_AT_ORIGIN。作业进行期间车辆不得移动或开始新作业。

## Objective

正确推进装卸作业工作量并在完成时更新货物状态
## Applicable Signals

- 车辆状态为 LOADING
- 车辆状态为 UNLOADING
- 存在进行中的装卸作业且 WorkUnits 大于 0

## Contraindications

- 车辆处于移动或其他非装卸状态
- 作业尚未创建

## Intervention Moves

- 读取车辆类型对应的 HandlingRate（BIKE=1, VAN=2, MINI_TRUCK=3, TRUCK=4）
- 在每个 Loading/Unloading Phase 将 WorkUnits 减去 HandlingRate
- 当 WorkUnits 降至 0 或以下时在该 tick 结束时完成作业
- 装载完成时将货物状态置为 ON_VEHICLE
- 卸载完成时将货物状态置为 DELIVERED，或在转移节点按场景规定置为 PENDING_AT_ORIGIN

## Workflow Steps

- 确认车辆状态为 LOADING 或 UNLOADING 且作业已创建
- 确定车辆类型对应的 HandlingRate
- 在当前 Loading/Unloading Phase 将作业 WorkUnits 减去 HandlingRate
- 判断 WorkUnits 是否降至 0 或以下
- 若未归零，保持作业进行中，车辆不得移动或开始新作业
- 若归零，在该 tick 结束时完成作业并按装载/卸载规则更新货物状态

## Constraints

- 作业 WorkUnits 等于该作业所处理货物 SizeUnits 之和
- HandlingRate 按车辆类型固定：BIKE=1, VAN=2, MINI_TRUCK=3, TRUCK=4
- 作业进行期间车辆不能移动或开始另一作业
- 作业完成发生在 WorkUnits 归零的那个 tick 结束时

## Cautions

- 卸载完成后的货物状态取决于是否为转移节点，需按场景规定区分 DELIVERED 与 PENDING_AT_ORIGIN

## Output Contract

- 作业 WorkUnits 归零且相关货物状态已按装载/卸载规则更新

## Example Therapist Responses

### Example 1

- Client/Input: VAN 车辆处于 LOADING 状态，作业 WorkUnits=5，当前 tick 执行 Loading/Unloading Phase
- Therapist/Output: WorkUnits 减至 3，作业未完成，车辆保持 LOADING 且不可移动
- Notes: VAN HandlingRate=2

### Example 2

- Client/Input: VAN 车辆处于 LOADING 状态，作业 WorkUnits=2，当前 tick 执行 Loading/Unloading Phase
- Therapist/Output: WorkUnits 减至 0，作业在该 tick 结束时完成，货物状态置为 ON_VEHICLE
- Notes: 归零即完成

## Triggers

- 车辆已进入 LOADING 或 UNLOADING 状态
- 需要计算作业剩余 WorkUnits 或判定完成

## Examples

### Example 1

Input:

  VAN 车辆处于 LOADING 状态，作业 WorkUnits=5，当前 tick 执行 Loading/Unloading Phase

Output:

  WorkUnits 减至 3，作业未完成，车辆保持 LOADING 且不可移动

Notes:

  VAN HandlingRate=2

### Example 2

Input:

  VAN 车辆处于 LOADING 状态，作业 WorkUnits=2，当前 tick 执行 Loading/Unloading Phase

Output:

  WorkUnits 减至 0，作业在该 tick 结束时完成，货物状态置为 ON_VEHICLE

Notes:

  归零即完成
