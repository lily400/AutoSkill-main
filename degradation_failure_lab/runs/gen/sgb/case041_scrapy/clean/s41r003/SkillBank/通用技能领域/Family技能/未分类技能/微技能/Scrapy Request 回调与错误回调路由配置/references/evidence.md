# Scrapy Request 回调与错误回调路由配置 Evidence

- family: 未分类技能
- skill_id: 65e1a9ed-69fb-5e8d-87f3-1bf759519ddd
- support_count: 1

## Evidence 1

- support_id: 1af53c44-b4c7-59ec-85f5-47ab11df8b85
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 6016:6791
- confidence: 0.70
- quote: In addition to an arbitrary callable, the following values are also
supported:

- `None` (default), which indicates that the
[`parse()`](spiders.html#scrapy.Spider.parse) method of the spider must be used.
- `NO_CALLBACK()`.

[`HttpErrorMiddleware`](spider-middleware.html#scrapy.spidermiddlewares.httperror.HttpErrorMiddleware)
raises exceptions for non-2xx responses by default, sending them
to the `errback` instead.
