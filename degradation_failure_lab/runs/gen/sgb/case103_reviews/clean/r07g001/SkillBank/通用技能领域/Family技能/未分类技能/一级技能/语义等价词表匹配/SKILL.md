---
id: "2397d849-24d7-57b6-afd2-4d85a98f6b06"
name: "语义等价词表匹配"
description: "使用语义等价词表判断产品属性描述与评论文本片段是否语义相近，为相似度判断提供参考依据；未命中等价组时标注不确定，不强行给出高置信判断。"
version: "0.1.0"
tags:
  - "语义匹配"
  - "等价词表"
  - "相似度判断"
  - "商品目录运营"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "需要判断两个属性描述是否语义等价"
  - "评论文本与产品属性需做近似匹配"
  - "需要基于等价表达做相似度判断"
examples:
  - input: "产品属性描述为 moisture-wicking，评论文本提到 quick-dry"
    output: "相似：二者属于同一等价组（moisture-wicking ≈ quick-dry ≈ sweat management）"
    notes: "依据词表已定义的等价关系"
  - input: "产品属性描述为 waterproof，评论文本提到 breathable"
    output: "不确定：词表未定义二者等价关系，不做高置信相似判断"
    notes: "未命中等价组时避免臆造"
---

# 语义等价词表匹配

使用语义等价词表判断产品属性描述与评论文本片段是否语义相近，为相似度判断提供参考依据；未命中等价组时标注不确定，不强行给出高置信判断。

## Prompt

当需要判断产品属性描述与评论文本是否语义等价时，参照语义等价词表进行匹配：先提取待比较的两个表达，在词表已定义的等价组中检索；若两者属于同一等价组，则判定为语义相近并注明所依据的等价关系；若未命中且无法从词表获得支持，则不做高置信相似判断，应标注为不确定或交由其他方法处理。本技能仅提供等价表达参考，不用于严格类别归属判断。

## Objective

提供语义等价表达参考以支持相似度判断
## Applicable Signals

- 待比较表达涉及功能性属性描述（如吸湿排汗、压缩贴合、轻量可收纳、保暖、防风）
- 评论文本用词与产品属性用词不同但可能指向同一概念

## Contraindications

- 需要严格类别归属判断
- 等价关系未在词表中定义且需高置信判断

## Intervention Moves

- 在等价词表中查找待比较表达所属的等价组
- 命中同一等价组则判定语义相近
- 未命中等价组则标注不确定，不强行给出高置信判断

## Workflow Steps

- 提取待比较的两个表达（产品属性描述与评论文本片段）
- 在语义等价词表中检索对应等价组
- 若两者属于同一等价组，输出相似判断并注明依据的等价关系
- 若未命中等价组，输出不确定或转交其他判断方法，避免高置信结论

## Constraints

- 仅依据词表中已定义的等价关系做判断
- 不得将等价词表用于类别归属等严格分类任务
- 词表未覆盖的表达不得臆造等价关系

## Cautions

- 部分等价关系依赖上下文（如保暖/隔热），需结合语境判断
- 等价词表为工作笔记性质，覆盖范围有限

## Output Contract

- 给出基于等价词表的相似/不相似判断，并注明所依据的等价关系；未命中时明确标注不确定。

## Example Therapist Responses

### Example 1

- Client/Input: 产品属性描述为 moisture-wicking，评论文本提到 quick-dry
- Therapist/Output: 相似：二者属于同一等价组（moisture-wicking ≈ quick-dry ≈ sweat management）
- Notes: 依据词表已定义的等价关系

### Example 2

- Client/Input: 产品属性描述为 waterproof，评论文本提到 breathable
- Therapist/Output: 不确定：词表未定义二者等价关系，不做高置信相似判断
- Notes: 未命中等价组时避免臆造

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断两个属性描述是否语义等价
- 评论文本与产品属性需做近似匹配
- 需要基于等价表达做相似度判断

## Examples

### Example 1

Input:

  产品属性描述为 moisture-wicking，评论文本提到 quick-dry

Output:

  相似：二者属于同一等价组（moisture-wicking ≈ quick-dry ≈ sweat management）

Notes:

  依据词表已定义的等价关系

### Example 2

Input:

  产品属性描述为 waterproof，评论文本提到 breathable

Output:

  不确定：词表未定义二者等价关系，不做高置信相似判断

Notes:

  未命中等价组时避免臆造
