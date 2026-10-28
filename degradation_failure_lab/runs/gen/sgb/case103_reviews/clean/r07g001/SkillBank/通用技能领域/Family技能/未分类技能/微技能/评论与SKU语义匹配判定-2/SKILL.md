---
id: "02c2e1bc-0a5a-5949-8500-c461cc404d8f"
name: "评论与SKU语义匹配判定"
description: "判断单条用户评论与单个产品SKU描述之间是否存在概念性语义匹配（语义等价或相关），从而决定该评论是否适用于该SKU。用于将评论映射到产品目录条目时的匹配判定环节。"
version: "0.1.0"
tags:
  - "语义匹配"
  - "概念等价判断"
  - "评论映射"
  - "SKU"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "需要判断评论是否适用于某SKU"
  - "评论与SKU描述用词不同但概念可能相关"
  - "将评论映射到产品目录条目"
examples:
  - input: "评论：\"Love the moisture-wicking fabric on my workout shirts\"；SKU：\"Performance tee with Dri-FIT technology and quick-dry fabric\""
    output: "适用（概念匹配）：吸湿排汗与Dri-FIT/快干为语义等价概念"
    notes: "概念等价"
  - input: "评论：\"Oversized fit is perfect for streetwear style\"；SKU：\"Relaxed fit hoodie with dropped shoulders and extended length\""
    output: "适用（概念相关）：Oversized与relaxed fit加延长版型为相关概念"
    notes: "概念相关"
---

# 评论与SKU语义匹配判定

判断单条用户评论与单个产品SKU描述之间是否存在概念性语义匹配（语义等价或相关），从而决定该评论是否适用于该SKU。用于将评论映射到产品目录条目时的匹配判定环节。

## Prompt

针对每一条评论-SKU对，判断二者是否在概念层面语义等价或相关，而非仅做字面关键词匹配。若评论用词与SKU描述不同但表达同一或相关概念，判为适用并说明理由；若概念不相关，判为不适用。输出每条评论-SKU对的适用/不适用判定及简要理由。

## Objective

判定单条评论与单个SKU描述之间是否存在概念性语义匹配
## Applicable Signals

- 评论与SKU描述用词不同但概念可能相关
- 需要判断评论是否适用于某SKU

## Contraindications

- 仅需字面关键词匹配
- SKU目录未通过校验

## Intervention Moves

- 识别评论与SKU描述中的核心概念
- 判断概念是否语义等价或相关
- 给出适用/不适用判定并说明理由

## Workflow Steps

- 提取评论中的核心概念（如功能、版型、风格）
- 提取SKU描述中的对应概念
- 判断二者是否语义等价或相关
- 输出适用/不适用判定及理由

## Constraints

- 判定基于概念语义而非字面关键词
- 每条评论-SKU对需给出明确判定与理由

## Cautions

- 用词不同但概念相关时应判为适用，避免仅凭字面不匹配而误判为不适用

## Output Contract

- 对每条评论-SKU对给出适用/不适用的判定及理由

## Example Therapist Responses

### Example 1

- Client/Input: 评论："Love the moisture-wicking fabric on my workout shirts"；SKU："Performance tee with Dri-FIT technology and quick-dry fabric"
- Therapist/Output: 适用（概念匹配）：吸湿排汗与Dri-FIT/快干为语义等价概念
- Notes: 概念等价

### Example 2

- Client/Input: 评论："Oversized fit is perfect for streetwear style"；SKU："Relaxed fit hoodie with dropped shoulders and extended length"
- Therapist/Output: 适用（概念相关）：Oversized与relaxed fit加延长版型为相关概念
- Notes: 概念相关

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断评论是否适用于某SKU
- 评论与SKU描述用词不同但概念可能相关
- 将评论映射到产品目录条目

## Examples

### Example 1

Input:

  评论："Love the moisture-wicking fabric on my workout shirts"；SKU："Performance tee with Dri-FIT technology and quick-dry fabric"

Output:

  适用（概念匹配）：吸湿排汗与Dri-FIT/快干为语义等价概念

Notes:

  概念等价

### Example 2

Input:

  评论："Oversized fit is perfect for streetwear style"；SKU："Relaxed fit hoodie with dropped shoulders and extended length"

Output:

  适用（概念相关）：Oversized与relaxed fit加延长版型为相关概念

Notes:

  概念相关
