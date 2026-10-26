# 下载器中间件激活与排序配置 Evidence

- family: 未分类技能
- skill_id: 76394f52-1f81-5c91-8ae3-fd51b942c5e1
- support_count: 2

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

## Evidence 2

- support_id: dade6cef-de64-56dd-8e02-786b2cc69422
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 10351:12510
- confidence: 0.75
- quote: **dont_filter*: [bool](https://docs.python.org/3/library/functions.html#bool)***

Whether this request may be filtered out by [components](components.html#topics-components) that support filtering out requests (`False`,
default), or those components should not filter out this request
(`True`).

This attribute is commonly set to `True` to prevent duplicate
requests from being filtered out.

When defining the start URLs of a spider through
[`start_urls`](spiders.html#scrapy.Spider.start_urls), this attribute is enabled by
default. See [`start()`](spiders.html#scrapy.Spider.start).

**attributes*: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]**= ('url', 'callback', 'method', 'headers', 'body', 'cookies', 'meta', 'encoding', 'priority', 'dont_filter', 'errback', 'flags', 'cb_kwargs')***

A tuple of [`str`](https://docs.python.org/3/library/stdtypes.html#str) objects containing the name of all public
attributes of the class that are also keyword parameters of the
`__init__()` method.

Currently used by `Request.replace()`, `Request.to_dict()` and
`request_from_dict()`.

**copy()[[source]](../_modules/scrapy/http/request.html#Request.copy)**

Return a new Request which is a copy of this Request. See also:
Passing additional data to callback functions.

**replace([*url*, *method*, *headers*, *body*, *cookies*, *meta*, *flags*, *encoding*, *priority*, *dont_filter*, *callback*, *errback*, *cb_kwargs*])[[source]](../_modules/scrapy/http/request.html#Request.replace)**

Return a Request object with the same members, except for those members
given new values by whichever keyword arguments are specified. The
`cb_kwargs` and `meta` attributes are shallow
copied by default (unless new values are given as arguments). See also
Passing additional data to callback functions.

***classmethod*from_curl(*curl_command: [str](https://docs.python.org/3/library/stdtypes.html#str)*, *ignore_unknown_options: [bool](https://docs.python.org/3/library/functions.html#bool) = True*, ***kwargs: Any*) → Self[[source]](../_modules/scrapy/http/request.html#Request.from_curl)**
