---
id: "c653b7cb-d435-5b30-b610-bd68969d5727"
name: "装卸作业工作量推进规则"
description: "按车辆 HandlingRate 在每个 tick 递减装卸作业的 WorkUnits，并在 WorkUnits 归零或小于零时于该 tick 末完成作业并更新货物状态。用于模拟 START_LOADING/START_UNLOADING 之后的多 tick 装卸过程。"
version: "0.1.0"
tags:
  - "装卸作业"
  - "WorkUnits"
  - "HandlingRate"
  - "离散时间步"
  - "货物状态"
triggers:
  - "车辆已进入 LOADING 或 UNLOADING 状态"
  - "需要计算作业剩余 WorkUnits 或判定作业是否完成"
  - "需要确定装载或卸载完成时货物状态如何转换"
examples:
  - input: "VAN 在 tick t 开始装载，所处理货物 SizeUnits 之和为 5。"
    output: "HandlingRate=2；tick t+1 后 WorkUnits=3，tick t+2 后 WorkUnits=1，tick t+3 后 WorkUnits=-1，作业在 tick t+3 末完成，货物状态置为 ON_VEHICLE。"
    notes: "WorkUnits 小于 0 仍按完成处理。"
---

# 装卸作业工作量推进规则

按车辆 HandlingRate 在每个 tick 递减装卸作业的 WorkUnits，并在 WorkUnits 归零或小于零时于该 tick 末完成作业并更新货物状态。用于模拟 START_LOADING/START_UNLOADING 之后的多 tick 装卸过程。

## Prompt

当车辆已进入 LOADING 或 UNLOADING 状态时，按以下步骤推进装卸作业：
1. 确认作业已创建，并记录其总 WorkUnits（等于该作业所处理货物 SizeUnits 之和）。
2. 根据车辆类型确定 HandlingRate：BIKE=1、VAN=2、MINI_TRUCK=3、TRUCK=4（工作单位/tick）。
3. 在每个后续 Loading/Unloading Phase 中，将 WorkUnits 减去该车辆的 HandlingRate。
4. 当 WorkUnits 达到 0 或小于 0 时，在该 tick 末完成作业：装载作业将货物状态置为 ON_VEHICLE；卸载作业将货物状态置为 DELIVERED，或在转移节点按场景规定置为 PENDING_AT_ORIGIN。
5. 作业进行期间，车辆不得移动，也不得开始另一作业。
输出作业剩余 WorkUnits、完成 tick 以及货物新状态。

## Objective

正确推进装卸作业工作量并判定完成时点与货物状态转换
## Applicable Signals

- 车辆状态为 LOADING 或 UNLOADING
- 存在进行中的装卸作业且 WorkUnits 大于 0
- 需要判定作业完成 tick 或货物状态转换

## Contraindications

- 车辆处于移动或其他非装卸状态
- 作业尚未创建
- 需要处理车辆移动、信号或容量规则而非装卸作业推进

## Intervention Moves

- 按车辆类型查表确定 HandlingRate
- 每个 Loading/Unloading Phase 将 WorkUnits 减去 HandlingRate
- WorkUnits 小于等于 0 时在该 tick 末完成作业
- 装载完成置货物为 ON_VEHICLE
- 卸载完成置货物为 DELIVERED 或按场景在转移节点置为 PENDING_AT_ORIGIN

## Workflow Steps

- 确认作业已创建并记录总 WorkUnits（所处理货物 SizeUnits 之和）
- 根据车辆类型确定 HandlingRate：BIKE=1、VAN=2、MINI_TRUCK=3、TRUCK=4
- 在每个后续 Loading/Unloading Phase 将 WorkUnits 减去 HandlingRate
- 当 WorkUnits 达到 0 或小于 0 时，在该 tick 末完成作业
- 装载完成将货物状态置为 ON_VEHICLE；卸载完成将货物状态置为 DELIVERED，或在转移节点按场景规定置为 PENDING_AT_ORIGIN
- 作业进行期间保持车辆不可移动且不可开始新作业

## Constraints

- WorkUnits 为整数，等于该作业所处理货物 SizeUnits 之和
- HandlingRate 由车辆类型唯一确定
- 完成判定发生在 WorkUnits 小于等于 0 的那个 tick 的末尾
- 作业进行中车辆不得移动或开始另一作业

## Cautions

- WorkUnits 可能因递减而小于 0，仍按完成处理
- 卸载完成后的货物状态取决于是否为转移节点及场景规定

## Output Contract

- 作业 WorkUnits 归零（或小于零）并输出货物新状态（ON_VEHICLE 或 DELIVERED/PENDING_AT_ORIGIN），同时标明完成 tick。

## Example Therapist Responses

### Example 1

- Client/Input: VAN 在 tick t 开始装载，所处理货物 SizeUnits 之和为 5。
- Therapist/Output: HandlingRate=2；tick t+1 后 WorkUnits=3，tick t+2 后 WorkUnits=1，tick t+3 后 WorkUnits=-1，作业在 tick t+3 末完成，货物状态置为 ON_VEHICLE。
- Notes: WorkUnits 小于 0 仍按完成处理。

## Triggers

- 车辆已进入 LOADING 或 UNLOADING 状态
- 需要计算作业剩余 WorkUnits 或判定作业是否完成
- 需要确定装载或卸载完成时货物状态如何转换

## Examples

### Example 1

Input:

  VAN 在 tick t 开始装载，所处理货物 SizeUnits 之和为 5。

Output:

  HandlingRate=2；tick t+1 后 WorkUnits=3，tick t+2 后 WorkUnits=1，tick t+3 后 WorkUnits=-1，作业在 tick t+3 末完成，货物状态置为 ON_VEHICLE。

Notes:

  WorkUnits 小于 0 仍按完成处理。
