---
id: "65e1a9ed-69fb-5e8d-87f3-1bf759519ddd"
name: "Scrapy Request 回调与错误回调路由配置"
description: "为 Scrapy Request 指定 callback 或 errback，并处理 None/NO_CALLBACK 默认行为，使响应或异常被路由到正确的处理函数。适用于需要自定义响应处理或捕获请求处理异常的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "callback"
  - "errback"
  - "路由"
triggers:
  - "需要自定义响应处理函数"
  - "需要捕获请求处理异常"
  - "需要显式声明不回调"
examples:
  - input: "需要自定义响应处理函数"
    output: "Request(url, callback=self.custom_parse)"
  - input: "需要捕获请求处理异常"
    output: "Request(url, callback=self.parse, errback=self.handle_error)"
---

# Scrapy Request 回调与错误回调路由配置

为 Scrapy Request 指定 callback 或 errback，并处理 None/NO_CALLBACK 默认行为，使响应或异常被路由到正确的处理函数。适用于需要自定义响应处理或捕获请求处理异常的场景。

## Prompt

在构造 Scrapy Request 时，明确指定 callback 用于处理正常响应、errback 用于处理异常。若 callback 为 None（默认），则响应交由 spider 的 parse() 方法处理；若使用 NO_CALLBACK()，则显式声明不回调。注意 HttpErrorMiddleware 默认对非 2xx 响应抛出异常并转交 errback，因此需要捕获 HTTP 错误时应配置 errback。

## Objective

正确配置请求的回调与错误回调路由
## Applicable Signals

- 需要自定义响应处理函数
- 需要捕获请求处理异常
- 需要显式声明不回调

## Contraindications

- 使用默认 parse 即可满足需求

## Intervention Moves

- 为 Request 指定 callback 处理正常响应
- 为 Request 指定 errback 处理异常
- 使用 None 默认交由 parse() 处理
- 使用 NO_CALLBACK() 显式声明不回调

## Workflow Steps

- 判断是否需要自定义响应处理：若默认 parse() 足够，则 callback 保持 None。
- 若需自定义处理，指定 callback 为对应处理函数。
- 若需捕获请求处理异常，指定 errback 为异常处理函数。
- 若需显式声明不回调，使用 NO_CALLBACK()。
- 注意 HttpErrorMiddleware 默认对非 2xx 响应抛出异常并转交 errback，据此配置错误处理。

## Constraints

- callback 为 None 时响应交由 spider 的 parse() 方法处理
- NO_CALLBACK() 用于显式声明不回调

## Cautions

- HttpErrorMiddleware 默认对非 2xx 响应抛出异常并发送到 errback，未配置 errback 时异常可能未被捕获

## Output Contract

- Request 携带正确的 callback/errback 配置

## Example Therapist Responses

### Example 1

- Client/Input: 需要自定义响应处理函数
- Therapist/Output: Request(url, callback=self.custom_parse)

### Example 2

- Client/Input: 需要捕获请求处理异常
- Therapist/Output: Request(url, callback=self.parse, errback=self.handle_error)

## Triggers

- 需要自定义响应处理函数
- 需要捕获请求处理异常
- 需要显式声明不回调

## Examples

### Example 1

Input:

  需要自定义响应处理函数

Output:

  Request(url, callback=self.custom_parse)

### Example 2

Input:

  需要捕获请求处理异常

Output:

  Request(url, callback=self.parse, errback=self.handle_error)
