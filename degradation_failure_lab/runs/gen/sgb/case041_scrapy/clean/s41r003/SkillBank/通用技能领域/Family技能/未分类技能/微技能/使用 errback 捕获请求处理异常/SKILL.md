---
id: "a465f31a-2043-56a4-8ead-67fa083ba31a"
name: "使用 errback 捕获请求处理异常"
description: "为 Request 指定 errback 回调，在下载或处理失败时接收 Failure 对象并访问其中的附加数据，实现自定义异常处理。当请求可能失败且需要自定义错误处理，或需要在失败时访问请求附加数据时使用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "errback"
  - "异常处理"
  - "Request"
  - "Failure"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "请求可能失败需要自定义错误处理"
  - "需要在失败时访问请求附加数据"
  - "需要区分正常回调与失败回调路径"
examples:
  - input: "Request(\"https://example.com\", callback=self.parse_page2, errback=self.errback_handler)"
    output: "请求失败时 errback_handler 被调用并接收 Failure 对象"
    notes: "errback 专注失败路径处理"
---

# 使用 errback 捕获请求处理异常

为 Request 指定 errback 回调，在下载或处理失败时接收 Failure 对象并访问其中的附加数据，实现自定义异常处理。当请求可能失败且需要自定义错误处理，或需要在失败时访问请求附加数据时使用。

## Prompt

当需要为某个 Request 定制失败处理时，在构造 Request 时传入 errback 参数指向处理函数。errback 会在请求下载或处理失败时被调用，接收一个 Failure 对象作为参数。可通过 Failure 访问异常信息，并结合请求附加数据（如 cb_kwargs 或 meta）进行后续处理。确保 errback 函数签名正确并能处理 Failure 对象。

## Objective

在请求失败时通过 errback 捕获并处理异常
## Applicable Signals

- 请求可能失败需要自定义错误处理
- 需要在失败时访问请求附加数据

## Contraindications

- 请求无失败风险或使用默认错误处理即可时

## Intervention Moves

- 在 Request 构造时指定 errback 参数
- 在 errback 函数中接收并处理 Failure 对象
- 通过附加数据在 errback 中获取请求上下文

## Workflow Steps

- 识别需要自定义失败处理的请求
- 编写 errback 处理函数，接收 Failure 对象
- 在构造 Request 时传入 errback 参数
- 在 errback 中访问 Failure 及请求附加数据进行处理

## Constraints

- errback 函数需正确接收 Failure 对象作为参数
- 附加数据需在请求构造时通过 cb_kwargs 或 meta 传入

## Cautions

- errback 仅处理失败路径，正常响应仍由 callback 处理
- 未指定 errback 时失败将走默认错误处理

## Output Contract

- errback 被调用并处理 Failure 对象

## Example Therapist Responses

### Example 1

- Client/Input: Request("https://example.com", callback=self.parse_page2, errback=self.errback_handler)
- Therapist/Output: 请求失败时 errback_handler 被调用并接收 Failure 对象
- Notes: errback 专注失败路径处理

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 请求可能失败需要自定义错误处理
- 需要在失败时访问请求附加数据
- 需要区分正常回调与失败回调路径

## Examples

### Example 1

Input:

  Request("https://example.com", callback=self.parse_page2, errback=self.errback_handler)

Output:

  请求失败时 errback_handler 被调用并接收 Failure 对象

Notes:

  errback 专注失败路径处理
