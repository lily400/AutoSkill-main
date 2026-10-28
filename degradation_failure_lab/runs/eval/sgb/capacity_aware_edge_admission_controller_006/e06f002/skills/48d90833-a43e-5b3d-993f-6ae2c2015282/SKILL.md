---
id: "48d90833-a43e-5b3d-993f-6ae2c2015282"
name: "货物装载容量校验"
description: "在将货物装载到车辆前，校验货物 SizeUnits 与车辆当前载重之和不超过车辆 CapacityUnits；用于离散时间步交通仿真中的装载决策，返回装载许可或拒绝判定。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "装载决策"
  - "容量约束"
  - "安全校验"
triggers:
  - "准备将货物分配到车辆"
  - "车辆已有部分载重需追加货物"
examples:
  - input: "货物 SizeUnits=3，车辆当前载重=5，CapacityUnits=10"
    output: "许可装载（3+5=8 ≤ 10）"
    notes: "满足容量约束"
  - input: "货物 SizeUnits=4，车辆当前载重=8，CapacityUnits=10"
    output: "拒绝装载（4+8=12 > 10）"
    notes: "超出容量约束"
---

# 货物装载容量校验

在将货物装载到车辆前，校验货物 SizeUnits 与车辆当前载重之和不超过车辆 CapacityUnits；用于离散时间步交通仿真中的装载决策，返回装载许可或拒绝判定。

## Prompt

在执行装载前，确认货物状态为 PENDING_AT_ORIGIN 且车辆非 OFFLINE，读取货物的 SizeUnits 与车辆当前载重，计算二者之和并与车辆 CapacityUnits 比较。若和不超过容量，则给出装载许可；否则拒绝装载并说明超容量原因。

## Objective

防止超容量装载，保证车辆载重约束不被违反
## Applicable Signals

- 存在待装载货物与目标车辆
- 车辆当前载重已知
- 货物 SizeUnits 已知

## Contraindications

- 货物状态非 PENDING_AT_ORIGIN
- 车辆处于 OFFLINE 状态

## Intervention Moves

- 读取货物 SizeUnits
- 读取车辆当前载重与 CapacityUnits
- 计算 SizeUnits 与当前载重之和
- 比较和与 CapacityUnits 并给出许可或拒绝

## Workflow Steps

- 确认货物状态为 PENDING_AT_ORIGIN 且车辆非 OFFLINE
- 获取货物 SizeUnits 与车辆当前载重
- 计算 SizeUnits 加当前载重之和
- 若和不超过 CapacityUnits 则许可装载，否则拒绝并说明超容量

## Constraints

- SizeUnits 为整数且 >= 1
- 装载后总载重不得超过 CapacityUnits

## Cautions

- OFFLINE 车辆在显式重新激活前不移动也不处理货物，不应作为装载目标

## Output Contract

- 返回通过校验的装载许可，或拒绝装载的判定结果及超容量原因

## Example Therapist Responses

### Example 1

- Client/Input: 货物 SizeUnits=3，车辆当前载重=5，CapacityUnits=10
- Therapist/Output: 许可装载（3+5=8 ≤ 10）
- Notes: 满足容量约束

### Example 2

- Client/Input: 货物 SizeUnits=4，车辆当前载重=8，CapacityUnits=10
- Therapist/Output: 拒绝装载（4+8=12 > 10）
- Notes: 超出容量约束

## Triggers

- 准备将货物分配到车辆
- 车辆已有部分载重需追加货物

## Examples

### Example 1

Input:

  货物 SizeUnits=3，车辆当前载重=5，CapacityUnits=10

Output:

  许可装载（3+5=8 ≤ 10）

Notes:

  满足容量约束

### Example 2

Input:

  货物 SizeUnits=4，车辆当前载重=8，CapacityUnits=10

Output:

  拒绝装载（4+8=12 > 10）

Notes:

  超出容量约束
