---
id: "ee0a65e4-e71e-5cc4-8a43-6869f37e5d3f"
name: "事件时间窗效果应用与恢复规则"
description: "在 Incident Resolution Phase 按 StartTick/EndTick 半开区间应用 CLOSE_EDGE 或 REDUCE_CAPACITY 效果，并在事件结束后恢复边基线属性；用于处理带时间窗的道路事件对边容量或通行状态的影响。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "事件处理"
  - "时间窗"
  - "边容量"
  - "Incident Resolution Phase"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要判断某 tick 是否应施加事件效果"
  - "事件结束后需恢复边基线属性"
  - "处理 CLOSE_EDGE 或 REDUCE_CAPACITY 类型事件"
examples:
  - input: "事件 EffectType=CLOSE_EDGE，StartTick=5，EndTick=10，当前 tick t=7"
    output: "该边处于关闭状态，禁止新车辆进入，已在边车辆继续行驶"
    notes: "5 <= 7 < 10 满足活动区间"
  - input: "事件 EffectType=REDUCE_CAPACITY，CapacityMultiplier=0.5，StartTick=5，EndTick=10，当前 tick t=10"
    output: "该边恢复基线容量（除非另有活动事件）"
    notes: "t >= EndTick 触发恢复"
---

# 事件时间窗效果应用与恢复规则

在 Incident Resolution Phase 按 StartTick/EndTick 半开区间应用 CLOSE_EDGE 或 REDUCE_CAPACITY 效果，并在事件结束后恢复边基线属性；用于处理带时间窗的道路事件对边容量或通行状态的影响。

## Prompt

在 Incident Resolution Phase 处理每个 tick 时：1) 读取事件的 AffectedEdgeID、StartTick、EndTick（EndTick 为排他）与 EffectType；2) 若 StartTick <= t < EndTick，则施加该事件效果（CLOSE_EDGE 禁止新车辆进入，已在边上的车辆继续行驶；REDUCE_CAPACITY 按 CapacityMultiplier 在 (0,1] 内降低容量）；3) 若 t >= EndTick，则将边恢复为基线属性，除非另有活动事件修改；4) 输出该 tick 每条受影响边的状态与容量。

## Objective

按时间窗正确应用和撤销事件对边的影响
## Applicable Signals

- 存在带 StartTick/EndTick 的事件定义
- 需要判定当前 tick 是否处于事件活动区间
- 事件已过期需恢复边基线属性

## Contraindications

- 无事件定义或事件字段缺失
- 事件缺少 EffectType 或时间窗字段

## Intervention Moves

- 按半开区间 StartTick <= t < EndTick 判定事件是否活动
- 对 CLOSE_EDGE 阻止新车辆进入但允许已在边车辆继续行驶
- 对 REDUCE_CAPACITY 按 CapacityMultiplier 调整容量
- 在 t >= EndTick 时恢复基线属性，除非被其他活动事件修改

## Workflow Steps

- 读取事件的 AffectedEdgeID、StartTick、EndTick、EffectType
- 判断当前 tick t 是否满足 StartTick <= t < EndTick
- 若活动则施加对应效果（CLOSE_EDGE 或 REDUCE_CAPACITY）
- 若 t >= EndTick 则恢复边基线属性，除非另有活动事件
- 输出该 tick 受影响边的状态与容量

## Constraints

- EndTick 为排他边界
- CapacityMultiplier 取值须在 (0,1] 内
- CLOSE_EDGE 活动期间不得有新车辆进入
- 恢复基线属性时须考虑其他活动事件的叠加影响

## Cautions

- 多个事件可能同时影响同一条边，恢复时需检查是否仍有其他活动事件

## Output Contract

- 每个 tick 的边状态与容量已按事件规则更新或恢复

## Example Therapist Responses

### Example 1

- Client/Input: 事件 EffectType=CLOSE_EDGE，StartTick=5，EndTick=10，当前 tick t=7
- Therapist/Output: 该边处于关闭状态，禁止新车辆进入，已在边车辆继续行驶
- Notes: 5 <= 7 < 10 满足活动区间

### Example 2

- Client/Input: 事件 EffectType=REDUCE_CAPACITY，CapacityMultiplier=0.5，StartTick=5，EndTick=10，当前 tick t=10
- Therapist/Output: 该边恢复基线容量（除非另有活动事件）
- Notes: t >= EndTick 触发恢复

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断某 tick 是否应施加事件效果
- 事件结束后需恢复边基线属性
- 处理 CLOSE_EDGE 或 REDUCE_CAPACITY 类型事件

## Examples

### Example 1

Input:

  事件 EffectType=CLOSE_EDGE，StartTick=5，EndTick=10，当前 tick t=7

Output:

  该边处于关闭状态，禁止新车辆进入，已在边车辆继续行驶

Notes:

  5 <= 7 < 10 满足活动区间

### Example 2

Input:

  事件 EffectType=REDUCE_CAPACITY，CapacityMultiplier=0.5，StartTick=5，EndTick=10，当前 tick t=10

Output:

  该边恢复基线容量（除非另有活动事件）

Notes:

  t >= EndTick 触发恢复
