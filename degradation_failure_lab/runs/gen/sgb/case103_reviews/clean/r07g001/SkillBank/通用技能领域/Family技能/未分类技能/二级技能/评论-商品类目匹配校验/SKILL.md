---
id: "cec8d08c-dd63-5fc9-b329-41264046ef35"
name: "评论-商品类目匹配校验"
description: "在将评论匹配到SKU前，先判定评论讨论的服装类目，并强制要求评论类目与SKU的category字段一致，否则不得匹配。用于判断某条评论是否适用于某SKU、且评论或SKU涉及服装类目归属的场景。"
version: "0.1.0"
tags:
  - "类目匹配"
  - "硬约束"
  - "评论-SKU匹配"
  - "匹配前校验"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "需要判断某条评论是否适用于某SKU"
  - "评论或SKU涉及服装类目归属"
  - "进入评论-SKU语义匹配前的类目校验环节"
examples:
  - input: "评论提及连帽衫的穿着体验，目标SKU的category为\"tops\""
    output: "评论类目=tops，与SKU类目一致，通过类目校验，允许匹配"
    notes: "上装类词汇映射到tops"
  - input: "评论提及慢跑裤的版型，目标SKU的category为\"outerwear\""
    output: "评论类目=bottoms，与SKU类目不一致，不通过类目校验，不得匹配"
    notes: "跨类目硬性拒绝"
---

# 评论-商品类目匹配校验

在将评论匹配到SKU前，先判定评论讨论的服装类目，并强制要求评论类目与SKU的category字段一致，否则不得匹配。用于判断某条评论是否适用于某SKU、且评论或SKU涉及服装类目归属的场景。

## Prompt

对每条待匹配评论，先分析其讨论的服装类型并判定类目，再与目标SKU的category字段比对。仅当两者类目一致时才允许进入后续匹配；类目不一致则直接判定为不适用，不得匹配。若无法判定评论类目，按不可匹配处理。

## Objective

防止跨类目错误匹配，保证评论只适用于同类目SKU
## Applicable Signals

- 评论提及上衣/衬衫/连帽衫/夹克等上装词汇
- 评论提及裤子/慢跑裤/短裤/紧身裤等下装词汇
- 评论提及外套/派克大衣/防风衣/背心等外套词汇
- SKU带有category字段需与评论类目比对

## Contraindications

- 评论未涉及任何服装类目信息且无法判定
- 任务不涉及评论与SKU匹配

## Intervention Moves

- 分析评论讨论的服装类型以判定其类目
- 将评论类目与SKU的category字段比对
- 类目一致则放行进入匹配，不一致则判定不适用

## Workflow Steps

- 读取待匹配评论内容，识别其讨论的服装类型
- 依据类目映射判定评论类目：上装类词汇→tops；下装类词汇→bottoms；外套类词汇→outerwear
- 读取目标SKU的category字段
- 比对评论类目与SKU类目是否一致
- 一致则通过类目校验并允许后续匹配；不一致或无法判定则判定为不适用，不得匹配

## Constraints

- 类目一致性为硬性要求，不满足即不得匹配
- 评论类目判定须基于评论实际讨论的服装类型，不得凭相似度推断
- 类目映射：tops对应上衣/衬衫/连帽衫/夹克；bottoms对应裤子/慢跑裤/短裤/紧身裤；outerwear对应外套/派克大衣/防风衣/背心

## Cautions

- 评论可能提及多种服装类型，需判定其主要讨论的类目
- 无法判定评论类目时应保守处理为不可匹配

## Output Contract

- 输出评论类目判定结果及是否通过类目一致性校验的结论（通过/不通过），不通过时不得进入匹配。

## Example Therapist Responses

### Example 1

- Client/Input: 评论提及连帽衫的穿着体验，目标SKU的category为"tops"
- Therapist/Output: 评论类目=tops，与SKU类目一致，通过类目校验，允许匹配
- Notes: 上装类词汇映射到tops

### Example 2

- Client/Input: 评论提及慢跑裤的版型，目标SKU的category为"outerwear"
- Therapist/Output: 评论类目=bottoms，与SKU类目不一致，不通过类目校验，不得匹配
- Notes: 跨类目硬性拒绝

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断某条评论是否适用于某SKU
- 评论或SKU涉及服装类目归属
- 进入评论-SKU语义匹配前的类目校验环节

## Examples

### Example 1

Input:

  评论提及连帽衫的穿着体验，目标SKU的category为"tops"

Output:

  评论类目=tops，与SKU类目一致，通过类目校验，允许匹配

Notes:

  上装类词汇映射到tops

### Example 2

Input:

  评论提及慢跑裤的版型，目标SKU的category为"outerwear"

Output:

  评论类目=bottoms，与SKU类目不一致，不通过类目校验，不得匹配

Notes:

  跨类目硬性拒绝
