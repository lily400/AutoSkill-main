# Settings — Scrapy 2.14.1 documentation

- Settings
- [Edit on GitHub](https://github.com/scrapy/scrapy/blob/master/docs/topics/settings.rst)

---

# Settings

The Scrapy settings allows you to customize the behaviour of all Scrapy
components, including the core, extensions, pipelines and spiders themselves.

The infrastructure of the settings provides a global namespace of key-value mappings
that the code can use to pull configuration values from. The settings can be
populated through different mechanisms, which are described below.

The settings are also the mechanism for selecting the currently active Scrapy
project (in case you have many).

For a list of available built-in settings see: Built-in settings reference.

## Designating the settings

When you use Scrapy, you have to tell it which settings you’re using. You can
do this by using an environment variable, `SCRAPY_SETTINGS_MODULE`.

The value of `SCRAPY_SETTINGS_MODULE` should be in Python path syntax, e.g.
`myproject.settings`. Note that the settings module should be on the
Python [import search path](https://docs.python.org/3/tutorial/modules.html#tut-searchpath).

## Populating the settings

Settings can be populated using different mechanisms, each of which has a
different precedence:

> 1. Command-line settings (highest precedence)
> 2. Spider settings
> 3. Project settings
> 4. Add-on settings
> 5. Command-specific default settings
> 6. Global default settings (lowest precedence)

### 1. Command-line settings

Settings set in the command line have the highest precedence, overriding any
other settings.

You can explicitly override one or more settings using the `-s` (or
`--set`) command-line option.

Example:

```
scrapy crawl myspider -s LOG_LEVEL=INFO -s LOG_FILE=scrapy.log
```

### 2. Spider settings

[Spiders](spiders.html#topics-spiders) can define their own settings that will take
precedence and override the project ones.

Pre-crawler settings cannot be defined
per spider, and reactor settings should not have
a different value per spider when [running multiple spiders in the
same process](practices.html#run-multiple-spiders).

One way to do so is by setting their [`custom_settings`](spiders.html#scrapy.Spider.custom_settings)
attribute:

```
import scrapy

class MySpider(scrapy.Spider):
    name = "myspider"

    custom_settings = {
        "SOME_SETTING": "some value",
    }
```

It’s often better to implement [`update_settings()`](spiders.html#scrapy.Spider.update_settings) instead,
and settings set there should use the `"spider"` priority explicitly:

```
import scrapy

class MySpider(scrapy.Spider):
    name = "myspider"

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("SOME_SETTING", "some value", priority="spider")
```

Added in version 2.11.

It’s also possible to modify the settings in the
[`from_crawler()`](spiders.html#scrapy.Spider.from_crawler) method, e.g. based on [spider
arguments](spiders.html#spiderargs) or other logic:

```
import scrapy

class MySpider(scrapy.Spider):
    name = "myspider"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        if "some_argument" in kwargs:
            spider.settings.set(
                "SOME_SETTING", kwargs["some_argument"], priority="spider"
            )
        return spider
```

### 3. Project settings

Scrapy projects include a settings module, usually a file called
`settings.py`, where you should populate most settings that apply to all your
spiders.

Designating the settings

### 4. Add-on settings

[Add-ons](addons.html#topics-addons) can modify settings. They should do this with
`"addon"` priority where possible.

### 5. Command-specific default settings

Each [Scrapy command](commands.html#topics-commands) can have its own default settings,
which override the global default settings.

Those command-specific default settings are specified in the
`default_settings` attribute of each command class.

### 6. Default global settings

The `scrapy.settings.default_settings` module defines global default values
for some built-in settings.

[`startproject`](commands.html#std-command-startproject) generates a `settings.py` file that sets
some settings to different values.

The reference documentation of settings indicates the default value if one
exists. If [`startproject`](commands.html#std-command-startproject) sets a value, that value is documented
as default, and the value from `scrapy.settings.default_settings` is
documented as “fallback”.

## Compatibility with pickle

Setting values must be [picklable](https://docs.python.org/3/library/pickle.html#pickle-picklable).

## Import paths and classes

When a setting references a callable object to be imported by Scrapy, such as a
class or a function, there are two different ways you can specify that object:

- As a string containing the import path of that object
- As the object itself

For example:

```
from mybot.pipelines.validate import ValidateMyItem

ITEM_PIPELINES = {
    # passing the classname...
    ValidateMyItem: 300,
    # ...equals passing the class path
    "mybot.pipelines.validate.ValidateMyItem": 300,
}
```

Passing non-callable objects is not supported.

## How to access settings

In a spider, settings are available through `self.settings`:

```
class MySpider(scrapy.Spider):
    name = "myspider"
    start_urls = ["http://example.com"]

    def parse(self, response):
        print(f"Existing settings: {self.settings.attributes.keys()}")
```

The `settings` attribute is set in the base Spider class after the spider
is initialized. If you want to use settings before the initialization
(e.g., in your spider’s `__init__()` method), you’ll need to override the
[`from_crawler()`](spiders.html#scrapy.Spider.from_crawler) method.

[Components](components.html#topics-components) can also [access settings](components.html#component-settings).

The `settings` object can be used like a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) (e.g.
`settings["LOG_ENABLED"]`). However, to support non-string setting values,
which may be passed from the command line as strings, it is recommended to use
one of the methods provided by the [`Settings`](api.html#scrapy.settings.Settings) API.

## Component priority dictionaries

A **component priority dictionary** is a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) where keys are
[components](components.html#topics-components) and values are component priorities. For
example:

```
{
    "path.to.ComponentA": None,
    ComponentB: 100,
}
```

A component can be specified either as a class object or through an import
path.

Component priority dictionaries are regular [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) objects.
Be careful not to define the same component more than once, e.g. with
different import path strings or defining both an import path and a
[`type`](https://docs.python.org/3/library/functions.html#type) object.

A priority can be an [`int`](https://docs.python.org/3/library/functions.html#int) or [`None`](https://docs.python.org/3/library/constants.html#None).

A component with priority 1 goes *before* a component with priority 2. What
going before entails, however, depends on the corresponding setting. For
example, in the `DOWNLOADER_MIDDLEWARES` setting, components have
their
[`process_request()`](downloader-middleware.html#scrapy.downloadermiddlewares.DownloaderMiddleware.process_request)
method executed before that of later components, but have their
[`process_response()`](downloader-middleware.html#scrapy.downloadermiddlewares.DownloaderMiddleware.process_response)
method executed after that of later components.

A component with priority [`None`](https://docs.python.org/3/library/constants.html#None) is disabled.

Some component priority dictionaries get merged with some built-in value. For
example, `DOWNLOADER_MIDDLEWARES` is merged with
`DOWNLOADER_MIDDLEWARES_BASE`. This is where [`None`](https://docs.python.org/3/library/constants.html#None) comes in
handy, allowing you to disable a component from the base setting in the regular
setting:

```
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": None,
}
```

## Special settings

The following settings work slightly differently than all other settings.

### Pre-crawler settings

**Pre-crawler settings** are settings used before the
[`Crawler`](api.html#scrapy.crawler.Crawler) object is created.

These settings cannot be set from a spider.

These settings are `SPIDER_LOADER_CLASS` and settings used by the
corresponding [component](components.html#topics-components), e.g.
`SPIDER_MODULES` and `SPIDER_LOADER_WARN_ONLY` for the
default component.

### Reactor settings

**Reactor settings** are settings tied to the [Twisted reactor](https://docs.twisted.org/en/stable/core/howto/reactor-basics.html).

These settings can be defined from a spider. However, because only 1 reactor
can be used per process, these settings cannot use a different value per spider
when [running multiple spiders in the same process](practices.html#run-multiple-spiders).

In general, if different spiders define different values, the first defined
value is used. However, if two spiders request a different reactor, an
exception is raised.

These settings are:

- `ASYNCIO_EVENT_LOOP` (not possible to set per-spider when using
[`AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess), see below)
- `DNS_RESOLVER` and settings used by the corresponding
component, e.g. `DNSCACHE_ENABLED`, `DNSCACHE_SIZE`
and `DNS_TIMEOUT` for the default one.
- `REACTOR_THREADPOOL_MAXSIZE`
- `TWISTED_REACTOR` (ignored when using
[`AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess), see below)

`ASYNCIO_EVENT_LOOP` and `TWISTED_REACTOR` are used upon
installing the reactor. The rest of the settings are applied when starting
the reactor.

There is an additional restriction for `TWISTED_REACTOR` and
`ASYNCIO_EVENT_LOOP` when using
[`AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess): when this class is instantiated,
it installs [`AsyncioSelectorReactor`](https://docs.twisted.org/en/stable/api/twisted.internet.asyncioreactor.AsyncioSelectorReactor.html),
ignoring the value of `TWISTED_REACTOR` and using the value of
`ASYNCIO_EVENT_LOOP` that was passed to
`AsyncCrawlerProcess.__init__()`. If a different value for
`TWISTED_REACTOR` or `ASYNCIO_EVENT_LOOP` is provided later,
e.g. in per-spider settings, an exception will be
raised.

## Built-in settings reference

Here’s a list of all available Scrapy settings, in alphabetical order, along
with their default values and the scope where they apply.

The scope, where available, shows where the setting is being used, if it’s tied
to any particular component. In that case the module of that component will be
shown, typically an extension, middleware or pipeline. It also means that the
component must be enabled in order for the setting to have any effect.

### ADDONS

Default: `{}`

A dict containing paths to the add-ons enabled in your project and their
priorities. For more information, see [Add-ons](addons.html#topics-addons).

### AWS_ACCESS_KEY_ID

Default: `None`

The AWS access key used by code that requires access to [Amazon Web services](https://aws.amazon.com/),
such as the [S3 feed storage backend](feed-exports.html#topics-feed-storage-s3).

### AWS_SECRET_ACCESS_KEY

Default: `None`

The AWS secret key used by code that requires access to [Amazon Web services](https://aws.amazon.com/),
such as the [S3 feed storage backend](feed-exports.html#topics-feed-storage-s3).

### AWS_SESSION_TOKEN

Default: `None`

The AWS security token used by code that requires access to [Amazon Web services](https://aws.amazon.com/),
such as the [S3 feed storage backend](feed-exports.html#topics-feed-storage-s3), when using
[temporary security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html).

### AWS_ENDPOINT_URL

Default: `None`

Endpoint URL used for S3-like storage, for example Minio or s3.scality.

### AWS_USE_SSL

Default: `None`

Use this option if you want to disable SSL connection for communication with
S3 or S3-like storage. By default SSL will be used.

### AWS_VERIFY

Default: `None`

Verify SSL connection between Scrapy and S3 or S3-like storage. By default
SSL verification will occur.

### AWS_REGION_NAME

Default: `None`

The name of the region associated with the AWS client.

### ASYNCIO_EVENT_LOOP

Default: `None`

Import path of a given `asyncio` event loop class.

If the asyncio reactor is enabled (see `TWISTED_REACTOR`) this setting can be used to specify the
asyncio event loop to be used with it. Set the setting to the import path of the
desired asyncio event loop class. If the setting is set to `None` the default asyncio
event loop will be used.

If you are installing the asyncio reactor manually using the `install_reactor()`
function, you can use the `event_loop_path` parameter to indicate the import path of the event loop
class to be used.

Note that the event loop class must inherit from [`asyncio.AbstractEventLoop`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.AbstractEventLoop).

Please be aware that, when using a non-default event loop
(either defined via `ASYNCIO_EVENT_LOOP` or installed with
`install_reactor()`), Scrapy will call
[`asyncio.set_event_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.set_event_loop), which will set the specified event loop
as the current loop for the current OS thread.

### BOT_NAME

Default: `<project name>` (fallback: `'scrapybot'`)

The name of the bot implemented by this Scrapy project (also known as the
project name). This name will be used for the logging too.

It’s automatically populated with your project name when you create your
project with the [`startproject`](commands.html#std-command-startproject) command.

### CONCURRENT_ITEMS

Default: `100`

Maximum number of concurrent items (per response) to process in parallel in
[item pipelines](item-pipeline.html#topics-item-pipeline).

### CONCURRENT_REQUESTS

Default: `16`

The maximum number of concurrent (i.e. simultaneous) requests that will be
performed by the Scrapy downloader.

### CONCURRENT_REQUESTS_PER_DOMAIN

Default: `1` (fallback: `8`)

The maximum number of concurrent (i.e. simultaneous) requests that will be
performed to any single domain.

See also: [AutoThrottle extension](autothrottle.html#topics-autothrottle) and its
[`AUTOTHROTTLE_TARGET_CONCURRENCY`](autothrottle.html#std-setting-AUTOTHROTTLE_TARGET_CONCURRENCY) option.

### DEFAULT_DROPITEM_LOG_LEVEL

Default: `"WARNING"`

Default [log level](https://docs.python.org/3/library/logging.html#levels) of messages about dropped items.

When an item is dropped by raising [`scrapy.exceptions.DropItem`](exceptions.html#scrapy.exceptions.DropItem) from the
[`process_item()`](item-pipeline.html#process_item) method of an [item pipeline](item-pipeline.html#topics-item-pipeline),
a message is logged, and by default its log level is the one configured in this
setting.

You may specify this log level as an integer (e.g. `20`), as a log level
constant (e.g. `logging.INFO`) or as a string with the name of a log level
constant (e.g. `"INFO"`).

When writing an item pipeline, you can force a different log level by setting
`scrapy.exceptions.DropItem.log_level` in your
[`scrapy.exceptions.DropItem`](exceptions.html#scrapy.exceptions.DropItem) exception. For example:

```
from scrapy.exceptions import DropItem

class MyPipeline:
    def process_item(self, item):
        if not item.get("price"):
            raise DropItem("Missing price data", log_level="INFO")
        return item
```

### DEFAULT_ITEM_CLASS

Default: `'scrapy.Item'`

The default class that will be used for instantiating items in the [the
Scrapy shell](shell.html#topics-shell).

### DEFAULT_REQUEST_HEADERS

Default:

```
{
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}
```

The default headers used for Scrapy HTTP Requests. They’re populated in the
[`DefaultHeadersMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware).

Cookies set via the `Cookie` header are not considered by the
[CookiesMiddleware](downloader-middleware.html#cookies-mw). If you need to set cookies for a request, use the
[`Request.cookies`](request-response.html#scrapy.Request) parameter. This is a known
current limitation that is being worked on.

### DEPTH_LIMIT

Default: `0`

Scope: `scrapy.spidermiddlewares.depth.DepthMiddleware`

The maximum depth that will be allowed to crawl for any site. If zero, no limit
will be imposed.

### DEPTH_PRIORITY

Default: `0`

Scope: `scrapy.spidermiddlewares.depth.DepthMiddleware`

An integer that is used to adjust the [`priority`](request-response.html#scrapy.Request.priority) of
a [`Request`](request-response.html#scrapy.Request) based on its depth.

The priority of a request is adjusted as follows:

```
request.priority = request.priority - (depth * DEPTH_PRIORITY)
```

As depth increases, positive values of `DEPTH_PRIORITY` decrease request
priority (BFO), while negative values increase request priority (DFO). See
also [Does Scrapy crawl in breadth-first or depth-first order?](../faq.html#faq-bfo-dfo).

This setting adjusts priority **in the opposite way** compared to
other priority settings `REDIRECT_PRIORITY_ADJUST`
and [`RETRY_PRIORITY_ADJUST`](downloader-middleware.html#std-setting-RETRY_PRIORITY_ADJUST).

### DEPTH_STATS_VERBOSE

Default: `False`

Scope: `scrapy.spidermiddlewares.depth.DepthMiddleware`

Whether to collect verbose depth stats. If this is enabled, the number of
requests for each depth is collected in the stats.

### DNSCACHE_ENABLED

Default: `True`

Whether to enable DNS in-memory cache.

### DNSCACHE_SIZE

Default: `10000`

DNS in-memory cache size.

### DNS_RESOLVER

Default: `'scrapy.resolver.CachingThreadedResolver'`

The class to be used to resolve DNS names. The default `scrapy.resolver.CachingThreadedResolver`
supports specifying a timeout for DNS requests via the `DNS_TIMEOUT` setting,
but works only with IPv4 addresses. Scrapy provides an alternative resolver,
`scrapy.resolver.CachingHostnameResolver`, which supports IPv4/IPv6 addresses but does not
take the `DNS_TIMEOUT` setting into account.

### DNS_TIMEOUT

Default: `60`

Timeout for processing of DNS queries in seconds. Float is supported.

### DOWNLOADER

Default: `'scrapy.core.downloader.Downloader'`

The downloader to use for crawling.

### DOWNLOADER_CLIENTCONTEXTFACTORY

Default: `'scrapy.core.downloader.contextfactory.ScrapyClientContextFactory'`

Represents the classpath to the ContextFactory to use.

Here, “ContextFactory” is a Twisted term for SSL/TLS contexts, defining
the TLS/SSL protocol version to use, whether to do certificate verification,
or even enable client-side authentication (and various other things).

Scrapy default context factory **does NOT perform remote server
certificate verification**. This is usually fine for web scraping.

If you do need remote server certificate verification enabled,
Scrapy also has another context factory class that you can set,
`'scrapy.core.downloader.contextfactory.BrowserLikeContextFactory'`,
which uses the platform’s certificates to validate remote endpoints.

If you do use a custom ContextFactory, make sure its `__init__` method
accepts a `method` parameter (this is the `OpenSSL.SSL` method mapping
`DOWNLOADER_CLIENT_TLS_METHOD`), a `tls_verbose_logging`
parameter (`bool`) and a `tls_ciphers` parameter (see
`DOWNLOADER_CLIENT_TLS_CIPHERS`).

This setting is specific to the built-in Twisted-based download handlers:
[`scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler) and
[`scrapy.core.downloader.handlers.http2.H2DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http2.H2DownloadHandler).

### DOWNLOADER_CLIENT_TLS_CIPHERS

Default: `'DEFAULT'`

Use this setting to customize the TLS/SSL ciphers used by the HTTPS download
handler.

The setting should contain a string in the [OpenSSL cipher list format](https://docs.openssl.org/master/man1/openssl-ciphers/#cipher-list-format),
these ciphers will be used as client ciphers. Changing this setting may be
necessary to access certain HTTPS websites: for example, you may need to use
`'DEFAULT:!DH'` for a website with weak DH parameters or enable a
specific cipher that is not included in `DEFAULT` if a website requires it.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers. Moreover, for the built-in Twisted-based
download handlers
([`scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler) and
[`scrapy.core.downloader.handlers.http2.H2DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http2.H2DownloadHandler)) it needs
to be implemented in the `DOWNLOADER_CLIENTCONTEXTFACTORY` class.

### DOWNLOADER_CLIENT_TLS_METHOD

Default: `'TLS'`

Use this setting to customize the TLS/SSL method used by the HTTPS download
handler.

This setting must be one of these string values:

- `'TLS'`: maps to OpenSSL’s `TLS_method()` (a.k.a `SSLv23_method()`),
which allows protocol negotiation, starting from the highest supported
by the platform; **default, recommended**
- `'TLSv1.0'`: this value forces HTTPS connections to use TLS version 1.0 ;
set this if you want the behavior of Scrapy<1.1
- `'TLSv1.1'`: forces TLS version 1.1
- `'TLSv1.2'`: forces TLS version 1.2

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers. Moreover, for the built-in Twisted-based
download handlers
([`scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler) and
[`scrapy.core.downloader.handlers.http2.H2DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http2.H2DownloadHandler)) it needs
to be implemented in the `DOWNLOADER_CLIENTCONTEXTFACTORY` class.

### DOWNLOADER_CLIENT_TLS_VERBOSE_LOGGING

Default: `False`

Setting this to `True` will enable DEBUG level messages about TLS connection
parameters after establishing HTTPS connections. The kind of information logged
depends on the implementation of the download handler and the versions of
the TLS-related libraries.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers. Moreover, for the built-in Twisted-based
download handlers
([`scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler) and
[`scrapy.core.downloader.handlers.http2.H2DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http2.H2DownloadHandler)) it needs
to be implemented in the `DOWNLOADER_CLIENTCONTEXTFACTORY` class.

### DOWNLOADER_MIDDLEWARES

Default:: `{}`

A dict containing the downloader middlewares enabled in your project, and their
orders. For more info see [Activating a downloader middleware](downloader-middleware.html#topics-downloader-middleware-setting).

### DOWNLOADER_MIDDLEWARES_BASE

Default:

```
{
    "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": 50,
    "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
    "scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware": 300,
    "scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware": 350,
    "scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware": 400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": 500,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
    "scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware": 560,
    "scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware": 580,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 590,
    "scrapy.downloadermiddlewares.redirect.RedirectMiddleware": 600,
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 700,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 750,
    "scrapy.downloadermiddlewares.stats.DownloaderStats": 850,
    "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": 900,
}
```

A dict containing the downloader middlewares enabled by default in Scrapy. Low
orders are closer to the engine, high orders are closer to the downloader. You
should never modify this setting in your project, modify
`DOWNLOADER_MIDDLEWARES` instead. For more info see
[Activating a downloader middleware](downloader-middleware.html#topics-downloader-middleware-setting).

### DOWNLOADER_STATS

Default: `True`

Whether to enable downloader stats collection.

### DOWNLOAD_DELAY

Default: `1` (fallback: `0`)

Minimum seconds to wait between 2 consecutive requests to the same domain.

Use `DOWNLOAD_DELAY` to throttle your crawling speed, to avoid hitting
servers too hard.

Decimal numbers are supported. For example, to send a maximum of 4 requests
every 10 seconds:

```
DOWNLOAD_DELAY = 2.5
```

This setting is also affected by the `RANDOMIZE_DOWNLOAD_DELAY`
setting, which is enabled by default.

Note that `DOWNLOAD_DELAY` can lower the effective per-domain
concurrency below `CONCURRENT_REQUESTS_PER_DOMAIN`. If the response
time of a domain is lower than `DOWNLOAD_DELAY`, the effective
concurrency for that domain is 1. When testing throttling configurations, it
usually makes sense to lower `CONCURRENT_REQUESTS_PER_DOMAIN` first,
and only increase `DOWNLOAD_DELAY` once
`CONCURRENT_REQUESTS_PER_DOMAIN` is 1 but a higher throttling is
desired.

This delay can be set per spider using `download_delay` spider attribute.

It is also possible to change this setting per domain, although it requires
non-trivial code. See the implementation of the [AutoThrottle](autothrottle.html#topics-autothrottle) extension for an example.

### DOWNLOAD_HANDLERS

Default: `{}`

A dict containing the [download handlers](download-handlers.html#topics-download-handlers)
enabled in your project.

See `DOWNLOAD_HANDLERS_BASE` for example format.

### DOWNLOAD_HANDLERS_BASE

Default:

```
{
    "data": "scrapy.core.downloader.handlers.datauri.DataURIDownloadHandler",
    "file": "scrapy.core.downloader.handlers.file.FileDownloadHandler",
    "http": "scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler",
    "https": "scrapy.core.downloader.handlers.http11.HTTP11DownloadHandler",
    "s3": "scrapy.core.downloader.handlers.s3.S3DownloadHandler",
    "ftp": "scrapy.core.downloader.handlers.ftp.FTPDownloadHandler",
}
```

A dict containing the [download handlers](download-handlers.html#topics-download-handlers)
enabled by default in Scrapy. You should never modify this setting in your
project, modify `DOWNLOAD_HANDLERS` instead.

You can disable any of these download handlers by assigning `None` to their
URI scheme in `DOWNLOAD_HANDLERS`. E.g., to disable the built-in FTP
handler (without replacement), place this in your `settings.py`:

```
DOWNLOAD_HANDLERS = {
    "ftp": None,
}
```

### DOWNLOAD_SLOTS

Default: `{}`

Allows to define concurrency/delay parameters on per slot (domain) basis:

> ```
> DOWNLOAD_SLOTS = {
>     "quotes.toscrape.com": {"concurrency": 1, "delay": 2, "randomize_delay": False},
>     "books.toscrape.com": {"delay": 3, "randomize_delay": False},
> }
> ```

For other downloader slots default settings values will be used:

- `DOWNLOAD_DELAY`: `delay`
- `CONCURRENT_REQUESTS_PER_DOMAIN`: `concurrency`
- `RANDOMIZE_DOWNLOAD_DELAY`: `randomize_delay`

### DOWNLOAD_TIMEOUT

Default: `180`

The amount of time (in secs) that the downloader will wait before timing out.

This timeout can be per-request using the [`download_timeout`](request-response.html#std-reqmeta-download_timeout)
[`Request.meta`](request-response.html#scrapy.Request.meta) key.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers.

### DOWNLOAD_MAXSIZE

Default: `1073741824` (1 GiB)

The maximum response body size (in bytes) allowed. Bigger responses are
aborted and ignored.

This applies both before and after compression. If decompressing a response
body would exceed this limit, decompression is aborted and the response is
ignored.

Use `0` to disable this limit.

This limit can be set per-request using the `download_maxsize`
[`Request.meta`](request-response.html#scrapy.Request.meta) key.

Checking responses before decompressing them needs to be implemented inside
the [download handler](download-handlers.html#topics-download-handlers), so it’s not
guaranteed to be supported by all 3rd-party handlers.

### DOWNLOAD_WARNSIZE

Default: `33554432` (32 MiB)

If the size of a response exceeds this value, before or after compression, a
warning will be logged about it.

Use `0` to disable this limit.

This limit can be set per-request using the `download_warnsize`
[`Request.meta`](request-response.html#scrapy.Request.meta) key.

Checking responses before decompressing them needs to be implemented inside
the [download handler](download-handlers.html#topics-download-handlers), so it’s not
guaranteed to be supported by all 3rd-party handlers.

### DOWNLOAD_FAIL_ON_DATALOSS

Default: `True`

Whether or not to fail on broken responses, that is, declared
`Content-Length` does not match content sent by the server or chunked
response was not properly finish. If `True`, these responses raise a
`ResponseFailed([_DataLoss])` error. If `False`, these responses
are passed through and the flag `dataloss` is added to the response, i.e.:
`'dataloss' in response.flags` is `True`.

Optionally, this can be set per-request basis by using the
[`download_fail_on_dataloss`](request-response.html#std-reqmeta-download_fail_on_dataloss) Request.meta key to `False`.

A broken response, or data loss error, may happen under several
circumstances, from server misconfiguration to network errors to data
corruption. It is up to the user to decide if it makes sense to process
broken responses considering they may contain partial or incomplete content.
If [`RETRY_ENABLED`](downloader-middleware.html#std-setting-RETRY_ENABLED) is `True` and this setting is set to `True`,
the `ResponseFailed([_DataLoss])` failure will be retried as usual.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers.

This setting is ignored by the
[`H2DownloadHandler`](download-handlers.html#scrapy.core.downloader.handlers.http2.H2DownloadHandler)
[download handler](download-handlers.html#topics-download-handlers). In case of a data loss
error, the corresponding HTTP/2 connection may be corrupted, affecting other
requests that use the same connection; hence, a `ResponseFailed([InvalidBodyLengthError])`
failure is always raised for every request that was using that connection.

### DUPEFILTER_CLASS

Default: `'scrapy.dupefilters.RFPDupeFilter'`

The class used to detect and filter duplicate requests.

The default, `RFPDupeFilter`, filters based on the
[`REQUEST_FINGERPRINTER_CLASS`](request-response.html#std-setting-REQUEST_FINGERPRINTER_CLASS) setting.

To change how duplicates are checked, you can point `DUPEFILTER_CLASS`
to a custom subclass of `RFPDupeFilter` that
overrides its `__init__` method to use a [different request
fingerprinting class](request-response.html#custom-request-fingerprinter). For example:

```
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import fingerprint

class CustomRequestFingerprinter:
    def fingerprint(self, request):
        return fingerprint(request, include_headers=["X-ID"])

class CustomDupeFilter(RFPDupeFilter):

    def __init__(self, path=None, debug=False, *, fingerprinter=None):
        super().__init__(
            path=path, debug=debug, fingerprinter=CustomRequestFingerprinter()
        )
```

To disable duplicate request filtering set `DUPEFILTER_CLASS` to
`'scrapy.dupefilters.BaseDupeFilter'`. Note that not filtering out duplicate
requests may cause crawling loops. It is usually better to set
the `dont_filter` parameter to `True` on the `__init__` method of a
specific [`Request`](request-response.html#scrapy.Request) object that should not be filtered out.

A class assigned to `DUPEFILTER_CLASS` must implement the following
interface:

```
class MyDupeFilter:

    @classmethod
    def from_crawler(cls, crawler):
        """Returns an instance of this duplicate request filtering class
        based on the current Crawler instance."""
        return cls()

    def request_seen(self, request):
        """Returns ``True`` if *request* is a duplicate of another request
        seen in a previous call to :meth:`request_seen`, or ``False``
        otherwise."""
        return False

    def open(self):
        """Called before the spider opens. It may return a deferred."""
        pass

    def close(self, reason):
        """Called before the spider closes. It may return a deferred."""
        pass

    def log(self, request, spider):
        """Logs that a request has been filtered out.

        It is called right after a call to :meth:`request_seen` that
        returns ``True``.

        If :meth:`request_seen` always returns ``False``, such as in the
        case of :class:`~scrapy.dupefilters.BaseDupeFilter`, this method
        may be omitted.
        """
        pass
```

***class*scrapy.dupefilters.BaseDupeFilter[[source]](../_modules/scrapy/dupefilters.html#BaseDupeFilter)**

Dummy duplicate request filtering class (`DUPEFILTER_CLASS`)
that does not filter out any request.

***class*scrapy.dupefilters.RFPDupeFilter(*path: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*, *debug: [bool](https://docs.python.org/3/library/functions.html#bool) = False*, ***, *fingerprinter: RequestFingerprinterProtocol | [None](https://docs.python.org/3/library/constants.html#None) = None*)[[source]](../_modules/scrapy/dupefilters.html#RFPDupeFilter)**

Duplicate request filtering class (`DUPEFILTER_CLASS`) that
filters out requests with the canonical
([`w3lib.url.canonicalize_url()`](https://w3lib.readthedocs.io/en/latest/w3lib.html#w3lib.url.canonicalize_url)) `url`,
`method` and `body`.

### DUPEFILTER_DEBUG

Default: `False`

By default, `RFPDupeFilter` only logs the first duplicate request.
Setting `DUPEFILTER_DEBUG` to `True` will make it log all duplicate requests.

### EDITOR

Default: `vi` (on Unix systems) or the IDLE editor (on Windows)

The editor to use for editing spiders with the [`edit`](commands.html#std-command-edit) command.
Additionally, if the `EDITOR` environment variable is set, the [`edit`](commands.html#std-command-edit)
command will prefer it over the default setting.

### EXTENSIONS

Default:: `{}`

Component priority dictionary of
enabled extensions. See [Extensions](extensions.html#topics-extensions).

### EXTENSIONS_BASE

Default:

```
{
    "scrapy.extensions.corestats.CoreStats": 0,
    "scrapy.extensions.telnet.TelnetConsole": 0,
    "scrapy.extensions.memusage.MemoryUsage": 0,
    "scrapy.extensions.memdebug.MemoryDebugger": 0,
    "scrapy.extensions.closespider.CloseSpider": 0,
    "scrapy.extensions.feedexport.FeedExporter": 0,
    "scrapy.extensions.logstats.LogStats": 0,
    "scrapy.extensions.spiderstate.SpiderState": 0,
    "scrapy.extensions.throttle.AutoThrottle": 0,
}
```

A dict containing the extensions available by default in Scrapy, and their
orders. This setting contains all stable built-in extensions. Keep in mind that
some of them need to be enabled through a setting.

For more information See the [extensions user guide](extensions.html#topics-extensions)
and the [list of available extensions](extensions.html#topics-extensions-ref).

### FEED_TEMPDIR

The Feed Temp dir allows you to set a custom folder to save crawler
temporary files before uploading with [FTP feed storage](feed-exports.html#topics-feed-storage-ftp) and
[Amazon S3](feed-exports.html#topics-feed-storage-s3).

### FEED_STORAGE_GCS_ACL

The Access Control List (ACL) used when storing items to [Google Cloud Storage](feed-exports.html#topics-feed-storage-gcs).
For more information on how to set this value, please refer to the column *JSON API* in [Google Cloud documentation](https://cloud.google.com/storage/docs/access-control/lists).

### FORCE_CRAWLER_PROCESS

Default: `False`

If `False`, [Scrapy commands that need a CrawlerProcess](commands.html#topics-commands-crawlerprocess) will decide between using
[`scrapy.crawler.AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess) and
[`scrapy.crawler.CrawlerProcess`](api.html#scrapy.crawler.CrawlerProcess) based on the value of the
`TWISTED_REACTOR` setting, but ignoring its value in per-spider
settings.

If `True`, these commands will always use
[`CrawlerProcess`](api.html#scrapy.crawler.CrawlerProcess).

Set this to `True` if you want to set `TWISTED_REACTOR` to a
non-default value in per-spider settings.

### FTP_PASSIVE_MODE

Default: `True`

Whether or not to use passive mode when initiating FTP transfers.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers.

### FTP_PASSWORD

Default: `"guest"`

The password to use for FTP connections when there is no `"ftp_password"`
in `Request` meta.

Paraphrasing [RFC 1635](https://datatracker.ietf.org/doc/html/rfc1635), although it is common to use either the password
“guest” or one’s e-mail address for anonymous FTP,
some FTP servers explicitly ask for the user’s e-mail address
and will not allow login with the “guest” password.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers.

### FTP_USER

Default: `"anonymous"`

The username to use for FTP connections when there is no `"ftp_user"`
in `Request` meta.

Handling of this setting needs to be implemented inside the [download
handler](download-handlers.html#topics-download-handlers), so it’s not guaranteed to be supported
by all 3rd-party handlers.

### GCS_PROJECT_ID

Default: `None`

The Project ID that will be used when storing data on [Google Cloud Storage](https://cloud.google.com/storage/).

### ITEM_PIPELINES

Default: `{}`

A dict containing the item pipelines to use, and their orders. Order values are
arbitrary, but it is customary to define them in the 0-1000 range. Lower orders
process before higher orders.

Example:

```
ITEM_PIPELINES = {
    "mybot.pipelines.validate.ValidateMyItem": 300,
    "mybot.pipelines.validate.StoreMyItem": 800,
}
```

### ITEM_PIPELINES_BASE

Default: `{}`

A dict containing the pipelines enabled by default in Scrapy. You should never
modify this setting in your project, modify `ITEM_PIPELINES` instead.

### JOBDIR

Default: `None`

A string indicating the directory for storing the state of a crawl when
[pausing and resuming crawls](jobs.html#topics-jobs).

### LOG_ENABLED

Default: `True`

Whether to enable logging.

### LOG_ENCODING

Default: `'utf-8'`

The encoding to use for logging.

### LOG_FILE

Default: `None`

File name to use for logging output. If `None`, standard error will be used.

### LOG_FILE_APPEND

Default: `True`

If `False`, the log file specified with `LOG_FILE` will be
overwritten (discarding the output from previous runs, if any).

### LOG_FORMAT

Default: `'%(asctime)s [%(name)s] %(levelname)s: %(message)s'`

String for formatting log messages. Refer to the
[Python logging documentation](https://docs.python.org/3/library/logging.html#logrecord-attributes) for the whole
list of available placeholders.

### LOG_DATEFORMAT

Default: `'%Y-%m-%d %H:%M:%S'`

String for formatting date/time, expansion of the `%(asctime)s` placeholder
in `LOG_FORMAT`. Refer to the
[Python datetime documentation](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior) for the
whole list of available directives.

### LOG_FORMATTER

Default: [`scrapy.logformatter.LogFormatter`](logging.html#scrapy.logformatter.LogFormatter)

The class to use for [formatting log messages](logging.html#custom-log-formats) for different actions.

### LOG_LEVEL

Default: `'DEBUG'`

Minimum level to log. Available levels are: CRITICAL, ERROR, WARNING,
INFO, DEBUG. For more info see [Logging](logging.html#topics-logging).

### LOG_STDOUT

Default: `False`

If `True`, all standard output (and error) of your process will be redirected
to the log. For example if you `print('hello')` it will appear in the Scrapy
log.

### LOG_SHORT_NAMES

Default: `False`

If `True`, the logs will just contain the root path. If it is set to `False`
then it displays the component responsible for the log output

### LOG_VERSIONS

Default: `["lxml", "libxml2", "cssselect", "parsel", "w3lib", "Twisted", "Python", "pyOpenSSL", "cryptography", "Platform"]`

Logs the installed versions of the specified items.

An item can be any installed Python package.

The following special items are also supported:

- `libxml2`
- `Platform` ([`platform.platform()`](https://docs.python.org/3/library/platform.html#platform.platform))
- `Python`

### LOGSTATS_INTERVAL

Default: `60.0`

The interval (in seconds) between each logging printout of the stats
by [`LogStats`](extensions.html#scrapy.extensions.logstats.LogStats).

### MEMDEBUG_ENABLED

Default: `False`

Whether to enable memory debugging.

### MEMDEBUG_NOTIFY

Default: `[]`

When memory debugging is enabled a memory report will be sent to the specified
addresses if this setting is not empty, otherwise the report will be written to
the log.

Example:

```
MEMDEBUG_NOTIFY = ['user@example.com']
```

### MEMUSAGE_ENABLED

Default: `True`

Scope: `scrapy.extensions.memusage`

Whether to enable the memory usage extension. This extension keeps track of
a peak memory used by the process (it writes it to stats). It can also
optionally shutdown the Scrapy process when it exceeds a memory limit
(see `MEMUSAGE_LIMIT_MB`), and notify by email when that happened
(see `MEMUSAGE_NOTIFY_MAIL`).

See [Memory usage extension](extensions.html#topics-extensions-ref-memusage).

### MEMUSAGE_LIMIT_MB

Default: `0`

Scope: `scrapy.extensions.memusage`

The maximum amount of memory to allow (in megabytes) before shutting down
Scrapy (if MEMUSAGE_ENABLED is True). If zero, no check will be performed.

See [Memory usage extension](extensions.html#topics-extensions-ref-memusage).

### MEMUSAGE_CHECK_INTERVAL_SECONDS

Default: `60.0`

Scope: `scrapy.extensions.memusage`

The [Memory usage extension](extensions.html#topics-extensions-ref-memusage)
checks the current memory usage, versus the limits set by
`MEMUSAGE_LIMIT_MB` and `MEMUSAGE_WARNING_MB`,
at fixed time intervals.

This sets the length of these intervals, in seconds.

See [Memory usage extension](extensions.html#topics-extensions-ref-memusage).

### MEMUSAGE_NOTIFY_MAIL

Default: `False`

Scope: `scrapy.extensions.memusage`

A list of emails to notify if the memory limit has been reached.

Example:

```
MEMUSAGE_NOTIFY_MAIL = ['user@example.com']
```

See [Memory usage extension](extensions.html#topics-extensions-ref-memusage).

### MEMUSAGE_WARNING_MB

Default: `0`

Scope: `scrapy.extensions.memusage`

The maximum amount of memory to allow (in megabytes) before sending a warning
email notifying about it. If zero, no warning will be produced.

### NEWSPIDER_MODULE

Default: `"<project name>.spiders"` (fallback: `""`)

Module where to create new spiders using the [`genspider`](commands.html#std-command-genspider) command.

Example:

```
NEWSPIDER_MODULE = 'mybot.spiders_dev'
```

### RANDOMIZE_DOWNLOAD_DELAY

Default: `True`

If enabled, Scrapy will wait a random amount of time (between 0.5 * `DOWNLOAD_DELAY` and 1.5 * `DOWNLOAD_DELAY`) while fetching requests from the same
website.

This randomization decreases the chance of the crawler being detected (and
subsequently blocked) by sites which analyze requests looking for statistically
significant similarities in the time between their requests.

The randomization policy is the same used by [wget](https://www.gnu.org/software/wget/manual/wget.html) `--random-wait` option.

If `DOWNLOAD_DELAY` is zero (default) this option has no effect.

### REACTOR_THREADPOOL_MAXSIZE

Default: `10`

The maximum limit for Twisted Reactor thread pool size. This is common
multi-purpose thread pool used by various Scrapy components. Threaded
DNS Resolver, BlockingFeedStorage, S3FilesStore just to name a few. Increase
this value if you’re experiencing problems with insufficient blocking IO.

### REDIRECT_PRIORITY_ADJUST

Default: `+2`

Scope: `scrapy.downloadermiddlewares.redirect.RedirectMiddleware`

Adjust redirect request priority relative to original request:

- **a positive priority adjust (default) means higher priority.**
- a negative priority adjust means lower priority.

### ROBOTSTXT_OBEY

Default: `True` (fallback: `False`)

If enabled, Scrapy will respect robots.txt policies. For more information see
[RobotsTxtMiddleware](downloader-middleware.html#topics-dlmw-robots).

While the default value is `False` for historical reasons,
this option is enabled by default in settings.py file generated
by `scrapy startproject` command.

### ROBOTSTXT_PARSER

Default: `'scrapy.robotstxt.ProtegoRobotParser'`

The parser backend to use for parsing `robots.txt` files. For more information see
[RobotsTxtMiddleware](downloader-middleware.html#topics-dlmw-robots).

#### ROBOTSTXT_USER_AGENT

Default: `None`

The user agent string to use for matching in the robots.txt file. If `None`,
the User-Agent header you are sending with the request or the
`USER_AGENT` setting (in that order) will be used for determining
the user agent to use in the robots.txt file.

### SCHEDULER

Default: `'scrapy.core.scheduler.Scheduler'`

The scheduler class to be used for crawling.
See the [Scheduler](scheduler.html#topics-scheduler) topic for details.

### SCHEDULER_DEBUG

Default: `False`

Setting to `True` will log debug information about the requests scheduler.
This currently logs (only once) if the requests cannot be serialized to disk.
Stats counter (`scheduler/unserializable`) tracks the number of times this happens.

Example entry in logs:

```
1956-01-31 00:00:00+0800 [scrapy.core.scheduler] ERROR: Unable to serialize request:
<GET http://example.com> - reason: cannot serialize <Request at 0x9a7c7ec>
(type Request)> - no more unserializable requests will be logged
(see 'scheduler/unserializable' stats counter)
```

### SCHEDULER_DISK_QUEUE

Default: `'scrapy.squeues.PickleLifoDiskQueue'`

Type of disk queue that will be used by the scheduler. Other available types
are `scrapy.squeues.PickleFifoDiskQueue`,
`scrapy.squeues.MarshalFifoDiskQueue`,
`scrapy.squeues.MarshalLifoDiskQueue`.

### SCHEDULER_MEMORY_QUEUE

Default: `'scrapy.squeues.LifoMemoryQueue'`

Type of in-memory queue used by the scheduler. Other available type is:
`scrapy.squeues.FifoMemoryQueue`.

### SCHEDULER_PRIORITY_QUEUE

Default: `'scrapy.pqueues.DownloaderAwarePriorityQueue'`

Type of priority queue used by the scheduler. Another available type is
`scrapy.pqueues.ScrapyPriorityQueue`.
`scrapy.pqueues.DownloaderAwarePriorityQueue` works better than
`scrapy.pqueues.ScrapyPriorityQueue` when you crawl many different
domains in parallel.

### SCHEDULER_START_DISK_QUEUE

Default: `'scrapy.squeues.PickleFifoDiskQueue'`

Type of disk queue (see `JOBDIR`) that the [scheduler](scheduler.html#topics-scheduler) uses for [start requests](spiders.html#start-requests).

For available choices, see `SCHEDULER_DISK_QUEUE`.

Use `None` or `""` to disable these separate queues entirely, and instead
have start requests share the same queues as other requests.

Disabling separate start request queues makes [start request order](scheduler.html#start-request-order) unintuitive: start requests will be sent in order
only until `CONCURRENT_REQUESTS` is reached, then remaining start
requests will be sent in reverse order.

### SCHEDULER_START_MEMORY_QUEUE

Default: `'scrapy.squeues.FifoMemoryQueue'`

Type of in-memory queue that the [scheduler](scheduler.html#topics-scheduler) uses for
[start requests](spiders.html#start-requests).

For available choices, see `SCHEDULER_MEMORY_QUEUE`.

Use `None` or `""` to disable these separate queues entirely, and instead
have start requests share the same queues as other requests.

Disabling separate start request queues makes [start request order](scheduler.html#start-request-order) unintuitive: start requests will be sent in order
only until `CONCURRENT_REQUESTS` is reached, then remaining start
requests will be sent in reverse order.

### SCRAPER_SLOT_MAX_ACTIVE_SIZE

Default: `5_000_000`

Soft limit (in bytes) for response data being processed.

While the sum of the sizes of all responses being processed is above this value,
Scrapy does not process new requests.

### SPIDER_CONTRACTS

Default:: `{}`

A dict containing the spider contracts enabled in your project, used for
testing spiders. For more info see [Spiders Contracts](contracts.html#topics-contracts).

### SPIDER_CONTRACTS_BASE

Default:

```
{
    "scrapy.contracts.default.UrlContract": 1,
    "scrapy.contracts.default.ReturnsContract": 2,
    "scrapy.contracts.default.ScrapesContract": 3,
}
```

A dict containing the Scrapy contracts enabled by default in Scrapy. You should
never modify this setting in your project, modify `SPIDER_CONTRACTS`
instead. For more info see [Spiders Contracts](contracts.html#topics-contracts).

You can disable any of these contracts by assigning `None` to their class
path in `SPIDER_CONTRACTS`. E.g., to disable the built-in
`ScrapesContract`, place this in your `settings.py`:

```
SPIDER_CONTRACTS = {
    "scrapy.contracts.default.ScrapesContract": None,
}
```

### SPIDER_LOADER_CLASS

Default: `'scrapy.spiderloader.SpiderLoader'`

The class that will be used for loading spiders, which must implement the
[SpiderLoader API](api.html#topics-api-spiderloader).

### SPIDER_LOADER_WARN_ONLY

Default: `False`

By default, when Scrapy tries to import spider classes from `SPIDER_MODULES`,
it will fail loudly if there is any `ImportError` or `SyntaxError` exception.
But you can choose to silence this exception and turn it into a simple
warning by setting `SPIDER_LOADER_WARN_ONLY = True`.

### SPIDER_MIDDLEWARES

Default:: `{}`

A dict containing the spider middlewares enabled in your project, and their
orders. For more info see [Activating a spider middleware](spider-middleware.html#topics-spider-middleware-setting).

### SPIDER_MIDDLEWARES_BASE

Default:

```
{
    "scrapy.spidermiddlewares.httperror.HttpErrorMiddleware": 50,
    "scrapy.spidermiddlewares.referer.RefererMiddleware": 700,
    "scrapy.spidermiddlewares.urllength.UrlLengthMiddleware": 800,
    "scrapy.spidermiddlewares.depth.DepthMiddleware": 900,
}
```

A dict containing the spider middlewares enabled by default in Scrapy, and
their orders. Low orders are closer to the engine, high orders are closer to
the spider. For more info see [Activating a spider middleware](spider-middleware.html#topics-spider-middleware-setting).

### SPIDER_MODULES

Default: `["<project name>.spiders"]` (fallback: `[]`)

A list of modules where Scrapy will look for spiders.

Example:

```
SPIDER_MODULES = ["mybot.spiders_prod", "mybot.spiders_dev"]
```

### STATS_CLASS

Default: `'scrapy.statscollectors.MemoryStatsCollector'`

The class to use for collecting stats, who must implement the
[Stats Collector API](api.html#topics-api-stats).

### STATS_DUMP

Default: `True`

Dump the [Scrapy stats](stats.html#topics-stats) (to the Scrapy log) once the spider
finishes.

For more info see: [Stats Collection](stats.html#topics-stats).

### STATSMAILER_RCPTS

Default: `[]` (empty list)

Send Scrapy stats after spiders finish scraping. See
[`StatsMailer`](extensions.html#scrapy.extensions.statsmailer.StatsMailer) for more info.

### TELNETCONSOLE_ENABLED

Default: `True`

A boolean which specifies if the [telnet console](telnetconsole.html#topics-telnetconsole)
will be enabled (provided its extension is also enabled).

### TEMPLATES_DIR

Default: `templates` dir inside scrapy module

The directory where to look for templates when creating new projects with
[`startproject`](commands.html#std-command-startproject) command and new spiders with [`genspider`](commands.html#std-command-genspider)
command.

The project name must not conflict with the name of custom files or directories
in the `project` subdirectory.

### TWISTED_REACTOR

Default: `"twisted.internet.asyncioreactor.AsyncioSelectorReactor"`

Import path of a given [`reactor`](https://docs.twisted.org/en/stable/api/twisted.internet.reactor.html).

Scrapy will install this reactor if no other reactor is installed yet, such as
when the `scrapy` CLI program is invoked or when using the
[`AsyncCrawlerProcess`](api.html#scrapy.crawler.AsyncCrawlerProcess) class or the
[`CrawlerProcess`](api.html#scrapy.crawler.CrawlerProcess) class.

If you are using the [`AsyncCrawlerRunner`](api.html#scrapy.crawler.AsyncCrawlerRunner) class or the
[`CrawlerRunner`](api.html#scrapy.crawler.CrawlerRunner) class, you also
need to install the correct reactor manually. You can do that using
`install_reactor()`:

**scrapy.utils.reactor.install_reactor(*reactor_path: [str](https://docs.python.org/3/library/stdtypes.html#str)*, *event_loop_path: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None) = None*) → [None](https://docs.python.org/3/library/constants.html#None)[[source]](../_modules/scrapy/utils/reactor.html#install_reactor)**

Installs the [`reactor`](https://docs.twisted.org/en/stable/api/twisted.internet.reactor.html) with the specified
import path. Also installs the asyncio event loop with the specified import
path if the asyncio reactor is enabled

If a reactor is already installed,
`install_reactor()` has no effect.

[`AsyncCrawlerRunner`](api.html#scrapy.crawler.AsyncCrawlerRunner) and other similar classes raise an
exception if the installed reactor does not match the
`TWISTED_REACTOR` setting; therefore, having top-level
[`reactor`](https://docs.twisted.org/en/stable/api/twisted.internet.reactor.html) imports in project files and imported
third-party libraries will make Scrapy raise an exception when it checks which
reactor is installed.

In order to use the reactor installed by Scrapy:

```
import scrapy
from twisted.internet import reactor

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, *args, **kwargs):
        self.timeout = int(kwargs.pop("timeout", "60"))
        super(QuotesSpider, self).__init__(*args, **kwargs)

    async def start(self):
        reactor.callLater(self.timeout, self.stop)

        urls = ["https://quotes.toscrape.com/page/1"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {"text": quote.css("span.text::text").get()}

    def stop(self):
        self.crawler.engine.close_spider(self, "timeout")
```

which raises an exception, becomes:

```
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, *args, **kwargs):
        self.timeout = int(kwargs.pop("timeout", "60"))
        super(QuotesSpider, self).__init__(*args, **kwargs)

    async def start(self):
        from twisted.internet import reactor

        reactor.callLater(self.timeout, self.stop)

        urls = ["https://quotes.toscrape.com/page/1"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {"text": quote.css("span.text::text").get()}

    def stop(self):
        self.crawler.engine.close_spider(self, "timeout")
```

If this setting is set `None`, Scrapy will use the existing reactor if one is
already installed, or install the default reactor defined by Twisted for the
current platform.

Changed in version 2.13: The default value was changed from `None` to
`"twisted.internet.asyncioreactor.AsyncioSelectorReactor"`.

For additional information, see [Choosing a Reactor and GUI Toolkit Integration](https://docs.twisted.org/en/stable/core/howto/choosing-reactor.html).

### URLLENGTH_LIMIT

Default: `2083`

Scope: `spidermiddlewares.urllength`

The maximum URL length to allow for crawled URLs.

This setting can act as a stopping condition in case of URLs of ever-increasing
length, which may be caused for example by a programming error either in the
target server or in your code. See also [`REDIRECT_MAX_TIMES`](downloader-middleware.html#std-setting-REDIRECT_MAX_TIMES) and
`DEPTH_LIMIT`.

Use `0` to allow URLs of any length.

The default value is copied from the [Microsoft Internet Explorer maximum URL
length](https://support.microsoft.com/en-us/topic/maximum-url-length-is-2-083-characters-in-internet-explorer-174e7c8a-6666-f4e0-6fd6-908b53c12246), even though this setting exists for different reasons.

### USER_AGENT

Default: `"Scrapy/VERSION (+https://scrapy.org)"`

The default User-Agent to use when crawling, unless overridden. This user agent is
also used by [`RobotsTxtMiddleware`](downloader-middleware.html#scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware)
if `ROBOTSTXT_USER_AGENT` setting is `None` and
there is no overriding User-Agent header specified for the request.

### WARN_ON_GENERATOR_RETURN_VALUE

Default: `True`

When enabled, Scrapy will warn if generator-based callback methods (like
`parse`) contain return statements with non-`None` values. This helps detect
potential mistakes in spider development.

Disable this setting to prevent syntax errors that may occur when dynamically
modifying generator function source code during runtime, skip AST parsing of
callback functions, or improve performance in auto-reloading development
environments.

### Settings documented elsewhere:

The following settings are documented elsewhere, please check each specific
case to see how to enable and use them.

- [AUTOTHROTTLE_DEBUG](autothrottle.html#std-setting-AUTOTHROTTLE_DEBUG)
- [AUTOTHROTTLE_ENABLED](autothrottle.html#std-setting-AUTOTHROTTLE_ENABLED)
- [AUTOTHROTTLE_MAX_DELAY](autothrottle.html#std-setting-AUTOTHROTTLE_MAX_DELAY)
- [AUTOTHROTTLE_START_DELAY](autothrottle.html#std-setting-AUTOTHROTTLE_START_DELAY)
- [AUTOTHROTTLE_TARGET_CONCURRENCY](autothrottle.html#std-setting-AUTOTHROTTLE_TARGET_CONCURRENCY)
- [CLOSESPIDER_ERRORCOUNT](extensions.html#std-setting-CLOSESPIDER_ERRORCOUNT)
- [CLOSESPIDER_ITEMCOUNT](extensions.html#std-setting-CLOSESPIDER_ITEMCOUNT)
- [CLOSESPIDER_PAGECOUNT](extensions.html#std-setting-CLOSESPIDER_PAGECOUNT)
- [CLOSESPIDER_PAGECOUNT_NO_ITEM](extensions.html#std-setting-CLOSESPIDER_PAGECOUNT_NO_ITEM)
- [CLOSESPIDER_TIMEOUT](extensions.html#std-setting-CLOSESPIDER_TIMEOUT)
- [CLOSESPIDER_TIMEOUT_NO_ITEM](extensions.html#std-setting-CLOSESPIDER_TIMEOUT_NO_ITEM)
- [COMMANDS_MODULE](commands.html#std-setting-COMMANDS_MODULE)
- [COMPRESSION_ENABLED](downloader-middleware.html#std-setting-COMPRESSION_ENABLED)
- [COOKIES_DEBUG](downloader-middleware.html#std-setting-COOKIES_DEBUG)
- [COOKIES_ENABLED](downloader-middleware.html#std-setting-COOKIES_ENABLED)
- [FEEDS](feed-exports.html#std-setting-FEEDS)
- [FEED_EXPORTERS](feed-exports.html#std-setting-FEED_EXPORTERS)
- [FEED_EXPORTERS_BASE](feed-exports.html#std-setting-FEED_EXPORTERS_BASE)
- [FEED_EXPORT_BATCH_ITEM_COUNT](feed-exports.html#std-setting-FEED_EXPORT_BATCH_ITEM_COUNT)
- [FEED_EXPORT_ENCODING](feed-exports.html#std-setting-FEED_EXPORT_ENCODING)
- [FEED_EXPORT_FIELDS](feed-exports.html#std-setting-FEED_EXPORT_FIELDS)
- [FEED_EXPORT_INDENT](feed-exports.html#std-setting-FEED_EXPORT_INDENT)
- [FEED_STORAGES](feed-exports.html#std-setting-FEED_STORAGES)
- [FEED_STORAGES_BASE](feed-exports.html#std-setting-FEED_STORAGES_BASE)
- [FEED_STORAGE_FTP_ACTIVE](feed-exports.html#std-setting-FEED_STORAGE_FTP_ACTIVE)
- [FEED_STORAGE_S3_ACL](feed-exports.html#std-setting-FEED_STORAGE_S3_ACL)
- [FEED_STORE_EMPTY](feed-exports.html#std-setting-FEED_STORE_EMPTY)
- [FEED_URI_PARAMS](feed-exports.html#std-setting-FEED_URI_PARAMS)
- [FILES_EXPIRES](media-pipeline.html#std-setting-FILES_EXPIRES)
- [FILES_RESULT_FIELD](media-pipeline.html#std-setting-FILES_RESULT_FIELD)
- [FILES_STORE](media-pipeline.html#std-setting-FILES_STORE)
- [FILES_STORE_GCS_ACL](media-pipeline.html#std-setting-FILES_STORE_GCS_ACL)
- [FILES_STORE_S3_ACL](media-pipeline.html#std-setting-FILES_STORE_S3_ACL)
- [FILES_URLS_FIELD](media-pipeline.html#std-setting-FILES_URLS_FIELD)
- [HTTPCACHE_ALWAYS_STORE](downloader-middleware.html#std-setting-HTTPCACHE_ALWAYS_STORE)
- [HTTPCACHE_DBM_MODULE](downloader-middleware.html#std-setting-HTTPCACHE_DBM_MODULE)
- [HTTPCACHE_DIR](downloader-middleware.html#std-setting-HTTPCACHE_DIR)
- [HTTPCACHE_ENABLED](downloader-middleware.html#std-setting-HTTPCACHE_ENABLED)
- [HTTPCACHE_EXPIRATION_SECS](downloader-middleware.html#std-setting-HTTPCACHE_EXPIRATION_SECS)
- [HTTPCACHE_GZIP](downloader-middleware.html#std-setting-HTTPCACHE_GZIP)
- [HTTPCACHE_IGNORE_HTTP_CODES](downloader-middleware.html#std-setting-HTTPCACHE_IGNORE_HTTP_CODES)
- [HTTPCACHE_IGNORE_MISSING](downloader-middleware.html#std-setting-HTTPCACHE_IGNORE_MISSING)
- [HTTPCACHE_IGNORE_RESPONSE_CACHE_CONTROLS](downloader-middleware.html#std-setting-HTTPCACHE_IGNORE_RESPONSE_CACHE_CONTROLS)
- [HTTPCACHE_IGNORE_SCHEMES](downloader-middleware.html#std-setting-HTTPCACHE_IGNORE_SCHEMES)
- [HTTPCACHE_POLICY](downloader-middleware.html#std-setting-HTTPCACHE_POLICY)
- [HTTPCACHE_STORAGE](downloader-middleware.html#std-setting-HTTPCACHE_STORAGE)
- [HTTPERROR_ALLOWED_CODES](spider-middleware.html#std-setting-HTTPERROR_ALLOWED_CODES)
- [HTTPERROR_ALLOW_ALL](spider-middleware.html#std-setting-HTTPERROR_ALLOW_ALL)
- [HTTPPROXY_AUTH_ENCODING](downloader-middleware.html#std-setting-HTTPPROXY_AUTH_ENCODING)
- [HTTPPROXY_ENABLED](downloader-middleware.html#std-setting-HTTPPROXY_ENABLED)
- [IMAGES_EXPIRES](media-pipeline.html#std-setting-IMAGES_EXPIRES)
- [IMAGES_MIN_HEIGHT](media-pipeline.html#std-setting-IMAGES_MIN_HEIGHT)
- [IMAGES_MIN_WIDTH](media-pipeline.html#std-setting-IMAGES_MIN_WIDTH)
- [IMAGES_RESULT_FIELD](media-pipeline.html#std-setting-IMAGES_RESULT_FIELD)
- [IMAGES_STORE](media-pipeline.html#std-setting-IMAGES_STORE)
- [IMAGES_STORE_GCS_ACL](media-pipeline.html#std-setting-IMAGES_STORE_GCS_ACL)
- [IMAGES_STORE_S3_ACL](media-pipeline.html#std-setting-IMAGES_STORE_S3_ACL)
- [IMAGES_THUMBS](media-pipeline.html#std-setting-IMAGES_THUMBS)
- [IMAGES_URLS_FIELD](media-pipeline.html#std-setting-IMAGES_URLS_FIELD)
- [MAIL_FROM](email.html#std-setting-MAIL_FROM)
- [MAIL_HOST](email.html#std-setting-MAIL_HOST)
- [MAIL_PASS](email.html#std-setting-MAIL_PASS)
- [MAIL_PORT](email.html#std-setting-MAIL_PORT)
- [MAIL_SSL](email.html#std-setting-MAIL_SSL)
- [MAIL_TLS](email.html#std-setting-MAIL_TLS)
- [MAIL_USER](email.html#std-setting-MAIL_USER)
- [MEDIA_ALLOW_REDIRECTS](media-pipeline.html#std-setting-MEDIA_ALLOW_REDIRECTS)
- [METAREFRESH_ENABLED](downloader-middleware.html#std-setting-METAREFRESH_ENABLED)
- [METAREFRESH_IGNORE_TAGS](downloader-middleware.html#std-setting-METAREFRESH_IGNORE_TAGS)
- [METAREFRESH_MAXDELAY](downloader-middleware.html#std-setting-METAREFRESH_MAXDELAY)
- [PERIODIC_LOG_DELTA](extensions.html#std-setting-PERIODIC_LOG_DELTA)
- [PERIODIC_LOG_STATS](extensions.html#std-setting-PERIODIC_LOG_STATS)
- [PERIODIC_LOG_TIMING_ENABLED](extensions.html#std-setting-PERIODIC_LOG_TIMING_ENABLED)
- [REDIRECT_ENABLED](downloader-middleware.html#std-setting-REDIRECT_ENABLED)
- [REDIRECT_MAX_TIMES](downloader-middleware.html#std-setting-REDIRECT_MAX_TIMES)
- [REFERER_ENABLED](spider-middleware.html#std-setting-REFERER_ENABLED)
- [REFERRER_POLICY](spider-middleware.html#std-setting-REFERRER_POLICY)
- [REQUEST_FINGERPRINTER_CLASS](request-response.html#std-setting-REQUEST_FINGERPRINTER_CLASS)
- [RETRY_ENABLED](downloader-middleware.html#std-setting-RETRY_ENABLED)
- [RETRY_EXCEPTIONS](downloader-middleware.html#std-setting-RETRY_EXCEPTIONS)
- [RETRY_HTTP_CODES](downloader-middleware.html#std-setting-RETRY_HTTP_CODES)
- [RETRY_PRIORITY_ADJUST](downloader-middleware.html#std-setting-RETRY_PRIORITY_ADJUST)
- [RETRY_TIMES](downloader-middleware.html#std-setting-RETRY_TIMES)
- [TELNETCONSOLE_HOST](telnetconsole.html#std-setting-TELNETCONSOLE_HOST)
- [TELNETCONSOLE_PASSWORD](telnetconsole.html#std-setting-TELNETCONSOLE_PASSWORD)
- [TELNETCONSOLE_PORT](telnetconsole.html#std-setting-TELNETCONSOLE_PORT)
- [TELNETCONSOLE_USERNAME](telnetconsole.html#std-setting-TELNETCONSOLE_USERNAME)
