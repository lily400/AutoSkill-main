---
id: "640822ef-e871-5fb8-8c7c-7e73290e410f"
name: "SKU竞品与情感计数更新"
description: "对单个已通过校验的SKU，依据其competitor_or_nike归属与情感极性，将对应的竞品/情感组合计数器加一；用于多SKU循环统计中的原子计数步骤。"
version: "0.1.0"
tags:
  - "计数统计"
  - "SKU"
  - "情感分类"
  - "竞品归属"
  - "微技能"
triggers:
  - "已获得单个SKU的competitor_or_nike字段"
  - "已完成该SKU的情感分类"
  - "处于逐SKU循环处理的计数阶段"
---

# SKU竞品与情感计数更新

对单个已通过校验的SKU，依据其competitor_or_nike归属与情感极性，将对应的竞品/情感组合计数器加一；用于多SKU循环统计中的原子计数步骤。

## Prompt

在逐SKU循环处理中，当已获得该SKU的competitor_or_nike字段与情感分类结果时，执行本微技能：先判定竞品归属（Nike或Competitor），再判定情感极性（Positive或Negative），然后对应当前SKU的该组合计数加一。仅执行单SKU的原子计数动作，不负责整体循环或目录校验。

## Objective

按竞品归属与情感极性正确递增对应SKU计数
## Applicable Signals

- competitor_or_nike字段已就绪
- 情感分析结果已就绪
- 该SKU已通过目录校验

## Contraindications

- 缺少竞品归属或情感判定结果
- SKU未通过目录校验

## Intervention Moves

- 从competitor_or_nike字段判定为Nike或Competitor
- 从情感分析结果判定为Positive或Negative
- 对应该SKU的竞品/情感组合计数加一

## Workflow Steps

- 读取该SKU的competitor_or_nike字段，判定为Nike或Competitor
- 读取该SKU的情感分析结果，判定为Positive或Negative
- 定位该SKU对应的竞品/情感组合计数器
- 将该计数器加一

## Constraints

- 仅处理单个SKU，不承担整体循环控制
- 计数前必须同时具备竞品归属与情感极性两项判定
- 仅对已通过目录校验的SKU执行

## Cautions

- 竞品归属与情感极性任一缺失时不得计数
- 避免将同一SKU重复计数

## Output Contract

- 该SKU对应竞品/情感组合的计数加一，并返回更新后的计数归属（竞品归属+情感极性）。

## Triggers

- 已获得单个SKU的competitor_or_nike字段
- 已完成该SKU的情感分类
- 处于逐SKU循环处理的计数阶段
