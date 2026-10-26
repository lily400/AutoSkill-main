---
id: "8a26e484-1c30-5f08-a668-ce5b4b7e99df"
name: "自定义 Request 指纹器实现"
description: "通过 REQUEST_FINGERPRINTER_CLASS 配置或编写自定义请求指纹器，为请求生成去重指纹，并遵守指纹限制（如不得依赖响应数据）。用于默认指纹不满足去重需求的爬取场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "请求去重"
  - "request-fingerprinter"
  - "去重配置"
triggers:
  - "默认指纹不满足去重需求"
  - "需要按特定字段组合生成请求指纹"
  - "需要定制请求去重逻辑"
---

# 自定义 Request 指纹器实现

通过 REQUEST_FINGERPRINTER_CLASS 配置或编写自定义请求指纹器，为请求生成去重指纹，并遵守指纹限制（如不得依赖响应数据）。用于默认指纹不满足去重需求的爬取场景。

## Prompt

当默认请求指纹无法满足去重需求时，实现一个自定义请求指纹器：先确认去重目标与所需字段组合，再编写指纹器类（基于请求本身的数据生成稳定指纹），通过 REQUEST_FINGERPRINTER_CLASS 配置启用，并校验其不依赖响应数据等限制。

## Objective

实现符合限制的自定义请求指纹生成
## Applicable Signals

- 默认指纹不满足去重需求
- 需要按特定字段组合生成请求指纹

## Contraindications

- 默认指纹已满足去重需求
- 指纹需依赖响应内容（受限制）

## Intervention Moves

- 确认去重目标与所需字段组合
- 编写自定义指纹器类
- 通过 REQUEST_FINGERPRINTER_CLASS 配置启用
- 校验指纹器遵守限制

## Workflow Steps

- 确认默认指纹为何不满足去重需求，明确期望的去重粒度与字段组合
- 编写自定义请求指纹器类，仅基于请求自身数据生成稳定指纹
- 通过 REQUEST_FINGERPRINTER_CLASS 配置启用该指纹器
- 校验指纹器不依赖响应数据等限制，并验证去重效果

## Constraints

- 指纹必须仅基于请求数据生成
- 不得依赖响应内容生成指纹
- 仅在默认指纹不满足需求时使用

## Cautions

- 依赖响应数据的指纹违反限制，不可采用

## Output Contract

- 可用的自定义指纹器类配置（含指纹器类与 REQUEST_FINGERPRINTER_CLASS 设置）

## Triggers

- 默认指纹不满足去重需求
- 需要按特定字段组合生成请求指纹
- 需要定制请求去重逻辑
