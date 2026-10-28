---
id: "84d5fe5e-e708-590e-8eef-c0647819df6e"
name: "输出数据有效性校验"
description: "在结构化输出提交或下游消费前，对 JSON 输出执行字段级数据有效性检查：确认标识字段与产品目录完全一致（区分大小写）、计数字段为整数且非负、JSON 可解析。用于输出交付前的质量把关。"
version: "0.1.0"
tags:
  - "输出校验"
  - "数据有效性"
  - "JSON"
  - "质量把关"
  - "sku_id"
triggers:
  - "生成含 sku_id 与计数字段的 JSON 输出后"
  - "需要确认输出可被下游系统解析时"
  - "输出提交或下游消费前的质量把关"
examples:
  - input: "含 sku_id 与四个计数字段的 JSON 输出"
    output: "校验通过，放行合规 JSON"
    notes: "所有 sku_id 与目录一致、计数为整数且非负、JSON 可解析"
  - input: "含负计数值的 JSON 输出"
    output: "校验失败：计数字段存在负值"
    notes: "标记失败并指明具体失败项，不放行"
---

# 输出数据有效性校验

在结构化输出提交或下游消费前，对 JSON 输出执行字段级数据有效性检查：确认标识字段与产品目录完全一致（区分大小写）、计数字段为整数且非负、JSON 可解析。用于输出交付前的质量把关。

## Prompt

在输出交付前执行数据有效性校验。逐项检查：1) 所有 sku_id 是否与产品目录中的值完全一致（区分大小写）；2) 四个计数字段是否均为整数；3) 所有计数是否 ≥ 0（无负值）；4) JSON 是否格式正确且可解析。任一项不通过则标记失败并说明具体失败项，不得放行。

## Objective

在输出交付前拦截格式错误、非法标识与非法计数值
## Applicable Signals

- 已生成含 sku_id 与计数字段的 JSON 输出
- 输出即将提交或交付下游系统

## Contraindications

- 输入本身缺失或无法解析，需先走无效输入处理流程
- 仅需检查逻辑一致性而非字段级有效性时

## Intervention Moves

- 逐项核对 sku_id 与产品目录完全一致（区分大小写）
- 确认四个计数字段均为整数
- 确认所有计数 ≥ 0
- 确认 JSON 格式正确且可解析
- 任一项不通过则标记失败并指明失败项

## Workflow Steps

- 读取待校验的 JSON 输出
- 核对所有 sku_id 与产品目录完全一致（区分大小写）
- 检查四个计数字段均为整数
- 检查所有计数 ≥ 0（无负值）
- 验证 JSON 格式正确且可解析
- 全部通过则放行；否则标记失败并列出具体失败项

## Constraints

- sku_id 必须与产品目录完全一致且区分大小写
- 四个计数字段必须为整数
- 所有计数必须 ≥ 0
- JSON 必须格式正确且可解析

## Cautions

- 本检查聚焦格式与字段级有效性，不替代逻辑一致性检查
- 输入缺失或无法解析时应先走无效输入处理流程，而非直接校验

## Output Contract

- 通过全部有效性检查的合规 JSON 输出，或带有明确失败标记及具体失败项的校验结果

## Example Therapist Responses

### Example 1

- Client/Input: 含 sku_id 与四个计数字段的 JSON 输出
- Therapist/Output: 校验通过，放行合规 JSON
- Notes: 所有 sku_id 与目录一致、计数为整数且非负、JSON 可解析

### Example 2

- Client/Input: 含负计数值的 JSON 输出
- Therapist/Output: 校验失败：计数字段存在负值
- Notes: 标记失败并指明具体失败项，不放行

## Triggers

- 生成含 sku_id 与计数字段的 JSON 输出后
- 需要确认输出可被下游系统解析时
- 输出提交或下游消费前的质量把关

## Examples

### Example 1

Input:

  含 sku_id 与四个计数字段的 JSON 输出

Output:

  校验通过，放行合规 JSON

Notes:

  所有 sku_id 与目录一致、计数为整数且非负、JSON 可解析

### Example 2

Input:

  含负计数值的 JSON 输出

Output:

  校验失败：计数字段存在负值

Notes:

  标记失败并指明具体失败项，不放行
