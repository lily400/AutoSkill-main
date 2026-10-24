# Downloader Middleware — Scrapy 2.14.1 documentation

- Downloader Middleware
- [Edit on GitHub](https://github.com/scrapy/scrapy/blob/master/docs/topics/downloader-middleware.rst)

---

# Downloader Middleware

The downloader middleware is a framework of hooks into Scrapy’s
request/response processing. It’s a light, low-level system for globally
altering Scrapy’s requests and responses.

## Activating a downloader middleware

To activate a downloader middleware component, add it to the
[`DOWNLOADER_MIDDLEWARES`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES) setting, which is a dict whose keys are the
middleware class paths and their values are the middleware orders.

Here’s an example:

```
DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.CustomDownloaderMiddleware": 543,
}
```

The [`DOWNLOADER_MIDDLEWARES`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES) setting is merged with the
[`DOWNLOADER_MIDDLEWARES_BASE`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES_BASE) setting defined in Scrapy (and not meant
to be overridden) and then sorted by order to get the final sorted list of
enabled middlewares: the first middleware is the one closer to the engine and
the last is the one closer to the downloader. In other words,
the `process_request()`
method of each middleware will be invoked in increasing
middleware order (100, 200, 300, …) and the `process_response()` method
of each middleware will be invoked in decreasing order.

To decide which order to assign to your middleware see the
[`DOWNLOADER_MIDDLEWARES_BASE`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES_BASE) setting and pick a value according to
where you want to insert the middleware. The order does matter because each
middleware performs a different action and your middleware could depend on some
previous (or subsequent) middleware being applied.

If you want to disable a built-in middleware (the ones defined in
[`DOWNLOADER_MIDDLEWARES_BASE`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES_BASE) and enabled by default) you must define it
in your project’s [`DOWNLOADER_MIDDLEWARES`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES) setting and assign `None`
as its value. For example, if you want to disable the user-agent middleware:

```
DOWNLOADER_MIDDLEWARES = {
    "myproject.middlewares.CustomDownloaderMiddleware": 543,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}
```

Finally, keep in mind that some middlewares may need to be enabled through a
particular setting. See each middleware documentation for more info.

## Writing your own downloader middleware

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

If it returns a [`Response`](request-response.html#scrapy.http.Response) object, Scrapy won’t bother
calling *any* other `process_request()` or `process_exception()` methods,
or the appropriate download function; it’ll return that response. The `process_response()`
methods of installed middleware is always called on every response.

If it returns a [`Request`](request-response.html#scrapy.Request) object, Scrapy will stop calling
`process_request()` methods and reschedule the returned request. Once the newly returned
request is performed, the appropriate middleware chain will be called on
the downloaded response.

If it raises an [`IgnoreRequest`](exceptions.html#scrapy.exceptions.IgnoreRequest) exception, the
`process_exception()` methods of installed downloader middleware will be called.
If none of them handle the exception, the errback function of the request
(`Request.errback`) is called. If no code handles the raised exception, it is
ignored and not logged (unlike other exceptions).

**Parameters:**

**request** ([`Request`](request-response.html#scrapy.Request) object) – the request being processed

**process_response(*request*, *response*)**

`process_response()` should either: return a [`Response`](request-response.html#scrapy.http.Response)
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

If it returns a [`Request`](request-response.html#scrapy.Request) object, the returned request is
rescheduled to be downloaded in the future. This stops the execution of
`process_exception()` methods of the middleware the same as returning a
response would.

**Parameters:**

- **request** (is a [`Request`](request-response.html#scrapy.Request) object) – the request that generated the exception
- **exception** (an `Exception` object) – the raised exception

## Built-in downloader middleware reference

This page describes all downloader middleware components that come with
Scrapy. For information on how to use them and how to write your own downloader
middleware, see the downloader middleware usage guide.

For a list of the components enabled by default (and their orders) see the
[`DOWNLOADER_MIDDLEWARES_BASE`](settings.html#std-setting-DOWNLOADER_MIDDLEWARES_BASE) setting.

### CookiesMiddleware

***class*scrapy.downloadermiddlewares.cookies.CookiesMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/cookies.html#CookiesMiddleware)**

This middleware enables working with sites that require cookies, such as
those that use sessions. It keeps track of cookies sent by web servers, and
sends them back on subsequent requests (from that spider), just like web
browsers do.

When non-UTF8 encoded byte sequences are passed to a
[`Request`](request-response.html#scrapy.Request), the `CookiesMiddleware` will log
a warning. Refer to [Advanced customization](logging.html#topics-logging-advanced-customization)
to customize the logging behaviour.

Cookies set via the `Cookie` header are not considered by the
CookiesMiddleware. If you need to set cookies for a request, use the
[`Request.cookies`](request-response.html#scrapy.Request) parameter. This is a known
current limitation that is being worked on.

The following settings can be used to configure the cookie middleware:

- `COOKIES_ENABLED`
- `COOKIES_DEBUG`

#### Multiple cookie sessions per spider

There is support for keeping multiple cookie sessions per spider by using the
`cookiejar` Request meta key. By default it uses a single cookie jar
(session), but you can pass an identifier to use different ones.

For example:

```
for i, url in enumerate(urls):
    yield scrapy.Request(url, meta={"cookiejar": i}, callback=self.parse_page)
```

Keep in mind that the `cookiejar` meta key is not “sticky”. You need to keep
passing it along on subsequent requests. For example:

```
def parse_page(self, response):
    # do some processing
    return scrapy.Request(
        "http://www.example.com/otherpage",
        meta={"cookiejar": response.meta["cookiejar"]},
        callback=self.parse_other_page,
    )
```

#### COOKIES_ENABLED

Default: `True`

Whether to enable the cookies middleware. If disabled, no cookies will be sent
to web servers.

Notice that despite the value of `COOKIES_ENABLED` setting if
`Request.`[`meta['dont_merge_cookies']`](request-response.html#std-reqmeta-dont_merge_cookies)
evaluates to `True` the request cookies will **not** be sent to the
web server and received cookies in [`Response`](request-response.html#scrapy.http.Response) will
**not** be merged with the existing cookies.

For more detailed information see the `cookies` parameter in
[`Request`](request-response.html#scrapy.Request).

#### COOKIES_DEBUG

Default: `False`

If enabled, Scrapy will log all cookies sent in requests (i.e. `Cookie`
header) and all cookies received in responses (i.e. `Set-Cookie` header).

Here’s an example of a log with `COOKIES_DEBUG` enabled:

```
2011-04-06 14:35:10-0300 [scrapy.core.engine] INFO: Spider opened
2011-04-06 14:35:10-0300 [scrapy.downloadermiddlewares.cookies] DEBUG: Sending cookies to: <GET http://www.diningcity.com/netherlands/index.html>
        Cookie: clientlanguage_nl=en_EN
2011-04-06 14:35:14-0300 [scrapy.downloadermiddlewares.cookies] DEBUG: Received cookies from: <200 http://www.diningcity.com/netherlands/index.html>
        Set-Cookie: JSESSIONID=B~FA4DC0C496C8762AE4F1A620EAB34F38; Path=/
        Set-Cookie: ip_isocode=US
        Set-Cookie: clientlanguage_nl=en_EN; Expires=Thu, 07-Apr-2011 21:21:34 GMT; Path=/
2011-04-06 14:49:50-0300 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://www.diningcity.com/netherlands/index.html> (referer: None)
[...]
```

### DefaultHeadersMiddleware

***class*scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/defaultheaders.html#DefaultHeadersMiddleware)**

This middleware sets all default requests headers specified in the
[`DEFAULT_REQUEST_HEADERS`](settings.html#std-setting-DEFAULT_REQUEST_HEADERS) setting.

### DownloadTimeoutMiddleware

***class*scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/downloadtimeout.html#DownloadTimeoutMiddleware)**

This middleware sets the download timeout for requests specified in the
[`DOWNLOAD_TIMEOUT`](settings.html#std-setting-DOWNLOAD_TIMEOUT) setting.

You can also set download timeout per-request using the
[`download_timeout`](request-response.html#std-reqmeta-download_timeout) [`Request.meta`](request-response.html#scrapy.Request.meta) key; this is supported
even when DownloadTimeoutMiddleware is disabled.

### HttpAuthMiddleware

***class*scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/httpauth.html#HttpAuthMiddleware)**

This middleware authenticates all requests generated from certain spiders
using [Basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) (aka. HTTP auth).

To enable HTTP authentication for a spider, set the `http_user` and
`http_pass` spider attributes to the authentication data and the
`http_auth_domain` spider attribute to the domain which requires this
authentication (its subdomains will be also handled in the same way).
You can set `http_auth_domain` to `None` to enable the
authentication for all requests but you risk leaking your authentication
credentials to unrelated domains.

In previous Scrapy versions HttpAuthMiddleware sent the authentication
data with all requests, which is a security problem if the spider
makes requests to several different domains. Currently if the
`http_auth_domain` attribute is not set, the middleware will use the
domain of the first request, which will work for some spiders but not
for others. In the future the middleware will produce an error instead.

Example:

```
from scrapy.spiders import CrawlSpider

class SomeIntranetSiteSpider(CrawlSpider):
    http_user = "someuser"
    http_pass = "somepass"
    http_auth_domain = "intranet.example.com"
    name = "intranet.example.com"

    # .. rest of the spider code omitted ...
```

### HttpCacheMiddleware

***class*scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/httpcache.html#HttpCacheMiddleware)**

This middleware provides low-level cache to all HTTP requests and responses.
It has to be combined with a cache storage backend as well as a cache policy.

Scrapy ships with the following HTTP cache storage backends:

> - Filesystem storage backend (default)
> - DBM storage backend

You can change the HTTP cache storage backend with the `HTTPCACHE_STORAGE`
setting. Or you can also implement your own storage backend.

Scrapy ships with two HTTP cache policies:

> - RFC2616 policy
> - Dummy policy (default)

You can change the HTTP cache policy with the `HTTPCACHE_POLICY`
setting. Or you can also implement your own policy.

You can also avoid caching a response on every policy using `dont_cache` meta key equals `True`.

#### Dummy policy (default)

***class*scrapy.extensions.httpcache.DummyPolicy[[source]](../_modules/scrapy/extensions/httpcache.html#DummyPolicy)**

This policy has no awareness of any HTTP Cache-Control directives.
Every request and its corresponding response are cached. When the same
request is seen again, the response is returned without transferring
anything from the Internet.

The Dummy policy is useful for testing spiders faster (without having
to wait for downloads every time) and for trying your spider offline,
when an Internet connection is not available. The goal is to be able to
“replay” a spider run *exactly as it ran before*.

#### RFC2616 policy

***class*scrapy.extensions.httpcache.RFC2616Policy[[source]](../_modules/scrapy/extensions/httpcache.html#RFC2616Policy)**

This policy provides a RFC2616 compliant HTTP cache, i.e. with HTTP
Cache-Control awareness, aimed at production and used in continuous
runs to avoid downloading unmodified data (to save bandwidth and speed up
crawls).

What is implemented:

- Do not attempt to store responses/requests with `no-store` cache-control directive set
- Do not serve responses from cache if `no-cache` cache-control directive is set even for fresh responses
- Compute freshness lifetime from `max-age` cache-control directive
- Compute freshness lifetime from `Expires` response header
- Compute freshness lifetime from `Last-Modified` response header (heuristic used by Firefox)
- Compute current age from `Age` response header
- Compute current age from `Date` header
- Revalidate stale responses based on `Last-Modified` response header
- Revalidate stale responses based on `ETag` response header
- Set `Date` header for any received response missing it
- Support `max-stale` cache-control directive in requests

This allows spiders to be configured with the full RFC2616 cache policy,
but avoid revalidation on a request-by-request basis, while remaining
conformant with the HTTP spec.

Example:

Add `Cache-Control: max-stale=600` to Request headers to accept responses that
have exceeded their expiration time by no more than 600 seconds.

See also: RFC2616, 14.9.3

What is missing:

- `Pragma: no-cache` support [https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9.1](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9.1)
- `Vary` header support [https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.6](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.6)
- Invalidation after updates or deletes [https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.10](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.10)
- … probably others ..

#### Filesystem storage backend (default)

***class*scrapy.extensions.httpcache.FilesystemCacheStorage[[source]](../_modules/scrapy/extensions/httpcache.html#FilesystemCacheStorage)**

File system storage backend is available for the HTTP cache middleware.

Each request/response pair is stored in a different directory containing
the following files:

- `request_body` - the plain request body
- `request_headers` - the request headers (in raw HTTP format)
- `response_body` - the plain response body
- `response_headers` - the request headers (in raw HTTP format)
- `meta` - some metadata of this cache resource in Python `repr()`
format (grep-friendly format)
- `pickled_meta` - the same metadata in `meta` but pickled for more
efficient deserialization

The directory name is made from the request fingerprint (see
`scrapy.utils.request.fingerprint`), and one level of subdirectories is
used to avoid creating too many files into the same directory (which is
inefficient in many file systems). An example directory could be:

```
/path/to/cache/dir/example.com/72/72811f648e718090f041317756c03adb0ada46c7
```

#### DBM storage backend

***class*scrapy.extensions.httpcache.DbmCacheStorage[[source]](../_modules/scrapy/extensions/httpcache.html#DbmCacheStorage)**

A [DBM](https://en.wikipedia.org/wiki/Dbm) storage backend is also available for the HTTP cache middleware.

By default, it uses the [`dbm`](https://docs.python.org/3/library/dbm.html#module-dbm), but you can change it with the
`HTTPCACHE_DBM_MODULE` setting.

#### Writing your own storage backend

You can implement a cache storage backend by creating a Python class that
defines the methods described below.

***class*scrapy.extensions.httpcache.CacheStorage**

**open_spider(*spider*)**

This method gets called after a spider has been opened for crawling. It handles
the [`open_spider`](signals.html#std-signal-spider_opened) signal.

**Parameters:**

**spider** ([`Spider`](spiders.html#scrapy.Spider) object) – the spider which has been opened

**close_spider(*spider*)**

This method gets called after a spider has been closed. It handles
the [`close_spider`](signals.html#std-signal-spider_closed) signal.

**Parameters:**

**spider** ([`Spider`](spiders.html#scrapy.Spider) object) – the spider which has been closed

**retrieve_response(*spider*, *request*)**

Return response if present in cache, or `None` otherwise.

**Parameters:**

- **spider** ([`Spider`](spiders.html#scrapy.Spider) object) – the spider which generated the request
- **request** ([`Request`](request-response.html#scrapy.Request) object) – the request to find cached response for

**store_response(*spider*, *request*, *response*)**

Store the given response in the cache.

**Parameters:**

- **spider** ([`Spider`](spiders.html#scrapy.Spider) object) – the spider for which the response is intended
- **request** ([`Request`](request-response.html#scrapy.Request) object) – the corresponding request the spider generated
- **response** ([`Response`](request-response.html#scrapy.http.Response) object) – the response to store in the cache

In order to use your storage backend, set:

- `HTTPCACHE_STORAGE` to the Python import path of your custom storage class.

#### HTTPCache middleware settings

The `HttpCacheMiddleware` can be configured through the following
settings:

##### HTTPCACHE_ENABLED

Default: `False`

Whether the HTTP cache will be enabled.

##### HTTPCACHE_EXPIRATION_SECS

Default: `0`

Expiration time for cached requests, in seconds.

Cached requests older than this time will be re-downloaded. If zero, cached
requests will never expire.

##### HTTPCACHE_DIR

Default: `'httpcache'`

The directory to use for storing the (low-level) HTTP cache. If empty, the HTTP
cache will be disabled. If a relative path is given, is taken relative to the
project data dir. For more info see: [Default structure of Scrapy projects](commands.html#topics-project-structure).

##### HTTPCACHE_IGNORE_HTTP_CODES

Default: `[]`

Don’t cache response with these HTTP codes.

##### HTTPCACHE_IGNORE_MISSING

Default: `False`

If enabled, requests not found in the cache will be ignored instead of downloaded.

##### HTTPCACHE_IGNORE_SCHEMES

Default: `['file']`

Don’t cache responses with these URI schemes.

##### HTTPCACHE_STORAGE

Default: `'scrapy.extensions.httpcache.FilesystemCacheStorage'`

The class which implements the cache storage backend.

##### HTTPCACHE_DBM_MODULE

Default: `'dbm'`

The database module to use in the DBM storage backend. This setting is specific to the DBM backend.

##### HTTPCACHE_POLICY

Default: `'scrapy.extensions.httpcache.DummyPolicy'`

The class which implements the cache policy.

##### HTTPCACHE_GZIP

Default: `False`

If enabled, will compress all cached data with gzip.
This setting is specific to the Filesystem backend.

##### HTTPCACHE_ALWAYS_STORE

Default: `False`

If enabled, will cache pages unconditionally.

A spider may wish to have all responses available in the cache, for
future use with `Cache-Control: max-stale`, for instance. The
DummyPolicy caches all responses but never revalidates them, and
sometimes a more nuanced policy is desirable.

This setting still respects `Cache-Control: no-store` directives in responses.
If you don’t want that, filter `no-store` out of the Cache-Control headers in
responses you feed to the cache middleware.

##### HTTPCACHE_IGNORE_RESPONSE_CACHE_CONTROLS

Default: `[]`

List of Cache-Control directives in responses to be ignored.

Sites often set “no-store”, “no-cache”, “must-revalidate”, etc., but get
upset at the traffic a spider can generate if it actually respects those
directives. This allows to selectively ignore Cache-Control directives
that are known to be unimportant for the sites being crawled.

We assume that the spider will not issue Cache-Control directives
in requests unless it actually needs them, so directives in requests are
not filtered.

### HttpCompressionMiddleware

***class*scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/httpcompression.html#HttpCompressionMiddleware)**

This middleware allows compressed (gzip, deflate) traffic to be
sent/received from web sites.

This middleware also supports decoding [brotli-compressed](https://www.ietf.org/rfc/rfc7932.txt) as well as
[zstd-compressed](https://www.ietf.org/rfc/rfc8478.txt) responses, provided that [brotli](https://pypi.org/project/Brotli/) or [zstandard](https://pypi.org/project/zstandard/) is
installed, respectively.

#### HttpCompressionMiddleware Settings

##### COMPRESSION_ENABLED

Default: `True`

Whether the Compression middleware will be enabled.

### HttpProxyMiddleware

***class*scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/httpproxy.html#HttpProxyMiddleware)**

This middleware sets the HTTP proxy to use for requests, by setting the
`proxy` meta value for [`Request`](request-response.html#scrapy.Request) objects.

Like the Python standard library module [`urllib.request`](https://docs.python.org/3/library/urllib.request.html#module-urllib.request), it obeys
the following environment variables:

- `http_proxy`
- `https_proxy`
- `no_proxy`

You can also set the meta key `proxy` per-request, to a value like
`http://some_proxy_server:port` or `http://username:password@some_proxy_server:port`.
Keep in mind this value will take precedence over `http_proxy`/`https_proxy`
environment variables, and it will also ignore `no_proxy` environment variable.

#### HttpProxyMiddleware settings

##### HTTPPROXY_ENABLED

Default: `True`

Whether or not to enable the `HttpProxyMiddleware`.

##### HTTPPROXY_AUTH_ENCODING

Default: `"latin-1"`

The default encoding for proxy authentication on `HttpProxyMiddleware`.

### OffsiteMiddleware

***class*scrapy.downloadermiddlewares.offsite.OffsiteMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/offsite.html#OffsiteMiddleware)**

Added in version 2.11.2.

Filters out Requests for URLs outside the domains covered by the spider.

This middleware filters out every request whose host names aren’t in the
spider’s [`allowed_domains`](spiders.html#scrapy.Spider.allowed_domains) attribute.
All subdomains of any domain in the list are also allowed.
E.g. the rule `www.example.org` will also allow `bob.www.example.org`
but not `www2.example.com` nor `example.com`.

When your spider returns a request for a domain not belonging to those
covered by the spider, this middleware will log a debug message similar to
this one:

```
DEBUG: Filtered offsite request to 'offsite.example': <GET http://offsite.example/some/page.html>
```

To avoid filling the log with too much noise, it will only print one of
these messages for each new domain filtered. So, for example, if another
request for `offsite.example` is filtered, no log message will be
printed. But if a request for `other.example` is filtered, a message
will be printed (but only for the first request filtered).

If the spider doesn’t define an
[`allowed_domains`](spiders.html#scrapy.Spider.allowed_domains) attribute, or the
attribute is empty, the offsite middleware will allow all requests.

If the request has the [`dont_filter`](request-response.html#scrapy.Request.dont_filter) attribute set to
`True` or `Request.meta` has `allow_offsite` set to `True`, then
the OffsiteMiddleware will allow the request even if its domain is not listed
in allowed domains.

### RedirectMiddleware

***class*scrapy.downloadermiddlewares.redirect.RedirectMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/redirect.html#RedirectMiddleware)**

This middleware handles redirection of requests based on response status.

The urls which the request goes through (while being redirected) can be found
in the `redirect_urls` [`Request.meta`](request-response.html#scrapy.Request.meta) key.

The reason behind each redirect in `redirect_urls` can be found in the
`redirect_reasons` [`Request.meta`](request-response.html#scrapy.Request.meta) key. For
example: `[301, 302, 307, 'meta refresh']`.

The format of a reason depends on the middleware that handled the corresponding
redirect. For example, `RedirectMiddleware` indicates the triggering
response status code as an integer, while `MetaRefreshMiddleware`
always uses the `'meta refresh'` string as reason.

The `RedirectMiddleware` can be configured through the following
settings (see the settings documentation for more info):

- `REDIRECT_ENABLED`
- `REDIRECT_MAX_TIMES`

If [`Request.meta`](request-response.html#scrapy.Request.meta) has `dont_redirect`
key set to True, the request will be ignored by this middleware.

If you want to handle some redirect status codes in your spider, you can
specify these in the `handle_httpstatus_list` spider attribute.

For example, if you want the redirect middleware to ignore 301 and 302
responses (and pass them through to your spider) you can do this:

```
class MySpider(CrawlSpider):
    handle_httpstatus_list = [301, 302]
```

The `handle_httpstatus_list` key of [`Request.meta`](request-response.html#scrapy.Request.meta) can also be used to specify which response codes to
allow on a per-request basis. You can also set the meta key
`handle_httpstatus_all` to `True` if you want to allow any response code
for a request.

#### RedirectMiddleware settings

##### REDIRECT_ENABLED

Default: `True`

Whether the Redirect middleware will be enabled.

##### REDIRECT_MAX_TIMES

Default: `20`

The maximum number of redirections that will be followed for a single request.
If maximum redirections are exceeded, the request is aborted and ignored.

### MetaRefreshMiddleware

***class*scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/redirect.html#MetaRefreshMiddleware)**

This middleware handles redirection of requests based on meta-refresh html tag.

The `MetaRefreshMiddleware` can be configured through the following
settings (see the settings documentation for more info):

- `METAREFRESH_ENABLED`
- `METAREFRESH_IGNORE_TAGS`
- `METAREFRESH_MAXDELAY`

This middleware obey `REDIRECT_MAX_TIMES` setting, `dont_redirect`,
`redirect_urls` and `redirect_reasons` request meta keys as described
for `RedirectMiddleware`

#### MetaRefreshMiddleware settings

##### METAREFRESH_ENABLED

Default: `True`

Whether the Meta Refresh middleware will be enabled.

##### METAREFRESH_IGNORE_TAGS

Default: `[]`

Meta tags within these tags are ignored.

Changed in version 2.11.2: The default value of `METAREFRESH_IGNORE_TAGS` changed from
`[]` to `["noscript"]`.

##### METAREFRESH_MAXDELAY

Default: `100`

The maximum meta-refresh delay (in seconds) to follow the redirection.
Some sites use meta-refresh for redirecting to a session expired page, so we
restrict automatic redirection to the maximum delay.

### RetryMiddleware

***class*scrapy.downloadermiddlewares.retry.RetryMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/retry.html#RetryMiddleware)**

A middleware to retry failed requests that are potentially caused by
temporary problems such as a connection timeout or HTTP 500 error.

Failed pages are collected on the scraping process and rescheduled at the
end, once the spider has finished crawling all regular (non failed) pages.

The `RetryMiddleware` can be configured through the following
settings (see the settings documentation for more info):

- `RETRY_ENABLED`
- `RETRY_TIMES`
- `RETRY_HTTP_CODES`
- `RETRY_EXCEPTIONS`

If [`Request.meta`](request-response.html#scrapy.Request.meta) has `dont_retry` key
set to True, the request will be ignored by this middleware.

To retry requests from a spider callback, you can use the
`get_retry_request()` function:

**scrapy.downloadermiddlewares.retry.get_retry_request(*request: Request*, ***, *spider: Spider*, *reason: str | Exception | type[Exception] = 'unspecified'*, *max_retry_times: int | None = None*, *priority_adjust: int | None = None*, *logger: Logger = <Logger scrapy.downloadermiddlewares.retry (WARNING)>*, *stats_base_key: str = 'retry'*) → [Request](request-response.html#scrapy.Request) | [None](https://docs.python.org/3/library/constants.html#None)[[source]](../_modules/scrapy/downloadermiddlewares/retry.html#get_retry_request)**

Returns a new [`Request`](request-response.html#scrapy.Request) object to retry the specified
request, or `None` if retries of the specified request have been
exhausted.

For example, in a [`Spider`](spiders.html#scrapy.Spider) callback, you could use it as
follows:

```
def parse(self, response):
    if not response.text:
        new_request_or_none = get_retry_request(
            response.request,
            spider=self,
            reason='empty',
        )
        return new_request_or_none
```

*spider* is the [`Spider`](spiders.html#scrapy.Spider) instance which is asking for the
retry request. It is used to access the [settings](settings.html#topics-settings)
and [stats](stats.html#topics-stats), and to provide extra logging context (see
[`logging.debug()`](https://docs.python.org/3/library/logging.html#logging.debug)).

*reason* is a string or an [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception) object that indicates the
reason why the request needs to be retried. It is used to name retry stats.

*max_retry_times* is a number that determines the maximum number of times
that *request* can be retried. If not specified or `None`, the number is
read from the [`max_retry_times`](request-response.html#std-reqmeta-max_retry_times) meta key of the request. If the
[`max_retry_times`](request-response.html#std-reqmeta-max_retry_times) meta key is not defined or `None`, the number
is read from the `RETRY_TIMES` setting.

*priority_adjust* is a number that determines how the priority of the new
request changes in relation to *request*. If not specified, the number is
read from the `RETRY_PRIORITY_ADJUST` setting.

*logger* is the logging.Logger object to be used when logging messages

*stats_base_key* is a string to be used as the base key for the
retry-related job stats

#### RetryMiddleware Settings

##### RETRY_ENABLED

Default: `True`

Whether the Retry middleware will be enabled.

##### RETRY_TIMES

Default: `2`

Maximum number of times to retry, in addition to the first download.

Maximum number of retries can also be specified per-request using
[`max_retry_times`](request-response.html#std-reqmeta-max_retry_times) attribute of [`Request.meta`](request-response.html#scrapy.Request.meta).
When initialized, the [`max_retry_times`](request-response.html#std-reqmeta-max_retry_times) meta key takes higher
precedence over the `RETRY_TIMES` setting.

##### RETRY_HTTP_CODES

Default: `[500, 502, 503, 504, 522, 524, 408, 429]`

Which HTTP response codes to retry. Other errors (DNS lookup issues,
connections lost, etc) are always retried.

In some cases you may want to add 400 to `RETRY_HTTP_CODES` because
it is a common code used to indicate server overload. It is not included by
default because HTTP specs say so.

##### RETRY_EXCEPTIONS

Default:

```
[
    'twisted.internet.defer.TimeoutError',
    'twisted.internet.error.TimeoutError',
    'twisted.internet.error.DNSLookupError',
    'twisted.internet.error.ConnectionRefusedError',
    'twisted.internet.error.ConnectionDone',
    'twisted.internet.error.ConnectError',
    'twisted.internet.error.ConnectionLost',
    'twisted.internet.error.TCPTimedOutError',
    'twisted.web.client.ResponseFailed',
    IOError,
    'scrapy.core.downloader.handlers.http11.TunnelError',
]
```

List of exceptions to retry.

Each list entry may be an exception type or its import path as a string.

An exception will not be caught when the exception type is not in
`RETRY_EXCEPTIONS` or when the maximum number of retries for a request
has been exceeded (see `RETRY_TIMES`). To learn about uncaught
exception propagation, see
`process_exception()`.

##### RETRY_PRIORITY_ADJUST

Default: `-1`

Adjust retry request priority relative to original request:

- a positive priority adjust means higher priority.
- **a negative priority adjust (default) means lower priority.**

### RobotsTxtMiddleware

***class*scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/robotstxt.html#RobotsTxtMiddleware)**

This middleware filters out requests forbidden by the robots.txt exclusion
standard.

To make sure Scrapy respects robots.txt make sure the middleware is enabled
and the [`ROBOTSTXT_OBEY`](settings.html#std-setting-ROBOTSTXT_OBEY) setting is enabled.

The [`ROBOTSTXT_USER_AGENT`](settings.html#std-setting-ROBOTSTXT_USER_AGENT) setting can be used to specify the
user agent string to use for matching in the [robots.txt](https://www.robotstxt.org/) file. If it
is `None`, the User-Agent header you are sending with the request or the
[`USER_AGENT`](settings.html#std-setting-USER_AGENT) setting (in that order) will be used for determining
the user agent to use in the [robots.txt](https://www.robotstxt.org/) file.

This middleware has to be combined with a [robots.txt](https://www.robotstxt.org/) parser.

Scrapy ships with support for the following [robots.txt](https://www.robotstxt.org/) parsers:

- Protego (default)
- RobotFileParser
- Robotexclusionrulesparser

You can change the [robots.txt](https://www.robotstxt.org/) parser with the [`ROBOTSTXT_PARSER`](settings.html#std-setting-ROBOTSTXT_PARSER)
setting. Or you can also implement support for a new parser.

If [`Request.meta`](request-response.html#scrapy.Request.meta) has
`dont_obey_robotstxt` key set to True
the request will be ignored by this middleware even if
[`ROBOTSTXT_OBEY`](settings.html#std-setting-ROBOTSTXT_OBEY) is enabled.

Parsers vary in several aspects:

- Language of implementation
- Supported specification
- Support for wildcard matching
- Usage of [length based rule](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt#order-of-precedence-for-rules):
in particular for `Allow` and `Disallow` directives, where the most
specific rule based on the length of the path trumps the less specific
(shorter) rule

Performance comparison of different parsers is available at [the following link](https://github.com/scrapy/scrapy/issues/3969).

#### Protego parser

Based on [Protego](https://github.com/scrapy/protego):

- implemented in Python
- is compliant with [Google’s Robots.txt Specification](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)
- supports wildcard matching
- uses the length based rule

Scrapy uses this parser by default.

#### RobotFileParser

Based on [`RobotFileParser`](https://docs.python.org/3/library/urllib.robotparser.html#urllib.robotparser.RobotFileParser):

- is Python’s built-in [robots.txt](https://www.robotstxt.org/) parser
- is compliant with [Martijn Koster’s 1996 draft specification](https://www.robotstxt.org/norobots-rfc.txt)
- lacks support for wildcard matching
- doesn’t use the length based rule

It is faster than Protego and backward-compatible with versions of Scrapy before 1.8.0.

In order to use this parser, set:

- [`ROBOTSTXT_PARSER`](settings.html#std-setting-ROBOTSTXT_PARSER) to `scrapy.robotstxt.PythonRobotParser`

#### Robotexclusionrulesparser

Based on [Robotexclusionrulesparser](https://pypi.org/project/robotexclusionrulesparser/):

- implemented in Python
- is compliant with [Martijn Koster’s 1996 draft specification](https://www.robotstxt.org/norobots-rfc.txt)
- supports wildcard matching
- doesn’t use the length based rule

In order to use this parser:

- Install `Robotexclusionrulesparser` by running
`pip install robotexclusionrulesparser`
- Set [`ROBOTSTXT_PARSER`](settings.html#std-setting-ROBOTSTXT_PARSER) setting to
`scrapy.robotstxt.RerpRobotParser`

#### Implementing support for a new parser

You can implement support for a new [robots.txt](https://www.robotstxt.org/) parser by subclassing
the abstract base class `RobotParser` and
implementing the methods described below.

***class*scrapy.robotstxt.RobotParser[[source]](../_modules/scrapy/robotstxt.html#RobotParser)**

***abstract*allowed(*url: [str](https://docs.python.org/3/library/stdtypes.html#str) | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)*, *user_agent: [str](https://docs.python.org/3/library/stdtypes.html#str) | [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)*) → [bool](https://docs.python.org/3/library/functions.html#bool)[[source]](../_modules/scrapy/robotstxt.html#RobotParser.allowed)**

Return `True` if `user_agent` is allowed to crawl `url`, otherwise return `False`.

**Parameters:**

- **url** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)*or*[*bytes*](https://docs.python.org/3/library/stdtypes.html#bytes)) – Absolute URL
- **user_agent** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)*or*[*bytes*](https://docs.python.org/3/library/stdtypes.html#bytes)) – User agent

***abstract classmethod*from_crawler(*crawler: [Crawler](api.html#scrapy.crawler.Crawler)*, *robotstxt_body: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)*) → Self[[source]](../_modules/scrapy/robotstxt.html#RobotParser.from_crawler)**

Parse the content of a [robots.txt](https://www.robotstxt.org/) file as bytes. This must be a class method.
It must return a new instance of the parser backend.

**Parameters:**

- **crawler** ([`Crawler`](api.html#scrapy.crawler.Crawler) instance) – crawler which made the request
- **robotstxt_body** ([*bytes*](https://docs.python.org/3/library/stdtypes.html#bytes)) – content of a [robots.txt](https://www.robotstxt.org/) file.

### DownloaderStats

***class*scrapy.downloadermiddlewares.stats.DownloaderStats[[source]](../_modules/scrapy/downloadermiddlewares/stats.html#DownloaderStats)**

Middleware that stores stats of all requests, responses and exceptions that
pass through it.

To use this middleware you must enable the [`DOWNLOADER_STATS`](settings.html#std-setting-DOWNLOADER_STATS)
setting.

### UserAgentMiddleware

***class*scrapy.downloadermiddlewares.useragent.UserAgentMiddleware[[source]](../_modules/scrapy/downloadermiddlewares/useragent.html#UserAgentMiddleware)**

Middleware that sets the `User-Agent` header.

The header value is taken from the [`USER_AGENT`](settings.html#std-setting-USER_AGENT) setting.
