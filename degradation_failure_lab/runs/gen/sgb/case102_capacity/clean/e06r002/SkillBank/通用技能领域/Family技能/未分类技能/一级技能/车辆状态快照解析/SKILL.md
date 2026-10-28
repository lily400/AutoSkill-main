---
id: "7a90ecb6-a5c8-5129-ab01-9f8db8b78041"
name: "车辆状态快照解析"
description: "从仿真状态快照的 VEHICLES 段读取并结构化每辆车的状态字段（车辆ID、类型、位置类型与位置ID、状态、载重占用、在车货物列表），用于构建或核对仿真状态快照。"
version: "0.1.0"
tags:
  - "状态快照"
  - "车辆解析"
  - "字段解析"
  - "交通仿真"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要读取或校验 VEHICLES 段内容"
  - "构建或核对仿真状态快照"
  - "需要获取车辆位置、状态与载重信息"
examples:
  - input: "VEHICLES\nV1 TRUCK LocationType: NODE LocationID: N1 Status: IDLE_AT_NODE LoadUnitsUsed: 0 OnboardConsignments: []"
    output: "车辆ID: V1, 类型: TRUCK, 位置类型: NODE, 位置ID: N1, 状态: IDLE_AT_NODE, 载重占用: 0, 在车货物: []"
---

# 车辆状态快照解析

从仿真状态快照的 VEHICLES 段读取并结构化每辆车的状态字段（车辆ID、类型、位置类型与位置ID、状态、载重占用、在车货物列表），用于构建或核对仿真状态快照。

## Prompt

定位状态快照中的 VEHICLES 段，逐行解析每辆车的条目：提取车辆ID、车辆类型、LocationType、LocationID、Status、LoadUnitsUsed、OnboardConsignments。保持字段原值，不推断缺失字段；对空列表保留为空。输出结构化的车辆状态列表，供后续状态核对或调度使用。

## Objective

从 VEHICLES 段正确读取并结构化每辆车的状态字段
## Applicable Signals

- 输入包含 VEHICLES 段
- 需要车辆位置类型为 NODE 等位置信息
- 需要载重占用与在车货物列表

## Contraindications

- 处理货物或事件段
- 需要执行调度决策而非解析状态

## Intervention Moves

- 定位 VEHICLES 段边界
- 逐行提取车辆字段
- 将 OnboardConsignments 解析为列表
- 汇总为结构化车辆状态列表

## Workflow Steps

- 定位 VEHICLES 段起始与结束
- 对每个车辆条目提取车辆ID与类型
- 提取 LocationType 与 LocationID
- 提取 Status 与 LoadUnitsUsed
- 解析 OnboardConsignments 列表
- 输出结构化车辆状态列表

## Constraints

- 仅解析 VEHICLES 段，不混入 CONSIGNMENTS 或 INCIDENTS 段
- 保持字段原值，不推断缺失字段

## Cautions

- 空在车货物列表应保留为空而非省略
- 位置类型与位置ID需成对读取

## Output Contract

- 结构化的车辆状态列表，每项含车辆ID、类型、位置类型、位置ID、状态、载重占用与在车货物列表

## Example Therapist Responses

### Example 1

- Client/Input: VEHICLES
V1 TRUCK LocationType: NODE LocationID: N1 Status: IDLE_AT_NODE LoadUnitsUsed: 0 OnboardConsignments: []
- Therapist/Output: 车辆ID: V1, 类型: TRUCK, 位置类型: NODE, 位置ID: N1, 状态: IDLE_AT_NODE, 载重占用: 0, 在车货物: []

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要读取或校验 VEHICLES 段内容
- 构建或核对仿真状态快照
- 需要获取车辆位置、状态与载重信息

## Examples

### Example 1

Input:

  VEHICLES
  V1 TRUCK LocationType: NODE LocationID: N1 Status: IDLE_AT_NODE LoadUnitsUsed: 0 OnboardConsignments: []

Output:

  车辆ID: V1, 类型: TRUCK, 位置类型: NODE, 位置ID: N1, 状态: IDLE_AT_NODE, 载重占用: 0, 在车货物: []
