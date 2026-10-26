# 下载器中间件 process_exception 异常处理分派 Evidence

- family: 未分类技能
- skill_id: 8229ccc7-e91d-5a88-8085-5887e69febd6
- support_count: 1

## Evidence 1

- support_id: 6744790f-99b3-50f4-8236-80c1fbd34b3a
- relation_type: support
- document: input002\downloader-middleware.md
- doc_id: d973e9fc-1e86-5c28-9def-81308171521e
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input002\downloader-middleware.md
- section: Downloader Middleware
- span: 4648:6896
- confidence: 0.85
- quote: `process_response()` should either: return a [`Response`](request-response.html#scrapy.http.Response)
object, return a [`Request`](request-response.html#scrapy.Request) object or
raise a [`IgnoreRequest`](exceptions.html#scrapy.exceptions.IgnoreRequest) exception.

If it returns a [`Response`](request-response.html#scrapy.http.Response) (it could be the same given
response, or a brand-new one), that response will continue to be processed
with the `process_response()` of the next middleware in the chain.

If it returns a [`Request`](request-response.html#scrapy.Request) object, the middleware chain is
halted and the returned request is rescheduled to be downloaded in the future.
This is the same behavior as if a request is returned from `process_request()`.

If it raises an [`IgnoreRequest`](exceptions.html#scrapy.exceptions.IgnoreRequest) exception, the errback
function of the request (`Request.errback`) is called. If no code handles the raised
exception, it is ignored and not logged (unlike other exceptions).

**Parameters:**

- **request** (is a [`Request`](request-response.html#scrapy.Request) object) – the request that originated the response
- **response** ([`Response`](request-response.html#scrapy.http.Response) object) – the response being processed

**process_exception(*request*, *exception*)**

Scrapy calls `process_exception()` when a [download handler](download-handlers.html#topics-download-handlers) or a `process_request()` (from a
downloader middleware) raises an exception (including an
[`IgnoreRequest`](exceptions.html#scrapy.exceptions.IgnoreRequest) exception).

`process_exception()` should return: either `None`,
a [`Response`](request-response.html#scrapy.http.Response) object, or a [`Request`](request-response.html#scrapy.Request) object.

If it returns `None`, Scrapy will continue processing this exception,
executing any other `process_exception()` methods of installed middleware,
until no middleware is left and the default exception handling kicks in.

If it returns a [`Response`](request-response.html#scrapy.http.Response) object, the `process_response()`
method chain of installed middleware is started, and Scrapy won’t bother calling
any other `process_exception()` methods of middleware.
