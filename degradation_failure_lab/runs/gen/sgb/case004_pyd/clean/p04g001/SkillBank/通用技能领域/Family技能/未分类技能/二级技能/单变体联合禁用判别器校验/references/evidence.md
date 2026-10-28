# 单变体联合禁用判别器校验 Evidence

- family: 未分类技能
- skill_id: 3062a472-2dcc-54ef-b18a-b64a5b592a3d
- support_count: 1

## Evidence 1

- support_id: 10a2a4ca-e66f-5c69-b297-d93f5cca7421
- relation_type: constraint
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 19227:19690
- confidence: 0.85
- quote: For callable `Discriminator`s:

```
some_field: Union[...] = Field(discriminator=Discriminator(...))
some_field: Annotated[Union[...], Discriminator(...)]
some_field: Annotated[Union[...], Field(discriminator=Discriminator(...))]
```

Discriminated unions cannot be used with only a single variant, such as `Union[Cat]`.

Python changes `Union[T]` into `T` at interpretation time, so it is not possible for `pydantic` to
distinguish fields of `Union[T]` from `T`.
