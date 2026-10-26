---
id: "4a141183-0f4c-5000-9f5c-660f26e01360"
name: "Feed 压缩导出配置"
description: "为 Scrapy feed 导出选择并配置压缩方式（gzip、lzma、bz2），通过 feed_options 传入对应压缩参数，以减小导出文件体积或满足传输要求。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "compression"
  - "feed_options"
triggers:
  - "需要压缩导出文件"
  - "需指定 gzip/lzma/bz2 压缩参数"
---

# Feed 压缩导出配置

为 Scrapy feed 导出选择并配置压缩方式（gzip、lzma、bz2），通过 feed_options 传入对应压缩参数，以减小导出文件体积或满足传输要求。

## Prompt

根据目标压缩格式，在 feed 的 feed_options 中设置对应的压缩参数：gzip 使用 gzip_compresslevel、gzip_mtime、gzip_filename；lzma 使用 lzma_format、lzma_check、lzma_preset、lzma_filters；bz2 使用 bz2_compresslevel。仅传入所选格式支持的参数，避免混用不同格式的参数。

## Objective

按所选压缩格式正确设置 feed_options 压缩参数
## Applicable Signals

- 需要压缩导出文件
- 需指定 gzip/lzma/bz2 压缩参数

## Contraindications

- 无需压缩输出
- 目标存储不支持压缩流

## Intervention Moves

- 确定目标压缩格式（gzip、lzma 或 bz2）
- 在 feed_options 中填入该格式支持的压缩参数

## Workflow Steps

- 确认是否需要压缩导出以及目标压缩格式
- 选择对应格式的参数集：gzip（gzip_compresslevel、gzip_mtime、gzip_filename）、lzma（lzma_format、lzma_check、lzma_preset、lzma_filters）、bz2（bz2_compresslevel）
- 将所选参数写入 feed 的 feed_options
- 检查未混入其他格式的参数

## Constraints

- 仅使用所选压缩格式支持的 feed_options 参数
- lzma_filters 在 pypy 7.3.1 及更早版本不可用

## Cautions

- 不同压缩格式的参数不可混用
- lzma_filters 存在 pypy 版本限制

## Output Contract

- 带正确压缩参数的 feed_options 配置

## Triggers

- 需要压缩导出文件
- 需指定 gzip/lzma/bz2 压缩参数
