# Pydantic 模型级校验器与 ValidationInfo 使用 子技能地图

## 子技能列表

- [Pydantic 模型级 before/after 校验器实现](通用技能领域/Family技能/未分类技能/微技能/Pydantic 模型级 before-after 校验器实现/SKILL.md) ｜ 微技能
  - 适用：使用 model_validator 在 before/after 阶段对整体模型输入执行校验，处理原始输入类型并支持提前终止校验，适用于跨字段或模型级约束。
  - 线索：需要跨字段或整体模型约束校验, 需要在 Pydantic 处理前后介入校验, pydantic, model_validator, 模型级校验
- [验证错误抛出与 ValidationInfo 使用](通用技能领域/Family技能/未分类技能/微技能/验证错误抛出与 ValidationInfo 使用/SKILL.md) ｜ 微技能
  - 适用：在 Pydantic 验证器中通过抛出验证错误报告校验失败，并使用 ValidationInfo 读取字段数据与校验上下文。适用于需要自定义错误信息或访问校验上下文的场景。
  - 线索：需要自定义校验失败信息, 验证器需要访问 ValidationInfo 数据或上下文, 需要在验证器中读取同模型其他字段的已校验值, pydantic, validator
