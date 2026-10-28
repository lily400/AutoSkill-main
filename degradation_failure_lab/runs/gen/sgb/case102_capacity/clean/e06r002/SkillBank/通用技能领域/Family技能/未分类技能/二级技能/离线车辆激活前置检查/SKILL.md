---
id: "cd7b1dd8-3432-5442-a015-5feff7370c87"
name: "离线车辆激活前置检查"
description: "在执行移动或货物处理前，检查目标车辆是否处于 OFFLINE 状态；离线车辆须先被场景或控制器显式激活才可参与运行。用于每步更新前对目标车辆做状态守卫。"
version: "0.1.0"
tags:
  - "车辆状态守卫"
  - "状态前置校验"
  - "交通仿真规则"
  - "OFFLINE"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "准备对某车辆执行移动或装卸动作"
  - "控制器考虑调度某车辆"
examples:
  - input: "控制器计划调度某车辆执行移动"
    output: "检测到该车辆为 OFFLINE，阻止移动并触发显式激活流程"
    notes: "激活后方可继续原定动作"
---

# 离线车辆激活前置检查

在执行移动或货物处理前，检查目标车辆是否处于 OFFLINE 状态；离线车辆须先被场景或控制器显式激活才可参与运行。用于每步更新前对目标车辆做状态守卫。

## Prompt

在准备对某车辆执行移动或装卸动作前，先读取该车辆当前状态。若状态为 OFFLINE，则不得执行移动或货物处理，须先由场景或控制器显式激活该车辆；若车辆已处于激活运行状态，则按正常流程继续。

## Objective

避免对未激活车辆执行移动或装卸操作
## Applicable Signals

- 目标车辆即将被调度或执行动作
- 车辆状态字段待确认

## Contraindications

- 车辆已处于激活运行状态

## Intervention Moves

- 读取车辆当前状态
- 若为 OFFLINE 则阻止移动与装卸
- 触发显式激活流程后再放行

## Workflow Steps

- 识别即将被操作的目标车辆
- 读取该车辆当前状态
- 若状态为 OFFLINE，则阻止移动与货物处理，并触发显式激活流程
- 确认车辆已激活后，再执行原定移动或装卸动作

## Constraints

- OFFLINE 车辆不得移动
- OFFLINE 车辆不得处理货物
- 仅场景或控制器的显式激活可使车辆恢复运行

## Cautions

- 不得将未激活车辆视为可调度资源
- 激活须为显式决策，不可隐式假定

## Output Contract

- 确认车辆可操作或触发显式激活流程

## Example Therapist Responses

### Example 1

- Client/Input: 控制器计划调度某车辆执行移动
- Therapist/Output: 检测到该车辆为 OFFLINE，阻止移动并触发显式激活流程
- Notes: 激活后方可继续原定动作

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 准备对某车辆执行移动或装卸动作
- 控制器考虑调度某车辆

## Examples

### Example 1

Input:

  控制器计划调度某车辆执行移动

Output:

  检测到该车辆为 OFFLINE，阻止移动并触发显式激活流程

Notes:

  激活后方可继续原定动作
