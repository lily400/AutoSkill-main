# Wrap 校验器前后处理与提前终止 Evidence

- family: 未分类技能
- skill_id: 15220ea2-0440-5d9e-ab4b-5d2ecf1b59ce
- support_count: 1

## Evidence 1

- support_id: db11b3c0-2994-554a-865c-f32af3a3ec17
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 8706:9552
- confidence: 0.55
- quote: print(Model(number=4))
#> number=8
print(Model(number='invalid'))  # (1)!
#> number='invalid'
```

1. Although `'invalid'` shouldn't validate against the `int` type, Pydantic accepts the input.
- ***Wrap* validators**: are the most flexible of all. You can run code before or after Pydantic and other validators
 process the input, or you can terminate validation immediately, either by returning the value early or by raising an
 error.

Annotated patternDecorator
