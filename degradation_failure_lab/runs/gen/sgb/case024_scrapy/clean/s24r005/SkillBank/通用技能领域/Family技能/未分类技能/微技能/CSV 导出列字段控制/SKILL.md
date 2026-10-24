---
id: "8cc3ce38-d0f7-54a5-9546-2056a0d42430"
name: "CSV 导出列字段控制"
description: "使用 FEED_EXPORT_FIELDS 指定 CSV 导出的列集合、顺序与列名；由于 CSV 使用固定表头，该设置对 CSV 尤为重要。适用于需要精确控制 CSV 输出结构时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed-exports"
  - "csv"
  - "FEED_EXPORT_FIELDS"
  - "导出配置"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "CSV 导出需要固定列顺序"
  - "CSV 导出需要自定义列名"
  - "需要限定 CSV 导出的列集合"
---

# CSV 导出列字段控制

使用 FEED_EXPORT_FIELDS 指定 CSV 导出的列集合、顺序与列名；由于 CSV 使用固定表头，该设置对 CSV 尤为重要。适用于需要精确控制 CSV 输出结构时。

## Prompt

当需要精确控制 CSV 导出的列集合、顺序或列名时，使用 FEED_EXPORT_FIELDS 设置来声明导出字段。注意 CSV 使用固定表头，因此该设置对 CSV 尤为关键；其他 feed 导出器也可使用该选项。配置后确认输出 CSV 的表头与数据列符合预期。

## Objective

精确控制 CSV 导出的列集合、顺序与命名
## Applicable Signals

- CSV 导出需要固定列顺序或自定义列名
- 需要限定 CSV 输出包含哪些列

## Contraindications

- 导出格式不需要固定表头控制时无需使用

## Intervention Moves

- 在设置中通过 FEED_EXPORT_FIELDS 声明导出字段列表
- 按期望顺序排列字段以控制列顺序
- 确认 CSV 表头与数据列与配置一致

## Workflow Steps

- 确认导出格式为 csv（FEEDS 中 format 键为 csv）
- 在 FEED_EXPORT_FIELDS 中按期望顺序列出字段
- 运行导出并核对 CSV 表头、列顺序与列名

## Constraints

- CSV 使用固定表头，字段控制对 CSV 尤为重要
- 其他 feed 导出器也可使用该选项

## Cautions

- 字段顺序与命名需与下游消费方约定一致

## Output Contract

- CSV 文件按指定列、顺序与列名输出

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- CSV 导出需要固定列顺序
- CSV 导出需要自定义列名
- 需要限定 CSV 导出的列集合
