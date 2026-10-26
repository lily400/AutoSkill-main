---
id: "248800e8-c919-5bb2-98b0-92a341972f97"
name: "Scrapy 请求 errback 失败处理"
description: "为 Scrapy 请求设置 errback 回调，在请求处理失败时接收 Failure 对象并执行降级、重试或记录；适用于需要容错处理的抓取请求。"
version: "0.1.0"
tags:
  - "scrapy"
  - "errback"
  - "异常处理"
  - "请求失败"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "请求可能失败需要容错"
  - "需要在失败时读取请求附加数据"
  - "需要为请求指定失败处理回调"
examples:
  - input: "构造一个可能失败的请求并需要失败时记录"
    output: "在 Request 中设置 errback 指向处理函数，函数接收 Failure 并记录失败信息"
    notes: "errback 默认 None，需显式指定"
---

# Scrapy 请求 errback 失败处理

为 Scrapy 请求设置 errback 回调，在请求处理失败时接收 Failure 对象并执行降级、重试或记录；适用于需要容错处理的抓取请求。

## Prompt

当请求可能失败且需要容错时，在构造 Request 时通过 errback 参数指定回调函数。errback 接收 Failure 对象，可在其中读取请求附加数据（如 cb_kwargs 或 meta）以完成降级、重试或记录。仅处理失败路径，不替代成功回调。

## Objective

在请求失败时通过 errback 捕获并处理异常
## Applicable Signals

- 请求可能失败需要容错
- 需要在失败时读取请求附加数据

## Contraindications

- 请求无需失败处理
- 仅处理成功响应

## Intervention Moves

- 在 Request 构造时设置 errback 参数指向处理函数
- errback 函数接收 Failure 对象并据此执行降级或记录
- 在 errback 中访问请求附加数据（cb_kwargs 或 meta）

## Workflow Steps

- 判断该请求是否需要失败容错处理
- 构造 Request 时通过 errback 参数指定失败处理函数
- 在 errback 函数中接收 Failure 对象
- 根据 Failure 与请求附加数据执行降级、重试或记录

## Constraints

- errback 默认值为 None，需显式设置才会触发失败处理
- errback 仅处理失败路径，成功响应仍由 callback 处理

## Cautions

- 通过 Cookie 头设置的 cookie 不被 CookiesMiddleware 识别，如需设置 cookie 应使用 Request.cookies 参数

## Output Contract

- errback 函数接收 Failure 并完成降级或记录

## Example Therapist Responses

### Example 1

- Client/Input: 构造一个可能失败的请求并需要失败时记录
- Therapist/Output: 在 Request 中设置 errback 指向处理函数，函数接收 Failure 并记录失败信息
- Notes: errback 默认 None，需显式指定

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 请求可能失败需要容错
- 需要在失败时读取请求附加数据
- 需要为请求指定失败处理回调

## Examples

### Example 1

Input:

  构造一个可能失败的请求并需要失败时记录

Output:

  在 Request 中设置 errback 指向处理函数，函数接收 Failure 并记录失败信息

Notes:

  errback 默认 None，需显式指定
