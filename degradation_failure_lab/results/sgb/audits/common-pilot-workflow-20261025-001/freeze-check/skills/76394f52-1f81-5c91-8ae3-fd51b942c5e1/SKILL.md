---
id: "76394f52-1f81-5c91-8ae3-fd51b942c5e1"
name: "下载器中间件激活与排序配置"
description: "当默认去重逻辑无法满足需求时，通过配置 REQUEST_FINGERPRINTER_CLASS 指定请求指纹器类，或编写自定义请求指纹器类来控制 Scrapy 的请求去重判断逻辑。适用于默认指纹不满足去重需求、需要按自定义字段组合判定请求唯一性时。"
version: "0.1.1"
tags:
  - "scrapy"
  - "去重"
  - "fingerprinter"
  - "请求指纹"
  - "配置"
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

当默认去重逻辑无法满足需求时，通过配置 REQUEST_FINGERPRINTER_CLASS 指定请求指纹器类，或编写自定义请求指纹器类来控制 Scrapy 的请求去重判断逻辑。适用于默认指纹不满足去重需求、需要按自定义字段组合判定请求唯一性时。

## Prompt

当默认请求指纹无法满足去重需求时，按以下步骤定制：1) 确认现有默认去重行为确实不满足需求；2) 决定是仅替换 REQUEST_FINGERPRINTER_CLASS 指向自定义类，还是编写完整 fingerprinter 实现；3) 编写 fingerprinter 类，使其基于请求属性生成稳定指纹；4) 遵守指纹计算限制（如不得依赖不可用或易变数据）；5) 在配置中接入该类并验证请求按新规则生成指纹。

## Objective

为请求定义并接入自定义去重指纹
## Applicable Signals

- 默认指纹不满足去重需求
- 需要按自定义字段组合判定请求唯一性

## Contraindications

- 默认去重行为已满足需求
- 无法遵守指纹计算限制的场景

## Intervention Moves

- 确认默认指纹不适用的具体原因
- 通过 REQUEST_FINGERPRINTER_CLASS 指定请求指纹器类
- 编写自定义请求指纹器类，基于请求属性生成稳定指纹
- 遵守请求指纹限制
- 验证去重行为符合预期

## Workflow Steps

- 判断默认去重是否满足需求，若不满足则进入自定义指纹流程
- 选择配置 REQUEST_FINGERPRINTER_CLASS 或编写自定义请求指纹器类
- 实现或指定指纹器类，基于请求属性生成稳定指纹，并遵守请求指纹限制
- 确认指纹器类可被正确加载并生效
- 验证去重行为符合预期

## Constraints

- 自定义指纹器须遵守请求指纹限制
- 仅在默认去重不满足需求时定制指纹

## Cautions

- 仅在默认去重不满足需求时定制指纹，避免不必要的复杂度
- 避免依赖易变或不可用数据生成指纹，以免去重不稳定
- 自定义指纹可能改变去重结果，需验证后再上线

## Output Contract

- 配置生效的自定义 fingerprinter 类，请求按新规则生成指纹

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
