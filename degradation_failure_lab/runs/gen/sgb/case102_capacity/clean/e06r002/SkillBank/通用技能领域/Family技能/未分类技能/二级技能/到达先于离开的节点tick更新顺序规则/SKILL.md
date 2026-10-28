---
id: "229c44db-e7ea-5d6e-b34d-aa7c88339b4d"
name: "到达先于离开的节点tick更新顺序规则"
description: "在节点级离散tick更新中，当同一tick既有车辆到达该节点、又有车辆尝试离开该节点时，强制先处理到达再处理离开，以保证更新顺序一致。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "tick更新"
  - "顺序一致性"
  - "节点更新"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "同一tick同时存在车辆到达节点与车辆尝试离开该节点"
  - "需要确定节点级tick更新的处理顺序"
examples:
  - input: "某tick内，车辆A到达节点N，同时车辆B尝试离开节点N"
    output: "先处理车辆A的到达，再处理车辆B的离开"
    notes: "体现到达先于离开的顺序一致性"
---

# 到达先于离开的节点tick更新顺序规则

在节点级离散tick更新中，当同一tick既有车辆到达该节点、又有车辆尝试离开该节点时，强制先处理到达再处理离开，以保证更新顺序一致。

## Prompt

在执行节点级tick更新时，先检查该tick是否同时存在到达事件与离开事件。若两者同时存在，必须先处理所有到达该节点的车辆，再处理尝试离开该节点的车辆；不得颠倒顺序。若该tick不存在到达或不存在离开事件，则本规则不适用，按常规更新流程处理。

## Objective

保证同tick到达与离开的处理顺序一致
## Applicable Signals

- 同一tick同时存在到达与离开事件

## Contraindications

- 该tick无到达或离开事件

## Intervention Moves

- 识别该tick的到达事件与离开事件
- 先处理到达该节点的车辆
- 再处理尝试离开该节点的车辆

## Workflow Steps

- 判断当前tick是否同时存在到达事件与离开事件
- 若同时存在，先处理所有到达该节点的车辆
- 到达处理完成后，再处理尝试离开该节点的车辆
- 若不同时存在，则不应用本规则，按常规更新流程处理

## Constraints

- 到达处理必须先于离开处理，不得颠倒
- 仅在同一tick同时存在到达与离开事件时适用

## Cautions

- 不要将本顺序规则与通行选择逻辑（如信号相位、优先级排序）混淆

## Output Contract

- 按到达先于离开执行的更新结果

## Example Therapist Responses

### Example 1

- Client/Input: 某tick内，车辆A到达节点N，同时车辆B尝试离开节点N
- Therapist/Output: 先处理车辆A的到达，再处理车辆B的离开
- Notes: 体现到达先于离开的顺序一致性

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 同一tick同时存在车辆到达节点与车辆尝试离开该节点
- 需要确定节点级tick更新的处理顺序

## Examples

### Example 1

Input:

  某tick内，车辆A到达节点N，同时车辆B尝试离开节点N

Output:

  先处理车辆A的到达，再处理车辆B的离开

Notes:

  体现到达先于离开的顺序一致性
