---
id: "51f5a8db-c4dd-53b6-9943-d8f3f4098fdc"
name: "多SKU语义匹配计数"
description: "将每条评论与产品目录做语义匹配，当一条评论可匹配多个 SKU 时分别计入各 SKU，避免漏计，最终产出每 SKU 评论计数 JSON 及简要状态说明。"
version: "0.1.0"
tags:
  - "语义匹配"
  - "计数汇总"
  - "多SKU"
  - "数据运营"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "需要按 SKU 统计评论提及量"
  - "评论可能同时提及多个商品"
  - "需要输出每 SKU 计数结果"
examples:
  - input: "一条评论同时提及连帽衫与运动裤，二者均与产品目录中的不同 SKU 语义匹配。"
    output: "该评论分别计入连帽衫对应 SKU 与运动裤对应 SKU 的计数，各加一。"
    notes: "体现多 SKU 匹配分别计入、避免漏计。"
---

# 多SKU语义匹配计数

将每条评论与产品目录做语义匹配，当一条评论可匹配多个 SKU 时分别计入各 SKU，避免漏计，最终产出每 SKU 评论计数 JSON 及简要状态说明。

## Prompt

对每条评论逐一与产品目录做语义匹配：若评论语义上匹配多个 SKU，则每个匹配的 SKU 各计一次，不得因单条评论只计一次而漏计。仅依据评论文本与目录的语义对应关系计数，不从未提供的字段推断分类值。完成后输出每 SKU 计数 JSON，并附简要状态说明；若存在阻塞（如必需字段缺失），明确说明以便快速补救。

## Objective

产出准确的每 SKU 评论计数
## Applicable Signals

- 评论文本可能同时提及多个商品（如连帽衫与运动裤同帖）
- 需要按 SKU 维度而非仅品牌维度汇总
- 存在产品目录可供语义比对

## Contraindications

- 评论与产品目录无对应关系
- 仅需品牌层面汇总

## Intervention Moves

- 逐条评论与产品目录做语义匹配
- 对匹配多个 SKU 的评论分别计入各 SKU
- 汇总每 SKU 计数并输出 JSON
- 附简要状态说明并明确阻塞项

## Workflow Steps

- 确认产品目录与评论数据可用，检查必需字段是否齐全
- 逐条评论与产品目录做语义匹配，识别所有语义对应的 SKU
- 对匹配多个 SKU 的评论，分别计入每个匹配 SKU，避免漏计
- 汇总生成每 SKU 计数 JSON
- 撰写简要状态说明，若存在阻塞则明确列出

## Constraints

- 不得因单条评论只计一次而漏计多 SKU 匹配
- 不得从未提供的字段推断分类值
- 必需字段缺失时应请求修正后的输入，而非继续处理不完整分类字段

## Cautions

- 评论可能同时提及多个商品，需防止漏计
- 若分类字段缺失，应明确报告阻塞而非自行推断

## Output Contract

- 每 SKU 计数的 JSON 及简要状态说明；若存在阻塞，需清晰说明阻塞项以便快速补救。

## Example Therapist Responses

### Example 1

- Client/Input: 一条评论同时提及连帽衫与运动裤，二者均与产品目录中的不同 SKU 语义匹配。
- Therapist/Output: 该评论分别计入连帽衫对应 SKU 与运动裤对应 SKU 的计数，各加一。
- Notes: 体现多 SKU 匹配分别计入、避免漏计。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要按 SKU 统计评论提及量
- 评论可能同时提及多个商品
- 需要输出每 SKU 计数结果

## Examples

### Example 1

Input:

  一条评论同时提及连帽衫与运动裤，二者均与产品目录中的不同 SKU 语义匹配。

Output:

  该评论分别计入连帽衫对应 SKU 与运动裤对应 SKU 的计数，各加一。

Notes:

  体现多 SKU 匹配分别计入、避免漏计。
