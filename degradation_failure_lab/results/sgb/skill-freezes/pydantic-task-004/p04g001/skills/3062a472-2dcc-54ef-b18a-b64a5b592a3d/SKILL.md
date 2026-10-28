---
id: "3062a472-2dcc-54ef-b18a-b64a5b592a3d"
name: "单变体联合禁用判别器校验"
description: "在定义带判别器的联合类型字段前，检查联合是否仅含单一变体；若仅含一个成员，应改用非联合类型，因为 Python 会把 Union[T] 折叠为 T，导致判别器无法生效。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "discriminated-union"
  - "前置校验"
  - "类型约束"
triggers:
  - "准备为联合字段添加判别器"
  - "联合类型仅包含一个成员"
  - "编写 Annotated[Union[...], Discriminator(...)] 或 Field(discriminator=...) 前"
examples:
  - input: "some_field: Annotated[Union[Cat], Discriminator(...)]"
    output: "拒绝添加判别器；改为 some_field: Cat 或补充其他变体后再使用判别器"
    notes: "Union[Cat] 会被 Python 折叠为 Cat"
---

# 单变体联合禁用判别器校验

在定义带判别器的联合类型字段前，检查联合是否仅含单一变体；若仅含一个成员，应改用非联合类型，因为 Python 会把 Union[T] 折叠为 T，导致判别器无法生效。

## Prompt

在编写带判别器的联合字段前执行前置校验：确认联合类型至少包含两个变体。若发现 Union[T] 这类单变体写法，停止添加 Discriminator，并改为直接使用 T 或补充其他变体。

## Objective

阻止对单变体联合使用判别器
## Applicable Signals

- 联合类型仅包含一个成员
- 计划为联合字段配置 Discriminator
- 字段声明中出现 Union[T] 形式

## Contraindications

- 联合包含两个及以上变体时无需触发此校验

## Intervention Moves

- 统计联合成员数量
- 若仅一个成员则拒绝添加判别器
- 建议改用非联合类型或补充变体

## Workflow Steps

- 识别待定义的联合字段及其成员列表
- 统计联合变体数量
- 若变体数小于 2，停止添加判别器并改用非联合类型或补充变体
- 若变体数大于等于 2，允许继续配置判别器

## Constraints

- 判别器不得用于仅含单一变体的联合
- 不得依赖 Union[T] 与 T 的区分，因为 Python 在解释时会将 Union[T] 折叠为 T

## Cautions

- 单变体联合在运行时无法与普通类型区分，判别逻辑会静默失效

## Output Contract

- 确认联合含多变体或改用非联合类型

## Example Therapist Responses

### Example 1

- Client/Input: some_field: Annotated[Union[Cat], Discriminator(...)]
- Therapist/Output: 拒绝添加判别器；改为 some_field: Cat 或补充其他变体后再使用判别器
- Notes: Union[Cat] 会被 Python 折叠为 Cat

## Triggers

- 准备为联合字段添加判别器
- 联合类型仅包含一个成员
- 编写 Annotated[Union[...], Discriminator(...)] 或 Field(discriminator=...) 前

## Examples

### Example 1

Input:

  some_field: Annotated[Union[Cat], Discriminator(...)]

Output:

  拒绝添加判别器；改为 some_field: Cat 或补充其他变体后再使用判别器

Notes:

  Union[Cat] 会被 Python 折叠为 Cat
