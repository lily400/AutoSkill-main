# 字段校验器显式返回值契约 Evidence

- family: 未分类技能
- skill_id: 2de78ee8-e350-5fb5-be7d-84c34b80f056
- support_count: 1

## Evidence 1

- support_id: 272d929a-d041-5fe9-848f-4dc9f3b6b3ef
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 2518:3041
- confidence: 0.82
- quote: try:
    Model(number=1)
except ValidationError as err:
    print(err)
    """
    1 validation error for Model
    number
      Value error, 1 is not an even number [type=value_error, input_value=1, input_type=int]
    """
```

1. Note that it is important to return the validated value.

Here is an example of a validator performing a validation check, and returning the value unchanged,
this time using the [`field_validator()`](../../api/functional_validators/#pydantic.functional_validators.field_validator) decorator.
