---
id: "2ed70ab0-4c0d-550c-b289-5766cd0acea3"
name: "自定义Spider中间件基类实现"
description: "使用BaseSpiderMiddleware基类简化异步process_spider_output()和process_start()方法的实现，通过get_processed_item/get_processed_request逐项处理spider输出，减少样板代码。"
version: "0.1.0"
tags:
  - "scrapy"
  - "spider-middleware"
  - "base-class"
  - "async"
triggers:
  - "需要编写异步process_spider_output或process_start的spider中间件"
  - "希望减少中间件样板代码"
examples:
  - input: "需要编写异步process_spider_output的中间件"
    output: "继承BaseSpiderMiddleware并实现get_processed_item，对每个item返回处理后对象或None"
    notes: "response在start seeds时为None"
---

# 自定义Spider中间件基类实现

使用BaseSpiderMiddleware基类简化异步process_spider_output()和process_start()方法的实现，通过get_processed_item/get_processed_request逐项处理spider输出，减少样板代码。

## Prompt

当需要编写包含异步process_spider_output()或process_start()方法的spider中间件时，继承scrapy.spidermiddlewares.base.BaseSpiderMiddleware，并实现get_processed_item(item, response)与/或get_processed_request(request, response)辅助方法。对每个来自start seeds或spider输出的item/request逐项处理：返回相同或不同的对象，或返回None以忽略该项。response参数在start seeds场景下为None。若中间件不包含这两个方法，则无需使用该基类。

## Objective

用基类辅助方法减少自定义spider中间件的样板代码并正确逐项处理item/request
## Applicable Signals

- 中间件需实现异步process_spider_output或process_start
- 存在大量重复的逐项处理样板代码

## Contraindications

- 中间件不包含process_spider_output或process_start方法
- 仅需同步简单钩子

## Intervention Moves

- 继承BaseSpiderMiddleware基类
- 实现get_processed_item逐项处理item
- 实现get_processed_request逐项处理request
- 对需忽略的项返回None

## Workflow Steps

- 确认中间件包含process_spider_output或process_start方法
- 继承scrapy.spidermiddlewares.base.BaseSpiderMiddleware
- 实现get_processed_item(item, response)返回处理后item或None
- 实现get_processed_request(request, response)返回处理后request或None
- 在start seeds场景下将response视为None

## Constraints

- 仅当中间件包含process_spider_output或process_start时才使用该基类
- 辅助方法必须逐项处理并返回相同/不同对象或None

## Cautions

- start seeds场景下response为None，需处理该情况

## Output Contract

- 可运行的spider中间件类，正确返回处理后的item/request或None以忽略

## Example Therapist Responses

### Example 1

- Client/Input: 需要编写异步process_spider_output的中间件
- Therapist/Output: 继承BaseSpiderMiddleware并实现get_processed_item，对每个item返回处理后对象或None
- Notes: response在start seeds时为None

## Triggers

- 需要编写异步process_spider_output或process_start的spider中间件
- 希望减少中间件样板代码

## Examples

### Example 1

Input:

  需要编写异步process_spider_output的中间件

Output:

  继承BaseSpiderMiddleware并实现get_processed_item，对每个item返回处理后对象或None

Notes:

  response在start seeds时为None
