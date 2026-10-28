---
id: "b6e41188-61e5-5ffb-a538-7007fe703ade"
name: "阶段内实体规范排序规则"
description: "当某一仿真阶段内需要确定多个实体的处理先后顺序时，按 VehicleID 升序、再按 NodeID 升序生成确定性处理序列，除非规则已明确指定其他优先级。用于消除阶段内处理顺序歧义。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "实体排序"
  - "规范键排序"
  - "阶段内处理"
  - "确定性"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "同一阶段内多个实体需确定处理先后"
  - "规则未指定其他优先级"
  - "需要消除阶段内处理顺序歧义"
---

# 阶段内实体规范排序规则

当某一仿真阶段内需要确定多个实体的处理先后顺序时，按 VehicleID 升序、再按 NodeID 升序生成确定性处理序列，除非规则已明确指定其他优先级。用于消除阶段内处理顺序歧义。

## Prompt

在单个仿真阶段内需要确定实体处理顺序时，先检查该阶段规则是否已明确指定优先级；若未指定，则按 VehicleID 升序排序，VehicleID 相同时再按 NodeID 升序排序，输出确定性的实体处理序列。不要用本规则编排跨阶段流程。

## Objective

在单个阶段内以确定性顺序处理实体，避免顺序歧义
## Applicable Signals

- 同一阶段内多个实体需确定处理先后
- 规则未指定其他优先级

## Contraindications

- 规则已明确指定不同优先级
- 跨阶段流程编排

## Intervention Moves

- 检查该阶段是否已有明确优先级规则
- 若无，则按 VehicleID 升序排序
- VehicleID 相同时按 NodeID 升序排序
- 输出确定性处理序列

## Workflow Steps

- 确认当前处于单个阶段内且存在多实体处理顺序需求
- 检查该阶段规则是否已指定优先级；若已指定则遵循该优先级
- 若未指定，按 VehicleID 升序排序
- VehicleID 相同时按 NodeID 升序排序
- 输出最终确定性处理序列

## Constraints

- 仅在单个阶段内应用
- 不得覆盖规则已明确指定的优先级

## Cautions

- 若规则另有优先级，本规范排序不适用
- 不要将本规则用于跨阶段流程编排

## Output Contract

- 按 VehicleID 再 NodeID 升序排列的实体处理序列

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 同一阶段内多个实体需确定处理先后
- 规则未指定其他优先级
- 需要消除阶段内处理顺序歧义
