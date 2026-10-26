# 自定义请求指纹器实现 Evidence

- family: 未分类技能
- skill_id: feef4a0a-e457-54fe-95b0-d28f9ed4ec32
- support_count: 2

## Evidence 1

- support_id: 01328c84-92a6-5654-91c4-f4f61433a574
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 24216:26606
- confidence: 0.85
- quote: For this reason, request headers are ignored by default when calculating
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

## Evidence 2

- support_id: e2dc9bf4-16a6-5561-9cec-b856efd38c54
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 21472:24214
- confidence: 0.80
- quote: To change how request fingerprints are built for your requests, use the
`REQUEST_FINGERPRINTER_CLASS` setting.

REQUEST_FINGERPRINTER_CLASS
Default: `scrapy.utils.request.RequestFingerprinter`

A request fingerprinter class or its
import path.

***class*scrapy.utils.request.RequestFingerprinter(*crawler: [Crawler](api.html#scrapy.crawler.Crawler) | [None](https://docs.python.org/3/library/constants.html#None) = None*)[[source]](../_modules/scrapy/utils/request.html#RequestFingerprinter)**

Default fingerprinter.

It takes into account a canonical version
([`w3lib.url.canonicalize_url()`](https://w3lib.readthedocs.io/en/latest/w3lib.html#w3lib.url.canonicalize_url)) of `request.url` and the values of `request.method` and `request.body`. It then generates an [SHA1](https://en.wikipedia.org/wiki/SHA-1) hash.

Writing your own request fingerprinter
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
