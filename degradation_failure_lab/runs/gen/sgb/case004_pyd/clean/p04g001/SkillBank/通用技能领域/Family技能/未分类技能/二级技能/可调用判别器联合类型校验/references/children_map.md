# 可调用判别器联合类型校验 子技能地图

## 子技能列表

- [Callable Discriminator Returns None for Unknown Tags](通用技能领域/Family技能/未分类技能/微技能/Callable Discriminator Returns None for Unknown Tags/SKILL.md) ｜ 微技能
  - 适用：When writing a callable Discriminator for a Pydantic union, explicitly return None for input types not covered by known branches so that a union_tag_not_found error is raised, and ensure the caller handles that error.
  - 线索：判别函数遇到未覆盖的输入类型, 需要明确未知判别值的失败行为, pydantic, union, discriminator
- [TypeAdapter 校验纯联合类型](通用技能领域/Family技能/未分类技能/微技能/TypeAdapter 校验纯联合类型/SKILL.md) ｜ 微技能
  - 适用：当校验目标仅为联合类型本身、且不希望继承 BaseModel 时，使用 TypeAdapter 包装联合类型并调用 validate_python 对数据执行校验，返回解析后的具体联合成员实例。
  - 线索：需要校验的数据目标仅为联合类型本身, 不希望为校验而继承 BaseModel, 需要对联合类型单独执行 validate_python, pydantic, union
- [可调用判别器设计](通用技能领域/Family技能/未分类技能/微技能/可调用判别器设计/SKILL.md) ｜ 微技能
  - 适用：当联合成员之间没有统一判别字段时，编写可调用 Discriminator 函数，使其同时处理 dict 与模型实例输入，从而在验证与序列化阶段都能正确判别，避免序列化警告或运行时错误。
  - 线索：联合成员之间没有单一统一判别字段, 需要在序列化阶段也能正确判别联合成员, 准备为 Union 配置 callable Discriminator, pydantic, union
