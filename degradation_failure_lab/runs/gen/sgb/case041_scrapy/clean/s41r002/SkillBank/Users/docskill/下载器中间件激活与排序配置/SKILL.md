---
id: "76394f52-1f81-5c91-8ae3-fd51b942c5e1"
name: "下载器中间件激活与排序配置"
description: "通过 DOWNLOADER_MIDDLEWARES 设置注册自定义下载器中间件并指定执行顺序，可用 None 禁用内置中间件。适用于需要全局改变请求/响应处理链的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "downloader-middleware"
  - "settings"
  - "middleware-configuration"
triggers:
  - "需要启用自定义下载器中间件"
  - "需要调整或禁用内置中间件顺序"
examples:
  - input: "需要启用自定义下载器中间件"
    output: "DOWNLOADER_MIDDLEWARES = {\n    \"myproject.middlewares.CustomDownloaderMiddleware\": 543,\n}"
  - input: "需要禁用内置 UserAgentMiddleware"
    output: "DOWNLOADER_MIDDLEWARES = {\n    \"myproject.middlewares.CustomDownloaderMiddleware\": 543,\n    \"scrapy.downloadermiddlewares.useragent.UserAgentMiddleware\": None,\n}"
---

# 下载器中间件激活与排序配置

通过 DOWNLOADER_MIDDLEWARES 设置注册自定义下载器中间件并指定执行顺序，可用 None 禁用内置中间件。适用于需要全局改变请求/响应处理链的场景。

## Prompt

在 Scrapy 项目的 settings 中配置 DOWNLOADER_MIDDLEWARES 字典：键为中间件类路径，值为中间件顺序（整数）。如需禁用某个内置中间件，将其类路径的值设为 None。配置完成后确认中间件依赖的专属设置是否已启用。

## Objective

正确注册并排序下载器中间件，使请求/响应处理链按预期生效
## Applicable Signals

- 需要启用自定义下载器中间件
- 需要调整或禁用内置中间件顺序

## Contraindications

- 仅需修改爬虫解析逻辑而非请求/响应链
- 中间件依赖的专属设置尚未确认

## Intervention Moves

- 在 DOWNLOADER_MIDDLEWARES 中添加中间件类路径与顺序值
- 将需禁用的内置中间件类路径值设为 None
- 确认中间件依赖的专属设置已启用

## Workflow Steps

- 确定要启用的自定义下载器中间件类路径
- 在 DOWNLOADER_MIDDLEWARES 字典中为每个中间件指定顺序值
- 如需禁用内置中间件，将其类路径值设为 None
- 检查中间件是否依赖特定设置并确认已启用

## Constraints

- DOWNLOADER_MIDDLEWARES 为字典，键为中间件类路径，值为中间件顺序
- 禁用内置中间件时使用 None 作为值

## Cautions

- 部分中间件可能需要通过特定设置启用，需查阅各中间件文档

## Output Contract

- DOWNLOADER_MIDDLEWARES 配置字典，含类路径与顺序值

## Example Therapist Responses

### Example 1

- Client/Input: 需要启用自定义下载器中间件
- Therapist/Output: DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.CustomDownloaderMiddleware": 543,
}

### Example 2

- Client/Input: 需要禁用内置 UserAgentMiddleware
- Therapist/Output: DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.CustomDownloaderMiddleware": 543,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}

## Triggers

- 需要启用自定义下载器中间件
- 需要调整或禁用内置中间件顺序

## Examples

### Example 1

Input:

  需要启用自定义下载器中间件

Output:

  DOWNLOADER_MIDDLEWARES = {
      "myproject.middlewares.CustomDownloaderMiddleware": 543,
  }

### Example 2

Input:

  需要禁用内置 UserAgentMiddleware

Output:

  DOWNLOADER_MIDDLEWARES = {
      "myproject.middlewares.CustomDownloaderMiddleware": 543,
      "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
  }
