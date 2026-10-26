---
id: "2d611108-970f-5e54-8821-4b26efe3a8bc"
name: "Feed URI 参数生成器"
description: "实现一个可调用函数，接收默认参数字典与 spider，返回新的参数字典，用于生成 feed 存储 URI 的动态参数（如 batch_id、batch_time、time）。适用于需要按批次或时间动态构造 feed 文件路径、配置 FEED_URI_PARAMS 的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "uri_param_generation"
  - "export_configuration"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要按批次或时间动态构造 feed 文件路径"
  - "配置 FEED_URI_PARAMS 时"
---

# Feed URI 参数生成器

实现一个可调用函数，接收默认参数字典与 spider，返回新的参数字典，用于生成 feed 存储 URI 的动态参数（如 batch_id、batch_time、time）。适用于需要按批次或时间动态构造 feed 文件路径、配置 FEED_URI_PARAMS 的场景。

## Prompt

实现一个 URI 参数生成函数：接收 params（默认键值对字典）与 spider（feed 条目的来源 spider），返回一个新的字典，包含 batch_id、batch_time、time 等动态参数。不要就地修改传入的 params（已弃用）。batch_id 为文件批次 ID，当 FEED_EXPORT_BATCH_ITEM_COUNT 为 0 时恒为 1；batch_time 为 UTC 日期时间，ISO 格式且将 ':' 替换为 '-'；time 为 batch_time 且微秒置为 0。

## Objective

为 feed 导出 URI 生成动态参数
## Applicable Signals

- 需要按批次或时间动态构造 feed 文件路径
- 配置 FEED_URI_PARAMS 时

## Contraindications

- 仅需静态固定输出路径时
- 不涉及 feed 导出配置时

## Intervention Moves

- 接收 params 默认键值对字典与 spider
- 构造包含 batch_id、batch_time、time 的新字典
- 返回新字典而非就地修改 params

## Workflow Steps

- 接收 params（默认键值对字典）与 spider（feed 条目来源 spider）
- 生成 batch_id：文件批次 ID，当 FEED_EXPORT_BATCH_ITEM_COUNT 为 0 时恒为 1
- 生成 batch_time：UTC 日期时间，ISO 格式且将 ':' 替换为 '-'
- 生成 time：batch_time 且微秒置为 0
- 返回包含上述键的新字典，不就地修改传入的 params

## Constraints

- 函数应返回新字典
- 就地修改传入的 params 已弃用，应避免

## Cautions

- batch_id 在 FEED_EXPORT_BATCH_ITEM_COUNT 为 0 时恒为 1
- batch_time 使用 UTC 时间且 ISO 格式中 ':' 替换为 '-'
- time 为 batch_time 且微秒置为 0

## Output Contract

- 返回包含 batch_id、batch_time、time 等键的新参数字典

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要按批次或时间动态构造 feed 文件路径
- 配置 FEED_URI_PARAMS 时
