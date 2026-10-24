---
id: "22a119a0-0339-5040-bae2-b8b592879f9b"
name: "Feed 导出压缩配置"
description: "为 Scrapy feed 导出选择并配置压缩方式（gzip/lzma/bz2）及其 feed_options 参数，控制输出文件的压缩行为。当需要压缩导出数据文件或指定具体压缩参数时使用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "compression"
  - "feed_options"
triggers:
  - "需要压缩导出的数据文件"
  - "需要指定 gzip/lzma/bz2 压缩参数"
---

# Feed 导出压缩配置

为 Scrapy feed 导出选择并配置压缩方式（gzip/lzma/bz2）及其 feed_options 参数，控制输出文件的压缩行为。当需要压缩导出数据文件或指定具体压缩参数时使用。

## Prompt

根据目标压缩格式，从对应压缩器的 feed_options 参数集中选择并配置参数：
- gzip：可用 gzip_compresslevel、gzip_mtime、gzip_filename，参数语义参见 gzip.GzipFile。
- lzma：可用 lzma_format、lzma_check、lzma_preset、lzma_filters；注意 lzma_filters 在 pypy 7.3.1 及更早版本不可用。
- bz2：可用 bz2_compresslevel，参数语义参见 bz2.BZ2File。
仅使用所选压缩格式支持的参数，输出选定格式及对应 feed_options 配置。

## Objective

正确配置 feed 导出的压缩格式与参数
## Applicable Signals

- 导出文件体积需要压缩
- 需要为 gzip/lzma/bz2 指定压缩级别或其他参数

## Contraindications

- 不需要压缩输出
- 使用不支持的压缩格式

## Intervention Moves

- 确定目标压缩格式（gzip/lzma/bz2）
- 从该格式支持的 feed_options 参数中选择所需参数
- 给出格式与参数配置

## Workflow Steps

- 确认是否需要压缩及目标压缩格式
- 查阅该格式支持的 feed_options 参数列表
- 选择并填写参数值
- 输出选定格式与 feed_options 配置

## Constraints

- 仅使用所选压缩格式明确支持的 feed_options 参数
- lzma_filters 不可用于 pypy 7.3.1 及更早版本

## Cautions

- 参数语义以对应标准库文档（gzip.GzipFile、lzma.LZMAFile、bz2.BZ2File）为准

## Output Contract

- 选定压缩格式并给出对应 feed_options 参数配置

## Triggers

- 需要压缩导出的数据文件
- 需要指定 gzip/lzma/bz2 压缩参数
