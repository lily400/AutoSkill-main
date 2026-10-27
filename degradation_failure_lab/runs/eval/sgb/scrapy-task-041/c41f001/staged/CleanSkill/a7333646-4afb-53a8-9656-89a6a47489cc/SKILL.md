---
id: "a7333646-4afb-53a8-9656-89a6a47489cc"
name: "Spider输出处理钩子实现"
description: "实现 process_spider_output(response, result) 钩子，对 Spider 处理响应后返回的 Request/item 可迭代结果进行拦截与改写，并返回新的可迭代对象。适用于需要在爬虫输出进入后续中间件前统一过滤或转换结果的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider_middleware"
  - "process_spider_output"
  - "hook"
triggers:
  - "需要过滤或改写 Spider 产出的 Request/item"
  - "需要在输出进入下游中间件前统一处理结果"
---

# Spider输出处理钩子实现

实现 process_spider_output(response, result) 钩子，对 Spider 处理响应后返回的 Request/item 可迭代结果进行拦截与改写，并返回新的可迭代对象。适用于需要在爬虫输出进入后续中间件前统一过滤或转换结果的场景。

## Prompt

实现 process_spider_output(response, result) 钩子：接收当前 response 与 Spider 返回的 result（Request 与 item 对象的可迭代对象），对结果流进行过滤或改写，并返回一个由 Request 对象和 item 对象组成的可迭代对象。确保返回值符合契约，供后续 Spider 中间件继续处理。

## Objective

在 Spider 输出阶段拦截并改写 Request/item 结果流
## Applicable Signals

- Spider 已处理响应并返回结果流
- 需要在结果流进入后续中间件前介入

## Contraindications

- 处理的是下载器请求/响应阶段而非 Spider 输出
- 仅需记录日志而无需改变结果流

## Intervention Moves

- 定义 process_spider_output(response, result) 方法
- 遍历 result 中的 Request 与 item 对象
- 按需过滤或转换结果
- 返回新的 Request/item 可迭代对象

## Workflow Steps

- 实现 process_spider_output(response, result) 方法，接收 response 与 Spider 返回的 result
- 对 result 中的 Request 对象和 item 对象进行过滤或改写
- 返回由 Request 对象和 item 对象组成的可迭代对象

## Constraints

- process_spider_output 必须返回 Request 对象和 item 对象的可迭代对象
- response 为生成该输出的响应对象
- result 为 Spider 返回的可迭代结果

## Cautions

- 若 result 为异步可迭代对象，需改用 process_spider_output_async 异步生成器变体
- 异常处理应使用 process_spider_exception，而非在输出钩子中吞掉异常

## Output Contract

- 返回符合契约的 Request/item 可迭代对象

## Triggers

- 需要过滤或改写 Spider 产出的 Request/item
- 需要在输出进入下游中间件前统一处理结果
