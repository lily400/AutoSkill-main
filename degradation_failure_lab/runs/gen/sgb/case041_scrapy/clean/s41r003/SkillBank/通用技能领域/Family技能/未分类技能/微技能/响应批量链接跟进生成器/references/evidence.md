# 响应批量链接跟进生成器 Evidence

- family: 未分类技能
- skill_id: a8682864-3e99-50f8-a466-765f0de8b334
- support_count: 1

## Evidence 1

- support_id: e05e63fb-f014-51d6-881d-5c9a663625c9
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 56332:62925
- confidence: 0.80
- quote: A shortcut to `TextResponse.selector.jmespath(query)`:

```
response.jmespath('object.[*]')
```

**xpath(*query*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.xpath)**

A shortcut to `TextResponse.selector.xpath(query)`:

```
response.xpath('//p')
```

**css(*query*)[[source]](../_modules/scrapy/http/response/text.html#TextResponse.css)**

A shortcut to `TextResponse.selector.css(query)`:

```
response.css('p')
```

Return a `Request` instance to follow a link `url`.
It accepts the same arguments as `Request.__init__()` method,
but `url` can be not only an absolute URL, but also

- a relative URL
- a [`Link`](link-extractors.html#scrapy.link.Link) object, e.g. the result of
[Link Extractors](link-extractors.html#topics-link-extractors)
- a [`Selector`](selectors.html#scrapy.Selector) object for a `<link>` or `<a>` element, e.g.
`response.css('a.my_link')[0]`
- an attribute [`Selector`](selectors.html#scrapy.Selector) (not SelectorList), e.g.
`response.css('a::attr(href)')[0]` or
`response.xpath('//img/@src')[0]`

See [A shortcut for creating Requests](../intro/tutorial.html#response-follow-example) for usage examples.

A generator that produces `Request` instances to follow all
links in `urls`. It accepts the same arguments as the `Request`’s
`__init__()` method, except that each `urls` element does not need to be
an absolute URL, it can be any of the following:

- a relative URL
- a [`Link`](link-extractors.html#scrapy.link.Link) object, e.g. the result of
[Link Extractors](link-extractors.html#topics-link-extractors)
- a [`Selector`](selectors.html#scrapy.Selector) object for a `<link>` or `<a>` element, e.g.
`response.css('a.my_link')[0]`
- an attribute [`Selector`](selectors.html#scrapy.Selector) (not SelectorList), e.g.
`response.css('a::attr(href)')[0]` or
`response.xpath('//img/@src')[0]`

In addition, `css` and `xpath` arguments are accepted to perform the link extraction
within the `follow_all()` method (only one of `urls`, `css` and `xpath` is accepted).

Note that when passing a `SelectorList` as argument for the `urls` parameter or
using the `css` or `xpath` parameters, this method will not produce requests for
selectors from which links cannot be obtained (for instance, anchor tags without an
`href` attribute)

**json()[[source]](../_modules/scrapy/http/response/text.html#TextResponse.json)**
