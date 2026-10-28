---
id: "4af0a451-fa59-56c0-b498-7eb801ffbcd2"
name: "联合校验错误聚合"
description: "当联合类型的所有成员均校验失败时，收集并返回全部成员的错误信息，而非仅返回首个错误，用于向调用方提供完整诊断反馈。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "error_aggregation"
  - "validation"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "联合类型校验失败"
  - "需要完整诊断反馈"
---

# 联合校验错误聚合

当联合类型的所有成员均校验失败时，收集并返回全部成员的错误信息，而非仅返回首个错误，用于向调用方提供完整诊断反馈。

## Prompt

在联合校验流程中，当所有成员均校验失败时，遍历各成员产生的错误并聚合为完整错误集合返回；不要只返回首个错误，也不要在已有成员成功时触发聚合。

## Objective

在所有联合成员失败时聚合返回全部错误
## Applicable Signals

- 联合所有成员均校验失败
- 需要向调用方提供完整错误集合以诊断

## Contraindications

- 已有成员校验成功
- 仅需返回单一错误

## Intervention Moves

- 确认所有联合成员均已尝试且失败
- 收集每个成员产生的错误
- 将全部错误聚合为单一结果返回

## Workflow Steps

- 确认联合校验在所有成员上均失败
- 收集各成员的错误信息
- 聚合全部错误并返回给调用方

## Constraints

- 仅在所有成员均失败时执行聚合
- 不得丢弃任何成员的错误

## Cautions

- 若存在成功成员则不应进入聚合路径

## Output Contract

- 返回包含所有成员错误的聚合错误结果

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 联合类型校验失败
- 需要完整诊断反馈
