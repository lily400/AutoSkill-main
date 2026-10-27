---
id: "508a30a5-6330-5c7e-a9a0-583ed481e86d"
name: "Scrapy 自定义请求指纹器配置"
description: "当默认请求去重指纹不满足需求时，通过 REQUEST_FINGERPRINTER_CLASS 选择或实现自定义请求指纹器，以控制请求去重行为。"
version: "0.1.0"
tags:
  - "scrapy"
  - "请求去重"
  - "请求指纹"
  - "REQUEST_FINGERPRINTER_CLASS"
triggers:
  - "默认去重指纹不满足需求"
  - "需要自定义请求唯一性判定"
  - "需要调整请求去重逻辑"
---

# Scrapy 自定义请求指纹器配置

当默认请求去重指纹不满足需求时，通过 REQUEST_FINGERPRINTER_CLASS 选择或实现自定义请求指纹器，以控制请求去重行为。

## Prompt

当默认请求指纹无法满足去重需求时，按以下步骤定制请求指纹：先确认默认指纹为何不适用，再决定是配置 REQUEST_FINGERPRINTER_CLASS 还是编写自定义 fingerprinter，实现后验证去重行为符合预期，并遵守指纹限制。

## Objective

定制请求指纹以控制去重行为
## Applicable Signals

- 默认去重指纹不满足需求
- 需要自定义请求唯一性判定

## Contraindications

- 默认指纹已满足去重需求

## Intervention Moves

- 确认默认指纹不适用的具体原因
- 通过 REQUEST_FINGERPRINTER_CLASS 选择指纹器
- 编写自定义 request fingerprinter
- 验证去重行为符合预期

## Workflow Steps

- 确认默认去重指纹为何不满足需求
- 决定使用 REQUEST_FINGERPRINTER_CLASS 配置现有指纹器，或编写自定义 request fingerprinter
- 实现或配置指纹器，遵守请求指纹限制
- 验证去重行为符合预期

## Constraints

- 遵守请求指纹限制
- 仅在默认指纹不满足需求时定制

## Cautions

- 自定义指纹可能改变去重结果，需验证后再上线

## Output Contract

- 已配置或实现的自定义请求指纹器，去重行为符合预期

## Triggers

- 默认去重指纹不满足需求
- 需要自定义请求唯一性判定
- 需要调整请求去重逻辑
