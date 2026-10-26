---
id: "6e8fed6d-ba68-5c69-9aea-416c70136130"
name: "Feed 导出配置回退解析"
description: "根据每个 feed 定义逐键解析导出配置，缺失键回退到对应全局设置（如 FEED_EXPORT_ENCODING、FEED_EXPORT_FIELDS、FEED_STORE_EMPTY、FEED_URI_PARAMS），确定最终生效的 feed 参数及回退来源。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed"
  - "configuration"
  - "fallback"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要确认某个 feed 键的最终取值"
  - "某个 feed 键未显式提供，需要知道回退设置"
examples:
  - input: "feed 定义仅提供 format=csv，未提供 encoding"
    output: "format=csv（显式）；encoding 回退到 FEED_EXPORT_ENCODING 的值"
    notes: "format 无回退，必须显式提供"
---

# Feed 导出配置回退解析

根据每个 feed 定义逐键解析导出配置，缺失键回退到对应全局设置（如 FEED_EXPORT_ENCODING、FEED_EXPORT_FIELDS、FEED_STORE_EMPTY、FEED_URI_PARAMS），确定最终生效的 feed 参数及回退来源。

## Prompt

给定一个 feed 定义（键值对）与可用的全局设置，逐键解析最终生效值：若 feed 定义中显式提供该键则采用其值；否则按回退映射取对应全局设置的值（batch_item_count→FEED_EXPORT_BATCH_ITEM_COUNT，encoding→FEED_EXPORT_ENCODING，fields→FEED_EXPORT_FIELDS，store_empty→FEED_STORE_EMPTY，uri_params→FEED_URI_PARAMS，indent→FEED_EXPORT_INDENT）。注意 format 为必填项，无回退值。输出每个键的最终取值及回退来源。

## Objective

确定每个 feed 定义最终生效的导出参数及其回退来源
## Applicable Signals

- 存在 feed 定义但部分键缺失
- 需要核对 feed 参数与全局设置的优先级

## Contraindications

- 需要实现自定义 exporter 或 storage 类
- 需要处理 item 过滤或后处理插件逻辑

## Intervention Moves

- 逐键检查 feed 定义是否显式提供
- 对缺失键应用对应回退设置
- 标记 format 为必填无回退
- 记录每个键的回退来源

## Workflow Steps

- 读取 feed 定义中的键值对
- 对每个键判断是否显式提供
- 若缺失则按回退映射取全局设置值（batch_item_count→FEED_EXPORT_BATCH_ITEM_COUNT，encoding→FEED_EXPORT_ENCODING，fields→FEED_EXPORT_FIELDS，store_empty→FEED_STORE_EMPTY，uri_params→FEED_URI_PARAMS，indent→FEED_EXPORT_INDENT）
- 确认 format 已提供，否则报错
- 汇总每个键的最终取值与回退来源

## Constraints

- format 为必填项，无回退值
- item_classes 未定义或为空时导出所有 item
- item_filter 默认使用 ItemFilter
- postprocessing 插件按列表顺序执行

## Cautions

- overwrite 默认值依赖存储后端：本地文件系统为 False，FTP 为 True，S3 为 True，GCS 为 True，标准输出为 False
- 部分 FTP 服务器可能不支持 APPE 追加命令
- S3、GCS 与标准输出不支持追加

## Output Contract

- 一份解析后的 feed 参数表，标明每个键的取值及回退来源

## Example Therapist Responses

### Example 1

- Client/Input: feed 定义仅提供 format=csv，未提供 encoding
- Therapist/Output: format=csv（显式）；encoding 回退到 FEED_EXPORT_ENCODING 的值
- Notes: format 无回退，必须显式提供

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要确认某个 feed 键的最终取值
- 某个 feed 键未显式提供，需要知道回退设置

## Examples

### Example 1

Input:

  feed 定义仅提供 format=csv，未提供 encoding

Output:

  format=csv（显式）；encoding 回退到 FEED_EXPORT_ENCODING 的值

Notes:

  format 无回退，必须显式提供
