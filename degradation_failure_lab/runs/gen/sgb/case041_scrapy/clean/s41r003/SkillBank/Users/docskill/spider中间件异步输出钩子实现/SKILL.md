---
id: "d019dfc8-693e-5c16-a087-b34f745060b8"
name: "Spider中间件异步输出钩子实现"
description: "实现 process_spider_output_async 异步生成器方法，在 Spider 输出结果为异步可迭代对象时替代同步 process_spider_output 被调用，用于异步爬虫管道中处理异步结果流。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider_middleware"
  - "async"
  - "process_spider_output_async"
triggers:
  - "Spider 输出结果为异步可迭代对象"
  - "需要异步生成器形式的输出处理"
  - "异步爬虫管道中需处理异步结果流"
examples:
  - input: "Spider 返回异步可迭代的 result"
    output: "process_spider_output_async(response, result) 作为异步生成器被调用并产出 Request 与 item"
    notes: "仅在 result 为异步可迭代时触发"
---

# Spider中间件异步输出钩子实现

实现 process_spider_output_async 异步生成器方法，在 Spider 输出结果为异步可迭代对象时替代同步 process_spider_output 被调用，用于异步爬虫管道中处理异步结果流。

## Prompt

在 Spider 中间件中定义 async 生成器方法 process_spider_output_async(response, result)。当 Spider 返回的 result 为异步可迭代对象时，Scrapy 会调用该方法而非 process_spider_output。方法需以异步生成器形式产出 Request 对象与 item 对象，保持与同步输出钩子一致的输出语义。

## Objective

在异步结果流场景下提供异步输出处理
## Applicable Signals

- Spider 输出结果为异步可迭代对象
- 需要异步生成器形式的输出处理

## Contraindications

- 结果为同步可迭代对象
- 未启用异步爬虫管道

## Intervention Moves

- 定义 async 生成器方法 process_spider_output_async(response, result)
- 在方法内异步产出 Request 对象与 item 对象
- 确保仅在 result 为异步可迭代时依赖该钩子

## Workflow Steps

- 确认 Spider 输出 result 为异步可迭代对象
- 在中间件中定义 async 生成器方法 process_spider_output_async(response, result)
- 在生成器中产出 Request 对象与 item 对象
- 验证异步结果流被正确传递至后续中间件

## Constraints

- 方法必须为异步生成器
- 仅在 result 为异步可迭代对象时被调用，替代 process_spider_output

## Cautions

- 同步结果流仍走 process_spider_output，不应依赖异步钩子处理

## Output Contract

- 定义可被调用的异步生成器方法 process_spider_output_async，产出 Request 与 item 对象

## Example Therapist Responses

### Example 1

- Client/Input: Spider 返回异步可迭代的 result
- Therapist/Output: process_spider_output_async(response, result) 作为异步生成器被调用并产出 Request 与 item
- Notes: 仅在 result 为异步可迭代时触发

## Triggers

- Spider 输出结果为异步可迭代对象
- 需要异步生成器形式的输出处理
- 异步爬虫管道中需处理异步结果流

## Examples

### Example 1

Input:

  Spider 返回异步可迭代的 result

Output:

  process_spider_output_async(response, result) 作为异步生成器被调用并产出 Request 与 item

Notes:

  仅在 result 为异步可迭代时触发
