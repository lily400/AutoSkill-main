# Scrapy 自定义请求指纹器配置 Evidence

- family: 未分类技能
- skill_id: 508a30a5-6330-5c7e-a9a0-583ed481e86d
- support_count: 1

## Evidence 1

- support_id: 075a1f80-a537-54ca-9e08-167432415257
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 17114:18236
- confidence: 0.75
- quote: def parse_page2(self, response, main_url, foo):
    yield dict(
        main_url=main_url,
        other_url=response.url,
        foo=foo,
    )
```

Using errbacks to catch exceptions in request processing
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
