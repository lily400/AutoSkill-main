---
id: "5ec4f759-4cce-551e-8fa3-5ad3cd48e463"
name: "自定义 Discriminator 错误信息"
description: "通过 Discriminator 构造器传入自定义错误类型、消息与上下文，使判别联合校验失败时输出更简洁可读的错误。适用于普通 Union 报错过于冗长、需要为判别失败提供清晰错误信息的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "discriminated-union"
  - "validation-error"
  - "discriminator"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "普通 Union 校验错误过于冗长"
  - "需要为判别失败提供清晰错误信息"
  - "判别联合校验失败需要定制错误输出"
examples:
  - input: "判别联合校验失败，普通 Union 报错过于冗长"
    output: "通过 Discriminator 构造器定制错误类型、消息与上下文后，ValidationError 输出简洁可读"
    notes: "需先确认字段为判别联合"
---

# 自定义 Discriminator 错误信息

通过 Discriminator 构造器传入自定义错误类型、消息与上下文，使判别联合校验失败时输出更简洁可读的错误。适用于普通 Union 报错过于冗长、需要为判别失败提供清晰错误信息的场景。

## Prompt

当判别联合校验失败且默认错误信息过于冗长时，使用 Discriminator 构造器定制错误类型、消息与上下文。先确认字段为判别联合（而非普通 Union），再定义判别函数或判别字段，并在 Discriminator 构造器中传入自定义错误规格，最后触发校验失败以确认输出简洁可读。

## Objective

定制判别联合的错误类型、消息与上下文
## Applicable Signals

- 普通 Union 校验错误过于冗长
- 需要为判别失败提供清晰错误信息

## Contraindications

- 默认错误信息已足够
- 非判别联合场景

## Intervention Moves

- 确认目标字段为判别联合而非普通 Union
- 定义判别函数或判别字段
- 在 Discriminator 构造器中传入自定义错误类型、消息与上下文
- 触发校验失败并核对错误输出是否简洁可读

## Workflow Steps

- 确认字段使用判别联合（discriminator）而非普通 Union
- 定义判别函数或判别字段以区分联合成员
- 在 Discriminator 构造器中传入自定义错误类型、消息与上下文
- 构造非法输入触发校验失败
- 核对 ValidationError 输出是否简洁可读并符合预期

## Constraints

- 仅用于判别联合场景
- 自定义错误规格需通过 Discriminator 构造器传入

## Cautions

- 若默认错误信息已足够清晰，无需定制
- 普通 Union 场景不适用本技能

## Output Contract

- 带自定义错误类型与消息的 ValidationError 输出

## Example Therapist Responses

### Example 1

- Client/Input: 判别联合校验失败，普通 Union 报错过于冗长
- Therapist/Output: 通过 Discriminator 构造器定制错误类型、消息与上下文后，ValidationError 输出简洁可读
- Notes: 需先确认字段为判别联合

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 普通 Union 校验错误过于冗长
- 需要为判别失败提供清晰错误信息
- 判别联合校验失败需要定制错误输出

## Examples

### Example 1

Input:

  判别联合校验失败，普通 Union 报错过于冗长

Output:

  通过 Discriminator 构造器定制错误类型、消息与上下文后，ValidationError 输出简洁可读

Notes:

  需先确认字段为判别联合
