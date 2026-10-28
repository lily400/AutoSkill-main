---
id: "2a47f56f-2ee0-5cb8-80c8-ed41f07d7ffc"
name: "TypeAdapter 校验纯联合类型"
description: "当校验目标仅为联合类型本身、且不希望继承 BaseModel 时，使用 TypeAdapter 包装联合类型并调用 validate_python 对数据执行校验，返回解析后的具体联合成员实例。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "TypeAdapter"
  - "validation"
triggers:
  - "需要校验的数据目标仅为联合类型本身"
  - "不希望为校验而继承 BaseModel"
  - "需要对联合类型单独执行 validate_python"
examples:
  - input: "type_adapter = TypeAdapter(Pet); type_adapter.validate_python({'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'})"
    output: "BlackCat(pet_type='cat', color='black', black_name='felix')"
    notes: "Pet 为嵌套可辨识联合类型"
---

# TypeAdapter 校验纯联合类型

当校验目标仅为联合类型本身、且不希望继承 BaseModel 时，使用 TypeAdapter 包装联合类型并调用 validate_python 对数据执行校验，返回解析后的具体联合成员实例。

## Prompt

确认校验目标是一个联合类型（而非完整模型字段）。用 TypeAdapter 包装该联合类型构造适配器，调用 validate_python 传入待校验数据，返回解析后的具体联合成员实例。若联合为可辨识联合，确保判别字段存在且取值匹配。

## Objective

用 TypeAdapter 对纯联合类型执行校验
## Applicable Signals

- 校验目标仅为联合类型本身
- 不希望继承 BaseModel
- 已有联合类型定义但无外层模型承载

## Contraindications

- 需要完整模型字段校验
- 已有 BaseModel 承载该字段

## Intervention Moves

- 用 TypeAdapter 包装联合类型构造适配器
- 调用 validate_python 传入待校验数据
- 返回解析后的具体联合成员实例

## Workflow Steps

- 确认校验目标为联合类型本身而非完整模型
- 用 TypeAdapter(联合类型) 构造适配器
- 调用 type_adapter.validate_python(数据)
- 返回解析后的具体联合成员实例

## Constraints

- 仅用于纯联合类型校验，不替代 BaseModel 字段校验
- 若为可辨识联合，判别字段须存在且取值匹配

## Cautions

- 联合校验错误信息可能较冗长，可考虑可辨识联合简化错误

## Output Contract

- 返回解析后的具体联合成员实例

## Example Therapist Responses

### Example 1

- Client/Input: type_adapter = TypeAdapter(Pet); type_adapter.validate_python({'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'})
- Therapist/Output: BlackCat(pet_type='cat', color='black', black_name='felix')
- Notes: Pet 为嵌套可辨识联合类型

## Triggers

- 需要校验的数据目标仅为联合类型本身
- 不希望为校验而继承 BaseModel
- 需要对联合类型单独执行 validate_python

## Examples

### Example 1

Input:

  type_adapter = TypeAdapter(Pet); type_adapter.validate_python({'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'})

Output:

  BlackCat(pet_type='cat', color='black', black_name='felix')

Notes:

  Pet 为嵌套可辨识联合类型
