# WeakKeyDictionary 指纹缓存 Evidence

- family: 未分类技能
- skill_id: 43affaf4-7057-57e5-9e23-916199739db6
- support_count: 1

## Evidence 1

- support_id: 06d4ac18-d31a-54db-aa6b-a41083998f76
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
