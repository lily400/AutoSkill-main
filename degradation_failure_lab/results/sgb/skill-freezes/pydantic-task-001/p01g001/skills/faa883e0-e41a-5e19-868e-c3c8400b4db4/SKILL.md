---
id: "faa883e0-e41a-5e19-868e-c3c8400b4db4"
name: "字段校验器访问已校验数据"
description: "在字段校验器中通过 ValidationInfo.data 读取已校验的其他字段值，用于跨字段依赖校验，可作为 after 模型校验器的替代方案。"
version: "0.1.0"
tags:
  - "pydantic"
  - "字段校验"
  - "跨字段校验"
  - "ValidationInfo"
triggers:
  - "需要在字段校验器中依赖其他已校验字段的值"
  - "希望用字段校验器替代 after 模型校验器"
---

# 字段校验器访问已校验数据

在字段校验器中通过 ValidationInfo.data 读取已校验的其他字段值，用于跨字段依赖校验，可作为 after 模型校验器的替代方案。

## Prompt

当需要在字段级校验中依赖其他已校验字段的值时，为字段校验器添加 ValidationInfo 参数，通过 info.data 读取已校验数据并据此完成校验；若依赖的字段尚未校验，则不要使用此方式。

## Objective

在字段级校验中安全访问已校验数据以完成跨字段校验
## Applicable Signals

- 字段校验逻辑需要读取其他字段的已校验值
- 考虑用字段校验器替代 after 模型校验器

## Contraindications

- 需要访问尚未校验的字段
- 校验逻辑与单字段无关且更适合模型级校验

## Intervention Moves

- 为字段校验器函数增加 ValidationInfo 参数
- 通过 info.data 属性读取已校验数据
- 基于已校验数据执行跨字段校验并返回结果

## Workflow Steps

- 确认目标字段依赖的其他字段在校验顺序中已先完成校验
- 在字段校验器签名中加入 ValidationInfo 参数
- 通过 info.data 读取已校验数据并执行校验逻辑
- 返回校验结果或抛出校验错误

## Constraints

- 仅能访问已校验的数据，不能依赖尚未校验的字段

## Cautions

- 依赖字段的校验顺序会影响 info.data 中可用数据，需确认顺序正确

## Output Contract

- 字段校验器正确读取 ValidationInfo.data 并返回校验结果

## Triggers

- 需要在字段校验器中依赖其他已校验字段的值
- 希望用字段校验器替代 after 模型校验器
