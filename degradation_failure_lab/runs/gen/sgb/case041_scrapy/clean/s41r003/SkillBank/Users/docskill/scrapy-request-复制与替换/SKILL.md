---
id: "c8444e68-02ba-56bd-91b5-83d547d251d1"
name: "Scrapy Request 复制与替换"
description: "使用 Request.copy() 或 Request.replace() 基于现有请求派生新请求，仅覆盖指定字段，并默认浅拷贝 cb_kwargs 与 meta。适用于需要在保留原请求上下文的前提下修改 URL、回调、优先级等字段时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "copy"
  - "replace"
  - "对象派生"
triggers:
  - "需要基于已有请求修改少量字段"
  - "需要复用原请求的 meta 或 cb_kwargs 上下文"
  - "需要复制一个请求对象"
examples:
  - input: "已有 Request 对象，需要将其 priority 提高并更换 callback"
    output: "request.replace(priority=10, callback=new_callback)"
    notes: "其余字段及 meta、cb_kwargs 默认浅拷贝保留"
  - input: "需要原样复制一个 Request 对象"
    output: "request.copy()"
    notes: "返回该请求的副本"
---

# Scrapy Request 复制与替换

使用 Request.copy() 或 Request.replace() 基于现有请求派生新请求，仅覆盖指定字段，并默认浅拷贝 cb_kwargs 与 meta。适用于需要在保留原请求上下文的前提下修改 URL、回调、优先级等字段时。

## Prompt

当需要基于已有 Request 派生新请求时：1) 若只需原样复制，调用 copy()；2) 若需修改部分字段，调用 replace() 并仅传入要覆盖的关键字参数（如 url、callback、priority、dont_filter 等）；3) 注意 cb_kwargs 与 meta 默认被浅拷贝，若需修改嵌套结构须显式传入新值或自行深拷贝；4) 确认返回的新 Request 除指定字段外其余属性与原请求一致。

## Objective

在保留原请求属性的基础上安全派生修改后的请求对象
## Applicable Signals

- 已有 Request 对象可作为派生基础
- 仅需覆盖 url、callback、priority、dont_filter 等少量字段
- 需要保留原请求的 meta 或 cb_kwargs 上下文

## Contraindications

- 需要完全新建无关请求
- 需要深拷贝嵌套 meta 结构时未显式处理

## Intervention Moves

- 调用 Request.copy() 获得原样副本
- 调用 Request.replace() 并仅传入需覆盖的关键字参数
- 对需要修改的嵌套 meta 或 cb_kwargs 显式传入新值或自行深拷贝

## Workflow Steps

- 确认存在可作为基础的现有 Request 对象
- 判断是原样复制（copy）还是字段覆盖（replace）
- 使用 replace() 时仅传入需修改的字段，其余保持默认
- 检查 cb_kwargs 与 meta 的浅拷贝语义，必要时显式处理嵌套结构
- 验证返回的新 Request 除指定字段外与原请求一致

## Constraints

- replace() 的 cb_kwargs 与 meta 默认浅拷贝，除非显式传入新值
- 仅覆盖明确指定的字段，不应意外改变其它属性

## Cautions

- 浅拷贝可能导致嵌套结构共享引用，修改嵌套内容时需谨慎

## Output Contract

- 返回一个仅指定字段被覆盖、其余属性与原请求一致的新 Request 对象

## Example Therapist Responses

### Example 1

- Client/Input: 已有 Request 对象，需要将其 priority 提高并更换 callback
- Therapist/Output: request.replace(priority=10, callback=new_callback)
- Notes: 其余字段及 meta、cb_kwargs 默认浅拷贝保留

### Example 2

- Client/Input: 需要原样复制一个 Request 对象
- Therapist/Output: request.copy()
- Notes: 返回该请求的副本

## Triggers

- 需要基于已有请求修改少量字段
- 需要复用原请求的 meta 或 cb_kwargs 上下文
- 需要复制一个请求对象

## Examples

### Example 1

Input:

  已有 Request 对象，需要将其 priority 提高并更换 callback

Output:

  request.replace(priority=10, callback=new_callback)

Notes:

  其余字段及 meta、cb_kwargs 默认浅拷贝保留

### Example 2

Input:

  需要原样复制一个 Request 对象

Output:

  request.copy()

Notes:

  返回该请求的副本
