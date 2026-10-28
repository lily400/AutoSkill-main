# 字段校验器通配符与字段检查配置 Evidence

- family: 未分类技能
- skill_id: a30b25f4-b752-5564-afbd-e34563890155
- support_count: 1

## Evidence 1

- support_id: 7ba43fca-2305-5677-b2fd-820abf303937
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 12743:13320
- confidence: 0.80
- quote: Here are a couple additional notes about the decorator usage:

- If you want the validator to apply to all fields (including the ones defined in subclasses), you can pass
 `'*'` as the field name argument.
- By default, the decorator will ensure the provided field name(s) are defined on the model. If you want to
 disable this check during class creation, you can do so by passing `False` to the `check_fields` argument.
 This is useful when the field validator is defined on a base class, and the field is expected to exist on
 subclasses.

Model validators
API Documentation
