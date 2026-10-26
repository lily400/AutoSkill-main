---
id: "bf71575c-b5d5-58ca-8289-0e9c2383eb7e"
name: "Scrapy 标准输出 Feed 导出"
description: "将抓取到的 item 通过 stdout 存储后端直接写入 Scrapy 进程的标准输出，无需任何外部库。适用于需要即时查看导出结果或通过管道交给下游进程、且不需要持久化文件的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "stdout"
  - "storage_backend"
triggers:
  - "需要即时查看导出结果而不落盘"
  - "导出结果需通过管道交给下游进程"
---

# Scrapy 标准输出 Feed 导出

将抓取到的 item 通过 stdout 存储后端直接写入 Scrapy 进程的标准输出，无需任何外部库。适用于需要即时查看导出结果或通过管道交给下游进程、且不需要持久化文件的场景。

## Prompt

当需要把 feed 导出到进程标准输出时，配置一个使用 stdout: URI 的 feed 导出。确认该存储后端不需要任何外部库；若需要持久化文件或远程存储，或需要延迟文件投递语义，则改用其他存储后端。

## Objective

使用 stdout 存储后端将 feed 输出到进程标准输出
## Applicable Signals

- 需要即时查看导出结果而不落盘
- 导出结果需通过管道交给下游进程

## Contraindications

- 需要持久化文件或远程存储
- 需要延迟文件投递语义

## Intervention Moves

- 选择 stdout 存储后端
- 配置使用 stdout: URI 的 feed 导出
- 确认无需安装外部库

## Workflow Steps

- 确认导出目标是进程标准输出而非文件或远程存储
- 配置 feed 使用 stdout: URI（URI scheme 为 stdout）
- 确认无需额外外部库即可运行
- 运行后从标准输出读取序列化后的 item

## Constraints

- 仅覆盖 stdout 这一单一存储后端配置动作
- 不适用于需要持久化或延迟文件投递的场景

## Cautions

- 标准输出会与进程其他输出混在一起，下游消费时需注意区分

## Output Contract

- 配置了 stdout: URI 的 feed 导出，item 序列化后写入标准输出

## Triggers

- 需要即时查看导出结果而不落盘
- 导出结果需通过管道交给下游进程
