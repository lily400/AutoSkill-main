# 下载器中间件激活与排序配置 Evidence

- family: 未分类技能
- skill_id: 76394f52-1f81-5c91-8ae3-fd51b942c5e1
- support_count: 1

## Evidence 1

- support_id: e3ff6f02-f2ea-5a8d-81b1-f3e2467a1637
- relation_type: support
- document: input002\downloader-middleware.md
- doc_id: d973e9fc-1e86-5c28-9def-81308171521e
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input002\downloader-middleware.md
- section: Downloader Middleware
- span: 212:4646
- confidence: 0.85
- quote: The downloader middleware is a framework of hooks into Scrapy’s
request/response processing. It’s a light, low-level system for globally
altering Scrapy’s requests and responses.

Activating a downloader middleware
To activate a downloader middleware component, add it to the
[`DOWNLOADER_MIDDLEWARES`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES) setting, which is a dict whose keys are the
middleware class paths and their values are the middleware orders.

Here’s an example:

```
DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.CustomDownloaderMiddleware": 543,
}
```

```
DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.CustomDownloaderMiddleware": 543,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}
```

Finally, keep in mind that some middlewares may need to be enabled through a
particular setting. See each middleware documentation for more info.

Writing your own downloader middleware
Each downloader middleware is a [component](components.html#topics-components) that
defines one or more of these methods:

***class*scrapy.downloadermiddlewares.DownloaderMiddleware**

Any of the downloader middleware methods may be defined as a
coroutine function (`async def`).

**process_request(*request*)**

This method is called for each request that goes through the download
middleware.

`process_request()` should either: return `None`, return a
[`Response`](request-response.html#scrapy.http.Response) object, return a [`Request`](request-response.html#scrapy.Request)
object, or raise [`IgnoreRequest`](exceptions.html#scrapy.exceptions.IgnoreRequest).

If it returns `None`, Scrapy will continue processing this request, executing all
other middlewares until, finally, the appropriate downloader handler is called
the request performed (and its response downloaded).

If it returns a [`Request`](request-response.html#scrapy.Request) object, Scrapy will stop calling
`process_request()` methods and reschedule the returned request. Once the newly returned
request is performed, the appropriate middleware chain will be called on
the downloaded response.

**Parameters:**

**request** ([`Request`](request-response.html#scrapy.Request) object) – the request being processed

**process_response(*request*, *response*)**
