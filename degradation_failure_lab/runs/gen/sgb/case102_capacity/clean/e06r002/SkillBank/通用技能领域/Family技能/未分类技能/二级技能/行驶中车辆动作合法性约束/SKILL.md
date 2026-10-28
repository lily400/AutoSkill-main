---
id: "fb8197f0-8b04-5737-97fc-0668903cd571"
name: "行驶中车辆动作合法性约束"
description: "当车辆状态为 MOVING（位于某条边上）时，校验其唯一合法动作为 CONTINUE_TRAVEL，禁止开始装卸；用于每 tick 车辆动作合法性判定。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "动作合法性"
  - "MOVING"
  - "CONTINUE_TRAVEL"
  - "护栏"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "车辆状态为 MOVING 且需确定其可执行动作"
  - "校验控制器下发的动作是否合法"
examples:
  - input: "车辆状态为 MOVING，控制器下发 START_LOADING"
    output: "动作非法，拒绝；合法动作限定为 CONTINUE_TRAVEL"
    notes: "行驶中车辆不得开始装卸"
  - input: "车辆状态为 MOVING，候选动作为 CONTINUE_TRAVEL"
    output: "动作合法，允许执行 CONTINUE_TRAVEL"
---

# 行驶中车辆动作合法性约束

当车辆状态为 MOVING（位于某条边上）时，校验其唯一合法动作为 CONTINUE_TRAVEL，禁止开始装卸；用于每 tick 车辆动作合法性判定。

## Prompt

在确定或校验某车辆本 tick 的动作时，先检查其状态。若状态为 MOVING（车辆位于边上），则唯一合法动作为 CONTINUE_TRAVEL；不得开始装载或卸载。若控制器下发或候选动作包含装卸类动作，应判定为非法并拒绝，返回合法动作 CONTINUE_TRAVEL。仅处理动作合法性判定，不涉及容量计算或信号判定。

## Objective

防止行驶中车辆执行装卸等非法动作
## Applicable Signals

- 车辆 Status = MOVING
- 车辆位于某条边上
- 需要判定本 tick 车辆动作

## Contraindications

- 车辆处于非行驶状态
- 与车辆动作无关的容量或信号判定

## Intervention Moves

- 读取车辆状态
- 若为 MOVING 则限定动作为 CONTINUE_TRAVEL
- 拒绝任何装卸类动作并标记非法

## Workflow Steps

- 检查车辆当前状态是否为 MOVING
- 若为 MOVING，将合法动作限定为 CONTINUE_TRAVEL
- 若候选动作包含开始装载或卸载，判定为非法并拒绝
- 输出合法动作或非法标记

## Constraints

- MOVING 状态下不得开始装载或卸载
- 仅对动作合法性做判定，不扩展到容量或信号规则

## Cautions

- 仅在车辆确实位于边上（MOVING）时适用
- 非行驶状态车辆不适用本约束

## Output Contract

- 确认车辆动作被限定为 CONTINUE_TRAVEL，或将装卸类动作标记为非法。

## Example Therapist Responses

### Example 1

- Client/Input: 车辆状态为 MOVING，控制器下发 START_LOADING
- Therapist/Output: 动作非法，拒绝；合法动作限定为 CONTINUE_TRAVEL
- Notes: 行驶中车辆不得开始装卸

### Example 2

- Client/Input: 车辆状态为 MOVING，候选动作为 CONTINUE_TRAVEL
- Therapist/Output: 动作合法，允许执行 CONTINUE_TRAVEL

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 车辆状态为 MOVING 且需确定其可执行动作
- 校验控制器下发的动作是否合法

## Examples

### Example 1

Input:

  车辆状态为 MOVING，控制器下发 START_LOADING

Output:

  动作非法，拒绝；合法动作限定为 CONTINUE_TRAVEL

Notes:

  行驶中车辆不得开始装卸

### Example 2

Input:

  车辆状态为 MOVING，候选动作为 CONTINUE_TRAVEL

Output:

  动作合法，允许执行 CONTINUE_TRAVEL
