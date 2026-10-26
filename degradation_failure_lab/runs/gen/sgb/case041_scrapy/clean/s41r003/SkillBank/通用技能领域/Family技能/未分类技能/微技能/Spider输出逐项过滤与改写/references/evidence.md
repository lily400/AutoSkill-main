# Spider输出逐项过滤与改写 Evidence

- family: 未分类技能
- skill_id: bfdf8b93-b24f-554c-938a-3cbb450e6e08
- support_count: 1

## Evidence 1

- support_id: ac30c3ad-d6b1-5786-aa71-a3b3bcfcb1f1
- relation_type: support
- document: input004\spider-middleware.md
- doc_id: 0846bc81-9f63-5a03-baf2-464e92f3e728
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input004\spider-middleware.md
- section: Spider Middleware
- span: 7072:9856
- confidence: 0.75
- quote: Base class for custom spider middlewares
Scrapy provides a base class for custom spider middlewares. It’s not required
to use it but it can help with simplifying middleware implementations and
reducing the amount of boilerplate code in [universal middlewares](coroutines.html#universal-spider-middleware).

***class*scrapy.spidermiddlewares.base.BaseSpiderMiddleware(*crawler: [Crawler](api.html#scrapy.crawler.Crawler)*)[[source]](../_modules/scrapy/spidermiddlewares/base.html#BaseSpiderMiddleware)**

Optional base class for spider middlewares.

Added in version 2.13.

This class provides helper methods for asynchronous
`process_spider_output()` and `process_start()` methods. Middlewares
that don’t have either of these methods don’t need to use this class.

**get_processed_item(*item: Any*, *response: [Response](request-response.html#scrapy.http.Response) | [None](https://docs.python.org/3/library/constants.html#None)*) → Any[[source]](../_modules/scrapy/spidermiddlewares/base.html#BaseSpiderMiddleware.get_processed_item)**

Return a processed item from the spider output.

This method is called with a single item from the start seeds or the
spider output. It should return the same or a different item, or
`None` to ignore it.

**Parameters:**

- **item** (*item object*) – the input item
- **response** ([`Response`](request-response.html#scrapy.http.Response) object or `None` for
start seeds) – the response being processed

**Returns:**

the processed item or `None`

Return a processed request from the spider output.

This method is called with a single request from the start seeds or the
spider output. It should return the same or a different request, or
`None` to ignore it.

**Parameters:**

- **request** ([`Request`](request-response.html#scrapy.Request) object) – the input request
- **response** ([`Response`](request-response.html#scrapy.http.Response) object or `None` for
start seeds) – the response being processed

**Returns:**

the processed request or `None`
