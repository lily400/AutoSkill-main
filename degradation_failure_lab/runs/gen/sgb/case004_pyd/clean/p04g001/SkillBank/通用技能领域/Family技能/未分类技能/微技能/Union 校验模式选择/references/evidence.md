# Union 校验模式选择 Evidence

- family: 未分类技能
- skill_id: faa3da58-bd45-51a5-93dd-11af9989f499
- support_count: 1

## Evidence 1

- support_id: c90f0711-9054-5f73-888c-2facb4f90c88
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 4191:4748
- confidence: 0.70
- quote: print(User(id=123))  # (1)
#> id=123
print(User(id='456'))  # (2)
#> id=456
```

1. As expected the input is validated against the `int` member and the result is as expected.
2. We're in lax mode and the numeric string `'123'` is valid as input to the first member of the union, `int`.
 Since that is tried first, we get the surprising result of `id` being an `int` instead of a `str`.

Smart Mode
Because of the potentially surprising results of `union_mode='left_to_right'`, in Pydantic >=2 the default mode for `Union` validation is `union_mode='smart'`.
