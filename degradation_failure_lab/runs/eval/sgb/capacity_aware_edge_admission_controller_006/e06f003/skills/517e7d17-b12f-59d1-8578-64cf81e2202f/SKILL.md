---
id: "517e7d17-b12f-59d1-8578-64cf81e2202f"
name: "边最大容量计算"
description: "依据车道数与每车道容量计算边的最大车辆数上限，供准入校验引用。用于需要确定边容量阈值的仿真配置或校验环节。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "容量参数"
  - "公式计算"
  - "配置"
triggers:
  - "需要确定某条边的最大车辆数"
  - "准入校验需要容量阈值"
---

# 边最大容量计算

依据车道数与每车道容量计算边的最大车辆数上限，供准入校验引用。用于需要确定边容量阈值的仿真配置或校验环节。

## Prompt

当需要确定某条边的最大车辆数上限时，读取该边的 LaneCount(edge) 与 CapacityPerLane(edge)，按 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge) 计算并返回数值。该结果仅作为静态容量阈值，供准入校验（如判断进入后占用是否超过上限）引用，不替代执行期的准入判定逻辑。

## Objective

提供边最大容量的计算公式与参数依赖
## Applicable Signals

- 需要确定某条边的最大车辆数
- 准入校验需要容量阈值

## Contraindications

- 车道数或每车道容量未定义时不应计算
- 不应将本计算当作执行期准入判定逻辑

## Intervention Moves

- 读取该边的 LaneCount(edge)
- 读取该边的 CapacityPerLane(edge)
- 按公式相乘得到 MaxVehicles(edge)

## Workflow Steps

- 确认目标边及其 LaneCount(edge) 与 CapacityPerLane(edge) 均已定义
- 计算 MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)
- 返回 MaxVehicles(edge) 数值，供准入校验引用

## Constraints

- 计算依赖 LaneCount(edge) 与 CapacityPerLane(edge) 两个参数
- 结果仅作为静态容量阈值使用

## Cautions

- 若参数缺失或未定义，应停止计算并说明缺失项，而非臆造数值

## Output Contract

- 得到 MaxVehicles(edge) 数值

## Triggers

- 需要确定某条边的最大车辆数
- 准入校验需要容量阈值
