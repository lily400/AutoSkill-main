---
id: "46e2a1dd-9c6d-5a57-8b18-94b38f95cc65"
name: "Response 选择器快捷提取"
description: "在已获得的 TextResponse 对象上直接调用 css/xpath/jmespath 快捷方法执行选择器查询，返回匹配的 SelectorList（或空结果）供后续解析使用。适用于已持有响应、需要按 CSS/XPath/JMESPath 语法定位或提取页面元素的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "response_parsing"
  - "selector_query"
  - "css"
  - "xpath"
  - "jmespath"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "已持有 TextResponse 对象需要提取页面元素"
  - "需要按 CSS/XPath/JMESPath 语法定位节点"
  - "解析阶段需要从响应中获取 SelectorList"
examples:
  - input: "response.css('p')"
    output: "匹配所有 <p> 元素的 SelectorList"
    notes: "等价于 TextResponse.selector.css(query)"
  - input: "response.xpath('//p')"
    output: "匹配所有 <p> 元素的 SelectorList"
    notes: "等价于 TextResponse.selector.xpath(query)"
  - input: "response.jmespath('object.[*]')"
    output: "按 JMESPath 查询返回的匹配结果"
    notes: "等价于 TextResponse.selector.jmespath(query)"
---

# Response 选择器快捷提取

在已获得的 TextResponse 对象上直接调用 css/xpath/jmespath 快捷方法执行选择器查询，返回匹配的 SelectorList（或空结果）供后续解析使用。适用于已持有响应、需要按 CSS/XPath/JMESPath 语法定位或提取页面元素的场景。

## Prompt

确认当前对象为 TextResponse（或子类）且已成功获取响应内容。根据目标元素选择合适的选择器语法：CSS 用 response.css(query)，XPath 用 response.xpath(query)，JMESPath 用 response.jmespath(query)。这些方法等价于对 TextResponse.selector 调用对应查询。执行后检查返回的 SelectorList：若为空，说明选择器未匹配，应调整选择器而非继续解析；若需提取属性值，使用 ::attr(...) 或 @attr 语法。仅做单次提取，不在此步骤构造或跟进请求。

## Objective

在响应对象上快速执行选择器查询并返回匹配结果
## Applicable Signals

- 已持有 TextResponse 对象需要提取元素
- 需要按 CSS/XPath/JMESPath 语法定位节点

## Contraindications

- 响应非文本类型或选择器语法不适用
- 需要跨请求调度而非单次提取

## Intervention Moves

- 调用 response.css(query) 执行 CSS 查询
- 调用 response.xpath(query) 执行 XPath 查询
- 调用 response.jmespath(query) 执行 JMESPath 查询
- 检查返回的 SelectorList 是否为空并据此调整选择器

## Workflow Steps

- 确认响应对象为 TextResponse 或其子类
- 按目标元素选择 CSS、XPath 或 JMESPath 语法
- 调用对应的快捷方法执行查询
- 检查返回的 SelectorList，必要时调整选择器或提取属性

## Constraints

- 仅在已获得的响应对象上执行单次提取
- 不在此步骤构造或跟进请求
- 选择器语法须与响应内容类型匹配

## Cautions

- 空 SelectorList 表示未匹配，应调整选择器而非继续解析
- 提取属性需使用 ::attr(...) 或 @attr 语法

## Output Contract

- 返回匹配的 SelectorList 或空结果

## Example Therapist Responses

### Example 1

- Client/Input: response.css('p')
- Therapist/Output: 匹配所有 <p> 元素的 SelectorList
- Notes: 等价于 TextResponse.selector.css(query)

### Example 2

- Client/Input: response.xpath('//p')
- Therapist/Output: 匹配所有 <p> 元素的 SelectorList
- Notes: 等价于 TextResponse.selector.xpath(query)

### Example 3

- Client/Input: response.jmespath('object.[*]')
- Therapist/Output: 按 JMESPath 查询返回的匹配结果
- Notes: 等价于 TextResponse.selector.jmespath(query)

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 已持有 TextResponse 对象需要提取页面元素
- 需要按 CSS/XPath/JMESPath 语法定位节点
- 解析阶段需要从响应中获取 SelectorList

## Examples

### Example 1

Input:

  response.css('p')

Output:

  匹配所有 <p> 元素的 SelectorList

Notes:

  等价于 TextResponse.selector.css(query)

### Example 2

Input:

  response.xpath('//p')

Output:

  匹配所有 <p> 元素的 SelectorList

Notes:

  等价于 TextResponse.selector.xpath(query)

### Example 3

Input:

  response.jmespath('object.[*]')

Output:

  按 JMESPath 查询返回的匹配结果

Notes:

  等价于 TextResponse.selector.jmespath(query)
