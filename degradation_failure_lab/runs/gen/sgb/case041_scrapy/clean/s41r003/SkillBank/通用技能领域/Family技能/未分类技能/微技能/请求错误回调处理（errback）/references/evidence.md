# 请求错误回调处理（errback） Evidence

- family: 未分类技能
- skill_id: 9719683e-0a4a-5d7e-8169-5d7d854d94d9
- support_count: 1

## Evidence 1

- support_id: 1d48009e-8ac2-5a3d-be19-6fffbcf003ee
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 18654:21470
- confidence: 0.85
- quote: async def start(self):
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

Accessing additional data in errback functions
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

You often do not need to worry about request fingerprints, the default request
fingerprinter works for most projects.

However, there is no universal way to generate a unique identifier from a
request, because different situations require comparing requests differently.
For example, sometimes you may need to compare URLs case-insensitively, include
URL fragments, exclude certain URL query parameters, include some or all
headers, etc.
