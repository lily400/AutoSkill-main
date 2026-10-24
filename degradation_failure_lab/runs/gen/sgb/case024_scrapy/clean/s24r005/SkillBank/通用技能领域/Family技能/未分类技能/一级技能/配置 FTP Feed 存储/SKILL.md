---
id: "34248732-50cd-510d-b3ed-a71e8ef808d1"
name: "配置 FTP Feed 存储"
description: "当需要将 Scrapy 抓取结果导出到 FTP 服务器时，使用 ftp:// URI 配置 feed 存储，并可按需切换主动/被动连接模式。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed-export"
  - "ftp"
  - "storage"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要将导出文件写入 FTP 服务器"
  - "需要调整 FTP 连接模式"
examples:
  - input: "需要将导出文件写入 FTP 服务器"
    output: "ftp://user:pass@ftp.example.com/path/to/export.csv"
    notes: "默认被动连接模式"
  - input: "需要使用主动连接模式"
    output: "设置 FEED_STORAGE_FTP_ACTIVE = True"
    notes: "在 ftp:// URI 基础上调整连接模式"
---

# 配置 FTP Feed 存储

当需要将 Scrapy 抓取结果导出到 FTP 服务器时，使用 ftp:// URI 配置 feed 存储，并可按需切换主动/被动连接模式。

## Prompt

使用 ftp:// 方案的 URI 配置 feed 存储，将导出文件写入 FTP 服务器。默认使用被动连接模式；如需主动连接模式，将 FEED_STORAGE_FTP_ACTIVE 设置为 True。FTP 存储无需额外外部库。

## Objective

正确配置 Scrapy feed 导出到 FTP 服务器
## Applicable Signals

- 目标存储为 FTP 服务器
- 需要指定 ftp:// 方案的 feed URI
- 需要选择主动或被动连接模式

## Contraindications

- 目标存储不是 FTP
- 仅需本地文件或标准输出

## Intervention Moves

- 使用 ftp:// 方案的 URI 指定 FTP 存储位置
- 默认保持被动连接模式
- 如需主动连接模式，将 FEED_STORAGE_FTP_ACTIVE 设置为 True

## Workflow Steps

- 确认目标存储为 FTP 服务器
- 构造 ftp:// 方案的 feed URI（含用户、密码、主机与路径）
- 默认使用被动连接模式；如需主动模式，设置 FEED_STORAGE_FTP_ACTIVE 为 True
- 确认无需额外外部库

## Constraints

- URI 必须使用 ftp 方案
- FTP 存储无需额外外部库

## Cautions

- 主动连接模式可能受网络环境影响，默认使用被动模式更稳妥

## Output Contract

- 可用的 ftp:// feed URI 配置及连接模式设置

## Example Therapist Responses

### Example 1

- Client/Input: 需要将导出文件写入 FTP 服务器
- Therapist/Output: ftp://user:pass@ftp.example.com/path/to/export.csv
- Notes: 默认被动连接模式

### Example 2

- Client/Input: 需要使用主动连接模式
- Therapist/Output: 设置 FEED_STORAGE_FTP_ACTIVE = True
- Notes: 在 ftp:// URI 基础上调整连接模式

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要将导出文件写入 FTP 服务器
- 需要调整 FTP 连接模式

## Examples

### Example 1

Input:

  需要将导出文件写入 FTP 服务器

Output:

  ftp://user:pass@ftp.example.com/path/to/export.csv

Notes:

  默认被动连接模式

### Example 2

Input:

  需要使用主动连接模式

Output:

  设置 FEED_STORAGE_FTP_ACTIVE = True

Notes:

  在 ftp:// URI 基础上调整连接模式
