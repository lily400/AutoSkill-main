---
id: "20f141fe-1520-568d-a0ef-844224151e15"
name: "Spider 中间件异常处理钩子实现"
description: "实现 process_spider_exception 钩子，在 Spider 或上游 process_spider_output 抛异常时，决定返回 None 让异常继续传播，或返回 Request/item 可迭代对象接管输出管道。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider_middleware"
  - "exception_handling"
  - "process_spider_exception"
triggers:
  - "需要捕获并处理 Spider 或 process_spider_output 抛出的异常"
  - "需要决定异常是否继续传播至引擎"
  - "需要在中间件层集中接管爬虫阶段异常并恢复输出流"
examples:
  - input: "Spider 处理响应时抛出异常，本中间件希望让引擎记录丢弃"
    output: "process_spider_exception 返回 None"
    notes: "异常继续传播至引擎"
  - input: "Spider 处理响应时抛出异常，本中间件希望恢复输出流"
    output: "process_spider_exception 返回包含 Request 或 item 的可迭代对象"
    notes: "process_spider_output 从下一个中间件开始执行"
---

# Spider 中间件异常处理钩子实现

实现 process_spider_exception 钩子，在 Spider 或上游 process_spider_output 抛异常时，决定返回 None 让异常继续传播，或返回 Request/item 可迭代对象接管输出管道。

## Prompt

在自定义 Spider 中间件中实现 process_spider_exception(response, exception) 钩子。判断当前异常是否应由本中间件接管：若需继续传播，返回 None，Scrapy 会继续调用后续中间件的 process_spider_exception，直至异常到达引擎被记录并丢弃；若需接管，返回一个 Request 或 item 对象的可迭代对象，此时 process_spider_output 管道从下一个中间件开始执行，且不再调用其他 process_spider_exception。确保返回值类型符合契约，不要返回非可迭代的单个对象。

## Objective

在 Spider 阶段异常时选择继续传播或接管输出
## Applicable Signals

- Spider 或上游 process_spider_output 抛出异常
- 需要自定义异常走向而非默认记录丢弃
- 需要在异常后恢复 Request/item 输出流

## Contraindications

- 处理正常输出流而非异常时应使用 process_spider_output
- 异常应直接交由引擎记录丢弃时无需实现该钩子

## Intervention Moves

- 实现 process_spider_exception(response, exception) 方法
- 判断异常是否由本中间件接管
- 返回 None 表示继续传播
- 返回 Request/item 可迭代对象表示接管并进入 process_spider_output 管道

## Workflow Steps

- 定义 process_spider_exception(response, exception) 方法
- 根据 response 与 exception 判断是否接管
- 若继续传播则返回 None
- 若接管则返回 Request 或 item 对象的可迭代对象
- 确认接管后 process_spider_output 从下一个中间件开始执行且不再调用其他 process_spider_exception

## Constraints

- 返回值只能是 None 或 Request/item 的可迭代对象
- 返回 None 时异常继续沿中间件链传播至引擎
- 返回可迭代对象时不再调用其他 process_spider_exception

## Cautions

- 返回非可迭代的单个对象会违反返回契约
- 接管异常会跳过后续中间件的异常处理钩子

## Output Contract

- 返回 None 或 Request/item 可迭代对象以明确异常走向

## Example Therapist Responses

### Example 1

- Client/Input: Spider 处理响应时抛出异常，本中间件希望让引擎记录丢弃
- Therapist/Output: process_spider_exception 返回 None
- Notes: 异常继续传播至引擎

### Example 2

- Client/Input: Spider 处理响应时抛出异常，本中间件希望恢复输出流
- Therapist/Output: process_spider_exception 返回包含 Request 或 item 的可迭代对象
- Notes: process_spider_output 从下一个中间件开始执行

## Triggers

- 需要捕获并处理 Spider 或 process_spider_output 抛出的异常
- 需要决定异常是否继续传播至引擎
- 需要在中间件层集中接管爬虫阶段异常并恢复输出流

## Examples

### Example 1

Input:

  Spider 处理响应时抛出异常，本中间件希望让引擎记录丢弃

Output:

  process_spider_exception 返回 None

Notes:

  异常继续传播至引擎

### Example 2

Input:

  Spider 处理响应时抛出异常，本中间件希望恢复输出流

Output:

  process_spider_exception 返回包含 Request 或 item 的可迭代对象

Notes:

  process_spider_output 从下一个中间件开始执行
