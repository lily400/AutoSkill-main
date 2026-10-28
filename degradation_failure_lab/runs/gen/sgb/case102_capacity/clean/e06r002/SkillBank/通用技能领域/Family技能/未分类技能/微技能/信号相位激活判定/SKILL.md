---
id: "7c827cd0-f8c6-5eed-8530-349ad41c6fc5"
name: "信号相位激活判定"
description: "根据固定信号周期（CycleLength）与有序相位列表（各相位含 Duration 与 GreenEdges），计算给定 tick t 的激活相位及其允许放行的入边集合，用于信号化节点的放行判定。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号控制"
  - "固定周期相位轮转"
  - "相位激活"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "节点为信号化节点"
  - "需要判定当前 tick 哪些入边可放行"
  - "需要计算给定 tick 的激活相位"
---

# 信号相位激活判定

根据固定信号周期（CycleLength）与有序相位列表（各相位含 Duration 与 GreenEdges），计算给定 tick t 的激活相位及其允许放行的入边集合，用于信号化节点的放行判定。

## Prompt

当节点为信号化节点且需要判定当前 tick 哪些入边可放行时使用本技能。
步骤：
1. 确认该节点为信号化节点，且已定义 CycleLength 与有序相位列表（每相位含 Duration 与 GreenEdges）。
2. 计算 tick t 在周期内的位置：pos = t mod CycleLength。
3. 按相位顺序累加各相位 Duration，找到使累加和首次大于 pos 的相位，即为 tick t 的激活相位。
4. 输出该激活相位及其 GreenEdges 集合，作为本 tick 允许放行的入边。
若节点无信号控制，或信号周期/相位列表未定义，则不适用本技能。

## Objective

确定 tick t 的激活信号相位及其允许放行的入边集合
## Applicable Signals

- 节点为信号化节点
- 需要判定当前 tick 哪些入边可放行

## Contraindications

- 节点无信号控制
- 信号周期或相位列表未定义

## Intervention Moves

- 计算 tick t 在周期内的位置 pos = t mod CycleLength
- 按相位顺序累加 Duration，定位覆盖 pos 的相位
- 返回激活相位及其 GreenEdges 集合

## Workflow Steps

- 确认节点为信号化节点且已定义 CycleLength 与有序相位列表
- 计算 pos = t mod CycleLength
- 按相位顺序累加 Duration，找到使累加和首次大于 pos 的相位
- 输出该激活相位及其 GreenEdges 集合

## Constraints

- 相位按有序列表顺序轮转
- 每相位含 Duration 与 GreenEdges
- 周期长度为 CycleLength 个 tick

## Cautions

- 信号周期或相位列表缺失时不应推断相位

## Output Contract

- 返回 tick t 的激活相位及其 GreenEdges 集合（允许放行的入边集合）。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 节点为信号化节点
- 需要判定当前 tick 哪些入边可放行
- 需要计算给定 tick 的激活相位
