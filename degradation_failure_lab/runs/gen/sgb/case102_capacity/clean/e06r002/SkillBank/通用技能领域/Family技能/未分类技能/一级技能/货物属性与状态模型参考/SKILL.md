---
id: "eabb39c2-523c-51b8-91f7-69616e60a20d"
name: "货物属性与状态模型参考"
description: "提供货物（Consignment）实体的标准字段集合与状态枚举定义，供仿真初始化、状态快照 CONSIGNMENTS 段及装载逻辑引用。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "货物建模"
  - "数据模式"
  - "状态枚举"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "构建或校验货物数据结构"
  - "生成状态快照中的 CONSIGNMENTS 段"
  - "需要引用货物字段或状态枚举"
examples:
  - input: "需要定义货物实体结构"
    output: "ConsignmentID（唯一）、OriginNode、DestinationNode、SizeUnits（整数>=1）、ReleaseTime、DueTime、PriorityLevel（LOW/STANDARD/HIGH/CRITICAL）、Status（PENDING_AT_ORIGIN/ON_VEHICLE/DELIVERED/CANCELLED）、AssignedVehicleID（可选）"
---

# 货物属性与状态模型参考

提供货物（Consignment）实体的标准字段集合与状态枚举定义，供仿真初始化、状态快照 CONSIGNMENTS 段及装载逻辑引用。

## Prompt

依据本参考定义货物实体的标准字段与状态枚举：ConsignmentID（唯一）、OriginNode、DestinationNode、SizeUnits（整数且 >= 1）、ReleaseTime（在 OriginNode 可用的起始 tick）、DueTime（到达 DestinationNode 的目标最晚 tick）、PriorityLevel（LOW/STANDARD/HIGH/CRITICAL）、Status（PENDING_AT_ORIGIN/ON_VEHICLE/DELIVERED/CANCELLED）、AssignedVehicleID（可选）。仅输出字段与枚举定义，不执行装载动作或容量校验。

## Objective

提供货物实体的标准字段与状态枚举参考
## Applicable Signals

- 需要定义或核对货物字段
- 需要枚举货物状态取值
- 需要为快照 CONSIGNMENTS 段提供结构

## Contraindications

- 需要执行装载动作而非定义数据结构
- 需要容量校验逻辑

## Intervention Moves

- 列出货物标准字段及类型约束
- 列出状态枚举取值
- 标注可选字段

## Workflow Steps

- 确认货物实体所需字段范围
- 按标准定义列出各字段及取值约束
- 列出 Status 枚举取值
- 标注 AssignedVehicleID 为可选字段
- 输出字段与枚举定义供下游引用

## Constraints

- SizeUnits 必须为整数且 >= 1
- Status 取值限于 PENDING_AT_ORIGIN、ON_VEHICLE、DELIVERED、CANCELLED
- PriorityLevel 取值限于 LOW、STANDARD、HIGH、CRITICAL
- ConsignmentID 必须唯一

## Cautions

- 本参考不含装载执行逻辑，容量校验需另行引用相应规则

## Output Contract

- 符合规范的货物字段与状态枚举定义

## Example Therapist Responses

### Example 1

- Client/Input: 需要定义货物实体结构
- Therapist/Output: ConsignmentID（唯一）、OriginNode、DestinationNode、SizeUnits（整数>=1）、ReleaseTime、DueTime、PriorityLevel（LOW/STANDARD/HIGH/CRITICAL）、Status（PENDING_AT_ORIGIN/ON_VEHICLE/DELIVERED/CANCELLED）、AssignedVehicleID（可选）

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 构建或校验货物数据结构
- 生成状态快照中的 CONSIGNMENTS 段
- 需要引用货物字段或状态枚举

## Examples

### Example 1

Input:

  需要定义货物实体结构

Output:

  ConsignmentID（唯一）、OriginNode、DestinationNode、SizeUnits（整数>=1）、ReleaseTime、DueTime、PriorityLevel（LOW/STANDARD/HIGH/CRITICAL）、Status（PENDING_AT_ORIGIN/ON_VEHICLE/DELIVERED/CANCELLED）、AssignedVehicleID（可选）
