---
id: "7b118a07-ff9b-54a5-b3a9-11d2e137c158"
name: "动作前置条件守卫"
description: "在生成车辆每tick动作请求时，对有条件动作（ENTER_EDGE、START_LOADING、START_UNLOADING、GO_OFFLINE、GO_ONLINE）校验其位置与状态前置条件；不满足则拒绝或修正该动作，仅保留合法动作请求。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "动作合法性"
  - "前置条件"
  - "守卫规则"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆请求进入边、装卸、上下线等有条件动作"
  - "需要判断动作在当前节点或状态是否允许"
examples:
  - input: "车辆位于非 HomeDepot 节点，请求 GO_OFFLINE"
    output: "拒绝 GO_OFFLINE，改为合法动作（如 WAIT）"
    notes: "GO_OFFLINE 需在 HomeDepot"
  - input: "车辆处于 OFFLINE 且位于 HomeDepot，请求 GO_ONLINE"
    output: "允许 GO_ONLINE，状态转为 IDLE_AT_NODE"
    notes: "满足前置条件"
---

# 动作前置条件守卫

在生成车辆每tick动作请求时，对有条件动作（ENTER_EDGE、START_LOADING、START_UNLOADING、GO_OFFLINE、GO_ONLINE）校验其位置与状态前置条件；不满足则拒绝或修正该动作，仅保留合法动作请求。

## Prompt

对每个非离线车辆拟发出的有条件动作，逐项核对前置条件：ENTER_EDGE 需车辆当前位于节点；START_LOADING 需车辆位于当前节点且目标货物在该节点；START_UNLOADING 需指定货物已在车上且其目的地或允许转运节点与当前节点匹配；GO_OFFLINE 需车辆位于其 HomeDepot；GO_ONLINE 需车辆处于 OFFLINE 且位于 HomeDepot。任一条件不满足则不得发出该动作，改为拒绝或替换为合法动作（如 WAIT）。注意动作在容量与冲突校验前仅为请求，本守卫只做前置条件过滤，不处理容量与冲突。

## Objective

阻止不满足位置或状态前置条件的非法动作请求
## Applicable Signals

- 车辆拟发出 ENTER_EDGE 且需确认是否在节点
- 车辆拟发出 START_LOADING 或 START_UNLOADING
- 车辆拟切换 GO_OFFLINE 或 GO_ONLINE
- 需判断动作在当前节点或状态是否允许

## Contraindications

- 动作本身无条件合法如 WAIT
- 已进入容量与冲突校验阶段

## Intervention Moves

- 识别动作类型及其前置条件
- 核对车辆当前位置与状态
- 对不满足条件的动作拒绝或替换为合法动作

## Workflow Steps

- 确定车辆当前所在节点与状态（在线/离线）
- 识别拟发出动作类型
- 按动作类型核对前置条件：ENTER_EDGE 需在节点；START_LOADING 需在节点且货物在该节点；START_UNLOADING 需货物在车上且目的地或允许转运节点匹配当前节点；GO_OFFLINE 需在 HomeDepot；GO_ONLINE 需 OFFLINE 且在 HomeDepot
- 对不满足条件的动作拒绝或修正为合法动作
- 输出仅含满足前置条件的动作请求

## Constraints

- 每个非离线车辆每tick至多选择一个动作
- 动作在容量与冲突校验前仅为请求，本守卫不替代该阶段

## Cautions

- 不要将前置条件校验与容量/冲突校验混淆
- GO_ONLINE 仅在车辆已处于 OFFLINE 且位于 HomeDepot 时允许

## Output Contract

- 非法动作被拒绝或修正，仅保留满足前置条件的动作请求。

## Example Therapist Responses

### Example 1

- Client/Input: 车辆位于非 HomeDepot 节点，请求 GO_OFFLINE
- Therapist/Output: 拒绝 GO_OFFLINE，改为合法动作（如 WAIT）
- Notes: GO_OFFLINE 需在 HomeDepot

### Example 2

- Client/Input: 车辆处于 OFFLINE 且位于 HomeDepot，请求 GO_ONLINE
- Therapist/Output: 允许 GO_ONLINE，状态转为 IDLE_AT_NODE
- Notes: 满足前置条件

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆请求进入边、装卸、上下线等有条件动作
- 需要判断动作在当前节点或状态是否允许

## Examples

### Example 1

Input:

  车辆位于非 HomeDepot 节点，请求 GO_OFFLINE

Output:

  拒绝 GO_OFFLINE，改为合法动作（如 WAIT）

Notes:

  GO_OFFLINE 需在 HomeDepot

### Example 2

Input:

  车辆处于 OFFLINE 且位于 HomeDepot，请求 GO_ONLINE

Output:

  允许 GO_ONLINE，状态转为 IDLE_AT_NODE

Notes:

  满足前置条件
