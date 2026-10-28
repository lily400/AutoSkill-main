---
id: "b509a4af-9652-5849-a3d7-68054c38b3c1"
name: "评论分类CSV输出校验"
description: "在评论分类结果交付给编排器或下游分析前，对CSV产出执行格式、列完整性、分类取值合法性与最小行数校验；校验通过则放行，不合格则向编排器返回明确错误说明。"
version: "0.1.0"
tags:
  - "CSV校验"
  - "输出合规"
  - "交付前检查"
  - "数据质量"
triggers:
  - "分类结果即将交付给编排器或下游分析"
  - "需要确认CSV可解析且列与取值合法"
  - "需要确认样本量是否满足下游分析最低要求"
examples:
  - input: "分类结果CSV，含全部必需列，分类取值合法，共25行"
    output: "校验通过，放行交付"
    notes: "格式、列、取值、行数四项均满足"
  - input: "分类结果CSV，is_sportswear列出现\"unknown\"取值"
    output: "校验失败，向编排器返回错误：is_sportswear取值非法"
    notes: "取值不在允许集合内即判不合格"
---

# 评论分类CSV输出校验

在评论分类结果交付给编排器或下游分析前，对CSV产出执行格式、列完整性、分类取值合法性与最小行数校验；校验通过则放行，不合格则向编排器返回明确错误说明。

## Prompt

在评论分类结果即将交付时执行本校验：先确认CSV可被解析，再核对必需列是否齐全，然后逐列检查分类取值是否落在允许集合内，最后确认行数达到最小样本量要求。任一检查失败即判定为不合格，并向编排器返回具体失败原因，不得放行。

## Objective

保证下游分析收到的评论分类CSV结构合法、取值合规、样本量充足
## Applicable Signals

- 分类结果已生成并准备交付
- 产出为CSV格式且含分类字段
- 下游分析依赖分类字段取值

## Contraindications

- 输入尚未完成分类
- 仅需生成原始评论列表且无需分类字段

## Intervention Moves

- 解析CSV确认格式有效
- 核对必需列是否全部存在
- 逐列校验分类取值是否在允许集合内
- 统计行数并确认达到最小样本量
- 不合格时向编排器返回明确错误说明

## Workflow Steps

- 尝试解析CSV，确认格式有效可解析
- 核对必需列齐全：review_id、review、is_sportswear、is_apparel_product、brand、competitor_or_nike
- 校验is_sportswear取值仅为yes或no
- 校验is_apparel_product取值仅为yes或no
- 校验competitor_or_nike取值仅为nike、competitor或n/a
- 统计行数，确认至少20行
- 全部通过则放行交付；任一失败则向编排器返回具体错误说明

## Constraints

- 分类列取值必须严格落在允许集合内，不接受近似或空值
- 行数下限为20行，低于下限视为不合格
- 校验不通过时不得将结果交付下游

## Cautions

- 校验失败时应指明具体失败项（格式、缺列、非法取值或行数不足），便于上游修正
- 不得为通过校验而擅自修改或补造分类数据

## Output Contract

- 通过校验的CSV，或向编排器返回的明确错误说明（指明失败的具体校验项）

## Example Therapist Responses

### Example 1

- Client/Input: 分类结果CSV，含全部必需列，分类取值合法，共25行
- Therapist/Output: 校验通过，放行交付
- Notes: 格式、列、取值、行数四项均满足

### Example 2

- Client/Input: 分类结果CSV，is_sportswear列出现"unknown"取值
- Therapist/Output: 校验失败，向编排器返回错误：is_sportswear取值非法
- Notes: 取值不在允许集合内即判不合格

## Triggers

- 分类结果即将交付给编排器或下游分析
- 需要确认CSV可解析且列与取值合法
- 需要确认样本量是否满足下游分析最低要求

## Examples

### Example 1

Input:

  分类结果CSV，含全部必需列，分类取值合法，共25行

Output:

  校验通过，放行交付

Notes:

  格式、列、取值、行数四项均满足

### Example 2

Input:

  分类结果CSV，is_sportswear列出现"unknown"取值

Output:

  校验失败，向编排器返回错误：is_sportswear取值非法

Notes:

  取值不在允许集合内即判不合格
