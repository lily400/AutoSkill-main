---
id: "cf805263-8bb0-5ad8-b191-a11b32305e52"
name: "边最大车辆数计算"
description: "按 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge) 计算指定边的最大允许占用车辆数，作为准入校验的容量基准。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "容量计算"
  - "边容量"
  - "准入校验"
triggers:
  - "需要判断占用是否超限"
  - "需要边容量基准值"
---

# 边最大车辆数计算

按 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge) 计算指定边的最大允许占用车辆数，作为准入校验的容量基准。

## Prompt

给定一条边的 LaneCount(edge) 与 CapacityPerLane(edge)，计算 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)，输出该边的最大允许占用车辆数，作为后续准入校验的容量基准。若缺少任一参数，不要臆造数值，应报告参数缺失。

## Objective

计算指定边的最大允许占用车辆数
## Applicable Signals

- 需要判断占用是否超限
- 需要边容量基准值

## Contraindications

- 缺少车道数或每车道容量参数

## Intervention Moves

- 读取该边的 LaneCount(edge)
- 读取该边的 CapacityPerLane(edge)
- 按公式相乘得到 MaxVehicles(edge)

## Workflow Steps

- 确认目标边并获取 LaneCount(edge) 与 CapacityPerLane(edge)
- 计算 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)
- 输出 MaxVehicles(edge) 数值，供准入校验使用

## Constraints

- 必须使用公式 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)
- 缺少任一参数时不得臆造数值

## Cautions

- 该结果仅作为容量基准，不替代准入判定逻辑

## Output Contract

- 输出 MaxVehicles(edge) 数值

## Triggers

- 需要判断占用是否超限
- 需要边容量基准值
