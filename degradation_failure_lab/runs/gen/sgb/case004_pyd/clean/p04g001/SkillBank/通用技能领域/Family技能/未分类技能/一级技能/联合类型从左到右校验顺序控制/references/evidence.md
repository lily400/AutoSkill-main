# 联合类型从左到右校验顺序控制 Evidence

- family: 未分类技能
- skill_id: 3df5f979-7629-5c57-8c24-746c21770722
- support_count: 1

## Evidence 1

- support_id: 146cba65-2453-529b-a463-e35a98f44942
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 3637:4111
- confidence: 0.75
- quote: print(User(id=123))  # (1)
#> id=123
print(User(id='456'))  # (2)
#> id=456
```

1. As expected the input is validated against the `int` member and the result is as expected.
2. We're in lax mode and the numeric string `'123'` is valid as input to the first member of the union, `int`.
 Since that is tried first, we get the surprising result of `id` being an `int` instead of a `str`.

Union with left to right - unexpected results
```
from pydantic import BaseModel, Field
