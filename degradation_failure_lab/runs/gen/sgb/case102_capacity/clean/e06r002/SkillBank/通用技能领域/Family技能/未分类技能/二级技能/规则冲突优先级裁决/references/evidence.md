# 规则冲突优先级裁决 Evidence

- family: 未分类技能
- skill_id: 0a34413e-f719-56fc-b923-223ce3f98e44
- support_count: 2

## Evidence 1

- support_id: ff334183-65e6-53c1-aabf-59543ca13ee3
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 34009:34436
- confidence: 0.85
- quote: R49. Secondary objectives may include minimizing total distance traveled or minimizing the number of vehicles used, but these only apply when explicitly specified.

13. Rule Conflicts and Undefined Behavior

R50. If two rules appear to conflict, rules with more specific scope override more general rules. For example, a scenario-specific rule about a single edge overrides this document’s generic capacity rule for that edge.

## Evidence 2

- support_id: a3ee0759-1ee6-5e75-a5db-bc6ce149d761
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 12824:13374
- confidence: 0.85
- quote: R49. Secondary objectives may include minimizing total distance traveled or minimizing the number of vehicles used, but these only apply when explicitly specified.

13. Rule Conflicts and Undefined Behavior
R50. If two rules appear to conflict, rules with more specific scope override more general rules. For example, a scenario-specific rule about a single edge overrides this document’s generic capacity rule for that edge.

R51. If behavior is not specified, it is considered undefined. Controllers must not assume any behavior in undefined cases.
