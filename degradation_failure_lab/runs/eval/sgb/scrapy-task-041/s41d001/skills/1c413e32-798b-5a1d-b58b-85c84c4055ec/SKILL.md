---
id: "1c413e32-798b-5a1d-b58b-85c84c4055ec"
name: "通过 cb_kwargs 向回调传递附加数据"
description: "在构造 scrapy.Request 时使用 cb_kwargs 将上下文数据传入后续回调函数，并在回调中读取这些参数，实现跨请求的状态传递。适用于需要在第二个回调中复用第一个回调的上下文数据，或回调函数需要额外参数而非仅 response 的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "callback"
  - "cb_kwargs"
  - "状态传递"
triggers:
  - "需要在第二个回调中复用第一个回调的上下文数据"
  - "回调函数需要额外参数而非仅 response"
examples:
  - input: "def parse(self, response):\n    request = scrapy.Request(\n        \"http://www.example.com/index.html\",\n        callback=self.parse_page2,\n        cb_kwargs=dict(main_url=response.url),\n    )\n    request.cb_kwargs[\"foo\"] = \"bar\"\n    yield request"
    output: "parse_page2 回调被调用时可读取 main_url 与 foo 参数"
    notes: "在 yield 前可继续向 cb_kwargs 追加参数"
---

# 通过 cb_kwargs 向回调传递附加数据

在构造 scrapy.Request 时使用 cb_kwargs 将上下文数据传入后续回调函数，并在回调中读取这些参数，实现跨请求的状态传递。适用于需要在第二个回调中复用第一个回调的上下文数据，或回调函数需要额外参数而非仅 response 的场景。

## Prompt

当需要在请求链的回调之间传递附加数据时：1) 在构造 scrapy.Request 时通过 cb_kwargs 传入字典参数；2) 可在 yield 前继续向 request.cb_kwargs 追加更多参数；3) 在目标回调函数签名中声明对应参数名以接收这些值。仅在数据无法从 response 本身获取时使用。

## Objective

在请求链的回调之间可靠传递附加参数
## Applicable Signals

- 回调函数需要接收 response 之外的上下文数据
- 需要在后续回调中复用前一回调获得的信息

## Contraindications

- 无需跨回调传递数据时
- 参数可通过 response 本身获取时

## Intervention Moves

- 在 scrapy.Request 构造时设置 cb_kwargs=dict(...)
- 在 yield 前向 request.cb_kwargs 追加额外键值
- 在目标回调函数签名中声明对应参数以接收数据

## Workflow Steps

- 确认目标回调需要 response 之外的附加数据
- 在构造 Request 时通过 cb_kwargs 传入字典
- 如需追加参数，在 yield 前修改 request.cb_kwargs
- 在回调函数签名中声明对应参数名接收数据

## Constraints

- cb_kwargs 仅用于回调参数传递，不用于请求序列化或异常处理
- 参数键名需与回调函数签名一致

## Cautions

- 避免将可通过 response 获取的数据重复放入 cb_kwargs

## Output Contract

- 回调函数成功接收到 cb_kwargs 中的参数

## Example Therapist Responses

### Example 1

- Client/Input: def parse(self, response):
    request = scrapy.Request(
        "http://www.example.com/index.html",
        callback=self.parse_page2,
        cb_kwargs=dict(main_url=response.url),
    )
    request.cb_kwargs["foo"] = "bar"
    yield request
- Therapist/Output: parse_page2 回调被调用时可读取 main_url 与 foo 参数
- Notes: 在 yield 前可继续向 cb_kwargs 追加参数

## Triggers

- 需要在第二个回调中复用第一个回调的上下文数据
- 回调函数需要额外参数而非仅 response

## Examples

### Example 1

Input:

  def parse(self, response):
      request = scrapy.Request(
          "http://www.example.com/index.html",
          callback=self.parse_page2,
          cb_kwargs=dict(main_url=response.url),
      )
      request.cb_kwargs["foo"] = "bar"
      yield request

Output:

  parse_page2 回调被调用时可读取 main_url 与 foo 参数

Notes:

  在 yield 前可继续向 cb_kwargs 追加参数
