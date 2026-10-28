---
id: "2de78ee8-e350-5fb5-be7d-84c34b80f056"
name: "字段校验器显式返回值契约"
description: "编写或审查 Pydantic 字段级 field_validator 时，确保校验逻辑在每条执行路径上显式返回最终值（原值或规范化后的值），避免字段被置空或校验失效。"
version: "0.1.0"
tags:
  - "pydantic"
  - "field_validator"
  - "返回值契约"
  - "数据校验"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "编写或修改 field_validator 函数体"
  - "校验器需要转换或规范化字段值"
  - "审查字段校验器实现是否正确"
examples:
  - input: "编写一个校验数字为偶数的 field_validator，仅做检查不修改值"
    output: "def check_even(cls, v):\n    if v % 2 != 0:\n        raise ValueError(f'{v} is not an even number')\n    return v"
    notes: "仅做检查时返回原值不变"
---

# 字段校验器显式返回值契约

编写或审查 Pydantic 字段级 field_validator 时，确保校验逻辑在每条执行路径上显式返回最终值（原值或规范化后的值），避免字段被置空或校验失效。

## Prompt

在实现或审查 field_validator 函数体时，遵循返回值契约：校验器必须用 return 语句返回最终值（原值或规范化后的值）。若校验器只做检查而不返回，Pydantic 会将字段置为 None 或导致校验失效。检查步骤：1) 确认函数体每条执行路径都以 return 结束；2) 若对值做了转换或规范化，返回转换后的值；3) 若仅做校验，返回原值不变；4) 通过实例化模型验证字段值符合预期。

## Objective

保证字段校验器显式返回校验后的值，避免模型字段被置空或校验失效。
## Applicable Signals

- 正在编写 field_validator 函数体
- 校验器对字段值做转换或规范化
- 校验器仅做检查而不修改值

## Contraindications

- 仅需声明字段约束（如 gt、max_length）而无需自定义逻辑
- 编写模型级校验器而非字段级校验器

## Intervention Moves

- 在每条执行路径末尾添加 return 语句
- 转换场景返回转换后的值
- 仅检查场景返回原值不变
- 实例化模型验证字段值符合预期

## Workflow Steps

- 确认校验器为字段级 field_validator
- 确保函数体每条执行路径都以 return 结束
- 若做了转换或规范化，返回转换后的值
- 若仅做校验，返回原值不变
- 实例化模型并检查字段值是否符合预期

## Constraints

- 校验器必须显式返回最终值
- 不得依赖隐式返回 None

## Cautions

- 遗漏 return 会导致字段被置空或校验失效
- 转换逻辑需返回转换后的值而非原始输入

## Output Contract

- 校验器函数以 return 语句返回最终值，且模型实例化后字段值符合预期。

## Example Therapist Responses

### Example 1

- Client/Input: 编写一个校验数字为偶数的 field_validator，仅做检查不修改值
- Therapist/Output: def check_even(cls, v):
    if v % 2 != 0:
        raise ValueError(f'{v} is not an even number')
    return v
- Notes: 仅做检查时返回原值不变

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 编写或修改 field_validator 函数体
- 校验器需要转换或规范化字段值
- 审查字段校验器实现是否正确

## Examples

### Example 1

Input:

  编写一个校验数字为偶数的 field_validator，仅做检查不修改值

Output:

  def check_even(cls, v):
      if v % 2 != 0:
          raise ValueError(f'{v} is not an even number')
      return v

Notes:

  仅做检查时返回原值不变
