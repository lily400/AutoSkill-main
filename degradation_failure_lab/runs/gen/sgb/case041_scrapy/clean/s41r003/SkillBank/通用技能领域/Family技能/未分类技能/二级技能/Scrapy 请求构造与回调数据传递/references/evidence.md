# Scrapy 请求构造与回调数据传递 Evidence

- family: 未分类技能
- skill_id: dc522835-58a3-552c-bd8b-30ad389282ea
- support_count: 1

## Evidence 1

- support_id: 99f4126d-cd4a-5f2a-800d-1aef199d69c7
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 3704:5024
- confidence: 0.75
- quote: For more info see [CookiesMiddleware](downloader-middleware.html#cookies-mw).

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
