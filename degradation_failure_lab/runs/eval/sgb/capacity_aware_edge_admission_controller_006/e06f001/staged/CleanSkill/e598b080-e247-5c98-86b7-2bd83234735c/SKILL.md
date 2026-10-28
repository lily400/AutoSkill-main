---
id: "e598b080-e247-5c98-86b7-2bd83234735c"
name: "优先级加权迟到惩罚计算"
description: "按货物优先级（LOW/STANDARD/HIGH/CRITICAL）映射每 tick 迟到惩罚权重（0.5/1.0/2.0/4.0），用于计算单件或汇总的迟到惩罚值或纳入服务评分。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "服务等级"
  - "迟到惩罚"
  - "优先级"
  - "加权计算"
triggers:
  - "需计算迟到惩罚或服务评分"
  - "存在不同优先级的货物"
  - "需要评估配送时效延误代价"
examples:
  - input: "一件 HIGH 优先级货物迟到 3 tick"
    output: "惩罚 = 3 × 2.0 = 6.0"
    notes: "HIGH 权重为 2.0"
---

# 优先级加权迟到惩罚计算

按货物优先级（LOW/STANDARD/HIGH/CRITICAL）映射每 tick 迟到惩罚权重（0.5/1.0/2.0/4.0），用于计算单件或汇总的迟到惩罚值或纳入服务评分。

## Prompt

根据每件货物的优先级选择对应的每 tick 迟到惩罚权重：LOW=0.5、STANDARD=1.0、HIGH=2.0、CRITICAL=4.0。对每件迟到货物，用其迟到 tick 数乘以对应权重得到惩罚值；如需总惩罚，将各货物惩罚值求和并注明所用权重映射。仅在有迟到信息和优先级信息时执行；缺少任一信息时不要臆造权重或迟到量。

## Objective

按优先级正确计算迟到惩罚
## Applicable Signals

- 货物带有 LOW/STANDARD/HIGH/CRITICAL 优先级标签
- 存在迟到 tick 数或可推导的迟到量
- 需要输出惩罚值或纳入服务评分

## Contraindications

- 无迟到信息
- 无优先级信息
- 优先级不在 LOW/STANDARD/HIGH/CRITICAL 范围内

## Intervention Moves

- 读取每件货物的优先级
- 按映射表选取每 tick 惩罚权重
- 用迟到 tick 数乘以权重得到单件惩罚
- 按需汇总为总惩罚

## Workflow Steps

- 确认每件货物优先级属于 LOW/STANDARD/HIGH/CRITICAL。
- 按映射选取权重：LOW=0.5、STANDARD=1.0、HIGH=2.0、CRITICAL=4.0。
- 计算单件惩罚 = 迟到 tick 数 × 权重。
- 如需总惩罚，将各件惩罚求和并标注所用权重。

## Constraints

- 权重必须严格按优先级映射，不得自行调整
- 仅对迟到货物计惩罚
- 缺少迟到或优先级信息时不得推断

## Cautions

- 不同优先级混载时需逐件分别计算，不可统一使用单一权重

## Output Contract

- 按优先级加权的迟到惩罚值（单件或汇总），并注明所用权重映射。

## Example Therapist Responses

### Example 1

- Client/Input: 一件 HIGH 优先级货物迟到 3 tick
- Therapist/Output: 惩罚 = 3 × 2.0 = 6.0
- Notes: HIGH 权重为 2.0

## Triggers

- 需计算迟到惩罚或服务评分
- 存在不同优先级的货物
- 需要评估配送时效延误代价

## Examples

### Example 1

Input:

  一件 HIGH 优先级货物迟到 3 tick

Output:

  惩罚 = 3 × 2.0 = 6.0

Notes:

  HIGH 权重为 2.0
