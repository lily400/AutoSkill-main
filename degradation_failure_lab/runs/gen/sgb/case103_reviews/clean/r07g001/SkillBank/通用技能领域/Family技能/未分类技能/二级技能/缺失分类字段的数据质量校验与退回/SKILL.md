---
id: "c0e659dc-db67-530f-87dc-425fd05b00be"
name: "缺失分类字段的数据质量校验与退回"
description: "当处理后的评论数据缺少必需分类字段（如 brand、competitor_or_nike）时，阻断后续处理并要求源系统提供修正输入，禁止从无关字段推断分类值。用于数据预处理阶段的数据质量守门。"
version: "0.1.0"
tags:
  - "数据质量"
  - "输入校验"
  - "退回"
  - "分类字段"
  - "守门规则"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "处理后的评论缺少必需分类列"
  - "解析器警告某字段映射缺失"
  - "分类字段不完整或为空"
examples:
  - input: "解析器警告：competitor_or_nike 映射缺失，晨间运行数据中该列可能缺失。"
    output: "阻断处理：competitor_or_nike 字段缺失，已停止下游计数，请源系统提供含该列的修正输入。"
    notes: "不得从 brand 文本或其他字段推断该分类值"
---

# 缺失分类字段的数据质量校验与退回

当处理后的评论数据缺少必需分类字段（如 brand、competitor_or_nike）时，阻断后续处理并要求源系统提供修正输入，禁止从无关字段推断分类值。用于数据预处理阶段的数据质量守门。

## Prompt

在执行下游计数或匹配前，先校验处理后的评论数据是否包含全部必需分类字段。若发现必需分类字段缺失或不完整，立即停止处理，不得从无关字段推断分类值，并向源系统发起修正输入请求，同时给出明确的阻断说明。

## Objective

防止使用不完整或推断出的分类字段产出下游计数结果
## Applicable Signals

- 处理后的评论缺少必需分类列
- 解析器警告某字段映射缺失
- 分类字段不完整或为空

## Contraindications

- 所有必需分类字段完整且有效
- 缺失字段可从同一记录的其他字段合法推导

## Intervention Moves

- 校验必需分类字段是否齐全
- 发现缺失时阻断后续处理
- 禁止从无关字段推断分类值
- 向源系统发起修正输入请求
- 输出明确的阻断说明

## Workflow Steps

- 检查处理后的评论数据是否包含全部必需分类字段（如 brand、competitor_or_nike）
- 若字段完整有效，放行至下游处理
- 若字段缺失或不完整，停止处理，不得从无关字段推断分类值
- 向源系统发起修正输入请求
- 输出明确的阻断说明，说明缺失字段与所需修正

## Constraints

- 不得在分类字段不完整时继续处理
- 不得从无关字段推断分类值
- 必需列缺失时必须请求源系统提供修正输入

## Cautions

- 阻断说明需清晰指出缺失字段，便于快速补救
- 在源系统修正前不得产出下游计数结果

## Output Contract

- 明确的阻断说明与向源系统发起的修正输入请求

## Example Therapist Responses

### Example 1

- Client/Input: 解析器警告：competitor_or_nike 映射缺失，晨间运行数据中该列可能缺失。
- Therapist/Output: 阻断处理：competitor_or_nike 字段缺失，已停止下游计数，请源系统提供含该列的修正输入。
- Notes: 不得从 brand 文本或其他字段推断该分类值

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 处理后的评论缺少必需分类列
- 解析器警告某字段映射缺失
- 分类字段不完整或为空

## Examples

### Example 1

Input:

  解析器警告：competitor_or_nike 映射缺失，晨间运行数据中该列可能缺失。

Output:

  阻断处理：competitor_or_nike 字段缺失，已停止下游计数，请源系统提供含该列的修正输入。

Notes:

  不得从 brand 文本或其他字段推断该分类值
