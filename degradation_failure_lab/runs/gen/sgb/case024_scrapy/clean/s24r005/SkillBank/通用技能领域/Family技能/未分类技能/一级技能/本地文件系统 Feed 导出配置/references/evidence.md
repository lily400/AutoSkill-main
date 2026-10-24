# 本地文件系统 Feed 导出配置 Evidence

- family: 未分类技能
- skill_id: 27330983-d562-5773-89a1-69b722b401e1
- support_count: 1

## Evidence 1

- support_id: 33ddb24e-13cd-5d13-b474-c4e86340464b
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 4117:4547
- confidence: 0.80
- quote: Local filesystem
The feeds are stored in the local filesystem.

- URI scheme: `file`
- Example URI: `file:///tmp/export.csv`
- Required external libraries: none

Note that for the local filesystem storage (only) you can omit the scheme if
you specify an absolute path like `/tmp/export.csv` (Unix systems only).
Alternatively you can also use a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path) object.
