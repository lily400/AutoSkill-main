# 联合类型精确度匹配评分 Evidence

- family: 未分类技能
- skill_id: 5faaba9c-de9a-593e-b531-bc2479e25d36
- support_count: 1

## Evidence 1

- support_id: 26404bea-5236-53ec-80a6-f3bba33795fc
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 6097:6574
- confidence: 0.80
- quote: For `exactness`, Pydantic scores a match of a union member into one of the following three groups (from highest score to lowest score):

- An exact type match, for example an `int` input to a `float | int` union validation is an exact type match for the `int` member
- Validation would have succeeded in [`strict` mode](../strict_mode/)
- Validation would have succeeded in lax mode

The union match which produced the highest exactness score will be considered the best match.
