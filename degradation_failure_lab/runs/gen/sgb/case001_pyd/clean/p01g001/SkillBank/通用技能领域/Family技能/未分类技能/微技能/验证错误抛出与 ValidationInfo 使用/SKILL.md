---
id: "9ac11db1-8466-56be-bf2b-9bed656dacd8"
name: "验证错误抛出与 ValidationInfo 使用"
description: "在 Pydantic 验证器中通过抛出验证错误报告校验失败，并使用 ValidationInfo 读取字段数据与校验上下文。适用于需要自定义错误信息或访问校验上下文的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validator"
  - "validation-error"
  - "validation-info"
  - "context"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "需要自定义校验失败信息"
  - "验证器需要访问 ValidationInfo 数据或上下文"
  - "需要在验证器中读取同模型其他字段的已校验值"
---

# 验证错误抛出与 ValidationInfo 使用

在 Pydantic 验证器中通过抛出验证错误报告校验失败，并使用 ValidationInfo 读取字段数据与校验上下文。适用于需要自定义错误信息或访问校验上下文的场景。

## Prompt

在编写或修改 Pydantic 验证器时，若需要自定义校验失败信息或访问校验上下文，按以下方式执行：
1. 判断是否需要自定义错误：若默认错误信息已足够且无需访问上下文，则不使用本技能。
2. 在验证器内检测到不满足条件时，抛出验证错误（如 ValueError 或 PydanticCustomError 等验证错误类型），并在错误信息中写明具体失败原因。
3. 若验证器需要访问同模型其他字段数据或校验上下文，在验证器签名中接收 ValidationInfo 参数，通过其 data 读取已校验字段数据、通过其 context 读取校验上下文。
4. 注意验证器执行顺序：after 验证器在整个模型校验完成后运行，定义为实例方法，且必须返回被校验的实例。
5. 确认抛出的错误信息明确、上下文读取正确。

## Objective

在验证器中正确抛出错误并读取校验信息
## Applicable Signals

- 需要自定义校验失败信息
- 验证器需要访问 ValidationInfo 数据或上下文
- 需要在验证器中读取同模型其他字段的已校验值

## Contraindications

- 默认错误信息已足够
- 无需访问校验上下文

## Intervention Moves

- 在验证器中抛出验证错误并写明失败原因
- 在验证器签名中接收 ValidationInfo 以读取 data 与 context
- after 验证器定义为实例方法并返回被校验实例

## Workflow Steps

- 判断是否需要自定义错误信息或访问校验上下文
- 在验证器中检测失败条件并抛出含明确信息的验证错误
- 如需上下文，在验证器签名中接收 ValidationInfo 并读取 data 或 context
- 确认 after 验证器为实例方法且返回被校验实例
- 核对错误信息与上下文读取结果

## Constraints

- after 验证器必须返回被校验的实例
- 错误信息应明确说明失败原因

## Cautions

- 验证器执行顺序会影响可访问的数据，需注意 after 验证器在整个模型校验完成后运行

## Output Contract

- 抛出含明确信息的验证错误，并正确读取 ValidationInfo 的 data 或 context。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要自定义校验失败信息
- 验证器需要访问 ValidationInfo 数据或上下文
- 需要在验证器中读取同模型其他字段的已校验值
