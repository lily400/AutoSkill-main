---
id: "555ffad0-26e3-5408-a321-ea0963dca8e6"
name: "评论子集筛选与品牌分组"
description: "从已分类评论CSV中按 is_sportswear=\"yes\" 且 is_apparel_product=\"yes\" 过滤，再按 competitor_or_nike 拆分为 Nike 与竞品两个子集，用于后续情感或计数分析前的数据准备。"
version: "0.1.0"
tags:
  - "评论数据预处理"
  - "条件过滤"
  - "分组"
  - "数据准备"
triggers:
  - "已有含 is_sportswear、is_apparel_product、competitor_or_nike 列的评论CSV"
  - "需要分别分析 Nike 与竞品评论"
examples:
  - input: "已分类评论CSV，含 is_sportswear、is_apparel_product、competitor_or_nike 列"
    output: "Nike 子集（is_sportswear=yes 且 is_apparel_product=yes 且 competitor_or_nike=nike）与竞品子集（同过滤条件且 competitor_or_nike=competitor）"
    notes: "competitor_or_nike=n/a 的行被排除"
---

# 评论子集筛选与品牌分组

从已分类评论CSV中按 is_sportswear="yes" 且 is_apparel_product="yes" 过滤，再按 competitor_or_nike 拆分为 Nike 与竞品两个子集，用于后续情感或计数分析前的数据准备。

## Prompt

接收已分类评论CSV，先校验所需列存在，再按 is_sportswear="yes" 且 is_apparel_product="yes" 过滤，最后按 competitor_or_nike 拆分为 Nike 子集与竞品子集并输出。

## Objective

生成符合条件且按品牌归属分组的评论子集
## Applicable Signals

- 输入为 review_processor 输出的已分类评论CSV
- CSV 含 review_id、review、is_sportswear、is_apparel_product、brand、competitor_or_nike 列
- 下游需要 Nike 与竞品两个独立子集

## Contraindications

- 输入缺少所需分类列
- 尚未完成评论分类

## Intervention Moves

- 校验所需分类列是否存在
- 按 is_sportswear="yes" 且 is_apparel_product="yes" 过滤
- 按 competitor_or_nike 拆分为 nike 与 competitor 两个子集

## Workflow Steps

- 读取已分类评论CSV，确认包含 is_sportswear、is_apparel_product、competitor_or_nike 列
- 过滤保留 is_sportswear="yes" 且 is_apparel_product="yes" 的行
- 在过滤结果中按 competitor_or_nike="nike" 提取 Nike 子集
- 在过滤结果中按 competitor_or_nike="competitor" 提取竞品子集
- 输出两个子集供后续情感或计数分析使用

## Constraints

- 过滤条件必须同时满足 is_sportswear="yes" 与 is_apparel_product="yes"
- 分组仅依据 competitor_or_nike 列的 nike 与 competitor 取值

## Cautions

- competitor_or_nike 为 "n/a" 的行不进入任一子集
- 缺少所需列时应停止并报告，而非猜测补全

## Output Contract

- 两个过滤后的评论子集（Nike 与竞品），均满足 is_sportswear="yes" 且 is_apparel_product="yes"，并分别对应 competitor_or_nike="nike" 与 "competitor"。

## Example Therapist Responses

### Example 1

- Client/Input: 已分类评论CSV，含 is_sportswear、is_apparel_product、competitor_or_nike 列
- Therapist/Output: Nike 子集（is_sportswear=yes 且 is_apparel_product=yes 且 competitor_or_nike=nike）与竞品子集（同过滤条件且 competitor_or_nike=competitor）
- Notes: competitor_or_nike=n/a 的行被排除

## Triggers

- 已有含 is_sportswear、is_apparel_product、competitor_or_nike 列的评论CSV
- 需要分别分析 Nike 与竞品评论

## Examples

### Example 1

Input:

  已分类评论CSV，含 is_sportswear、is_apparel_product、competitor_or_nike 列

Output:

  Nike 子集（is_sportswear=yes 且 is_apparel_product=yes 且 competitor_or_nike=nike）与竞品子集（同过滤条件且 competitor_or_nike=competitor）

Notes:

  competitor_or_nike=n/a 的行被排除
