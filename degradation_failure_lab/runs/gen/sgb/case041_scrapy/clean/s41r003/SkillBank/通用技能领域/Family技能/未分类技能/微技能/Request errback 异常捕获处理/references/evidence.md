# Request errback 异常捕获处理 Evidence

- family: 未分类技能
- skill_id: 476dd988-1326-59c4-be91-32595e7d8692
- support_count: 1

## Evidence 1

- support_id: a25db1ec-ab39-5dd9-978d-c586fefc9e1a
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 36373:38334
- confidence: 0.75
- quote: - **response** (`Response` object) – the response containing a HTML form which will be used
to pre-populate the form fields
- **formname** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the form with name attribute set to this value will be used.
- **formid** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the form with id attribute set to this value will be used.
- **formxpath** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the first form that matches the xpath will be used.
- **formcss** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – if given, the first form that matches the css selector will be used.
- **formnumber** ([*int*](https://docs.python.org/3/library/functions.html#int)) – the number of form to use, when the response contains
multiple forms. The first one (and also the default) is `0`.
- **formdata** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – fields to override in the form data. If a field was
already present in the response `<form>` element, its value is
overridden by the one passed in this parameter. If a value passed in
this parameter is `None`, the field will not be included in the
request, even if it was present in the response `<form>` element.
- **clickdata** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – attributes to lookup the control clicked. If it’s not
given, the form data will be submitted simulating a click on the
first clickable element. In addition to html attributes, the control
can be identified by its zero-based index relative to other
submittable inputs inside the form, via the `nr` attribute.
- **dont_click** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – If True, the form data will be submitted without
clicking in any element.

The other parameters of this class method are passed directly to the
`FormRequest` `__init__()` method.
