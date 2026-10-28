---
id: "45604ce9-4ef0-5a7e-a285-7fb55f63928b"
name: "交付状态判定与延误tick计算规则"
description: "用于交通仿真结果评估：判定consignment是否已在DestinationNode卸载完成交付，并按规则计算延误tick值（按时或提前为0，否则为DeliveredTime减DueTime）。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "交付评估"
  - "延误计算"
  - "指标规则"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需判定consignment是否交付"
  - "需计算consignment延误tick"
  - "需汇总交付结果用于评估"
examples:
  - input: "consignment已在DestinationNode卸载，DeliveredTime=12，DueTime=10"
    output: "交付状态：已交付；延误：2 ticks"
    notes: "DeliveredTime大于DueTime"
  - input: "consignment已在DestinationNode卸载，DeliveredTime=8，DueTime=10"
    output: "交付状态：已交付；延误：0 ticks"
    notes: "提前交付，延误记为0"
---

# 交付状态判定与延误tick计算规则

用于交通仿真结果评估：判定consignment是否已在DestinationNode卸载完成交付，并按规则计算延误tick值（按时或提前为0，否则为DeliveredTime减DueTime）。

## Prompt

当需要评估consignment的交付状态或计算延误时使用本规则。先确认该consignment是否已在DestinationNode卸载：已卸载则标记为已交付；未卸载则视为未交付。对已交付的consignment计算延误：若DeliveredTime小于等于DueTime，延误为0；否则延误为DeliveredTime减DueTime的tick数。仅输出交付状态与延误tick值，不生成车辆动作或进行容量校验。

## Objective

统一判定交付状态并计算延误tick
## Applicable Signals

- 存在consignment的卸载记录或DeliveredTime
- 需要DueTime与DeliveredTime对比
- 需要输出交付状态或延误指标

## Contraindications

- 需生成车辆动作
- 需进行容量与冲突校验
- 需调度或路径规划

## Intervention Moves

- 检查consignment是否在DestinationNode卸载以判定交付
- 对已交付consignment比较DeliveredTime与DueTime
- 按规则计算延误tick值

## Workflow Steps

- 确认consignment是否已在DestinationNode卸载；是则标记为已交付，否则标记为未交付。
- 对已交付consignment读取DeliveredTime与DueTime。
- 若DeliveredTime小于等于DueTime，延误记为0；否则延误记为DeliveredTime减DueTime的tick数。
- 输出交付状态与延误tick值。

## Constraints

- 交付判定仅以在DestinationNode卸载为准
- 延误仅在已交付时计算
- 延误不得为负值，按时或提前统一记为0

## Cautions

- 未交付的consignment不适用延误公式，应单独标记为未交付
- 本规则不涉及车辆动作合法性或容量校验

## Output Contract

- 返回每个consignment的交付状态（已交付/未交付）及已交付者的延误tick值（0或DeliveredTime减DueTime）。

## Example Therapist Responses

### Example 1

- Client/Input: consignment已在DestinationNode卸载，DeliveredTime=12，DueTime=10
- Therapist/Output: 交付状态：已交付；延误：2 ticks
- Notes: DeliveredTime大于DueTime

### Example 2

- Client/Input: consignment已在DestinationNode卸载，DeliveredTime=8，DueTime=10
- Therapist/Output: 交付状态：已交付；延误：0 ticks
- Notes: 提前交付，延误记为0

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需判定consignment是否交付
- 需计算consignment延误tick
- 需汇总交付结果用于评估

## Examples

### Example 1

Input:

  consignment已在DestinationNode卸载，DeliveredTime=12，DueTime=10

Output:

  交付状态：已交付；延误：2 ticks

Notes:

  DeliveredTime大于DueTime

### Example 2

Input:

  consignment已在DestinationNode卸载，DeliveredTime=8，DueTime=10

Output:

  交付状态：已交付；延误：0 ticks

Notes:

  提前交付，延误记为0
