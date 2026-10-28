---
id: "9eb16e27-a3e6-5b09-a407-854038ca54a2"
name: "Pydantic before 校验器安全变异约束"
description: "在编写或审查 Pydantic before 校验器时，约束对原始输入的直接变异行为：若校验器后续可能抛出验证错误，应避免直接变异值，以防变异后的值经 union 等路径传递给其他校验器产生副作用。"
version: "0.1.0"
tags:
  - "pydantic"
  - "validator"
  - "before-validator"
  - "mutation-safety"
  - "union"
triggers:
  - "编写 before 校验器"
  - "审查 before 校验器中的值变异"
  - "校验器内存在后续可能抛出验证错误的路径"
  - "使用 union 且涉及 before 校验器变异"
---

# Pydantic before 校验器安全变异约束

在编写或审查 Pydantic before 校验器时，约束对原始输入的直接变异行为：若校验器后续可能抛出验证错误，应避免直接变异值，以防变异后的值经 union 等路径传递给其他校验器产生副作用。

## Prompt

在编写或审查 before 校验器时执行以下约束检查：
1. 确认当前校验器为 before 模式（在模型实例化之前运行，处理原始输入）。
2. 判断校验器内是否存在后续可能抛出验证错误的路径。
3. 若存在该路径，避免直接变异输入值；改为基于副本或返回新值，确保变异不会泄漏到其他校验器（尤其是 union 场景）。
4. 若确需变异且不会抛出错误，方可就地修改，并说明理由。
5. 输出符合约束的 before 校验器实现或审查结论。

## Objective

防止 before 校验器中不安全的值变异导致副作用传播
## Applicable Signals

- 正在编写 before 校验器
- 校验器内可能后续抛出验证错误
- 输入值可能经 union 传递给其他校验器

## Contraindications

- after 校验器中已实例化的安全场景
- 校验器不会抛出验证错误且无 union 传播风险的就地变异

## Intervention Moves

- 识别 before 校验器中的错误抛出路径
- 避免直接变异原始输入值
- 改用副本或返回新值以隔离变异
- 在 union 场景下确认变异不会泄漏

## Workflow Steps

- 确认校验器为 before 模式
- 检查是否存在后续抛出验证错误的路径
- 若存在则避免直接变异输入值，改用副本或返回新值
- 在 union 场景下验证变异不会传递给其他校验器
- 输出符合约束的实现或审查结论

## Constraints

- 仅在 before 校验器场景应用
- 存在后续错误抛出路径时不得直接变异原始输入
- 需考虑 union 下变异值可能传递给其他校验器

## Cautions

- before 校验器处理的是任意原始输入，需谨慎对待类型
- 就地变异在 union 场景下可能产生难以追踪的副作用

## Output Contract

- 未发生不安全变异的 before 校验器实现，或针对现有 before 校验器的变异安全审查结论

## Triggers

- 编写 before 校验器
- 审查 before 校验器中的值变异
- 校验器内存在后续可能抛出验证错误的路径
- 使用 union 且涉及 before 校验器变异
