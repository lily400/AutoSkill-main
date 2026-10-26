---
id: "be9aee15-e037-5420-b34a-eb9af1223666"
name: "process_request 请求拦截与分流"
description: "实现下载器中间件的 process_request 钩子，在请求进入下载器前按规则改写、重调度、短路或丢弃请求。适用于需要在下载前修改请求或按条件重定向、过滤请求的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "downloader-middleware"
  - "process_request"
  - "request_processing"
  - "hook_implementation"
triggers:
  - "需要在下载前修改请求"
  - "需要按条件重定向或丢弃请求"
  - "需要提前短路请求、跳过下载"
examples:
  - input: "请求需在下载前被改写后继续处理"
    output: "process_request 返回 None，Scrapy 继续执行其余中间件直至下载"
    notes: "继续处理路径"
  - input: "请求需被重定向到新地址"
    output: "process_request 返回新的 Request 对象，Scrapy 停止调用后续 process_request 并重新调度"
    notes: "重调度路径"
  - input: "请求应被过滤丢弃"
    output: "process_request 抛出 IgnoreRequest"
    notes: "丢弃路径"
---

# process_request 请求拦截与分流

实现下载器中间件的 process_request 钩子，在请求进入下载器前按规则改写、重调度、短路或丢弃请求。适用于需要在下载前修改请求或按条件重定向、过滤请求的场景。

## Prompt

实现 process_request(request) 方法，根据业务规则选择四种返回值之一：返回 None 表示继续沿中间件链处理该请求；返回 Request 对象表示停止调用后续 process_request 并重新调度该请求；返回 Response 对象表示提前短路、跳过下载；抛出 IgnoreRequest 表示丢弃该请求。方法可定义为协程函数（async def）。确保每个分支逻辑明确、互斥且可预测。

## Objective

在请求进入下载器前按规则改写、重调度、短路或丢弃请求
## Applicable Signals

- 需要在下载前修改请求
- 需要按条件重定向或丢弃请求
- 需要提前短路请求、跳过下载

## Contraindications

- 只需处理已下载的响应
- 需要跨阶段编排整个中间件链

## Intervention Moves

- 返回 None 继续处理该请求
- 返回 Request 对象以停止后续 process_request 并重新调度
- 返回 Response 对象以提前短路、跳过下载
- 抛出 IgnoreRequest 以丢弃该请求

## Workflow Steps

- 在下载器中间件组件中定义 process_request(request) 方法
- 根据业务规则判断应继续、重调度、短路还是丢弃
- 返回 None 继续沿中间件链处理
- 返回 Request 对象以重新调度该请求
- 返回 Response 对象以提前短路
- 抛出 IgnoreRequest 以丢弃请求

## Constraints

- process_request 只能返回 None、Response、Request 或抛出 IgnoreRequest
- 返回 Request 时会停止调用后续 process_request 方法并重新调度该请求
- 方法可定义为协程函数（async def）

## Cautions

- 返回 Request 会中断当前中间件链，需确认重调度不会造成循环
- 部分中间件可能需通过特定设置启用

## Output Contract

- process_request 方法返回 None/Request/Response 或抛出 IgnoreRequest 的明确分支逻辑

## Example Therapist Responses

### Example 1

- Client/Input: 请求需在下载前被改写后继续处理
- Therapist/Output: process_request 返回 None，Scrapy 继续执行其余中间件直至下载
- Notes: 继续处理路径

### Example 2

- Client/Input: 请求需被重定向到新地址
- Therapist/Output: process_request 返回新的 Request 对象，Scrapy 停止调用后续 process_request 并重新调度
- Notes: 重调度路径

### Example 3

- Client/Input: 请求应被过滤丢弃
- Therapist/Output: process_request 抛出 IgnoreRequest
- Notes: 丢弃路径

## Triggers

- 需要在下载前修改请求
- 需要按条件重定向或丢弃请求
- 需要提前短路请求、跳过下载

## Examples

### Example 1

Input:

  请求需在下载前被改写后继续处理

Output:

  process_request 返回 None，Scrapy 继续执行其余中间件直至下载

Notes:

  继续处理路径

### Example 2

Input:

  请求需被重定向到新地址

Output:

  process_request 返回新的 Request 对象，Scrapy 停止调用后续 process_request 并重新调度

Notes:

  重调度路径

### Example 3

Input:

  请求应被过滤丢弃

Output:

  process_request 抛出 IgnoreRequest

Notes:

  丢弃路径
