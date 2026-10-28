---
id: "ce42f188-5a29-5be4-8bcc-43617ba9a0f2"
name: "无信号节点优先级冲突裁决"
description: "在无信号下游节点，按入边优先级排序处理车辆队列；同优先级跨入边冲突时以较小 VehicleID 先行。用于无信号交叉口的通行顺序裁决。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "无信号交叉口"
  - "优先级排序"
  - "冲突裁决"
  - "VehicleID"
triggers:
  - "下游节点为无信号节点"
  - "多入边车辆同时竞争通行"
examples:
  - input: "无信号下游节点，两条同优先级入边各有车辆竞争通行"
    output: "按 VehicleID 较小者先行裁决通行顺序"
    notes: "同优先级跨入边冲突场景"
  - input: "无信号下游节点，入边优先级不同"
    output: "高优先级入边队列先于低优先级队列处理"
    notes: "优先级排序场景"
---

# 无信号节点优先级冲突裁决

在无信号下游节点，按入边优先级排序处理车辆队列；同优先级跨入边冲突时以较小 VehicleID 先行。用于无信号交叉口的通行顺序裁决。

## Prompt

当本 tick 有车辆尝试进入无信号下游节点时，按以下顺序裁决通行：1) 按入边优先级从高到低处理各入边队列；2) 同一入边内按到达队列顺序（FIFO）处理；3) 若不同入边且优先级相同的车辆发生冲突，VehicleID 较小者先行。输出本 tick 的通行顺序裁决结果。

## Objective

按优先级与 VehicleID 裁决无信号节点的车辆通行顺序
## Applicable Signals

- 下游节点为无信号节点
- 多入边车辆同时竞争通行

## Contraindications

- 下游节点为信号化节点（应改用信号绿灯规则）
- 无冲突的单一入边场景

## Intervention Moves

- 按入边优先级从高到低处理队列
- 同一入边内按到达顺序（FIFO）处理
- 同优先级跨入边冲突时以较小 VehicleID 先行

## Workflow Steps

- 确认下游节点为无信号节点
- 按入边优先级排序各入边队列
- 逐入边按 FIFO 处理车辆
- 同优先级跨入边冲突时比较 VehicleID，较小者先行
- 输出本 tick 通行顺序裁决结果

## Constraints

- 仅适用于无信号下游节点
- 同优先级冲突裁决仅以 VehicleID 较小者先行

## Cautions

- 若下游节点为信号化节点，不应使用本裁决，应改用信号绿灯与 FIFO 规则

## Output Contract

- 本 tick 无信号节点的通行顺序裁决结果

## Example Therapist Responses

### Example 1

- Client/Input: 无信号下游节点，两条同优先级入边各有车辆竞争通行
- Therapist/Output: 按 VehicleID 较小者先行裁决通行顺序
- Notes: 同优先级跨入边冲突场景

### Example 2

- Client/Input: 无信号下游节点，入边优先级不同
- Therapist/Output: 高优先级入边队列先于低优先级队列处理
- Notes: 优先级排序场景

## Triggers

- 下游节点为无信号节点
- 多入边车辆同时竞争通行

## Examples

### Example 1

Input:

  无信号下游节点，两条同优先级入边各有车辆竞争通行

Output:

  按 VehicleID 较小者先行裁决通行顺序

Notes:

  同优先级跨入边冲突场景

### Example 2

Input:

  无信号下游节点，入边优先级不同

Output:

  高优先级入边队列先于低优先级队列处理

Notes:

  优先级排序场景
