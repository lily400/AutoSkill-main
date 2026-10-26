---
id: "d5862d9c-e48d-5b19-9342-c94d0fbc3157"
name: "Feed 存储后端 URI 配置"
description: "通过 FEEDS 设置使用一个或多个 URI 定义 feed 存储位置，并按 URI scheme 选择本地文件系统、FTP、S3、GCS 或标准输出等存储后端。适用于需要将导出结果写入特定存储位置的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "storage_backend"
  - "FEEDS"
  - "URI"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
  - "kind:parent"
triggers:
  - "需要将 feed 写入远程或本地存储"
  - "需要多目标存储输出"
  - "需要按 URI scheme 选择存储后端"
---

# Feed 存储后端 URI 配置

通过 FEEDS 设置使用一个或多个 URI 定义 feed 存储位置，并按 URI scheme 选择本地文件系统、FTP、S3、GCS 或标准输出等存储后端。适用于需要将导出结果写入特定存储位置的场景。

## Prompt

当需要为 feed 导出指定存储位置时，使用 FEEDS 设置配置一个或多个 URI。根据 URI scheme 选择对应存储后端（本地文件系统、FTP、S3、GCS、标准输出）。若需扩展或自定义存储后端，可通过 FEED_STORAGES 相关设置调整。确认每个 URI 的 scheme 与目标后端匹配后再启用导出。

## Objective

为 feed 导出配置正确的存储后端与 URI
## Applicable Signals

- 需要将 feed 写入远程或本地存储
- 需要多目标存储输出
- 需要按 URI scheme 选择存储后端

## Contraindications

- 仅需选择序列化格式而存储位置已确定

## Intervention Moves

- 在 FEEDS 设置中定义一个或多个存储 URI
- 根据 URI scheme 匹配本地文件系统、FTP、S3、GCS 或标准输出后端
- 如需扩展后端，通过 FEED_STORAGES 相关设置配置

## Workflow Steps

- 确定 feed 的目标存储位置（本地、FTP、S3、GCS 或标准输出）
- 在 FEEDS 设置中写入对应的一个或多个 URI
- 确认每个 URI 的 scheme 与目标存储后端匹配
- 如需自定义或扩展后端，调整 FEED_STORAGES 相关设置

## Constraints

- 存储位置必须通过 FEEDS 设置中的 URI 定义
- 存储后端由 URI scheme 决定

## Cautions

- 多目标输出时需确保每个 URI 的 scheme 均正确对应后端

## Output Contract

- 已按 URI scheme 配置好存储后端的 FEEDS 设置

## 子技能目录
- [Feed URI 动态参数注入](通用技能领域/Family技能/未分类技能/微技能/Feed URI 动态参数注入/SKILL.md) ｜ 适用：通过定义 uri_params 函数并配置 FEED_URI_PARAMS，将爬虫运行时属性（如 spider.name）动态注入到 feed 导出 URI 中，实现按爬虫或运行上下文区分的动态导出文件名。适用于多个爬虫共用同一导出命令但需区分输出文件，或需要在导出文件名中包含运行时属性的场景。
- [Feed URI 参数生成器](通用技能领域/Family技能/未分类技能/微技能/Feed URI 参数生成器/SKILL.md) ｜ 适用：实现一个可调用函数，接收默认参数字典与 spider，返回新的参数字典，用于生成 feed 存储 URI 的动态参数（如 batch_id、batch_time、time）。适用于需要按批次或时间动态构造 feed 文件路径、配置 FEED_URI_PARAMS 的场景。
- [Feed 压缩导出配置](通用技能领域/Family技能/未分类技能/微技能/Feed 压缩导出配置/SKILL.md) ｜ 适用：为 Scrapy feed 导出选择并配置压缩方式（gzip、lzma、bz2），通过 feed_options 传入对应压缩参数，以减小导出文件体积或满足传输要求。
- [Scrapy 标准输出 Feed 导出](通用技能领域/Family技能/未分类技能/微技能/Scrapy 标准输出 Feed 导出/SKILL.md) ｜ 适用：将抓取到的 item 通过 stdout 存储后端直接写入 Scrapy 进程的标准输出，无需任何外部库。适用于需要即时查看导出结果或通过管道交给下游进程、且不需要持久化文件的场景。
- [批量 Feed 输出文件命名占位符配置](通用技能领域/Family技能/未分类技能/微技能/批量 Feed 输出文件命名占位符配置/SKILL.md) ｜ 适用：在 Scrapy feed 导出会生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符区分不同输出文件名，并可用 printf 风格格式化控制编号位数。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `Feed URI 动态参数注入` 时，优先调用它。 线索：需要在导出文件名中包含爬虫名称或其他运行时属性, 多个爬虫共用同一导出命令但需区分输出文件, scrapy, feed_export, uri_parameterization
- 当目标、阶段或方法更接近 `Feed URI 参数生成器` 时，优先调用它。 线索：需要按批次或时间动态构造 feed 文件路径, 配置 FEED_URI_PARAMS 时, scrapy, feed_export, uri_param_generation
- 当目标、阶段或方法更接近 `Feed 压缩导出配置` 时，优先调用它。 线索：需要压缩导出文件, 需指定 gzip/lzma/bz2 压缩参数, scrapy, feed_export, compression
- 当目标、阶段或方法更接近 `Scrapy 标准输出 Feed 导出` 时，优先调用它。 线索：需要即时查看导出结果而不落盘, 导出结果需通过管道交给下游进程, scrapy, feed_export, stdout
- 当目标、阶段或方法更接近 `批量 Feed 输出文件命名占位符配置` 时，优先调用它。 线索：需要一次导出生成多个文件, 输出文件名需要按批次区分或排序, scrapy, feed_export, uri_placeholder

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要将 feed 写入远程或本地存储
- 需要多目标存储输出
- 需要按 URI scheme 选择存储后端
