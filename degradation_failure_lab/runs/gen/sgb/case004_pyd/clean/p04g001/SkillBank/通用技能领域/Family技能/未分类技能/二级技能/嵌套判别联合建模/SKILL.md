---
id: "933c98e2-d5e4-54c4-9a7d-ec0587081593"
name: "嵌套判别联合建模"
description: "通过嵌套 Annotated 类型组合多个判别器，为需要多级判别键的联合类型建模。当单一字段判别器不足以区分联合成员、需要按层级组合判别条件时使用。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "discriminated-union"
  - "annotated"
  - "type-modeling"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
  - "kind:parent"
triggers:
  - "需要按多个字段层级区分联合成员"
  - "单一 discriminator 无法覆盖全部变体"
  - "联合成员共享部分判别键但需进一步细分"
examples:
  - input: "需要区分 pet_type 为 cat 且进一步按 color 区分黑猫/白猫，以及 pet_type 为 dog 的联合类型"
    output: "Cat = Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')]\nPet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]"
    notes: "内层按 color 判别，外层按 pet_type 判别"
  - input: "用 TypeAdapter 校验 {'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}"
    output: "BlackCat(pet_type='cat', color='black', black_name='felix')"
    notes: "嵌套判别联合可被 TypeAdapter 直接使用"
---

# 嵌套判别联合建模

通过嵌套 Annotated 类型组合多个判别器，为需要多级判别键的联合类型建模。当单一字段判别器不足以区分联合成员、需要按层级组合判别条件时使用。

## Prompt

当联合成员无法由单一判别字段唯一区分时，使用嵌套 Annotated 类型逐层组合判别器：先为内层联合定义判别器并包装为 Annotated 类型，再将该类型作为外层联合的成员，并为外层联合设置另一个判别器。最终产出一个可被 BaseModel 字段或 TypeAdapter 直接使用的联合类型。

## Objective

用嵌套 Annotated 判别联合表达多级判别键的联合类型
## Applicable Signals

- 联合成员可由单一判别字段唯一区分时不应使用本技能
- 存在多个变体需要按层级组合判别条件
- 需要为联合类型提供更简洁的校验错误信息

## Contraindications

- 联合成员可由单一判别字段唯一区分
- 仅需校验单个模型而非联合

## Intervention Moves

- 为内层联合成员定义各自的判别字段 Literal 值
- 用 Annotated[Union[...], Field(discriminator=...)] 包装内层联合
- 将内层 Annotated 类型作为外层联合成员之一
- 为外层联合设置另一个 discriminator 字段
- 用 BaseModel 字段或 TypeAdapter 验证嵌套联合类型

## Workflow Steps

- 确认联合成员需要多级判别键，单一 discriminator 不足
- 为内层联合成员定义判别字段（如 color）的 Literal 值
- 用 Annotated[Union[内层成员...], Field(discriminator='内层字段')] 定义内层联合类型
- 将内层联合类型与其他成员组合，用 Annotated[Union[...], Field(discriminator='外层字段')] 定义外层联合
- 在 BaseModel 字段中引用该联合类型，或使用 TypeAdapter 直接校验
- 验证合法输入被解析为正确的具体成员类型

## Constraints

- 每个字段只能设置一个 discriminator，多判别器需通过嵌套 Annotated 实现
- 内层与外层判别字段应各自唯一标识对应层级的变体

## Cautions

- 嵌套层级过深会增加类型复杂度与维护成本
- 判别字段缺失或取值不匹配时会触发校验错误

## Output Contract

- 可被 BaseModel 或 TypeAdapter 使用的嵌套判别联合类型定义

## Example Therapist Responses

### Example 1

- Client/Input: 需要区分 pet_type 为 cat 且进一步按 color 区分黑猫/白猫，以及 pet_type 为 dog 的联合类型
- Therapist/Output: Cat = Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')]
Pet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]
- Notes: 内层按 color 判别，外层按 pet_type 判别

### Example 2

- Client/Input: 用 TypeAdapter 校验 {'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}
- Therapist/Output: BlackCat(pet_type='cat', color='black', black_name='felix')
- Notes: 嵌套判别联合可被 TypeAdapter 直接使用

## 子技能目录
- [字符串判别器字段声明](通用技能领域/Family技能/未分类技能/微技能/字符串判别器字段声明/SKILL.md) ｜ 适用：在 Pydantic 模型定义中，为联合字段声明字符串判别器（str discriminator），使校验时按标签字段分派到对应联合成员。适用于联合成员可由单一字符串字段区分的场景，提供 Field(discriminator=...) 与 Annotated 两种声明语法。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `字符串判别器字段声明` 时，优先调用它。 线索：联合字段的成员可通过单一字符串字段区分, 需要简洁的判别器声明语法, 希望用 Field(discriminator=...) 或 Annotated 模式声明判别器, pydantic, union

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要按多个字段层级区分联合成员
- 单一 discriminator 无法覆盖全部变体
- 联合成员共享部分判别键但需进一步细分

## Examples

### Example 1

Input:

  需要区分 pet_type 为 cat 且进一步按 color 区分黑猫/白猫，以及 pet_type 为 dog 的联合类型

Output:

  Cat = Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')]
  Pet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]

Notes:

  内层按 color 判别，外层按 pet_type 判别

### Example 2

Input:

  用 TypeAdapter 校验 {'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}

Output:

  BlackCat(pet_type='cat', color='black', black_name='felix')

Notes:

  嵌套判别联合可被 TypeAdapter 直接使用
