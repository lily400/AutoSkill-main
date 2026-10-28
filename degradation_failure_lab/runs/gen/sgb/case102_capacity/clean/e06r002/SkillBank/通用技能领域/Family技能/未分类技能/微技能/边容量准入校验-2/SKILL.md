---
id: "2f3c4ace-1ca8-53a7-8b8b-3cd72ddc0fee"
name: "边容量准入校验"
description: "在移动执行阶段判断车辆能否进入目标边：检查边状态为 OPEN、进入后占用不超过 LaneCount×CapacityPerLane、且下游节点信号/交叉口规则允许；用于逐 tick 的车辆移动执行。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "移动执行"
  - "容量校验"
  - "准入判定"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆请求 ENTER_EDGE"
  - "需要判断目标边是否可容纳新增占用"
  - "移动执行阶段需要校验边准入"
examples:
  - input: "车辆请求 ENTER_EDGE，目标边 Status=OPEN，进入后占用未超 MaxVehicles，下游信号允许"
    output: "批准进入"
  - input: "车辆请求 ENTER_EDGE，但进入后占用将超过 MaxVehicles"
    output: "拒绝进入，车辆在当前节点执行 WAIT"
---

# 边容量准入校验

在移动执行阶段判断车辆能否进入目标边：检查边状态为 OPEN、进入后占用不超过 LaneCount×CapacityPerLane、且下游节点信号/交叉口规则允许；用于逐 tick 的车辆移动执行。

## Prompt

对每个 ENTER_EDGE 请求执行准入判定：
1. 计算目标边的 MaxVehicles = LaneCount(edge) × CapacityPerLane(edge)。
2. 检查边 Status 是否为 OPEN；非 OPEN 则拒绝。
3. 检查批准进入后占用是否不超过 MaxVehicles；超限则拒绝。
4. 检查下游节点的信号或交叉口规则是否允许进入；不允许则拒绝。
5. 三项条件全部满足才批准进入；任一条件失败则拒绝，车辆改为在当前节点执行 WAIT。
输出每个请求的批准/拒绝判定及失败原因。

## Objective

按容量与信号约束决定 ENTER_EDGE 是否被批准
## Applicable Signals

- 车辆请求 ENTER_EDGE
- 需要判断目标边是否可容纳新增占用

## Contraindications

- 边状态未知或未初始化
- 处于非移动执行阶段

## Intervention Moves

- 计算 MaxVehicles = LaneCount × CapacityPerLane
- 校验边 Status = OPEN
- 校验进入后占用不超过 MaxVehicles
- 校验下游节点信号/交叉口规则允许进入
- 条件失败时令车辆执行 WAIT

## Workflow Steps

- 计算目标边 MaxVehicles = LaneCount(edge) × CapacityPerLane(edge)
- 检查边 Status 是否为 OPEN
- 检查批准进入后占用是否不超过 MaxVehicles
- 检查下游节点信号或交叉口规则是否允许进入
- 三项条件全部满足则批准 ENTER_EDGE，否则拒绝并令车辆在当前节点 WAIT

## Constraints

- 仅在移动执行阶段执行准入判定
- MaxVehicles 必须由 LaneCount 与 CapacityPerLane 相乘得出
- 任一条件失败即拒绝进入

## Cautions

- 边状态未知或未初始化时不应执行判定
- 拒绝进入的车辆应改为 WAIT，而非停留在未定义状态

## Output Contract

- 对每个 ENTER_EDGE 请求给出批准或拒绝的判定结果，拒绝时说明失败条件，并指示车辆执行 WAIT。

## Example Therapist Responses

### Example 1

- Client/Input: 车辆请求 ENTER_EDGE，目标边 Status=OPEN，进入后占用未超 MaxVehicles，下游信号允许
- Therapist/Output: 批准进入

### Example 2

- Client/Input: 车辆请求 ENTER_EDGE，但进入后占用将超过 MaxVehicles
- Therapist/Output: 拒绝进入，车辆在当前节点执行 WAIT

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆请求 ENTER_EDGE
- 需要判断目标边是否可容纳新增占用
- 移动执行阶段需要校验边准入

## Examples

### Example 1

Input:

  车辆请求 ENTER_EDGE，目标边 Status=OPEN，进入后占用未超 MaxVehicles，下游信号允许

Output:

  批准进入

### Example 2

Input:

  车辆请求 ENTER_EDGE，但进入后占用将超过 MaxVehicles

Output:

  拒绝进入，车辆在当前节点执行 WAIT
