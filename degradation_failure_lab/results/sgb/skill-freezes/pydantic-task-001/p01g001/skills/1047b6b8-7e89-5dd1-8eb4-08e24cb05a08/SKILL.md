---
id: "1047b6b8-7e89-5dd1-8eb4-08e24cb05a08"
name: "After 模型验证器实现"
description: "实现 Pydantic after 模型验证器：将其定义为实例方法，在整个模型校验完成后运行，作为初始化后钩子，并必须返回校验后的实例。适用于需要在模型级校验完成后执行跨字段逻辑或后初始化处理的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "model_validator"
  - "after-validator"
  - "模型验证器"
  - "数据校验"
triggers:
  - "需要在整个模型校验完成后执行跨字段逻辑"
  - "需要后初始化钩子"
  - "需要在模型级校验后对已校验实例做处理"
examples:
  - input: "需要在整个模型校验完成后执行跨字段逻辑"
    output: "定义一个 after 模式模型验证器，作为实例方法接收 self，执行逻辑后返回校验后的实例"
    notes: "验证器必须返回实例"
---

# After 模型验证器实现

实现 Pydantic after 模型验证器：将其定义为实例方法，在整个模型校验完成后运行，作为初始化后钩子，并必须返回校验后的实例。适用于需要在模型级校验完成后执行跨字段逻辑或后初始化处理的场景。

## Prompt

编写 after 模型验证器时：1) 使用 model_validator(mode='after') 装饰器（或等价 after 模式）声明；2) 将方法定义为实例方法，接收 self；3) 在方法体内执行跨字段或后初始化逻辑；4) 必须返回校验后的实例（通常 return self）。不要用于仅需单字段校验或需在模型校验前修改输入的场景。

## Objective

正确编写 after 模型验证器并返回校验后的实例
## Applicable Signals

- 需要在整个模型校验完成后执行跨字段逻辑
- 需要后初始化钩子

## Contraindications

- 只需单字段校验
- 需要在模型校验前修改输入

## Intervention Moves

- 使用 after 模式声明模型验证器
- 将验证器定义为实例方法并接收 self
- 在方法内执行跨字段或后初始化逻辑
- 返回校验后的实例

## Workflow Steps

- 确认需求属于模型级校验完成后的处理，而非单字段校验或前置输入修改
- 使用 after 模式声明模型验证器
- 将验证器定义为实例方法，接收 self
- 在方法体内实现跨字段或后初始化逻辑
- 确保方法返回校验后的实例

## Constraints

- after 验证器必须定义为实例方法
- after 验证器必须返回校验后的实例

## Cautions

- 若误用于单字段校验或前置输入修改场景，应改用其他验证器模式

## Output Contract

- 返回校验后实例的 after 验证器方法

## Example Therapist Responses

### Example 1

- Client/Input: 需要在整个模型校验完成后执行跨字段逻辑
- Therapist/Output: 定义一个 after 模式模型验证器，作为实例方法接收 self，执行逻辑后返回校验后的实例
- Notes: 验证器必须返回实例

## Triggers

- 需要在整个模型校验完成后执行跨字段逻辑
- 需要后初始化钩子
- 需要在模型级校验后对已校验实例做处理

## Examples

### Example 1

Input:

  需要在整个模型校验完成后执行跨字段逻辑

Output:

  定义一个 after 模式模型验证器，作为实例方法接收 self，执行逻辑后返回校验后的实例

Notes:

  验证器必须返回实例
