---
id: "784f9ca3-1275-5212-8362-163ca94dec83"
name: "Scrapy 请求去重过滤控制"
description: "通过设置 Request 的 dont_filter 属性，控制支持过滤的组件是否跳过对该请求的去重过滤。适用于需要重复抓取同一 URL，或确保起始 URL 不被过滤的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "dont_filter"
  - "去重"
  - "请求构造"
triggers:
  - "需要重复请求同一 URL 而不被过滤"
  - "start_urls 场景需确保起始请求不被去重"
  - "构造 Request 时需显式控制去重行为"
examples:
  - input: "需要重复请求同一 URL 而不被过滤"
    output: "构造 Request 时设置 dont_filter=True"
    notes: "阻止支持过滤的组件过滤该请求"
  - input: "无重复抓取需求"
    output: "保持 dont_filter 默认 False"
    notes: "允许默认去重"
---

# Scrapy 请求去重过滤控制

通过设置 Request 的 dont_filter 属性，控制支持过滤的组件是否跳过对该请求的去重过滤。适用于需要重复抓取同一 URL，或确保起始 URL 不被过滤的场景。

## Prompt

在构造 Request 时，根据是否需要重复抓取同一 URL 来决定 dont_filter 的取值：默认 False 表示允许被支持过滤的组件过滤掉；设为 True 表示这些组件不应过滤该请求。仅在确有重复抓取需求时设为 True，避免无谓地绕过默认去重。

## Objective

按需关闭或开启请求的去重过滤
## Applicable Signals

- 同一 URL 需要被重复抓取
- 起始 URL 请求需避免被去重过滤
- 需要显式覆盖默认去重行为

## Contraindications

- 希望依赖默认去重以避免重复抓取时不应设为 True
- 无明确重复抓取需求时不应关闭过滤

## Intervention Moves

- 在 Request 构造参数中设置 dont_filter=True 以阻止支持过滤的组件过滤该请求
- 保持默认 False 以允许默认去重
- 通过 start_urls 定义起始 URL 时注意该属性默认启用

## Workflow Steps

- 判断当前请求是否需要重复抓取同一 URL 或作为起始请求不被过滤
- 若需要，则在 Request 构造时设置 dont_filter=True；否则保持默认 False
- 确认调度组件据此决定是否过滤该请求

## Constraints

- dont_filter 为布尔属性，默认 False
- 仅在确有重复抓取需求时设为 True

## Cautions

- 滥用 dont_filter=True 会绕过默认去重，可能导致重复抓取

## Output Contract

- 请求携带正确的 dont_filter 取值，调度组件据此决定是否过滤

## Example Therapist Responses

### Example 1

- Client/Input: 需要重复请求同一 URL 而不被过滤
- Therapist/Output: 构造 Request 时设置 dont_filter=True
- Notes: 阻止支持过滤的组件过滤该请求

### Example 2

- Client/Input: 无重复抓取需求
- Therapist/Output: 保持 dont_filter 默认 False
- Notes: 允许默认去重

## Triggers

- 需要重复请求同一 URL 而不被过滤
- start_urls 场景需确保起始请求不被去重
- 构造 Request 时需显式控制去重行为

## Examples

### Example 1

Input:

  需要重复请求同一 URL 而不被过滤

Output:

  构造 Request 时设置 dont_filter=True

Notes:

  阻止支持过滤的组件过滤该请求

### Example 2

Input:

  无重复抓取需求

Output:

  保持 dont_filter 默认 False

Notes:

  允许默认去重
