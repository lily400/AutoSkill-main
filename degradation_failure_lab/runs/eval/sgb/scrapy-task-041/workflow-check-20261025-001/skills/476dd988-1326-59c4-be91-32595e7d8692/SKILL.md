---
id: "476dd988-1326-59c4-be91-32595e7d8692"
name: "Request errback 异常捕获处理"
description: "为 Scrapy Request 配置 errback 回调以捕获请求处理过程中的异常，并在 errback 中访问 meta 附加数据进行失败分支处理。适用于需要逐请求容错与失败分支处理的爬取流程。"
version: "0.1.0"
tags:
  - "scrapy"
  - "errback"
  - "异常处理"
  - "request"
  - "meta"
triggers:
  - "请求可能失败需要失败分支处理"
  - "需要在异常时读取 meta 附加数据"
  - "需要为单个 Request 定制错误处理逻辑"
examples:
  - input: "某请求可能失败，且需要在失败时读取 meta 中的分类信息"
    output: "构造 Request 时传入 errback，errback 中读取 request.meta 的分类信息并记录或重试"
    notes: "附加数据需在发起请求时通过 meta 传入"
---

# Request errback 异常捕获处理

为 Scrapy Request 配置 errback 回调以捕获请求处理过程中的异常，并在 errback 中访问 meta 附加数据进行失败分支处理。适用于需要逐请求容错与失败分支处理的爬取流程。

## Prompt

当某个 Request 可能失败且需要独立的失败分支处理时，为其绑定 errback 回调。在 errback 中接收 failure 对象，读取 request.meta 中的附加数据以区分上下文，并执行相应的错误处理逻辑（记录、重试或降级）。仅在需要逐请求失败处理时使用；若异常已由中间件统一处理或仅需成功回调，则不要额外配置 errback。

## Objective

通过 errback 捕获并处理请求异常
## Applicable Signals

- 请求可能失败需要失败分支处理
- 需要在异常时读取 meta 附加数据

## Contraindications

- 仅需正常成功回调处理
- 异常由中间件统一处理无需逐请求配置

## Intervention Moves

- 在构造 Request 时传入 errback 参数绑定异常处理函数
- 在 errback 函数中接收 failure 对象并读取 request.meta 附加数据
- 根据 meta 上下文执行记录、重试或降级等错误处理

## Workflow Steps

- 判断该请求是否需要独立的失败分支处理
- 构造 Request 时通过 errback 参数绑定异常处理函数
- 在 errback 中接收 failure 对象并访问 request.meta 中的附加数据
- 依据附加数据执行相应的错误处理逻辑

## Constraints

- errback 仅处理该 Request 的失败分支，不替代正常 callback 流程
- 附加数据需在发起请求时通过 meta 传入，errback 中方可读取

## Cautions

- 若异常已由中间件统一处理，逐请求配置 errback 可能造成重复处理
- errback 中应避免吞掉异常而不做任何记录或降级

## Output Contract

- 绑定 errback 的 Request 及对应的异常处理逻辑，失败时可读取 meta 附加数据并执行错误处理

## Example Therapist Responses

### Example 1

- Client/Input: 某请求可能失败，且需要在失败时读取 meta 中的分类信息
- Therapist/Output: 构造 Request 时传入 errback，errback 中读取 request.meta 的分类信息并记录或重试
- Notes: 附加数据需在发起请求时通过 meta 传入

## Triggers

- 请求可能失败需要失败分支处理
- 需要在异常时读取 meta 附加数据
- 需要为单个 Request 定制错误处理逻辑

## Examples

### Example 1

Input:

  某请求可能失败，且需要在失败时读取 meta 中的分类信息

Output:

  构造 Request 时传入 errback，errback 中读取 request.meta 的分类信息并记录或重试

Notes:

  附加数据需在发起请求时通过 meta 传入
