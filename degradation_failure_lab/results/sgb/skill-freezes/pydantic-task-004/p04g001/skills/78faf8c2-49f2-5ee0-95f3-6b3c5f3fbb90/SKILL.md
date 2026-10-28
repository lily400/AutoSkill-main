---
id: "78faf8c2-49f2-5ee0-95f3-6b3c5f3fbb90"
name: "Union 智能模式成员选择"
description: "按 Pydantic Smart Mode 规则在联合类型成员间选择最佳匹配：先按精确度评分，再以有效字段数决胜，平局用精确度打破。用于需要从多个候选模型/类型中确定唯一有效解析结果的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "smart_mode"
  - "validation"
  - "scoring"
triggers:
  - "需要从多个候选 BaseModel/dataclass/TypedDict 中确定最佳匹配"
  - "联合成员可能同时部分匹配，需要评分决胜"
examples:
  - input: "联合成员 A 与 B 均部分匹配，A 有效字段数更高"
    output: "返回成员 A 的解析结果"
    notes: "有效字段数优先"
  - input: "联合成员 A 与 B 有效字段数相同，A 精确度更高"
    output: "返回成员 A 的解析结果"
    notes: "平局用精确度打破"
  - input: "所有联合成员校验均失败"
    output: "返回全部成员的错误集合"
    notes: "失败时汇总所有错误"
---

# Union 智能模式成员选择

按 Pydantic Smart Mode 规则在联合类型成员间选择最佳匹配：先按精确度评分，再以有效字段数决胜，平局用精确度打破。用于需要从多个候选模型/类型中确定唯一有效解析结果的场景。

## Prompt

当联合类型需要从多个候选成员中确定唯一最佳匹配时，按 Smart Mode 流程执行：从左到右尝试各成员，记录成功匹配的精确度类别与有效字段数；全部评估后返回有效字段数最高的成员；若并列，则用精确度评分打破平局；若全部失败，返回所有错误。不要在此流程中改用左到右短路或判别联合策略。

## Objective

在联合类型校验中按有效字段数与精确度评分选出唯一最佳成员
## Applicable Signals

- 联合成员为 BaseModel、dataclass 或 TypedDict 等结构化类型
- 多个成员可能同时部分匹配，需要评分决胜
- 需要返回单一最佳成员而非首个成功匹配

## Contraindications

- 仅需左到右首个成功匹配即可（应使用 Left to Right Mode）
- 存在可用的判别字段（应优先使用 Discriminated Unions）

## Intervention Moves

- 从左到右尝试每个联合成员
- 将成功匹配归入精确度类别并统计有效字段数
- 全部评估后按有效字段数选出最高者
- 平局时用精确度评分打破
- 全部失败时汇总所有错误

## Workflow Steps

- 从左到右依次尝试每个联合成员，记录成功匹配的精确度类别与有效字段数。
- 全部成员评估完成后，返回有效字段数最高的成员。
- 若有效字段数并列，使用精确度评分作为决胜，返回精确度最高的成员。
- 若所有成员均校验失败，返回全部错误。

## Constraints

- 必须评估全部成员后再做选择，不得在首个成功匹配处短路
- 平局决胜必须使用精确度评分
- 全部失败时必须返回所有错误而非单一错误

## Cautions

- Smart Mode 与 Left to Right Mode 行为不同，勿混用
- 若存在判别字段，应优先考虑 Discriminated Unions 以获得更确定的解析

## Output Contract

- 返回有效字段数最高、平局时精确度最高的单一成员结果；若全部失败则返回所有错误。

## Example Therapist Responses

### Example 1

- Client/Input: 联合成员 A 与 B 均部分匹配，A 有效字段数更高
- Therapist/Output: 返回成员 A 的解析结果
- Notes: 有效字段数优先

### Example 2

- Client/Input: 联合成员 A 与 B 有效字段数相同，A 精确度更高
- Therapist/Output: 返回成员 A 的解析结果
- Notes: 平局用精确度打破

### Example 3

- Client/Input: 所有联合成员校验均失败
- Therapist/Output: 返回全部成员的错误集合
- Notes: 失败时汇总所有错误

## Triggers

- 需要从多个候选 BaseModel/dataclass/TypedDict 中确定最佳匹配
- 联合成员可能同时部分匹配，需要评分决胜

## Examples

### Example 1

Input:

  联合成员 A 与 B 均部分匹配，A 有效字段数更高

Output:

  返回成员 A 的解析结果

Notes:

  有效字段数优先

### Example 2

Input:

  联合成员 A 与 B 有效字段数相同，A 精确度更高

Output:

  返回成员 A 的解析结果

Notes:

  平局用精确度打破

### Example 3

Input:

  所有联合成员校验均失败

Output:

  返回全部成员的错误集合

Notes:

  失败时汇总所有错误
