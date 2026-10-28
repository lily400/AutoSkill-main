---
id: "b8eb69db-0a6a-5752-a165-55c26d41304c"
name: "预爬虫阶段设置配置"
description: "在安装或启动 reactor 之前，配置 Scrapy 的预爬虫阶段特殊设置（ASYNCIO_EVENT_LOOP、TWISTED_REACTOR、DNS_RESOLVER 及相关 DNS 设置、REACTOR_THREADPOOL_MAXSIZE），以确保爬虫启动时使用正确的异步事件循环、DNS 解析器和线程池容量。"
version: "0.1.0"
tags:
  - "scrapy"
  - "settings"
  - "pre-crawl"
  - "reactor"
  - "dns"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要自定义异步事件循环或 Twisted reactor"
  - "需要调整 DNS 解析器或 DNS 缓存相关参数"
  - "需要设置 reactor 线程池最大容量"
---

# 预爬虫阶段设置配置

在安装或启动 reactor 之前，配置 Scrapy 的预爬虫阶段特殊设置（ASYNCIO_EVENT_LOOP、TWISTED_REACTOR、DNS_RESOLVER 及相关 DNS 设置、REACTOR_THREADPOOL_MAXSIZE），以确保爬虫启动时使用正确的异步事件循环、DNS 解析器和线程池容量。

## Prompt

当需要自定义异步事件循环、Twisted reactor、DNS 解析器或 reactor 线程池容量时，使用本技能。先确认当前是否使用 AsyncCrawlerProcess，以及 reactor 是否已安装；据此判断哪些设置可配置、在何时生效。输出一份预爬虫阶段设置清单，标明每项设置的生效时机（安装 reactor 时或启动 reactor 时）。

## Objective

正确配置预爬虫阶段设置，使 reactor 安装和启动时使用指定的异步事件循环、DNS 解析器和线程池大小。
## Applicable Signals

- 需要自定义异步事件循环或 Twisted reactor
- 需要调整 DNS 解析器或 DNS 缓存相关参数
- 需要设置 reactor 线程池最大容量

## Contraindications

- 使用 AsyncCrawlerProcess 时尝试按 spider 设置 ASYNCIO_EVENT_LOOP 或 TWISTED_REACTOR
- 在 reactor 已安装后尝试修改这些设置

## Intervention Moves

- 识别预爬虫阶段设置项：ASYNCIO_EVENT_LOOP、TWISTED_REACTOR、DNS_RESOLVER 及对应 DNS 设置（如 DNSCACHE_ENABLED、DNSCACHE_SIZE、DNS_TIMEOUT）、REACTOR_THREADPOOL_MAXSIZE
- 区分生效时机：ASYNCIO_EVENT_LOOP 与 TWISTED_REACTOR 在安装 reactor 时生效，其余设置在启动 reactor 时生效
- 确认是否使用 AsyncCrawlerProcess，以判断 ASYNCIO_EVENT_LOOP 与 TWISTED_REACTOR 是否可按 spider 设置

## Workflow Steps

- 确认运行方式：是否使用 AsyncCrawlerProcess
- 确认 reactor 是否已安装
- 列出需要调整的预爬虫阶段设置项
- 标注每项设置的生效时机（安装 reactor 时或启动 reactor 时）
- 输出配置清单

## Constraints

- ASYNCIO_EVENT_LOOP 与 TWISTED_REACTOR 在安装 reactor 时生效
- DNS_RESOLVER 及相关 DNS 设置、REACTOR_THREADPOOL_MAXSIZE 在启动 reactor 时生效
- 使用 AsyncCrawlerProcess 时，ASYNCIO_EVENT_LOOP 与 TWISTED_REACTOR 无法按 spider 设置，TWISTED_REACTOR 被忽略

## Cautions

- 这些设置必须在 reactor 安装或启动之前确定，安装后修改无效

## Output Contract

- 一份明确列出预爬虫阶段设置项及其生效时机的配置说明或配置清单。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要自定义异步事件循环或 Twisted reactor
- 需要调整 DNS 解析器或 DNS 缓存相关参数
- 需要设置 reactor 线程池最大容量
