# FormRequest 表单提交构造 Evidence

- family: 未分类技能
- skill_id: 8efb2db6-37e9-5869-8b32-ec06a4206585
- support_count: 1

## Evidence 1

- support_id: 2ba446da-1f01-5ab6-be5e-a904789f17b3
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 38545:39232
- confidence: 0.85
- quote: ```
return [
    FormRequest(
        url="http://www.example.com/post/action",
        formdata={"name": "John Doe", "age": "27"},
        callback=self.after_post,
    )
]
```

Using FormRequest.from_response() to simulate a user login
It is usual for web sites to provide pre-populated form fields through `<input
type="hidden">` elements, such as session related data or authentication
tokens (for login pages). When scraping, you’ll want these fields to be
automatically pre-populated and only override a couple of them, such as the
user name and password. You can use the `FormRequest.from_response()`
method for this job. Here’s an example spider which uses it:

```
import scrapy
