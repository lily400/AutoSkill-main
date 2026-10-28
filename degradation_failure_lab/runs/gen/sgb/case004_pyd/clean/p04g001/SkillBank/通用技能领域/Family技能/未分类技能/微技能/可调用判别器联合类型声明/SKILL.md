---
id: "2b84f18e-800d-523e-a397-ef2f1358157d"
name: "可调用判别器联合类型声明"
description: "使用 Discriminator 对象配合 Field 或 Annotated 声明带判别器的联合类型字段，用于需要按判别字段路由到具体变体的模型定义。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "discriminator"
  - "字段声明"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "需要为联合字段指定可调用判别器"
  - "字段需按判别值选择具体变体"
examples:
  - input: "需要为联合字段指定可调用判别器"
    output: "some_field: Annotated[Union[...], Discriminator(...)]"
    notes: "也可使用 Field(discriminator=Discriminator(...)) 形式"
---

# 可调用判别器联合类型声明

使用 Discriminator 对象配合 Field 或 Annotated 声明带判别器的联合类型字段，用于需要按判别字段路由到具体变体的模型定义。

## Prompt

在定义模型字段时，若需要按判别值将联合类型路由到具体变体，使用可调用 Discriminator 声明判别联合字段。支持三种等价写法：Field(discriminator=Discriminator(...))、Annotated[Union[...], Discriminator(...)]、Annotated[Union[...], Field(discriminator=Discriminator(...))]。声明前确认联合至少包含两个变体，且判别逻辑可从字段值推导。

## Objective

正确声明基于可调用 Discriminator 的判别联合字段
## Applicable Signals

- 联合字段需要按判别字段路由到具体变体
- 需要为联合字段指定可调用判别器

## Contraindications

- 联合仅含单一变体（如 Union[Cat]），Python 会将其折叠为 T，无法区分
- 判别逻辑无法从字段值推导

## Intervention Moves

- 选择 Field(discriminator=Discriminator(...)) 或 Annotated 形式声明判别联合
- 确认联合包含多个变体且判别逻辑可从字段值推导

## Workflow Steps

- 确认联合至少包含两个变体，排除 Union[T] 单变体情形
- 确认判别逻辑可从字段值推导
- 选择声明形式：Field(discriminator=Discriminator(...))、Annotated[Union[...], Discriminator(...)] 或 Annotated[Union[...], Field(discriminator=Discriminator(...))]
- 写出字段声明并交由 pydantic 解析验证

## Constraints

- 判别联合不能仅含单一变体
- Union[T] 在解释时被 Python 折叠为 T，pydantic 无法区分二者

## Cautions

- 单变体联合声明会静默退化为普通类型，需在声明前检查变体数量

## Output Contract

- 可被 pydantic 解析的判别联合字段声明

## Example Therapist Responses

### Example 1

- Client/Input: 需要为联合字段指定可调用判别器
- Therapist/Output: some_field: Annotated[Union[...], Discriminator(...)]
- Notes: 也可使用 Field(discriminator=Discriminator(...)) 形式

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要为联合字段指定可调用判别器
- 字段需按判别值选择具体变体

## Examples

### Example 1

Input:

  需要为联合字段指定可调用判别器

Output:

  some_field: Annotated[Union[...], Discriminator(...)]

Notes:

  也可使用 Field(discriminator=Discriminator(...)) 形式
