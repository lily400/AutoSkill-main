---
id: "0f70cd3f-8916-5100-949a-b17f1bc29338"
name: "Offsite请求域名过滤"
description: "在请求被调度时，基于spider允许域名的正则判断请求是否属于站内；站外请求应被忽略，站内请求继续进入调度。用于控制爬虫只跟随允许域名范围内的链接。"
version: "0.1.0"
tags:
  - "scrapy"
  - "offsite"
  - "域名过滤"
  - "请求调度"
  - "IgnoreRequest"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要限制爬虫只抓取指定域名"
  - "需要拦截站外链接请求"
  - "请求进入request_scheduled阶段需要做域名归属判断"
examples:
  - input: "请求hostname不在允许域名正则范围内"
    output: "该请求被忽略，不进入调度"
    notes: "站外请求拦截"
  - input: "请求hostname匹配允许域名正则"
    output: "该请求继续进入调度"
    notes: "站内请求放行"
---

# Offsite请求域名过滤

在请求被调度时，基于spider允许域名的正则判断请求是否属于站内；站外请求应被忽略，站内请求继续进入调度。用于控制爬虫只跟随允许域名范围内的链接。

## Prompt

当请求进入调度阶段时，使用spider允许域名正则对请求hostname进行匹配：解析请求URL得到hostname（无法解析时视为空字符串），用host_regex.search(host)判断是否站内；站内请求放行继续调度，站外请求按忽略处理。

## Objective

在请求调度阶段过滤掉不属于允许域名的站外请求
## Applicable Signals

- spider已配置允许域名范围
- 请求被调度时需判断是否站内
- 存在站外链接需要被拦截

## Contraindications

- 需要跨域抓取且无域名白名单
- 请求URL无法解析出hostname时不应直接放行

## Intervention Moves

- 在spider_opened时构建host_regex
- 在request_scheduled中调用process_request处理请求
- 用urlparse_cached获取hostname，None时置为空字符串
- 用host_regex.search(host)判断是否站内并决定放行或忽略

## Workflow Steps

- spider_opened阶段通过get_host_regex(spider)构建host_regex
- 请求被调度时触发request_scheduled，调用process_request
- 解析请求得到hostname，无法解析时使用空字符串
- 用host_regex.search(host)判断是否站内
- 站内请求继续进入调度，站外请求被忽略

## Constraints

- 域名判断必须基于spider允许域名正则
- hostname为None时不得直接放行，应按空字符串处理

## Cautions

- hostname可能为None（如javascript链接），需按空字符串处理以避免误判
- 过滤发生在调度阶段，需确保host_regex在spider_opened时已构建

## Output Contract

- 站外请求被忽略，站内请求继续进入调度

## Example Therapist Responses

### Example 1

- Client/Input: 请求hostname不在允许域名正则范围内
- Therapist/Output: 该请求被忽略，不进入调度
- Notes: 站外请求拦截

### Example 2

- Client/Input: 请求hostname匹配允许域名正则
- Therapist/Output: 该请求继续进入调度
- Notes: 站内请求放行

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要限制爬虫只抓取指定域名
- 需要拦截站外链接请求
- 请求进入request_scheduled阶段需要做域名归属判断

## Examples

### Example 1

Input:

  请求hostname不在允许域名正则范围内

Output:

  该请求被忽略，不进入调度

Notes:

  站外请求拦截

### Example 2

Input:

  请求hostname匹配允许域名正则

Output:

  该请求继续进入调度

Notes:

  站内请求放行
