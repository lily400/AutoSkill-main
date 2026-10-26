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
  - "未分类技能"
  - "profile:scrapy::未分类技能"
  - "kind:parent"
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

## 子技能目录
- [回调参数透传至 errback](通用技能领域/Family技能/未分类技能/微技能/回调参数透传至 errback/SKILL.md) ｜ 适用：通过 cb_kwargs 向回调传递上下文参数，并在 errback 中经 Failure.request.cb_kwargs 取回，用于失败时仍能基于原始上下文处理。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `回调参数透传至 errback` 时，优先调用它。 线索：失败后仍需基于原始请求上下文产出数据或做后续处理, 需要在 errback 中访问 callback 的参数, scrapy, errback, cb_kwargs

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 默认去重指纹不满足需求
- 需要自定义请求唯一性判定
- 需要调整请求去重逻辑
