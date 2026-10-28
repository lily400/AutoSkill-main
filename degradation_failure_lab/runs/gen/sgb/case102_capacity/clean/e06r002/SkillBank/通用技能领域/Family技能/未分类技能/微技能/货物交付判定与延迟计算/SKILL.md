---
id: "3d6e58bf-08cd-5887-aebd-a1013e9ac2cf"
name: "货物交付判定与延迟计算"
description: "判定货物在目的节点卸载即视为交付，并按交付时间与截止时间计算延迟tick数；用于评估配送结果与服务水平。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "交付判定"
  - "延迟计算"
  - "服务水平"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "货物在目的节点完成卸载"
  - "需要统计延迟指标"
  - "评估配送结果或服务水平"
examples:
  - input: "货物在 DestinationNode 卸载，DeliveredTime=12，DueTime=10"
    output: "已交付，延迟=2 tick"
    notes: "超过截止时间按差值计延迟"
  - input: "货物在 DestinationNode 卸载，DeliveredTime=8，DueTime=10"
    output: "已交付，延迟=0 tick"
    notes: "未超时延迟记0"
---

# 货物交付判定与延迟计算

判定货物在目的节点卸载即视为交付，并按交付时间与截止时间计算延迟tick数；用于评估配送结果与服务水平。

## Prompt

对每件货物执行交付判定与延迟计算：
1. 确认货物已在 DestinationNode 完成卸载；未卸载的货物不判定为已交付。
2. 若已交付，取交付时间 DeliveredTime 与截止时间 DueTime。
3. 若 DeliveredTime <= DueTime，延迟记为 0。
4. 否则延迟 = DeliveredTime - DueTime（单位：tick）。
5. 输出每件货物的交付状态及延迟tick数。
缺少交付时间或截止时间数据时，不计算延迟，并标注数据缺失。

## Objective

计算每件货物的交付状态与延迟量
## Applicable Signals

- 货物已在 DestinationNode 卸载
- 存在交付时间与截止时间记录
- 需要延迟tick数用于服务水平统计

## Contraindications

- 货物尚未卸载
- 缺少交付时间或截止时间数据

## Intervention Moves

- 判定卸载于 DestinationNode 即视为交付
- 比较 DeliveredTime 与 DueTime
- 按差值计算延迟tick数，未超时记0

## Workflow Steps

- 确认货物是否在 DestinationNode 完成卸载
- 对已交付货物读取 DeliveredTime 与 DueTime
- 若 DeliveredTime <= DueTime，延迟记为0
- 否则延迟 = DeliveredTime - DueTime（tick）
- 输出每件货物的交付状态及延迟tick数

## Constraints

- 仅在目的节点卸载才视为交付
- 延迟单位为tick
- 未超时延迟必须为0而非负值

## Cautions

- 缺少交付时间或截止时间时不得臆造延迟值，应标注数据缺失

## Output Contract

- 每件货物的交付状态及延迟tick数

## Example Therapist Responses

### Example 1

- Client/Input: 货物在 DestinationNode 卸载，DeliveredTime=12，DueTime=10
- Therapist/Output: 已交付，延迟=2 tick
- Notes: 超过截止时间按差值计延迟

### Example 2

- Client/Input: 货物在 DestinationNode 卸载，DeliveredTime=8，DueTime=10
- Therapist/Output: 已交付，延迟=0 tick
- Notes: 未超时延迟记0

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 货物在目的节点完成卸载
- 需要统计延迟指标
- 评估配送结果或服务水平

## Examples

### Example 1

Input:

  货物在 DestinationNode 卸载，DeliveredTime=12，DueTime=10

Output:

  已交付，延迟=2 tick

Notes:

  超过截止时间按差值计延迟

### Example 2

Input:

  货物在 DestinationNode 卸载，DeliveredTime=8，DueTime=10

Output:

  已交付，延迟=0 tick

Notes:

  未超时延迟记0
