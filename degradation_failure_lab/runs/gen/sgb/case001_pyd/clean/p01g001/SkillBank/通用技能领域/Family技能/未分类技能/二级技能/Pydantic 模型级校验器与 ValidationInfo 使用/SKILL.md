---
id: "4641701b-2dc0-5429-a380-d65c1c0ec55d"
name: "Pydantic 模型级校验器与 ValidationInfo 使用"
description: "实现 Pydantic 模型级校验器，并在校验中通过 ValidationInfo 读取字段数据、已校验数据与校验上下文，用于跨字段依赖或需要访问上下文的校验场景。"
version: "0.1.0"
tags:
  - "pydantic"
  - "模型校验"
  - "ValidationInfo"
  - "跨字段校验"
  - "校验上下文"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
  - "kind:parent"
triggers:
  - "校验逻辑依赖多个字段"
  - "需要访问 ValidationInfo 的 data"
  - "需要访问 ValidationInfo 的 context"
  - "需要实现模型级而非字段级校验"
---

# Pydantic 模型级校验器与 ValidationInfo 使用

实现 Pydantic 模型级校验器，并在校验中通过 ValidationInfo 读取字段数据、已校验数据与校验上下文，用于跨字段依赖或需要访问上下文的校验场景。

## Prompt

当校验逻辑依赖多个字段，或需要访问 ValidationInfo 的 data 或 context 时，使用本技能：在模型中定义模型级校验器（annotated 或 decorator 模式），按需读取 info.data（已校验字段值）与 info.context（校验上下文），在条件不满足时抛出校验错误，并构造模型实例验证校验器按预期工作。

## Objective

实现模型级校验并正确读取校验信息与上下文
## Applicable Signals

- 校验规则涉及两个及以上字段的相互依赖
- 校验需要读取已校验字段数据（data）
- 校验需要读取外部传入的校验上下文（context）

## Contraindications

- 仅涉及单字段简单约束时，应使用字段级校验器而非模型级校验器

## Intervention Moves

- 选择模型级校验器模式（annotated 或 decorator）
- 在校验器中通过 ValidationInfo 读取 data 与 context
- 在条件不满足时抛出校验错误
- 运行模型验证校验器行为

## Workflow Steps

- 判断校验是否确需跨字段依赖或访问校验上下文
- 在模型中定义模型级校验器（annotated 或 decorator 模式）
- 在校验器中通过 ValidationInfo 读取所需字段数据（data）与上下文（context）
- 当校验条件不满足时抛出校验错误
- 构造模型实例验证校验器按预期工作

## Constraints

- 仅在跨字段依赖或需要访问 ValidationInfo 数据/上下文时使用模型级校验器
- 单字段简单约束应使用字段级校验器

## Cautions

- 校验器执行顺序会影响可读取的字段数据，需注意依赖字段的校验先后

## Output Contract

- 可运行的模型校验器，正确使用 ValidationInfo 数据与上下文，并在条件不满足时产生校验错误

## 子技能目录
- [Pydantic 模型级 before/after 校验器实现](通用技能领域/Family技能/未分类技能/微技能/Pydantic 模型级 before-after 校验器实现/SKILL.md) ｜ 适用：使用 model_validator 在 before/after 阶段对整体模型输入执行校验，处理原始输入类型并支持提前终止校验，适用于跨字段或模型级约束。
- [验证错误抛出与 ValidationInfo 使用](通用技能领域/Family技能/未分类技能/微技能/验证错误抛出与 ValidationInfo 使用/SKILL.md) ｜ 适用：在 Pydantic 验证器中通过抛出验证错误报告校验失败，并使用 ValidationInfo 读取字段数据与校验上下文。适用于需要自定义错误信息或访问校验上下文的场景。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `Pydantic 模型级 before/after 校验器实现` 时，优先调用它。 线索：需要跨字段或整体模型约束校验, 需要在 Pydantic 处理前后介入校验, pydantic, model_validator, 模型级校验
- 当目标、阶段或方法更接近 `验证错误抛出与 ValidationInfo 使用` 时，优先调用它。 线索：需要自定义校验失败信息, 验证器需要访问 ValidationInfo 数据或上下文, 需要在验证器中读取同模型其他字段的已校验值, pydantic, validator

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 校验逻辑依赖多个字段
- 需要访问 ValidationInfo 的 data
- 需要访问 ValidationInfo 的 context
- 需要实现模型级而非字段级校验
