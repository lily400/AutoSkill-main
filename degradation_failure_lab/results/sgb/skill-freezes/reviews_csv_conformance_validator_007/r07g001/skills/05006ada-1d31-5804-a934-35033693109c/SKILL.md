---
id: "05006ada-1d31-5804-a934-35033693109c"
name: "评论分类字段判定"
description: "对每条评论文本逐条判定是否为运动服饰、是否为服装产品以及品牌归属（nike/competitor/n/a），产出符合取值约束的结构化分类字段。适用于已有可解析评论文本、需要为每条评论打上分类标签的场景。"
version: "0.1.0"
tags:
  - "评论分类"
  - "语义判定"
  - "结构化输出"
  - "运营流程"
triggers:
  - "已有评论文本需要打上运动服饰/服装/品牌标签"
  - "需要为每条评论生成结构化分类字段"
---

# 评论分类字段判定

对每条评论文本逐条判定是否为运动服饰、是否为服装产品以及品牌归属（nike/competitor/n/a），产出符合取值约束的结构化分类字段。适用于已有可解析评论文本、需要为每条评论打上分类标签的场景。

## Prompt

逐条读取评论文本，对每条评论分别判定三个分类字段：is_sportswear（仅 yes/no）、is_apparel_product（仅 yes/no）、competitor_or_nike（仅 nike/competitor/n/a）。严格使用允许取值，不臆造标签；对无法判定的品牌归属使用 n/a。输出为逐条对应的分类字段，供后续 CSV 组装与校验使用。

## Objective

为每条评论生成合规的分类标签
## Applicable Signals

- 评论文本已提供且可解析
- 需要逐条输出 is_sportswear、is_apparel_product、competitor_or_nike 字段

## Contraindications

- 评论缺失或无法解析
- 仅需计数统计无需逐条分类

## Intervention Moves

- 逐条读取评论文本
- 判定是否为运动服饰并赋 yes/no
- 判定是否为服装产品并赋 yes/no
- 判定品牌归属并赋 nike/competitor/n/a
- 对无法判定品牌归属的评论赋 n/a

## Workflow Steps

- 确认评论文本可解析且逐条可读
- 对每条评论判定 is_sportswear，取值仅限 yes 或 no
- 对每条评论判定 is_apparel_product，取值仅限 yes 或 no
- 对每条评论判定 competitor_or_nike，取值仅限 nike、competitor 或 n/a
- 输出每条评论对应的三个分类字段

## Constraints

- is_sportswear 仅允许 yes 或 no
- is_apparel_product 仅允许 yes 或 no
- competitor_or_nike 仅允许 nike、competitor 或 n/a
- 不得输出允许取值之外的标签

## Cautions

- 品牌归属无法判定时使用 n/a，不得强行归类
- 分类结果需与评论逐条对应，避免错位

## Output Contract

- 每条评论对应的 is_sportswear、is_apparel_product、competitor_or_nike 字段值，取值符合允许集合，可供后续 CSV 组装与校验使用。

## Triggers

- 已有评论文本需要打上运动服饰/服装/品牌标签
- 需要为每条评论生成结构化分类字段
