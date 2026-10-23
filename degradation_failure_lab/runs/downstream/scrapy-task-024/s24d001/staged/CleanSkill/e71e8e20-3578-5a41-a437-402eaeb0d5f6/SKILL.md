---
id: "e71e8e20-3578-5a41-a437-402eaeb0d5f6"
name: "批量输出文件命名占位符配置"
description: "在生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符来区分不同批次文件名，并可用 printf 风格格式化控制编号位数。适用于需要按批次拆分导出文件的抓取配置场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "uri_placeholder"
  - "batch"
triggers:
  - "需要生成多个输出文件"
  - "需要按批次区分导出文件名"
  - "配置 feed URI 以支持批次拆分"
examples:
  - input: "需要按批次生成多个输出文件，希望批次号固定为 5 位"
    output: "feed URI 中使用 %(batch_id)05d，例如批次 3 生成 00003、批次 123 生成 00123"
    notes: "printf 风格格式化用于控制编号位数"
  - input: "需要按创建时间区分多个输出文件"
    output: "feed URI 中使用 %(batch_time)s，替换为创建 feed 时的时间戳（如 2020-03-28T14-45-08.237134）"
---

# 批量输出文件命名占位符配置

在生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符来区分不同批次文件名，并可用 printf 风格格式化控制编号位数。适用于需要按批次拆分导出文件的抓取配置场景。

## Prompt

当需要为多文件批量导出配置 feed URI 时，确认 URI 中至少包含一个批次占位符：%(batch_time)s（创建 feed 时的时间戳）或 %(batch_id)d（从 1 开始的批次序号）。如需固定编号位数，使用 printf 风格格式化，例如 %(batch_id)05d 将 3 变为 00003。仅配置文件名占位符，不涉及序列化格式或存储后端选择。

## Objective

为多文件批量导出配置唯一且可读的文件名占位符
## Applicable Signals

- 导出目标为多个文件而非单一文件
- 需要按批次或时间区分输出文件名

## Contraindications

- 仅导出单个输出文件
- 不需要批次拆分

## Intervention Moves

- 在 feed URI 中插入 %(batch_time)s 占位符以按创建时间命名
- 在 feed URI 中插入 %(batch_id)d 占位符以按批次序号命名
- 使用 printf 风格格式化（如 %(batch_id)05d）控制编号位数

## Workflow Steps

- 确认导出场景需要生成多个输出文件
- 在 feed URI 中选择并插入至少一个占位符：%(batch_time)s 或 %(batch_id)d
- 如需固定编号位数，改用 printf 风格格式化，例如 %(batch_id)05d
- 校验最终 URI 至少包含一个批次占位符

## Constraints

- 生成多个输出文件时，feed URI 必须至少包含一个批次占位符
- 占位符仅限 %(batch_time)s 或 %(batch_id)d 两类

## Cautions

- %(batch_id)d 为从 1 开始的序号，格式化时注意位数与排序可读性

## Output Contract

- 包含至少一个 batch_time 或 batch_id 占位符的 feed URI 配置

## Example Therapist Responses

### Example 1

- Client/Input: 需要按批次生成多个输出文件，希望批次号固定为 5 位
- Therapist/Output: feed URI 中使用 %(batch_id)05d，例如批次 3 生成 00003、批次 123 生成 00123
- Notes: printf 风格格式化用于控制编号位数

### Example 2

- Client/Input: 需要按创建时间区分多个输出文件
- Therapist/Output: feed URI 中使用 %(batch_time)s，替换为创建 feed 时的时间戳（如 2020-03-28T14-45-08.237134）

## Triggers

- 需要生成多个输出文件
- 需要按批次区分导出文件名
- 配置 feed URI 以支持批次拆分

## Examples

### Example 1

Input:

  需要按批次生成多个输出文件，希望批次号固定为 5 位

Output:

  feed URI 中使用 %(batch_id)05d，例如批次 3 生成 00003、批次 123 生成 00123

Notes:

  printf 风格格式化用于控制编号位数

### Example 2

Input:

  需要按创建时间区分多个输出文件

Output:

  feed URI 中使用 %(batch_time)s，替换为创建 feed 时的时间戳（如 2020-03-28T14-45-08.237134）
