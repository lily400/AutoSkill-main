---
id: "5ce59155-7453-5a08-a86c-28d26cba5683"
name: "设置 FEEDS 导出目标"
description: "在 Scrapy 的 FEEDS 设置中声明导出目标，指定 URI 与序列化格式（及可选参数），作为 feed 导出的强制入口配置。适用于需要新增或修改导出目标时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed-exports"
  - "settings"
  - "FEEDS"
  - "数据导出"
triggers:
  - "需要新增一个导出目标"
  - "需要修改现有导出 URI 或格式"
  - "需要为 feed 导出声明强制入口配置"
---

# 设置 FEEDS 导出目标

在 Scrapy 的 FEEDS 设置中声明导出目标，指定 URI 与序列化格式（及可选参数），作为 feed 导出的强制入口配置。适用于需要新增或修改导出目标时。

## Prompt

在 Scrapy 项目设置中配置 FEEDS 字典：以导出 URI 为键，值为包含 format 等可选参数的映射。FEEDS 为强制设置，默认空字典 {}。仅当需要新增或修改导出目标时执行；若只是调整编码、缩进等次要参数，应改用对应独立设置而非改动 FEEDS 结构。

## Objective

正确填写 FEEDS 字典以指定导出 URI 与格式。
## Applicable Signals

- 需要新增一个导出目标
- 需要修改现有导出 URI 或格式

## Contraindications

- 仅调整编码或缩进等次要参数时不应改动 FEEDS 结构
- 未确定导出 URI 或格式时不应写入 FEEDS

## Intervention Moves

- 在设置中定义 FEEDS 字典
- 以 URI 为键、格式映射为值声明导出目标
- 确认 FEEDS 非空且包含有效 URI 与格式

## Workflow Steps

- 确认需要新增或修改的导出目标 URI 与格式
- 在设置中编写 FEEDS 字典，URI 作为键，值为含 format 的映射
- 校验 FEEDS 中包含有效的 URI 与格式映射

## Constraints

- FEEDS 为强制设置，默认值为空字典 {}
- 导出目标必须以 URI 与格式映射的形式声明

## Cautions

- 编码、缩进、字段等次要参数应通过各自独立设置调整，避免与 FEEDS 入口配置混淆

## Output Contract

- FEEDS 中包含有效的 URI 与格式映射。

## Triggers

- 需要新增一个导出目标
- 需要修改现有导出 URI 或格式
- 需要为 feed 导出声明强制入口配置
