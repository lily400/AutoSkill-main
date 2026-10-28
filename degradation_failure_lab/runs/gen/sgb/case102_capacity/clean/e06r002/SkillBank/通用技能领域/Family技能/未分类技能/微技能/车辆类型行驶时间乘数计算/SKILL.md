---
id: "388f332f-588f-55a1-871d-61edd45ed0ce"
name: "车辆类型行驶时间乘数计算"
description: "依据车辆类型对应的行驶时间乘数与边基础时间，计算车辆在该边上的行驶时间，用于推进MOVING状态的剩余行驶时间。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "行驶时间"
  - "车辆类型"
  - "乘数计算"
  - "时间推进"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆进入或位于边上需计算剩余行驶时间"
  - "需要按车辆类型调整速度"
examples:
  - input: "车辆类型为TRUCK，边基础时间为10"
    output: "行驶时间 = 10 × 0.8 = 8"
    notes: "TRUCK乘数为0.8"
  - input: "车辆类型为BIKE，边基础时间为10"
    output: "行驶时间 = 10 × 1.5 = 15"
    notes: "BIKE乘数为1.5"
---

# 车辆类型行驶时间乘数计算

依据车辆类型对应的行驶时间乘数与边基础时间，计算车辆在该边上的行驶时间，用于推进MOVING状态的剩余行驶时间。

## Prompt

当需要计算某车辆在某条边上的行驶时间时：1) 确认车辆当前位于边上且需要计算行驶时间；2) 读取车辆类型（BIKE/VAN/TRUCK/MINI_TRUCK）；3) 取该类型对应的行驶时间乘数（BIKE 1.5，VAN 1.0，MINI_TRUCK 1.0，TRUCK 0.8）；4) 用边的基础时间乘以该乘数得到行驶时间；5) 输出该车辆在该边上的行驶时间数值，供MOVING状态推进使用。若车辆类型无乘数定义，停止计算并报告缺失；车辆处于节点静止状态时不适用本计算。

## Objective

按车辆类型乘数正确计算边行驶时间
## Applicable Signals

- 车辆进入或位于边上需计算剩余行驶时间
- 需要按类型调整速度

## Contraindications

- 车辆处于节点静止状态
- 无类型乘数定义时

## Intervention Moves

- 读取车辆类型
- 查表取该类型行驶时间乘数
- 以边基础时间乘以乘数得到行驶时间
- 输出行驶时间数值

## Workflow Steps

- 确认车辆当前位于边上且需要计算行驶时间
- 读取车辆类型（BIKE/VAN/TRUCK/MINI_TRUCK）
- 取对应乘数：BIKE 1.5，VAN 1.0，MINI_TRUCK 1.0，TRUCK 0.8
- 用边基础时间乘以乘数得到行驶时间
- 返回该车辆在该边上的行驶时间数值

## Constraints

- 仅使用已定义的四种车辆类型及其乘数
- 乘数取值固定：BIKE 1.5，VAN 1.0，MINI_TRUCK 1.0，TRUCK 0.8
- 仅在车辆位于边上时计算

## Cautions

- 若车辆类型无乘数定义，不得臆造乘数，应报告缺失
- 车辆处于节点静止状态时不适用本计算

## Output Contract

- 该车辆在该边上的行驶时间数值

## Example Therapist Responses

### Example 1

- Client/Input: 车辆类型为TRUCK，边基础时间为10
- Therapist/Output: 行驶时间 = 10 × 0.8 = 8
- Notes: TRUCK乘数为0.8

### Example 2

- Client/Input: 车辆类型为BIKE，边基础时间为10
- Therapist/Output: 行驶时间 = 10 × 1.5 = 15
- Notes: BIKE乘数为1.5

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆进入或位于边上需计算剩余行驶时间
- 需要按车辆类型调整速度

## Examples

### Example 1

Input:

  车辆类型为TRUCK，边基础时间为10

Output:

  行驶时间 = 10 × 0.8 = 8

Notes:

  TRUCK乘数为0.8

### Example 2

Input:

  车辆类型为BIKE，边基础时间为10

Output:

  行驶时间 = 10 × 1.5 = 15

Notes:

  BIKE乘数为1.5
