---
id: "19fd8d56-4789-5286-b8c0-cd0bd0f60cc5"
name: "按SKU生成四类情感计数并输出JSON"
description: "基于产品目录与已处理评论，为每个SKU统计四类情感计数，并输出固定长度JSON数组及含评论统计的SUCCESS状态消息。适用于已提供产品目录与评论数据、需要按SKU交付情感计数的场景。"
version: "0.1.0"
tags:
  - "情感计数"
  - "按SKU聚合"
  - "JSON输出"
  - "运营数据处理"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "已提供product_catalog.json与processed_reviews.csv"
  - "需要按SKU输出四类情感计数"
  - "需要交付固定长度JSON数组与SUCCESS状态消息"
examples:
  - input: "已提供product_catalog.json与processed_reviews.csv，需按SKU输出四类情感计数"
    output: "JSON数组（每个SKU一个对象，含sku_id与四个整数计数字段）及含评论统计的SUCCESS状态消息"
    notes: "输入不完美时在状态消息中注明但仍交付计数"
---

# 按SKU生成四类情感计数并输出JSON

基于产品目录与已处理评论，为每个SKU统计四类情感计数，并输出固定长度JSON数组及含评论统计的SUCCESS状态消息。适用于已提供产品目录与评论数据、需要按SKU交付情感计数的场景。

## Prompt

读取产品目录与已处理评论数据，按SKU分组统计四类情感计数，输出固定长度JSON数组（每个SKU一个对象，含sku_id与四个整数计数字段），并附标准SUCCESS状态消息及评论统计。若输入存在瑕疵，在状态消息中说明但仍需完成计数交付。

## Objective

为每个SKU产出四类情感整数计数并交付标准JSON与状态消息
## Applicable Signals

- 已提供product_catalog.json与processed_reviews.csv
- 需要按SKU输出四类情感计数
- 需要固定长度JSON数组交付

## Contraindications

- 缺少产品目录或评论数据
- 需要主观语义判断而非计数

## Intervention Moves

- 读取产品目录确定SKU清单
- 读取已处理评论并按SKU分组
- 对每个SKU统计四类情感计数
- 组装固定长度JSON数组
- 生成含评论统计的SUCCESS状态消息

## Workflow Steps

- 校验product_catalog.json与processed_reviews.csv是否可用
- 从产品目录提取SKU清单
- 按SKU对已处理评论分组
- 统计每个SKU的四类情感整数计数
- 输出每个SKU一个对象的JSON数组（含sku_id与四个整数计数字段）
- 生成标准SUCCESS状态消息并附评论统计
- 若输入不完美，在状态消息中注明但仍完成交付

## Constraints

- JSON数组长度须与SKU数量一致（每个SKU一个对象）
- 计数字段须为整数
- 即使输入存在瑕疵也需完成计数交付并在状态中说明

## Cautions

- 输入不完美时不得静默忽略，须在状态消息中注明
- 避免将主观语义判断混入计数流程

## Output Contract

- 含每个SKU一个对象的JSON数组（sku_id与四个整数计数字段）及带评论统计的SUCCESS状态消息

## Example Therapist Responses

### Example 1

- Client/Input: 已提供product_catalog.json与processed_reviews.csv，需按SKU输出四类情感计数
- Therapist/Output: JSON数组（每个SKU一个对象，含sku_id与四个整数计数字段）及含评论统计的SUCCESS状态消息
- Notes: 输入不完美时在状态消息中注明但仍交付计数

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 已提供product_catalog.json与processed_reviews.csv
- 需要按SKU输出四类情感计数
- 需要交付固定长度JSON数组与SUCCESS状态消息

## Examples

### Example 1

Input:

  已提供product_catalog.json与processed_reviews.csv，需按SKU输出四类情感计数

Output:

  JSON数组（每个SKU一个对象，含sku_id与四个整数计数字段）及含评论统计的SUCCESS状态消息

Notes:

  输入不完美时在状态消息中注明但仍交付计数
