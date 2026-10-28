---
id: "7ba74262-2445-50bc-9936-6b2950cefcaf"
name: "信号交叉口相位-绿灯边映射查询"
description: "根据信号节点的周期长度与当前 tick 计算所处相位，并返回该相位允许通行的 GreenEdges 集合；用于仿真推进或状态快照时判定某条入边是否获得绿灯。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号配时"
  - "相位映射"
  - "绿灯边"
  - "状态查询"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要判断某入边在 tick t 是否绿灯"
  - "需要为信号节点生成状态快照"
  - "需要确定信号节点当前所处相位"
examples:
  - input: "节点 N3，CycleLength = 6，tick t = 3，查询相位与 GreenEdges"
    output: "t mod 6 = 3，属于 Phase B（ticks 2-3 mod 6），GreenEdges = {E3, E5, E12}"
    notes: "相位区间按 mod CycleLength 匹配"
  - input: "节点 N4，CycleLength = 4，tick t = 1，查询相位与 GreenEdges"
    output: "t mod 4 = 1，属于 Phase 1（ticks 0-1 mod 4），GreenEdges = {E3}"
    notes: "简单双相位周期"
---

# 信号交叉口相位-绿灯边映射查询

根据信号节点的周期长度与当前 tick 计算所处相位，并返回该相位允许通行的 GreenEdges 集合；用于仿真推进或状态快照时判定某条入边是否获得绿灯。

## Prompt

输入信号节点定义（CycleLength 与各相位的 tick 区间及 GreenEdges）与当前 tick t。先对 t 按 CycleLength 取模得到周期内位置，再匹配该位置所属相位，输出相位标识与该相位的 GreenEdges 集合。若需判定某条入边，检查该边是否在 GreenEdges 中。仅做相位到绿灯边的映射查询，不涉及车辆移动、冲突裁决或容量排队。

## Objective

在给定 tick 下确定信号节点的当前相位及其绿灯边集合
## Applicable Signals

- 节点已配置 CycleLength 与相位定义
- 查询目标为某入边在特定 tick 的通行权
- 需要输出信号节点状态快照

## Contraindications

- 节点未配置信号（无 CycleLength/相位定义）
- 需要处理非信号冲突或容量排队

## Intervention Moves

- 对当前 tick 按 CycleLength 取模
- 将取模结果匹配到相位 tick 区间
- 返回相位标识与对应 GreenEdges 集合
- 按需检查目标入边是否在 GreenEdges 中

## Workflow Steps

- 读取信号节点的 CycleLength 与各相位定义（tick 区间、GreenEdges）
- 计算 t mod CycleLength 得到周期内位置
- 匹配该位置所属相位
- 输出相位标识与 GreenEdges 集合
- 如需判定入边，检查该边是否在 GreenEdges 中

## Constraints

- 仅做相位到绿灯边的映射查询
- 不涉及车辆移动、冲突裁决或容量排队
- 相位区间以 mod CycleLength 的 tick 区间为准

## Cautions

- 不同节点周期长度不同，需按各自 CycleLength 取模
- 同一相位可能包含多条 GreenEdges，需完整返回集合

## Output Contract

- 返回当前相位标识与该相位的 GreenEdges 集合；如查询入边，附带该边是否绿灯的判定。

## Example Therapist Responses

### Example 1

- Client/Input: 节点 N3，CycleLength = 6，tick t = 3，查询相位与 GreenEdges
- Therapist/Output: t mod 6 = 3，属于 Phase B（ticks 2-3 mod 6），GreenEdges = {E3, E5, E12}
- Notes: 相位区间按 mod CycleLength 匹配

### Example 2

- Client/Input: 节点 N4，CycleLength = 4，tick t = 1，查询相位与 GreenEdges
- Therapist/Output: t mod 4 = 1，属于 Phase 1（ticks 0-1 mod 4），GreenEdges = {E3}
- Notes: 简单双相位周期

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判断某入边在 tick t 是否绿灯
- 需要为信号节点生成状态快照
- 需要确定信号节点当前所处相位

## Examples

### Example 1

Input:

  节点 N3，CycleLength = 6，tick t = 3，查询相位与 GreenEdges

Output:

  t mod 6 = 3，属于 Phase B（ticks 2-3 mod 6），GreenEdges = {E3, E5, E12}

Notes:

  相位区间按 mod CycleLength 匹配

### Example 2

Input:

  节点 N4，CycleLength = 4，tick t = 1，查询相位与 GreenEdges

Output:

  t mod 4 = 1，属于 Phase 1（ticks 0-1 mod 4），GreenEdges = {E3}

Notes:

  简单双相位周期
