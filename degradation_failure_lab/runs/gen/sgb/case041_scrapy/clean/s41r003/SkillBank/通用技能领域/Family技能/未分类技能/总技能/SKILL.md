---
id: "2fcf2c8c-ee2d-5471-a738-db6f6386065f"
name: "未分类技能"
description: "未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。"
version: "0.1.0"
tags:
  - "未分类技能"
  - "总导航"
  - "子技能地图"
  - "kind:parent"
  - "profile:scrapy::未分类技能"
triggers:
  - "未分类技能"
  - "未分类技能 总导航"
  - "未分类技能 子技能地图"
---

# 未分类技能

未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。

## Prompt

## 适用场景
- 当当前问题明确属于或需要路由到 未分类技能 时，先使用本总技能决定子技能选择顺序。
- 本技能用于导航与组合，不替代子技能中的具体执行 SOP。

## 不适用/风险边界
- 不要把本技能当作具体干预脚本；真正执行时必须继续调用对应子技能。
- 如存在明显高风险或危机信号，应优先调用风险/危机类子技能。

## 总流程
1. 先判断当前问题是否适合进入该家族或领域的处理路径。
2. 再根据任务类型、阶段和风险边界选择最合适的子技能。
3. 调用对应子技能执行具体步骤、规则和输出格式。
4. 最后输出所选子技能、选择理由、执行顺序与风险提示。

## 子技能目录（一级技能目录）
- Scrapy Request.meta 特殊键配置参考 ｜ 类型：request_configuration ｜ 适用条件：列举并说明 Scrapy Request.meta 中可用的特殊键（如 bindaddress、download_timeout、max_retry_times、proxy、dont_redirect 等），用于在构造请求时按需设置下载行为。适用于需要查阅或选择 meta 键来调整单个请求行为的场景。
- Scrapy 响应类型选择与解析 ｜ 类型：response_handling ｜ 适用条件：根据响应的 Content-Type 与内容特征选择合适的 Scrapy Response 子类（TextResponse/HtmlResponse/XmlResponse/JsonResponse），并调用其解析方法（json、urljoin 等）提取数据或构造绝对 URL。适用于处理已获取的响应对象，而非发起请求。
- Scrapy 响应编码解析优先级 ｜ 类型：response_handling ｜ 适用条件：按固定优先级解析 Scrapy 响应文本的编码来源：先取 __init__ 传入的 encoding，再取 Content-Type 头声明，再取响应体声明（HtmlResponse/XmlResponse 支持），最后回退到从响应体推断。用于需要确定响应文本编码或排查乱码时。

## 选用规则（一级技能目录）
- 当问题命中“需要为单个请求设置超时、代理、重试或重定向行为、不确定某个 meta 键的名称或用途、scrapy、request”这类线索时，优先选择 Scrapy Request.meta 特殊键配置参考。
- 当问题命中“需要从响应中解析 JSON 或构造绝对 URL、响应带有 JSON MIME 类型或 HTML/XML 编码声明、scrapy、response”这类线索时，优先选择 Scrapy 响应类型选择与解析。
- 当问题命中“需要确定响应文本编码、响应出现乱码需排查编码来源、需要判断编码来自参数、头部还是响应体、scrapy”这类线索时，优先选择 Scrapy 响应编码解析优先级。

## 输出格式
- family_route:
  - family: 未分类技能
  - selected_children: [子技能名称列表]
  - rationale: 说明为什么选择这些子技能
  - cautions: 风险边界与切换条件

## Files

- `references/children_manifest.json`
- `references/children_map.md`

## Triggers

- 未分类技能
- 未分类技能 总导航
- 未分类技能 子技能地图
