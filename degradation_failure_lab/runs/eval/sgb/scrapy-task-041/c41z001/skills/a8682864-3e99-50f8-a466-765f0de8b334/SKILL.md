---
id: "a8682864-3e99-50f8-a466-765f0de8b334"
name: "响应批量链接跟进生成器"
description: "使用 response.follow_all 通过 urls、css 或 xpath 参数批量生成跟进 Request 的生成器，自动跳过无法获取链接的选择器。适用于需要遍历页面所有链接的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "follow_all"
  - "request_construction"
  - "crawl_navigation"
  - "parse"
triggers:
  - "需要一次性跟进页面中多个链接"
  - "使用 css/xpath 参数批量提取链接"
  - "解析回调中需生成多个 Request"
examples:
  - input: "response.follow_all(css='a.my_link', callback=self.parse_item)"
    output: "yield 生成器，逐个产出指向各链接的 Request"
    notes: "css 参数批量提取链接"
  - input: "response.follow_all(xpath='//img/@src')"
    output: "yield 生成器，逐个产出指向各图片 URL 的 Request"
    notes: "xpath 属性选择器批量提取"
---

# 响应批量链接跟进生成器

使用 response.follow_all 通过 urls、css 或 xpath 参数批量生成跟进 Request 的生成器，自动跳过无法获取链接的选择器。适用于需要遍历页面所有链接的场景。

## Prompt

在解析回调中需要一次性跟进页面多个链接时，调用 response.follow_all 生成 Request 生成器。

执行要点：
1. 选择一种链接来源参数：urls（列表）、css 或 xpath，三者互斥，只能传其一。
2. urls 元素可为相对 URL、Link 对象、指向 <link>/<a> 的 Selector，或属性 Selector（非 SelectorList）。
3. 其余参数与 Request.__init__() 相同，可传 callback、meta 等。
4. 将生成器 yield 出去（或迭代 yield 每个 Request），交由引擎调度。
5. 注意：当传入 SelectorList 或使用 css/xpath 参数时，无法获取链接的选择器（如无 href 的 <a>）不会产生 Request，无需额外过滤。

## Objective

批量生成跟进多个链接的 Request 生成器
## Applicable Signals

- 页面包含多个待跟进链接
- 希望用 css 或 xpath 一次性提取并跟进链接
- 需要以生成器方式产出多个 Request

## Contraindications

- 仅需跟进单个链接（应使用 response.follow）
- 同时传入 urls、css、xpath 中的多个参数

## Intervention Moves

- 调用 response.follow_all 并仅传入 urls、css、xpath 之一
- 将生成器 yield 给引擎
- 依赖内置逻辑自动跳过无法获取链接的选择器

## Workflow Steps

- 确定链接来源：urls 列表、css 选择器或 xpath 选择器，三选一
- 调用 response.follow_all(urls=... 或 css=... 或 xpath=...)，按需附加 callback、meta 等 Request 参数
- 在解析回调中 yield 该生成器（或迭代 yield 每个 Request）
- 确认无 href 等无法获取链接的选择器已被自动跳过

## Constraints

- urls、css、xpath 三者互斥，仅允许传入其一
- urls 元素可为相对 URL、Link 对象、Selector 或属性 Selector（非 SelectorList）
- 其余参数与 Request.__init__() 一致

## Cautions

- 传入 SelectorList 或使用 css/xpath 时，无法获取链接的选择器不会产生 Request，属预期行为
- 不要与单链接 follow 混用同一批链接来源

## Output Contract

- 产出多个 Request 实例的生成器，交由引擎调度跟进

## Example Therapist Responses

### Example 1

- Client/Input: response.follow_all(css='a.my_link', callback=self.parse_item)
- Therapist/Output: yield 生成器，逐个产出指向各链接的 Request
- Notes: css 参数批量提取链接

### Example 2

- Client/Input: response.follow_all(xpath='//img/@src')
- Therapist/Output: yield 生成器，逐个产出指向各图片 URL 的 Request
- Notes: xpath 属性选择器批量提取

## Triggers

- 需要一次性跟进页面中多个链接
- 使用 css/xpath 参数批量提取链接
- 解析回调中需生成多个 Request

## Examples

### Example 1

Input:

  response.follow_all(css='a.my_link', callback=self.parse_item)

Output:

  yield 生成器，逐个产出指向各链接的 Request

Notes:

  css 参数批量提取链接

### Example 2

Input:

  response.follow_all(xpath='//img/@src')

Output:

  yield 生成器，逐个产出指向各图片 URL 的 Request

Notes:

  xpath 属性选择器批量提取
