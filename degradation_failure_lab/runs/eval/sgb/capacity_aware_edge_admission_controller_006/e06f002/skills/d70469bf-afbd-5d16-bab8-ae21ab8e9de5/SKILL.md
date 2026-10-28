---
id: "d70469bf-afbd-5d16-bab8-ae21ab8e9de5"
name: "装卸作业逐tick推进与完成判定"
description: "当车辆已进入 LOADING 或 UNLOADING 状态后，按车辆 HandlingRate 在每个 Loading/Unloading Phase 逐 tick 递减作业 WorkUnits，并在 WorkUnits 小于等于 0 时于该 tick 末完成作业并更新货物状态。"
version: "0.1.0"
tags:
  - "装卸作业"
  - "WorkUnits"
  - "HandlingRate"
  - "逐tick推进"
  - "货物状态转换"
  - "Loading/Unloading Phase"
triggers:
  - "车辆已进入 LOADING 或 UNLOADING 状态"
  - "需要计算作业剩余 WorkUnits 或完成时点"
  - "需要判定装载/卸载完成后的货物状态转换"
examples:
  - input: "VAN 在 tick t 开始装载，所处理货物 SizeUnits 之和为 5，HandlingRate=2。"
    output: "tick t+1 后 WorkUnits=3，tick t+2 后 WorkUnits=1，tick t+3 后 WorkUnits=-1，于 tick t+3 末完成装载，货物状态置为 ON_VEHICLE。"
    notes: "WorkUnits 递减至小于零仍按完成处理。"
  - input: "TRUCK 在转运节点开始卸载，作业 WorkUnits=4，HandlingRate=4。"
    output: "该 tick 的 Loading/Unloading Phase 后 WorkUnits=0，于该 tick 末完成卸载，货物状态按场景规定置为 DELIVERED 或 PENDING_AT_ORIGIN。"
    notes: "卸载完成状态取决于是否为转运节点。"
---

# 装卸作业逐tick推进与完成判定

当车辆已进入 LOADING 或 UNLOADING 状态后，按车辆 HandlingRate 在每个 Loading/Unloading Phase 逐 tick 递减作业 WorkUnits，并在 WorkUnits 小于等于 0 时于该 tick 末完成作业并更新货物状态。

## Prompt

当车辆已选择 START_LOADING 或 START_UNLOADING 并进入 LOADING/UNLOADING 状态时，按以下步骤推进装卸作业：
1. 确认作业已创建，且 WorkUnits 等于该作业所处理货物 SizeUnits 之和。
2. 确认车辆类型对应的 HandlingRate：BIKE=1、VAN=2、MINI_TRUCK=3、TRUCK=4 工作单位/tick。
3. 在每个后续 Loading/Unloading Phase，将 WorkUnits 减去该车辆的 HandlingRate。
4. 若递减后 WorkUnits 小于等于 0，则在该 tick 末完成作业：装载作业将货物状态置为 ON_VEHICLE；卸载作业按场景规定将货物状态置为 DELIVERED，或在转运节点置为 PENDING_AT_ORIGIN。
5. 作业进行期间，车辆不得移动，也不得开始另一作业。
仅处理装卸作业推进与完成判定，不处理车辆移动、信号或路径逻辑。

## Objective

正确推进装卸作业并判定完成时机与货物状态转换
## Applicable Signals

- 车辆状态为 LOADING
- 车辆状态为 UNLOADING
- 存在进行中的装卸作业且 WorkUnits 大于 0
- 需要确定作业完成 tick 及货物新状态

## Contraindications

- 车辆尚未开始装卸作业
- 需要处理车辆移动或信号逻辑
- 作业尚未创建或 WorkUnits 未初始化

## Intervention Moves

- 按车辆类型查取 HandlingRate
- 每个 Loading/Unloading Phase 将 WorkUnits 减去 HandlingRate
- WorkUnits 小于等于 0 时在该 tick 末完成作业
- 装载完成将货物状态置为 ON_VEHICLE
- 卸载完成将货物状态置为 DELIVERED 或转运节点的 PENDING_AT_ORIGIN
- 作业进行期间锁定车辆，禁止移动或开始新作业

## Workflow Steps

- 确认车辆已通过 START_LOADING 或 START_UNLOADING 进入 LOADING/UNLOADING 状态
- 确认作业 WorkUnits 等于所处理货物 SizeUnits 之和
- 按车辆类型确定 HandlingRate（BIKE=1、VAN=2、MINI_TRUCK=3、TRUCK=4）
- 在每个后续 Loading/Unloading Phase 将 WorkUnits 减去 HandlingRate
- 若 WorkUnits 小于等于 0，则在该 tick 末完成作业并更新货物状态
- 装载完成置为 ON_VEHICLE；卸载完成置为 DELIVERED 或转运节点的 PENDING_AT_ORIGIN
- 作业进行期间保持车辆不可移动且不可开始新作业

## Constraints

- WorkUnits 必须等于该作业所处理货物 SizeUnits 之和
- HandlingRate 必须按车辆类型取值：BIKE=1、VAN=2、MINI_TRUCK=3、TRUCK=4
- 完成判定条件为 WorkUnits 小于等于 0，完成时点为该 tick 末
- 作业进行期间车辆不得移动或开始另一作业

## Cautions

- WorkUnits 可能因递减而小于零，仍按小于等于 0 判定完成
- 卸载完成后的货物状态取决于是否为转运节点，需按场景规定区分 DELIVERED 与 PENDING_AT_ORIGIN
- 本规则不覆盖移动、信号或路径逻辑，遇到这些需求应转交相应规则

## Output Contract

- 作业 WorkUnits 归零或小于零，并在该 tick 末输出作业完成结果及货物新状态（装载为 ON_VEHICLE；卸载为 DELIVERED 或转运节点的 PENDING_AT_ORIGIN）。

## Example Therapist Responses

### Example 1

- Client/Input: VAN 在 tick t 开始装载，所处理货物 SizeUnits 之和为 5，HandlingRate=2。
- Therapist/Output: tick t+1 后 WorkUnits=3，tick t+2 后 WorkUnits=1，tick t+3 后 WorkUnits=-1，于 tick t+3 末完成装载，货物状态置为 ON_VEHICLE。
- Notes: WorkUnits 递减至小于零仍按完成处理。

### Example 2

- Client/Input: TRUCK 在转运节点开始卸载，作业 WorkUnits=4，HandlingRate=4。
- Therapist/Output: 该 tick 的 Loading/Unloading Phase 后 WorkUnits=0，于该 tick 末完成卸载，货物状态按场景规定置为 DELIVERED 或 PENDING_AT_ORIGIN。
- Notes: 卸载完成状态取决于是否为转运节点。

## Triggers

- 车辆已进入 LOADING 或 UNLOADING 状态
- 需要计算作业剩余 WorkUnits 或完成时点
- 需要判定装载/卸载完成后的货物状态转换

## Examples

### Example 1

Input:

  VAN 在 tick t 开始装载，所处理货物 SizeUnits 之和为 5，HandlingRate=2。

Output:

  tick t+1 后 WorkUnits=3，tick t+2 后 WorkUnits=1，tick t+3 后 WorkUnits=-1，于 tick t+3 末完成装载，货物状态置为 ON_VEHICLE。

Notes:

  WorkUnits 递减至小于零仍按完成处理。

### Example 2

Input:

  TRUCK 在转运节点开始卸载，作业 WorkUnits=4，HandlingRate=4。

Output:

  该 tick 的 Loading/Unloading Phase 后 WorkUnits=0，于该 tick 末完成卸载，货物状态按场景规定置为 DELIVERED 或 PENDING_AT_ORIGIN。

Notes:

  卸载完成状态取决于是否为转运节点。
