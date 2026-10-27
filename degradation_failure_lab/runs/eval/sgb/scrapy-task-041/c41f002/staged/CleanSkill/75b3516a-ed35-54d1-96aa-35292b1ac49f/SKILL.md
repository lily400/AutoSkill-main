---
id: "75b3516a-ed35-54d1-96aa-35292b1ac49f"
name: "允许域名正则构建"
description: "在 spider_opened 阶段根据 spider 配置构建用于匹配允许域名的 host_regex 正则对象，供后续请求过滤逻辑复用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "offsite"
  - "域名规则"
  - "正则构建"
  - "spider_opened"
triggers:
  - "spider启动时需要初始化域名匹配规则"
  - "需要在请求过滤前准备站内域名判定规则"
---

# 允许域名正则构建

在 spider_opened 阶段根据 spider 配置构建用于匹配允许域名的 host_regex 正则对象，供后续请求过滤逻辑复用。

## Prompt

在 spider_opened 阶段调用 get_host_regex(spider) 构建 host_regex 正则对象并保存为实例属性，供后续 should_follow 等请求过滤逻辑复用。仅做规则初始化，不在此步骤过滤请求。

## Objective

在spider_opened阶段构建host_regex
## Applicable Signals

- spider启动时需要初始化域名匹配规则

## Contraindications

- spider尚未打开或未配置允许域名

## Intervention Moves

- 在spider_opened中调用get_host_regex(spider)
- 将返回的正则对象保存为self.host_regex供后续复用

## Workflow Steps

- 在spider_opened(self, spider)中调用self.get_host_regex(spider)
- 将结果赋值给self.host_regex
- 后续请求过滤逻辑直接复用该正则对象

## Constraints

- 仅在spider_opened阶段执行初始化
- 本步骤不执行请求过滤，只构建规则

## Cautions

- hostname可能为None（如javascript链接），匹配时需容错处理

## Output Contract

- 生成可复用的host_regex正则对象

## Triggers

- spider启动时需要初始化域名匹配规则
- 需要在请求过滤前准备站内域名判定规则
