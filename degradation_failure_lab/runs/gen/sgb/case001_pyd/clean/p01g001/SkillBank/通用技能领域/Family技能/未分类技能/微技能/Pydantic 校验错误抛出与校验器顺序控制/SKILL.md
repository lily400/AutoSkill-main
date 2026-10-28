---
id: "6f6dd4cb-79fc-53a5-a853-3cf312474f21"
name: "Pydantic 校验错误抛出与校验器顺序控制"
description: "在 Pydantic 自定义校验器中按规范抛出结构化校验错误，并依据校验器执行顺序安排依赖关系，确保多校验器编排与失败处理正确。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validation"
  - "error-handling"
  - "validator-ordering"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "校验失败需返回结构化错误"
  - "多个校验器存在执行顺序依赖"
  - "需要自定义校验失败处理"
---

# Pydantic 校验错误抛出与校验器顺序控制

在 Pydantic 自定义校验器中按规范抛出结构化校验错误，并依据校验器执行顺序安排依赖关系，确保多校验器编排与失败处理正确。

## Prompt

当自定义校验失败需要返回结构化错误，或多个校验器之间存在执行顺序依赖时使用本技能。步骤：1) 确认当前校验器是否应抛出错误而非静默返回；2) 使用 Pydantic 规范方式抛出校验错误（如 ValueError/AssertionError 或 PydanticCustomError），确保错误类型与信息结构化；3) 若存在多校验器依赖，明确各校验器的执行顺序（字段校验器与模型校验器的先后、同字段多校验器的顺序），据此安排依赖；4) 验证失败时输出包含字段路径、错误类型与输入值的结构化错误。不要用于没有自定义校验失败路径的场景。

## Objective

正确抛出校验错误并控制校验器执行顺序
## Applicable Signals

- 校验失败需返回结构化错误
- 多个校验器存在执行顺序依赖

## Contraindications

- 无自定义校验失败路径时

## Intervention Moves

- 在校验器中以规范方式抛出校验错误
- 明确并安排多校验器的执行顺序以满足依赖
- 确认失败输出包含字段路径、错误类型与输入值

## Workflow Steps

- 确认校验器应抛出错误而非静默返回
- 使用规范方式抛出结构化校验错误
- 梳理字段校验器与模型校验器的执行顺序
- 按依赖关系安排多校验器顺序
- 验证失败输出为结构化错误

## Constraints

- 仅在存在自定义校验失败路径或顺序依赖时使用
- 错误信息需结构化并包含字段路径与错误类型

## Cautions

- 忽略校验器执行顺序可能导致依赖失效或错误信息不准确

## Output Contract

- 符合规范的校验错误输出（含字段路径、错误类型、输入值）与明确的校验器执行顺序

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 校验失败需返回结构化错误
- 多个校验器存在执行顺序依赖
- 需要自定义校验失败处理
