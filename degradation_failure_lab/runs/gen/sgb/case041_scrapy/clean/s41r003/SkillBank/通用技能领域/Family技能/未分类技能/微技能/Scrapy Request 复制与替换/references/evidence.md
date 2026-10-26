# Scrapy Request 复制与替换 Evidence

- family: 未分类技能
- skill_id: c8444e68-02ba-56bd-91b5-83d547d251d1
- support_count: 1

## Evidence 1

- support_id: 7f6128f3-f7b9-5fa2-9259-ca909997587f
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 10351:12510
- confidence: 0.85
- quote: **dont_filter*: [bool](https://docs.python.org/3/library/functions.html#bool)***

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
