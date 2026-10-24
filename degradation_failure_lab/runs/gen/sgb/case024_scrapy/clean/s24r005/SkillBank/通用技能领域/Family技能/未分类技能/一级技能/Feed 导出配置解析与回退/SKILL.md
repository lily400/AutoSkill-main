---
id: "1ed8b5f3-d142-54b2-86a1-a18ac23b8fd9"
name: "Feed 导出配置解析与回退"
description: "解析 Scrapy feed 定义中的导出配置键（format、encoding、fields、batch_item_count、overwrite、store_empty、uri_params、postprocessing 等），并在键缺失时确定其对应的 FEED_* 全局设置回退值。用于配置 FEEDS 或排查导出参数未生效时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed"
  - "configuration"
  - "fallback"
  - "export"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要确定某个 feed 键的取值来源"
  - "配置 FEEDS 或排查导出参数未生效"
  - "需要核对 feed 定义与全局 FEED_* 设置的优先级"
examples:
  - input: "feed 定义仅给出 format=csv，未给出 encoding 与 overwrite，存储为本地文件系统。"
    output: "format=csv（显式）；encoding 回退到 FEED_EXPORT_ENCODING；overwrite=False（本地文件系统默认）。"
    notes: "format 无回退，必须显式提供。"
---

# Feed 导出配置解析与回退

解析 Scrapy feed 定义中的导出配置键（format、encoding、fields、batch_item_count、overwrite、store_empty、uri_params、postprocessing 等），并在键缺失时确定其对应的 FEED_* 全局设置回退值。用于配置 FEEDS 或排查导出参数未生效时。

## Prompt

给定一个 feed 定义（键值映射），逐键解析其最终生效值：若 feed 定义中显式提供该键则采用显式值；否则回退到对应的 FEED_* 设置；对无回退的键（如 format）标记为必填缺失。输出一份解析后的配置映射，标明每个键的来源（显式/回退/缺失）。

## Objective

正确解析 feed 定义键及其全局设置回退值
## Applicable Signals

- feed 定义中某键未显式给出
- 导出参数疑似未生效
- 需要确认 overwrite 等键的默认行为

## Contraindications

- 需要实现自定义 exporter 或 storage 后端
- 需要执行实际序列化或存储写入流程

## Intervention Moves

- 逐键比对 feed 定义与 FEED_* 回退设置
- 对无回退键（format）标记为必填
- 对 overwrite 按存储后端确定默认值
- 对 postprocessing 保留列表顺序

## Workflow Steps

- 读取 feed 定义中的显式键值。
- 对每个键查找对应 FEED_* 回退设置：batch_item_count→FEED_EXPORT_BATCH_ITEM_COUNT，encoding→FEED_EXPORT_ENCODING，fields→FEED_EXPORT_FIELDS，indent→FEED_EXPORT_INDENT，store_empty→FEED_STORE_EMPTY，uri_params→FEED_URI_PARAMS。
- 确认 format 为必填，无回退值，缺失即报错。
- 对 item_classes 未定义或为空时视为导出全部 item；item_filter 默认使用 ItemFilter。
- 对 overwrite 按存储后端确定默认值：本地文件系统 False，FTP True，S3 True，GCS True，标准输出 False。
- 保留 postprocessing 插件列表顺序。
- 汇总输出解析后的配置映射，标明每个键的来源。

## Constraints

- format 为必填键，无回退值。
- overwrite 默认值依赖存储后端，不可统一假设。
- postprocessing 插件按列表顺序使用。

## Cautions

- 部分 FTP 服务器可能不支持追加（APPE 命令）。
- S3、GCS 与标准输出不支持追加，overwrite 默认 True 或 False 需按后端区分。

## Output Contract

- 一份解析后的 feed 配置映射，标明每个键的显式值或回退设置及其来源。

## Example Therapist Responses

### Example 1

- Client/Input: feed 定义仅给出 format=csv，未给出 encoding 与 overwrite，存储为本地文件系统。
- Therapist/Output: format=csv（显式）；encoding 回退到 FEED_EXPORT_ENCODING；overwrite=False（本地文件系统默认）。
- Notes: format 无回退，必须显式提供。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要确定某个 feed 键的取值来源
- 配置 FEEDS 或排查导出参数未生效
- 需要核对 feed 定义与全局 FEED_* 设置的优先级

## Examples

### Example 1

Input:

  feed 定义仅给出 format=csv，未给出 encoding 与 overwrite，存储为本地文件系统。

Output:

  format=csv（显式）；encoding 回退到 FEED_EXPORT_ENCODING；overwrite=False（本地文件系统默认）。

Notes:

  format 无回退，必须显式提供。
