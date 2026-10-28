# 可调用判别器联合类型声明 Evidence

- family: 未分类技能
- skill_id: 2b84f18e-800d-523e-a397-ef2f1358157d
- support_count: 1

## Evidence 1

- support_id: 27887876-ec3d-5f4c-86f5-71c9f69cb187
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 19227:19690
- confidence: 0.80
- quote: For callable `Discriminator`s:

```
some_field: Union[...] = Field(discriminator=Discriminator(...))
some_field: Annotated[Union[...], Discriminator(...)]
some_field: Annotated[Union[...], Field(discriminator=Discriminator(...))]
```

Discriminated unions cannot be used with only a single variant, such as `Union[Cat]`.

Python changes `Union[T]` into `T` at interpretation time, so it is not possible for `pydantic` to
distinguish fields of `Union[T]` from `T`.
