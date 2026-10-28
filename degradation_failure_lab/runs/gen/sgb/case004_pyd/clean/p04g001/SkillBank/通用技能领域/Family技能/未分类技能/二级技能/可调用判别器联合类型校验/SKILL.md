---
id: "556b9c81-2257-59a9-9233-b7eab81bd6d8"
name: "可调用判别器联合类型校验"
description: "使用 callable Discriminator 配合 Tag 注解，将联合类型按运行时类型分派到对应成员进行校验。适用于联合成员无法用单一字符串字段区分、需要自定义判别逻辑的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "discriminator"
  - "callable"
  - "tag"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
  - "kind:parent"
triggers:
  - "联合成员需按运行时类型（如 int 与 dict/BaseModel）区分"
  - "字符串判别字段无法覆盖判别逻辑"
examples:
  - input: "value 字段联合 int 与 SpecialValue，判别函数按 isinstance 返回 'int' 或 'model'"
    output: "输入 {'value': {'value': 1}} 得到 SpecialValue(value=1)；输入 {'value': 123} 得到 123"
    notes: "判别值未找到时返回 None，触发 union_tag_not_found"
---

# 可调用判别器联合类型校验

使用 callable Discriminator 配合 Tag 注解，将联合类型按运行时类型分派到对应成员进行校验。适用于联合成员无法用单一字符串字段区分、需要自定义判别逻辑的场景。

## Prompt

为联合类型字段配置可调用判别器：定义判别函数，按运行时类型返回对应 Tag 标签；用 Annotated 将各联合成员标注 Tag，并用 Discriminator 包裹整个联合；判别值未找到时返回 None。随后用 model_validate 验证不同输入能分派到正确成员。

## Objective

为联合类型字段配置可调用判别器，实现按运行时类型分派校验
## Applicable Signals

- 联合成员需按运行时类型（如 int 与 dict/BaseModel）区分
- 字符串判别字段无法覆盖判别逻辑

## Contraindications

- 联合成员可用单一字符串字段直接区分时优先用 str 判别器
- 判别函数无法稳定返回标签时

## Intervention Moves

- 定义判别函数，按 isinstance 判断运行时类型并返回对应标签
- 判别值未找到时返回 None
- 用 Annotated 为每个联合成员标注 Tag
- 用 Discriminator 包裹联合并传入判别函数
- 用 model_validate 验证不同输入分派到正确成员

## Workflow Steps

- 定义判别函数，按运行时类型返回对应标签字符串
- 判别值未找到时返回 None
- 用 Annotated 为每个联合成员标注 Tag
- 用 Annotated 将联合与 Discriminator(判别函数) 组合为字段类型
- 用 model_validate 验证不同输入分派到正确成员实例

## Constraints

- 判别函数必须对每个可接受输入返回稳定标签
- 判别值未找到时应返回 None 而非抛出异常

## Cautions

- 判别函数返回 None 时会触发 union_tag_not_found 错误

## Output Contract

- 带 Discriminator 与 Tag 注解的联合字段模型，能正确校验并返回对应成员实例

## Example Therapist Responses

### Example 1

- Client/Input: value 字段联合 int 与 SpecialValue，判别函数按 isinstance 返回 'int' 或 'model'
- Therapist/Output: 输入 {'value': {'value': 1}} 得到 SpecialValue(value=1)；输入 {'value': 123} 得到 123
- Notes: 判别值未找到时返回 None，触发 union_tag_not_found

## 子技能目录
- [Callable Discriminator Returns None for Unknown Tags](通用技能领域/Family技能/未分类技能/微技能/Callable Discriminator Returns None for Unknown Tags/SKILL.md) ｜ 适用：When writing a callable Discriminator for a Pydantic union, explicitly return None for input types not covered by known branches so that a union_tag_not_found error is raised, and ensure the caller handles that error.
- [TypeAdapter 校验纯联合类型](通用技能领域/Family技能/未分类技能/微技能/TypeAdapter 校验纯联合类型/SKILL.md) ｜ 适用：当校验目标仅为联合类型本身、且不希望继承 BaseModel 时，使用 TypeAdapter 包装联合类型并调用 validate_python 对数据执行校验，返回解析后的具体联合成员实例。
- [可调用判别器设计](通用技能领域/Family技能/未分类技能/微技能/可调用判别器设计/SKILL.md) ｜ 适用：当联合成员之间没有统一判别字段时，编写可调用 Discriminator 函数，使其同时处理 dict 与模型实例输入，从而在验证与序列化阶段都能正确判别，避免序列化警告或运行时错误。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `Callable Discriminator Returns None for Unknown Tags` 时，优先调用它。 线索：判别函数遇到未覆盖的输入类型, 需要明确未知判别值的失败行为, pydantic, union, discriminator
- 当目标、阶段或方法更接近 `TypeAdapter 校验纯联合类型` 时，优先调用它。 线索：需要校验的数据目标仅为联合类型本身, 不希望为校验而继承 BaseModel, 需要对联合类型单独执行 validate_python, pydantic, union
- 当目标、阶段或方法更接近 `可调用判别器设计` 时，优先调用它。 线索：联合成员之间没有单一统一判别字段, 需要在序列化阶段也能正确判别联合成员, 准备为 Union 配置 callable Discriminator, pydantic, union

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 联合成员需按运行时类型（如 int 与 dict/BaseModel）区分
- 字符串判别字段无法覆盖判别逻辑

## Examples

### Example 1

Input:

  value 字段联合 int 与 SpecialValue，判别函数按 isinstance 返回 'int' 或 'model'

Output:

  输入 {'value': {'value': 1}} 得到 SpecialValue(value=1)；输入 {'value': 123} 得到 123

Notes:

  判别值未找到时返回 None，触发 union_tag_not_found
