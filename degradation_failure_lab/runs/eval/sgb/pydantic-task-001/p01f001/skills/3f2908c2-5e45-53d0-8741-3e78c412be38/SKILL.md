---
id: "3f2908c2-5e45-53d0-8741-3e78c412be38"
name: "Pydantic 校验器执行顺序控制"
description: "按 Pydantic 规定的顺序组织字段校验器与模型校验器：字段校验先于模型校验，before 模式先于 after 模式，确保校验逻辑的依赖关系正确。适用于模型中存在多个校验器或校验逻辑依赖其他字段已校验值的设计场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validator"
  - "ordering"
  - "validation"
triggers:
  - "模型中有多个字段校验器和模型校验器"
  - "校验逻辑依赖其他字段已校验后的值"
  - "需要确定 before 与 after 校验器的相对执行位置"
examples:
  - input: "模型中有字段校验器与依赖其他字段已校验值的模型校验器"
    output: "将依赖已校验值的逻辑放入模型校验器，字段校验器保持在前执行"
    notes: "字段校验先于模型校验"
---

# Pydantic 校验器执行顺序控制

按 Pydantic 规定的顺序组织字段校验器与模型校验器：字段校验先于模型校验，before 模式先于 after 模式，确保校验逻辑的依赖关系正确。适用于模型中存在多个校验器或校验逻辑依赖其他字段已校验值的设计场景。

## Prompt

在设计或审查 Pydantic 模型校验器时，先梳理各校验器的依赖关系，再按 Pydantic 执行顺序规则安排：字段校验器先于模型校验器执行；同一层级内 before 模式先于 after 模式执行。若某校验逻辑依赖其他字段已校验后的值，应将其放在模型校验器或 after 模式中；若需要处理原始输入，应使用 before 模式并注意原始输入类型不确定。确认顺序后检查依赖关系是否成立。

## Objective

正确安排多个校验器的执行顺序
## Applicable Signals

- 模型中同时存在字段校验器与模型校验器
- 校验器之间或校验器与字段之间存在数据依赖
- 校验器使用 before 或 after 模式且需要确定执行先后

## Contraindications

- 只有一个独立校验器且无顺序依赖
- 校验器之间不存在任何数据或执行依赖

## Intervention Moves

- 识别每个校验器的依赖对象与所需输入状态
- 按字段校验先于模型校验的规则排列
- 在同一层级内按 before 先于 after 的规则排列
- 对依赖已校验值的逻辑改用模型校验器或 after 模式
- 对需要处理原始输入的逻辑使用 before 模式并处理类型不确定性

## Workflow Steps

- 列出模型中所有字段校验器与模型校验器
- 标注每个校验器的输入依赖（原始输入或已校验值）
- 按字段校验先于模型校验排序
- 在同一层级内按 before 先于 after 排序
- 验证排序后各校验器的依赖关系成立

## Constraints

- 字段校验器先于模型校验器执行
- before 模式先于 after 模式执行
- 依赖已校验值的逻辑不得放在 before 模式中

## Cautions

- before 模式接收原始输入，类型不确定，需处理所有可能的输入类型
- 即使 before 校验器对输入做了转换，Pydantic 仍会按声明类型执行校验

## Output Contract

- 校验器顺序符合 Pydantic 执行规则且依赖关系正确的模型设计

## Example Therapist Responses

### Example 1

- Client/Input: 模型中有字段校验器与依赖其他字段已校验值的模型校验器
- Therapist/Output: 将依赖已校验值的逻辑放入模型校验器，字段校验器保持在前执行
- Notes: 字段校验先于模型校验

## Triggers

- 模型中有多个字段校验器和模型校验器
- 校验逻辑依赖其他字段已校验后的值
- 需要确定 before 与 after 校验器的相对执行位置

## Examples

### Example 1

Input:

  模型中有字段校验器与依赖其他字段已校验值的模型校验器

Output:

  将依赖已校验值的逻辑放入模型校验器，字段校验器保持在前执行

Notes:

  字段校验先于模型校验
