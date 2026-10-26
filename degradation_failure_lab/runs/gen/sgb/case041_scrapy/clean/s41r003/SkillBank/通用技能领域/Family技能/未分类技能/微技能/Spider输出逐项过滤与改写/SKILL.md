---
id: "bfdf8b93-b24f-554c-938a-3cbb450e6e08"
name: "Spider输出逐项过滤与改写"
description: "对spider输出或start seeds中的单个item/request进行逐项处理：保留原样、改写为不同对象，或返回None丢弃，从而实现输出过滤与转换。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider-middleware"
  - "output-filtering"
  - "item"
  - "request"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要过滤或改写spider产出的item"
  - "需要拦截或替换spider输出中的request"
  - "需要对start seeds中的item/request做逐项处理"
examples:
  - input: "spider输出中的单个item与对应response"
    output: "返回同一item（保留）、改写后的item，或None（丢弃）"
    notes: "response为None表示来自start seeds"
  - input: "spider输出中的单个request与对应response"
    output: "返回同一request（保留）、改写后的request，或None（丢弃）"
---

# Spider输出逐项过滤与改写

对spider输出或start seeds中的单个item/request进行逐项处理：保留原样、改写为不同对象，或返回None丢弃，从而实现输出过滤与转换。

## Prompt

当需要过滤或改写spider产出的item，或需要拦截/替换request时，使用本技能。对每个item或request单独做决策：返回同一对象表示保留，返回不同对象表示改写，返回None表示忽略该项。处理item时调用get_processed_item(item, response)，处理request时调用对应的request处理方法；response为None表示该项来自start seeds。

## Objective

逐项决定item/request的保留、改写或丢弃
## Applicable Signals

- spider输出中存在需要过滤的item
- spider输出中存在需要拦截或替换的request
- start seeds中的item/request需要逐项处理

## Contraindications

- 无需对spider输出做任何变更时不应使用

## Intervention Moves

- 对单个item调用get_processed_item(item, response)
- 对单个request调用对应的request处理方法
- 返回同一对象以保留
- 返回不同对象以改写
- 返回None以忽略该项

## Workflow Steps

- 接收来自spider输出或start seeds的单个item/request
- 判断该项应保留、改写还是丢弃
- 保留时返回原对象，改写时返回新对象，丢弃时返回None
- 对每个item/request重复上述逐项决策

## Constraints

- 每次只处理单个item或request
- response为None表示该项来自start seeds
- 返回值必须是item/request对象或None

## Cautions

- 改写时应返回新的有效对象，避免返回无效类型
- 返回None会静默丢弃该项，需确认丢弃符合预期

## Output Contract

- 返回相同或不同的item/request，或返回None表示忽略该项

## Example Therapist Responses

### Example 1

- Client/Input: spider输出中的单个item与对应response
- Therapist/Output: 返回同一item（保留）、改写后的item，或None（丢弃）
- Notes: response为None表示来自start seeds

### Example 2

- Client/Input: spider输出中的单个request与对应response
- Therapist/Output: 返回同一request（保留）、改写后的request，或None（丢弃）

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要过滤或改写spider产出的item
- 需要拦截或替换spider输出中的request
- 需要对start seeds中的item/request做逐项处理

## Examples

### Example 1

Input:

  spider输出中的单个item与对应response

Output:

  返回同一item（保留）、改写后的item，或None（丢弃）

Notes:

  response为None表示来自start seeds

### Example 2

Input:

  spider输出中的单个request与对应response

Output:

  返回同一request（保留）、改写后的request，或None（丢弃）
