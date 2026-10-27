---
id: "73a590a4-6d1d-596f-b842-7ead4a57d901"
name: "批量 Feed 输出文件命名占位符配置"
description: "在 Scrapy feed 导出会生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符区分不同输出文件名，并可用 printf 风格格式化控制编号位数。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "uri_placeholder"
  - "batch_output"
triggers:
  - "需要一次导出生成多个文件"
  - "输出文件名需要按批次区分或排序"
examples:
  - input: "需要按批次序号生成多文件，且编号为 5 位"
    output: "feed URI 中使用 %(batch_id)05d，使 3 变为 00003、123 变为 00123"
    notes: "printf 风格格式化控制编号位数"
  - input: "需要按创建时间区分多个输出文件"
    output: "feed URI 中使用 %(batch_time)s，替换为创建时的时间戳"
    notes: "时间戳示例形如 2020-03-28T14-45-08.237134"
---

# 批量 Feed 输出文件命名占位符配置

在 Scrapy feed 导出会生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符区分不同输出文件名，并可用 printf 风格格式化控制编号位数。

## Prompt

当一次 feed 导出会生成多个输出文件时，检查 feed URI 是否至少包含一个批次占位符：%(batch_time)s 或 %(batch_id)d。若需要固定位数或可排序编号，使用 printf 风格格式化调整，例如 %(batch_id)05d。确认占位符位于 URI 中会生成不同文件名的位置，然后交付最终 URI 配置。

## Objective

为多文件 feed 输出配置唯一且可排序的文件名
## Applicable Signals

- feed 导出配置将产生多个输出文件
- 需要按批次时间或批次序号区分文件名

## Contraindications

- 仅导出单个输出文件
- 不需要区分批次文件名

## Intervention Moves

- 在 feed URI 中加入 %(batch_time)s 以按创建时间戳区分文件
- 在 feed URI 中加入 %(batch_id)d 以按 1-based 批次序号区分文件
- 使用 printf 风格格式化（如 %(batch_id)05d）控制编号位数

## Workflow Steps

- 确认本次导出会生成多个输出文件。
- 在 feed URI 中至少加入一个批次占位符：%(batch_time)s 或 %(batch_id)d。
- 如需固定位数或可排序编号，改用 printf 风格格式化，例如 %(batch_id)05d。
- 校验 URI 能生成唯一且可排序的文件名后交付配置。

## Constraints

- 多文件导出时 feed URI 必须至少包含一个批次占位符
- 占位符需使用 printf 风格字符串格式化语法

## Cautions

- batch_id 为 1-based 序号，格式化时注意位数与排序需求

## Output Contract

- 包含 batch_time 或 batch_id 占位符的 feed URI 配置

## Example Therapist Responses

### Example 1

- Client/Input: 需要按批次序号生成多文件，且编号为 5 位
- Therapist/Output: feed URI 中使用 %(batch_id)05d，使 3 变为 00003、123 变为 00123
- Notes: printf 风格格式化控制编号位数

### Example 2

- Client/Input: 需要按创建时间区分多个输出文件
- Therapist/Output: feed URI 中使用 %(batch_time)s，替换为创建时的时间戳
- Notes: 时间戳示例形如 2020-03-28T14-45-08.237134

## Triggers

- 需要一次导出生成多个文件
- 输出文件名需要按批次区分或排序

## Examples

### Example 1

Input:

  需要按批次序号生成多文件，且编号为 5 位

Output:

  feed URI 中使用 %(batch_id)05d，使 3 变为 00003、123 变为 00123

Notes:

  printf 风格格式化控制编号位数

### Example 2

Input:

  需要按创建时间区分多个输出文件

Output:

  feed URI 中使用 %(batch_time)s，替换为创建时的时间戳

Notes:

  时间戳示例形如 2020-03-28T14-45-08.237134
