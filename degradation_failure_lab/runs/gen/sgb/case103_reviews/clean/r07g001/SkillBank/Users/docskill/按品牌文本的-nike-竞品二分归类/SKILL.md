---
id: "5705f35c-9afe-5668-81aa-6ae7e5d4f172"
name: "按品牌文本的 Nike/竞品二分归类"
description: "当结构化品牌标志（competitor_or_nike）缺失时，依据评论文本中明确出现的品牌线索，将每条记录归为 nike 或 competitor，作为下游按 Nike/竞品拆分计数的临时充分方案。"
version: "0.1.0"
tags:
  - "品牌识别"
  - "文本归类"
  - "评论分类"
  - "数据运营"
triggers:
  - "competitor_or_nike 字段缺失但评论文本含品牌名"
  - "下游需要按 Nike/竞品拆分计数"
---

# 按品牌文本的 Nike/竞品二分归类

当结构化品牌标志（competitor_or_nike）缺失时，依据评论文本中明确出现的品牌线索，将每条记录归为 nike 或 competitor，作为下游按 Nike/竞品拆分计数的临时充分方案。

## Prompt

在结构化品牌标志缺失、但评论文本含品牌线索时，逐条读取评论文本，识别其中出现的品牌名，将其归为 nike 或 competitor。仅依据文本中明确出现的品牌线索判断，不得从无关字段推断。若某条记录文本无任何品牌线索，标记为无法归类并上报，不要臆测。输出每条记录的归类结果，并附简要状态说明与阻塞项。

## Objective

在品牌标志缺失时仍能按品牌文本完成 Nike 与竞品的区分
## Applicable Signals

- competitor_or_nike 字段缺失
- 评论文本中出现品牌名
- 下游计数需要 Nike/竞品二分

## Contraindications

- 评论文本无任何品牌线索
- 结构化品牌字段已完整可用

## Intervention Moves

- 逐条读取评论文本
- 识别文本中出现的品牌名
- 将记录归为 nike 或 competitor
- 对无品牌线索的记录标记为无法归类并上报

## Workflow Steps

- 确认 competitor_or_nike 字段缺失且评论文本含品牌线索
- 逐条读取评论文本并识别品牌名
- 将记录归为 nike 或 competitor
- 对无品牌线索的记录标记为无法归类，不臆测
- 输出归类结果并附状态说明与阻塞项

## Constraints

- 仅依据评论文本中明确出现的品牌线索判断
- 不得从无关字段推断分类值
- 无品牌线索时不得强行归类

## Cautions

- 一条评论可能提及多个品牌，需按文本线索谨慎判断
- 该归类为临时充分方案，后续应待结构化字段修复后复核

## Output Contract

- 每条记录标注为 nike 或 competitor 的归类结果，并附简要状态说明与阻塞项。

## Triggers

- competitor_or_nike 字段缺失但评论文本含品牌名
- 下游需要按 Nike/竞品拆分计数
