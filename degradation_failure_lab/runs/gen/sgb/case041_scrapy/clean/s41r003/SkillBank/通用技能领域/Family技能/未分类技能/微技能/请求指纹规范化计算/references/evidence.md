# 请求指纹规范化计算 Evidence

- family: 未分类技能
- skill_id: bbb2cc51-443c-5e23-a285-3b443df42cb5
- support_count: 1

## Evidence 1

- support_id: dc44d88e-0494-5b0c-bc90-ad37742213b0
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 21472:24214
- confidence: 0.75
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
