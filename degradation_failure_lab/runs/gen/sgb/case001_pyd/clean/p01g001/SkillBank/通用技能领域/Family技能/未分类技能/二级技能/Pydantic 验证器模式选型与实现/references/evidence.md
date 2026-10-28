# Pydantic 验证器模式选型与实现 Evidence

- family: 未分类技能
- skill_id: 0166b7ef-ec54-5e0c-9bd2-086b92fc3430
- support_count: 1

## Evidence 1

- support_id: 9b6f3d1a-174b-5fec-aa83-6b70de715354
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 13640:13966
- confidence: 0.70
- quote: **Three** different types of model validators can be used:

- ***After* validators**: run after the whole model has been validated. As such, they are defined as
 *instance* methods and can be seen as post-initialization hooks. Important note: the validated instance
 should be returned.

```
from typing_extensions import Self
