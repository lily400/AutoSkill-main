# 预爬虫阶段设置配置 Evidence

- family: 未分类技能
- skill_id: b8eb69db-0a6a-5752-a165-55c26d41304c
- support_count: 1

## Evidence 1

- support_id: 5ab480d4-bc8e-5d60-beaf-8675dd26b01d
- relation_type: support
- document: input002\settings.md
- doc_id: 63a3e42d-b022-53bd-918f-7256d9f5f5a2
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case050_scrapy\clean\s50g001\inputs\input002\settings.md
- section: Settings
- span: 9344:9956
- confidence: 0.75
- quote: These settings are:

- `ASYNCIO_EVENT_LOOP` (not possible to set per-spider when using
[`AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess), see below)
- `DNS_RESOLVER` and settings used by the corresponding
component, e.g. `DNSCACHE_ENABLED`, `DNSCACHE_SIZE`
and `DNS_TIMEOUT` for the default one.
- `REACTOR_THREADPOOL_MAXSIZE`
- `TWISTED_REACTOR` (ignored when using
[`AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess), see below)

`ASYNCIO_EVENT_LOOP` and `TWISTED_REACTOR` are used upon
installing the reactor. The rest of the settings are applied when starting
the reactor.
