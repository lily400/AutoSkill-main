---
id: "a94f2864-b63a-5846-89f5-7c5ef080e3a7"
name: "输入数据质量校验与阻断"
description: "在进入下游处理前，对商品目录JSON与评论CSV执行数据质量门控：校验可解析性、字段完整性、类别合法性与分类取值约束；无效输入阻断并上报，低量输入告警后继续。用于数据接入阶段的质量门控。"
version: "0.1.0"
tags:
  - "数据质量"
  - "输入校验"
  - "门控"
  - "阻断上报"
  - "数据接入"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "开始处理目录或评论数据前"
  - "需要判断输入是否可继续下游流程"
  - "数据接入阶段的质量门控"
examples:
  - input: "目录JSON无法解析"
    output: "阻断：目录JSON解析失败，已上报编排方"
    notes: "无效输入必须阻断"
  - input: "评论CSV有效但某子集仅8条"
    output: "告警：子集数据量偏低（8条），继续处理"
    notes: "低量告警后继续"
---

# 输入数据质量校验与阻断

在进入下游处理前，对商品目录JSON与评论CSV执行数据质量门控：校验可解析性、字段完整性、类别合法性与分类取值约束；无效输入阻断并上报，低量输入告警后继续。用于数据接入阶段的质量门控。

## Prompt

作为数据接入阶段的质量门控执行者，按以下顺序校验输入：
1. 校验目录JSON可解析，且数组长度符合预期（如50条）。
2. 逐条校验SKU字段齐全，且category取值属于允许集合（tops、bottoms、outerwear）。
3. 校验评论CSV可解析，必需列齐全，分类取值严格受限于约定取值。
4. 任一输入无效时，阻断下游流程，并向编排方上报明确状态与问题说明。
5. 输入有效但任一子集数据量偏低（如少于10条）时，发出告警并继续。
仅执行校验与门控判断，不进行语义匹配或分类判断。

## Objective

确保输入数据合法完整，非法输入被阻断并上报
## Applicable Signals

- 开始处理目录或评论数据前
- 需要判断输入是否可继续下游流程

## Contraindications

- 数据已通过校验且无需重复检查
- 仅做语义判断不涉及输入合法性

## Intervention Moves

- 校验目录JSON可解析且数组长度符合预期
- 逐条校验SKU字段齐全且category属于允许集合
- 校验评论CSV可解析、必需列齐全、分类取值严格受限
- 无效输入时阻断并上报明确状态与问题说明
- 低量输入时告警并继续

## Workflow Steps

- 校验目录JSON可解析，数组长度符合预期
- 逐条校验SKU字段齐全，category ∈ {tops, bottoms, outerwear}
- 校验评论CSV可解析，必需列齐全，分类取值严格受限
- 任一输入无效则阻断并上报编排方，附明确状态与问题说明
- 输入有效但任一子集数据量偏低（如少于10条）则告警并继续

## Constraints

- 类别取值必须严格属于允许集合
- 分类取值必须严格受限于约定取值
- 无效输入必须阻断，不得静默继续
- 低量仅告警，不阻断

## Cautions

- 不得将低量告警误判为阻断
- 不得在未完成校验前放行下游流程

## Output Contract

- 输出通过/阻断状态及问题说明，或低量告警

## Example Therapist Responses

### Example 1

- Client/Input: 目录JSON无法解析
- Therapist/Output: 阻断：目录JSON解析失败，已上报编排方
- Notes: 无效输入必须阻断

### Example 2

- Client/Input: 评论CSV有效但某子集仅8条
- Therapist/Output: 告警：子集数据量偏低（8条），继续处理
- Notes: 低量告警后继续

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 开始处理目录或评论数据前
- 需要判断输入是否可继续下游流程
- 数据接入阶段的质量门控

## Examples

### Example 1

Input:

  目录JSON无法解析

Output:

  阻断：目录JSON解析失败，已上报编排方

Notes:

  无效输入必须阻断

### Example 2

Input:

  评论CSV有效但某子集仅8条

Output:

  告警：子集数据量偏低（8条），继续处理

Notes:

  低量告警后继续
