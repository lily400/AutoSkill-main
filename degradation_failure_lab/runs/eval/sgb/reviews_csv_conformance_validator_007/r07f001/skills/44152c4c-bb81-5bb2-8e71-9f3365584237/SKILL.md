---
id: "44152c4c-bb81-5bb2-8e71-9f3365584237"
name: "产品描述品类归类"
description: "根据产品描述中的关键词，将商品归入上装、下装或外套等品类，用于SKU匹配前的品类判定。"
version: "0.1.0"
tags:
  - "商品分类"
  - "关键词规则匹配"
  - "品类判定"
  - "SKU匹配前置"
triggers:
  - "需要从产品描述确定品类"
  - "进入SKU匹配前的分类步骤"
examples:
  - input: "Men's fleece pullover hoodie"
    output: "上装"
    notes: "命中连帽衫/套头衫关键词"
  - input: "Men's windbreaker jacket"
    output: "外套"
    notes: "命中防风衣/夹克关键词"
---

# 产品描述品类归类

根据产品描述中的关键词，将商品归入上装、下装或外套等品类，用于SKU匹配前的品类判定。

## Prompt

读取产品描述文本，按关键词规则判定品类：上装（连帽衫、T恤、长袖、卫衣、套头衫、球衣）；下装（长裤、束脚裤、短裤、紧身裤、打底裤、运动裤）；外套（夹克、防风衣、派克大衣、马甲、教练夹克）。输出单一品类标签；若描述中无可识别品类关键词，标记为无法判定并说明原因，不臆测。

## Objective

从产品描述文本判定产品所属品类
## Applicable Signals

- 产品描述文本已提供
- 流程处于SKU匹配前的分类步骤

## Contraindications

- 描述缺少可识别品类关键词
- 需要主观审美判断而非品类归类

## Intervention Moves

- 扫描描述中的品类关键词
- 按上装/下装/外套关键词表归类
- 输出单一品类标签

## Workflow Steps

- 读取产品描述文本
- 对照品类关键词表：上装=连帽衫、T恤、长袖、卫衣、套头衫、球衣；下装=长裤、束脚裤、短裤、紧身裤、打底裤、运动裤；外套=夹克、防风衣、派克大衣、马甲、教练夹克
- 确定唯一品类标签
- 若无可识别关键词，标记无法判定并说明原因

## Constraints

- 仅依据描述中的关键词判定，不引入外部信息
- 输出单一品类标签，不输出多个并列品类

## Cautions

- 描述可能同时含多个品类词，需以主体商品为准
- 关键词缺失时不得臆测品类

## Output Contract

- 输出产品品类标签（上装/下装/外套），或标记无法判定并附原因。

## Example Therapist Responses

### Example 1

- Client/Input: Men's fleece pullover hoodie
- Therapist/Output: 上装
- Notes: 命中连帽衫/套头衫关键词

### Example 2

- Client/Input: Men's windbreaker jacket
- Therapist/Output: 外套
- Notes: 命中防风衣/夹克关键词

## Triggers

- 需要从产品描述确定品类
- 进入SKU匹配前的分类步骤

## Examples

### Example 1

Input:

  Men's fleece pullover hoodie

Output:

  上装

Notes:

  命中连帽衫/套头衫关键词

### Example 2

Input:

  Men's windbreaker jacket

Output:

  外套

Notes:

  命中防风衣/夹克关键词
