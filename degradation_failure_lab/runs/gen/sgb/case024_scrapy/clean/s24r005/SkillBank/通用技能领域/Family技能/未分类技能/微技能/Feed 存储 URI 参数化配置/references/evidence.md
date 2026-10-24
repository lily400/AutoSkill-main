# Feed 存储 URI 参数化配置 Evidence

- family: 未分类技能
- skill_id: 7c6e4142-008c-527e-97cd-842ef4911d30
- support_count: 1

## Evidence 1

- support_id: c0747914-b67b-51ab-98ed-14261db6d75a
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 3720:4115
- confidence: 0.70
- quote: Here are some examples to illustrate:

- Store in FTP using one directory per spider:
  - `ftp://user:password@ftp.example.com/scraping/feeds/%(name)s/%(time)s.json`
- Store in S3 using one directory per spider:
  - `s3://mybucket/scraping/feeds/%(name)s/%(time)s.json`

[Spider arguments](spiders.html#spiderargs) become spider attributes, hence
they can also be used as storage URI parameters.
