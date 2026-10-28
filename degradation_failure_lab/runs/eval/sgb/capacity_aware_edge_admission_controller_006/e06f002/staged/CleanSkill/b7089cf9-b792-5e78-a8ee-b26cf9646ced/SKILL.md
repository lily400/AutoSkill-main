---
id: "b7089cf9-b792-5e78-a8ee-b26cf9646ced"
name: "信号相位通行判定"
description: "根据当前 tick 与信号周期相位判断指定边是否处于绿灯，从而决定车辆能否进入下游节点；用于逐 tick 推进仿真时校验车辆进入合法性，并给出可进入的最早 tick。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号控制"
  - "相位周期"
  - "通行判定"
  - "micro_skill"
triggers:
  - "需要判断某车辆能否在给定 tick 进入下游节点"
  - "存在多相位信号且各边绿灯时段不同"
  - "逐 tick 推进仿真时需校验车辆进入合法性"
examples:
  - input: "周期长度 6，Phase A 为 t mod 6 = 0，E2 属于 Phase A，E5 不属于 Phase A；当前 tick = 6，车辆 V2 欲进入 E2 下游，V3 欲进入 E5 下游。"
    output: "tick 6 时 E2 为绿灯，V2 可进入；E5 非绿灯，V3 需等待至 Phase B（tick 8 或 9）方可进入。"
    notes: "体现同一 tick 下不同边相位不同导致的通行差异。"
---

# 信号相位通行判定

根据当前 tick 与信号周期相位判断指定边是否处于绿灯，从而决定车辆能否进入下游节点；用于逐 tick 推进仿真时校验车辆进入合法性，并给出可进入的最早 tick。

## Prompt

给定当前 tick、信号周期长度与相位划分，以及目标边所属相位，先对 tick 取模确定所处相位，再判断目标边在该相位是否为绿灯。若为绿灯则允许车辆进入下游节点；若为红灯则输出等待结论，并推算该边下一次绿灯的最早 tick。仅处理通行许可判定，不涉及容量、排队或冲突计算。

## Objective

判定指定边在当前 tick 是否允许车辆进入，并给出可进入的最早 tick
## Applicable Signals

- 目标边受多相位信号控制
- 各边绿灯时段按相位周期不同
- 需要基于 tick 取模确定当前相位

## Contraindications

- 边无信号控制
- 需要计算容量或排队而非通行许可
- 需要处理容量折减或事故影响

## Intervention Moves

- 对当前 tick 按周期长度取模得到相位位置
- 将相位位置映射到对应相位
- 判断目标边在该相位是否为绿灯
- 若为红灯则推算下一次绿灯的最早 tick

## Workflow Steps

- 读取当前 tick、信号周期长度与相位划分
- 计算 t mod 周期长度，确定当前所处相位
- 确认目标边所属相位及其绿灯时段
- 若当前相位为目标边绿灯，则判定允许进入
- 若为红灯，则推算该边下一次绿灯的最早 tick 并输出等待结论

## Constraints

- 判定必须基于 tick 对周期取模，而非绝对 tick
- 仅判定单一边的通行许可，不扩展到其他边或容量计算

## Cautions

- 不同边可能属于不同相位，绿灯时段不同，需逐边判定
- 相位边界处需确认取模结果对应的相位归属

## Output Contract

- 输出该边在当前 tick 的通行/等待结论，并在等待时给出可进入的最早 tick。

## Example Therapist Responses

### Example 1

- Client/Input: 周期长度 6，Phase A 为 t mod 6 = 0，E2 属于 Phase A，E5 不属于 Phase A；当前 tick = 6，车辆 V2 欲进入 E2 下游，V3 欲进入 E5 下游。
- Therapist/Output: tick 6 时 E2 为绿灯，V2 可进入；E5 非绿灯，V3 需等待至 Phase B（tick 8 或 9）方可进入。
- Notes: 体现同一 tick 下不同边相位不同导致的通行差异。

## Triggers

- 需要判断某车辆能否在给定 tick 进入下游节点
- 存在多相位信号且各边绿灯时段不同
- 逐 tick 推进仿真时需校验车辆进入合法性

## Examples

### Example 1

Input:

  周期长度 6，Phase A 为 t mod 6 = 0，E2 属于 Phase A，E5 不属于 Phase A；当前 tick = 6，车辆 V2 欲进入 E2 下游，V3 欲进入 E5 下游。

Output:

  tick 6 时 E2 为绿灯，V2 可进入；E5 非绿灯，V3 需等待至 Phase B（tick 8 或 9）方可进入。

Notes:

  体现同一 tick 下不同边相位不同导致的通行差异。
