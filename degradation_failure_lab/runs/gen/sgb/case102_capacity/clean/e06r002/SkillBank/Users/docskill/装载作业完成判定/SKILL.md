---
id: "31180147-95d5-579b-bbdb-e12964b710ae"
name: "装载作业完成判定"
description: "对 START_LOADING 发起的装载作业，按 WorkUnits=SizeUnits 与 HandlingRate 计算完成所需 tick 数，并据此更新车辆与货物状态。适用于车辆在节点开始装载货物、需要判断何时装载完成时。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "装卸作业"
  - "工作量计算"
  - "状态更新"
triggers:
  - "车辆执行 START_LOADING"
  - "需要判断货物何时装载完成"
  - "装载阶段需要更新车辆与货物状态"
examples:
  - input: "V1 在 N1 执行 START_LOADING([C1])，SizeUnits(C1)=3，HandlingRate(TRUCK)=4"
    output: "WorkUnits=3 ≤ HandlingRate=4，装载在单 tick 内完成；tick 1 时 V1 已装载 C1 并空闲于 N1"
    notes: "ScoreSoFar 仍为 0，尚无指标"
---

# 装载作业完成判定

对 START_LOADING 发起的装载作业，按 WorkUnits=SizeUnits 与 HandlingRate 计算完成所需 tick 数，并据此更新车辆与货物状态。适用于车辆在节点开始装载货物、需要判断何时装载完成时。

## Prompt

当车辆在节点执行 START_LOADING 时，按以下步骤判定装载作业完成情况：
1. 确认车辆位于节点且已发起装载，货物处于 PENDING_AT_ORIGIN 等可装载状态。
2. 计算 WorkUnits = SizeUnits(货物)。
3. 取对应车辆类型的 HandlingRate。
4. 用 WorkUnits 与 HandlingRate 推算完成所需 tick 数（若 WorkUnits ≤ HandlingRate，则单 tick 内完成）。
5. 若本 tick 内完成，更新车辆状态为已装载并空闲于当前节点，货物随车；若未完成，保留作业进行中状态。
6. 输出更新后的车辆与货物状态，供后续 tick 快照使用。

## Objective

判定装载作业是否在单 tick 内完成并更新状态
## Applicable Signals

- 车辆在节点发起 START_LOADING
- 货物处于待装载状态
- 需要推算装载完成所需 tick 数

## Contraindications

- 车辆未在节点或未发起装载
- 涉及卸载作业

## Intervention Moves

- 计算 WorkUnits = SizeUnits(货物)
- 取车辆类型对应的 HandlingRate
- 比较 WorkUnits 与 HandlingRate 判定是否单 tick 完成
- 更新车辆为已装载并空闲、货物随车

## Workflow Steps

- 确认车辆位于节点且已发起装载
- 计算 WorkUnits = SizeUnits(货物)
- 取对应车辆类型的 HandlingRate
- 推算完成所需 tick 数
- 按结果更新车辆与货物状态
- 输出更新后的状态供快照使用

## Constraints

- WorkUnits 必须等于货物 SizeUnits
- HandlingRate 必须按车辆类型取值
- 仅在装载阶段执行，不处理卸载

## Cautions

- 若 WorkUnits 超过 HandlingRate，作业需跨多个 tick，不可误判为单 tick 完成

## Output Contract

- 车辆状态更新为已装载并空闲于当前节点，货物状态相应更新（随车），并给出完成所需 tick 数。

## Example Therapist Responses

### Example 1

- Client/Input: V1 在 N1 执行 START_LOADING([C1])，SizeUnits(C1)=3，HandlingRate(TRUCK)=4
- Therapist/Output: WorkUnits=3 ≤ HandlingRate=4，装载在单 tick 内完成；tick 1 时 V1 已装载 C1 并空闲于 N1
- Notes: ScoreSoFar 仍为 0，尚无指标

## Triggers

- 车辆执行 START_LOADING
- 需要判断货物何时装载完成
- 装载阶段需要更新车辆与货物状态

## Examples

### Example 1

Input:

  V1 在 N1 执行 START_LOADING([C1])，SizeUnits(C1)=3，HandlingRate(TRUCK)=4

Output:

  WorkUnits=3 ≤ HandlingRate=4，装载在单 tick 内完成；tick 1 时 V1 已装载 C1 并空闲于 N1

Notes:

  ScoreSoFar 仍为 0，尚无指标
