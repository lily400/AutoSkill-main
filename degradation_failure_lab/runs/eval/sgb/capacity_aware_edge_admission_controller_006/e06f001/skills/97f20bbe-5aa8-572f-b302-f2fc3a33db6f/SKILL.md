---
id: "97f20bbe-5aa8-572f-b302-f2fc3a33db6f"
name: "运输中车辆动作合法性约束"
description: "当车辆Status=MOVING（位于边上）时，禁止其开始装载或卸载，唯一合法动作为CONTINUE_TRAVEL；用于在动作生成阶段校验车辆动作合法性。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "动作合法性"
  - "状态约束"
  - "MOVING"
  - "CONTINUE_TRAVEL"
triggers:
  - "车辆状态为MOVING"
  - "校验车辆动作合法性"
  - "生成车辆每tick动作"
---

# 运输中车辆动作合法性约束

当车辆Status=MOVING（位于边上）时，禁止其开始装载或卸载，唯一合法动作为CONTINUE_TRAVEL；用于在动作生成阶段校验车辆动作合法性。

## Prompt

在生成或校验车辆动作时，先检查车辆状态。若Status=MOVING（车辆位于边上），则不得生成START_LOADING或START_UNLOADING动作，唯一合法动作为CONTINUE_TRAVEL；若车辆位于节点上，则不适用本规则，按常规动作枚举处理。

## Objective

防止运输中车辆执行非法装卸动作
## Applicable Signals

- 车辆Status=MOVING
- 车辆位于边上
- 需要对车辆动作做合法性校验

## Contraindications

- 车辆位于节点上且可执行装卸
- 车辆状态非MOVING

## Intervention Moves

- 检查车辆Status字段
- 若为MOVING则拒绝START_LOADING/START_UNLOADING
- 将唯一合法动作限定为CONTINUE_TRAVEL

## Workflow Steps

- 读取车辆当前Status
- 若Status=MOVING，则屏蔽START_LOADING与START_UNLOADING动作
- 仅允许CONTINUE_TRAVEL作为该车辆本tick动作
- 输出校验后的合法动作

## Constraints

- MOVING车辆不得开始装载或卸载
- MOVING车辆唯一合法动作为CONTINUE_TRAVEL

## Cautions

- 动作在容量与冲突检查阶段前仅为请求，本规则在动作生成阶段先行约束
- 仅对Status=MOVING的车辆生效，勿误用于节点上的车辆

## Output Contract

- MOVING车辆仅产生CONTINUE_TRAVEL动作，非法装卸动作被拒绝。

## Triggers

- 车辆状态为MOVING
- 校验车辆动作合法性
- 生成车辆每tick动作
