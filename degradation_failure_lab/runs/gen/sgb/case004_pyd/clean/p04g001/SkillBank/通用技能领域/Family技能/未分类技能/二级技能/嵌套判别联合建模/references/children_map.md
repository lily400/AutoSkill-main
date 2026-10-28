# 嵌套判别联合建模 子技能地图

## 子技能列表

- [字符串判别器字段声明](通用技能领域/Family技能/未分类技能/微技能/字符串判别器字段声明/SKILL.md) ｜ 微技能
  - 适用：在 Pydantic 模型定义中，为联合字段声明字符串判别器（str discriminator），使校验时按标签字段分派到对应联合成员。适用于联合成员可由单一字符串字段区分的场景，提供 Field(discriminator=...) 与 Annotated 两种声明语法。
  - 线索：联合字段的成员可通过单一字符串字段区分, 需要简洁的判别器声明语法, 希望用 Field(discriminator=...) 或 Annotated 模式声明判别器, pydantic, union
