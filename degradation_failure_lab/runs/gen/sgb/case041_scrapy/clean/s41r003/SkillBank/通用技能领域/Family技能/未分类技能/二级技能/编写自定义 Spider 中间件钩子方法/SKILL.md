---
id: "89ce30fa-7ffc-51bf-92e6-d77f76cb9f7c"
name: "编写自定义 Spider 中间件钩子方法"
description: "实现 SpiderMiddleware 子类的钩子方法（process_start、process_start_requests、process_spider_input），用于定制 Spider 启动输出、进入 Spider 的响应以及 Spider 产出的请求与 item 的处理逻辑。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider-middleware"
  - "hook-method"
  - "middleware_implementation"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
  - "kind:parent"
triggers:
  - "需要拦截并处理发往 Spider 的响应"
  - "需要处理 Spider 生成的请求或 item"
  - "需要定制 Spider 启动输出"
examples:
  - input: "需要处理 Spider 启动输出"
    output: "async def process_start(self, start):\n    async for item_or_request in start:\n        yield item_or_request"
    notes: "兼容旧版本可另加同步 process_start_requests"
  - input: "需要处理进入 Spider 的响应"
    output: "实现 process_spider_input(response)，返回 None 继续处理或抛出异常中断"
---

# 编写自定义 Spider 中间件钩子方法

实现 SpiderMiddleware 子类的钩子方法（process_start、process_start_requests、process_spider_input），用于定制 Spider 启动输出、进入 Spider 的响应以及 Spider 产出的请求与 item 的处理逻辑。

## Prompt

实现一个 SpiderMiddleware 子类，按需覆盖一个或多个钩子方法：
1. 继承 scrapy.spidermiddlewares.SpiderMiddleware。
2. 若需处理 Spider 启动输出，实现 async process_start(start)，遍历 start 并 yield 与 start 相同类型的对象；如需兼容 2.13 以下版本，另实现同步 process_start_requests(start, spider) 并 yield from start。
3. 若需处理进入 Spider 的响应，实现 process_spider_input(response)，返回 None 表示继续处理，或抛出异常中断。
4. 仅实现当前需求所需的钩子，保持方法职责单一。
5. 完成后交由注册配置环节将类路径写入 SPIDER_MIDDLEWARES。

## Objective

实现一个或多个 Spider 中间件钩子方法以定制处理流程
## Applicable Signals

- 需要拦截并处理发往 Spider 的响应
- 需要处理 Spider 生成的请求或 item
- 需要定制 Spider 启动输出

## Contraindications

- 仅需调整已有中间件顺序而无需新逻辑

## Intervention Moves

- 继承 SpiderMiddleware 基类
- 实现 async process_start 遍历并 yield 启动输出
- 为旧版本补充同步 process_start_requests
- 实现 process_spider_input 返回 None 或抛出异常

## Workflow Steps

- 确认需要定制的处理点（启动输出、进入响应、产出请求/item）
- 创建继承 SpiderMiddleware 的子类
- 按需实现对应钩子方法
- 确保 process_spider_input 返回 None 或抛出异常
- 将类路径交由注册配置环节写入 SPIDER_MIDDLEWARES

## Constraints

- process_spider_input 只能返回 None 或抛出异常
- process_start 需为 async 并 yield 与 start 相同类型的对象
- 兼容旧版本时需额外提供同步 process_start_requests

## Cautions

- 部分中间件可能还需通过特定设置启用，需查阅对应中间件文档

## Output Contract

- 可注册的 SpiderMiddleware 子类，含已实现的钩子方法

## Example Therapist Responses

### Example 1

- Client/Input: 需要处理 Spider 启动输出
- Therapist/Output: async def process_start(self, start):
    async for item_or_request in start:
        yield item_or_request
- Notes: 兼容旧版本可另加同步 process_start_requests

### Example 2

- Client/Input: 需要处理进入 Spider 的响应
- Therapist/Output: 实现 process_spider_input(response)，返回 None 继续处理或抛出异常中断

## 子技能目录
- [process_spider_input 返回值契约](通用技能领域/Family技能/未分类技能/微技能/process_spider_input 返回值契约/SKILL.md) ｜ 适用：确保自定义 Spider 中间件的 process_spider_input 钩子符合 Scrapy 框架契约：对每个进入 Spider 的响应调用，必须返回 None 或抛出异常；返回 None 时处理链继续执行后续中间件直至交给 Spider。用于实现该钩子时校验返回值行为。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `process_spider_input 返回值契约` 时，优先调用它。 线索：实现 process_spider_input 方法, 审查 Spider 中间件钩子返回值, 响应进入 Spider 前需要放行或中断, scrapy, spider-middleware

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要拦截并处理发往 Spider 的响应
- 需要处理 Spider 生成的请求或 item
- 需要定制 Spider 启动输出

## Examples

### Example 1

Input:

  需要处理 Spider 启动输出

Output:

  async def process_start(self, start):
      async for item_or_request in start:
          yield item_or_request

Notes:

  兼容旧版本可另加同步 process_start_requests

### Example 2

Input:

  需要处理进入 Spider 的响应

Output:

  实现 process_spider_input(response)，返回 None 继续处理或抛出异常中断
