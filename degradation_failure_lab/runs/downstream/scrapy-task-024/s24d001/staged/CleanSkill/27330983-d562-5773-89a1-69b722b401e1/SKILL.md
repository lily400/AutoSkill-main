---
id: "27330983-d562-5773-89a1-69b722b401e1"
name: "本地文件系统 Feed 导出配置"
description: "配置 Scrapy feed 导出到本地文件系统：使用 file URI 方案或绝对路径，也可传入 pathlib.Path 对象。适用于需要将抓取结果落盘到本机文件的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "local_filesystem"
  - "storage_configuration"
triggers:
  - "需要把抓取结果保存到本机文件"
  - "用户询问 file:// URI 或绝对路径写法"
  - "用户询问本地文件 feed 是否需要额外依赖"
examples:
  - input: "如何把抓取结果导出到本机 /tmp/export.csv？"
    output: "使用 file URI：file:///tmp/export.csv；在 Unix 系统上也可直接写绝对路径 /tmp/export.csv，或传入 pathlib.Path 对象。本地文件系统无需额外外部库。"
---

# 本地文件系统 Feed 导出配置

配置 Scrapy feed 导出到本地文件系统：使用 file URI 方案或绝对路径，也可传入 pathlib.Path 对象。适用于需要将抓取结果落盘到本机文件的场景。

## Prompt

当需要把抓取结果保存到本机文件时，按以下要点给出本地文件系统 feed 配置：
1. 使用 file URI 方案，例如 file:///tmp/export.csv。
2. 本地文件系统存储可省略 scheme，直接给出绝对路径（仅 Unix 系统），例如 /tmp/export.csv。
3. 也可使用 pathlib.Path 对象作为目标。
4. 本地文件系统无需额外外部库。
仅覆盖本地文件系统这一存储后端；远程存储或自定义存储插件不在本技能范围内。

## Objective

正确指定本地文件系统作为 feed 存储目标
## Applicable Signals

- 需要把抓取结果保存到本机文件
- 用户询问 file:// URI 或绝对路径写法

## Contraindications

- 目标是远程存储如 FTP/S3/GCS
- 需要自定义存储后端插件

## Intervention Moves

- 指定 file URI 方案（如 file:///tmp/export.csv）
- 在 Unix 系统上可省略 scheme 直接使用绝对路径
- 可传入 pathlib.Path 对象作为目标

## Workflow Steps

- 确认导出目标是本机文件系统
- 选择 file URI 或绝对路径（Unix）或 pathlib.Path 对象
- 确认无需额外外部库即可使用

## Constraints

- 省略 scheme 的绝对路径写法仅适用于 Unix 系统
- 仅覆盖本地文件系统存储后端

## Cautions

- 非 Unix 系统不要依赖省略 scheme 的绝对路径写法

## Output Contract

- 可用的本地文件 feed URI 或绝对路径配置

## Example Therapist Responses

### Example 1

- Client/Input: 如何把抓取结果导出到本机 /tmp/export.csv？
- Therapist/Output: 使用 file URI：file:///tmp/export.csv；在 Unix 系统上也可直接写绝对路径 /tmp/export.csv，或传入 pathlib.Path 对象。本地文件系统无需额外外部库。

## Triggers

- 需要把抓取结果保存到本机文件
- 用户询问 file:// URI 或绝对路径写法
- 用户询问本地文件 feed 是否需要额外依赖

## Examples

### Example 1

Input:

  如何把抓取结果导出到本机 /tmp/export.csv？

Output:

  使用 file URI：file:///tmp/export.csv；在 Unix 系统上也可直接写绝对路径 /tmp/export.csv，或传入 pathlib.Path 对象。本地文件系统无需额外外部库。
