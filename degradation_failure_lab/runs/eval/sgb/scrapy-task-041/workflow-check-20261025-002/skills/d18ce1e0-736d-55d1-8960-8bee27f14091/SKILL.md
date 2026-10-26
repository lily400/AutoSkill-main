---
id: "d18ce1e0-736d-55d1-8960-8bee27f14091"
name: "请求hostname安全判定"
description: "对单个请求解析其URL的hostname，并用已初始化的允许域名正则判断该请求是否应被跟随；hostname为空（如javascript链接等错误URL）时按不匹配处理。用于单请求的站内/站外判定。"
version: "0.1.0"
tags:
  - "scrapy"
  - "offsite"
  - "should_follow"
  - "hostname"
  - "正则匹配"
triggers:
  - "需要对单个请求做站内/站外判定"
  - "已有host_regex并需判断某请求是否应跟随"
---

# 请求hostname安全判定

对单个请求解析其URL的hostname，并用已初始化的允许域名正则判断该请求是否应被跟随；hostname为空（如javascript链接等错误URL）时按不匹配处理。用于单请求的站内/站外判定。

## Prompt

输入一个请求对象与已初始化的host_regex。先通过缓存的URL解析取得请求的hostname；若hostname为None或空字符串，则视为不匹配。否则用host_regex对hostname执行search，返回布尔结果表示是否应跟随该请求。不要在此步骤构建或修改正则，也不要执行调度阶段的过滤逻辑。

## Objective

判断单个请求是否属于允许域名
## Applicable Signals

- 需要对单个请求做站内/站外判定
- host_regex已初始化可用

## Contraindications

- host_regex尚未初始化
- 需要构建或修改允许域名正则
- 需要执行调度阶段的批量过滤

## Intervention Moves

- 用缓存URL解析获取请求hostname
- hostname为空时按不匹配处理
- 用host_regex对hostname执行search并返回布尔结果

## Workflow Steps

- 取得已初始化的host_regex
- 通过urlparse_cached解析请求，取hostname，空值置为空字符串
- 用host_regex.search(host)判断是否匹配
- 返回布尔值表示是否应跟随该请求

## Constraints

- hostname可能为None（如javascript链接），须按不匹配处理
- 仅做单请求判定，不构建正则、不做调度过滤

## Cautions

- host_regex未初始化时不应调用本判定

## Output Contract

- 返回布尔值表示是否应跟随该请求

## Triggers

- 需要对单个请求做站内/站外判定
- 已有host_regex并需判断某请求是否应跟随
