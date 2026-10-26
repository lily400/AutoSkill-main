---
id: "d21e58c7-9e4a-5dc6-bda8-df8bf3ea9e76"
name: "自定义请求指纹器"
description: "当默认请求指纹不满足去重需求时，实现自定义 REQUEST_FINGERPRINTER_CLASS，按业务比较规则规范化 URL（大小写、片段、查询参数、请求头等）生成请求唯一标识，从而控制去重行为。适用于需要定制去重比较规则的 Scrapy 爬虫。"
version: "0.1.0"
tags:
  - "scrapy"
  - "请求去重"
  - "指纹器"
  - "REQUEST_FINGERPRINTER_CLASS"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
  - "kind:parent"
triggers:
  - "默认指纹导致误去重或漏去重"
  - "需要按大小写、片段、查询参数或请求头定制比较规则"
  - "需要为请求生成符合业务比较规则的唯一标识"
examples:
  - input: "默认指纹无法区分大小写不同的 URL，导致误去重"
    output: "实现大小写不敏感规范化的自定义指纹器并通过 REQUEST_FINGERPRINTER_CLASS 启用，验证去重行为符合预期"
    notes: "比较规则需与业务语义一致"
---

# 自定义请求指纹器

当默认请求指纹不满足去重需求时，实现自定义 REQUEST_FINGERPRINTER_CLASS，按业务比较规则规范化 URL（大小写、片段、查询参数、请求头等）生成请求唯一标识，从而控制去重行为。适用于需要定制去重比较规则的 Scrapy 爬虫。

## Prompt

在确认默认指纹无法满足去重需求后，实现一个自定义请求指纹器类，按业务需要的比较规则（如大小写不敏感、包含/排除 URL 片段、包含/排除查询参数、包含部分或全部请求头）规范化请求并生成唯一标识，然后通过 REQUEST_FINGERPRINTER_CLASS 配置启用，并验证去重行为符合预期。

## Objective

按业务比较规则生成请求唯一指纹以控制去重
## Applicable Signals

- 默认请求指纹器无法区分或错误合并本应不同/相同的请求
- 业务要求对 URL 大小写、片段、查询参数或请求头采用特定比较方式

## Contraindications

- 默认指纹已满足去重需求时
- 去重问题源于调度器配置而非指纹规则时

## Intervention Moves

- 明确业务去重比较规则（大小写、片段、查询参数、请求头）
- 实现自定义请求指纹器类，规范化请求并生成唯一标识
- 通过 REQUEST_FINGERPRINTER_CLASS 配置启用自定义指纹器
- 验证去重行为符合预期

## Workflow Steps

- 确认默认请求指纹器无法满足当前去重需求，并明确差异点
- 定义业务比较规则：是否大小写敏感、是否包含 URL 片段、包含或排除哪些查询参数、是否纳入请求头
- 编写自定义请求指纹器类，按上述规则规范化请求并生成唯一标识
- 在项目配置中通过 REQUEST_FINGERPRINTER_CLASS 指向自定义指纹器类
- 运行爬虫并验证去重行为符合预期

## Constraints

- 仅在默认指纹不满足需求时启用自定义指纹器
- 指纹生成规则需与业务去重语义一致
- 去重问题若源于调度器配置，应先修正调度器配置而非改指纹规则

## Cautions

- 不存在通用的请求唯一标识生成方式，需按具体场景确定比较规则
- 修改指纹规则会改变去重结果，需验证不会引入误去重或漏去重

## Output Contract

- 配置生效的自定义请求指纹器类及去重行为验证结果

## Example Therapist Responses

### Example 1

- Client/Input: 默认指纹无法区分大小写不同的 URL，导致误去重
- Therapist/Output: 实现大小写不敏感规范化的自定义指纹器并通过 REQUEST_FINGERPRINTER_CLASS 启用，验证去重行为符合预期
- Notes: 比较规则需与业务语义一致

## 子技能目录
- [请求错误回调处理（errback）](通用技能领域/Family技能/未分类技能/微技能/请求错误回调处理（errback）/SKILL.md) ｜ 适用：为 Scrapy 请求配置 errback，并按失败类型（HttpError、DNSLookupError、TimeoutError/TCPTimedOutError）分支记录与处理异常。适用于需要区分不同下载失败并做针对性处理的爬虫。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `请求错误回调处理（errback）` 时，优先调用它。 线索：需要区分 HTTP 错误、DNS 错误、超时等不同失败类型, 希望在请求失败时记录日志或产出诊断数据, scrapy, errback, 错误处理

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 默认指纹导致误去重或漏去重
- 需要按大小写、片段、查询参数或请求头定制比较规则
- 需要为请求生成符合业务比较规则的唯一标识

## Examples

### Example 1

Input:

  默认指纹无法区分大小写不同的 URL，导致误去重

Output:

  实现大小写不敏感规范化的自定义指纹器并通过 REQUEST_FINGERPRINTER_CLASS 启用，验证去重行为符合预期

Notes:

  比较规则需与业务语义一致
