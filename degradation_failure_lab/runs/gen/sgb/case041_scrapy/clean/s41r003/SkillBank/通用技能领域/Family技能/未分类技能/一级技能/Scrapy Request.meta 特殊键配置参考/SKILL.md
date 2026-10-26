---
id: "10a65f13-3661-544b-8e28-ddfa920527b5"
name: "Scrapy Request.meta 特殊键配置参考"
description: "列举并说明 Scrapy Request.meta 中可用的特殊键（如 bindaddress、download_timeout、max_retry_times、proxy、dont_redirect 等），用于在构造请求时按需设置下载行为。适用于需要查阅或选择 meta 键来调整单个请求行为的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "meta"
  - "reference"
  - "request_configuration"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要为单个请求设置超时、代理、重试或重定向行为"
  - "不确定某个 meta 键的名称或用途"
examples:
  - input: "需要为某个请求设置下载超时"
    output: "在 Request 的 meta 中设置 download_timeout 键"
    notes: "download_timeout 为单请求级超时覆盖"
  - input: "需要为某个请求指定代理"
    output: "在 Request 的 meta 中设置 proxy 键"
    notes: "proxy 为单请求级代理设置"
---

# Scrapy Request.meta 特殊键配置参考

列举并说明 Scrapy Request.meta 中可用的特殊键（如 bindaddress、download_timeout、max_retry_times、proxy、dont_redirect 等），用于在构造请求时按需设置下载行为。适用于需要查阅或选择 meta 键来调整单个请求行为的场景。

## Prompt

当需要为单个 Scrapy 请求调整下载行为（超时、代理、重试、重定向、缓存、cookie 等）时，查阅本参考清单，确认目标 meta 键的名称与用途，再在构造 Request 时按需设置。仅用于键名与用途查阅，不涉及跨阶段流程编排或自定义中间件实现。

## Objective

提供 Request.meta 特殊键的权威清单与用途说明，供构造请求时查阅
## Applicable Signals

- 构造 Request 时需要覆盖默认下载行为
- 需要确认 meta 键的准确名称以避免拼写错误
- 需要按请求粒度而非全局设置调整行为

## Contraindications

- 需要跨阶段爬虫流程编排
- 需要编写自定义中间件逻辑

## Intervention Moves

- 从清单中定位与目标行为对应的 meta 键
- 确认该键的用途与作用范围（单请求级）
- 在 Request 构造时将该键写入 meta 字典

## Workflow Steps

- 明确要调整的下载行为（超时、代理、重试、重定向、缓存、cookie、大小限制等）
- 在 meta 特殊键清单中查找对应键名
- 核对键名拼写与用途说明
- 在构造 Request 时将该键写入 meta 字典

## Constraints

- 仅用于单请求级 meta 键查阅与设置
- 不替代全局 Settings 配置
- 不涉及中间件实现细节

## Cautions

- 部分键（如 download_latency、redirect_urls、redirect_reasons、is_start_request）由框架写入，通常不应由用户手动设置
- 键名拼写错误不会报错但会静默失效

## Output Contract

- 选定并正确设置所需的 meta 键

## Example Therapist Responses

### Example 1

- Client/Input: 需要为某个请求设置下载超时
- Therapist/Output: 在 Request 的 meta 中设置 download_timeout 键
- Notes: download_timeout 为单请求级超时覆盖

### Example 2

- Client/Input: 需要为某个请求指定代理
- Therapist/Output: 在 Request 的 meta 中设置 proxy 键
- Notes: proxy 为单请求级代理设置

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要为单个请求设置超时、代理、重试或重定向行为
- 不确定某个 meta 键的名称或用途

## Examples

### Example 1

Input:

  需要为某个请求设置下载超时

Output:

  在 Request 的 meta 中设置 download_timeout 键

Notes:

  download_timeout 为单请求级超时覆盖

### Example 2

Input:

  需要为某个请求指定代理

Output:

  在 Request 的 meta 中设置 proxy 键

Notes:

  proxy 为单请求级代理设置
