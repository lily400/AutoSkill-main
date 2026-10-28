---
id: "9ccdd3de-95c4-539a-8b1a-1d6792e1b2f3"
name: "评审到SKU适用性分析流程"
description: "对产品目录与评审数据执行校验、类别匹配与语义相似度映射、情感分类和按SKU计数，产出每SKU计数JSON与简洁状态消息，并标注假设与阻塞项。"
version: "0.1.0"
tags:
  - "评审-SKU映射"
  - "语义匹配"
  - "情感分类"
  - "计数汇总"
  - "运营分析"
triggers:
  - "需要将评审映射到产品SKU并统计计数"
  - "需要输出每SKU计数JSON和状态消息"
  - "收到产品目录与评审数据并要求完成适用性分析"
examples:
  - input: "产品目录JSON与评审数据，要求完成评审到SKU适用性分析"
    output: "每SKU计数JSON及状态消息，标注类别归一化与数据覆盖假设"
    notes: "类别标签临时归入错误类别时按语义判断并标注"
---

# 评审到SKU适用性分析流程

对产品目录与评审数据执行校验、类别匹配与语义相似度映射、情感分类和按SKU计数，产出每SKU计数JSON与简洁状态消息，并标注假设与阻塞项。

## Prompt

执行评审到SKU的适用性分析：先校验产品目录JSON（对象数量与类别取值，类别应仅限tops/bottoms/outerwear）与评审数据（所需列齐全、行数覆盖范围），再按类别匹配与语义相似度将每条评审映射到对应SKU，对映射结果进行情感分类，按SKU汇总计数，最终输出每SKU计数JSON及简洁状态消息。若输入不完美，按可标注假设的方式继续并明确说明假设与阻塞项及解决所需。

## Objective

完成评审到SKU的适用性分析并输出每SKU计数与状态消息
## Applicable Signals

- 提供了产品目录JSON与评审数据
- 任务要求按SKU汇总评审计数
- 下游需要每SKU计数JSON与状态消息

## Contraindications

- 输入目录或评审数据未通过一致性校验且无法标注假设
- 任务不涉及SKU映射或计数

## Intervention Moves

- 校验产品目录JSON结构与类别取值
- 校验评审数据列完整性
- 按类别匹配与语义相似度将评审映射到SKU
- 对映射后的评审进行情感分类
- 按SKU汇总计数
- 输出每SKU计数JSON与状态消息

## Workflow Steps

- 读取并校验产品目录JSON，确认对象数量与类别取值（仅tops/bottoms/outerwear）
- 读取并校验评审数据，确认所需列齐全
- 对每条评审执行类别匹配与语义相似度判断，映射到对应SKU
- 对映射结果进行情感分类
- 按SKU汇总计数
- 生成每SKU计数JSON与简洁状态消息，标注任何假设与阻塞项

## Constraints

- 类别应仅限tops/bottoms/outerwear
- 目录应在分析前尽量完整
- 若数据不完美，需在结果中明确标注假设
- 若存在阻塞，需清楚说明阻塞项及解决所需

## Cautions

- 类别标签可能被临时归入错误类别，需按语义判断而非仅依赖字段名
- 评审数据可能缺少列或行数不足，需说明覆盖范围
- 不得因个别字段问题而静默阻塞，应标注假设后继续

## Output Contract

- 每SKU计数JSON及简洁状态消息，包含假设标注与阻塞说明（如有）

## Example Therapist Responses

### Example 1

- Client/Input: 产品目录JSON与评审数据，要求完成评审到SKU适用性分析
- Therapist/Output: 每SKU计数JSON及状态消息，标注类别归一化与数据覆盖假设
- Notes: 类别标签临时归入错误类别时按语义判断并标注

## Triggers

- 需要将评审映射到产品SKU并统计计数
- 需要输出每SKU计数JSON和状态消息
- 收到产品目录与评审数据并要求完成适用性分析

## Examples

### Example 1

Input:

  产品目录JSON与评审数据，要求完成评审到SKU适用性分析

Output:

  每SKU计数JSON及状态消息，标注类别归一化与数据覆盖假设

Notes:

  类别标签临时归入错误类别时按语义判断并标注
