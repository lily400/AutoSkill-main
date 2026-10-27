---
id: "206b95c3-ad84-55ae-acea-c8787d0858fb"
name: "启用并排序 Spider 中间件"
description: "通过 SPIDER_MIDDLEWARES 设置注册自定义 Spider 中间件并指定执行顺序，可用 None 禁用内置中间件。适用于需要插入或替换 Spider 处理链中某个中间件时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider-middleware"
  - "settings"
  - "middleware-configuration"
triggers:
  - "需要启用自定义 Spider 中间件"
  - "需要禁用或替换内置中间件"
examples:
  - input: "启用自定义 Spider 中间件"
    output: "SPIDER_MIDDLEWARES = {\n    \"myproject.middlewares.CustomSpiderMiddleware\": 543,\n}"
  - input: "禁用内置 RefererMiddleware 并替换为自定义中间件"
    output: "SPIDER_MIDDLEWARES = {\n    \"scrapy.spidermiddlewares.referer.RefererMiddleware\": None,\n    \"myproject.middlewares.CustomRefererSpiderMiddleware\": 700,\n}"
---

# 启用并排序 Spider 中间件

通过 SPIDER_MIDDLEWARES 设置注册自定义 Spider 中间件并指定执行顺序，可用 None 禁用内置中间件。适用于需要插入或替换 Spider 处理链中某个中间件时。

## Prompt

在 Scrapy 项目的设置中配置 SPIDER_MIDDLEWARES 字典：键为中间件类路径，值为中间件顺序（整数）。如需禁用内置中间件，将其值设为 None。如需替换内置中间件，先禁用原中间件再以新类路径注册并指定顺序。配置完成后确认该中间件是否还需要通过其他专用设置启用。

## Objective

正确注册并排序 Spider 中间件以控制处理链行为
## Applicable Signals

- 需要启用自定义 Spider 中间件
- 需要禁用或替换内置中间件

## Contraindications

- 中间件还需额外专用设置才能生效而未确认

## Intervention Moves

- 在 SPIDER_MIDDLEWARES 字典中添加中间件类路径与顺序值
- 将内置中间件值设为 None 以禁用
- 以新类路径注册替换中间件并指定顺序

## Workflow Steps

- 确定要启用、禁用或替换的中间件类路径
- 在 SPIDER_MIDDLEWARES 字典中为每个中间件指定类路径与顺序值
- 如需禁用内置中间件，将其值设为 None
- 如需替换内置中间件，先禁用原中间件再注册新中间件并指定顺序
- 确认该中间件是否还需通过其他专用设置启用

## Constraints

- SPIDER_MIDDLEWARES 为字典，键为中间件类路径，值为中间件顺序
- 禁用内置中间件须将值设为 None

## Cautions

- 部分中间件可能需要通过特定设置额外启用，需查阅对应中间件文档确认

## Output Contract

- SPIDER_MIDDLEWARES 配置字典，含类路径与顺序值

## Example Therapist Responses

### Example 1

- Client/Input: 启用自定义 Spider 中间件
- Therapist/Output: SPIDER_MIDDLEWARES = {
    "myproject.middlewares.CustomSpiderMiddleware": 543,
}

### Example 2

- Client/Input: 禁用内置 RefererMiddleware 并替换为自定义中间件
- Therapist/Output: SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.referer.RefererMiddleware": None,
    "myproject.middlewares.CustomRefererSpiderMiddleware": 700,
}

## Triggers

- 需要启用自定义 Spider 中间件
- 需要禁用或替换内置中间件

## Examples

### Example 1

Input:

  启用自定义 Spider 中间件

Output:

  SPIDER_MIDDLEWARES = {
      "myproject.middlewares.CustomSpiderMiddleware": 543,
  }

### Example 2

Input:

  禁用内置 RefererMiddleware 并替换为自定义中间件

Output:

  SPIDER_MIDDLEWARES = {
      "scrapy.spidermiddlewares.referer.RefererMiddleware": None,
      "myproject.middlewares.CustomRefererSpiderMiddleware": 700,
  }
