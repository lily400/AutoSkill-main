---
id: "12d1ad66-9416-5cce-87f7-c629df2206c1"
name: "货物状态快照解析"
description: "解析状态快照中 CONSIGNMENTS 段的货物条目，按货物状态条件读取并结构化 ConsignmentID、Status、CurrentNode、AssignedVehicleID 与 DeliveredTime 等字段，用于读取或校验货物分配与交付状态。"
version: "0.1.0"
tags:
  - "状态快照"
  - "货物解析"
  - "条件字段"
  - "交通仿真"
triggers:
  - "需要读取或校验 CONSIGNMENTS 段内容"
  - "核对货物分配与交付状态"
  - "需要将货物条目转为结构化状态列表"
examples:
  - input: "CONSIGNMENTS 段中一条货物条目，含 ConsignmentID、Status 及条件字段"
    output: "结构化条目：ConsignmentID、Status，以及按状态条件读取的 CurrentNode / AssignedVehicleID / DeliveredTime"
    notes: "仅输出条目实际提供的字段"
---

# 货物状态快照解析

解析状态快照中 CONSIGNMENTS 段的货物条目，按货物状态条件读取并结构化 ConsignmentID、Status、CurrentNode、AssignedVehicleID 与 DeliveredTime 等字段，用于读取或校验货物分配与交付状态。

## Prompt

定位状态快照中的 CONSIGNMENTS 段，逐条读取货物条目。对每个条目先读取 ConsignmentID 与 Status，再依据状态条件读取其余字段：当状态为 PENDING_AT_ORIGIN 或货物停留在中间节点时读取 CurrentNode；当存在分配车辆时读取 AssignedVehicleID；当货物已交付时读取 DeliveredTime。仅输出由条目实际提供的字段，不推断缺失字段，不处理车辆段或事件段，不进行路径规划。

## Objective

按货物状态条件正确读取并结构化货物字段
## Applicable Signals

- 输入包含 CONSIGNMENTS 段
- 需要核对货物分配或交付状态
- 需要将货物条目转为结构化列表

## Contraindications

- 处理车辆段或事件段
- 需要执行路径规划
- 输入中不存在 CONSIGNMENTS 段

## Intervention Moves

- 定位 CONSIGNMENTS 段并逐条切分货物条目
- 先读取 ConsignmentID 与 Status 作为基础字段
- 按状态条件读取 CurrentNode、AssignedVehicleID、DeliveredTime
- 仅保留条目实际提供的字段并汇总为列表

## Workflow Steps

- 定位状态快照中的 CONSIGNMENTS 段
- 逐条切分货物条目
- 读取每个条目的 ConsignmentID 与 Status
- 当状态为 PENDING_AT_ORIGIN 或停留在中间节点时读取 CurrentNode
- 当存在分配车辆时读取 AssignedVehicleID
- 当货物已交付时读取 DeliveredTime
- 汇总为结构化货物状态列表

## Constraints

- 字段读取必须与货物状态条件一致
- 不得为条目补造未提供的字段
- 仅处理 CONSIGNMENTS 段，不混入车辆或事件段

## Cautions

- 状态与字段的对应关系依赖条目实际内容，缺失字段应留空而非推断
- 不同状态下的字段集合不同，需逐条判断

## Output Contract

- 结构化的货物状态列表，每条含 ConsignmentID 与 Status，并按状态条件附带 CurrentNode、AssignedVehicleID、DeliveredTime 等字段。

## Example Therapist Responses

### Example 1

- Client/Input: CONSIGNMENTS 段中一条货物条目，含 ConsignmentID、Status 及条件字段
- Therapist/Output: 结构化条目：ConsignmentID、Status，以及按状态条件读取的 CurrentNode / AssignedVehicleID / DeliveredTime
- Notes: 仅输出条目实际提供的字段

## Triggers

- 需要读取或校验 CONSIGNMENTS 段内容
- 核对货物分配与交付状态
- 需要将货物条目转为结构化状态列表

## Examples

### Example 1

Input:

  CONSIGNMENTS 段中一条货物条目，含 ConsignmentID、Status 及条件字段

Output:

  结构化条目：ConsignmentID、Status，以及按状态条件读取的 CurrentNode / AssignedVehicleID / DeliveredTime

Notes:

  仅输出条目实际提供的字段
