# Scrapy 本地文件系统 Feed 导出配置 Evidence

- family: 未分类技能
- skill_id: 9b39f25d-2b76-5a1f-b683-d6e33df3493e
- support_count: 1

## Evidence 1

- support_id: 2388fb13-3683-50b4-a4c6-59004c3336a5
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 4117:4547
- confidence: 0.70
- quote: Local filesystem
The feeds are stored in the local filesystem.

- URI scheme: `file`
- Example URI: `file:///tmp/export.csv`
- Required external libraries: none

Note that for the local filesystem storage (only) you can omit the scheme if
you specify an absolute path like `/tmp/export.csv` (Unix systems only).
Alternatively you can also use a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path) object.
