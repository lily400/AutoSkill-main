---
id: "5faaba9c-de9a-593e-b531-bc2479e25d36"
name: "联合类型精确度匹配评分"
description: "说明 Pydantic 校验联合类型（Union）时如何按精确度对成员匹配打分并选出最佳匹配，用于判断或解释联合类型中哪个成员应胜出。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "exactness"
  - "匹配选择"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "需要判断联合类型多个成员中哪个匹配最优"
  - "解释联合类型校验结果的选择依据"
examples:
  - input: "int 输入匹配 float | int 联合类型"
    output: "int 成员为精确类型匹配，得分最高，判定为最佳匹配。"
    notes: "精确类型匹配优先于其他层级"
---

# 联合类型精确度匹配评分

说明 Pydantic 校验联合类型（Union）时如何按精确度对成员匹配打分并选出最佳匹配，用于判断或解释联合类型中哪个成员应胜出。

## Prompt

当需要判断联合类型多个成员中哪个匹配最优，或解释联合类型校验结果的选择依据时，按精确度评分规则对每个成员匹配打分：精确类型匹配得分最高，其次是在 strict 模式下会成功的匹配，再次是在 lax 模式下会成功的匹配；取得最高精确度得分的成员即为最佳匹配。仅用于联合类型匹配选择，不用于单类型校验或自定义判别器逻辑。

## Objective

按精确度评分规则确定联合类型的最佳匹配成员
## Applicable Signals

- 输入需要匹配多个候选类型之一
- 需要说明为何某个联合成员被选中

## Contraindications

- 非联合类型的单类型校验
- 需要自定义判别器逻辑而非精确度评分时

## Intervention Moves

- 对每个联合成员计算精确度得分
- 按精确类型匹配 > strict 模式成功 > lax 模式成功排序
- 选择得分最高的成员作为最佳匹配

## Workflow Steps

- 确认校验对象为联合类型且存在多个候选成员
- 对每个成员判断匹配层级：精确类型匹配、strict 模式成功、lax 模式成功
- 按层级从高到低赋分
- 选出最高精确度得分的成员作为最佳匹配
- 输出按精确度排序的成员匹配结论

## Constraints

- 评分仅依据三个精确度层级，不引入其他自定义权重
- 仅在联合类型场景下应用

## Cautions

- 精确类型匹配优先于 strict 模式成功，strict 模式成功优先于 lax 模式成功
- 若需自定义判别器逻辑，应改用判别联合而非精确度评分

## Output Contract

- 给出按精确度排序的成员匹配结论，并指明最佳匹配成员。

## Example Therapist Responses

### Example 1

- Client/Input: int 输入匹配 float | int 联合类型
- Therapist/Output: int 成员为精确类型匹配，得分最高，判定为最佳匹配。
- Notes: 精确类型匹配优先于其他层级

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断联合类型多个成员中哪个匹配最优
- 解释联合类型校验结果的选择依据

## Examples

### Example 1

Input:

  int 输入匹配 float | int 联合类型

Output:

  int 成员为精确类型匹配，得分最高，判定为最佳匹配。

Notes:

  精确类型匹配优先于其他层级
