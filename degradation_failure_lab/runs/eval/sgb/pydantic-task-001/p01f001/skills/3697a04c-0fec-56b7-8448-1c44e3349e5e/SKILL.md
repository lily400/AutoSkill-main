---
id: "3697a04c-0fec-56b7-8448-1c44e3349e5e"
name: "Before 校验器安全实现"
description: "在 Pydantic 中实现 before 模式校验器：在内部解析与校验之前处理原始输入，并避免在校验失败前直接修改值，防止变更值流入其他校验器（如 unions）。适用于需要处理原始输入且校验器可能抛出校验错误的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "before-validator"
  - "数据校验"
  - "副作用防护"
triggers:
  - "需要在 Pydantic 内部解析前处理原始输入"
  - "校验器可能抛出校验错误且涉及值变更"
examples:
  - input: "需要在 Pydantic 解析前处理原始输入，且校验器可能抛出校验错误"
    output: "实现 before 校验器：处理原始输入，避免在校验失败前原地修改值，返回新值交由类型注解再次校验"
    notes: "若无需处理原始输入，应改用 after 校验器"
---

# Before 校验器安全实现

在 Pydantic 中实现 before 模式校验器：在内部解析与校验之前处理原始输入，并避免在校验失败前直接修改值，防止变更值流入其他校验器（如 unions）。适用于需要处理原始输入且校验器可能抛出校验错误的场景。

## Prompt

实现 before 校验器时，先确认需求必须在 Pydantic 内部解析前处理原始输入；函数接收原始输入（理论上可为任意对象），需自行处理类型不确定性。若后续可能抛出校验错误，避免直接原地修改值，改为返回新值或在校验通过后再变更，以防变更值流入其他校验器（如 unions）。返回的值将由 Pydantic 依据类型注解再次校验。

## Objective

安全地实现 before 校验器，避免副作用污染后续校验
## Applicable Signals

- 需要绕过或先于 Pydantic 内部解析与校验（如 str 到 int 的强制转换）处理输入
- 校验逻辑需面对任意原始对象类型
- 校验函数内可能抛出校验错误且涉及值变更

## Contraindications

- after 校验器已能满足需求
- 无需处理原始输入类型

## Intervention Moves

- 确认使用 before 模式而非默认 after 模式
- 在函数内处理原始输入的类型不确定性
- 避免在校验失败前直接原地修改值
- 返回新值交由类型注解再次校验

## Workflow Steps

- 判断是否必须在 Pydantic 内部解析前处理原始输入，否则改用 after 校验器
- 编写 before 校验器函数，接收原始输入并处理其类型不确定性
- 若函数后续可能抛出校验错误，避免直接原地修改值，改为返回新值
- 返回结果，由 Pydantic 依据类型注解再次校验

## Constraints

- before 校验器运行于 Pydantic 内部解析与校验之前
- 返回的值必须能通过类型注解的再次校验
- 避免在校验失败前直接修改值，以防变更值流入其他校验器（如 unions）

## Cautions

- before 校验器比 after 校验器更灵活，但需处理任意原始输入对象
- 在 unions 场景下，被修改的值可能传递给其他校验器，需格外谨慎

## Output Contract

- 返回经类型注解再次校验的值的 before 校验器函数

## Example Therapist Responses

### Example 1

- Client/Input: 需要在 Pydantic 解析前处理原始输入，且校验器可能抛出校验错误
- Therapist/Output: 实现 before 校验器：处理原始输入，避免在校验失败前原地修改值，返回新值交由类型注解再次校验
- Notes: 若无需处理原始输入，应改用 after 校验器

## Triggers

- 需要在 Pydantic 内部解析前处理原始输入
- 校验器可能抛出校验错误且涉及值变更

## Examples

### Example 1

Input:

  需要在 Pydantic 解析前处理原始输入，且校验器可能抛出校验错误

Output:

  实现 before 校验器：处理原始输入，避免在校验失败前原地修改值，返回新值交由类型注解再次校验

Notes:

  若无需处理原始输入，应改用 after 校验器
