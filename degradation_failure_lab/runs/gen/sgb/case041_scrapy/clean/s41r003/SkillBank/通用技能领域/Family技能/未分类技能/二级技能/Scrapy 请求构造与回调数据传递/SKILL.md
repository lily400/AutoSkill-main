---
id: "dc522835-58a3-552c-bd8b-30ad389282ea"
name: "Scrapy 请求构造与回调数据传递"
description: "构造 scrapy.Request 时正确设置 url、callback、errback、cb_kwargs、cookies、priority、dont_filter 等参数，并把附加数据通过 cb_kwargs 传给回调。适用于需要发起请求并向下游回调传递上下文数据的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "callback"
  - "cb_kwargs"
  - "cookies"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
  - "kind:parent"
triggers:
  - "需要发起新的抓取请求"
  - "需要向回调函数传递额外上下文数据"
---

# Scrapy 请求构造与回调数据传递

构造 scrapy.Request 时正确设置 url、callback、errback、cb_kwargs、cookies、priority、dont_filter 等参数，并把附加数据通过 cb_kwargs 传给回调。适用于需要发起请求并向下游回调传递上下文数据的场景。

## Prompt

在需要发起新的抓取请求时，构造 scrapy.Request 对象：明确设置 url；按需绑定 callback 与 errback；将需要传给回调的上下文数据放入 cb_kwargs（dict，会作为关键字参数传给 callback）；如需设置 cookie，使用 Request 的 cookies 参数而非 Cookie 头；按需设置 priority、dont_filter、encoding、flags 等参数。构造完成后确认回调与 cb_kwargs 已正确绑定。

## Objective

构造可正确路由回调并携带附加数据的 Scrapy 请求
## Applicable Signals

- 需要发起新的抓取请求
- 需要向回调函数传递额外上下文数据

## Contraindications

- 仅需解析已有响应
- 需要设置 Cookie 头而非 cookies 参数

## Intervention Moves

- 设置 url 参数
- 绑定 callback 与 errback
- 通过 cb_kwargs 传递附加数据给回调
- 使用 cookies 参数设置请求 cookie
- 按需设置 priority、dont_filter、encoding、flags

## Workflow Steps

- 确定请求目标 url
- 按需绑定 callback 与 errback
- 将需要传给回调的上下文数据放入 cb_kwargs
- 如需 cookie，使用 Request 的 cookies 参数而非 Cookie 头
- 按需设置 priority、dont_filter、encoding、flags 等参数
- 确认回调与 cb_kwargs 已正确绑定

## Constraints

- cb_kwargs 必须是 dict，会作为关键字参数传给 callback
- 设置 cookie 应使用 Request.cookies 参数，通过 Cookie 头设置的 cookie 不被 CookiesMiddleware 处理

## Cautions

- 通过 Cookie 头设置的 cookie 不被 CookiesMiddleware 考虑，这是已知限制

## Output Contract

- 一个配置完整、回调与 cb_kwargs 正确绑定的 Request 对象

## 子技能目录
- [Scrapy 请求 errback 失败处理](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求 errback 失败处理/SKILL.md) ｜ 适用：为 Scrapy 请求设置 errback 回调，在请求处理失败时接收 Failure 对象并执行降级、重试或记录；适用于需要容错处理的抓取请求。
- [从 cURL 命令构造 Scrapy Request](通用技能领域/Family技能/未分类技能/微技能/从 cURL 命令构造 Scrapy Request/SKILL.md) ｜ 适用：使用 Request.from_curl 从 cURL 命令字符串创建 Scrapy Request，自动填充 HTTP 方法、URL、头、cookie 和 body；当已有 cURL 命令（如从浏览器复制）需要转为 Scrapy 请求时使用。
- [通过 cb_kwargs 向回调传递附加数据](通用技能领域/Family技能/未分类技能/微技能/通过 cb_kwargs 向回调传递附加数据/SKILL.md) ｜ 适用：在构造 scrapy.Request 时使用 cb_kwargs 将上下文数据传入后续回调函数，并在回调中读取这些参数，实现跨请求的状态传递。适用于需要在第二个回调中复用第一个回调的上下文数据，或回调函数需要额外参数而非仅 response 的场景。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `Scrapy 请求 errback 失败处理` 时，优先调用它。 线索：请求可能失败需要容错, 需要在失败时读取请求附加数据, 需要为请求指定失败处理回调, scrapy, errback
- 当目标、阶段或方法更接近 `从 cURL 命令构造 Scrapy Request` 时，优先调用它。 线索：已有 cURL 命令需转为 Scrapy 请求, 需复用从浏览器复制的请求, scrapy, request, curl
- 当目标、阶段或方法更接近 `通过 cb_kwargs 向回调传递附加数据` 时，优先调用它。 线索：需要在第二个回调中复用第一个回调的上下文数据, 回调函数需要额外参数而非仅 response, scrapy, request, callback

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要发起新的抓取请求
- 需要向回调函数传递额外上下文数据
