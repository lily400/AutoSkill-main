---
id: "d9f5202a-1d1b-5545-a2d2-49b57c524a65"
name: "进入边失败回退WAIT规则"
description: "当车辆请求ENTER_EDGE但未满足进入条件时，将其状态回退为在当前节点执行WAIT；用于处理进入边被拒绝后的状态回退判定。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "车辆状态回退"
  - "ENTER_EDGE"
  - "WAIT"
  - "规则判定"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆请求进入边但条件校验失败"
  - "车辆发起ENTER_EDGE请求后被拒绝"
---

# 进入边失败回退WAIT规则

当车辆请求ENTER_EDGE但未满足进入条件时，将其状态回退为在当前节点执行WAIT；用于处理进入边被拒绝后的状态回退判定。

## Prompt

在车辆移动更新阶段，检查车辆是否发起了ENTER_EDGE请求。若请求存在但未满足进入条件（如信号相位、容量、队列等校验失败），不要放行车辆，而是将车辆状态置为在当前节点WAIT。若进入条件全部满足或车辆未发起ENTER_EDGE请求，则不适用本规则。

## Objective

在进入边条件不满足时正确回退为WAIT状态
## Applicable Signals

- 车辆请求进入边但条件校验失败

## Contraindications

- 车辆进入条件全部满足
- 车辆未发起ENTER_EDGE请求

## Intervention Moves

- 确认车辆已发起ENTER_EDGE请求
- 确认进入条件校验失败
- 将车辆状态置为当前节点WAIT

## Workflow Steps

- 识别车辆是否发起ENTER_EDGE请求
- 校验进入条件是否满足
- 若校验失败，将车辆状态置为当前节点WAIT

## Constraints

- 仅在ENTER_EDGE请求存在且条件校验失败时触发
- 回退目标状态为当前节点的WAIT

## Cautions

- 不要将条件满足的车辆误判为WAIT
- 不要对未发起ENTER_EDGE请求的车辆应用本规则

## Output Contract

- 车辆状态置为当前节点WAIT

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆请求进入边但条件校验失败
- 车辆发起ENTER_EDGE请求后被拒绝
