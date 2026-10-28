---
id: "07a1c597-7956-5d8e-aed6-d14736bd7484"
name: "产品目录JSON结构校验"
description: "对产品目录JSON数组执行结构与字段校验，确认每个对象含唯一sku_id、合法category枚举与非空silhouette_description；用于接收或清洗产品目录输入、进入后续匹配流程之前。"
version: "0.1.0"
tags:
  - "输入校验"
  - "结构校验"
  - "产品目录"
  - "JSON"
  - "合规守卫"
  - "未分类技能"
  - "profile:procedural_task_execution_operational_procedures::未分类技能"
triggers:
  - "收到产品目录JSON需进入后续匹配流程"
  - "需确认category取值合法"
  - "需确认sku_id唯一性与silhouette_description非空"
examples:
  - input: "产品目录JSON数组，其中某对象category为\"accessories\""
    output: "校验失败：category取值非法（应为tops/bottoms/outerwear）"
    notes: "枚举校验拦截"
  - input: "产品目录JSON数组，某对象silhouette_description为空字符串"
    output: "校验失败：silhouette_description为空"
    notes: "非空校验拦截"
---

# 产品目录JSON结构校验

对产品目录JSON数组执行结构与字段校验，确认每个对象含唯一sku_id、合法category枚举与非空silhouette_description；用于接收或清洗产品目录输入、进入后续匹配流程之前。

## Prompt

在执行任何产品目录匹配或分类任务前，先校验输入是否为JSON数组，且每个对象均含sku_id（字符串、唯一）、category（仅限"tops"、"bottoms"、"outerwear"）、silhouette_description（非空字符串）。逐项检查并记录缺失或非法字段；若校验不通过，标记失败并列出问题项，不进入后续流程。

## Objective

确保产品目录输入满足必需结构与字段约束，拦截无效数据
## Applicable Signals

- 产品目录JSON即将进入匹配或分类流程
- category字段取值需确认是否在允许枚举内
- sku_id或silhouette_description存在缺失或重复风险

## Contraindications

- 输入不是产品目录JSON
- 仅需语义相似度判断而无需结构校验

## Intervention Moves

- 确认输入为JSON数组
- 逐对象检查sku_id为字符串且唯一
- 检查category属于"tops"、"bottoms"、"outerwear"
- 检查silhouette_description为非空字符串
- 汇总缺失或非法字段并给出通过/失败结论

## Workflow Steps

- 确认输入为JSON数组，每个元素为对象
- 校验sku_id：存在、为字符串、在数组内唯一
- 校验category：存在且取值属于"tops"、"bottoms"、"outerwear"
- 校验silhouette_description：存在且为非空字符串
- 记录所有缺失或非法字段，输出通过或失败结论

## Constraints

- category仅允许"tops"、"bottoms"、"outerwear"三个取值
- sku_id必须唯一
- silhouette_description不得为空
- 校验不通过时不得进入后续匹配流程

## Cautions

- 仅做结构与字段校验，不承担语义相似度或情感分类判断
- 对部分缺失的输入应明确标记而非静默补全

## Output Contract

- 通过或标记失败的校验结果，列出缺失或非法字段

## Example Therapist Responses

### Example 1

- Client/Input: 产品目录JSON数组，其中某对象category为"accessories"
- Therapist/Output: 校验失败：category取值非法（应为tops/bottoms/outerwear）
- Notes: 枚举校验拦截

### Example 2

- Client/Input: 产品目录JSON数组，某对象silhouette_description为空字符串
- Therapist/Output: 校验失败：silhouette_description为空
- Notes: 非空校验拦截

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 收到产品目录JSON需进入后续匹配流程
- 需确认category取值合法
- 需确认sku_id唯一性与silhouette_description非空

## Examples

### Example 1

Input:

  产品目录JSON数组，其中某对象category为"accessories"

Output:

  校验失败：category取值非法（应为tops/bottoms/outerwear）

Notes:

  枚举校验拦截

### Example 2

Input:

  产品目录JSON数组，某对象silhouette_description为空字符串

Output:

  校验失败：silhouette_description为空

Notes:

  非空校验拦截
