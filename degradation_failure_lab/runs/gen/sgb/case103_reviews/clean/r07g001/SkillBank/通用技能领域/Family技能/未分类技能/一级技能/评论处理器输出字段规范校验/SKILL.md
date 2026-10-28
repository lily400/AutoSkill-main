---
id: "f9e899fc-f503-5a1c-8705-424e9e1c5fee"
name: "评论处理器输出字段规范校验"
description: "依据数据字典（Review Processor Output Fields v7.2）校验评论处理器输出字段是否存在、类型正确、枚举取值合法，用于下游消费前确认结构化输出符合约定。"
version: "0.1.0"
tags:
  - "数据校验"
  - "schema校验"
  - "输出验证"
  - "评论处理"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "需要验证评论处理器输出结构"
  - "下游系统消费前做字段合规检查"
examples:
  - input: "输出含 is_sportswear=\"maybe\""
    output: "不合规：is_sportswear 取值 \"maybe\" 不在枚举 {\"yes\",\"no\"} 内"
    notes: "枚举校验示例"
---

# 评论处理器输出字段规范校验

依据数据字典（Review Processor Output Fields v7.2）校验评论处理器输出字段是否存在、类型正确、枚举取值合法，用于下游消费前确认结构化输出符合约定。

## Prompt

使用本技能时，先确认字段规范版本与待校验输出一致，再逐字段核对存在性、类型与枚举取值，最后输出通过/不合规字段清单。仅做规范校验，不修改或补全业务数据。

## Objective

确保评论处理器输出符合字段与枚举约定
## Applicable Signals

- 待校验输出声称遵循 Review Processor Output Fields v7.2
- 下游消费前需要字段合规确认

## Contraindications

- 字段规范未定义或版本不匹配时

## Intervention Moves

- 核对字段是否存在
- 核对字段类型
- 核对枚举取值合法性
- 汇总不合规字段清单

## Workflow Steps

- 确认字段规范版本与待校验输出一致
- 逐字段检查存在性：review_id、review、is_sportswear、is_apparel_product、brand、competitor_or_nike
- 检查类型：review_id 与 review 为 string，brand 为 string（规范化品牌名或 "N/A"）
- 检查枚举：is_sportswear 与 is_apparel_product 取 {"yes","no"}；competitor_or_nike 取 {"nike","competitor","n/a"}
- 汇总通过/不合规字段清单并交付

## Constraints

- 仅依据已定义的字段规范版本进行校验
- 不修改或补全业务数据，只报告合规结果

## Cautions

- 版本不匹配时不应套用本规范
- 枚举取值需严格匹配，注意大小写与 "N/A" 与 "n/a" 的差异

## Output Contract

- 字段合规检查结果：整体通过或不合规字段清单（含字段名与不合规原因）

## Example Therapist Responses

### Example 1

- Client/Input: 输出含 is_sportswear="maybe"
- Therapist/Output: 不合规：is_sportswear 取值 "maybe" 不在枚举 {"yes","no"} 内
- Notes: 枚举校验示例

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要验证评论处理器输出结构
- 下游系统消费前做字段合规检查

## Examples

### Example 1

Input:

  输出含 is_sportswear="maybe"

Output:

  不合规：is_sportswear 取值 "maybe" 不在枚举 {"yes","no"} 内

Notes:

  枚举校验示例
