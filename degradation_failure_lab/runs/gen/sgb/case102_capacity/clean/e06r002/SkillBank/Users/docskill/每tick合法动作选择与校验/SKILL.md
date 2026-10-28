---
id: "37d5e779-abfa-5504-bc05-f91c8c869f35"
name: "每Tick合法动作选择与校验"
description: "为每个非离线车辆在每个tick生成唯一合法动作请求（WAIT/ENTER_EDGE/CONTINUE_TRAVEL/START_LOADING/START_UNLOADING/GO_OFFLINE/GO_ONLINE），并将动作视为请求交由容量与冲突校验阶段裁决。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "离散时间步"
  - "动作选择"
  - "合法性校验"
  - "车辆调度"
triggers:
  - "需要为车辆生成下一tick动作"
  - "需要判断某动作是否合法"
  - "需要枚举某车辆在当前状态下的可选动作"
examples:
  - input: "车辆在节点上，Status = IDLE_AT_NODE，位于 HomeDepot"
    output: "GO_OFFLINE（请求，待校验）"
    notes: "仅在 HomeDepot 且非离线时合法"
  - input: "车辆 Status = MOVING，位于某边上"
    output: "CONTINUE_TRAVEL（请求，待校验）"
    notes: "MOVING 状态唯一合法动作"
---

# 每Tick合法动作选择与校验

为每个非离线车辆在每个tick生成唯一合法动作请求（WAIT/ENTER_EDGE/CONTINUE_TRAVEL/START_LOADING/START_UNLOADING/GO_OFFLINE/GO_ONLINE），并将动作视为请求交由容量与冲突校验阶段裁决。

## Prompt

对每个非离线车辆，在每个tick只选择一个合法动作，并明确该动作是待校验的请求而非已生效结果。

执行要点：
1. 确认车辆状态：若 Status = MOVING（在边上），唯一合法动作为 CONTINUE_TRAVEL，不得装卸。
2. 若车辆在节点上，从合法动作集中选择一个：WAIT、ENTER_EDGE(edgeID)、START_LOADING(consignmentIDs)、START_UNLOADING(consignmentIDs)、GO_OFFLINE、GO_ONLINE。
3. 约束校验：GO_OFFLINE 仅在 HomeDepot 且当前非离线时合法；GO_ONLINE 仅在 HomeDepot 且当前为 OFFLINE 时合法；START_UNLOADING 仅对在车上且目的地或允许换装节点匹配当前节点的货物合法。
4. 每车每tick恰好一个动作，不得多选或省略。
5. 将动作标记为请求，交由容量与冲突校验阶段确认，不在此阶段判定生效。

## Objective

为每个车辆在每个tick生成唯一合法动作请求并交由校验阶段裁决
## Applicable Signals

- 需要为车辆生成下一tick动作
- 需要判断某动作是否合法
- 车辆状态为 IDLE_AT_NODE 或 MOVING 需确定动作

## Contraindications

- 车辆处于MOVING状态却请求装卸
- 需要跨多阶段整体调度协议
- 需要在此阶段直接裁决容量或冲突

## Intervention Moves

- 读取车辆当前状态与位置
- 按状态筛选合法动作集
- 为每车选择恰好一个动作
- 标注为待校验请求并移交容量与冲突校验

## Workflow Steps

- 确认车辆是否非离线；离线车辆不参与本tick动作选择
- 若 Status = MOVING，仅输出 CONTINUE_TRAVEL
- 若在节点上，依据状态与位置从合法动作集中选择一个动作
- 校验动作前置条件（HomeDepot、货物匹配等）
- 将动作标记为请求，移交容量与冲突校验阶段

## Constraints

- 每个非离线车辆每tick恰好选择一个动作
- MOVING 状态车辆唯一合法动作为 CONTINUE_TRAVEL
- GO_OFFLINE 仅在 HomeDepot 且非离线时合法
- GO_ONLINE 仅在 HomeDepot 且为 OFFLINE 时合法
- 动作在容量与冲突校验前仅为请求

## Cautions

- 不得将动作请求视为已生效结果
- 不得为同一车辆在同一tick生成多个动作
- 装卸动作需确认货物在车上且目的地或允许换装节点匹配当前节点

## Output Contract

- 每车辆每tick一个合法动作请求，标注为待校验，进入容量与冲突校验阶段

## Example Therapist Responses

### Example 1

- Client/Input: 车辆在节点上，Status = IDLE_AT_NODE，位于 HomeDepot
- Therapist/Output: GO_OFFLINE（请求，待校验）
- Notes: 仅在 HomeDepot 且非离线时合法

### Example 2

- Client/Input: 车辆 Status = MOVING，位于某边上
- Therapist/Output: CONTINUE_TRAVEL（请求，待校验）
- Notes: MOVING 状态唯一合法动作

## Triggers

- 需要为车辆生成下一tick动作
- 需要判断某动作是否合法
- 需要枚举某车辆在当前状态下的可选动作

## Examples

### Example 1

Input:

  车辆在节点上，Status = IDLE_AT_NODE，位于 HomeDepot

Output:

  GO_OFFLINE（请求，待校验）

Notes:

  仅在 HomeDepot 且非离线时合法

### Example 2

Input:

  车辆 Status = MOVING，位于某边上

Output:

  CONTINUE_TRAVEL（请求，待校验）

Notes:

  MOVING 状态唯一合法动作
