---
id: "02c9f164-57a7-5df7-acd9-117c5b242abc"
name: "响应链接跟进生成请求"
description: "使用 response.follow 从相对 URL、Link、Selector 或属性 Selector 构造并返回单个 Request 以跟进链接；适用于解析阶段需要跳转到下一页面时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "follow"
  - "navigation"
  - "parse"
triggers:
  - "需要跟进单个链接到下一页面"
  - "链接为相对 URL 或 Selector 对象"
  - "解析阶段需要构造后续请求"
examples:
  - input: "response.follow(response.css('a.my_link')[0])"
    output: "返回一个指向该链接的 Request 实例"
    notes: "传入 <a> 元素的 Selector"
  - input: "response.follow(response.css('a::attr(href)')[0])"
    output: "返回一个指向该 href 的 Request 实例"
    notes: "传入属性 Selector"
---

# 响应链接跟进生成请求

使用 response.follow 从相对 URL、Link、Selector 或属性 Selector 构造并返回单个 Request 以跟进链接；适用于解析阶段需要跳转到下一页面时。

## Prompt

在解析回调中，当需要从当前响应跟进单个链接到下一页面时，调用 response.follow(url, ...)。url 可为绝对 URL、相对 URL、Link 对象、指向 <link>/<a> 元素的 Selector，或属性 Selector（非 SelectorList）。其余参数与 Request.__init__() 相同。返回一个可调度的 Request 实例。若需批量跟进多个链接，改用 follow_all；若目标是提取数据而非生成请求，改用选择器方法。

## Objective

基于响应中的链接生成单个后续 Request
## Applicable Signals

- 当前响应中存在需要跳转的单个链接
- 链接以相对 URL、Link 对象或 Selector 形式给出

## Contraindications

- 需要批量跟进多个链接（应使用 follow_all）
- 目标不是生成请求而是提取数据

## Intervention Moves

- 调用 response.follow(url, ...) 并传入与 Request.__init__() 相同的参数
- url 支持绝对 URL、相对 URL、Link 对象、<link>/<a> 的 Selector 或属性 Selector
- 返回生成的 Request 实例供调度

## Workflow Steps

- 确认需要跟进的是单个链接
- 确定 url 形式（绝对/相对 URL、Link、Selector 或属性 Selector）
- 调用 response.follow(url, ...) 构造 Request
- 返回该 Request 实例

## Constraints

- url 若为 Selector，须为单个 Selector 而非 SelectorList
- 其余参数与 Request.__init__() 一致

## Cautions

- 批量跟进场景不应使用本技能，应改用 follow_all

## Output Contract

- 返回一个可调度的 Request 实例

## Example Therapist Responses

### Example 1

- Client/Input: response.follow(response.css('a.my_link')[0])
- Therapist/Output: 返回一个指向该链接的 Request 实例
- Notes: 传入 <a> 元素的 Selector

### Example 2

- Client/Input: response.follow(response.css('a::attr(href)')[0])
- Therapist/Output: 返回一个指向该 href 的 Request 实例
- Notes: 传入属性 Selector

## Triggers

- 需要跟进单个链接到下一页面
- 链接为相对 URL 或 Selector 对象
- 解析阶段需要构造后续请求

## Examples

### Example 1

Input:

  response.follow(response.css('a.my_link')[0])

Output:

  返回一个指向该链接的 Request 实例

Notes:

  传入 <a> 元素的 Selector

### Example 2

Input:

  response.follow(response.css('a::attr(href)')[0])

Output:

  返回一个指向该 href 的 Request 实例

Notes:

  传入属性 Selector
