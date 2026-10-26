---
id: "7505e0c3-79f4-53b0-821e-5bd21936d8dd"
name: "通用技能领域"
description: "通用技能领域 的领域总导航技能：负责进入对应 family 的总路由。"
version: "0.1.0"
tags:
  - "通用技能领域"
  - "kind:domain_root"
  - "profile:brand_reputation_management::未分类技能"
triggers:
  - "通用技能领域"
  - "通用技能领域 总导航"
---

# 通用技能领域

通用技能领域 的领域总导航技能：负责进入对应 family 的总路由。

## Prompt

## Family目录
- [未分类技能](通用技能领域/Family技能/未分类技能/总技能/SKILL.md) ｜ 已同步技能数：2

## 选用规则（各 Family）
- 优先根据文档中明确的方法学术语、章节主题和任务目标进入对应 family。
- 当同一文档未显式指定 family 时，AutoSkill4Doc 会在配置的 family_candidates 中做受约束分类。
- 进入 family 后，再由 family 总技能继续选择一级、二级和微技能。

## 输出格式
- domain_route:
  - domain: 通用技能领域
  - family: 选中的 family 名称
  - rationale: 说明为什么选择该 family

## Files

- `references/domain_manifest.json`

## Triggers

- 通用技能领域
- 通用技能领域 总导航
