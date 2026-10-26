# 启用并排序 Spider 中间件 Evidence

- family: 未分类技能
- skill_id: 206b95c3-ad84-55ae-acea-c8787d0858fb
- support_count: 1

## Evidence 1

- support_id: 49e02c97-0154-5297-830e-d147be7bd221
- relation_type: support
- document: input004\spider-middleware.md
- doc_id: 0846bc81-9f63-5a03-baf2-464e92f3e728
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input004\spider-middleware.md
- section: Spider Middleware
- span: 196:4319
- confidence: 0.85
- quote: The spider middleware is a framework of hooks into Scrapy’s spider processing
mechanism where you can plug custom functionality to process the responses that
are sent to [Spiders](spiders.html#topics-spiders) for processing and to process the requests
and items that are generated from spiders.

Activating a spider middleware
To activate a spider middleware component, add it to the
[`SPIDER_MIDDLEWARES`](settings.html#std-setting-SPIDER_MIDDLEWARES) setting, which is a dict whose keys are the
middleware class path and their values are the middleware orders.

Here’s an example:

```
SPIDER_MIDDLEWARES = {
    "myproject.middlewares.CustomSpiderMiddleware": 543,
}
```

```
SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.referer.RefererMiddleware": None,
    "myproject.middlewares.CustomRefererSpiderMiddleware": 700,
}
```

Finally, keep in mind that some middlewares may need to be enabled through a
particular setting. See each middleware documentation for more info.

Writing your own spider middleware
Each spider middleware is a [component](components.html#topics-components) that defines
one or more of these methods:

***class*scrapy.spidermiddlewares.SpiderMiddleware**

***async*process_start(*start: AsyncIterator[Any]*, */*) → AsyncIterator[Any]**

Iterate over the output of [`start()`](spiders.html#scrapy.Spider.start) or that
of the `process_start()` method of an earlier spider middleware,
overriding it. For example:

```
async def process_start(self, start):
    async for item_or_request in start:
        yield item_or_request
```

You may yield the same type of objects as [`start()`](spiders.html#scrapy.Spider.start).

To write spider middlewares that work on Scrapy versions lower than
2.13, define also a synchronous `process_start_requests()` method
that returns an iterable. For example:

```
def process_start_requests(self, start, spider):
    yield from start
```

**process_spider_input(*response*)**

This method is called for each response that goes through the spider
middleware and into the spider, for processing.

`process_spider_input()` should return `None` or raise an
exception.

If it returns `None`, Scrapy will continue processing this response,
executing all other middlewares until, finally, the response is handed
to the spider for processing.

**Parameters:**
