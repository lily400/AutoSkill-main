# 验证错误抛出与 ValidationInfo 使用 Evidence

- family: 未分类技能
- skill_id: 9ac11db1-8466-56be-bf2b-9bed656dacd8
- support_count: 1

## Evidence 1

- support_id: 2e8ea401-616d-581c-a467-677d700210ff
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 13640:13966
- confidence: 0.65
- quote: **Three** different types of model validators can be used:

- ***After* validators**: run after the whole model has been validated. As such, they are defined as
 *instance* methods and can be seen as post-initialization hooks. Important note: the validated instance
 should be returned.

```
from typing_extensions import Self
