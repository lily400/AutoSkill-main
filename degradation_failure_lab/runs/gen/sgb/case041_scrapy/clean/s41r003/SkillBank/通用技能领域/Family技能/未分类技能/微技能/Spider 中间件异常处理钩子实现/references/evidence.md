# Spider 中间件异常处理钩子实现 Evidence

- family: 未分类技能
- skill_id: 20f141fe-1520-568d-a0ef-844224151e15
- support_count: 1

## Evidence 1

- support_id: 95142d24-e939-5852-9565-319303e04d3d
- relation_type: support
- document: input004\spider-middleware.md
- doc_id: 0846bc81-9f63-5a03-baf2-464e92f3e728
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input004\spider-middleware.md
- section: Spider Middleware
- span: 4321:7070
- confidence: 0.82
- quote: **response** ([`Response`](request-response.html#scrapy.http.Response) object) – the response being processed

**process_spider_output(*response*, *result*)**

This method is called with the results returned from the Spider, after
it has processed the response.

`process_spider_output()` must return an iterable of
[`Request`](request-response.html#scrapy.Request) objects and [item objects](items.html#topics-items).

**Parameters:**

- **response** ([`Response`](request-response.html#scrapy.http.Response) object) – the response which generated this output from the
spider
- **result** (an iterable of [`Request`](request-response.html#scrapy.Request) objects and
[item objects](items.html#topics-items)) – the result returned by the spider

***async*process_spider_output_async(*response*, *result*)**

If defined, this method must be an [asynchronous generator](https://docs.python.org/3/glossary.html#term-asynchronous-generator),
which will be called instead of `process_spider_output()` if
`result` is an [asynchronous iterable](https://docs.python.org/3/glossary.html#term-asynchronous-iterable).

**process_spider_exception(*response*, *exception*)**

This method is called when a spider or `process_spider_output()`
method (from a previous spider middleware) raises an exception.

`process_spider_exception()` should return either `None` or an
iterable of [`Request`](request-response.html#scrapy.Request) or [item](items.html#topics-items)
objects.

If it returns `None`, Scrapy will continue processing this exception,
executing any other `process_spider_exception()` in the following
middleware components, until no middleware components are left and the
exception reaches the engine (where it’s logged and discarded).

If it returns an iterable the `process_spider_output()` pipeline
kicks in, starting from the next spider middleware, and no other
`process_spider_exception()` will be called.

**Parameters:**

- **response** ([`Response`](request-response.html#scrapy.http.Response) object) – the response being processed when the exception was
raised
- **exception** ([`Exception`](https://docs.python.org/3/library/exceptions.html#Exception) object) – the exception raised
