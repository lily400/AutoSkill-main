---
id: "5f68eb1c-4e17-5d4f-9cd8-ca06e2efa98c"
name: "评论子集筛选与品牌分组"
description: "从已处理的评论CSV中筛选同时满足运动装与服装产品标记的记录，并按品牌归属（Nike 与竞品）分成两组，供后续逐SKU分析使用。"
version: "0.1.0"
tags:
  - "评论分析"
  - "数据筛选"
  - "分组"
  - "数据准备"
triggers:
  - "已有处理后的评论CSV且含 is_sportswear、is_apparel_product、competitor_or_nike 字段"
  - "需要为后续SKU分析准备品牌分组子集"
---

# 评论子集筛选与品牌分组

从已处理的评论CSV中筛选同时满足运动装与服装产品标记的记录，并按品牌归属（Nike 与竞品）分成两组，供后续逐SKU分析使用。

## Prompt

在已处理的评论CSV上执行条件过滤与分组：先保留 is_sportswear="yes" 且 is_apparel_product="yes" 的记录，再按 competitor_or_nike 字段拆分为 Nike 组（"nike"）与竞品组（"competitor"），输出两个分组子集供后续SKU分析。

## Objective

从评论数据中构建按品牌分组的运动服装子集
## Applicable Signals

- 评论数据已预处理并带有品类与品牌归属标记字段
- 下游任务需要按品牌分组的运动服装评论子集

## Contraindications

- 原始数据缺少所需标记字段
- 目标不是运动服装品类

## Intervention Moves

- 按 is_sportswear="yes" 与 is_apparel_product="yes" 做交集过滤
- 按 competitor_or_nike 字段拆分为 Nike 组与竞品组

## Workflow Steps

- 确认评论CSV包含 is_sportswear、is_apparel_product、competitor_or_nike 字段
- 筛选 is_sportswear="yes" 且 is_apparel_product="yes" 的记录形成子集
- 将子集按 competitor_or_nike="nike" 与 "competitor" 拆分为两组
- 输出两个分组子集供后续逐SKU分析

## Constraints

- 两个过滤条件必须同时满足（AND）
- 分组仅依据 competitor_or_nike 字段取值

## Cautions

- 若字段缺失或取值不规范，应先校验数据而非强行分组

## Output Contract

- 两个分组后的评论子集：Nike 组与竞品组，可直接用于后续逐SKU分析。

## Triggers

- 已有处理后的评论CSV且含 is_sportswear、is_apparel_product、competitor_or_nike 字段
- 需要为后续SKU分析准备品牌分组子集
