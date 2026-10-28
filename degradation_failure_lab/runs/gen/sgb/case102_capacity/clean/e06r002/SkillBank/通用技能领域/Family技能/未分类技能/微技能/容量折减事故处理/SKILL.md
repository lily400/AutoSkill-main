---
id: "8dc3c6d0-79a0-5680-b080-b5f2c64deb11"
name: "容量折减事故处理"
description: "当边存在激活事故且给出 CapacityMultiplier 时，按折减系数计算该边的有效容量，并据此更新排队与通行状态。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "容量折减"
  - "事故处理"
  - "排队计算"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "边存在激活事故且给出 CapacityMultiplier"
  - "需更新受影响边容量与队列"
examples:
  - input: "E9（N4 至 N9）上存在事故 I1，CapacityMultiplier = 0.5"
    output: "E9 有效容量 = 原容量 × 0.5，并据此更新 E9 的排队与通行状态"
---

# 容量折减事故处理

当边存在激活事故且给出 CapacityMultiplier 时，按折减系数计算该边的有效容量，并据此更新排队与通行状态。

## Prompt

识别受影响边上的激活事故及其 CapacityMultiplier，将原容量乘以该乘数得到有效容量，再以有效容量更新该边的排队与通行状态，最后输出折减后的有效容量及更新后的队列状态。

## Objective

按事故容量乘数计算受影响边的有效容量
## Applicable Signals

- 边存在激活事故且给出 CapacityMultiplier
- 需更新受影响边容量与队列

## Contraindications

- 无事故激活
- 事故未指定容量乘数

## Intervention Moves

- 读取受影响边上的激活事故及其 CapacityMultiplier
- 将原容量乘以 CapacityMultiplier 得到有效容量
- 以有效容量更新该边的排队与通行状态

## Workflow Steps

- 确认受影响边上存在激活事故且已给出 CapacityMultiplier
- 计算有效容量 = 原容量 × CapacityMultiplier
- 以有效容量更新该边的排队与通行状态
- 输出折减后的有效容量及更新后的队列状态

## Constraints

- 仅在事故激活且指定容量乘数时执行
- 有效容量必须基于原容量与乘数计算，不得凭空设定

## Cautions

- 事故未指定容量乘数时不应套用折减

## Output Contract

- 输出折减后的有效容量及更新后的队列状态

## Example Therapist Responses

### Example 1

- Client/Input: E9（N4 至 N9）上存在事故 I1，CapacityMultiplier = 0.5
- Therapist/Output: E9 有效容量 = 原容量 × 0.5，并据此更新 E9 的排队与通行状态

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 边存在激活事故且给出 CapacityMultiplier
- 需更新受影响边容量与队列

## Examples

### Example 1

Input:

  E9（N4 至 N9）上存在事故 I1，CapacityMultiplier = 0.5

Output:

  E9 有效容量 = 原容量 × 0.5，并据此更新 E9 的排队与通行状态
