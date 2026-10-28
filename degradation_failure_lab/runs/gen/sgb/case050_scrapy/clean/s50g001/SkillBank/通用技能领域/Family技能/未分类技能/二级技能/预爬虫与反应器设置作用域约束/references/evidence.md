# 预爬虫与反应器设置作用域约束 Evidence

- family: 未分类技能
- skill_id: 8031195d-6143-5db6-828f-0b0ace06658a
- support_count: 1

## Evidence 1

- support_id: b15beeba-16ee-50a5-9878-e45c94466f03
- relation_type: constraint
- document: input002\settings.md
- doc_id: 63a3e42d-b022-53bd-918f-7256d9f5f5a2
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case050_scrapy\clean\s50g001\inputs\input002\settings.md
- section: Settings
- span: 1691:2115
- confidence: 0.65
- quote: ```
scrapy crawl myspider -s LOG_LEVEL=INFO -s LOG_FILE=scrapy.log
```

2. Spider settings
[Spiders](spiders.html#topics-spiders) can define their own settings that will take
precedence and override the project ones.

Pre-crawler settings cannot be defined
per spider, and reactor settings should not have
a different value per spider when [running multiple spiders in the
same process](practices.html#run-multiple-spiders).
