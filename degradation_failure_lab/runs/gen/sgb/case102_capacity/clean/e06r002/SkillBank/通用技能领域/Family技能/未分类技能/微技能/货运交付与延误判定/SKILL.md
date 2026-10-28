---
id: "20fcdd02-8fae-5c9e-a2e7-d5e30a089d04"
name: "货运交付与延误判定"
description: "依据货运是否在目的节点完成卸载来判定交付状态，并按DueTime计算延误tick数（准时为0，否则为DeliveredTime减DueTime）。用于评估货运完成情况与服务指标。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "货运评估"
  - "延误计算"
  - "服务指标"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "货运在目的节点完成卸载"
  - "需要统计延误或服务水平"
  - "需要输出货运交付状态与延误指标"
examples:
  - input: "货运在DueTime=10时于DestinationNode卸载，DeliveredTime=10"
    output: "交付状态：已交付；延误：0 tick"
    notes: "准时交付延误为0"
  - input: "货运在DueTime=10时于DestinationNode卸载，DeliveredTime=14"
    output: "交付状态：已交付；延误：4 tick"
    notes: "延误为DeliveredTime减DueTime"
---

# 货运交付与延误判定

依据货运是否在目的节点完成卸载来判定交付状态，并按DueTime计算延误tick数（准时为0，否则为DeliveredTime减DueTime）。用于评估货运完成情况与服务指标。

## Prompt

对每个货运对象执行交付与延误判定：
1. 确认该货运是否已在DestinationNode完成卸载；未卸载则标记为未交付，不计算延误。
2. 已卸载则记录DeliveredTime（卸载完成的tick）。
3. 若DeliveredTime <= DueTime，延误为0；否则延误 = DeliveredTime - DueTime（tick）。
4. 输出每个货运的交付状态与延误tick值。
仅做指标判定，不涉及车辆动作选择或前置条件校验。

## Objective

判定货运是否交付并计算其延误tick数
## Applicable Signals

- 货运已在DestinationNode卸载
- 存在DueTime与DeliveredTime可用于比较
- 需要汇总延误或服务水平指标

## Contraindications

- 货运尚未卸载
- 需要计算车辆动作而非货运指标
- 缺少DueTime或DeliveredTime信息

## Intervention Moves

- 检查卸载节点是否为DestinationNode
- 记录DeliveredTime
- 比较DeliveredTime与DueTime并计算延误
- 输出交付状态与延误tick值

## Workflow Steps

- 确认货运是否在DestinationNode完成卸载
- 未卸载则标记未交付并跳过延误计算
- 已卸载则记录DeliveredTime
- 若DeliveredTime <= DueTime则延误为0，否则延误 = DeliveredTime - DueTime
- 输出每个货运的交付状态与延误tick值

## Constraints

- 交付判定仅以在DestinationNode卸载为准
- 延误以tick为单位
- 准时交付延误记为0而非负值

## Cautions

- 未卸载的货运不应计算延误
- 避免将车辆动作请求误当作交付完成

## Output Contract

- 每个货运的交付状态与延误tick值

## Example Therapist Responses

### Example 1

- Client/Input: 货运在DueTime=10时于DestinationNode卸载，DeliveredTime=10
- Therapist/Output: 交付状态：已交付；延误：0 tick
- Notes: 准时交付延误为0

### Example 2

- Client/Input: 货运在DueTime=10时于DestinationNode卸载，DeliveredTime=14
- Therapist/Output: 交付状态：已交付；延误：4 tick
- Notes: 延误为DeliveredTime减DueTime

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 货运在目的节点完成卸载
- 需要统计延误或服务水平
- 需要输出货运交付状态与延误指标

## Examples

### Example 1

Input:

  货运在DueTime=10时于DestinationNode卸载，DeliveredTime=10

Output:

  交付状态：已交付；延误：0 tick

Notes:

  准时交付延误为0

### Example 2

Input:

  货运在DueTime=10时于DestinationNode卸载，DeliveredTime=14

Output:

  交付状态：已交付；延误：4 tick

Notes:

  延误为DeliveredTime减DueTime
