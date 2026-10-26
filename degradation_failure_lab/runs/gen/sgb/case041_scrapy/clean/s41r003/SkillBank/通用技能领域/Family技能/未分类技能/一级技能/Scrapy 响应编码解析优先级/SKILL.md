---
id: "7ce0ae55-8c21-5690-a09e-d2e8d99adb28"
name: "Scrapy 响应编码解析优先级"
description: "按固定优先级解析 Scrapy 响应文本的编码来源：先取 __init__ 传入的 encoding，再取 Content-Type 头声明，再取响应体声明（HtmlResponse/XmlResponse 支持），最后回退到从响应体推断。用于需要确定响应文本编码或排查乱码时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "response_handling"
  - "encoding_resolution"
  - "response_parsing"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要确定响应文本编码"
  - "响应出现乱码需排查编码来源"
  - "需要判断编码来自参数、头部还是响应体"
---

# Scrapy 响应编码解析优先级

按固定优先级解析 Scrapy 响应文本的编码来源：先取 __init__ 传入的 encoding，再取 Content-Type 头声明，再取响应体声明（HtmlResponse/XmlResponse 支持），最后回退到从响应体推断。用于需要确定响应文本编码或排查乱码时。

## Prompt

当需要确定 Scrapy 响应文本的编码来源或排查乱码时，按以下顺序逐级尝试解析编码：1) __init__() 方法传入的 encoding 参数；2) Content-Type HTTP 头中声明的编码（若无效/未知则忽略并继续）；3) 响应体中声明的编码（仅 HtmlResponse 与 XmlResponse 提供此功能，TextResponse 不提供）；4) 从响应体推断编码（最脆弱，最后尝试）。输出最终采用的编码及其来源层级。

## Objective

确定响应文本的正确编码来源顺序
## Applicable Signals

- 需要确定响应文本编码
- 响应出现乱码需排查编码来源

## Contraindications

- 处理非文本二进制响应
- 编码已由调用方明确指定且无需回退

## Intervention Moves

- 检查 __init__ 传入的 encoding 参数
- 检查 Content-Type 头声明的编码，无效则忽略
- 检查响应体声明的编码（HtmlResponse/XmlResponse）
- 回退到从响应体推断编码

## Workflow Steps

- 优先采用 __init__() 传入的 encoding 参数
- 若无，则读取 Content-Type HTTP 头声明的编码；若该编码无效（未知）则忽略并继续
- 若无，则读取响应体声明的编码（HtmlResponse 与 XmlResponse 支持，TextResponse 不提供）
- 若仍无，则从响应体推断编码（最脆弱，最后尝试）
- 记录最终采用的编码及其来源层级

## Constraints

- 必须按固定优先级顺序解析
- Content-Type 头中无效编码应被忽略并继续下一机制
- 响应体声明编码仅 HtmlResponse/XmlResponse 支持

## Cautions

- 从响应体推断编码是最脆弱的方法，应作为最后手段

## Output Contract

- 确定最终采用的编码及其来源层级

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要确定响应文本编码
- 响应出现乱码需排查编码来源
- 需要判断编码来自参数、头部还是响应体
