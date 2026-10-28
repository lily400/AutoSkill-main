---
id: "7e9b6184-6ad1-511a-a756-2b9fff70151b"
name: "混合情感评论极性判定规则"
description: "对同时包含正面与负面内容的评论，按主导情感判定单一极性；均衡时默认判为负面以保守避免误判。用于情感分类计数前的极性裁决。"
version: "0.1.0"
tags:
  - "情感分类"
  - "极性判定"
  - "混合评论"
  - "规则判定"
  - "计数前置"
triggers:
  - "评论同时含正面与负面表述"
  - "需要为计数任务输出单一极性标签"
examples:
  - input: "产品保暖又时尚，但洗几次后起球且价格过高"
    output: "negative"
    notes: "耐用性问题显著，整体判为负面"
---

# 混合情感评论极性判定规则

对同时包含正面与负面内容的评论，按主导情感判定单一极性；均衡时默认判为负面以保守避免误判。用于情感分类计数前的极性裁决。

## Prompt

当一条评论同时包含正面与负面表述时，先判断哪一方为主导情感：若整体偏正面、仅有次要批评，判为 positive；若整体偏负面、仅有次要称赞，判为 negative；若正负大致均衡，默认判为 negative（保守策略，优先避免误判）。最终为每条混合评论输出唯一极性标签。

## Objective

为混合情感评论确定单一极性标签
## Applicable Signals

- 评论中同时出现正面与负面表述
- 下游计数任务要求每条评论只有一个极性标签

## Contraindications

- 评论情感单一明确
- 任务不涉及情感极性计数

## Intervention Moves

- 识别评论中的正面与负面成分
- 判断主导情感方向
- 正负均衡时按保守策略默认判为 negative
- 输出唯一极性标签

## Workflow Steps

- 检查评论是否同时包含正面与负面表述；若情感单一，直接按单一极性处理，不适用本规则。
- 若整体偏正面、仅有次要批评，判为 positive。
- 若整体偏负面、仅有次要称赞，判为 negative。
- 若正负大致均衡，默认判为 negative（保守策略）。
- 输出该评论的唯一极性标签（positive/negative）。

## Constraints

- 每条混合评论只能输出一个极性标签
- 均衡情形必须默认判为 negative
- 判定需基于评论中正负成分的相对主导性

## Cautions

- 显著问题（如耐用性缺陷）应视为重要负面信号，可能使整体判为 negative
- 保守默认负面可能低估正面倾向，需在均衡情形下才启用

## Output Contract

- 每条混合评论获得唯一极性标签（positive/negative）

## Example Therapist Responses

### Example 1

- Client/Input: 产品保暖又时尚，但洗几次后起球且价格过高
- Therapist/Output: negative
- Notes: 耐用性问题显著，整体判为负面

## Triggers

- 评论同时含正面与负面表述
- 需要为计数任务输出单一极性标签

## Examples

### Example 1

Input:

  产品保暖又时尚，但洗几次后起球且价格过高

Output:

  negative

Notes:

  耐用性问题显著，整体判为负面
