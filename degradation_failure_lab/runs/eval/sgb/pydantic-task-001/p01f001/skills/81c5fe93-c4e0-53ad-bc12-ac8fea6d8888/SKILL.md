---
id: "81c5fe93-c4e0-53ad-bc12-ac8fea6d8888"
name: "Pydantic 特殊类型与跳过校验参考"
description: "提供 Pydantic 中 InstanceOf 特殊类型与 SkipValidation 跳过校验的用法参考，用于需要校验字段为某类实例或临时跳过某字段校验时查阅。"
version: "0.1.0"
tags:
  - "pydantic"
  - "特殊类型"
  - "SkipValidation"
  - "InstanceOf"
  - "参考"
triggers:
  - "需要校验字段为某类实例"
  - "需要跳过某字段校验"
  - "查阅 InstanceOf 或 SkipValidation 用法"
examples:
  - input: "需要校验列表元素均为某类实例"
    output: "使用 InstanceOf[类型] 注解字段，如 fruits: list[InstanceOf[Fruit]]；传入非实例时抛出 ValidationError 并指明字段路径与类型。"
    notes: "校验失败信息包含字段路径与 is_instance_of 类型"
  - input: "需要跳过某字段校验"
    output: "使用 SkipValidation 注解该字段。"
    notes: "跳过校验会放弃该字段的校验保护"
---

# Pydantic 特殊类型与跳过校验参考

提供 Pydantic 中 InstanceOf 特殊类型与 SkipValidation 跳过校验的用法参考，用于需要校验字段为某类实例或临时跳过某字段校验时查阅。

## Prompt

当需要判断字段值是否为某类的实例，或需要临时跳过某字段的校验时，查阅本参考：
1. 若需校验字段为某类实例，使用 InstanceOf[类型] 作为字段注解，校验失败会抛出 ValidationError 并指明字段路径与类型。
2. 若需跳过某字段校验，使用 SkipValidation 注解该字段。
3. 若常规字段约束已能满足需求，则不要引入特殊类型或跳过校验。
仅提供用法参考，不执行完整校验器实现流程。

## Objective

提供特殊类型与跳过校验的用法参考
## Applicable Signals

- 字段需限定为某类实例
- 字段需临时跳过校验
- 常规字段约束不足以表达需求

## Contraindications

- 常规字段约束即可满足需求时
- 需要完整校验器实现工作流时

## Intervention Moves

- 使用 InstanceOf[类型] 注解字段以校验实例类型
- 使用 SkipValidation 注解字段以跳过校验
- 校验失败时读取 ValidationError 中的字段路径与类型信息

## Workflow Steps

- 判断需求属于实例类型校验还是跳过校验
- 选择 InstanceOf 或 SkipValidation 注解
- 应用注解并验证行为，必要时读取 ValidationError 信息

## Constraints

- 仅作为用法参考，不替代完整校验器实现
- 优先使用常规字段约束，特殊类型仅在必要时引入

## Cautions

- 跳过校验会放弃该字段的校验保护，应谨慎使用
- InstanceOf 校验失败会抛出 ValidationError，需妥善处理

## Output Contract

- 选用正确的特殊类型或跳过校验方式，并说明其适用场景与行为。

## Example Therapist Responses

### Example 1

- Client/Input: 需要校验列表元素均为某类实例
- Therapist/Output: 使用 InstanceOf[类型] 注解字段，如 fruits: list[InstanceOf[Fruit]]；传入非实例时抛出 ValidationError 并指明字段路径与类型。
- Notes: 校验失败信息包含字段路径与 is_instance_of 类型

### Example 2

- Client/Input: 需要跳过某字段校验
- Therapist/Output: 使用 SkipValidation 注解该字段。
- Notes: 跳过校验会放弃该字段的校验保护

## Triggers

- 需要校验字段为某类实例
- 需要跳过某字段校验
- 查阅 InstanceOf 或 SkipValidation 用法

## Examples

### Example 1

Input:

  需要校验列表元素均为某类实例

Output:

  使用 InstanceOf[类型] 注解字段，如 fruits: list[InstanceOf[Fruit]]；传入非实例时抛出 ValidationError 并指明字段路径与类型。

Notes:

  校验失败信息包含字段路径与 is_instance_of 类型

### Example 2

Input:

  需要跳过某字段校验

Output:

  使用 SkipValidation 注解该字段。

Notes:

  跳过校验会放弃该字段的校验保护
