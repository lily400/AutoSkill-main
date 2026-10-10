---
id: "a4333861-781b-5e31-8d77-8610cdcd674d"
name: "敏感列排除"
description: "使用 qsv select 的否定正则选择器在输出中排除匹配敏感模式的列（如 SSN、account_no、password），适用于数据脱敏或共享前的列裁剪。"
version: "0.1.0"
tags:
  - "qsv"
  - "select"
  - "数据脱敏"
  - "否定正则选择器"
  - "列裁剪"
  - "qsv-select"
  - "profile:qsv::qsv_select"
triggers:
  - "输出将共享或发布"
  - "存在已知敏感列名模式"
  - "需要在数据变换阶段裁剪敏感列"
examples:
  - input: "qsv select '!/SSN|account_no|password/'"
    output: "不包含 SSN、account_no、password 列的 CSV 输出"
    notes: "使用否定正则选择器排除敏感列"
---

# 敏感列排除

使用 qsv select 的否定正则选择器在输出中排除匹配敏感模式的列（如 SSN、account_no、password），适用于数据脱敏或共享前的列裁剪。

## Prompt

当输出将被共享或发布，且存在已知敏感列名模式时，使用 qsv select 的否定正则选择器排除敏感列。

执行步骤：
1. 确认敏感列名模式（如 SSN、account_no、password）。
2. 构造否定正则选择器：qsv select '!/SSN|account_no|password/'。
3. 运行命令生成不含敏感列的 CSV 输出。
4. 校验输出列中不再包含匹配敏感模式的列。

注意：仅在输出将共享或发布时使用；若需保留全部列用于审计或敏感列模式未定义，则不应使用本规则。

## Objective

在输出中移除匹配敏感模式的列
## Applicable Signals

- 输出将共享或发布
- 存在已知敏感列名模式

## Contraindications

- 需要保留全部列用于审计
- 敏感列模式未定义

## Intervention Moves

- 使用否定正则选择器排除敏感列：qsv select '!/SSN|account_no|password/'

## Workflow Steps

- 确认敏感列名模式
- 构造否定正则选择器
- 运行 qsv select 生成输出
- 校验输出不含敏感列

## Constraints

- 仅在输出将共享或发布时使用
- 敏感列模式必须已定义

## Cautions

- 排除后需校验输出列，避免遗漏敏感列

## Output Contract

- 不包含敏感列的 CSV 输出

## Example Therapist Responses

### Example 1

- Client/Input: qsv select '!/SSN|account_no|password/'
- Therapist/Output: 不包含 SSN、account_no、password 列的 CSV 输出
- Notes: 使用否定正则选择器排除敏感列

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 输出将共享或发布
- 存在已知敏感列名模式
- 需要在数据变换阶段裁剪敏感列

## Examples

### Example 1

Input:

  qsv select '!/SSN|account_no|password/'

Output:

  不包含 SSN、account_no、password 列的 CSV 输出

Notes:

  使用否定正则选择器排除敏感列
