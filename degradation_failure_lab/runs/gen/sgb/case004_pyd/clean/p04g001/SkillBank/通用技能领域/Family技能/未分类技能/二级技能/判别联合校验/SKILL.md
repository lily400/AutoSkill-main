---
id: "9fe92bc9-6546-50f8-bcae-efb34ffbb5f2"
name: "判别联合校验"
description: "使用判别字段（含 str 判别器、可调用 Discriminator 及嵌套判别联合）将联合类型路由到唯一成员进行校验；适用于成员可由判别字段明确区分的场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "union_validation"
  - "discriminated_union"
  - "routing"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "联合成员可由一个判别字段唯一区分"
  - "需要支持 str 判别器"
  - "需要使用可调用 Discriminator"
  - "需要处理嵌套判别联合"
---

# 判别联合校验

使用判别字段（含 str 判别器、可调用 Discriminator 及嵌套判别联合）将联合类型路由到唯一成员进行校验；适用于成员可由判别字段明确区分的场景。

## Prompt

当联合类型的成员可由一个判别字段唯一区分时，使用本技能：先确认判别字段存在且取值能唯一映射到某个成员，再按判别值选中唯一成员并执行该成员的校验，返回其校验结果。若判别值无法匹配任何成员或成员间无可靠判别字段，则不要使用本技能，改用顺序或评分选择策略。

## Objective

依据判别字段将输入路由到唯一联合成员并校验
## Applicable Signals

- 联合成员可由一个判别字段唯一区分
- 需要支持 str 判别器、可调用 Discriminator 或嵌套判别联合

## Contraindications

- 成员间无可靠判别字段
- 仅需按顺序或评分选择成员

## Intervention Moves

- 识别并确认判别字段
- 按判别值路由到唯一成员
- 对选中成员执行校验并返回结果

## Workflow Steps

- 确认联合成员可由一个判别字段唯一区分。
- 确定判别器形式：str 判别器、可调用 Discriminator 或嵌套判别联合。
- 读取判别字段取值并映射到唯一成员。
- 对选中成员执行校验。
- 返回该成员的校验结果。

## Constraints

- 仅在成员可由判别字段唯一区分时使用
- 判别值必须能唯一映射到某个成员

## Cautions

- 判别值无法匹配任何成员时应报错而非回退到顺序选择
- 嵌套判别联合需逐层解析判别字段

## Output Contract

- 按判别值选中唯一成员并返回其校验结果

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 联合成员可由一个判别字段唯一区分
- 需要支持 str 判别器
- 需要使用可调用 Discriminator
- 需要处理嵌套判别联合
