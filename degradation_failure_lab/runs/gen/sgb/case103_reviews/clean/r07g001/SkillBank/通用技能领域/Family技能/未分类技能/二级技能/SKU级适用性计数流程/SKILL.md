---
id: "2b8ed26f-aff0-5dec-8eea-5b441acd1033"
name: "SKU级适用性计数流程"
description: "在目录与已处理评论均通过输入校验后，按SKU粒度统计适用性计数并产出可交付结果表；适用于需要按SKU输出计数交付物的场景。"
version: "0.1.0"
tags:
  - "计数统计"
  - "语义匹配"
  - "SKU"
  - "交付计算"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "输入目录与评论均已通过校验"
  - "需要按SKU输出适用性计数"
  - "需要产出SKU级计数交付物"
---

# SKU级适用性计数流程

在目录与已处理评论均通过输入校验后，按SKU粒度统计适用性计数并产出可交付结果表；适用于需要按SKU输出计数交付物的场景。

## Prompt

确认目录与已处理评论均已通过输入校验后，按SKU粒度对每个SKU统计适用性计数，并输出按SKU列出的计数结果表。若输入缺失或无效，明确说明阻塞状态，不要静默修补或跳过无效输入。

## Objective

产出SKU级适用性计数交付物
## Applicable Signals

- 目录与已处理评论均通过输入校验
- 任务要求按SKU粒度给出适用性计数

## Contraindications

- 输入未通过校验
- 仅需定性判断而非计数

## Intervention Moves

- 确认输入校验状态
- 按SKU逐项统计适用性计数
- 汇总为按SKU列出的结果表

## Workflow Steps

- 确认目录与已处理评论均已通过输入校验
- 按SKU粒度对每个SKU统计适用性计数
- 输出按SKU列出的适用性计数结果表
- 若输入缺失或无效，明确报告阻塞状态而非静默修补

## Constraints

- 必须使用通过校验的输入
- 不得对无效输入做静默的事后修补
- 计数须按SKU粒度产出

## Cautions

- 时间压力下不得跳过输入校验或跳过无效输入而不说明
- 不得以部分有效数据替代完整交付而不明确标注

## Output Contract

- 按SKU列出的适用性计数结果表；若输入无效则给出明确的阻塞状态说明。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 输入目录与评论均已通过校验
- 需要按SKU输出适用性计数
- 需要产出SKU级计数交付物
