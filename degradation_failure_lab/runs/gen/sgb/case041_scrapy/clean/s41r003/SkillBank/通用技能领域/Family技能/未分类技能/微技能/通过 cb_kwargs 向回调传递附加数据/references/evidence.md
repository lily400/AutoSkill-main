# 通过 cb_kwargs 向回调传递附加数据 Evidence

- family: 未分类技能
- skill_id: 1c413e32-798b-5a1d-b58b-85c84c4055ec
- support_count: 1

## Evidence 1

- support_id: 09e04765-caeb-5abd-88f0-b22b645bbfa8
- relation_type: support
- document: input003\request-response.md
- doc_id: acd53fe2-91e6-5d61-9beb-63fa936ab397
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case041_scrapy\clean\r13fe557951\inputs\input003\request-response.md
- section: Requests and Responses
- span: 12512:17112
- confidence: 0.85
- quote: Create a Request object from a string containing a [cURL](https://curl.se/) command. It populates the HTTP method, the
URL, the headers, the cookies and the body. It accepts the same
arguments as the `Request` class, taking preference and
overriding the values of the same arguments contained in the cURL
command.

Unrecognized options are ignored by default. To raise an error when
finding unknown options call this method by passing
`ignore_unknown_options=False`.

To translate a cURL command into a Scrapy request,
you may use [curl2scrapy](https://michael-shub.github.io/curl2scrapy/).

Return a dictionary containing the Request’s data.

Use `request_from_dict()` to convert back into a `Request` object.

If a spider is given, this method will try to find out the name of the spider methods used as callback
and errback and include them in the output dict, raising an exception if they cannot be found.

When assigned to the `callback` parameter of
`Request`, it indicates that the request is not meant
to have a spider callback at all.

For example:

```
Request("https://example.com", callback=NO_CALLBACK)
```

Create a `Request` object from a dict.

If a spider is given, it will try to resolve the callbacks looking at the
spider for methods with the same name.

Passing additional data to callback functions
The callback of a request is a function that will be called when the response
of that request is downloaded. The callback function will be called with the
downloaded `Response` object as its first argument.

Example:

```
def parse_page1(self, response):
    return scrapy.Request(
        "http://www.example.com/some_page.html", callback=self.parse_page2
    )

def parse_page2(self, response):
    # this would log http://www.example.com/some_page.html
    self.logger.info("Visited %s", response.url)
```

In some cases you may be interested in passing arguments to those callback
functions so you can receive the arguments later, in the second callback.
The following example shows how to achieve this by using the
`Request.cb_kwargs` attribute:

```
def parse(self, response):
    request = scrapy.Request(
        "http://www.example.com/index.html",
        callback=self.parse_page2,
        cb_kwargs=dict(main_url=response.url),
    )
    request.cb_kwargs["foo"] = "bar"  # add more arguments for the callback
    yield request
