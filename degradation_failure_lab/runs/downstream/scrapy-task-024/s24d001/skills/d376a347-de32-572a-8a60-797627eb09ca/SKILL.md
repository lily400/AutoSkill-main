---
id: "d376a347-de32-572a-8a60-797627eb09ca"
name: "标准输出Feed导出"
description: "将Scrapy抓取到的item通过stdout: URI方案直接写入进程标准输出，无需外部库。适用于需要即时查看抓取结果或通过管道传给下游进程的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed导出"
  - "标准输出"
  - "stdout"
triggers:
  - "需要即时查看抓取结果"
  - "需要将结果通过管道传给下游进程"
---

# 标准输出Feed导出

将Scrapy抓取到的item通过stdout: URI方案直接写入进程标准输出，无需外部库。适用于需要即时查看抓取结果或通过管道传给下游进程的场景。

## Prompt

当需要将Scrapy feed输出到进程标准输出时，使用stdout: URI方案配置feed导出。确认无需外部库依赖，并注意该存储后端可能涉及延迟文件交付语义。

## Objective

通过stdout: URI将feed输出到标准输出
## Applicable Signals

- 需要即时查看抓取结果
- 需要将结果通过管道传给下游进程

## Contraindications

- 需要持久化到文件或远程存储
- 需要延迟文件交付语义

## Intervention Moves

- 在feed配置中使用stdout: URI方案
- 确认无需外部库依赖

## Workflow Steps

- 确认输出目标为进程标准输出而非文件或远程存储
- 使用stdout: URI方案配置feed
- 确认无需安装外部库
- 运行抓取并验证item以序列化格式打印到标准输出

## Constraints

- 仅覆盖stdout存储后端这一单一输出通道
- 不适用于需要持久化到文件或远程存储的场景

## Cautions

- 部分存储后端使用延迟文件交付语义，需注意stdout的行为

## Output Contract

- 抓取item以序列化格式打印到进程标准输出

## Triggers

- 需要即时查看抓取结果
- 需要将结果通过管道传给下游进程
