---
id: "50016175-02e2-59a2-b10a-9128ffd4676a"
name: "Before 校验器预处理原始输入"
description: "使用 before 校验器在 Pydantic 内部类型校验前对任意原始输入做规范化处理（如将标量包装为列表），并覆盖所有可能的输入类型；处理后的值仍会继续进入 Pydantic 的字段类型校验。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validator"
  - "before-validator"
  - "input-normalization"
triggers:
  - "输入类型不确定，需要在校验前先规范化"
  - "需要把标量包装为列表等预处理动作"
  - "需要在 Pydantic 内部类型校验前干预原始输入"
examples:
  - input: "字段为 list[int]，传入标量 2"
    output: "before 校验器将 2 包装为 [2]，随后 Pydantic 校验通过，numbers=[2]"
    notes: "value 使用 Any 类型提示以接收原始输入"
  - input: "字段为 list[int]，传入 'str'"
    output: "校验器处理后仍由 Pydantic 执行 int 校验，产生 int_parsing 校验错误"
    notes: "说明 before 校验器不替代内部类型校验"
---

# Before 校验器预处理原始输入

使用 before 校验器在 Pydantic 内部类型校验前对任意原始输入做规范化处理（如将标量包装为列表），并覆盖所有可能的输入类型；处理后的值仍会继续进入 Pydantic 的字段类型校验。

## Prompt

在字段上声明 before 校验器，接收原始输入（类型提示用 Any，因为校验前输入可以是任何类型）。在校验器内对原始输入做规范化处理（例如把标量包装为列表），并显式覆盖所有可能的输入类型（包括 tuple 等通常能通过 list 校验的序列类型）。处理完成后返回结果，交由 Pydantic 继续按字段类型执行内部校验；不要假设校验器已替代类型校验。

## Objective

在类型校验前对原始输入做规范化处理
## Applicable Signals

- 字段可能收到标量而非列表等非预期形态
- 需要在类型转换前统一输入形态
- 原始输入类型无法预先确定

## Contraindications

- 无需在类型校验前干预输入
- 无法枚举所有可能的输入类型
- 希望跳过 Pydantic 内部类型校验（应改用 plain 校验器）

## Intervention Moves

- 用 Any 作为 value 的类型提示以接收任意原始输入
- 在校验器内将标量包装为列表等规范化处理
- 显式处理 tuple 等其它可能通过 list 校验的序列类型
- 返回处理后结果，交由 Pydantic 继续类型校验

## Workflow Steps

- 确认该字段需要在类型校验前干预原始输入
- 声明 before 校验器，value 使用 Any 类型提示
- 在校验器内枚举并处理所有可能的输入类型（含标量、tuple 等序列）
- 返回规范化后的值
- 依赖 Pydantic 继续对返回值执行字段类型校验

## Constraints

- before 校验器接收的是原始输入，类型提示应为 Any
- 必须覆盖所有可能的输入类型，包括 tuple 等通常能通过 list 校验的序列
- before 校验器不会跳过 Pydantic 对字段类型的内部校验

## Cautions

- 若只处理部分输入类型，未覆盖的形态可能在后续类型校验中报错
- 若需要在校验器返回后立即终止校验，应使用 plain 校验器而非 before 校验器

## Output Contract

- 经预处理的输入继续进入 Pydantic 类型校验；校验器返回规范化后的值，由 Pydantic 按字段类型完成后续校验。

## Example Therapist Responses

### Example 1

- Client/Input: 字段为 list[int]，传入标量 2
- Therapist/Output: before 校验器将 2 包装为 [2]，随后 Pydantic 校验通过，numbers=[2]
- Notes: value 使用 Any 类型提示以接收原始输入

### Example 2

- Client/Input: 字段为 list[int]，传入 'str'
- Therapist/Output: 校验器处理后仍由 Pydantic 执行 int 校验，产生 int_parsing 校验错误
- Notes: 说明 before 校验器不替代内部类型校验

## Triggers

- 输入类型不确定，需要在校验前先规范化
- 需要把标量包装为列表等预处理动作
- 需要在 Pydantic 内部类型校验前干预原始输入

## Examples

### Example 1

Input:

  字段为 list[int]，传入标量 2

Output:

  before 校验器将 2 包装为 [2]，随后 Pydantic 校验通过，numbers=[2]

Notes:

  value 使用 Any 类型提示以接收原始输入

### Example 2

Input:

  字段为 list[int]，传入 'str'

Output:

  校验器处理后仍由 Pydantic 执行 int 校验，产生 int_parsing 校验错误

Notes:

  说明 before 校验器不替代内部类型校验
