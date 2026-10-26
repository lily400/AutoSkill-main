---
id: "d9545371-1c8c-5f0e-aa54-f9568fa3fffd"
name: "process_spider_input 返回值契约"
description: "确保自定义 Spider 中间件的 process_spider_input 钩子符合 Scrapy 框架契约：对每个进入 Spider 的响应调用，必须返回 None 或抛出异常；返回 None 时处理链继续执行后续中间件直至交给 Spider。用于实现该钩子时校验返回值行为。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider-middleware"
  - "process_spider_input"
  - "return-contract"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "实现 process_spider_input 方法"
  - "审查 Spider 中间件钩子返回值"
  - "响应进入 Spider 前需要放行或中断"
examples:
  - input: "实现 process_spider_input 以放行响应"
    output: "def process_spider_input(self, response):\n    return None"
    notes: "返回 None 表示继续处理链"
---

# process_spider_input 返回值契约

确保自定义 Spider 中间件的 process_spider_input 钩子符合 Scrapy 框架契约：对每个进入 Spider 的响应调用，必须返回 None 或抛出异常；返回 None 时处理链继续执行后续中间件直至交给 Spider。用于实现该钩子时校验返回值行为。

## Prompt

实现或审查 process_spider_input 方法时，确认其返回值符合契约：正常放行时返回 None，让 Scrapy 继续执行后续中间件直至响应交给 Spider；需要中断或报错时抛出异常。不要返回其他值，也不要在该方法内直接处理响应内容。

## Objective

保证 process_spider_input 返回值符合框架约定
## Applicable Signals

- 正在编写 process_spider_input 方法
- 需要确认响应是否继续沿中间件链传递

## Contraindications

- 实现其他不涉及该返回契约的钩子

## Intervention Moves

- 正常放行时返回 None
- 需要中断时抛出异常
- 避免返回其他值

## Workflow Steps

- 确认当前实现的是 process_spider_input 钩子
- 在正常路径返回 None 以继续处理链
- 在需要中断或报错时抛出异常
- 检查方法中不存在返回非 None 值的分支

## Constraints

- 返回值只能是 None 或抛出异常
- 返回 None 后由 Scrapy 继续执行后续中间件直至交给 Spider

## Cautions

- 不要在该钩子中返回响应对象或其他值来替代框架的继续处理逻辑

## Output Contract

- 返回 None 或抛出异常的实现，处理链可继续

## Example Therapist Responses

### Example 1

- Client/Input: 实现 process_spider_input 以放行响应
- Therapist/Output: def process_spider_input(self, response):
    return None
- Notes: 返回 None 表示继续处理链

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 实现 process_spider_input 方法
- 审查 Spider 中间件钩子返回值
- 响应进入 Spider 前需要放行或中断

## Examples

### Example 1

Input:

  实现 process_spider_input 以放行响应

Output:

  def process_spider_input(self, response):
      return None

Notes:

  返回 None 表示继续处理链
