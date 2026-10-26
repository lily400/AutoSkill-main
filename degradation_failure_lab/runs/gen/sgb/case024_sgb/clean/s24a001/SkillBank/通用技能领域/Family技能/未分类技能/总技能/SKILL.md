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
- Feed 存储后端选择与依赖校验 ｜ 类型：feed_export ｜ 适用条件：根据目标输出位置为 Scrapy feed 选择内置存储后端（本地文件系统、FTP、S3、GCS、标准输出），并在使用前校验所需外部库是否已安装，给出可用后端与依赖校验结论。
- Feed 导出设置参考清单 ｜ 类型：数据导出配置 ｜ 适用条件：提供 Scrapy feed 导出相关设置项的参考清单，用于查阅有哪些导出配置项，或在排查导出行为时对照设置项；仅作参考，不执行具体配置操作。
- Feed 导出配置回退解析 ｜ 类型：feed_export_configuration ｜ 适用条件：根据每个 feed 定义逐键解析导出配置，缺失键回退到对应全局设置（如 FEED_EXPORT_ENCODING、FEED_EXPORT_FIELDS、FEED_STORE_EMPTY、FEED_URI_PARAMS），确定最终生效的 feed 参数及回退来源。
- Feed 覆盖与追加策略选择 ｜ 类型：feed_export_configuration ｜ 适用条件：根据目标存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并判断该后端是否支持追加写入。用于配置 feed 写入模式时。
- FTP Feed 存储配置 ｜ 类型：feed_export ｜ 适用条件：配置 Scrapy feed 导出到 FTP 服务器，包括 ftp 方案 URI 构造与主动/被动连接模式选择。适用于需要将抓取结果直接写入 FTP 的场景。
- Scrapy GCS Feed 导出配置 ｜ 类型：feed_export ｜ 适用条件：配置 Scrapy feed 导出到 Google Cloud Storage：使用 gs:// URI 方案，并依赖 google-cloud-storage 库完成认证与写入。当需要把抓取结果写入 GCS 存储桶时使用。
- Scrapy 本地文件系统 Feed 导出配置 ｜ 类型：feed_export ｜ 适用条件：配置 Scrapy feed 导出到本地文件系统，使用 file URI scheme、Unix 绝对路径或 pathlib.Path 对象指定存储目标。
- 延迟文件投递存储后端识别 ｜ 类型：feed_export ｜ 适用条件：在配置 Scrapy feed 导出时，识别哪些存储后端采用延迟文件投递语义，并据此选择合适的存储后端或排查导出结果未即时出现的问题。

## 选用规则（一级技能目录）
- 当问题命中“需要把抓取结果导出到本地、FTP、S3、GCS 或标准输出、不确定某存储后端是否可用、需要确认存储后端的外部依赖是否满足、scrapy”这类线索时，优先选择 Feed 存储后端选择与依赖校验。
- 当问题命中“需要了解有哪些 feed 导出相关设置项、排查导出行为时对照设置清单、查阅 feed 导出可用配置项、scrapy”这类线索时，优先选择 Feed 导出设置参考清单。
- 当问题命中“需要确认某个 feed 键的最终取值、某个 feed 键未显式提供，需要知道回退设置、scrapy、feed”这类线索时，优先选择 Feed 导出配置回退解析。
- 当问题命中“需要决定 feed 文件是否覆盖或追加、目标存储后端可能不支持追加操作、配置 feed 的 overwrite 参数、scrapy”这类线索时，优先选择 Feed 覆盖与追加策略选择。
- 当问题命中“需要将 feed 导出到 FTP 服务器、需要切换 FTP 主动/被动连接模式、scrapy、feed_export”这类线索时，优先选择 FTP Feed 存储配置。
- 当问题命中“需要将 feed 导出到 Google Cloud Storage、目标导出 URI 以 gs:// 开头、需要为 Scrapy feed 配置 GCS 存储后端、scrapy”这类线索时，优先选择 Scrapy GCS Feed 导出配置。
- 当问题命中“需要把抓取结果导出到本机文件、用户询问 file URI 或绝对路径写法、需要为 feed 指定本地文件系统存储目标、scrapy”这类线索时，优先选择 Scrapy 本地文件系统 Feed 导出配置。
- 当问题命中“需要判断某存储后端是否延迟写入文件、导出结果未按预期即时出现需排查存储后端行为、在多个存储后端间选择时需考虑写入时机、scrapy”这类线索时，优先选择 延迟文件投递存储后端识别。

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
