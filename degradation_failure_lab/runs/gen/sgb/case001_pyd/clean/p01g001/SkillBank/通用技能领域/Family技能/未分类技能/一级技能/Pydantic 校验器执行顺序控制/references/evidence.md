# Pydantic 校验器执行顺序控制 Evidence

- family: 未分类技能
- skill_id: 3f2908c2-5e45-53d0-8741-3e78c412be38
- support_count: 1

## Evidence 1

- support_id: 7346aadc-b010-5048-980e-caf4c4da45d8
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 5464:6382
- confidence: 0.75
- quote: print(Model(numbers=2))
#> numbers=[2]
try:
    Model(numbers='str')
except ValidationError as err:
    print(err)  # (3)!
    """
    1 validation error for Model
    numbers.0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='str', input_type=str]
    """
```

1. Notice the use of [`Any`](https://docs.python.org/3/library/typing.html#typing.Any) as a type hint for `value`. *Before* validators take the raw input, which
 can be anything.
2. Note that you might want to check for other sequence types (such as tuples) that would normally successfully
 validate against the `list` type. *Before* validators give you more flexibility, but you have to account for
 every possible case.
3. Pydantic still performs validation against the `int` type, no matter if our `ensure_list` validator
 did operations on the original input type.

```
from typing import Any
