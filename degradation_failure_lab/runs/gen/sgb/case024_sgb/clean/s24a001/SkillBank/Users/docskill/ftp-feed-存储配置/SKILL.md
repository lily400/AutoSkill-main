---
id: "563ce5c2-6cd7-5937-8918-787b1fc2b465"
name: "FTP Feed 存储配置"
description: "配置 Scrapy feed 导出到 FTP 服务器，包括 ftp 方案 URI 构造与主动/被动连接模式选择。适用于需要将抓取结果直接写入 FTP 的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "ftp"
  - "storage_configuration"
triggers:
  - "需要将 feed 导出到 FTP 服务器"
  - "需要切换 FTP 主动/被动连接模式"
examples:
  - input: "需要将 feed 导出到 FTP 服务器"
    output: "ftp://user:pass@ftp.example.com/path/to/export.csv"
    notes: "默认被动连接模式"
  - input: "需要使用主动连接模式"
    output: "FEED_STORAGE_FTP_ACTIVE = True"
    notes: "在设置中启用主动模式"
---

# FTP Feed 存储配置

配置 Scrapy feed 导出到 FTP 服务器，包括 ftp 方案 URI 构造与主动/被动连接模式选择。适用于需要将抓取结果直接写入 FTP 的场景。

## Prompt

当需要将 Scrapy feed 导出到 FTP 服务器时，使用本技能：构造 ftp 方案的 feed URI（形如 ftp://user:pass@host/path/to/export.csv），确认无需额外外部库；默认使用被动连接模式，如需主动模式则将 FEED_STORAGE_FTP_ACTIVE 设为 True。

## Objective

正确配置 FTP 作为 feed 存储后端并选择连接模式
## Applicable Signals

- 目标存储后端为 FTP 服务器
- 需要指定 FTP 连接模式

## Contraindications

- 目标存储为本地文件系统、S3 或 GCS
- 仅需标准输出

## Intervention Moves

- 使用 ftp 方案构造 feed URI
- 默认采用被动连接模式
- 如需主动模式则设置 FEED_STORAGE_FTP_ACTIVE 为 True

## Workflow Steps

- 确认目标为 FTP 存储后端
- 构造 ftp:// 方案的 feed URI，包含用户、密码、主机与导出路径
- 确认无需额外外部库
- 默认使用被动连接模式；如需主动模式，将 FEED_STORAGE_FTP_ACTIVE 设为 True

## Constraints

- URI 必须使用 ftp 方案
- 主动模式需显式设置 FEED_STORAGE_FTP_ACTIVE

## Cautions

- URI 中包含凭据，注意避免泄露

## Output Contract

- 可用的 FTP feed URI 与 FEED_STORAGE_FTP_ACTIVE 设置

## Example Therapist Responses

### Example 1

- Client/Input: 需要将 feed 导出到 FTP 服务器
- Therapist/Output: ftp://user:pass@ftp.example.com/path/to/export.csv
- Notes: 默认被动连接模式

### Example 2

- Client/Input: 需要使用主动连接模式
- Therapist/Output: FEED_STORAGE_FTP_ACTIVE = True
- Notes: 在设置中启用主动模式

## Triggers

- 需要将 feed 导出到 FTP 服务器
- 需要切换 FTP 主动/被动连接模式

## Examples

### Example 1

Input:

  需要将 feed 导出到 FTP 服务器

Output:

  ftp://user:pass@ftp.example.com/path/to/export.csv

Notes:

  默认被动连接模式

### Example 2

Input:

  需要使用主动连接模式

Output:

  FEED_STORAGE_FTP_ACTIVE = True

Notes:

  在设置中启用主动模式
