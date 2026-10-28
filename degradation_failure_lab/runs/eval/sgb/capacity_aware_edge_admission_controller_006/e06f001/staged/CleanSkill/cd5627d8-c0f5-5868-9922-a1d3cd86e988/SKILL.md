---
id: "cd5627d8-c0f5-5868-9922-a1d3cd86e988"
name: "容量与冲突检查裁决"
description: "在移动承诺阶段之后，依据边容量、信号与优先级逐条裁决每个移动承诺是否被批准或拒绝，并输出逐条裁决结果。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "容量校验"
  - "冲突裁决"
  - "移动承诺"
triggers:
  - "车辆已提交进入某边的移动承诺"
  - "需要判定某个移动是否被允许"
  - "进入 Capacity & Conflict Check Phase"
examples:
  - input: "车辆已提交进入某边的承诺，该边容量已满"
    output: "该承诺裁决为拒绝"
    notes: "容量不足导致拒绝"
---

# 容量与冲突检查裁决

在移动承诺阶段之后，依据边容量、信号与优先级逐条裁决每个移动承诺是否被批准或拒绝，并输出逐条裁决结果。

## Prompt

在 Movement Commitment Phase 产生移动承诺后执行本技能：收集本 tick 的移动承诺集合，按 VehicleID 升序、再按 NodeID 升序确定处理顺序（除非规则另有优先级），对每条承诺检查目标边容量是否允许进入，检查信号与优先级约束，逐条记录该承诺的批准或拒绝结果。仅输出裁决结果，不执行移动、不推进剩余行程时间、不更新指标。

## Objective

依据容量、信号和优先级裁决移动承诺的批准或拒绝
## Applicable Signals

- 车辆已提交进入某边的承诺
- 需要判定移动是否被允许

## Contraindications

- 尚未产生移动承诺
- 仅做指标统计
- 处于 Incident Resolution 或 Movement Execution 等其他阶段

## Intervention Moves

- 读取当前边容量与占用情况
- 检查目标边信号状态
- 比较承诺之间的优先级
- 对每条承诺给出批准或拒绝结论

## Workflow Steps

- 收集本 tick 的移动承诺集合
- 按 VehicleID 升序、再按 NodeID 升序确定处理顺序（除非规则另有优先级）
- 对每条承诺检查目标边容量是否允许进入
- 检查信号与优先级约束
- 记录该承诺的批准或拒绝结果

## Constraints

- 仅在本阶段裁决，不执行移动或推进剩余行程时间
- 不更新交付延迟、行驶距离等指标
- 排序遵循 VehicleID 升序、再 NodeID 升序，除非规则指定不同优先级

## Cautions

- 部分承诺可能因容量、信号或优先级被拒绝，需逐条记录而非整体判定

## Output Contract

- 每个移动承诺的批准/拒绝结果列表

## Example Therapist Responses

### Example 1

- Client/Input: 车辆已提交进入某边的承诺，该边容量已满
- Therapist/Output: 该承诺裁决为拒绝
- Notes: 容量不足导致拒绝

## Triggers

- 车辆已提交进入某边的移动承诺
- 需要判定某个移动是否被允许
- 进入 Capacity & Conflict Check Phase

## Examples

### Example 1

Input:

  车辆已提交进入某边的承诺，该边容量已满

Output:

  该承诺裁决为拒绝

Notes:

  容量不足导致拒绝
