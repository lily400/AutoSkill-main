---
id: "2fcf2c8c-ee2d-5471-a738-db6f6386065f"
name: "未分类技能"
description: "未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。"
version: "0.1.0"
tags:
  - "未分类技能"
  - "总导航"
  - "子技能地图"
  - "kind:parent"
  - "profile:default::未分类技能"
triggers:
  - "未分类技能"
  - "未分类技能 总导航"
  - "未分类技能 子技能地图"
---

# 未分类技能

未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。

## Prompt

## 适用场景
- 当当前问题明确属于或需要路由到 未分类技能 时，先使用本总技能决定子技能选择顺序。
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
- CSV Duplicate Row Removal ｜ 类型：file_transformation ｜ 适用条件：Reads a CSV file, removes exact duplicate rows based on all columns, and writes the deduplicated data to a new file while preserving the original.

## 选用规则（一级技能目录）
- 当问题命中“user needs to clean CSV data、input has suspected duplicate rows、original file must remain unmodified、csv”这类线索时，优先选择 CSV Duplicate Row Removal。

## 输出格式
- family_route:
  - family: 未分类技能
  - selected_children: [子技能名称列表]
  - rationale: 说明为什么选择这些子技能
  - cautions: 风险边界与切换条件

## Files

- `references/children_manifest.json`
- `references/children_map.md`

## Triggers

- 未分类技能
- 未分类技能 总导航
- 未分类技能 子技能地图
