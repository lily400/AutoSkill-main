---
id: "1d99d4c7-ebb1-59e6-9050-779cd4dc28b3"
name: "装卸期间车辆锁定约束"
description: "当车辆处于 LOADING 或 UNLOADING 状态且存在进行中的装卸作业时，判定该车辆本 tick 的合法动作：拒绝移动或启动新作业请求，保持装卸状态直至作业完成。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "状态合法性"
  - "装卸锁定"
  - "合法动作校验"
  - "动作合法性"
  - "状态锁定"
  - "装卸作业"
triggers:
  - "车辆状态为 LOADING 或 UNLOADING"
  - "需要判定该车辆本 tick 可执行的动作"
  - "收到针对装卸中车辆的移动或启动新作业请求"
  - "生成或校验该车辆本 tick 动作"
  - "检查装卸作业进行中的状态一致性"
examples:
  - input: "车辆状态为 LOADING，收到本 tick 移动请求"
    output: "拒绝移动请求，车辆保持 LOADING 状态"
    notes: "装卸作业进行中禁止移动"
  - input: "车辆状态为 UNLOADING，收到启动新作业请求"
    output: "拒绝启动新作业请求，车辆保持 UNLOADING 状态"
    notes: "装卸作业进行中禁止启动另一作业"
  - input: "车辆 Status=LOADING，作业 WorkUnits=3，本 tick 请求 MOVE。"
    output: "拒绝 MOVE，本 tick 合法动作仅为无操作，状态保持 LOADING。"
    notes: "作业未完成期间持续锁定。"
---

# 装卸期间车辆锁定约束

当车辆处于 LOADING 或 UNLOADING 状态且存在进行中的装卸作业时，判定该车辆本 tick 的合法动作：拒绝移动或启动新作业请求，保持装卸状态直至作业完成。

## Prompt

在判定某车辆本 tick 的合法动作前，先检查其状态。若状态为 LOADING 或 UNLOADING 且存在进行中的装卸作业，则拒绝任何移动或启动新作业的请求，车辆保持装卸状态，仅允许装卸作业按 HandlingRate 继续推进。若车辆无进行中的装卸作业，则不适用本约束。

## Objective

防止装卸进行中的车辆被非法移动或重复启动作业
## Applicable Signals

- 车辆状态为 LOADING
- 车辆状态为 UNLOADING
- 车辆存在进行中的装卸作业
- 车辆 Status 为 LOADING
- 车辆 Status 为 UNLOADING
- 存在未完成的装卸作业（WorkUnits > 0）

## Contraindications

- 车辆无进行中的装卸作业
- 车辆状态不是 LOADING 或 UNLOADING
- 车辆处于空闲或移动状态
- 装卸作业已在本 tick 结束时完成（WorkUnits 降至 0 或以下）

## Intervention Moves

- 检查车辆当前状态
- 若处于装卸中则拒绝移动请求
- 若处于装卸中则拒绝启动新作业请求
- 保持车辆装卸状态直至作业完成
- 读取车辆当前 Status
- 若处于装卸中，将本 tick 合法动作限制为无操作
- 拒绝移动或启动新作业的请求
- 保持作业与状态不变直至作业完成

## Workflow Steps

- 读取车辆当前状态
- 判断状态是否为 LOADING 或 UNLOADING
- 若为装卸中，拒绝任何移动或启动新作业的请求
- 保持车辆状态不变，仅允许装卸作业按 HandlingRate 推进
- 若作业 WorkUnits 降至 0 或以下，在当 tick 结束时完成作业并更新相关 consignment 状态
- 读取目标车辆当前 Status。
- 若 Status 不是 LOADING 或 UNLOADING，则不适用本约束。
- 若 Status 为 LOADING 或 UNLOADING 且作业未完成，则将该车辆本 tick 合法动作集合限定为无操作。
- 拒绝任何移动或启动新作业的动作请求。
- 保持车辆状态与作业 WorkUnits 不变，等待后续 Loading/Unloading Phase 继续扣减。

## Constraints

- 装卸作业进行中车辆不能移动
- 装卸作业进行中车辆不能启动另一个作业
- 作业完成前车辆状态不得被其他动作改变
- 仅在车辆处于装卸作业进行中时生效。
- 不得在锁定期间修改车辆位置或创建新作业。

## Cautions

- 本约束只负责状态锁定，不负责 WorkUnits 结算；结算由装卸推进逻辑处理
- 作业完成发生在当 tick 结束时，而非 WorkUnits 归零的瞬间
- 作业完成判定发生在该 tick 结束时，完成当 tick 仍受锁定约束。
- 需与装卸 WorkUnits 扣减逻辑配合，避免提前解锁。

## Output Contract

- 非法移动或重复作业请求被拒绝，车辆保持 LOADING/UNLOADING 状态直至作业完成。
- 被锁定车辆的动作集合仅含无操作，非法动作被拒绝，且车辆状态与作业保持不变。

## Example Therapist Responses

### Example 1

- Client/Input: 车辆状态为 LOADING，收到本 tick 移动请求
- Therapist/Output: 拒绝移动请求，车辆保持 LOADING 状态
- Notes: 装卸作业进行中禁止移动

### Example 2

- Client/Input: 车辆状态为 UNLOADING，收到启动新作业请求
- Therapist/Output: 拒绝启动新作业请求，车辆保持 UNLOADING 状态
- Notes: 装卸作业进行中禁止启动另一作业

### Example 3

- Client/Input: 车辆 Status=LOADING，作业 WorkUnits=3，本 tick 请求 MOVE。
- Therapist/Output: 拒绝 MOVE，本 tick 合法动作仅为无操作，状态保持 LOADING。
- Notes: 作业未完成期间持续锁定。

## Triggers

- 车辆状态为 LOADING 或 UNLOADING
- 需要判定该车辆本 tick 可执行的动作
- 收到针对装卸中车辆的移动或启动新作业请求
- 生成或校验该车辆本 tick 动作
- 检查装卸作业进行中的状态一致性

## Examples

### Example 1

Input:

  车辆状态为 LOADING，收到本 tick 移动请求

Output:

  拒绝移动请求，车辆保持 LOADING 状态

Notes:

  装卸作业进行中禁止移动

### Example 2

Input:

  车辆状态为 UNLOADING，收到启动新作业请求

Output:

  拒绝启动新作业请求，车辆保持 UNLOADING 状态

Notes:

  装卸作业进行中禁止启动另一作业

### Example 3

Input:

  车辆 Status=LOADING，作业 WorkUnits=3，本 tick 请求 MOVE。

Output:

  拒绝 MOVE，本 tick 合法动作仅为无操作，状态保持 LOADING。

Notes:

  作业未完成期间持续锁定。
