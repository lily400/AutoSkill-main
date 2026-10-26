# Scrapy 响应类型选择与解析 Evidence

- family: 未分类技能
- skill_id: 75b3b50e-8659-5572-9a05-b5b329f0f460
- support_count: 1

## Evidence 1

- support_id: ffda67fc-a75b-50d0-af88-b586ad8a3ce5
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 62927:64393
- confidence: 0.60
- quote: Deserialize a JSON document to a Python object.

Returns a Python object from deserialized JSON document.
The result is cached after the first call.

**urljoin(*url*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.urljoin)**

Constructs an absolute url by combining the Response’s base url with
a possible relative url. The base url shall be extracted from the
`<base>` tag, or just `Response.url` if there is no such
tag.

HtmlResponse objects
***class*scrapy.http.HtmlResponse(*url*[, *...*])[[source]](../_modules/scrapy/http/response/html.html#HtmlResponse)**

The `HtmlResponse` class is a subclass of `TextResponse`
which adds encoding auto-discovering support by looking into the HTML [meta
http-equiv](https://www.w3schools.com/TAGS/att_meta_http_equiv.asp) attribute. See `TextResponse.encoding`.

XmlResponse objects
***class*scrapy.http.XmlResponse(*url*[, *...*])[[source]](../_modules/scrapy/http/response/xml.html#XmlResponse)**

The `XmlResponse` class is a subclass of `TextResponse` which
adds encoding auto-discovering support by looking into the XML declaration
line. See `TextResponse.encoding`.

JsonResponse objects
***class*scrapy.http.JsonResponse(*url*[, *...*])[[source]](../_modules/scrapy/http/response/json.html#JsonResponse)**

The `JsonResponse` class is a subclass of `TextResponse`
that is used when the response has a [JSON MIME type](https://mimesniff.spec.whatwg.org/#json-mime-type) in its Content-Type
header.
