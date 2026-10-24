---
id: "2fcf2c8c-ee2d-5471-a738-db6f6386065f"
name: "未分类技能"
description: "未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。"
version: "0.1.0"
tags:
  - "未分类技能"
  - "总导航"
  - "子技能地图"
  - "kind:parent"
  - "profile:scrapy::未分类技能"
triggers:
  - "未分类技能"
  - "未分类技能 总导航"
  - "未分类技能 子技能地图"
---

# 未分类技能

未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。

## Prompt

## 适用场景
- 当当前问题明确属于或需要路由到 未分类技能 时，先使用本总技能决定子技能选择顺序。
- 本技能用于导航与组合，不替代子技能中的具体执行 SOP。

## 不适用/风险边界
- 不要把本技能当作具体干预脚本；真正执行时必须继续调用对应子技能。
- 如存在明显高风险或危机信号，应优先调用风险/危机类子技能。

## 总流程
1. 先判断当前问题是否适合进入该家族或领域的处理路径。
2. 再根据任务类型、阶段和风险边界选择最合适的子技能。
3. 调用对应子技能执行具体步骤、规则和输出格式。
4. 最后输出所选子技能、选择理由、执行顺序与风险提示。

## 子技能目录（一级技能目录）
- Feed 导出压缩配置 ｜ 类型：feed_export ｜ 适用条件：为 Scrapy feed 导出选择并配置压缩方式（gzip/lzma/bz2）及其 feed_options 参数，控制输出文件的压缩行为。当需要压缩导出数据文件或指定具体压缩参数时使用。
- Feed 导出设置项参考 ｜ 类型：配置参考 ｜ 适用条件：提供 Scrapy feed 导出相关设置项的查阅参考，列出各设置项名称及其用途，用于确认某个导出设置项的名称或作用。
- Feed 导出配置解析与回退 ｜ 类型：feed_export_configuration ｜ 适用条件：解析 Scrapy feed 定义中的导出配置键（format、encoding、fields、batch_item_count、overwrite、store_empty、uri_params、postprocessing 等），并在键缺失时确定其对应的 FEED_* 全局设置回退值。用于配置 FEEDS 或排查导出参数未生效时。
- Scrapy S3 Feed 存储后端配置 ｜ 类型：feed_export ｜ 适用条件：为 Scrapy feed 导出配置 S3 或 S3 兼容对象存储后端，包括自定义 ACL、endpoint 与 region，并明确 overwrite 默认行为。
- 延迟文件交付时序处理 ｜ 类型：feed导出 ｜ 适用条件：说明部分 feed 存储后端采用延迟文件交付的时序特性，帮助调用方判断下游流程是否可以在 feed 写入后立即依赖文件存在，并据此调整等待或触发逻辑。
- 本地文件系统 Feed 导出配置 ｜ 类型：feed_export ｜ 适用条件：配置 Scrapy feed 导出到本地文件系统：使用 file URI 方案或绝对路径，也可传入 pathlib.Path 对象。适用于需要将抓取结果落盘到本机文件的场景。
- 配置 FTP Feed 存储 ｜ 类型：feed_export ｜ 适用条件：当需要将 Scrapy 抓取结果导出到 FTP 服务器时，使用 ftp:// URI 配置 feed 存储，并可按需切换主动/被动连接模式。

## 选用规则（一级技能目录）
- 当问题命中“需要压缩导出的数据文件、需要指定 gzip/lzma/bz2 压缩参数、scrapy、feed_export”这类线索时，优先选择 Feed 导出压缩配置。
- 当问题命中“需要确认某个导出设置项的名称或作用、查阅 feed 导出配置项清单、scrapy、feed”这类线索时，优先选择 Feed 导出设置项参考。
- 当问题命中“需要确定某个 feed 键的取值来源、配置 FEEDS 或排查导出参数未生效、需要核对 feed 定义与全局 FEED_* 设置的优先级、scrapy”这类线索时，优先选择 Feed 导出配置解析与回退。
- 当问题命中“需要将导出结果写入 S3 或 S3 兼容存储、需要自定义 ACL、endpoint 或 region、scrapy、feed_export”这类线索时，优先选择 Scrapy S3 Feed 存储后端配置。
- 当问题命中“下游流程依赖feed文件已存在、使用支持延迟交付的存储后端、需要在feed写入后立即读取导出文件、scrapy”这类线索时，优先选择 延迟文件交付时序处理。
- 当问题命中“需要把抓取结果保存到本机文件、用户询问 file:// URI 或绝对路径写法、用户询问本地文件 feed 是否需要额外依赖、scrapy”这类线索时，优先选择 本地文件系统 Feed 导出配置。
- 当问题命中“需要将导出文件写入 FTP 服务器、需要调整 FTP 连接模式、scrapy、feed-export”这类线索时，优先选择 配置 FTP Feed 存储。

## 输出格式
- family_route:
  - family: 未分类技能
  - selected_children: [子技能名称列表]
  - rationale: 说明为什么选择这些子技能
  - cautions: 风险边界与切换条件

## Files

- `references/children_manifest.json`
- `references/children_map.md`

## Triggers

- 未分类技能
- 未分类技能 总导航
- 未分类技能 子技能地图
