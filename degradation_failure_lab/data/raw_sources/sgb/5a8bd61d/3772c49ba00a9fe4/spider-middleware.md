# Spider Middleware — Scrapy 2.14.1 documentation

- Spider Middleware
- [Edit on GitHub](https://github.com/scrapy/scrapy/blob/master/docs/topics/spider-middleware.rst)

---

# Spider Middleware

The spider middleware is a framework of hooks into Scrapy’s spider processing
mechanism where you can plug custom functionality to process the responses that
are sent to [Spiders](spiders.html#topics-spiders) for processing and to process the requests
and items that are generated from spiders.

## Activating a spider middleware

To activate a spider middleware component, add it to the
[`SPIDER_MIDDLEWARES`](settings.html#std-setting-SPIDER_MIDDLEWARES) setting, which is a dict whose keys are the
middleware class path and their values are the middleware orders.

Here’s an example:

```
SPIDER_MIDDLEWARES = {
    "myproject.middlewares.CustomSpiderMiddleware": 543,
}
```

The [`SPIDER_MIDDLEWARES`](settings.html#std-setting-SPIDER_MIDDLEWARES) setting is merged with the
[`SPIDER_MIDDLEWARES_BASE`](settings.html#std-setting-SPIDER_MIDDLEWARES_BASE) setting defined in Scrapy (and not meant to
be overridden) and then sorted by order to get the final sorted list of enabled
middlewares: the first middleware is the one closer to the engine and the last
is the one closer to the spider. In other words,
the `process_spider_input()`
method of each middleware will be invoked in increasing
middleware order (100, 200, 300, …), and the
`process_spider_output()` method
of each middleware will be invoked in decreasing order.

To decide which order to assign to your middleware see the
[`SPIDER_MIDDLEWARES_BASE`](settings.html#std-setting-SPIDER_MIDDLEWARES_BASE) setting and pick a value according to where
you want to insert the middleware. The order does matter because each
middleware performs a different action and your middleware could depend on some
previous (or subsequent) middleware being applied.

If you want to disable a builtin middleware (the ones defined in
[`SPIDER_MIDDLEWARES_BASE`](settings.html#std-setting-SPIDER_MIDDLEWARES_BASE), and enabled by default) you must define it
in your project [`SPIDER_MIDDLEWARES`](settings.html#std-setting-SPIDER_MIDDLEWARES) setting and assign `None` as its
value. For example, if you want to disable the off-site middleware:

```
SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.referer.RefererMiddleware": None,
    "myproject.middlewares.CustomRefererSpiderMiddleware": 700,
}
```

Finally, keep in mind that some middlewares may need to be enabled through a
particular setting. See each middleware documentation for more info.

## Writing your own spider middleware

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

If it raises an exception, Scrapy won’t bother calling any other spider
middleware `process_spider_input()` and will call the request
errback if there is one, otherwise it will start the `process_spider_exception()`
chain. The output of the errback is chained back in the other
direction for `process_spider_output()` to process it, or
`process_spider_exception()` if it raised an exception.

**Parameters:**

**response** ([`Response`](request-response.html#scrapy.http.Response) object) – the response being processed

**process_spider_output(*response*, *result*)**

This method is called with the results returned from the Spider, after
it has processed the response.

`process_spider_output()` must return an iterable of
[`Request`](request-response.html#scrapy.Request) objects and [item objects](items.html#topics-items).

Consider defining this method as an [asynchronous generator](https://docs.python.org/3/glossary.html#term-asynchronous-generator),
which will be a requirement in a future version of Scrapy. However, if
you plan on sharing your spider middleware with other people, consider
either [enforcing Scrapy 2.7](components.html#enforce-component-requirements)
as a minimum requirement of your spider middleware, or [making
your spider middleware universal](coroutines.html#universal-spider-middleware) so that
it works with Scrapy versions earlier than Scrapy 2.7.

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

### Base class for custom spider middlewares

Scrapy provides a base class for custom spider middlewares. It’s not required
to use it but it can help with simplifying middleware implementations and
reducing the amount of boilerplate code in [universal middlewares](coroutines.html#universal-spider-middleware).

***class*scrapy.spidermiddlewares.base.BaseSpiderMiddleware(*crawler: [Crawler](api.html#scrapy.crawler.Crawler)*)[[source]](../_modules/scrapy/spidermiddlewares/base.html#BaseSpiderMiddleware)**

Optional base class for spider middlewares.

Added in version 2.13.

This class provides helper methods for asynchronous
`process_spider_output()` and `process_start()` methods. Middlewares
that don’t have either of these methods don’t need to use this class.

You can override the
`get_processed_request()`
method to add processing code for requests and the
`get_processed_item()`
method to add processing code for items. These methods take a single
request or item from the spider output iterable and return a request or
item (the same or a new one), or `None` to remove this request or item
from the processing.

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

**get_processed_request(*request: [Request](request-response.html#scrapy.Request)*, *response: [Response](request-response.html#scrapy.http.Response) | [None](https://docs.python.org/3/library/constants.html#None)*) → [Request](request-response.html#scrapy.Request) | [None](https://docs.python.org/3/library/constants.html#None)[[source]](../_modules/scrapy/spidermiddlewares/base.html#BaseSpiderMiddleware.get_processed_request)**

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

## Built-in spider middleware reference

This page describes all spider middleware components that come with Scrapy. For
information on how to use them and how to write your own spider middleware, see
the spider middleware usage guide.

For a list of the components enabled by default (and their orders) see the
[`SPIDER_MIDDLEWARES_BASE`](settings.html#std-setting-SPIDER_MIDDLEWARES_BASE) setting.

### DepthMiddleware

***class*scrapy.spidermiddlewares.depth.DepthMiddleware[[source]](../_modules/scrapy/spidermiddlewares/depth.html#DepthMiddleware)**

DepthMiddleware is used for tracking the depth of each Request inside the
site being scraped. It works by setting `request.meta['depth'] = 0` whenever
there is no value previously set (usually just the first Request) and
incrementing it by 1 otherwise.

It can be used to limit the maximum depth to scrape, control Request
priority based on their depth, and things like that.

The `DepthMiddleware` can be configured through the following
settings (see the settings documentation for more info):

> - [`DEPTH_LIMIT`](settings.html#std-setting-DEPTH_LIMIT) - The maximum depth that will be allowed to
> crawl for any site. If zero, no limit will be imposed.
> - [`DEPTH_STATS_VERBOSE`](settings.html#std-setting-DEPTH_STATS_VERBOSE) - Whether to collect the number of
> requests for each depth.
> - [`DEPTH_PRIORITY`](settings.html#std-setting-DEPTH_PRIORITY) - Whether to prioritize the requests based on
> their depth.

### HttpErrorMiddleware

***class*scrapy.spidermiddlewares.httperror.HttpErrorMiddleware[[source]](../_modules/scrapy/spidermiddlewares/httperror.html#HttpErrorMiddleware)**

Filter out unsuccessful (erroneous) HTTP responses so that spiders don’t
have to deal with them, which (most of the time) imposes an overhead,
consumes more resources, and makes the spider logic more complex.

According to the [HTTP standard](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html), successful responses are those whose
status codes are in the 200-300 range.

If you still want to process response codes outside that range, you can
specify which response codes the spider is able to handle using the
`handle_httpstatus_list` spider attribute or
`HTTPERROR_ALLOWED_CODES` setting.

For example, if you want your spider to handle 404 responses you can do
this:

```
from scrapy.spiders import CrawlSpider

class MySpider(CrawlSpider):
    handle_httpstatus_list = [404]
```

The `handle_httpstatus_list` key of [`Request.meta`](request-response.html#scrapy.Request.meta) can also be used to specify which response codes to
allow on a per-request basis. You can also set the meta key `handle_httpstatus_all`
to `True` if you want to allow any response code for a request, and `False` to
disable the effects of the `handle_httpstatus_all` key.

Keep in mind, however, that it’s usually a bad idea to handle non-200
responses, unless you really know what you’re doing.

For more information see: [HTTP Status Code Definitions](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html).

#### HttpErrorMiddleware settings

##### HTTPERROR_ALLOWED_CODES

Default: `[]`

Pass all responses with non-200 status codes contained in this list.

##### HTTPERROR_ALLOW_ALL

Default: `False`

Pass all responses, regardless of its status code.

### RefererMiddleware

***class*scrapy.spidermiddlewares.referer.RefererMiddleware[[source]](../_modules/scrapy/spidermiddlewares/referer.html#RefererMiddleware)**

Populates Request `Referer` header, based on the URL of the Response which
generated it.

#### RefererMiddleware settings

##### REFERER_ENABLED

Default: `True`

Whether to enable referer middleware.

##### REFERRER_POLICY

Default: `'scrapy.spidermiddlewares.referer.DefaultReferrerPolicy'`

[Referrer Policy](https://www.w3.org/TR/referrer-policy) to apply when populating Request “Referer” header.

You can also set the Referrer Policy per request,
using the special `"referrer_policy"` [Request.meta](request-response.html#topics-request-meta) key,
with the same acceptable values as for the `REFERRER_POLICY` setting.

###### Acceptable values for REFERRER_POLICY

- either a path to a `scrapy.spidermiddlewares.referer.ReferrerPolicy`
subclass — a custom policy or one of the built-in ones (see classes below),
- or one or more comma-separated standard W3C-defined string values,
- or the special `"scrapy-default"`.

| String value | Class name (as a string) |
| --- | --- |
| `"scrapy-default"` (default) | `scrapy.spidermiddlewares.referer.DefaultReferrerPolicy` |
| [“no-referrer”](https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer) | `scrapy.spidermiddlewares.referer.NoReferrerPolicy` |
| [“no-referrer-when-downgrade”](https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer-when-downgrade) | `scrapy.spidermiddlewares.referer.NoReferrerWhenDowngradePolicy` |
| [“same-origin”](https://www.w3.org/TR/referrer-policy/#referrer-policy-same-origin) | `scrapy.spidermiddlewares.referer.SameOriginPolicy` |
| [“origin”](https://www.w3.org/TR/referrer-policy/#referrer-policy-origin) | `scrapy.spidermiddlewares.referer.OriginPolicy` |
| [“strict-origin”](https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin) | `scrapy.spidermiddlewares.referer.StrictOriginPolicy` |
| [“origin-when-cross-origin”](https://www.w3.org/TR/referrer-policy/#referrer-policy-origin-when-cross-origin) | `scrapy.spidermiddlewares.referer.OriginWhenCrossOriginPolicy` |
| [“strict-origin-when-cross-origin”](https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin-when-cross-origin) | `scrapy.spidermiddlewares.referer.StrictOriginWhenCrossOriginPolicy` |
| [“unsafe-url”](https://www.w3.org/TR/referrer-policy/#referrer-policy-unsafe-url) | `scrapy.spidermiddlewares.referer.UnsafeUrlPolicy` |

***class*scrapy.spidermiddlewares.referer.ReferrerPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#ReferrerPolicy)**

Abstract base class for referrer policies.

***class*scrapy.spidermiddlewares.referer.DefaultReferrerPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#DefaultReferrerPolicy)**

A variant of “no-referrer-when-downgrade”,
with the addition that “Referer” is not sent if the parent request was
using `file://` or `s3://` scheme.

Scrapy’s default referrer policy — just like [“no-referrer-when-downgrade”](https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer-when-downgrade),
the W3C-recommended value for browsers — will send a non-empty
“Referer” header from any `http(s)://` to any `https://` URL,
even if the domain is different.

[“same-origin”](https://www.w3.org/TR/referrer-policy/#referrer-policy-same-origin) may be a better choice if you want to remove referrer
information for cross-domain requests.

***class*scrapy.spidermiddlewares.referer.NoReferrerPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#NoReferrerPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer](https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer)

The simplest policy is “no-referrer”, which specifies that no referrer information
is to be sent along with requests made from a particular request client to any origin.
The header will be omitted entirely.

***class*scrapy.spidermiddlewares.referer.NoReferrerWhenDowngradePolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#NoReferrerWhenDowngradePolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer-when-downgrade](https://www.w3.org/TR/referrer-policy/#referrer-policy-no-referrer-when-downgrade)

The “no-referrer-when-downgrade” policy sends a full URL along with requests
from a TLS-protected environment settings object to a potentially trustworthy URL,
and requests from clients which are not TLS-protected to any origin.

Requests from TLS-protected clients to non-potentially trustworthy URLs,
on the other hand, will contain no referrer information.
A Referer HTTP header will not be sent.

This is a user agent’s default behavior, if no policy is otherwise specified.

“no-referrer-when-downgrade” policy is the W3C-recommended default,
and is used by major web browsers.

However, it is NOT Scrapy’s default referrer policy (see `DefaultReferrerPolicy`).

***class*scrapy.spidermiddlewares.referer.SameOriginPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#SameOriginPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-same-origin](https://www.w3.org/TR/referrer-policy/#referrer-policy-same-origin)

The “same-origin” policy specifies that a full URL, stripped for use as a referrer,
is sent as referrer information when making same-origin requests from a particular request client.

Cross-origin requests, on the other hand, will contain no referrer information.
A Referer HTTP header will not be sent.

***class*scrapy.spidermiddlewares.referer.OriginPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#OriginPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-origin](https://www.w3.org/TR/referrer-policy/#referrer-policy-origin)

The “origin” policy specifies that only the ASCII serialization
of the origin of the request client is sent as referrer information
when making both same-origin requests and cross-origin requests
from a particular request client.

***class*scrapy.spidermiddlewares.referer.StrictOriginPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#StrictOriginPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin](https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin)

The “strict-origin” policy sends the ASCII serialization
of the origin of the request client when making requests:
- from a TLS-protected environment settings object to a potentially trustworthy URL, and
- from non-TLS-protected environment settings objects to any origin.

Requests from TLS-protected request clients to non- potentially trustworthy URLs,
on the other hand, will contain no referrer information.
A Referer HTTP header will not be sent.

***class*scrapy.spidermiddlewares.referer.OriginWhenCrossOriginPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#OriginWhenCrossOriginPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-origin-when-cross-origin](https://www.w3.org/TR/referrer-policy/#referrer-policy-origin-when-cross-origin)

The “origin-when-cross-origin” policy specifies that a full URL,
stripped for use as a referrer, is sent as referrer information
when making same-origin requests from a particular request client,
and only the ASCII serialization of the origin of the request client
is sent as referrer information when making cross-origin requests
from a particular request client.

***class*scrapy.spidermiddlewares.referer.StrictOriginWhenCrossOriginPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#StrictOriginWhenCrossOriginPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin-when-cross-origin](https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin-when-cross-origin)

The “strict-origin-when-cross-origin” policy specifies that a full URL,
stripped for use as a referrer, is sent as referrer information
when making same-origin requests from a particular request client,
and only the ASCII serialization of the origin of the request client
when making cross-origin requests:

- from a TLS-protected environment settings object to a potentially trustworthy URL, and
- from non-TLS-protected environment settings objects to any origin.

Requests from TLS-protected clients to non- potentially trustworthy URLs,
on the other hand, will contain no referrer information.
A Referer HTTP header will not be sent.

***class*scrapy.spidermiddlewares.referer.UnsafeUrlPolicy[[source]](../_modules/scrapy/spidermiddlewares/referer.html#UnsafeUrlPolicy)**

[https://www.w3.org/TR/referrer-policy/#referrer-policy-unsafe-url](https://www.w3.org/TR/referrer-policy/#referrer-policy-unsafe-url)

The “unsafe-url” policy specifies that a full URL, stripped for use as a referrer,
is sent along with both cross-origin requests
and same-origin requests made from a particular request client.

Note: The policy’s name doesn’t lie; it is unsafe.
This policy will leak origins and paths from TLS-protected resources
to insecure origins.
Carefully consider the impact of setting such a policy for potentially sensitive documents.

“unsafe-url” policy is NOT recommended.

### StartSpiderMiddleware

***class*scrapy.spidermiddlewares.start.StartSpiderMiddleware(*crawler: [Crawler](api.html#scrapy.crawler.Crawler)*)[[source]](../_modules/scrapy/spidermiddlewares/start.html#StartSpiderMiddleware)**

Set `is_start_request`.

#### is_start_request

[`meta`](request-response.html#scrapy.Request.meta) key that is set to `True` in [start
requests](spiders.html#start-requests), allowing you to tell start requests apart from
other requests, e.g. in [downloader middlewares](downloader-middleware.html#topics-downloader-middleware).

### UrlLengthMiddleware

***class*scrapy.spidermiddlewares.urllength.UrlLengthMiddleware[[source]](../_modules/scrapy/spidermiddlewares/urllength.html#UrlLengthMiddleware)**

Filters out requests with URLs longer than URLLENGTH_LIMIT

The `UrlLengthMiddleware` can be configured through the following
settings (see the settings documentation for more info):

> - [`URLLENGTH_LIMIT`](settings.html#std-setting-URLLENGTH_LIMIT) - The maximum URL length to allow for crawled URLs.
