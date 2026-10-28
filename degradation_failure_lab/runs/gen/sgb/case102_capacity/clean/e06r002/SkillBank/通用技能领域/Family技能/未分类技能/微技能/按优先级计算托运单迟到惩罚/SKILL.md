---
id: "d097f190-6b6f-5b0e-b989-589cb4cac21f"
name: "按优先级计算托运单迟到惩罚"
description: "在评分/结算阶段，对单张已完成且迟到的托运单，按优先级映射每 tick 迟到惩罚权重并计算该托运单的迟到惩罚值。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "服务评分"
  - "迟到惩罚"
  - "优先级权重"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要计算托运单迟到惩罚"
  - "需要按优先级区分惩罚权重"
  - "结算阶段需要单张托运单的迟到成本"
examples:
  - input: "托运单优先级 HIGH，迟到 3 tick"
    output: "迟到惩罚 = 3 × 2.0 = 6.0"
    notes: "HIGH 权重为 2.0"
  - input: "托运单优先级 LOW，迟到 2 tick"
    output: "迟到惩罚 = 2 × 0.5 = 1.0"
    notes: "LOW 权重为 0.5"
---

# 按优先级计算托运单迟到惩罚

在评分/结算阶段，对单张已完成且迟到的托运单，按优先级映射每 tick 迟到惩罚权重并计算该托运单的迟到惩罚值。

## Prompt

在评分/结算阶段，对每张已迟到的托运单：1) 读取其优先级；2) 按映射取每 tick 迟到惩罚权重（LOW=0.5，STANDARD=1.0，HIGH=2.0，CRITICAL=4.0）；3) 计算迟到 tick 数（实际完成 tick 减去应完成 tick，未迟到则为 0）；4) 惩罚值 = 迟到 tick 数 × 对应权重。仅输出单项惩罚，不计算整体网络服务分。

## Objective

按优先级权重正确计算单张托运单的迟到惩罚值
## Applicable Signals

- 托运单已完成且存在迟到 tick
- 需要按优先级映射惩罚权重
- 需要单项托运单的迟到惩罚值

## Contraindications

- 托运单未迟到（惩罚为 0，无需计算）
- 需要计算整体网络服务分而非单项惩罚

## Intervention Moves

- 读取托运单优先级
- 按优先级映射每 tick 惩罚权重
- 计算迟到 tick 数
- 以迟到 tick 数乘以权重得到惩罚值

## Workflow Steps

- 确认托运单已完成并确定迟到 tick 数
- 读取托运单优先级
- 按映射取权重：LOW=0.5，STANDARD=1.0，HIGH=2.0，CRITICAL=4.0
- 惩罚值 = 迟到 tick 数 × 权重
- 输出该托运单的迟到惩罚值

## Constraints

- 权重必须严格按优先级映射，不得混用
- 仅计算单项惩罚，不汇总为整体服务分

## Cautions

- 迟到 tick 数为 0 时惩罚应为 0
- 优先级取值须为 LOW/STANDARD/HIGH/CRITICAL 之一

## Output Contract

- 每张托运单的迟到惩罚值（迟到 tick 数 × 对应优先级权重）

## Example Therapist Responses

### Example 1

- Client/Input: 托运单优先级 HIGH，迟到 3 tick
- Therapist/Output: 迟到惩罚 = 3 × 2.0 = 6.0
- Notes: HIGH 权重为 2.0

### Example 2

- Client/Input: 托运单优先级 LOW，迟到 2 tick
- Therapist/Output: 迟到惩罚 = 2 × 0.5 = 1.0
- Notes: LOW 权重为 0.5

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要计算托运单迟到惩罚
- 需要按优先级区分惩罚权重
- 结算阶段需要单张托运单的迟到成本

## Examples

### Example 1

Input:

  托运单优先级 HIGH，迟到 3 tick

Output:

  迟到惩罚 = 3 × 2.0 = 6.0

Notes:

  HIGH 权重为 2.0

### Example 2

Input:

  托运单优先级 LOW，迟到 2 tick

Output:

  迟到惩罚 = 2 × 0.5 = 1.0

Notes:

  LOW 权重为 0.5
