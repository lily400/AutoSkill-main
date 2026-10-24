# Requests and Responses — Scrapy 2.14.1 documentation

- Requests and Responses
- [Edit on GitHub](https://github.com/scrapy/scrapy/blob/master/docs/topics/request-response.rst)

---

# Requests and Responses

Scrapy uses `Request` and `Response` objects for crawling web
sites.

Typically, `Request` objects are generated in the spiders and pass
across the system until they reach the Downloader, which executes the request
and returns a `Response` object which travels back to the spider that
issued the request.

Both `Request` and `Response` classes have subclasses which add
functionality not required in the base classes. These are described
below in Request subclasses and
Response subclasses.

## Request objects

***class*scrapy.Request(**args: Any*, ***kwargs: Any*)[[source]](../_modules/scrapy/http/request.html#Request)**

Represents an HTTP request, which is usually generated in a Spider and
executed by the Downloader, thus generating a `Response`.

**Parameters:**

- **url** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) –

the URL of this request

If the URL is invalid, a [`ValueError`](https://docs.python.org/3/library/exceptions.html#ValueError) exception is raised.
- **callback** (*Callable**[**Concatenate**[**Response**,**...**]**,**Any**]**|**None*) – sets `callback`, defaults to `None`.
- **method** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – the HTTP method of this request. Defaults to `'GET'`.
- **meta** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – the initial values for the `Request.meta` attribute. If
given, the dict passed in this parameter will be shallow copied.
- **body** ([*bytes*](https://docs.python.org/3/library/stdtypes.html#bytes)*or*[*str*](https://docs.python.org/3/library/stdtypes.html#str)) – the request body. If a string is passed, then it’s encoded as
bytes using the `encoding` passed (which defaults to `utf-8`). If
`body` is not given, an empty bytes object is stored. Regardless of the
type of this argument, the final value stored will be a bytes object
(never a string or `None`).
- **headers** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) –

the headers of this request. The dict values can be strings
(for single valued headers) or lists (for multi-valued headers). If
`None` is passed as value, the HTTP header will not be sent at all.

Cookies set via the `Cookie` header are not considered by the
[CookiesMiddleware](downloader-middleware.html#cookies-mw). If you need to set cookies for a request, use the
`cookies` argument. This is a known current limitation that is being
worked on.
- **cookies** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)*or*[*list*](https://docs.python.org/3/library/stdtypes.html#list)) –

the request cookies. These can be sent in two forms.

```
request_with_cookies = Request(
    url="http://www.example.com",
    cookies={"currency": "USD", "country": "UY"},
)
```

```
request_with_cookies = Request(
    url="https://www.example.com",
    cookies=[
        {
            "name": "currency",
            "value": "USD",
            "domain": "example.com",
            "path": "/currency",
            "secure": True,
        },
    ],
)
```

The latter form allows for customizing the `domain` and `path`
attributes of the cookie. This is only useful if the cookies are saved
for later requests.

When some site returns cookies (in a response) those are stored in the
cookies for that domain and will be sent again in future requests.
That’s the typical behaviour of any regular web browser.

Note that setting the `dont_merge_cookies` key to `True` in
`request.meta` causes custom cookies to be
ignored.

For more info see [CookiesMiddleware](downloader-middleware.html#cookies-mw).

Cookies set via the `Cookie` header are not considered by the
[CookiesMiddleware](downloader-middleware.html#cookies-mw). If you need to set cookies for a request, use the
`scrapy.Request.cookies` parameter. This is a known
current limitation that is being worked on.
  1. Using a dict:
  1. Using a list of dicts:
- **encoding** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – the encoding of this request (defaults to `'utf-8'`).
This encoding will be used to percent-encode the URL and to convert the
body to bytes (if given as a string).
- **priority** ([*int*](https://docs.python.org/3/library/functions.html#int)) – sets `priority`, defaults to `0`.
- **dont_filter** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – sets `dont_filter`, defaults to `False`.
- **errback** (*Callable**[**[**Failure**]**,**Any**]**|**None*) – sets `errback`, defaults to `None`.
- **flags** ([*list*](https://docs.python.org/3/library/stdtypes.html#list)) – Flags sent to the request, can be used for logging or similar purposes.
- **cb_kwargs** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – A dict with arbitrary data that will be passed as keyword arguments to the Request’s callback.

**url**

A string containing the URL of this request. Keep in mind that this
attribute contains the escaped URL, so it can differ from the URL passed in
the `__init__()` method.

This attribute is read-only. To change the URL of a Request use
`replace()`.

**method**

A string representing the HTTP method in the request. This is guaranteed to
be uppercase. Example: `"GET"`, `"POST"`, `"PUT"`, etc

**headers**

A dictionary-like (`scrapy.http.headers.Headers`) object which contains
the request headers.

**body**

The request body as bytes.

This attribute is read-only. To change the body of a Request use
`replace()`.

**callback*: CallbackT | [None](https://docs.python.org/3/library/constants.html#None)***

[`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable) to parse the
`Response` to this request once received.

The callable must expect the response as its first parameter, and
support any additional keyword arguments set through
`cb_kwargs`.

In addition to an arbitrary callable, the following values are also
supported:

- `None` (default), which indicates that the
[`parse()`](spiders.html#scrapy.Spider.parse) method of the spider must be used.
- `NO_CALLBACK()`.

If an unhandled exception is raised during request or response
processing, i.e. by a [spider middleware](spider-middleware.html#topics-spider-middleware), [downloader middleware](downloader-middleware.html#topics-downloader-middleware) or download handler
([`DOWNLOAD_HANDLERS`](settings.html#std-setting-DOWNLOAD_HANDLERS)), `errback` is called instead.

[`HttpErrorMiddleware`](spider-middleware.html#scrapy.spidermiddlewares.httperror.HttpErrorMiddleware)
raises exceptions for non-2xx responses by default, sending them
to the `errback` instead.

Passing additional data to callback functions

**errback*: Callable[[Failure], Any] | [None](https://docs.python.org/3/library/constants.html#None)***

[`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable) to handle exceptions raised
during request or response processing.

The callable must expect a [`Failure`](https://docs.twisted.org/en/stable/api/twisted.python.failure.Failure.html) as
its first parameter.

Using errbacks to catch exceptions in request processing

**priority*: [int](https://docs.python.org/3/library/functions.html#int)***

Default: `0`

Value that the [scheduler](scheduler.html#topics-scheduler) may use for
request prioritization.

Built-in schedulers prioritize requests with a higher priority
value.

Negative values are allowed.

**cb_kwargs**

A dictionary that contains arbitrary metadata for this request. Its contents
will be passed to the Request’s callback as keyword arguments. It is empty
for new Requests, which means by default callbacks only get a
`Response` object as argument.

This dict is [shallow copied](https://docs.python.org/3/library/copy.html) when the request is
cloned using the `copy()` or `replace()` methods, and can also be
accessed, in your spider, from the `response.cb_kwargs` attribute.

In case of a failure to process the request, this dict can be accessed as
`failure.request.cb_kwargs` in the request’s errback. For more information,
see Accessing additional data in errback functions.

**meta*= {}***

> A dictionary of arbitrary metadata for the request.
>
>
>
> You may extend request metadata as you see fit.
>
>
>
> Request metadata can also be accessed through the
> `meta` attribute of a response.
>
>
>
> To pass data from one spider callback to another, consider using
> `cb_kwargs` instead. However, request metadata may be the right
> choice in certain scenarios, such as to maintain some debugging data
> across all follow-up requests (e.g. the source URL).
>
>
>
> A common use of request metadata is to define request-specific
> parameters for Scrapy components (extensions, middlewares, etc.). For
> example, if you set `dont_retry` to `True`,
> [`RetryMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.retry.RetryMiddleware) will never
> retry that request, even if it fails. See Request.meta special keys.
>
>
>
> You may also use request metadata in your custom Scrapy components, for
> example, to keep request state information relevant to your component.
> For example,
> [`RetryMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.retry.RetryMiddleware) uses the
> `retry_times` metadata key to keep track of how many times a request
> has been retried so far.
>
>
>
> Copying all the metadata of a previous request into a new, follow-up
> request in a spider callback is a bad practice, because request
> metadata may include metadata set by Scrapy components that is not
> meant to be copied into other requests. For example, copying the
> `retry_times` metadata key into follow-up requests can lower the
> amount of retries allowed for those follow-up requests.
>
>
>
> You should only copy all request metadata from one request to another
> if the new request is meant to replace the old request, as is often the
> case when returning a request from a [downloader middleware](downloader-middleware.html#topics-downloader-middleware) method.
>
>
>
> Also mind that the `copy()` and `replace()` request methods
> [shallow-copy](https://docs.python.org/3/library/copy.html) request metadata.

**dont_filter*: [bool](https://docs.python.org/3/library/functions.html#bool)***

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

Create a Request object from a string containing a [cURL](https://curl.se/) command. It populates the HTTP method, the
URL, the headers, the cookies and the body. It accepts the same
arguments as the `Request` class, taking preference and
overriding the values of the same arguments contained in the cURL
command.

Unrecognized options are ignored by default. To raise an error when
finding unknown options call this method by passing
`ignore_unknown_options=False`.

Using `from_curl()` from `Request`
subclasses, such as `JsonRequest`, or
`XmlRpcRequest`, as well as having
[downloader middlewares](downloader-middleware.html#topics-downloader-middleware)
and
[spider middlewares](spider-middleware.html#topics-spider-middleware)
enabled, such as
[`DefaultHeadersMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware),
[`UserAgentMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.useragent.UserAgentMiddleware),
or
[`HttpCompressionMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware),
may modify the `Request` object.

To translate a cURL command into a Scrapy request,
you may use [curl2scrapy](https://michael-shub.github.io/curl2scrapy/).

**to_dict(***, *spider: [Spider](spiders.html#scrapy.spiders.Spider) | [None](https://docs.python.org/3/library/constants.html#None) = None*) → [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)][[source]](../_modules/scrapy/http/request.html#Request.to_dict)**

Return a dictionary containing the Request’s data.

Use `request_from_dict()` to convert back into a `Request` object.

If a spider is given, this method will try to find out the name of the spider methods used as callback
and errback and include them in the output dict, raising an exception if they cannot be found.

### Other functions related to requests

**scrapy.http.request.NO_CALLBACK(**args: [Any](https://docs.python.org/3/library/typing.html#typing.Any)*, ***kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any)*) → [NoReturn](https://docs.python.org/3/library/typing.html#typing.NoReturn)[[source]](../_modules/scrapy/http/request.html#NO_CALLBACK)**

When assigned to the `callback` parameter of
`Request`, it indicates that the request is not meant
to have a spider callback at all.

For example:

```
Request("https://example.com", callback=NO_CALLBACK)
```

This value should be used by [components](components.html#topics-components) that
create and handle their own requests, e.g. through
`scrapy.core.engine.ExecutionEngine.download()`, so that downloader
middlewares handling such requests can treat them differently from requests
intended for the [`parse()`](spiders.html#scrapy.Spider.parse) callback.

**scrapy.utils.request.request_from_dict(*d: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*, ***, *spider: [Spider](spiders.html#scrapy.spiders.Spider) | [None](https://docs.python.org/3/library/constants.html#None) = None*) → Request[[source]](../_modules/scrapy/utils/request.html#request_from_dict)**

Create a `Request` object from a dict.

If a spider is given, it will try to resolve the callbacks looking at the
spider for methods with the same name.

### Passing additional data to callback functions

The callback of a request is a function that will be called when the response
of that request is downloaded. The callback function will be called with the
downloaded `Response` object as its first argument.

Example:

```
def parse_page1(self, response):
    return scrapy.Request(
        "http://www.example.com/some_page.html", callback=self.parse_page2
    )

def parse_page2(self, response):
    # this would log http://www.example.com/some_page.html
    self.logger.info("Visited %s", response.url)
```

In some cases you may be interested in passing arguments to those callback
functions so you can receive the arguments later, in the second callback.
The following example shows how to achieve this by using the
`Request.cb_kwargs` attribute:

```
def parse(self, response):
    request = scrapy.Request(
        "http://www.example.com/index.html",
        callback=self.parse_page2,
        cb_kwargs=dict(main_url=response.url),
    )
    request.cb_kwargs["foo"] = "bar"  # add more arguments for the callback
    yield request

def parse_page2(self, response, main_url, foo):
    yield dict(
        main_url=main_url,
        other_url=response.url,
        foo=foo,
    )
```

`Request.cb_kwargs` was introduced in version `1.7`.
Prior to that, using `Request.meta` was recommended for passing
information around callbacks. After `1.7`, `Request.cb_kwargs`
became the preferred way for handling user information, leaving `Request.meta`
for communication with components like middlewares and extensions.

### Using errbacks to catch exceptions in request processing

The errback of a request is a function that will be called when an exception
is raise while processing it.

It receives a [`Failure`](https://docs.twisted.org/en/stable/api/twisted.python.failure.Failure.html) as first parameter and can
be used to track connection establishment timeouts, DNS errors etc.

Here’s an example spider logging all errors and catching some specific
errors if needed:

```
import scrapy

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class ErrbackSpider(scrapy.Spider):
    name = "errback_example"
    start_urls = [
        "http://www.httpbin.org/",  # HTTP 200 expected
        "http://www.httpbin.org/status/404",  # Not found error
        "http://www.httpbin.org/status/500",  # server issue
        "http://www.httpbin.org:12345/",  # non-responding host, timeout expected
        "https://example.invalid/",  # DNS error expected
    ]

    async def start(self):
        for u in self.start_urls:
            yield scrapy.Request(
                u,
                callback=self.parse_httpbin,
                errback=self.errback_httpbin,
                dont_filter=True,
            )

    def parse_httpbin(self, response):
        self.logger.info("Got successful response from {}".format(response.url))
        # do something useful here...

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error("DNSLookupError on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError on %s", request.url)
```

### Accessing additional data in errback functions

In case of a failure to process the request, you may be interested in
accessing arguments to the callback functions so you can process further
based on the arguments in the errback. The following example shows how to
achieve this by using `Failure.request.cb_kwargs`:

```
def parse(self, response):
    request = scrapy.Request(
        "http://www.example.com/index.html",
        callback=self.parse_page2,
        errback=self.errback_page2,
        cb_kwargs=dict(main_url=response.url),
    )
    yield request

def parse_page2(self, response, main_url):
    pass

def errback_page2(self, failure):
    yield dict(
        main_url=failure.request.cb_kwargs["main_url"],
    )
```

### Request fingerprints

There are some aspects of scraping, such as filtering out duplicate requests
(see [`DUPEFILTER_CLASS`](settings.html#std-setting-DUPEFILTER_CLASS)) or caching responses (see
[`HTTPCACHE_POLICY`](downloader-middleware.html#std-setting-HTTPCACHE_POLICY)), where you need the ability to generate a short,
unique identifier from a `Request` object: a request
fingerprint.

You often do not need to worry about request fingerprints, the default request
fingerprinter works for most projects.

However, there is no universal way to generate a unique identifier from a
request, because different situations require comparing requests differently.
For example, sometimes you may need to compare URLs case-insensitively, include
URL fragments, exclude certain URL query parameters, include some or all
headers, etc.

To change how request fingerprints are built for your requests, use the
`REQUEST_FINGERPRINTER_CLASS` setting.

#### REQUEST_FINGERPRINTER_CLASS

Default: `scrapy.utils.request.RequestFingerprinter`

A request fingerprinter class or its
import path.

***class*scrapy.utils.request.RequestFingerprinter(*crawler: [Crawler](api.html#scrapy.crawler.Crawler) | [None](https://docs.python.org/3/library/constants.html#None) = None*)[[source]](../_modules/scrapy/utils/request.html#RequestFingerprinter)**

Default fingerprinter.

It takes into account a canonical version
([`w3lib.url.canonicalize_url()`](https://w3lib.readthedocs.io/en/latest/w3lib.html#w3lib.url.canonicalize_url)) of `request.url` and the values of `request.method` and `request.body`. It then generates an [SHA1](https://en.wikipedia.org/wiki/SHA-1) hash.

#### Writing your own request fingerprinter

A request fingerprinter is a [component](components.html#topics-components) that must
implement the following method:

**fingerprint(*self*, *request: scrapy.Request*)**

Return a [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes) object that uniquely identifies *request*.

See also Request fingerprint restrictions.

The `fingerprint()` method of the default request fingerprinter,
`scrapy.utils.request.RequestFingerprinter`, uses
`scrapy.utils.request.fingerprint()` with its default parameters. For some
common use cases you can use `scrapy.utils.request.fingerprint()` as well
in your `fingerprint()` method implementation:

**scrapy.utils.request.fingerprint(*request: Request*, ***, *include_headers: Iterable[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *keep_fragments: [bool](https://docs.python.org/3/library/functions.html#bool) = False*) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)[[source]](../_modules/scrapy/utils/request.html#fingerprint)**

Return the request fingerprint.

The request fingerprint is a hash that uniquely identifies the resource the
request points to. For example, take the following two urls:
`http://www.example.com/query?id=111&cat=222`,
`http://www.example.com/query?cat=222&id=111`.

Even though those are two different URLs both point to the same resource
and are equivalent (i.e. they should return the same response).

Another example are cookies used to store session ids. Suppose the
following page is only accessible to authenticated users:
`http://www.example.com/members/offers.html`.

Lots of sites use a cookie to store the session id, which adds a random
component to the HTTP Request and thus should be ignored when calculating
the fingerprint.

For this reason, request headers are ignored by default when calculating
the fingerprint. If you want to include specific headers use the
include_headers argument, which is a list of Request headers to include.

Also, servers usually ignore fragments in urls when handling requests,
so they are also ignored by default when calculating the fingerprint.
If you want to include them, set the keep_fragments argument to True
(for instance when handling requests with a headless browser).

For example, to take the value of a request header named `X-ID` into
account:

```
# my_project/settings.py
REQUEST_FINGERPRINTER_CLASS = "my_project.utils.RequestFingerprinter"

# my_project/utils.py
from scrapy.utils.request import fingerprint

class RequestFingerprinter:
    def fingerprint(self, request):
        return fingerprint(request, include_headers=["X-ID"])
```

You can also write your own fingerprinting logic from scratch.

However, if you do not use `scrapy.utils.request.fingerprint()`, make sure
you use [`WeakKeyDictionary`](https://docs.python.org/3/library/weakref.html#weakref.WeakKeyDictionary) to cache request fingerprints:

- Caching saves CPU by ensuring that fingerprints are calculated only once
per request, and not once per Scrapy component that needs the fingerprint
of a request.
- Using [`WeakKeyDictionary`](https://docs.python.org/3/library/weakref.html#weakref.WeakKeyDictionary) saves memory by ensuring that
request objects do not stay in memory forever just because you have
references to them in your cache dictionary.

For example, to take into account only the URL of a request, without any prior
URL canonicalization or taking the request method or body into account:

```
from hashlib import sha1
from weakref import WeakKeyDictionary

from scrapy.utils.python import to_bytes

class RequestFingerprinter:
    cache = WeakKeyDictionary()

    def fingerprint(self, request):
        if request not in self.cache:
            fp = sha1()
            fp.update(to_bytes(request.url))
            self.cache[request] = fp.digest()
        return self.cache[request]
```

If you need to be able to override the request fingerprinting for arbitrary
requests from your spider callbacks, you may implement a request fingerprinter
that reads fingerprints from `request.meta`
when available, and then falls back to
`scrapy.utils.request.fingerprint()`. For example:

```
from scrapy.utils.request import fingerprint

class RequestFingerprinter:
    def fingerprint(self, request):
        if "fingerprint" in request.meta:
            return request.meta["fingerprint"]
        return fingerprint(request)
```

If you need to reproduce the same fingerprinting algorithm as Scrapy 2.6, use
the following request fingerprinter:

```
from hashlib import sha1
from weakref import WeakKeyDictionary

from scrapy.utils.python import to_bytes
from w3lib.url import canonicalize_url

class RequestFingerprinter:
    cache = WeakKeyDictionary()

    def fingerprint(self, request):
        if request not in self.cache:
            fp = sha1()
            fp.update(to_bytes(request.method))
            fp.update(to_bytes(canonicalize_url(request.url)))
            fp.update(request.body or b"")
            self.cache[request] = fp.digest()
        return self.cache[request]
```

#### Request fingerprint restrictions

Scrapy components that use request fingerprints may impose additional
restrictions on the format of the fingerprints that your request
fingerprinter generates.

The following built-in Scrapy components have such restrictions:

- [`scrapy.extensions.httpcache.FilesystemCacheStorage`](downloader-middleware.html#scrapy.extensions.httpcache.FilesystemCacheStorage) (default
value of [`HTTPCACHE_STORAGE`](downloader-middleware.html#std-setting-HTTPCACHE_STORAGE))

Request fingerprints must be at least 1 byte long.

Path and filename length limits of the file system of
[`HTTPCACHE_DIR`](downloader-middleware.html#std-setting-HTTPCACHE_DIR) also apply. Inside [`HTTPCACHE_DIR`](downloader-middleware.html#std-setting-HTTPCACHE_DIR),
the following directory structure is created:

For example, if a request fingerprint is made of 20 bytes (default),
[`HTTPCACHE_DIR`](downloader-middleware.html#std-setting-HTTPCACHE_DIR) is `'/home/user/project/.scrapy/httpcache'`,
and the name of your spider is `'my_spider'` your file system must
support a file path like:

```
/home/user/project/.scrapy/httpcache/my_spider/01/0123456789abcdef0123456789abcdef01234567/response_headers
```
  - [`Spider.name`](spiders.html#scrapy.Spider.name)
    - first byte of a request fingerprint as hexadecimal
      - fingerprint as hexadecimal
        - filenames up to 16 characters long
- [`scrapy.extensions.httpcache.DbmCacheStorage`](downloader-middleware.html#scrapy.extensions.httpcache.DbmCacheStorage)

The underlying DBM implementation must support keys as long as twice
the number of bytes of a request fingerprint, plus 5. For example,
if a request fingerprint is made of 20 bytes (default),
45-character-long keys must be supported.

## Request.meta special keys

The `Request.meta` attribute can contain any arbitrary data, but there
are some special keys recognized by Scrapy and its built-in extensions.

Those are:

- [`allow_offsite`](downloader-middleware.html#std-reqmeta-allow_offsite)
- [`autothrottle_dont_adjust_delay`](autothrottle.html#std-reqmeta-autothrottle_dont_adjust_delay)
- `bindaddress`
- [`cookiejar`](downloader-middleware.html#std-reqmeta-cookiejar)
- [`dont_cache`](downloader-middleware.html#std-reqmeta-dont_cache)
- `dont_merge_cookies`
- [`dont_obey_robotstxt`](downloader-middleware.html#std-reqmeta-dont_obey_robotstxt)
- [`dont_redirect`](downloader-middleware.html#std-reqmeta-dont_redirect)
- [`dont_retry`](downloader-middleware.html#std-reqmeta-dont_retry)
- `download_fail_on_dataloss`
- `download_latency`
- [`download_maxsize`](settings.html#std-reqmeta-download_maxsize)
- [`download_warnsize`](settings.html#std-reqmeta-download_warnsize)
- `download_timeout`
- `ftp_password` (See [`FTP_PASSWORD`](settings.html#std-setting-FTP_PASSWORD) for more info)
- `ftp_user` (See [`FTP_USER`](settings.html#std-setting-FTP_USER) for more info)
- [`handle_httpstatus_all`](spider-middleware.html#std-reqmeta-handle_httpstatus_all)
- [`handle_httpstatus_list`](spider-middleware.html#std-reqmeta-handle_httpstatus_list)
- [`is_start_request`](spider-middleware.html#std-reqmeta-is_start_request)
- `max_retry_times`
- [`proxy`](downloader-middleware.html#std-reqmeta-proxy)
- [`redirect_reasons`](downloader-middleware.html#std-reqmeta-redirect_reasons)
- [`redirect_urls`](downloader-middleware.html#std-reqmeta-redirect_urls)
- [`referrer_policy`](spider-middleware.html#std-reqmeta-referrer_policy)

### bindaddress

The IP of the outgoing IP address to use for the performing the request.

### download_timeout

The amount of time (in secs) that the downloader will wait before timing out.
See also: [`DOWNLOAD_TIMEOUT`](settings.html#std-setting-DOWNLOAD_TIMEOUT).

### download_latency

The amount of time spent to fetch the response, since the request has been
started, i.e. HTTP message sent over the network. This meta key only becomes
available when the response has been downloaded. While most other meta keys are
used to control Scrapy behavior, this one is supposed to be read-only.

### download_fail_on_dataloss

Whether or not to fail on broken responses. See:
[`DOWNLOAD_FAIL_ON_DATALOSS`](settings.html#std-setting-DOWNLOAD_FAIL_ON_DATALOSS).

### max_retry_times

The meta key is used set retry times per request. When initialized, the
`max_retry_times` meta key takes higher precedence over the
[`RETRY_TIMES`](downloader-middleware.html#std-setting-RETRY_TIMES) setting.

## Stopping the download of a Response

Raising a [`StopDownload`](exceptions.html#scrapy.exceptions.StopDownload) exception from a handler for the
[`bytes_received`](signals.html#scrapy.signals.bytes_received) or [`headers_received`](signals.html#scrapy.signals.headers_received)
signals will stop the download of a given response. See the following example:

```
import scrapy

class StopSpider(scrapy.Spider):
    name = "stop"
    start_urls = ["https://docs.scrapy.org/en/latest/"]

    @classmethod
    def from_crawler(cls, crawler):
        spider = super().from_crawler(crawler)
        crawler.signals.connect(
            spider.on_bytes_received, signal=scrapy.signals.bytes_received
        )
        return spider

    def parse(self, response):
        # 'last_chars' show that the full response was not downloaded
        yield {"len": len(response.text), "last_chars": response.text[-40:]}

    def on_bytes_received(self, data, request, spider):
        raise scrapy.exceptions.StopDownload(fail=False)
```

which produces the following output:

```
2020-05-19 17:26:12 [scrapy.core.engine] INFO: Spider opened
2020-05-19 17:26:12 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2020-05-19 17:26:13 [scrapy.core.downloader.handlers.http11] DEBUG: Download stopped for <GET https://docs.scrapy.org/en/latest/> from signal handler StopSpider.on_bytes_received
2020-05-19 17:26:13 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://docs.scrapy.org/en/latest/> (referer: None) ['download_stopped']
2020-05-19 17:26:13 [scrapy.core.scraper] DEBUG: Scraped from <200 https://docs.scrapy.org/en/latest/>
{'len': 279, 'last_chars': 'dth, initial-scale=1.0">\n  \n  <title>Scr'}
2020-05-19 17:26:13 [scrapy.core.engine] INFO: Closing spider (finished)
```

By default, resulting responses are handled by their corresponding errbacks. To
call their callback instead, like in this example, pass `fail=False` to the
[`StopDownload`](exceptions.html#scrapy.exceptions.StopDownload) exception.

## Request subclasses

Here is the list of built-in `Request` subclasses. You can also subclass
it to implement your own custom functionality.

### FormRequest objects

The FormRequest class extends the base `Request` with functionality for
dealing with HTML forms. It uses [lxml.html forms](https://lxml.de/lxmlhtml.html#forms) to pre-populate form
fields with form data from `Response` objects.

***class*scrapy.FormRequest(*url*[, *formdata*, *...*])**

The `FormRequest` class adds a new keyword parameter to the `__init__()` method. The
remaining arguments are the same as for the `Request` class and are
not documented here.

**Parameters:**

**formdata** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)*or*[*collections.abc.Iterable*](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)) – is a dictionary (or iterable of (key, value) tuples)
containing HTML Form data which will be url-encoded and assigned to the
body of the request.

The `FormRequest` objects support the following class method in
addition to the standard `Request` methods:

***classmethod*from_response(*response*[, *formname=None*, *formid=None*, *formnumber=0*, *formdata=None*, *formxpath=None*, *formcss=None*, *clickdata=None*, *dont_click=False*, *...*])**

Returns a new `FormRequest` object with its form field values
pre-populated with those found in the HTML `<form>` element contained
in the given response. For an example see
Using FormRequest.from_response() to simulate a user login.

The policy is to automatically simulate a click, by default, on any form
control that looks clickable, like a `<input type="submit">`. Even
though this is quite convenient, and often the desired behaviour,
sometimes it can cause problems which could be hard to debug. For
example, when working with forms that are filled and/or submitted using
javascript, the default `from_response()` behaviour may not be the
most appropriate. To disable this behaviour you can set the
`dont_click` argument to `True`. Also, if you want to change the
control clicked (instead of disabling it) you can also use the
`clickdata` argument.

Using this method with select elements which have leading
or trailing whitespace in the option values will not work due to a
[bug in lxml](https://bugs.launchpad.net/lxml/+bug/1665241), which should be fixed in lxml 3.8 and above.

**Parameters:**

- **response** (`Response` object) – the response containing a HTML form which will be used
to pre-populate the form fields
- **formname** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the form with name attribute set to this value will be used.
- **formid** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the form with id attribute set to this value will be used.
- **formxpath** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the first form that matches the xpath will be used.
- **formcss** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the first form that matches the css selector will be used.
- **formnumber** ([*int*](https://docs.python.org/3/library/functions.html#int)) – the number of form to use, when the response contains
multiple forms. The first one (and also the default) is `0`.
- **formdata** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – fields to override in the form data. If a field was
already present in the response `<form>` element, its value is
overridden by the one passed in this parameter. If a value passed in
this parameter is `None`, the field will not be included in the
request, even if it was present in the response `<form>` element.
- **clickdata** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – attributes to lookup the control clicked. If it’s not
given, the form data will be submitted simulating a click on the
first clickable element. In addition to html attributes, the control
can be identified by its zero-based index relative to other
submittable inputs inside the form, via the `nr` attribute.
- **dont_click** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, the form data will be submitted without
clicking in any element.

The other parameters of this class method are passed directly to the
`FormRequest` `__init__()` method.

### Request usage examples

#### Using FormRequest to send data via HTTP POST

If you want to simulate a HTML Form POST in your spider and send a couple of
key-value fields, you can return a `FormRequest` object (from your
spider) like this:

```
return [
    FormRequest(
        url="http://www.example.com/post/action",
        formdata={"name": "John Doe", "age": "27"},
        callback=self.after_post,
    )
]
```

#### Using FormRequest.from_response() to simulate a user login

It is usual for web sites to provide pre-populated form fields through `<input
type="hidden">` elements, such as session related data or authentication
tokens (for login pages). When scraping, you’ll want these fields to be
automatically pre-populated and only override a couple of them, such as the
user name and password. You can use the `FormRequest.from_response()`
method for this job. Here’s an example spider which uses it:

```
import scrapy

def authentication_failed(response):
    # TODO: Check the contents of the response and return True if it failed
    # or False if it succeeded.
    pass

class LoginSpider(scrapy.Spider):
    name = "example.com"
    start_urls = ["http://www.example.com/users/login.php"]

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={"username": "john", "password": "secret"},
            callback=self.after_login,
        )

    def after_login(self, response):
        if authentication_failed(response):
            self.logger.error("Login failed")
            return

        # continue scraping with authenticated session...
```

### JsonRequest

The JsonRequest class extends the base `Request` class with functionality for
dealing with JSON requests.

***class*scrapy.http.JsonRequest(*url*[, *... data*, *dumps_kwargs*])[[source]](../_modules/scrapy/http/request/json_request.html#JsonRequest)**

The `JsonRequest` class adds two new keyword parameters to the `__init__()` method. The
remaining arguments are the same as for the `Request` class and are
not documented here.

Using the `JsonRequest` will set the `Content-Type` header to `application/json`
and `Accept` header to `application/json, text/javascript, */*; q=0.01`

**Parameters:**

- **data** ([*object*](https://docs.python.org/3/library/functions.html#object)) – is any JSON serializable object that needs to be JSON encoded and assigned to body.
If the `body` argument is provided this parameter will be ignored.
If the `body` argument is not provided and the
`data` argument is provided the `method` will be
set to `'POST'` automatically.
- **dumps_kwargs** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – Parameters that will be passed to underlying [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps) method which is used to serialize
data into JSON format.

**attributes*: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]**= ('url', 'callback', 'method', 'headers', 'body', 'cookies', 'meta', 'encoding', 'priority', 'dont_filter', 'errback', 'flags', 'cb_kwargs', 'dumps_kwargs')***

A tuple of [`str`](https://docs.python.org/3/library/stdtypes.html#str) objects containing the name of all public
attributes of the class that are also keyword parameters of the
`__init__()` method.

Currently used by `Request.replace()`, `Request.to_dict()` and
`request_from_dict()`.

### JsonRequest usage example

Sending a JSON POST request with a JSON payload:

```
data = {
    "name1": "value1",
    "name2": "value2",
}
yield JsonRequest(url="http://www.example.com/post/action", data=data)
```

## Response objects

***class*scrapy.http.Response(**args: Any*, ***kwargs: Any*)[[source]](../_modules/scrapy/http/response.html#Response)**

An object that represents an HTTP response, which is usually
downloaded (by the Downloader) and fed to the Spiders for processing.

**Parameters:**

- **url** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – the URL of this response
- **status** ([*int*](https://docs.python.org/3/library/functions.html#int)) – the HTTP status of the response. Defaults to `200`.
- **headers** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – the headers of this response. The dict values can be strings
(for single valued headers) or lists (for multi-valued headers).
- **body** ([*bytes*](https://docs.python.org/3/library/stdtypes.html#bytes)) – the response body. To access the decoded text as a string, use
`response.text` from an encoding-aware
Response subclass,
such as `TextResponse`.
- **flags** ([*list*](https://docs.python.org/3/library/stdtypes.html#list)) – is a list containing the initial values for the
`Response.flags` attribute. If given, the list will be shallow
copied.
- **request** (*scrapy.Request*) – the initial value of the `Response.request` attribute.
This represents the `Request` that generated this response.
- **certificate** ([*twisted.internet.ssl.Certificate*](https://docs.twisted.org/en/stable/api/twisted.internet.ssl.Certificate.html)) – an object representing the server’s SSL certificate.
- **ip_address** ([`ipaddress.IPv4Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address) or [`ipaddress.IPv6Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address)) – The IP address of the server from which the Response originated.
- **protocol** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – The protocol that was used to download the response.
For instance: “HTTP/1.0”, “HTTP/1.1”, “h2”

**url**

A string containing the URL of the response.

This attribute is read-only. To change the URL of a Response use
`replace()`.

**status**

An integer representing the HTTP status of the response. Example: `200`,
`404`.

**headers**

A dictionary-like (`scrapy.http.headers.Headers`) object which contains
the response headers. Values can be accessed using
`get()` to return the first header value with
the specified name or `getlist()` to return
all header values with the specified name. For example, this call will give you
all cookies in the headers:

```
response.headers.getlist('Set-Cookie')
```

**body**

The response body as bytes.

If you want the body as a string, use `TextResponse.text` (only
available in `TextResponse` and subclasses).

This attribute is read-only. To change the body of a Response use
`replace()`.

**request**

The `Request` object that generated this response. This attribute is
assigned in the Scrapy engine, after the response and the request have passed
through all [Downloader Middlewares](downloader-middleware.html#topics-downloader-middleware).
In particular, this means that:

- HTTP redirections will create a new request from the request before
redirection. It has the majority of the same metadata and original
request attributes and gets assigned to the redirected response
instead of the propagation of the original request.
- Response.request.url doesn’t always equal Response.url
- This attribute is only available in the spider code, and in the
[Spider Middlewares](spider-middleware.html#topics-spider-middleware), but not in
Downloader Middlewares (although you have the Request available there by
other means) and handlers of the [`response_downloaded`](signals.html#std-signal-response_downloaded) signal.

**meta**

A shortcut to the `meta` attribute of the
`Response.request` object (i.e. `self.request.meta`).

Unlike the `Response.request` attribute, the `Response.meta`
attribute is propagated along redirects and retries, so you will get
the original `Request.meta` sent from your spider.

`Request.meta` attribute

**cb_kwargs**

A shortcut to the `cb_kwargs` attribute of the
`Response.request` object (i.e. `self.request.cb_kwargs`).

Unlike the `Response.request` attribute, the
`Response.cb_kwargs` attribute is propagated along redirects and
retries, so you will get the original `Request.cb_kwargs` sent from your spider.

`Request.cb_kwargs` attribute

**flags**

A list that contains flags for this response. Flags are labels used for
tagging Responses. For example: `'cached'`, `'redirected`’, etc. And
they’re shown on the string representation of the Response (`__str__()`
method) which is used by the engine for logging.

**certificate**

A [`twisted.internet.ssl.Certificate`](https://docs.twisted.org/en/stable/api/twisted.internet.ssl.Certificate.html) object representing
the server’s SSL certificate.

Only populated for `https` responses, `None` otherwise.

**ip_address**

The IP address of the server from which the Response originated.

This attribute is currently only populated by the HTTP 1.1 download
handler, i.e. for `http(s)` responses. For other handlers,
`ip_address` is always `None`.

**protocol**

The protocol that was used to download the response.
For instance: “HTTP/1.0”, “HTTP/1.1”

This attribute is currently only populated by the HTTP download
handlers, i.e. for `http(s)` responses. For other handlers,
`protocol` is always `None`.

**attributes*: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]**= ('url', 'status', 'headers', 'body', 'flags', 'request', 'certificate', 'ip_address', 'protocol')***

A tuple of [`str`](https://docs.python.org/3/library/stdtypes.html#str) objects containing the name of all public
attributes of the class that are also keyword parameters of the
`__init__()` method.

Currently used by `Response.replace()`.

**copy()[[source]](../_modules/scrapy/http/response.html#Response.copy)**

Returns a new Response which is a copy of this Response.

**replace([*url*, *status*, *headers*, *body*, *request*, *flags*, *cls*])[[source]](../_modules/scrapy/http/response.html#Response.replace)**

Returns a Response object with the same members, except for those members
given new values by whichever keyword arguments are specified. The
attribute `Response.meta` is copied by default.

**urljoin(*url*)[[source]](../_modules/scrapy/http/response.html#Response.urljoin)**

Constructs an absolute url by combining the Response’s `url` with
a possible relative url.

This is a wrapper over [`urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin), it’s merely an alias for
making this call:

```
urllib.parse.urljoin(response.url, url)
```

**follow(*url: [str](https://docs.python.org/3/library/stdtypes.html#str) | [Link](link-extractors.html#scrapy.link.Link)*, *callback: CallbackT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *method: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'GET'*, *headers: Mapping[AnyStr, Any] | Iterable[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[AnyStr, Any]] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *body: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cookies: CookiesT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *meta: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *encoding: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = 'utf-8'*, *priority: [int](https://docs.python.org/3/library/functions.html#int) = 0*, *dont_filter: [bool](https://docs.python.org/3/library/functions.html#bool) = False*, *errback: Callable[[Failure], Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cb_kwargs: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *flags: [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None*) → Request[[source]](../_modules/scrapy/http/response.html#Response.follow)**

Return a `Request` instance to follow a link `url`.
It accepts the same arguments as `Request.__init__()` method,
but `url` can be a relative URL or a [`Link`](link-extractors.html#scrapy.link.Link) object,
not only an absolute URL.

`TextResponse` provides a `follow()`
method which supports selectors in addition to absolute/relative URLs
and Link objects.

**follow_all(*urls: Iterable[[str](https://docs.python.org/3/library/stdtypes.html#str) | [Link](link-extractors.html#scrapy.link.Link)]*, *callback: CallbackT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *method: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'GET'*, *headers: Mapping[AnyStr, Any] | Iterable[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[AnyStr, Any]] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *body: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cookies: CookiesT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *meta: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *encoding: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = 'utf-8'*, *priority: [int](https://docs.python.org/3/library/functions.html#int) = 0*, *dont_filter: [bool](https://docs.python.org/3/library/functions.html#bool) = False*, *errback: Callable[[Failure], Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cb_kwargs: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *flags: [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None*) → Iterable[Request][[source]](../_modules/scrapy/http/response.html#Response.follow_all)**

Return an iterable of `Request` instances to follow all links
in `urls`. It accepts the same arguments as `Request.__init__()` method,
but elements of `urls` can be relative URLs or [`Link`](link-extractors.html#scrapy.link.Link) objects,
not only absolute URLs.

`TextResponse` provides a `follow_all()`
method which supports selectors in addition to absolute/relative URLs
and Link objects.

## Response subclasses

Here is the list of available built-in Response subclasses. You can also
subclass the Response class to implement your own functionality.

### TextResponse objects

***class*scrapy.http.TextResponse(*url*[, *encoding*[, *...*]])[[source]](../_modules/scrapy/http/response/text.html#TextResponse)**

`TextResponse` objects adds encoding capabilities to the base
`Response` class, which is meant to be used only for binary data,
such as images, sounds or any media file.

`TextResponse` objects support a new `__init__()` method argument, in
addition to the base `Response` objects. The remaining functionality
is the same as for the `Response` class and is not documented here.

**Parameters:**

**encoding** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – is a string which contains the encoding to use for this
response. If you create a `TextResponse` object with a string as
body, it will be converted to bytes encoded using this encoding. If
*encoding* is `None` (default), the encoding will be looked up in the
response headers and body instead.

`TextResponse` objects support the following attributes in addition
to the standard `Response` ones:

**text**

Response body, as a string.

The same as `response.body.decode(response.encoding)`, but the
result is cached after the first call, so you can access
`response.text` multiple times without extra overhead.

`str(response.body)` is not a correct way to convert the response
body into a string:

```
>>> str(b"body")
"b'body'"
```

**encoding**

A string with the encoding of this response. The encoding is resolved by
trying the following mechanisms, in order:

1. the encoding passed in the `__init__()` method `encoding` argument
2. the encoding declared in the Content-Type HTTP header. If this
encoding is not valid (i.e. unknown), it is ignored and the next
resolution mechanism is tried.
3. the encoding declared in the response body. The TextResponse class
doesn’t provide any special functionality for this. However, the
`HtmlResponse` and `XmlResponse` classes do.
4. the encoding inferred by looking at the response body. This is the more
fragile method but also the last one tried.

**selector**

A [`Selector`](selectors.html#scrapy.Selector) instance using the response as
target. The selector is lazily instantiated on first access.

**attributes*: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]**= ('url', 'status', 'headers', 'body', 'flags', 'request', 'certificate', 'ip_address', 'protocol', 'encoding')***

A tuple of [`str`](https://docs.python.org/3/library/stdtypes.html#str) objects containing the name of all public
attributes of the class that are also keyword parameters of the
`__init__()` method.

Currently used by `Response.replace()`.

`TextResponse` objects support the following methods in addition to
the standard `Response` ones:

**jmespath(*query*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.jmespath)**

A shortcut to `TextResponse.selector.jmespath(query)`:

```
response.jmespath('object.[*]')
```

**xpath(*query*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.xpath)**

A shortcut to `TextResponse.selector.xpath(query)`:

```
response.xpath('//p')
```

**css(*query*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.css)**

A shortcut to `TextResponse.selector.css(query)`:

```
response.css('p')
```

**follow(*url: [str](https://docs.python.org/3/library/stdtypes.html#str) | [Link](link-extractors.html#scrapy.link.Link) | parsel.Selector*, *callback: CallbackT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *method: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'GET'*, *headers: Mapping[AnyStr, Any] | Iterable[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[AnyStr, Any]] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *body: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cookies: CookiesT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *meta: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *encoding: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *priority: [int](https://docs.python.org/3/library/functions.html#int) = 0*, *dont_filter: [bool](https://docs.python.org/3/library/functions.html#bool) = False*, *errback: Callable[[Failure], Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cb_kwargs: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *flags: [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None*) → Request[[source]](../_modules/scrapy/http/response/text.html#TextResponse.follow)**

Return a `Request` instance to follow a link `url`.
It accepts the same arguments as `Request.__init__()` method,
but `url` can be not only an absolute URL, but also

- a relative URL
- a [`Link`](link-extractors.html#scrapy.link.Link) object, e.g. the result of
[Link Extractors](link-extractors.html#topics-link-extractors)
- a [`Selector`](selectors.html#scrapy.Selector) object for a `<link>` or `<a>` element, e.g.
`response.css('a.my_link')[0]`
- an attribute [`Selector`](selectors.html#scrapy.Selector) (not SelectorList), e.g.
`response.css('a::attr(href)')[0]` or
`response.xpath('//img/@src')[0]`

See [A shortcut for creating Requests](../intro/tutorial.html#response-follow-example) for usage examples.

**follow_all(*urls: Iterable[[str](https://docs.python.org/3/library/stdtypes.html#str) | [Link](link-extractors.html#scrapy.link.Link)] | parsel.SelectorList | [None](https://docs.python.org/3/library/constants.html#None) = None*, *callback: CallbackT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *method: [str](https://docs.python.org/3/library/stdtypes.html#str) = 'GET'*, *headers: Mapping[AnyStr, Any] | Iterable[[tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[AnyStr, Any]] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *body: [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) | [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cookies: CookiesT | [None](https://docs.python.org/3/library/constants.html#None) = None*, *meta: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *encoding: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *priority: [int](https://docs.python.org/3/library/functions.html#int) = 0*, *dont_filter: [bool](https://docs.python.org/3/library/functions.html#bool) = False*, *errback: Callable[[Failure], Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *cb_kwargs: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), Any] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *flags: [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)] | [None](https://docs.python.org/3/library/constants.html#None) = None*, *css: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *xpath: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*) → Iterable[Request][[source]](../_modules/scrapy/http/response/text.html#TextResponse.follow_all)**

A generator that produces `Request` instances to follow all
links in `urls`. It accepts the same arguments as the `Request`’s
`__init__()` method, except that each `urls` element does not need to be
an absolute URL, it can be any of the following:

- a relative URL
- a [`Link`](link-extractors.html#scrapy.link.Link) object, e.g. the result of
[Link Extractors](link-extractors.html#topics-link-extractors)
- a [`Selector`](selectors.html#scrapy.Selector) object for a `<link>` or `<a>` element, e.g.
`response.css('a.my_link')[0]`
- an attribute [`Selector`](selectors.html#scrapy.Selector) (not SelectorList), e.g.
`response.css('a::attr(href)')[0]` or
`response.xpath('//img/@src')[0]`

In addition, `css` and `xpath` arguments are accepted to perform the link extraction
within the `follow_all()` method (only one of `urls`, `css` and `xpath` is accepted).

Note that when passing a `SelectorList` as argument for the `urls` parameter or
using the `css` or `xpath` parameters, this method will not produce requests for
selectors from which links cannot be obtained (for instance, anchor tags without an
`href` attribute)

**json()[[source]](../_modules/scrapy/http/response/text.html#TextResponse.json)**

Deserialize a JSON document to a Python object.

Returns a Python object from deserialized JSON document.
The result is cached after the first call.

**urljoin(*url*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.urljoin)**

Constructs an absolute url by combining the Response’s base url with
a possible relative url. The base url shall be extracted from the
`<base>` tag, or just `Response.url` if there is no such
tag.

### HtmlResponse objects

***class*scrapy.http.HtmlResponse(*url*[, *...*])[[source]](../_modules/scrapy/http/response/html.html#HtmlResponse)**

The `HtmlResponse` class is a subclass of `TextResponse`
which adds encoding auto-discovering support by looking into the HTML [meta
http-equiv](https://www.w3schools.com/TAGS/att_meta_http_equiv.asp) attribute. See `TextResponse.encoding`.

### XmlResponse objects

***class*scrapy.http.XmlResponse(*url*[, *...*])[[source]](../_modules/scrapy/http/response/xml.html#XmlResponse)**

The `XmlResponse` class is a subclass of `TextResponse` which
adds encoding auto-discovering support by looking into the XML declaration
line. See `TextResponse.encoding`.

### JsonResponse objects

***class*scrapy.http.JsonResponse(*url*[, *...*])[[source]](../_modules/scrapy/http/response/json.html#JsonResponse)**

The `JsonResponse` class is a subclass of `TextResponse`
that is used when the response has a [JSON MIME type](https://mimesniff.spec.whatwg.org/#json-mime-type) in its Content-Type
header.
