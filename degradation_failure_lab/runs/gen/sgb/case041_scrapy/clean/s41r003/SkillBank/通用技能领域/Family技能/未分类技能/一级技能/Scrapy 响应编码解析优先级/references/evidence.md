# Scrapy 响应编码解析优先级 Evidence

- family: 未分类技能
- skill_id: 7ce0ae55-8c21-5690-a09e-d2e8d99adb28
- support_count: 1

## Evidence 1

- support_id: 1acae754-1302-540f-af00-1b4af9e890e3
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 54830:55491
- confidence: 0.70
- quote: A string with the encoding of this response. The encoding is resolved by
trying the following mechanisms, in order:

1. the encoding passed in the `__init__()` method `encoding` argument
2. the encoding declared in the Content-Type HTTP header. If this
encoding is not valid (i.e. unknown), it is ignored and the next
resolution mechanism is tried.
3. the encoding declared in the response body. The TextResponse class
doesn’t provide any special functionality for this. However, the
`HtmlResponse` and `XmlResponse` classes do.
4. the encoding inferred by looking at the response body. This is the more
fragile method but also the last one tried.

**selector**
