# 批量输出文件命名占位符配置 Evidence

- family: 未分类技能
- skill_id: e71e8e20-3578-5a41-a437-402eaeb0d5f6
- support_count: 1

## Evidence 1

- support_id: 4d254b70-a51b-53b8-906d-abc37f8e8926
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
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
