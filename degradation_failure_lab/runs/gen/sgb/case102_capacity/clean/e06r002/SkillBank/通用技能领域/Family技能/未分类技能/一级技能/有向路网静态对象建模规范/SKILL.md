---
id: "ebbc3a65-a1e0-5ce8-8232-82a9945bd90c"
name: "有向路网静态对象建模规范"
description: "按规范定义或校验交通仿真中的静态路网对象（节点、边、车辆、货物）的必填字段与取值约束，用于构建或检查仿真初始数据结构。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "路网建模"
  - "数据结构规范"
  - "有向图"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要定义或校验节点与边的字段"
  - "需要确认对象类型与属性约束"
  - "构建仿真初始路网数据结构"
---

# 有向路网静态对象建模规范

按规范定义或校验交通仿真中的静态路网对象（节点、边、车辆、货物）的必填字段与取值约束，用于构建或检查仿真初始数据结构。

## Prompt

依据本规范逐类定义或校验仿真对象：先确认对象类型（节点、边、车辆、货物），再为每个对象补齐必填字段并检查取值约束。路网为有向图，每条边由有序节点对 (from_node, to_node) 表示；双向道路应拆分为两条独立的有向边。若遇到规范未覆盖的情形，标记为未定义，不要自行臆造规则。

## Objective

按规范定义节点、边、车辆、货物的必填字段与取值约束
## Applicable Signals

- 需要定义或校验节点与边的字段
- 需要确认对象类型与属性约束
- 需要建立有向图形式的路网结构

## Contraindications

- 需要执行逐tick更新逻辑
- 需要处理信号或事故动态行为

## Intervention Moves

- 识别四类主要对象：节点、边、车辆、货物
- 为节点补齐 NodeID、NodeType 及停车位与队列属性
- 为边补齐 EdgeID、FromNode/ToNode、长度、基础通行时间、车道数、每车道容量、道路等级、下游信号类型
- 将双向道路拆分为两条独立有向边
- 对规范未覆盖情形标记为未定义

## Workflow Steps

- 确认待建模或校验的对象类型（节点、边、车辆、货物）
- 按有向图结构确定每条边的有序节点对 (from_node, to_node)
- 为节点填写唯一标识 NodeID、NodeType（INTERSECTION/DEPOT/CUSTOMER/HUB）、停车位与入边队列
- 为边填写唯一标识 EdgeID、FromNode、ToNode、长度、BaseTravelTime、LaneCount、CapacityPerLane、RoadClass（LOCAL/ARTERIAL/RING）、SignalType（SIGNALIZED/UNSIGNALIZED）
- 检查双向道路是否已拆分为两条独立有向边
- 对规范未覆盖的情形标记为未定义，不自行补充规则

## Constraints

- 所有行为必须遵循规范文档中的规则
- 路网为有向图，每条边为有序节点对
- LaneCount 为正整数
- NodeType 取值限于 INTERSECTION、DEPOT、CUSTOMER、HUB
- RoadClass 取值限于 LOCAL、ARTERIAL、RING
- SignalType 取值限于 SIGNALIZED、UNSIGNALIZED

## Cautions

- 规范未覆盖的情形视为未定义，需等待补充规则，不得臆造
- 本规范仅覆盖静态数据结构，不涉及动态更新与冲突处理

## Output Contract

- 符合字段与取值约束的路网对象定义，包含节点、边、车辆、货物的完整属性，且未覆盖情形被明确标记为未定义。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要定义或校验节点与边的字段
- 需要确认对象类型与属性约束
- 构建仿真初始路网数据结构
