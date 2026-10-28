---
id: "2f1bc8c6-2861-5c8a-958a-6d30100bd274"
name: "评论分类字段小写规范化"
description: "将评论 CSV 中的分类字段（如 is_sportswear、is_apparel_product）取值统一转换为严格小写，处理大写或混合大小写的行，使数据符合下游小写格式契约，同时保持行数与其余字段不变。"
version: "0.1.0"
tags:
  - "数据清洗"
  - "取值规范化"
  - "评论数据"
  - "预处理"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "发现分类字段存在大写或混合大小写取值"
  - "评论数据需清洗以符合下游小写格式契约"
examples:
  - input: "is_sportswear 取值为 \"Yes\""
    output: "is_sportswear 取值为 \"yes\""
    notes: "仅转换大小写，其余字段不变"
---

# 评论分类字段小写规范化

将评论 CSV 中的分类字段（如 is_sportswear、is_apparel_product）取值统一转换为严格小写，处理大写或混合大小写的行，使数据符合下游小写格式契约，同时保持行数与其余字段不变。

## Prompt

读取评论 CSV，识别分类字段（如 is_sportswear、is_apparel_product），扫描各分类字段取值，标记大写或混合大小写的行，将标记取值转换为严格小写（如 "Yes" -> "yes"），校验转换后分类字段全部为小写且行数不变，输出规范化后的数据。

## Objective

使分类取值严格符合小写格式要求
## Applicable Signals

- 分类字段出现大写或混合大小写取值（如 "Yes"）
- 下游要求分类取值严格小写

## Contraindications

- 字段已全部为规范小写
- 需要修改的是缺失列而非取值格式

## Intervention Moves

- 定位分类字段中的非小写取值
- 将取值统一转换为严格小写
- 保持行数与其余字段不变

## Workflow Steps

- 读取评论 CSV 并识别分类字段（如 is_sportswear、is_apparel_product）
- 扫描各分类字段取值，标记大写或混合大小写的行
- 将标记取值转换为严格小写
- 校验转换后分类字段全部为小写且行数不变

## Constraints

- 仅规范化取值大小写，不改变行数
- 不新增或删除列

## Cautions

- 缺失列问题不属于本技能范围，应另行处理

## Output Contract

- 分类字段全部为小写且行数不变的规范化数据

## Example Therapist Responses

### Example 1

- Client/Input: is_sportswear 取值为 "Yes"
- Therapist/Output: is_sportswear 取值为 "yes"
- Notes: 仅转换大小写，其余字段不变

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 发现分类字段存在大写或混合大小写取值
- 评论数据需清洗以符合下游小写格式契约

## Examples

### Example 1

Input:

  is_sportswear 取值为 "Yes"

Output:

  is_sportswear 取值为 "yes"

Notes:

  仅转换大小写，其余字段不变
