---
id: "75b3b50e-8659-5572-9a05-b5b329f0f460"
name: "Scrapy 响应类型选择与解析"
description: "根据响应的 Content-Type 与内容特征选择合适的 Scrapy Response 子类（TextResponse/HtmlResponse/XmlResponse/JsonResponse），并调用其解析方法（json、urljoin 等）提取数据或构造绝对 URL。适用于处理已获取的响应对象，而非发起请求。"
version: "0.1.0"
tags:
  - "scrapy"
  - "response"
  - "parsing"
  - "json"
  - "urljoin"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要从响应中解析 JSON 或构造绝对 URL"
  - "响应带有 JSON MIME 类型或 HTML/XML 编码声明"
examples:
  - input: "响应 Content-Type 为 JSON MIME 类型"
    output: "使用 JsonResponse 并调用 json() 得到 Python 对象"
    notes: "结果在首次调用后缓存"
  - input: "响应含相对 URL 且页面有 <base> 标签"
    output: "调用 urljoin() 返回基于 <base> 的绝对 URL"
---

# Scrapy 响应类型选择与解析

根据响应的 Content-Type 与内容特征选择合适的 Scrapy Response 子类（TextResponse/HtmlResponse/XmlResponse/JsonResponse），并调用其解析方法（json、urljoin 等）提取数据或构造绝对 URL。适用于处理已获取的响应对象，而非发起请求。

## Prompt

当需要处理一个已获取的 Scrapy 响应时：1) 检查响应的 Content-Type 与内容特征；2) 若为 JSON MIME 类型，使用 JsonResponse 并调用 json() 反序列化为 Python 对象（结果在首次调用后缓存）；3) 若为 HTML 且需依据 meta http-equiv 自动发现编码，使用 HtmlResponse；4) 若为 XML 且需依据 XML 声明行自动发现编码，使用 XmlResponse；5) 其他文本响应使用 TextResponse；6) 需要绝对 URL 时调用 urljoin()，其基址取自 <base> 标签，若无则取 Response.url。

## Objective

为给定响应选择正确的 Response 子类并正确解析其内容
## Applicable Signals

- 响应 Content-Type 为 JSON MIME 类型
- HTML 响应含 meta http-equiv 编码声明
- XML 响应含 XML 声明行
- 需要将相对 URL 转为绝对 URL

## Contraindications

- 响应内容类型未知且无法判定子类
- 需要发起请求而非处理响应

## Intervention Moves

- 依据 Content-Type 判定 JSON 响应并选用 JsonResponse
- 对 HTML 响应选用 HtmlResponse 以自动发现编码
- 对 XML 响应选用 XmlResponse 以自动发现编码
- 调用 json() 反序列化并利用缓存
- 调用 urljoin() 结合 <base> 标签或 Response.url 构造绝对 URL

## Workflow Steps

- 检查响应 Content-Type 与内容特征
- 选择匹配的 Response 子类
- 调用相应解析方法（json、urljoin 等）
- 返回解析后的 Python 对象或绝对 URL

## Constraints

- 仅在处理已获取的响应时使用，不用于构造请求
- 子类选择须与响应实际内容类型一致

## Cautions

- json() 结果在首次调用后缓存，后续调用返回同一对象
- urljoin 的基址优先取 <base> 标签，缺失时回退到 Response.url

## Output Contract

- 选定 Response 子类并产出解析后的 Python 对象或绝对 URL

## Example Therapist Responses

### Example 1

- Client/Input: 响应 Content-Type 为 JSON MIME 类型
- Therapist/Output: 使用 JsonResponse 并调用 json() 得到 Python 对象
- Notes: 结果在首次调用后缓存

### Example 2

- Client/Input: 响应含相对 URL 且页面有 <base> 标签
- Therapist/Output: 调用 urljoin() 返回基于 <base> 的绝对 URL

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要从响应中解析 JSON 或构造绝对 URL
- 响应带有 JSON MIME 类型或 HTML/XML 编码声明

## Examples

### Example 1

Input:

  响应 Content-Type 为 JSON MIME 类型

Output:

  使用 JsonResponse 并调用 json() 得到 Python 对象

Notes:

  结果在首次调用后缓存

### Example 2

Input:

  响应含相对 URL 且页面有 <base> 标签

Output:

  调用 urljoin() 返回基于 <base> 的绝对 URL
