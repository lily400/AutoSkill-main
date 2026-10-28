# 联合校验错误聚合 Evidence

- family: 未分类技能
- skill_id: 4af0a451-fa59-56c0-b498-7eb801ffbcd2
- support_count: 1

## Evidence 1

- support_id: 4ab62e87-1ea5-5ae8-af9f-eeb711787c41
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 6669:7864
- confidence: 0.75
- quote: `BaseModel`, `dataclass`, and `TypedDict`All other data types

1. Union members are attempted left to right, with any successful matches scored into one of the three exactness categories described above,
with the valid fields set count also tallied.
2. After all members have been evaluated, the member with the highest "valid fields set" count is returned.
3. If there's a tie for the highest "valid fields set" count, the exactness score is used as a tiebreaker, and the member with the highest exactness score is returned.
4. If validation failed on all the members, return all the errors.

1. Union members are attempted left to right, with any successful matches scored into one of the three exactness categories described above.
  - If validation succeeds with an exact type match, that member is returned immediately and following members will not be attempted.
2. If validation succeeded on at least one member as a "strict" match, the leftmost of those "strict" matches is returned.
3. If validation succeeded on at least one member in "lax" mode, the leftmost match is returned.
4. Validation failed on all the members, return all the errors.

Python 3.9 and abovePython 3.10 and above
