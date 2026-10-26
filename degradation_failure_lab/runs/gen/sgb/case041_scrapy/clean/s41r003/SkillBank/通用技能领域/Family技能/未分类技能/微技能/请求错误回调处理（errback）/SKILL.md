---
id: "9719683e-0a4a-5d7e-8169-5d7d854d94d9"
name: "请求错误回调处理（errback）"
description: "为 Scrapy 请求配置 errback，并按失败类型（HttpError、DNSLookupError、TimeoutError/TCPTimedOutError）分支记录与处理异常。适用于需要区分不同下载失败并做针对性处理的爬虫。"
version: "0.1.0"
tags:
  - "scrapy"
  - "errback"
  - "错误处理"
  - "请求调度"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要区分 HTTP 错误、DNS 错误、超时等不同失败类型"
  - "希望在请求失败时记录日志或产出诊断数据"
examples:
  - input: "请求失败并触发 errback，failure 为 HttpError"
    output: "记录 repr(failure)，并从 failure.value.response 取非 200 响应，记录 \"HttpError on <url>\""
    notes: "HttpError 分支可访问响应对象"
  - input: "请求失败并触发 errback，failure 为 DNSLookupError"
    output: "记录 repr(failure)，并从 failure.request 取原始请求，记录 \"DNSLookupError on <url>\""
    notes: "DNS 分支只能访问原始请求"
  - input: "请求失败并触发 errback，failure 为 TimeoutError 或 TCPTimedOutError"
    output: "记录 repr(failure)，并从 failure.request 取原始请求，记录 \"TimeoutError on <url>\""
    notes: "超时分支只能访问原始请求"
---

# 请求错误回调处理（errback）

为 Scrapy 请求配置 errback，并按失败类型（HttpError、DNSLookupError、TimeoutError/TCPTimedOutError）分支记录与处理异常。适用于需要区分不同下载失败并做针对性处理的爬虫。

## Prompt

在发起请求时为其指定 errback 回调；在 errback 中接收 failure 对象，先用 failure.check() 判断异常类型，再按类型分支处理：HttpError 时从 failure.value.response 取非 200 响应并记录其 URL；DNSLookupError 时从 failure.request 取原始请求并记录其 URL；TimeoutError/TCPTimedOutError 时同样从 failure.request 取请求并记录。始终先记录 failure 的 repr 作为兜底日志。

## Objective

在请求失败时按异常类型分流处理并记录日志
## Applicable Signals

- 请求需要自定义失败处理而非默认日志
- 需要针对不同下载异常类型做差异化响应

## Contraindications

- 仅需默认失败日志、无需分类处理时
- 失败原因与请求处理无关（如解析逻辑错误）

## Intervention Moves

- 在 scrapy.Request 中设置 errback 指向处理函数
- 在 errback 中先记录 repr(failure) 作为通用日志
- 使用 failure.check(HttpError) 分支，从 failure.value.response 获取非 200 响应
- 使用 failure.check(DNSLookupError) 分支，从 failure.request 获取原始请求
- 使用 failure.check(TimeoutError, TCPTimedOutError) 分支，从 failure.request 获取原始请求

## Workflow Steps

- 在构造 scrapy.Request 时传入 errback 参数指向错误处理函数
- 在 errback 函数中接收 failure 参数并记录 repr(failure)
- 按 failure.check() 判断异常类型并进入对应分支
- 在 HttpError 分支读取 failure.value.response 并记录其 URL
- 在 DNSLookupError 与 TimeoutError/TCPTimedOutError 分支读取 failure.request 并记录其 URL

## Constraints

- errback 必须与请求一同配置，否则失败不会进入自定义处理
- 分支判断应使用 failure.check() 而非直接比较异常类型

## Cautions

- 不同异常类型可获取的对象不同：HttpError 提供 response，DNS/超时提供 request
- 未覆盖的异常类型应保留通用日志以便排查

## Output Contract

- 按失败类型分支处理的 errback 函数及对应日志输出

## Example Therapist Responses

### Example 1

- Client/Input: 请求失败并触发 errback，failure 为 HttpError
- Therapist/Output: 记录 repr(failure)，并从 failure.value.response 取非 200 响应，记录 "HttpError on <url>"
- Notes: HttpError 分支可访问响应对象

### Example 2

- Client/Input: 请求失败并触发 errback，failure 为 DNSLookupError
- Therapist/Output: 记录 repr(failure)，并从 failure.request 取原始请求，记录 "DNSLookupError on <url>"
- Notes: DNS 分支只能访问原始请求

### Example 3

- Client/Input: 请求失败并触发 errback，failure 为 TimeoutError 或 TCPTimedOutError
- Therapist/Output: 记录 repr(failure)，并从 failure.request 取原始请求，记录 "TimeoutError on <url>"
- Notes: 超时分支只能访问原始请求

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要区分 HTTP 错误、DNS 错误、超时等不同失败类型
- 希望在请求失败时记录日志或产出诊断数据

## Examples

### Example 1

Input:

  请求失败并触发 errback，failure 为 HttpError

Output:

  记录 repr(failure)，并从 failure.value.response 取非 200 响应，记录 "HttpError on <url>"

Notes:

  HttpError 分支可访问响应对象

### Example 2

Input:

  请求失败并触发 errback，failure 为 DNSLookupError

Output:

  记录 repr(failure)，并从 failure.request 取原始请求，记录 "DNSLookupError on <url>"

Notes:

  DNS 分支只能访问原始请求

### Example 3

Input:

  请求失败并触发 errback，failure 为 TimeoutError 或 TCPTimedOutError

Output:

  记录 repr(failure)，并从 failure.request 取原始请求，记录 "TimeoutError on <url>"

Notes:

  超时分支只能访问原始请求
