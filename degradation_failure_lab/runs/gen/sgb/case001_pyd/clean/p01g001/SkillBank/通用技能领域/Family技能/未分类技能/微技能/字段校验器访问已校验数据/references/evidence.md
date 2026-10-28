# 字段校验器访问已校验数据 Evidence

- family: 未分类技能
- skill_id: faa883e0-e41a-5e19-868e-c3c8400b4db4
- support_count: 1

## Evidence 1

- support_id: 05fba65e-8e32-5890-9b0e-cd585a29238e
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 18138:19108
- confidence: 0.75
- quote: Validation info
Both the field and model validators callables (in all modes) can optionally take an extra
[`ValidationInfo`](../../api/pydantic_core_schema/#pydantic_core.core_schema.ValidationInfo) argument, providing useful extra information, such as:

- already validated data
- user defined context
- the current [validation mode](../models/#validating-data): either `'python'`, `'json'` or `'strings'` (see the [`mode`](../../api/pydantic_core_schema/#pydantic_core.core_schema.ValidationInfo.mode) property)
- the current field name, if using a field validator (see the [`field_name`](../../api/pydantic_core_schema/#pydantic_core.core_schema.ValidationInfo.field_name) property).

Validation data
For field validators, the already validated data can be accessed using the [`data`](../../api/pydantic_core_schema/#pydantic_core.core_schema.ValidationInfo.data)
property. Here is an example than can be used as an alternative to the *after* model validator
example:
