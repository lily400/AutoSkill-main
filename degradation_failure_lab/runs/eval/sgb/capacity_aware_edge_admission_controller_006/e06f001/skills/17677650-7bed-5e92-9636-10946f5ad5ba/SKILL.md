---
id: "17677650-7bed-5e92-9636-10946f5ad5ba"
name: "信号相位通行准入校验"
description: "在离散时间步交通仿真中，依据当前激活相位的 GreenEdges 集合，判定某车辆能否从其所在边进入交叉口；用于每 tick 的车辆移动合法性检查。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号相位"
  - "通行准入"
  - "规则校验"
  - "离散时间步"
triggers:
  - "需要判定车辆能否进入交叉口"
  - "已确定当前激活相位及其GreenEdges"
  - "每tick车辆移动合法性检查"
examples:
  - input: "当前激活相位的GreenEdges包含边E1，车辆位于边E1并拟进入交叉口。"
    output: "允许进入交叉口；依据：边E1属于当前相位GreenEdges。"
  - input: "当前激活相位的GreenEdges不包含边E2，车辆位于边E2并拟进入交叉口。"
    output: "不允许进入交叉口；依据：边E2不在当前相位GreenEdges中。"
---

# 信号相位通行准入校验

在离散时间步交通仿真中，依据当前激活相位的 GreenEdges 集合，判定某车辆能否从其所在边进入交叉口；用于每 tick 的车辆移动合法性检查。

## Prompt

给定当前 tick 的激活相位及其 GreenEdges 集合，以及待判定车辆所在的边，执行单一准入判定：仅当该边属于当前相位的 GreenEdges 时，允许车辆进入交叉口；否则不允许。输出布尔判定结果及依据（所依据的相位与边是否在 GreenEdges 中）。不要扩展到装卸、容量或非交叉口路段行驶判定。

## Objective

确保车辆仅在所属边处于当前相位绿灯集合时才进入交叉口
## Applicable Signals

- 存在当前激活相位
- 已提供该相位的GreenEdges集合
- 待判定车辆位于某条边上并拟进入交叉口

## Contraindications

- 未提供当前相位或GreenEdges信息
- 非交叉口路段的普通行驶判定
- 涉及装卸作业或边容量/队列冲突的判定

## Intervention Moves

- 读取当前tick的激活相位
- 获取该相位的GreenEdges集合
- 检查车辆所在边是否属于GreenEdges
- 返回允许/不允许进入交叉口的判定及依据

## Workflow Steps

- 确认当前tick的激活相位。
- 获取该相位的GreenEdges集合。
- 确定待判定车辆所在的边。
- 判断该边是否在GreenEdges中。
- 输出布尔判定及依据。

## Constraints

- 判定仅依据当前激活相位的GreenEdges集合
- 仅适用于交叉口进入判定，不覆盖其他通行规则

## Cautions

- 若缺少相位或GreenEdges信息，应拒绝判定而非默认放行
- 不得将本判定与装卸、容量规则混用

## Output Contract

- 返回该车辆本tick是否允许进入交叉口的布尔判定及依据（所依据的相位与边是否在GreenEdges中）。

## Example Therapist Responses

### Example 1

- Client/Input: 当前激活相位的GreenEdges包含边E1，车辆位于边E1并拟进入交叉口。
- Therapist/Output: 允许进入交叉口；依据：边E1属于当前相位GreenEdges。

### Example 2

- Client/Input: 当前激活相位的GreenEdges不包含边E2，车辆位于边E2并拟进入交叉口。
- Therapist/Output: 不允许进入交叉口；依据：边E2不在当前相位GreenEdges中。

## Triggers

- 需要判定车辆能否进入交叉口
- 已确定当前激活相位及其GreenEdges
- 每tick车辆移动合法性检查

## Examples

### Example 1

Input:

  当前激活相位的GreenEdges包含边E1，车辆位于边E1并拟进入交叉口。

Output:

  允许进入交叉口；依据：边E1属于当前相位GreenEdges。

### Example 2

Input:

  当前激活相位的GreenEdges不包含边E2，车辆位于边E2并拟进入交叉口。

Output:

  不允许进入交叉口；依据：边E2不在当前相位GreenEdges中。
