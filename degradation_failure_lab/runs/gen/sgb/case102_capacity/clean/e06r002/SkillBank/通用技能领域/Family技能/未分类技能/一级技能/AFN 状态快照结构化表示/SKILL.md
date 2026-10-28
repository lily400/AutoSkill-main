---
id: "53a03e0c-8321-5a5d-be09-8665642e8b76"
name: "AFN 状态快照结构化表示"
description: "提供 AFN 仿真状态快照的统一分区与字段约定（GLOBAL/NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE），用于在任意 tick 生成或解析可复用的状态表示。当需要定义或解析仿真状态快照格式、或需要跨 tick 传递一致的仿真状态时使用。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "状态表示"
  - "快照规范"
  - "结构化数据"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要定义仿真状态快照格式时"
  - "需要解析已有状态快照时"
  - "需要跨 tick 传递一致的仿真状态时"
examples:
  - input: "需要为某 tick 生成状态快照"
    output: "GLOBAL: TimeTick=当前 tick 索引; ScenarioName=\"Morning Rush\"; ScoreSoFar=累计服务分数（可能暂定）。随后按 NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE 分区组织。"
    notes: "示例仅展示 GLOBAL 分区字段，其余分区按规范组织。"
---

# AFN 状态快照结构化表示

提供 AFN 仿真状态快照的统一分区与字段约定（GLOBAL/NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE），用于在任意 tick 生成或解析可复用的状态表示。当需要定义或解析仿真状态快照格式、或需要跨 tick 传递一致的仿真状态时使用。

## Prompt

依据 AFN 状态快照规范，将给定 tick 的仿真状态组织为结构化快照。按分区依次输出：GLOBAL（TimeTick 当前 tick 索引、ScenarioName 场景名、ScoreSoFar 累计服务分数，可能为暂定值）、NODES、EDGES、VEHICLES、CONSIGNMENTS、INCIDENTS_ACTIVE。每个分区保持字段命名一致，便于跨 tick 生成与解析复用。本技能仅负责状态表示与字段约定，不执行仿真推进、冲突裁决或信号决策。

## Objective

提供统一的状态快照分区与字段约定，供仿真状态生成与解析复用。
## Applicable Signals

- 需要定义或解析仿真状态快照格式
- 需要跨 tick 传递一致的仿真状态

## Contraindications

- 需要执行具体仿真推进或冲突裁决时
- 需要信号配时决策或事件处理逻辑时

## Intervention Moves

- 按 GLOBAL/NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE 分区组织快照
- 在 GLOBAL 分区填写 TimeTick、ScenarioName、ScoreSoFar
- 保持各分区字段命名一致以支持解析复用

## Workflow Steps

- 确定当前 tick 索引与场景名
- 填写 GLOBAL 分区：TimeTick、ScenarioName、ScoreSoFar
- 按分区组织 NODES、EDGES、VEHICLES、CONSIGNMENTS、INCIDENTS_ACTIVE
- 校验各分区字段命名与结构一致性

## Constraints

- 快照必须包含 GLOBAL 分区且含 TimeTick、ScenarioName、ScoreSoFar 字段
- ScoreSoFar 允许为暂定值
- 仅描述状态表示，不包含执行流程或裁决逻辑

## Cautions

- ScoreSoFar 可能为暂定值，下游不应视为最终分数
- 本技能不覆盖仿真推进、冲突裁决等执行内容

## Output Contract

- 一份符合分区与字段约定的状态快照结构说明，包含 GLOBAL/NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE 各分区及字段定义。

## Example Therapist Responses

### Example 1

- Client/Input: 需要为某 tick 生成状态快照
- Therapist/Output: GLOBAL: TimeTick=当前 tick 索引; ScenarioName="Morning Rush"; ScoreSoFar=累计服务分数（可能暂定）。随后按 NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE 分区组织。
- Notes: 示例仅展示 GLOBAL 分区字段，其余分区按规范组织。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要定义仿真状态快照格式时
- 需要解析已有状态快照时
- 需要跨 tick 传递一致的仿真状态时

## Examples

### Example 1

Input:

  需要为某 tick 生成状态快照

Output:

  GLOBAL: TimeTick=当前 tick 索引; ScenarioName="Morning Rush"; ScoreSoFar=累计服务分数（可能暂定）。随后按 NODES/EDGES/VEHICLES/CONSIGNMENTS/INCIDENTS_ACTIVE 分区组织。

Notes:

  示例仅展示 GLOBAL 分区字段，其余分区按规范组织。
