---
id: "100c7e33-dfd6-594b-929c-0a53ce77829e"
name: "Feed 存储 URI 参数替换"
description: "在创建 feed 时按规则替换存储 URI 中的占位参数（%(time)s、%(name)s 及 spider 同名属性），用于生成动态输出路径。当需要按时间戳或 spider 名称动态生成输出文件路径，或在 URI 中引用 spider 自定义属性作为路径片段时使用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "uri_parameter_substitution"
  - "feed_creation"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要按时间戳或 spider 名称动态生成输出文件路径"
  - "需要在 URI 中引用 spider 自定义属性作为路径片段"
examples:
  - input: "存储 URI 含 %(time)s 与 %(name)s 占位参数"
    output: "生成包含创建时间戳与 spider 名称的最终存储 URI"
    notes: "时间戳在 feed 创建时确定"
  - input: "存储 URI 含 %(site_id)s 占位参数，spider 具有 site_id 属性"
    output: "生成以 spider.site_id 属性值替换该片段的最终存储 URI"
    notes: "其他命名参数按 spider 同名属性替换"
---

# Feed 存储 URI 参数替换

在创建 feed 时按规则替换存储 URI 中的占位参数（%(time)s、%(name)s 及 spider 同名属性），用于生成动态输出路径。当需要按时间戳或 spider 名称动态生成输出文件路径，或在 URI 中引用 spider 自定义属性作为路径片段时使用。

## Prompt

解析 feed 存储 URI 中的 %(...)s 占位参数，并在 feed 创建时刻完成替换：%(time)s 替换为创建时的时间戳，%(name)s 替换为 spider 名称，其他命名参数替换为 spider 上同名属性的当前值。替换后输出最终存储 URI 字符串。

## Objective

正确解析并替换 feed 存储 URI 中的命名参数，生成最终输出路径
## Applicable Signals

- 存储 URI 中包含 %(time)s 或 %(name)s 占位参数
- 存储 URI 中包含引用 spider 自定义属性的命名参数（如 %(site_id)s）
- 需要在 feed 创建时确定最终输出路径

## Contraindications

- URI 中不含任何 %(...)s 占位参数
- 需要替换的参数在 spider 上不存在同名属性

## Intervention Moves

- 识别 URI 中的 %(...)s 占位参数
- 将 %(time)s 替换为 feed 创建时的时间戳
- 将 %(name)s 替换为 spider 名称
- 将其他命名参数替换为 spider 上同名属性的当前值
- 输出替换完成的最终存储 URI

## Workflow Steps

- 扫描存储 URI，提取所有 %(...)s 命名占位参数
- 对 %(time)s 使用 feed 创建时刻的时间戳替换
- 对 %(name)s 使用 spider 名称替换
- 对其他命名参数使用 spider 上同名属性的当前值替换
- 返回替换完成的最终存储 URI 字符串

## Constraints

- 替换发生在 feed 创建时刻，而非配置解析时刻
- 仅替换 URI 中实际存在的命名占位参数

## Cautions

- 若引用的 spider 属性不存在，无法完成同名替换，应避免使用该占位参数

## Output Contract

- 返回替换完成的最终存储 URI 字符串，可直接用于创建 feed。

## Example Therapist Responses

### Example 1

- Client/Input: 存储 URI 含 %(time)s 与 %(name)s 占位参数
- Therapist/Output: 生成包含创建时间戳与 spider 名称的最终存储 URI
- Notes: 时间戳在 feed 创建时确定

### Example 2

- Client/Input: 存储 URI 含 %(site_id)s 占位参数，spider 具有 site_id 属性
- Therapist/Output: 生成以 spider.site_id 属性值替换该片段的最终存储 URI
- Notes: 其他命名参数按 spider 同名属性替换

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要按时间戳或 spider 名称动态生成输出文件路径
- 需要在 URI 中引用 spider 自定义属性作为路径片段

## Examples

### Example 1

Input:

  存储 URI 含 %(time)s 与 %(name)s 占位参数

Output:

  生成包含创建时间戳与 spider 名称的最终存储 URI

Notes:

  时间戳在 feed 创建时确定

### Example 2

Input:

  存储 URI 含 %(site_id)s 占位参数，spider 具有 site_id 属性

Output:

  生成以 spider.site_id 属性值替换该片段的最终存储 URI

Notes:

  其他命名参数按 spider 同名属性替换
