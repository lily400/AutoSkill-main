---
id: "8cd10359-1f17-575a-aaf7-6dbcd9da0c79"
name: "Feed 导出设置项参考"
description: "提供 Scrapy feed 导出相关设置项的查阅参考，列出各设置项名称及其用途，用于确认某个导出设置项的名称或作用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed"
  - "settings"
  - "reference"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要确认某个导出设置项的名称或作用"
  - "查阅 feed 导出配置项清单"
examples:
  - input: "FEEDS 设置项是做什么的？"
    output: "FEEDS 是配置 feed 导出的必填设置项，默认值为 {}。"
---

# Feed 导出设置项参考

提供 Scrapy feed 导出相关设置项的查阅参考，列出各设置项名称及其用途，用于确认某个导出设置项的名称或作用。

## Prompt

当调用方需要确认某个 feed 导出设置项的名称或作用时，依据本参考列出相关设置项并说明其用途。仅提供设置项层面的参考信息，不执行端到端配置流程。

## Objective

提供 feed 导出相关设置项的查阅参考
## Applicable Signals

- 调用方询问某个导出设置项的名称或含义
- 需要一份 feed 导出设置项清单

## Contraindications

- 需要端到端配置流程而非单项说明

## Intervention Moves

- 定位到具体设置项
- 说明该设置项的用途

## Workflow Steps

- 确认调用方要查询的设置项或查询意图
- 在设置项清单中定位对应条目
- 返回设置项名称及其用途说明

## Constraints

- 仅提供设置项层面的参考信息
- 不执行配置动作或端到端配置流程

## Cautions

- FEEDS 为必填设置项，其余为可选配置项

## Output Contract

- 可定位到具体设置项及其用途的参考信息

## Example Therapist Responses

### Example 1

- Client/Input: FEEDS 设置项是做什么的？
- Therapist/Output: FEEDS 是配置 feed 导出的必填设置项，默认值为 {}。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要确认某个导出设置项的名称或作用
- 查阅 feed 导出配置项清单

## Examples

### Example 1

Input:

  FEEDS 设置项是做什么的？

Output:

  FEEDS 是配置 feed 导出的必填设置项，默认值为 {}。
