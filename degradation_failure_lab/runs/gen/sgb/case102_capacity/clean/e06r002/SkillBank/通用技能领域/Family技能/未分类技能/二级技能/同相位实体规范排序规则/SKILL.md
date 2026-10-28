---
id: "2a0027f2-f608-579c-82cb-dd9b628d283a"
name: "同相位实体规范排序规则"
description: "当同一相位内需要确定多个实体的处理顺序且规则未指定其他优先级时，按VehicleID升序、再按NodeID升序的规范顺序处理，以消除顺序歧义并保证仿真确定性。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "确定性"
  - "排序约束"
  - "每tick更新"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "同相位内多个实体需排序处理"
  - "规则未指定其他优先级"
  - "需要消除实体处理顺序歧义"
---

# 同相位实体规范排序规则

当同一相位内需要确定多个实体的处理顺序且规则未指定其他优先级时，按VehicleID升序、再按NodeID升序的规范顺序处理，以消除顺序歧义并保证仿真确定性。

## Prompt

在每tick更新中，若同一相位内需要对实体排序处理，先检查是否有规则明确指定了不同优先级；若无，则按VehicleID升序排序，VehicleID相同时再按NodeID升序排序，输出确定性的实体处理顺序列表。

## Objective

消除同相位内实体处理顺序的歧义
## Applicable Signals

- 同相位内多个实体需排序处理
- 规则未指定其他优先级

## Contraindications

- 规则已明确指定不同优先级
- 跨相位处理

## Intervention Moves

- 检查是否存在规则明确指定的不同优先级
- 若无其他优先级，按VehicleID升序排序
- VehicleID相同时按NodeID升序排序
- 输出确定性实体处理顺序列表

## Workflow Steps

- 确认当前处理处于同一相位内且需要实体排序
- 检查是否有规则明确指定了不同优先级
- 若无，按VehicleID升序排序
- VehicleID相同时按NodeID升序排序
- 输出确定性的实体处理顺序列表

## Constraints

- 仅在规则未指定其他优先级时应用规范排序
- 排序仅限同一相位内，不跨相位

## Cautions

- 若规则已明确指定不同优先级，应遵循该优先级而非规范排序

## Output Contract

- 确定性的实体处理顺序列表

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 同相位内多个实体需排序处理
- 规则未指定其他优先级
- 需要消除实体处理顺序歧义
