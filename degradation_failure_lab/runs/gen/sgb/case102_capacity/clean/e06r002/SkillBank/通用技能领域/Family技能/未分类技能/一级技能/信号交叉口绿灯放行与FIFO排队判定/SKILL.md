---
id: "0693600c-9b20-5996-8e38-1b1d384e424d"
name: "信号交叉口绿灯放行与FIFO排队判定"
description: "在信号化下游节点，按入边信号组的当前相位判定车辆本tick能否进入交叉口，并按到达队列的FIFO顺序确定同一入边多车的放行顺序。"
version: "0.1.0"
tags:
  - "交通仿真"
  - "信号交叉口"
  - "绿灯相位"
  - "FIFO"
  - "车辆放行"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "需要判定某入边车辆本tick能否进入信号交叉口"
  - "需要确定同一入边多车的放行顺序"
  - "逐tick更新信号交叉口车辆移动"
examples:
  - input: "下游节点为信号化节点，入边A信号组处于GREEN，队列到达顺序为v1、v2；入边B信号组处于RED。"
    output: "本tick可放行：入边A按FIFO顺序放行v1、v2；入边B不放行。"
---

# 信号交叉口绿灯放行与FIFO排队判定

在信号化下游节点，按入边信号组的当前相位判定车辆本tick能否进入交叉口，并按到达队列的FIFO顺序确定同一入边多车的放行顺序。

## Prompt

给定信号化下游节点、各入边的信号组与当前相位、以及各入边节点队列的到达顺序，执行以下判定：
1. 确认下游节点为信号化节点，且车辆已到达该节点队列；否则不适用本规则。
2. 对每条入边，检查其信号组当前是否处于GREEN相位。
3. 仅对处于GREEN相位的入边，按到达节点队列的先后顺序（FIFO）依次放行车辆进入交叉口。
4. 非GREEN相位入边上的车辆本tick不放行。
5. 输出本tick可放行车辆列表，按入边分组并保持FIFO顺序。

## Objective

按信号相位与FIFO顺序正确判定交叉口车辆放行
## Applicable Signals

- 下游节点为信号化节点
- 入边配置了信号组
- 车辆已到达节点队列并请求进入下游边

## Contraindications

- 下游节点无信号控制
- 车辆尚未到达节点队列

## Intervention Moves

- 检查入边信号组当前相位是否为GREEN
- 对GREEN相位入边按到达队列FIFO顺序放行
- 对非GREEN相位入边本tick不放行

## Workflow Steps

- 确认下游节点为信号化节点且车辆已到达节点队列
- 读取各入边信号组及当前相位
- 筛选处于GREEN相位的入边
- 对每条GREEN入边按到达队列FIFO顺序放行车辆
- 汇总本tick可放行车辆列表及顺序

## Constraints

- 仅GREEN相位信号组的入边可释放新车辆进入交叉口
- 同一入边放行顺序必须为到达队列的FIFO顺序

## Cautions

- 本规则仅覆盖信号放行判定，不处理进入失败后的回退行为
- 相位判定以当前tick为准

## Output Contract

- 输出本tick可放行车辆列表，按入边分组并保持FIFO顺序

## Example Therapist Responses

### Example 1

- Client/Input: 下游节点为信号化节点，入边A信号组处于GREEN，队列到达顺序为v1、v2；入边B信号组处于RED。
- Therapist/Output: 本tick可放行：入边A按FIFO顺序放行v1、v2；入边B不放行。

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要判定某入边车辆本tick能否进入信号交叉口
- 需要确定同一入边多车的放行顺序
- 逐tick更新信号交叉口车辆移动

## Examples

### Example 1

Input:

  下游节点为信号化节点，入边A信号组处于GREEN，队列到达顺序为v1、v2；入边B信号组处于RED。

Output:

  本tick可放行：入边A按FIFO顺序放行v1、v2；入边B不放行。
