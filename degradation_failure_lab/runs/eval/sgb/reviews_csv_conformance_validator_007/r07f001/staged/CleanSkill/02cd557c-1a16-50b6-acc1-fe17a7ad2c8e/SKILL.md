---
id: "02cd557c-1a16-50b6-acc1-fe17a7ad2c8e"
name: "输入文件校验与中止规则"
description: "在开始分析前校验产品目录 JSON 与评论 CSV 的结构与取值格式；任一硬性约束不满足即中止并请求修正文件，用于多代理评审分析流程的入口把关。"
version: "0.1.0"
tags:
  - "输入校验"
  - "数据契约"
  - "中止守卫"
  - "前置检查"
triggers:
  - "收到产品目录或评论文件准备开始分析"
  - "上游交付物格式或取值可疑"
  - "多代理评审分析流程入口把关"
examples:
  - input: "评论 CSV 中 is_sportswear 出现 \"Yes\"（大写），且缺少 competitor_or_nike 列"
    output: "中止：需修正字段 is_sportswear（须小写）、缺失列 competitor_or_nike；请提供修正后文件"
    notes: "格式与结构违规均触发中止"
  - input: "产品目录 JSON 为数组但仅 49 个 SKU"
    output: "中止：SKU 数量为 49，要求恰好 50 个唯一 SKU；请补齐后重交"
    notes: "数量不符属硬性约束违规"
---

# 输入文件校验与中止规则

在开始分析前校验产品目录 JSON 与评论 CSV 的结构与取值格式；任一硬性约束不满足即中止并请求修正文件，用于多代理评审分析流程的入口把关。

## Prompt

作为分析前置守卫，先校验输入文件再放行下游分析。
1) 校验产品目录 JSON：必须为数组，恰好 50 个唯一 SKU；每个条目须含 sku_id（字符串）、category（取值 tops|bottoms|outerwear）、silhouette_description（非空字符串）。
2) 校验评论 CSV：必须包含列 review_id, review, is_sportswear, is_apparel_product, brand, competitor_or_nike；分类取值必须严格小写格式。
3) 任一硬性约束不满足：立即中止，不进入分析，输出中止状态并列出需修正的字段。
4) 全部通过：放行并说明校验通过。
5) 若过滤后 Nike 或竞品评论少于 10 条，不中止，但在状态中标注低量条件后继续。

## Objective

阻止不合格输入进入下游分析，保证数据契约合规
## Applicable Signals

- 产品目录 JSON 或评论 CSV 刚交付待分析
- 字段缺失、取值大小写异常或数量不符等可疑迹象

## Contraindications

- 输入已通过校验且无需复核
- 仅需做语义分析而非数据把关

## Intervention Moves

- 逐项核对产品目录 JSON 的结构与字段约束
- 核对评论 CSV 的必需列与分类取值小写格式
- 发现违规即中止并列出待修正字段
- 低量评论时标注状态而非中止

## Workflow Steps

- 校验产品目录 JSON：数组、恰好 50 个唯一 SKU、sku_id 为字符串、category 属于 tops|bottoms|outerwear、silhouette_description 非空
- 校验评论 CSV：包含 review_id, review, is_sportswear, is_apparel_product, brand, competitor_or_nike 列
- 校验分类取值严格小写
- 任一硬性约束不满足则中止并请求修正文件，列出需修正字段
- 全部通过则放行；若 Nike 或竞品评论少于 10 条，标注低量条件后继续

## Constraints

- 硬性约束不满足必须中止，不得带病进入分析
- 分类取值必须严格小写
- 产品目录必须恰好 50 个唯一 SKU
- 低量评论不构成中止条件，仅需状态标注

## Cautions

- 大小写不一致（如 Yes）视为格式违规
- 缺失列（如 competitor_or_nike）视为结构违规
- 不得因上游口头催促而跳过校验

## Output Contract

- 校验通过放行，或输出中止状态并列出需修正的字段

## Example Therapist Responses

### Example 1

- Client/Input: 评论 CSV 中 is_sportswear 出现 "Yes"（大写），且缺少 competitor_or_nike 列
- Therapist/Output: 中止：需修正字段 is_sportswear（须小写）、缺失列 competitor_or_nike；请提供修正后文件
- Notes: 格式与结构违规均触发中止

### Example 2

- Client/Input: 产品目录 JSON 为数组但仅 49 个 SKU
- Therapist/Output: 中止：SKU 数量为 49，要求恰好 50 个唯一 SKU；请补齐后重交
- Notes: 数量不符属硬性约束违规

## Triggers

- 收到产品目录或评论文件准备开始分析
- 上游交付物格式或取值可疑
- 多代理评审分析流程入口把关

## Examples

### Example 1

Input:

  评论 CSV 中 is_sportswear 出现 "Yes"（大写），且缺少 competitor_or_nike 列

Output:

  中止：需修正字段 is_sportswear（须小写）、缺失列 competitor_or_nike；请提供修正后文件

Notes:

  格式与结构违规均触发中止

### Example 2

Input:

  产品目录 JSON 为数组但仅 49 个 SKU

Output:

  中止：SKU 数量为 49，要求恰好 50 个唯一 SKU；请补齐后重交

Notes:

  数量不符属硬性约束违规
