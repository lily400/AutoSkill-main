# FTP Feed 存储配置 Evidence

- family: 未分类技能
- skill_id: 563ce5c2-6cd7-5937-8918-787b1fc2b465
- support_count: 1

## Evidence 1

- support_id: b7eaef5d-d216-5dfd-8d34-2b2fb167806b
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 4549:4967
- confidence: 0.80
- quote: FTP
The feeds are stored in a FTP server.

- URI scheme: `ftp`
- Example URI: `ftp://user:pass@ftp.example.com/path/to/export.csv`
- Required external libraries: none

FTP supports two different connection modes: [active or passive](https://stackoverflow.com/a/1699163). Scrapy uses the passive connection
mode by default. To use the active connection mode instead, set the
`FEED_STORAGE_FTP_ACTIVE` setting to `True`.
