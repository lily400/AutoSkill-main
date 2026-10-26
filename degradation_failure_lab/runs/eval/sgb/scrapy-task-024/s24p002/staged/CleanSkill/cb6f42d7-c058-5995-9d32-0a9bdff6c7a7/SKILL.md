---
id: "cb6f42d7-c058-5995-9d32-0a9bdff6c7a7"
name: "Feed 导出设置参考清单"
description: "提供 Scrapy feed 导出相关设置项的参考清单，用于查阅有哪些导出配置项，或在排查导出行为时对照设置项；仅作参考，不执行具体配置操作。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed导出"
  - "配置参考"
  - "设置项"
triggers:
  - "需要了解有哪些 feed 导出相关设置项"
  - "排查导出行为时对照设置清单"
  - "查阅 feed 导出可用配置项"
examples:
  - input: "feed 导出有哪些相关设置项？"
    output: "FEEDS（必填）、FEED_EXPORT_ENCODING、FEED_STORE_EMPTY、FEED_EXPORT_FIELDS、FEED_EXPORT_INDENT、FEED_STORAGES、FEED_STORAGE_FTP_ACTIVE、FEED_STORAGE_S3_ACL、FEED_EXPORTERS、FEED_EXPORT_BATCH_ITEM_COUNT。"
---

# Feed 导出设置参考清单

提供 Scrapy feed 导出相关设置项的参考清单，用于查阅有哪些导出配置项，或在排查导出行为时对照设置项；仅作参考，不执行具体配置操作。

## Prompt

当调用方需要了解 feed 导出涉及哪些设置项，或需要对照设置清单排查导出行为时，输出一份设置项参考清单。清单应包含：FEEDS（必填）、FEED_EXPORT_ENCODING、FEED_STORE_EMPTY、FEED_EXPORT_FIELDS、FEED_EXPORT_INDENT、FEED_STORAGES、FEED_STORAGE_FTP_ACTIVE、FEED_STORAGE_S3_ACL、FEED_EXPORTERS、FEED_EXPORT_BATCH_ITEM_COUNT。仅提供清单与用途说明，不代为执行配置修改。

## Objective

提供 feed 导出相关设置项的完整参考清单。
## Applicable Signals

- 调用方询问 feed 导出有哪些可配置项
- 调用方需要对照设置清单定位导出行为

## Contraindications

- 需要直接执行导出配置操作时不应使用本参考清单
- 需要具体设置取值语义或示例时，本清单不提供执行动作

## Intervention Moves

- 列出 feed 导出相关设置项名称
- 标注 FEEDS 为必填项
- 说明清单用途为查阅与对照

## Workflow Steps

- 确认调用方需求为查阅设置项清单
- 输出 feed 导出设置项清单，标注 FEEDS 为必填
- 说明清单仅用于查阅与对照，不执行配置

## Constraints

- 仅提供设置项清单，不代为修改配置
- 清单内容以来源列出的设置项为准，不扩展未列出的项

## Cautions

- FEEDS 为必填设置，其余为可选配置项
- 本资产为参考型知识，不包含执行步骤

## Output Contract

- 一份可对照的 feed 导出设置项清单，包含 FEEDS（必填）及编码、空结果存储、导出字段、缩进、存储后端、FTP/S3 相关、导出器、批量条数等设置项。

## Example Therapist Responses

### Example 1

- Client/Input: feed 导出有哪些相关设置项？
- Therapist/Output: FEEDS（必填）、FEED_EXPORT_ENCODING、FEED_STORE_EMPTY、FEED_EXPORT_FIELDS、FEED_EXPORT_INDENT、FEED_STORAGES、FEED_STORAGE_FTP_ACTIVE、FEED_STORAGE_S3_ACL、FEED_EXPORTERS、FEED_EXPORT_BATCH_ITEM_COUNT。

## Triggers

- 需要了解有哪些 feed 导出相关设置项
- 排查导出行为时对照设置清单
- 查阅 feed 导出可用配置项

## Examples

### Example 1

Input:

  feed 导出有哪些相关设置项？

Output:

  FEEDS（必填）、FEED_EXPORT_ENCODING、FEED_STORE_EMPTY、FEED_EXPORT_FIELDS、FEED_EXPORT_INDENT、FEED_STORAGES、FEED_STORAGE_FTP_ACTIVE、FEED_STORAGE_S3_ACL、FEED_EXPORTERS、FEED_EXPORT_BATCH_ITEM_COUNT。
