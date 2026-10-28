---
id: "bf353d26-6bae-5420-af2e-9952d66eb683"
name: "信号相位通行门控校验"
description: "在离散时间步交通仿真中，当车辆剩余行程时间归零并尝试进入受信号控制的节点时，依据当前 tick 对应相位的 GreenEdges 集合判定是否允许完成进入；若车辆所在边不在绿灯集合内，则推迟到达至后续 tick。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号相位"
  - "门控校验"
  - "离散时间步"
  - "移动执行"
triggers:
  - "车辆剩余行程时间归零并尝试到达节点"
  - "节点存在信号相位与 GreenEdges 定义"
  - "Movement Execution Phase 中处理节点进入"
examples:
  - input: "tick 4，V2 在 E2 上剩余行程时间由 1 减至 0，尝试到达 N3；tick 4 对应 Phase C，GreenEdges = {E18, E19, E7}"
    output: "E2 不在 GreenEdges 内，V2 不得在 tick 4 完成进入 N3，到达推迟至 tick 5，V2 保持在 E2 下游边界"
    notes: "tick 5 仍为 Phase C，限制继续适用"
---

# 信号相位通行门控校验

在离散时间步交通仿真中，当车辆剩余行程时间归零并尝试进入受信号控制的节点时，依据当前 tick 对应相位的 GreenEdges 集合判定是否允许完成进入；若车辆所在边不在绿灯集合内，则推迟到达至后续 tick。

## Prompt

当车辆在 Movement Execution Phase 中剩余行程时间减至 0 并尝试到达节点时，执行本校验：
1. 确认目标节点存在信号相位定义（含 GreenEdges）。
2. 计算当前 tick 对应的相位（如 t mod 周期）。
3. 检查车辆所在边是否属于该相位的 GreenEdges。
4. 若属于，允许完成进入节点的移动。
5. 若不属于，禁止完成进入，将到达推迟到后续 tick，车辆保持在所在边下游边界。
6. 输出明确的允许/推迟判定结果。

## Objective

确保车辆仅在所属边处于当前相位绿灯集合时才完成节点进入
## Applicable Signals

- 车辆剩余行程时间归零并尝试到达节点
- 节点存在信号相位与 GreenEdges 定义

## Contraindications

- 节点无信号控制
- 车辆尚未到达节点边界

## Intervention Moves

- 计算当前 tick 对应相位
- 检查车辆所在边是否在 GreenEdges 集合内
- 允许进入或推迟到达至后续 tick

## Workflow Steps

- 确认目标节点存在信号相位定义（含 GreenEdges）
- 计算当前 tick 对应的相位
- 检查车辆所在边是否属于该相位的 GreenEdges
- 若属于则允许完成进入节点的移动
- 若不属于则禁止进入并将到达推迟到后续 tick，车辆保持在所在边下游边界
- 输出允许或推迟的判定结果

## Constraints

- 仅在车辆剩余行程时间归零并尝试到达节点时执行
- 必须依据当前 tick 对应相位的 GreenEdges 判定
- 非绿灯边不得完成进入节点的移动

## Cautions

- 相位随时间循环，需正确计算 tick 对应相位
- 推迟到达的车辆在后续 tick 需重新校验

## Output Contract

- 车辆到达被允许或明确推迟到后续 tick 的判定结果

## Example Therapist Responses

### Example 1

- Client/Input: tick 4，V2 在 E2 上剩余行程时间由 1 减至 0，尝试到达 N3；tick 4 对应 Phase C，GreenEdges = {E18, E19, E7}
- Therapist/Output: E2 不在 GreenEdges 内，V2 不得在 tick 4 完成进入 N3，到达推迟至 tick 5，V2 保持在 E2 下游边界
- Notes: tick 5 仍为 Phase C，限制继续适用

## Triggers

- 车辆剩余行程时间归零并尝试到达节点
- 节点存在信号相位与 GreenEdges 定义
- Movement Execution Phase 中处理节点进入

## Examples

### Example 1

Input:

  tick 4，V2 在 E2 上剩余行程时间由 1 减至 0，尝试到达 N3；tick 4 对应 Phase C，GreenEdges = {E18, E19, E7}

Output:

  E2 不在 GreenEdges 内，V2 不得在 tick 4 完成进入 N3，到达推迟至 tick 5，V2 保持在 E2 下游边界

Notes:

  tick 5 仍为 Phase C，限制继续适用
