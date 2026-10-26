---
id: "447019bb-4d06-58fd-92a7-55b05d0d4e9b"
name: "下载器中间件 process_response 返回值路由"
description: "在下载器中间件的 process_response 钩子中，根据返回值类型决定后续链路走向：返回 Response 继续交给下一个中间件处理，返回 Request 中止链路并重新调度下载，抛出 IgnoreRequest 触发请求的 errback。用于编写或调试响应处理中间件时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "downloader_middleware"
  - "process_response"
  - "返回值分派"
triggers:
  - "编写或修改 process_response 方法"
  - "需要根据响应结果决定继续、重调度或触发 errback"
  - "调试下载器中间件响应阶段的路由行为"
examples:
  - input: "希望响应继续被后续中间件处理"
    output: "返回 Response（原响应或新响应）"
    notes: "链路交给下一个中间件的 process_response"
  - input: "希望中止当前链路并重新下载"
    output: "返回 Request"
    notes: "该请求被重新调度下载"
  - input: "希望放弃该请求"
    output: "抛出 IgnoreRequest"
    notes: "调用 Request.errback；无处理则被忽略且不记录日志"
---

# 下载器中间件 process_response 返回值路由

在下载器中间件的 process_response 钩子中，根据返回值类型决定后续链路走向：返回 Response 继续交给下一个中间件处理，返回 Request 中止链路并重新调度下载，抛出 IgnoreRequest 触发请求的 errback。用于编写或调试响应处理中间件时。

## Prompt

实现或调试 process_response(request, response) 时，先明确本次要达成的路由目标，再选择返回值类型：
1) 若需继续处理响应，返回 Response（可为原响应或全新响应），链路将交给下一个中间件的 process_response。
2) 若需中止当前链路并重新下载，返回 Request，行为等同于 process_request 返回 Request，该请求被重新调度。
3) 若需放弃该请求，抛出 IgnoreRequest，将调用 Request.errback；若无代码处理该异常，则被忽略且不记录日志（与其他异常不同）。
确保返回值类型与预期链路行为一致，避免返回非法类型。

## Objective

按返回值类型正确路由 process_response 的后续处理
## Applicable Signals

- 正在实现 process_response 钩子
- 需要根据响应结果决定继续、重调度或触发 errback

## Contraindications

- 处理请求阶段逻辑（应使用 process_request）
- 处理异常阶段逻辑（应使用 process_exception）

## Intervention Moves

- 返回 Response 以继续交给下一个中间件
- 返回 Request 以中止链路并重新调度下载
- 抛出 IgnoreRequest 以触发请求的 errback

## Workflow Steps

- 确认本次 process_response 的路由目标（继续、重调度或放弃）
- 按目标选择返回值：Response 继续、Request 重调度、IgnoreRequest 触发 errback
- 核对返回值类型与预期链路行为一致

## Constraints

- process_response 只能返回 Response、返回 Request 或抛出 IgnoreRequest
- 返回 Request 会中止中间件链并重新调度下载
- 抛出 IgnoreRequest 时若无代码处理则被忽略且不记录日志

## Cautions

- 返回 Request 的行为等同于 process_request 返回 Request，需注意重调度影响
- IgnoreRequest 未被处理时静默忽略，可能掩盖问题

## Output Contract

- process_response 返回 Response/Request 或抛出 IgnoreRequest，且链路行为符合预期

## Example Therapist Responses

### Example 1

- Client/Input: 希望响应继续被后续中间件处理
- Therapist/Output: 返回 Response（原响应或新响应）
- Notes: 链路交给下一个中间件的 process_response

### Example 2

- Client/Input: 希望中止当前链路并重新下载
- Therapist/Output: 返回 Request
- Notes: 该请求被重新调度下载

### Example 3

- Client/Input: 希望放弃该请求
- Therapist/Output: 抛出 IgnoreRequest
- Notes: 调用 Request.errback；无处理则被忽略且不记录日志

## Triggers

- 编写或修改 process_response 方法
- 需要根据响应结果决定继续、重调度或触发 errback
- 调试下载器中间件响应阶段的路由行为

## Examples

### Example 1

Input:

  希望响应继续被后续中间件处理

Output:

  返回 Response（原响应或新响应）

Notes:

  链路交给下一个中间件的 process_response

### Example 2

Input:

  希望中止当前链路并重新下载

Output:

  返回 Request

Notes:

  该请求被重新调度下载

### Example 3

Input:

  希望放弃该请求

Output:

  抛出 IgnoreRequest

Notes:

  调用 Request.errback；无处理则被忽略且不记录日志
