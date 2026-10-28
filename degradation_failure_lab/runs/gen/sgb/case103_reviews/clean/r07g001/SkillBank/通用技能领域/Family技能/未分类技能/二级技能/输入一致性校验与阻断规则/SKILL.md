---
id: "15b74fb7-f677-5822-a5fc-fcbe81d32338"
name: "输入一致性校验与阻断规则"
description: "在分析前校验产品目录类别是否仅限 tops/bottoms/outerwear 且目录完整、评审 CSV 列是否齐全；不满足约定时明确阻断并说明所需修复，而不是继续分析。"
version: "0.1.0"
tags:
  - "输入校验"
  - "合规守卫"
  - "数据完整性"
  - "阻断规则"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "下游依赖严格输入一致性"
  - "产品目录类别或评审 CSV 列可能不符合约定"
  - "目录可能不完整或存在未纳入的新增对象"
examples:
  - input: "目录中某外层单品类别被标为 jackets，且评审 CSV 缺少一列。"
    output: "阻断：类别 jackets 不在 tops/bottoms/outerwear 内；评审 CSV 缺少约定列。所需修复：将类别规范为 outerwear，补齐缺失列后重新提交。"
    notes: "阻断需逐项列出问题与修复要求"
---

# 输入一致性校验与阻断规则

在分析前校验产品目录类别是否仅限 tops/bottoms/outerwear 且目录完整、评审 CSV 列是否齐全；不满足约定时明确阻断并说明所需修复，而不是继续分析。

## Prompt

作为分析前的合规守卫：先检查产品目录（JSON）中每个对象的类别字段是否仅取 tops/bottoms/outerwear，并确认目录完整（无缺失对象）；再检查评审 CSV 是否包含约定列。任一条件不满足时，停止分析并输出明确的阻断说明，列出具体不符合项及所需修复；全部通过时输出通过结论，允许进入分析。

## Objective

确保下游依赖的输入严格符合约定格式与完整性
## Applicable Signals

- 下游明确要求严格输入一致性
- 目录类别字段出现约定外取值（如以 jackets 代替 outerwear）
- 评审 CSV 可能缺少列
- 目录对象数量与预期不一致

## Contraindications

- 已明确允许标注假设并继续分析
- 输入已通过校验

## Intervention Moves

- 逐项校验目录类别取值是否属于 tops/bottoms/outerwear
- 核对目录完整性（对象数量与预期一致）
- 核对评审 CSV 列是否齐全
- 对不符合项输出阻断说明与所需修复

## Workflow Steps

- 读取产品目录 JSON 与评审 CSV
- 校验目录类别字段仅取 tops/bottoms/outerwear
- 校验目录完整性
- 校验评审 CSV 列齐全
- 若全部通过，输出通过结论并放行分析
- 若存在不符合项，输出阻断说明，逐项列出问题与所需修复

## Constraints

- 类别仅允许 tops/bottoms/outerwear
- 目录须完整后方可分析
- 评审 CSV 须包含约定列

## Cautions

- 不得因业务方要求“先出信号”而跳过校验
- 不得自行将约定外类别静默改写为合规类别

## Output Contract

- 通过校验的结论，或明确的阻断说明及所需修复清单

## Example Therapist Responses

### Example 1

- Client/Input: 目录中某外层单品类别被标为 jackets，且评审 CSV 缺少一列。
- Therapist/Output: 阻断：类别 jackets 不在 tops/bottoms/outerwear 内；评审 CSV 缺少约定列。所需修复：将类别规范为 outerwear，补齐缺失列后重新提交。
- Notes: 阻断需逐项列出问题与修复要求

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 下游依赖严格输入一致性
- 产品目录类别或评审 CSV 列可能不符合约定
- 目录可能不完整或存在未纳入的新增对象

## Examples

### Example 1

Input:

  目录中某外层单品类别被标为 jackets，且评审 CSV 缺少一列。

Output:

  阻断：类别 jackets 不在 tops/bottoms/outerwear 内；评审 CSV 缺少约定列。所需修复：将类别规范为 outerwear，补齐缺失列后重新提交。

Notes:

  阻断需逐项列出问题与修复要求
