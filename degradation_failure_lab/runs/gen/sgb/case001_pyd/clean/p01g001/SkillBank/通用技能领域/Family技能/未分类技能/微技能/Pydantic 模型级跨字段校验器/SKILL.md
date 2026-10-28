---
id: "4045e587-c93f-5cf1-96d8-34f912827e83"
name: "Pydantic 模型级跨字段校验器"
description: "使用 model_validator(mode='after') 在模型实例化后校验同一模型内多个字段之间的一致性，不一致时抛出 ValueError。适用于字段级约束无法表达的跨字段逻辑。"
version: "0.1.0"
tags:
  - "pydantic"
  - "model_validator"
  - "跨字段校验"
  - "数据校验"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "需要比较同一模型内多个字段的值"
  - "字段级约束无法表达跨字段逻辑"
  - "需要在模型实例化后校验字段一致性"
examples:
  - input: "class UserModel(BaseModel):\n    username: str\n    password: str\n    password_repeat: str"
    output: "@model_validator(mode='after')\ndef check_passwords_match(self) -> Self:\n    if self.password != self.password_repeat:\n        raise ValueError('Passwords do not match')\n    return self"
    notes: "跨字段一致性校验示例"
---

# Pydantic 模型级跨字段校验器

使用 model_validator(mode='after') 在模型实例化后校验同一模型内多个字段之间的一致性，不一致时抛出 ValueError。适用于字段级约束无法表达的跨字段逻辑。

## Prompt

在模型定义中声明一个 mode='after' 的 model_validator，接收已实例化的模型自身，比较相关字段值；若不一致则抛出 ValueError 并给出清晰错误信息；校验通过时返回 self。

## Objective

在模型实例化后执行跨字段一致性校验并在失败时抛出验证错误
## Applicable Signals

- 模型包含两个及以上需相互比较的字段
- 单字段约束无法覆盖的依赖关系

## Contraindications

- 仅需单字段约束时
- 需要在实例化前处理原始输入时（应使用 before 校验器）

## Intervention Moves

- 声明 @model_validator(mode='after') 方法
- 在方法内比较相关字段值
- 不一致时 raise ValueError 并说明原因
- 校验通过时 return self

## Workflow Steps

- 确认跨字段一致性需求无法由字段级约束表达
- 在模型类中定义 mode='after' 的 model_validator 方法
- 在方法内读取并比较相关字段
- 不一致时抛出 ValueError 并给出明确错误信息
- 校验通过时返回 self

## Constraints

- after 校验器在模型实例化后运行，操作的是已解析的字段值
- 校验失败必须抛出 ValueError 以触发验证错误

## Cautions

- before 校验器处理原始输入，若在 before 中直接修改值后又抛出验证错误，被修改的值可能传递给其他校验器（如使用 unions 时），应避免

## Output Contract

- 返回 self 的 after 模型校验器，校验失败时抛出 ValueError

## Example Therapist Responses

### Example 1

- Client/Input: class UserModel(BaseModel):
    username: str
    password: str
    password_repeat: str
- Therapist/Output: @model_validator(mode='after')
def check_passwords_match(self) -> Self:
    if self.password != self.password_repeat:
        raise ValueError('Passwords do not match')
    return self
- Notes: 跨字段一致性校验示例

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要比较同一模型内多个字段的值
- 字段级约束无法表达跨字段逻辑
- 需要在模型实例化后校验字段一致性

## Examples

### Example 1

Input:

  class UserModel(BaseModel):
      username: str
      password: str
      password_repeat: str

Output:

  @model_validator(mode='after')
  def check_passwords_match(self) -> Self:
      if self.password != self.password_repeat:
          raise ValueError('Passwords do not match')
      return self

Notes:

  跨字段一致性校验示例
