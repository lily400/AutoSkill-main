---
id: "945ee694-0375-5f27-a671-6805bddfe600"
name: "自定义 Feed 导出器扩展"
description: "通过 FEED_EXPORTERS 设置注册自定义导出器，以扩展 Scrapy Feed 导出支持的序列化格式；当内置导出格式无法满足输出需求时使用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed-exports"
  - "FEED_EXPORTERS"
  - "导出格式扩展"
triggers:
  - "内置导出格式无法满足输出需求"
  - "需要扩展 Feed 支持的序列化格式"
---

# 自定义 Feed 导出器扩展

通过 FEED_EXPORTERS 设置注册自定义导出器，以扩展 Scrapy Feed 导出支持的序列化格式；当内置导出格式无法满足输出需求时使用。

## Prompt

当内置导出格式无法满足输出需求时，使用 FEED_EXPORTERS 设置注册自定义导出器，使其可作为 FEEDS 中 format 键的取值使用。先确认内置格式确实不满足需求，再定义并注册自定义导出器，最后验证其可被 FEEDS 的 format 键引用。

## Objective

通过 FEED_EXPORTERS 扩展自定义导出格式
## Applicable Signals

- 内置导出格式无法满足输出需求
- 需要新增一种 Feed 序列化格式

## Contraindications

- 内置格式已满足需求

## Intervention Moves

- 确认内置格式（json、jsonlines、csv、xml、pickle、marshal）均不满足需求
- 通过 FEED_EXPORTERS 设置注册自定义导出器
- 在 FEEDS 的 format 键中使用自定义格式名

## Workflow Steps

- 确认内置导出格式无法满足输出需求
- 通过 FEED_EXPORTERS 设置注册自定义导出器
- 在 FEEDS 的 format 键中引用自定义格式名
- 验证导出结果符合预期

## Constraints

- 仅在需要扩展格式时使用 FEED_EXPORTERS
- 自定义格式名需与 FEEDS 的 format 键取值一致

## Cautions

- 若使用 JSON 处理大型 feed，需注意相关警告

## Output Contract

- 自定义导出器注册成功并可用于 FEEDS 的 format 键

## Triggers

- 内置导出格式无法满足输出需求
- 需要扩展 Feed 支持的序列化格式
