# 未分类技能 子技能地图

- parent: `未分类技能/总技能/SKILL.md`

## 子技能列表

1. [Callable Discriminator Returns None for Unknown Tags](通用技能领域/Family技能/未分类技能/微技能/Callable Discriminator Returns None for Unknown Tags/SKILL.md)
   - 层级：微技能
   - 类型：联合类型校验
   - 适用条件：When writing a callable Discriminator for a Pydantic union, explicitly return None for input types not covered by known branches so that a union_tag_not_found error is raised, and ensure the caller handles that error.
2. [TypeAdapter 校验纯联合类型](通用技能领域/Family技能/未分类技能/微技能/TypeAdapter 校验纯联合类型/SKILL.md)
   - 层级：微技能
   - 类型：联合类型校验
   - 适用条件：当校验目标仅为联合类型本身、且不希望继承 BaseModel 时，使用 TypeAdapter 包装联合类型并调用 validate_python 对数据执行校验，返回解析后的具体联合成员实例。
3. [Union 左到右短路匹配](通用技能领域/Family技能/未分类技能/微技能/Union 左到右短路匹配/SKILL.md)
   - 层级：微技能
   - 类型：union_validation
   - 适用条件：按 Left to Right Mode 依次尝试联合成员：精确类型匹配立即返回，否则取最左的 strict 匹配，再退到最左的 lax 匹配；全部失败时返回所有错误。用于成员顺序具有优先级语义、希望精确匹配时快速短路的场景。
4. [Union 智能模式成员选择](通用技能领域/Family技能/未分类技能/二级技能/Union 智能模式成员选择/SKILL.md)
   - 层级：二级技能
   - 类型：union_validation
   - 适用条件：按 Pydantic Smart Mode 规则在联合类型成员间选择最佳匹配：先按精确度评分，再以有效字段数决胜，平局用精确度打破。用于需要从多个候选模型/类型中确定唯一有效解析结果的场景。
5. [Union 智能模式最佳匹配选择](通用技能领域/Family技能/未分类技能/一级技能/Union 智能模式最佳匹配选择/SKILL.md)
   - 层级：一级技能
   - 类型：union_validation
   - 适用条件：在 Pydantic 校验 Union 类型时，依据有效字段设置数量与匹配精确度两项指标，判断输入应归属哪个候选成员类型。适用于需要解释或预测智能模式下成员选择结果的场景。
6. [Union 校验模式选择](通用技能领域/Family技能/未分类技能/微技能/Union 校验模式选择/SKILL.md)
   - 层级：微技能
   - 类型：类型校验配置
   - 适用条件：在 Pydantic 模型定义含 Union 字段时，根据输入歧义风险选择 union_mode（left_to_right 或 smart），避免宽松模式下数值字符串被意外匹配到 int 成员而非 str。
7. [判别联合校验](通用技能领域/Family技能/未分类技能/二级技能/判别联合校验/SKILL.md)
   - 层级：二级技能
   - 类型：union_validation
   - 适用条件：使用判别字段（含 str 判别器、可调用 Discriminator 及嵌套判别联合）将联合类型路由到唯一成员进行校验；适用于成员可由判别字段明确区分的场景。
8. [单变体联合禁用判别器校验](通用技能领域/Family技能/未分类技能/二级技能/单变体联合禁用判别器校验/SKILL.md)
   - 层级：二级技能
   - 类型：联合类型约束
   - 适用条件：在定义带判别器的联合类型字段前，检查联合是否仅含单一变体；若仅含一个成员，应改用非联合类型，因为 Python 会把 Union[T] 折叠为 T，导致判别器无法生效。
9. [可调用判别器联合类型声明](通用技能领域/Family技能/未分类技能/微技能/可调用判别器联合类型声明/SKILL.md)
   - 层级：微技能
   - 类型：模型字段声明
   - 适用条件：使用 Discriminator 对象配合 Field 或 Annotated 声明带判别器的联合类型字段，用于需要按判别字段路由到具体变体的模型定义。
10. [可调用判别器联合类型校验](通用技能领域/Family技能/未分类技能/二级技能/可调用判别器联合类型校验/SKILL.md)
   - 层级：二级技能
   - 类型：联合类型校验
   - 适用条件：使用 callable Discriminator 配合 Tag 注解，将联合类型按运行时类型分派到对应成员进行校验。适用于联合成员无法用单一字符串字段区分、需要自定义判别逻辑的场景。
11. [可调用判别器设计](通用技能领域/Family技能/未分类技能/微技能/可调用判别器设计/SKILL.md)
   - 层级：微技能
   - 类型：联合类型校验
   - 适用条件：当联合成员之间没有统一判别字段时，编写可调用 Discriminator 函数，使其同时处理 dict 与模型实例输入，从而在验证与序列化阶段都能正确判别，避免序列化警告或运行时错误。
12. [字符串判别器字段声明](通用技能领域/Family技能/未分类技能/微技能/字符串判别器字段声明/SKILL.md)
   - 层级：微技能
   - 类型：联合类型校验
   - 适用条件：在 Pydantic 模型定义中，为联合字段声明字符串判别器（str discriminator），使校验时按标签字段分派到对应联合成员。适用于联合成员可由单一字符串字段区分的场景，提供 Field(discriminator=...) 与 Annotated 两种声明语法。
13. [嵌套判别联合建模](通用技能领域/Family技能/未分类技能/二级技能/嵌套判别联合建模/SKILL.md)
   - 层级：二级技能
   - 类型：联合类型建模
   - 适用条件：通过嵌套 Annotated 类型组合多个判别器，为需要多级判别键的联合类型建模。当单一字段判别器不足以区分联合成员、需要按层级组合判别条件时使用。
14. [联合校验错误聚合](通用技能领域/Family技能/未分类技能/微技能/联合校验错误聚合/SKILL.md)
   - 层级：微技能
   - 类型：union_validation
   - 适用条件：当联合类型的所有成员均校验失败时，收集并返回全部成员的错误信息，而非仅返回首个错误，用于向调用方提供完整诊断反馈。
15. [联合类型从左到右校验顺序控制](通用技能领域/Family技能/未分类技能/一级技能/联合类型从左到右校验顺序控制/SKILL.md)
   - 层级：一级技能
   - 类型：联合类型校验
   - 适用条件：解释并预测 Pydantic 联合类型按声明顺序从左到右依次尝试成员校验的行为，以及 lax 模式下类型转换导致的意外匹配；用于调试或设计含混合成员（如 int/str）的联合字段。
16. [联合类型精确度匹配评分](通用技能领域/Family技能/未分类技能/一级技能/联合类型精确度匹配评分/SKILL.md)
   - 层级：一级技能
   - 类型：联合类型校验
   - 适用条件：说明 Pydantic 校验联合类型（Union）时如何按精确度对成员匹配打分并选出最佳匹配，用于判断或解释联合类型中哪个成员应胜出。
17. [自定义 Discriminator 错误信息](通用技能领域/Family技能/未分类技能/微技能/自定义 Discriminator 错误信息/SKILL.md)
   - 层级：微技能
   - 类型：校验错误处理
   - 适用条件：通过 Discriminator 构造器传入自定义错误类型、消息与上下文，使判别联合校验失败时输出更简洁可读的错误。适用于普通 Union 报错过于冗长、需要为判别失败提供清晰错误信息的场景。
