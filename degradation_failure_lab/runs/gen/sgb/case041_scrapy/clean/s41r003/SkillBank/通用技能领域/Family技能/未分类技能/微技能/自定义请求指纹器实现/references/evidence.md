# 自定义请求指纹器实现 Evidence

- family: 未分类技能
- skill_id: 6ea881fb-07e2-5ee9-8311-f419990e543a
- support_count: 1

## Evidence 1

- support_id: d20ddbb2-0d5c-5a11-a759-cdcd60a3dc2f
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 26608:28062
- confidence: 0.80
- quote: ```
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

Request fingerprint restrictions
Scrapy components that use request fingerprints may impose additional
restrictions on the format of the fingerprints that your request
fingerprinter generates.

The following built-in Scrapy components have such restrictions:

- [`scrapy.extensions.httpcache.FilesystemCacheStorage`](downloader-middleware.html#scrapy.extensions.httpcache.FilesystemCacheStorage) (default
value of [`HTTPCACHE_STORAGE`](downloader-middleware.html#std-setting-HTTPCACHE_STORAGE))

Request fingerprints must be at least 1 byte long.
