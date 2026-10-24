# Feed URI 动态参数注入 Evidence

- family: 未分类技能
- skill_id: 090a1758-18b6-52ae-b493-2519ea84762f
- support_count: 1

## Evidence 1

- support_id: 30447e44-12ab-5dd1-a8c3-57e0f85470ea
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 23915:24443
- confidence: 0.85
- quote: For example, to include the [`name`](spiders.html#scrapy.Spider.name) of the
source spider in the feed URI:

1. Define the following function somewhere in your project:

```
# myproject/utils.py
def uri_params(params, spider):
    return {**params, "spider_name": spider.name}
```
2. Point `FEED_URI_PARAMS` to that function in your settings:

```
# myproject/settings.py
FEED_URI_PARAMS = "myproject.utils.uri_params"
```
3. Use `%(spider_name)s` in your feed URI:

```
scrapy crawl <spider_name> -o "%(spider_name)s.jsonl"
```
