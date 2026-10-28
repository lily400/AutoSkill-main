# Before 校验器安全实现 Evidence

- family: 未分类技能
- skill_id: 3697a04c-0fec-56b7-8448-1c44e3349e5e
- support_count: 1

## Evidence 1

- support_id: 1357f09a-b5c0-5879-b48e-cea9442a8913
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 4403:5097
- confidence: 0.65
- quote: print(Model(number=2))
#> number=4
```

1. `'after'` is the default mode for the decorator, and can be omitted.
- ***Before* validators**: run before Pydantic's internal parsing and validation (e.g. coercion of a `str` to an `int`).
 These are more flexible than *after* validators, but they also have to deal with the raw input, which
 in theory could be any arbitrary object. You should also avoid mutating the value directly if you are raising a
 validation error later in your validator function, as the mutated value may be passed to other
 validators if using [unions](../unions/).

The value returned from this callable is then validated against the provided type annotation by Pydantic.
