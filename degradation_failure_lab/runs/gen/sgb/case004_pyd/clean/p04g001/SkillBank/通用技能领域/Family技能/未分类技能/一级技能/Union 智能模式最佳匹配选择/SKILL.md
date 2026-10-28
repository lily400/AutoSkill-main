---
id: "437b622a-24b1-5afd-9dbd-23b939ad5556"
name: "Union 智能模式最佳匹配选择"
description: "在 Pydantic 校验 Union 类型时，依据有效字段设置数量与匹配精确度两项指标，判断输入应归属哪个候选成员类型。适用于需要解释或预测智能模式下成员选择结果的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "smart_mode"
  - "type_resolution"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "校验 Union 类型且存在多个候选成员"
  - "需要解释或预测智能模式下的成员选择结果"
---

# Union 智能模式最佳匹配选择

在 Pydantic 校验 Union 类型时，依据有效字段设置数量与匹配精确度两项指标，判断输入应归属哪个候选成员类型。适用于需要解释或预测智能模式下成员选择结果的场景。

## Prompt

当需要判断 Union 输入在智能模式下匹配到哪个成员时：1) 确认当前为智能模式而非从左到右模式；2) 对每个候选成员评估有效字段设置数量（适用于模型、dataclass、typed dict）；3) 评估匹配精确度（适用于所有类型）；4) 综合两项指标确定最佳匹配成员；5) 说明所选成员及依据。若输入与所有成员均不匹配，则不属于本技能范围，应转入错误处理。

## Objective

依据有效字段数与匹配精确度两项指标确定 Union 的最佳成员匹配
## Applicable Signals

- Union 校验存在多个候选成员
- 需要解释智能模式成员选择结果

## Contraindications

- 使用从左到右模式而非智能模式
- 输入与所有成员均不匹配需要报错处理

## Intervention Moves

- 确认处于智能模式
- 统计各候选成员的有效字段设置数量
- 评估各候选成员的匹配精确度
- 综合两项指标选出最佳匹配成员

## Workflow Steps

- 确认当前为智能模式
- 对每个候选成员评估有效字段设置数量（模型、dataclass、typed dict）
- 对每个候选成员评估匹配精确度（所有类型）
- 综合两项指标确定最佳匹配成员
- 说明所选成员及依据

## Constraints

- 仅在智能模式下适用
- 有效字段数量指标仅对模型、dataclass、typed dict 有意义
- 匹配精确度指标适用于所有类型

## Cautions

- 若输入与所有成员均不匹配，应转入 Union 校验错误处理而非本技能

## Output Contract

- 确定并说明 Union 输入匹配到的具体成员类型及依据

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 校验 Union 类型且存在多个候选成员
- 需要解释或预测智能模式下的成员选择结果
