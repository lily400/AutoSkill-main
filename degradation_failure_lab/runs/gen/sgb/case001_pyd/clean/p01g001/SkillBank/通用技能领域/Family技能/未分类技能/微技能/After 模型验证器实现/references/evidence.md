# After 模型验证器实现 Evidence

- family: 未分类技能
- skill_id: 1047b6b8-7e89-5dd1-8eb4-08e24cb05a08
- support_count: 1

## Evidence 1

- support_id: 59ab0904-85ac-559f-b937-5100c9721a70
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 13640:13966
- confidence: 0.75
- quote: **Three** different types of model validators can be used:

- ***After* validators**: run after the whole model has been validated. As such, they are defined as
 *instance* methods and can be seen as post-initialization hooks. Important note: the validated instance
 should be returned.

```
from typing_extensions import Self
