# 批量 Feed 输出文件命名占位符配置 Evidence

- family: 未分类技能
- skill_id: 73a590a4-6d1d-596f-b842-7ead4a57d901
- support_count: 1

## Evidence 1

- support_id: 0d3699e6-d229-51d6-a8b4-425d20c76871
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 21442:22112
- confidence: 0.85
- quote: When generating multiple output files, you must use at least one of the following
placeholders in the feed URI to indicate how the different output file names are
generated:

- `%(batch_time)s` - gets replaced by a timestamp when the feed is being created
(e.g. `2020-03-28T14-45-08.237134`)
- `%(batch_id)d` - gets replaced by the 1-based sequence number of the batch.

Use [printf-style string formatting](https://docs.python.org/3/library/stdtypes.html#old-string-formatting) to
alter the number format. For example, to make the batch ID a 5-digit
number by introducing leading zeroes as needed, use `%(batch_id)05d`
(e.g. `3` becomes `00003`, `123` becomes `00123`).
