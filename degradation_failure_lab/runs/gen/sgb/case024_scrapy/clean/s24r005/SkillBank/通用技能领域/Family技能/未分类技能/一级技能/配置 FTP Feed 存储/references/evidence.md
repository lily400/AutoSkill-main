# 配置 FTP Feed 存储 Evidence

- family: 未分类技能
- skill_id: 34248732-50cd-510d-b3ed-a71e8ef808d1
- support_count: 1

## Evidence 1

- support_id: 1e069413-242e-5182-8552-0b936cb2212e
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 4549:4967
- confidence: 0.70
- quote: FTP
The feeds are stored in a FTP server.

- URI scheme: `ftp`
- Example URI: `ftp://user:pass@ftp.example.com/path/to/export.csv`
- Required external libraries: none

FTP supports two different connection modes: [active or passive](https://stackoverflow.com/a/1699163). Scrapy uses the passive connection
mode by default. To use the active connection mode instead, set the
`FEED_STORAGE_FTP_ACTIVE` setting to `True`.
