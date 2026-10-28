---
id: "8031195d-6143-5db6-828f-0b0ace06658a"
name: "预爬虫与反应器设置作用域约束"
description: "约束预爬虫设置不可按 Spider 定义、反应器设置在同一进程多 Spider 运行时不应按 Spider 取不同值；用于配置多 Spider 同进程运行或考虑在 Spider 中定义受限设置时，避免因按 Spider 覆盖受限设置导致运行异常。"
version: "0.1.0"
tags:
  - "scrapy"
  - "settings"
  - "配置约束"
  - "作用域限制"
  - "多spider"
triggers:
  - "同一进程运行多个 Spider"
  - "考虑在 Spider 中定义预爬虫或反应器设置"
  - "审查 Spider 级设置是否会覆盖受限设置类别"
examples:
  - input: "在同一进程运行多个 Spider，并考虑在某个 Spider 中定义反应器设置的不同取值"
    output: "指出反应器设置不应按 Spider 取不同值，建议统一为项目级一致取值"
    notes: "多 Spider 同进程场景"
---

# 预爬虫与反应器设置作用域约束

约束预爬虫设置不可按 Spider 定义、反应器设置在同一进程多 Spider 运行时不应按 Spider 取不同值；用于配置多 Spider 同进程运行或考虑在 Spider 中定义受限设置时，避免因按 Spider 覆盖受限设置导致运行异常。

## Prompt

在配置 Scrapy 项目时，检查是否存在按 Spider 定义预爬虫设置或为反应器设置按 Spider 赋不同值的情况。若同一进程运行多个 Spider，确保反应器设置保持一致；预爬虫设置只能在项目级定义，不得放入 Spider 设置。发现违规时移除 Spider 级覆盖并回退到项目级配置，最后确认受限设置未被按 Spider 覆盖。

## Objective

避免因按 Spider 覆盖受限设置导致运行异常
## Applicable Signals

- 同一进程运行多个 Spider
- Spider 设置中出现预爬虫设置
- 反应器设置在不同 Spider 间取值不一致

## Contraindications

- 单 Spider 独立进程运行且无相关设置

## Intervention Moves

- 识别受限设置类别（预爬虫设置、反应器设置）
- 检查 Spider 级设置是否覆盖受限类别
- 将预爬虫设置回退到项目级定义
- 统一同一进程内各 Spider 的反应器设置取值

## Workflow Steps

- 确认当前是否在同一进程运行多个 Spider
- 检查 Spider 设置中是否定义了预爬虫设置
- 检查反应器设置是否在不同 Spider 间取值不同
- 移除违规的 Spider 级覆盖并回退到项目级配置
- 确认受限设置未被按 Spider 覆盖

## Constraints

- 预爬虫设置不可按 Spider 定义
- 同一进程多 Spider 运行时反应器设置不应按 Spider 取不同值

## Cautions

- Spider 设置通常优先于项目设置，但该优先级不适用于预爬虫设置与反应器设置的作用域限制

## Output Contract

- 确认受限设置未被按 Spider 覆盖，并给出回退到项目级配置的结论

## Example Therapist Responses

### Example 1

- Client/Input: 在同一进程运行多个 Spider，并考虑在某个 Spider 中定义反应器设置的不同取值
- Therapist/Output: 指出反应器设置不应按 Spider 取不同值，建议统一为项目级一致取值
- Notes: 多 Spider 同进程场景

## Triggers

- 同一进程运行多个 Spider
- 考虑在 Spider 中定义预爬虫或反应器设置
- 审查 Spider 级设置是否会覆盖受限设置类别

## Examples

### Example 1

Input:

  在同一进程运行多个 Spider，并考虑在某个 Spider 中定义反应器设置的不同取值

Output:

  指出反应器设置不应按 Spider 取不同值，建议统一为项目级一致取值

Notes:

  多 Spider 同进程场景
