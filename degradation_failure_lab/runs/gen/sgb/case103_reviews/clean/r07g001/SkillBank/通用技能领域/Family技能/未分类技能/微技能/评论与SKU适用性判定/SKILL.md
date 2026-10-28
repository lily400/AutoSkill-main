---
id: "48691e88-23cd-542f-8180-3a558c1ccf5c"
name: "评论与SKU适用性判定"
description: "判断单条评论是否适用于某个SKU：先核对评论讨论的产品类别与SKU类别是否一致，再判断评论中提到的属性是否与SKU的silhouette_description语义匹配；两个条件同时满足才判定为适用。用于将评论匹配到具体SKU的场景。"
version: "0.1.0"
tags:
  - "评论匹配"
  - "SKU适用性"
  - "类别过滤"
  - "语义相似度"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "需要判断某条评论能否用于某个SKU"
  - "已有评论文本与SKU的silhouette_description"
  - "需要将评论匹配到具体SKU"
examples:
  - input: "评论讨论上衣类产品的版型与剪裁，SKU类别为tops，silhouette_description描述相应版型特征"
    output: "适用：true；依据：类别一致（tops），且评论属性与silhouette_description语义匹配"
    notes: "两个条件同时满足"
  - input: "评论讨论裤装，SKU类别为outerwear"
    output: "适用：false；依据：产品类别不一致"
    notes: "类别不一致直接判定不适用"
---

# 评论与SKU适用性判定

判断单条评论是否适用于某个SKU：先核对评论讨论的产品类别与SKU类别是否一致，再判断评论中提到的属性是否与SKU的silhouette_description语义匹配；两个条件同时满足才判定为适用。用于将评论匹配到具体SKU的场景。

## Prompt

对给定的单条评论与单个SKU执行适用性判定。步骤：1) 确认SKU类别（tops、bottoms或outerwear）与silhouette_description均可用；2) 判断评论讨论的产品类别是否与SKU类别一致，不一致则直接判定不适用；3) 类别一致时，将评论中提到的属性与SKU的silhouette_description进行语义匹配判断；4) 仅当类别一致且属性语义匹配两个条件同时满足时，判定为适用；5) 输出布尔判定及简要依据。

## Objective

判定单条评论对单个SKU的适用性
## Applicable Signals

- 输入包含单条评论文本
- 输入包含SKU类别与silhouette_description
- 任务要求给出评论对SKU是否适用的结论

## Contraindications

- 缺少SKU类别或silhouette_description
- 评论与商品无关或为无效输入

## Intervention Moves

- 核对评论讨论的产品类别与SKU类别是否一致
- 类别一致时将评论属性与silhouette_description做语义匹配
- 两条件同时满足才判定适用
- 输出布尔判定及依据

## Workflow Steps

- 确认SKU类别（tops、bottoms或outerwear）与silhouette_description可用
- 判断评论讨论的产品类别是否与SKU类别一致，不一致则判定不适用
- 类别一致时，判断评论中提到的属性是否与silhouette_description语义匹配
- 仅当两个条件同时满足时判定为适用
- 输出布尔判定及简要依据

## Constraints

- 适用判定必须同时满足类别一致与属性语义匹配两个条件
- 类别不一致时无需进行语义匹配，直接判定不适用

## Cautions

- 语义匹配为判断性要求，需基于silhouette_description而非主观偏好
- 输入缺失或无效时不应强行给出判定

## Output Contract

- 输出该评论对该SKU是否适用的布尔判定及依据（类别一致性与属性语义匹配的说明）。

## Example Therapist Responses

### Example 1

- Client/Input: 评论讨论上衣类产品的版型与剪裁，SKU类别为tops，silhouette_description描述相应版型特征
- Therapist/Output: 适用：true；依据：类别一致（tops），且评论属性与silhouette_description语义匹配
- Notes: 两个条件同时满足

### Example 2

- Client/Input: 评论讨论裤装，SKU类别为outerwear
- Therapist/Output: 适用：false；依据：产品类别不一致
- Notes: 类别不一致直接判定不适用

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断某条评论能否用于某个SKU
- 已有评论文本与SKU的silhouette_description
- 需要将评论匹配到具体SKU

## Examples

### Example 1

Input:

  评论讨论上衣类产品的版型与剪裁，SKU类别为tops，silhouette_description描述相应版型特征

Output:

  适用：true；依据：类别一致（tops），且评论属性与silhouette_description语义匹配

Notes:

  两个条件同时满足

### Example 2

Input:

  评论讨论裤装，SKU类别为outerwear

Output:

  适用：false；依据：产品类别不一致

Notes:

  类别不一致直接判定不适用
