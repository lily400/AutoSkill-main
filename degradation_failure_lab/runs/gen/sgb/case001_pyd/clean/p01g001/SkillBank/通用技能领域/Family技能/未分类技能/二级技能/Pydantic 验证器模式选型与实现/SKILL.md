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
  - "未分类技能"
  - "profile:pydantic::未分类技能"
  - "kind:parent"
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

## 子技能目录
- [After 模型验证器实现](通用技能领域/Family技能/未分类技能/微技能/After 模型验证器实现/SKILL.md) ｜ 适用：实现 Pydantic after 模型验证器：将其定义为实例方法，在整个模型校验完成后运行，作为初始化后钩子，并必须返回校验后的实例。适用于需要在模型级校验完成后执行跨字段逻辑或后初始化处理的场景。
- [Pydantic 模型级跨字段校验器](通用技能领域/Family技能/未分类技能/微技能/Pydantic 模型级跨字段校验器/SKILL.md) ｜ 适用：使用 model_validator(mode='after') 在模型实例化后校验同一模型内多个字段之间的一致性，不一致时抛出 ValueError。适用于字段级约束无法表达的跨字段逻辑。
- [字段校验器显式返回值契约](通用技能领域/Family技能/未分类技能/微技能/字段校验器显式返回值契约/SKILL.md) ｜ 适用：编写或审查 Pydantic 字段级 field_validator 时，确保校验逻辑在每条执行路径上显式返回最终值（原值或规范化后的值），避免字段被置空或校验失效。
- [字段校验器通配符与字段检查配置](通用技能领域/Family技能/未分类技能/微技能/字段校验器通配符与字段检查配置/SKILL.md) ｜ 适用：使用装饰器式字段校验器时，通过传入 '*' 使校验器作用于所有字段（含子类字段），并通过 check_fields=False 在基类上定义校验器而允许字段在子类中存在。适用于在基类或跨字段场景中复用字段校验逻辑。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `After 模型验证器实现` 时，优先调用它。 线索：需要在整个模型校验完成后执行跨字段逻辑, 需要后初始化钩子, 需要在模型级校验后对已校验实例做处理, pydantic, model_validator
- 当目标、阶段或方法更接近 `Pydantic 模型级跨字段校验器` 时，优先调用它。 线索：需要比较同一模型内多个字段的值, 字段级约束无法表达跨字段逻辑, 需要在模型实例化后校验字段一致性, pydantic, model_validator
- 当目标、阶段或方法更接近 `字段校验器显式返回值契约` 时，优先调用它。 线索：编写或修改 field_validator 函数体, 校验器需要转换或规范化字段值, 审查字段校验器实现是否正确, pydantic, field_validator
- 当目标、阶段或方法更接近 `字段校验器通配符与字段检查配置` 时，优先调用它。 线索：需要在基类上定义字段校验器并期望子类字段也受校验, 希望校验器作用于模型全部字段, pydantic, field-validator, decorator

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

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
