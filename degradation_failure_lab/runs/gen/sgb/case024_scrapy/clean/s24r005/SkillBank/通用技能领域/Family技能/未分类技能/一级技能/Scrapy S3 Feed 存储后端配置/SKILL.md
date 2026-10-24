---
id: "3c445cfa-3f7b-50b1-b612-d9b3a9b462c0"
name: "Scrapy S3 Feed 存储后端配置"
description: "为 Scrapy feed 导出配置 S3 或 S3 兼容对象存储后端，包括自定义 ACL、endpoint 与 region，并明确 overwrite 默认行为。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "s3"
  - "storage_backend"
  - "configuration"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要将导出结果写入 S3 或 S3 兼容存储"
  - "需要自定义 ACL、endpoint 或 region"
---

# Scrapy S3 Feed 存储后端配置

为 Scrapy feed 导出配置 S3 或 S3 兼容对象存储后端，包括自定义 ACL、endpoint 与 region，并明确 overwrite 默认行为。

## Prompt

当导出目标为 S3 或 S3 兼容对象存储时，按以下步骤配置：1) 在 FEEDS 中指定 s3:// 存储 URI；2) 如需自定义访问控制，设置 FEED_STORAGE_S3_ACL；3) 如需自定义服务端点，设置 AWS_ENDPOINT_URL；4) 如需指定区域，设置 AWS_REGION_NAME；5) 注意该存储后端在 FEEDS 中 overwrite 键的默认值为 True，若需保留历史文件应显式覆盖该默认值。

## Objective

正确配置 S3 存储后端参数以导出 feed
## Applicable Signals

- 导出目标为 S3 或 S3 兼容对象存储
- 需要自定义 ACL、endpoint 或 region

## Contraindications

- 导出目标为本地文件系统、FTP 或标准输出
- 仅需选择序列化格式而无需对象存储

## Intervention Moves

- 在 FEEDS 中指定 s3:// 存储 URI
- 设置 FEED_STORAGE_S3_ACL 自定义 ACL
- 设置 AWS_ENDPOINT_URL 自定义端点
- 设置 AWS_REGION_NAME 指定区域
- 确认 overwrite 默认值为 True 并按需覆盖

## Workflow Steps

- 确认导出目标为 S3 或 S3 兼容存储
- 在 FEEDS 中配置 s3:// 存储 URI
- 按需设置 FEED_STORAGE_S3_ACL、AWS_ENDPOINT_URL、AWS_REGION_NAME
- 核对 overwrite 默认值 True 是否符合预期，必要时显式覆盖

## Constraints

- 仅适用于 S3 存储后端
- overwrite 默认值为 True，需注意覆盖已有文件的风险

## Cautions

- 默认 overwrite=True 可能导致已有导出文件被覆盖

## Output Contract

- 一份包含 FEED_STORAGE_S3_ACL、AWS_ENDPOINT_URL、AWS_REGION_NAME 及 overwrite 默认值的 S3 存储配置

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要将导出结果写入 S3 或 S3 兼容存储
- 需要自定义 ACL、endpoint 或 region
