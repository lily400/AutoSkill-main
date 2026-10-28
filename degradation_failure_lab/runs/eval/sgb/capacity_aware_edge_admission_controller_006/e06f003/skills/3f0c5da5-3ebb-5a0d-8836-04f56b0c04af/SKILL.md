---
id: "3f0c5da5-3ebb-5a0d-8836-04f56b0c04af"
name: "信号交叉口到达边识别"
description: "根据信号设置说明，识别被信号控制的交叉口节点及其受控到达边集合，用于确定信号化节点范围。适用于需要明确哪些到达边受信号控制时。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号配置"
  - "规则匹配"
  - "场景初始化"
triggers:
  - "需要确定哪些到达边受信号控制"
  - "需要确定信号化节点范围"
  - "场景初始化时解析信号设置"
examples:
  - input: "Node N3 (Central Intersection) is signalized for edges arriving from N2, N4, N5, N10, N7, and N8."
    output: "信号化节点：N3；受控到达边来源：N2, N4, N5, N10, N7, N8"
---

# 信号交叉口到达边识别

根据信号设置说明，识别被信号控制的交叉口节点及其受控到达边集合，用于确定信号化节点范围。适用于需要明确哪些到达边受信号控制时。

## Prompt

读取信号设置说明，定位被声明为信号化的节点，提取该节点受控的到达边来源节点集合，输出信号化节点与受控到达边清单。仅依据说明中明确声明的信号化节点，不推断未声明的节点。

## Objective

确定信号化节点及其受控到达边
## Applicable Signals

- 信号设置说明中声明某节点为信号化
- 需要列出受信号控制的到达边

## Contraindications

- 节点未声明为信号化
- 信号设置说明缺失或未覆盖目标节点

## Intervention Moves

- 定位信号化节点声明
- 提取该节点受控的到达边来源节点集合
- 整理为信号化节点与受控到达边清单

## Workflow Steps

- 读取信号设置说明
- 识别被声明为信号化的节点
- 提取该节点受控的到达边来源节点
- 输出信号化节点与受控到达边清单

## Constraints

- 仅依据说明中明确声明的信号化节点
- 不推断未声明的节点或到达边

## Cautions

- 信号化节点可能受控多条到达边，需完整列出
- 避免将未声明信号化的节点纳入清单

## Output Contract

- 信号化节点与受控到达边清单

## Example Therapist Responses

### Example 1

- Client/Input: Node N3 (Central Intersection) is signalized for edges arriving from N2, N4, N5, N10, N7, and N8.
- Therapist/Output: 信号化节点：N3；受控到达边来源：N2, N4, N5, N10, N7, N8

## Triggers

- 需要确定哪些到达边受信号控制
- 需要确定信号化节点范围
- 场景初始化时解析信号设置

## Examples

### Example 1

Input:

  Node N3 (Central Intersection) is signalized for edges arriving from N2, N4, N5, N10, N7, and N8.

Output:

  信号化节点：N3；受控到达边来源：N2, N4, N5, N10, N7, N8
