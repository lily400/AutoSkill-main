---
id: "3df5f979-7629-5c57-8c24-746c21770722"
name: "联合类型从左到右校验顺序控制"
description: "解释并预测 Pydantic 联合类型按声明顺序从左到右依次尝试成员校验的行为，以及 lax 模式下类型转换导致的意外匹配；用于调试或设计含混合成员（如 int/str）的联合字段。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "validation-order"
  - "lax-mode"
  - "type-coercion"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "需要解释联合类型为何返回非预期成员类型"
  - "设计含 int/str 混合成员的联合字段"
  - "调试联合类型解析结果"
examples:
  - input: "联合字段声明为 int | str，输入为字符串 '123'，结果 id 为 int 类型"
    output: "因为联合按声明顺序先尝试 int 成员，lax 模式下 '123' 被转换为 int 并通过校验，故结果为 int 而非 str。"
    notes: "体现从左到右顺序与 lax 类型转换的意外匹配"
---

# 联合类型从左到右校验顺序控制

解释并预测 Pydantic 联合类型按声明顺序从左到右依次尝试成员校验的行为，以及 lax 模式下类型转换导致的意外匹配；用于调试或设计含混合成员（如 int/str）的联合字段。

## Prompt

当需要解释联合类型为何返回非预期成员类型，或设计含 int/str 混合成员的联合字段时，按以下要点说明：联合类型按成员声明顺序从左到右依次尝试校验，第一个通过校验的成员即为结果；在 lax 模式下，字符串等输入可能被转换为更早声明的成员类型（如 '123' 被转换为 int），从而产生意外匹配。若需要确定性区分成员类型，应改用判别联合而非依赖顺序。

## Objective

理解并预测联合类型按声明顺序校验的行为及 lax 模式下的类型转换陷阱
## Applicable Signals

- 联合字段返回了与预期不同的成员类型
- 联合成员包含可相互转换的类型（如 int 与 str）
- 输入为数字字符串但结果被解析为 int

## Contraindications

- 需要确定性区分成员类型时应改用判别联合，而非依赖顺序校验

## Intervention Moves

- 说明联合类型按声明顺序从左到右尝试成员校验
- 指出 lax 模式下字符串可被转换为更早声明的 int 成员
- 建议在需要确定性区分时改用判别联合

## Workflow Steps

- 确认联合成员的声明顺序
- 判断输入是否可被更早声明的成员在 lax 模式下转换
- 解释实际匹配到的成员及原因
- 若需确定性区分，建议改用判别联合

## Constraints

- 仅适用于解释或预测联合类型校验顺序与类型转换行为
- 不替代判别联合等确定性区分方案

## Cautions

- lax 模式下的隐式类型转换可能导致与直觉不符的解析结果

## Output Contract

- 能说明联合类型按声明顺序尝试且 lax 模式会转换字符串为 int 的规则

## Example Therapist Responses

### Example 1

- Client/Input: 联合字段声明为 int | str，输入为字符串 '123'，结果 id 为 int 类型
- Therapist/Output: 因为联合按声明顺序先尝试 int 成员，lax 模式下 '123' 被转换为 int 并通过校验，故结果为 int 而非 str。
- Notes: 体现从左到右顺序与 lax 类型转换的意外匹配

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要解释联合类型为何返回非预期成员类型
- 设计含 int/str 混合成员的联合字段
- 调试联合类型解析结果

## Examples

### Example 1

Input:

  联合字段声明为 int | str，输入为字符串 '123'，结果 id 为 int 类型

Output:

  因为联合按声明顺序先尝试 int 成员，lax 模式下 '123' 被转换为 int 并通过校验，故结果为 int 而非 str。

Notes:

  体现从左到右顺序与 lax 类型转换的意外匹配
