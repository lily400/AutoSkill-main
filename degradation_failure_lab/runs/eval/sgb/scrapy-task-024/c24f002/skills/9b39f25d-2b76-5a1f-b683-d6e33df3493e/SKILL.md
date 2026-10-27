---
id: "9b39f25d-2b76-5a1f-b683-d6e33df3493e"
name: "Scrapy 本地文件系统 Feed 导出配置"
description: "配置 Scrapy feed 导出到本地文件系统，使用 file URI scheme、Unix 绝对路径或 pathlib.Path 对象指定存储目标。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "storage_configuration"
  - "local_filesystem"
triggers:
  - "需要把抓取结果导出到本机文件"
  - "用户询问 file URI 或绝对路径写法"
  - "需要为 feed 指定本地文件系统存储目标"
examples:
  - input: "需要把抓取结果导出到本机 /tmp/export.csv"
    output: "file:///tmp/export.csv"
    notes: "使用 file URI scheme"
  - input: "在 Unix 系统上导出到 /tmp/export.csv"
    output: "/tmp/export.csv"
    notes: "省略 scheme 的绝对路径写法"
---

# Scrapy 本地文件系统 Feed 导出配置

配置 Scrapy feed 导出到本地文件系统，使用 file URI scheme、Unix 绝对路径或 pathlib.Path 对象指定存储目标。

## Prompt

当需要把 Scrapy 抓取结果导出到本机文件时，按以下方式指定本地文件系统作为 feed 存储目标：使用 file URI scheme（如 file:///tmp/export.csv），或在 Unix 系统上省略 scheme 直接给出绝对路径（如 /tmp/export.csv），也可传入 pathlib.Path 对象。确认无需额外外部库。

## Objective

正确指定本地文件系统作为 feed 存储目标
## Applicable Signals

- 需要把抓取结果导出到本机文件
- 用户询问 file URI 或绝对路径写法
- 需要为 feed 指定本地文件系统存储目标

## Contraindications

- 目标是远程存储如 S3/FTP/GCS
- 需要自定义存储后端插件

## Intervention Moves

- 使用 file URI scheme 指定本地路径
- 在 Unix 系统上省略 scheme 直接给出绝对路径
- 传入 pathlib.Path 对象作为存储目标

## Workflow Steps

- 确认导出目标为本机文件系统
- 选择 file URI scheme、绝对路径或 pathlib.Path 之一指定目标
- 确认无需额外外部库即可使用

## Constraints

- 省略 scheme 的绝对路径写法仅在 Unix 系统上可用
- 本地文件系统存储无需额外外部库

## Cautions

- 省略 scheme 的绝对路径写法不适用于非 Unix 系统

## Output Contract

- 可用的本地文件 feed URI 或绝对路径配置

## Example Therapist Responses

### Example 1

- Client/Input: 需要把抓取结果导出到本机 /tmp/export.csv
- Therapist/Output: file:///tmp/export.csv
- Notes: 使用 file URI scheme

### Example 2

- Client/Input: 在 Unix 系统上导出到 /tmp/export.csv
- Therapist/Output: /tmp/export.csv
- Notes: 省略 scheme 的绝对路径写法

## Triggers

- 需要把抓取结果导出到本机文件
- 用户询问 file URI 或绝对路径写法
- 需要为 feed 指定本地文件系统存储目标

## Examples

### Example 1

Input:

  需要把抓取结果导出到本机 /tmp/export.csv

Output:

  file:///tmp/export.csv

Notes:

  使用 file URI scheme

### Example 2

Input:

  在 Unix 系统上导出到 /tmp/export.csv

Output:

  /tmp/export.csv

Notes:

  省略 scheme 的绝对路径写法
