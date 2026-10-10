---
id: "d6c5e020-d9fe-54ce-93dc-440420fd976a"
name: "qsv-select"
description: "qsv-select 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。"
version: "0.1.0"
tags:
  - "qsv-select"
  - "总导航"
  - "子技能地图"
  - "kind:parent"
  - "profile:qsv::qsv_select"
triggers:
  - "qsv-select"
  - "qsv-select 总导航"
  - "qsv-select 子技能地图"
---

# qsv-select

qsv-select 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。

## Prompt

## 适用场景
- 当当前问题明确属于或需要路由到 qsv-select 时，先使用本总技能决定子技能选择顺序。
- 本技能用于导航与组合，不替代子技能中的具体执行 SOP。

## 不适用/风险边界
- 不要把本技能当作具体干预脚本；真正执行时必须继续调用对应子技能。
- 如存在明显高风险或危机信号，应优先调用风险/危机类子技能。

## 总流程
1. 先判断当前问题是否适合进入该家族或领域的处理路径。
2. 再根据任务类型、阶段和风险边界选择最合适的子技能。
3. 调用对应子技能执行具体步骤、规则和输出格式。
4. 最后输出所选子技能、选择理由、执行顺序与风险提示。

## 子技能目录（一级技能目录）
- CSV 列选择与重排 ｜ 类型：列选择 ｜ 适用条件：使用 qsv select 的列选择器语法，按索引、名称、范围或正则选择、重排、反转、复制或删除 CSV 列，生成仅包含目标列集合与顺序的 CSV 输出。适用于需要精确控制输出列集合与顺序的场景。
- 敏感列排除 ｜ 类型：数据脱敏 ｜ 适用条件：使用 qsv select 的否定正则选择器在输出中排除匹配敏感模式的列（如 SSN、account_no、password），适用于数据脱敏或共享前的列裁剪。

## 选用规则（一级技能目录）
- 当问题命中“需要按索引或名称挑选列、需要重排或反转列顺序、需要复制或删除特定列、需要按正则匹配列名进行选择或排除”这类线索时，优先选择 CSV 列选择与重排。
- 当问题命中“输出将共享或发布、存在已知敏感列名模式、需要在数据变换阶段裁剪敏感列、qsv”这类线索时，优先选择 敏感列排除。

## 输出格式
- family_route:
  - family: qsv-select
  - selected_children: [子技能名称列表]
  - rationale: 说明为什么选择这些子技能
  - cautions: 风险边界与切换条件

## Files

- `references/children_manifest.json`
- `references/children_map.md`

## Triggers

- qsv-select
- qsv-select 总导航
- qsv-select 子技能地图
