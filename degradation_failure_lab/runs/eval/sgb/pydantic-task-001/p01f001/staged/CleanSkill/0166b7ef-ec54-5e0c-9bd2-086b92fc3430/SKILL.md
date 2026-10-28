---
id: "0166b7ef-ec54-5e0c-9bd2-086b92fc3430"
name: "Pydantic 验证器模式选型与实现"
description: "根据校验需求选择字段验证器（annotated 或 decorator 模式）或模型验证器（before/after），并按正确签名实现，用于为 Pydantic 模型添加自定义校验逻辑时。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validator"
  - "字段校验"
  - "模型校验"
  - "模式选型"
triggers:
  - "需要为字段或整个模型添加自定义校验"
  - "不确定使用 annotated 还是 decorator 模式"
  - "需要在 before 与 after 模型验证器之间做选择"
examples:
  - input: "需要在整个模型校验完成后做跨字段一致性检查"
    output: "选择 after 模型验证器，定义为实例方法并返回校验后的实例"
    notes: "after 验证器在整体模型校验后运行"
---

# Pydantic 验证器模式选型与实现

根据校验需求选择字段验证器（annotated 或 decorator 模式）或模型验证器（before/after），并按正确签名实现，用于为 Pydantic 模型添加自定义校验逻辑时。

## Prompt

先判断校验目标是单个字段还是整个模型：字段级校验在 annotated 模式与 decorator 模式之间选型，模型级校验在 before 与 after 之间选型。选定后按对应签名实现验证器，确保 after 模型验证器为实例方法并返回校验后的实例。最后给出可运行代码并说明选型理由。

## Objective

为给定校验需求选择并实现正确的 Pydantic 验证器模式
## Applicable Signals

- 校验逻辑作用于单个字段
- 校验逻辑需要访问整个已校验模型
- 需要在初始化前后介入校验

## Contraindications

- 仅需内置字段约束即可满足
- 校验逻辑与模型定义无关

## Intervention Moves

- 区分字段级与模型级校验需求
- 字段级在 annotated 与 decorator 模式间选型
- 模型级在 before 与 after 之间选型
- 按所选模式实现验证器并校验签名

## Workflow Steps

- 明确校验目标是单字段还是整个模型
- 字段级：在 annotated 模式与 decorator 模式之间选择并实现
- 模型级：在 before 与 after 验证器之间选择并实现
- after 验证器定义为实例方法并返回校验后的实例
- 输出可运行代码并说明选型理由

## Constraints

- after 模型验证器必须返回校验后的实例
- 验证器签名需与所选模式匹配

## Cautions

- 模型级 after 验证器作为实例方法运行，属于初始化后钩子，遗漏返回值会导致校验结果丢失

## Output Contract

- 可运行的验证器代码，模式选择有明确理由

## Example Therapist Responses

### Example 1

- Client/Input: 需要在整个模型校验完成后做跨字段一致性检查
- Therapist/Output: 选择 after 模型验证器，定义为实例方法并返回校验后的实例
- Notes: after 验证器在整体模型校验后运行

## Triggers

- 需要为字段或整个模型添加自定义校验
- 不确定使用 annotated 还是 decorator 模式
- 需要在 before 与 after 模型验证器之间做选择

## Examples

### Example 1

Input:

  需要在整个模型校验完成后做跨字段一致性检查

Output:

  选择 after 模型验证器，定义为实例方法并返回校验后的实例

Notes:

  after 验证器在整体模型校验后运行
