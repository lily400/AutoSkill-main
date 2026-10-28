---
id: "6dc410d7-38f2-5336-b043-b10575df5d21"
name: "事件生命周期与容量影响应用"
description: "在每 tick 的事件解析阶段，依据 StartTick/EndTick 判断事件是否生效，并对受影响边应用 CLOSE_EDGE 或 REDUCE_CAPACITY 效果；事件结束后恢复基线属性。用于需要判断某 tick 是否有事件生效或需要应用/撤销边容量与关闭效果时。"
version: "0.1.0"
tags:
  - "事件处理"
  - "容量影响"
  - "边状态更新"
  - "事件解析阶段"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要判断某 tick 是否有事件生效"
  - "需要应用或撤销边容量/关闭效果"
  - "进入事件解析阶段处理事件生命周期"
examples:
  - input: "tick t 满足 StartTick <= t < EndTick，EffectType=CLOSE_EDGE"
    output: "该边关闭：已在边上的车辆继续行驶，禁止新车辆进入；记录该事件本 tick 生效"
  - input: "tick t 满足 t >= EndTick，且无其他生效事件作用于该边"
    output: "该边恢复基线属性；记录该事件本 tick 失效"
---

# 事件生命周期与容量影响应用

在每 tick 的事件解析阶段，依据 StartTick/EndTick 判断事件是否生效，并对受影响边应用 CLOSE_EDGE 或 REDUCE_CAPACITY 效果；事件结束后恢复基线属性。用于需要判断某 tick 是否有事件生效或需要应用/撤销边容量与关闭效果时。

## Prompt

在事件解析阶段处理单个 tick：
1. 遍历所有事件定义，读取 IncidentID、AffectedEdgeID、StartTick、EndTick（EndTick 为排他）、EffectType 与 CapacityMultiplier。
2. 判定生效条件：若 StartTick <= t < EndTick，则该事件在本 tick 生效；若 t >= EndTick，则该事件失效。
3. 对生效事件按 EffectType 应用效果：CLOSE_EDGE 时边关闭，已在边上的车辆继续正常行驶，但禁止新车辆进入；REDUCE_CAPACITY 时按 CapacityMultiplier（取值 (0,1]）缩减边容量。
4. 对失效事件，将边恢复为基线属性，除非该边仍被另一个生效事件修改。
5. 输出更新后的边状态及每个事件在本 tick 的生效/失效记录。

## Objective

按 tick 正确应用和撤销事件对边状态/容量的影响
## Applicable Signals

- 存在带 StartTick/EndTick 的事件定义
- 需要判定事件在 tick t 是否生效
- 需要应用 CLOSE_EDGE 或 REDUCE_CAPACITY 效果

## Contraindications

- 无事件定义或事件已全部过期
- 需要处理车辆路径选择而非边状态

## Intervention Moves

- 按 StartTick <= t < EndTick 判定事件生效
- 对 CLOSE_EDGE 禁止新车辆进入但允许已在边上的车辆继续行驶
- 对 REDUCE_CAPACITY 按 CapacityMultiplier 缩减容量
- 事件失效后恢复基线属性，除非被其他生效事件修改

## Workflow Steps

- 读取事件定义字段（IncidentID、AffectedEdgeID、StartTick、EndTick、EffectType、CapacityMultiplier）
- 按 StartTick <= t < EndTick 判定本 tick 生效事件
- 对生效事件应用 CLOSE_EDGE 或 REDUCE_CAPACITY 效果
- 对 t >= EndTick 的事件恢复边基线属性（除非被其他生效事件修改）
- 输出更新后的边状态与事件生效/失效记录

## Constraints

- EndTick 为排他边界
- CapacityMultiplier 取值在 (0,1] 区间
- CLOSE_EDGE 生效期间禁止新车辆进入，已在边上的车辆继续正常行驶
- 恢复基线属性时需检查是否仍有其他生效事件修改该边

## Cautions

- 同一 tick 可能有多个事件作用于同一边，需按生效事件综合确定最终状态
- 事件失效不等于无条件恢复基线，需排除其他生效事件的影响

## Output Contract

- 更新后的边状态（关闭或容量乘数）及事件生效/失效记录

## Example Therapist Responses

### Example 1

- Client/Input: tick t 满足 StartTick <= t < EndTick，EffectType=CLOSE_EDGE
- Therapist/Output: 该边关闭：已在边上的车辆继续行驶，禁止新车辆进入；记录该事件本 tick 生效

### Example 2

- Client/Input: tick t 满足 t >= EndTick，且无其他生效事件作用于该边
- Therapist/Output: 该边恢复基线属性；记录该事件本 tick 失效

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断某 tick 是否有事件生效
- 需要应用或撤销边容量/关闭效果
- 进入事件解析阶段处理事件生命周期

## Examples

### Example 1

Input:

  tick t 满足 StartTick <= t < EndTick，EffectType=CLOSE_EDGE

Output:

  该边关闭：已在边上的车辆继续行驶，禁止新车辆进入；记录该事件本 tick 生效

### Example 2

Input:

  tick t 满足 t >= EndTick，且无其他生效事件作用于该边

Output:

  该边恢复基线属性；记录该事件本 tick 失效
