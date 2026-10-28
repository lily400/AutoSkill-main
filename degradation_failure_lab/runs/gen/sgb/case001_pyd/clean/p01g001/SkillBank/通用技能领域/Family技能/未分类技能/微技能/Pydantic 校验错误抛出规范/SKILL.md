---
id: "bfefe7d8-3421-5458-9efa-0bc78f7f439d"
name: "Pydantic 校验错误抛出规范"
description: "在校验器内检测到非法输入时，通过抛出 ValueError 或 PydanticCustomError 报告校验失败，使 Pydantic 将其包装为结构化 ValidationError 并附带错误类型与输入信息。适用于需要拒绝非法输入或自定义错误消息/错误类型的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validation"
  - "error-reporting"
  - "validator"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "校验器检测到非法输入需要拒绝"
  - "需要自定义错误消息或错误类型"
  - "希望校验失败以结构化 ValidationError 形式暴露给调用方"
examples:
  - input: "校验器检测到输入无法解析为整数"
    output: "抛出 ValueError，Pydantic 包装为 ValidationError，错误类型为 int_parsing 并附带输入值"
    notes: "错误消息应说明期望类型与实际输入"
---

# Pydantic 校验错误抛出规范

在校验器内检测到非法输入时，通过抛出 ValueError 或 PydanticCustomError 报告校验失败，使 Pydantic 将其包装为结构化 ValidationError 并附带错误类型与输入信息。适用于需要拒绝非法输入或自定义错误消息/错误类型的场景。

## Prompt

当校验器判定输入非法时，不要返回布尔值或静默修正，而应抛出异常：简单场景抛出 ValueError 并给出清晰消息；需要自定义错误类型或结构化上下文时抛出 PydanticCustomError。抛出后由 Pydantic 统一包装为 ValidationError，调用方据此获得结构化错误信息。仅用于校验类失败，系统级异常不应以此方式报告。

## Objective

在校验失败时产生结构化、可读的校验错误
## Applicable Signals

- 校验器内已判定输入不满足约束
- 需要向调用方提供明确的错误类型与输入值
- 默认错误消息不足以表达业务含义

## Contraindications

- 校验通过、无需报错时不应抛出异常
- 需要抛出非校验类异常（如系统错误、IO 错误）时不应使用本技能

## Intervention Moves

- 在非法分支抛出 ValueError 并附清晰消息
- 需要自定义错误类型时抛出 PydanticCustomError
- 依赖 Pydantic 将异常包装为 ValidationError，不自行构造错误对象

## Workflow Steps

- 在校验器逻辑中判断输入是否满足约束
- 若不满足，选择 ValueError（简单消息）或 PydanticCustomError（自定义类型/上下文）
- 抛出异常并给出可读的错误消息
- 由 Pydantic 包装为 ValidationError 返回给调用方

## Constraints

- 仅在校验失败分支抛出异常
- 错误消息应清晰可读，便于定位问题
- 不自行构造或吞掉 ValidationError

## Cautions

- 抛出非校验类异常不会被包装为 ValidationError，可能破坏调用方错误处理
- 错误消息应避免泄露敏感输入细节

## Output Contract

- 抛出 ValueError 或 PydanticCustomError，并被 Pydantic 包装为结构化 ValidationError，包含错误类型与输入信息

## Example Therapist Responses

### Example 1

- Client/Input: 校验器检测到输入无法解析为整数
- Therapist/Output: 抛出 ValueError，Pydantic 包装为 ValidationError，错误类型为 int_parsing 并附带输入值
- Notes: 错误消息应说明期望类型与实际输入

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 校验器检测到非法输入需要拒绝
- 需要自定义错误消息或错误类型
- 希望校验失败以结构化 ValidationError 形式暴露给调用方

## Examples

### Example 1

Input:

  校验器检测到输入无法解析为整数

Output:

  抛出 ValueError，Pydantic 包装为 ValidationError，错误类型为 int_parsing 并附带输入值

Notes:

  错误消息应说明期望类型与实际输入
