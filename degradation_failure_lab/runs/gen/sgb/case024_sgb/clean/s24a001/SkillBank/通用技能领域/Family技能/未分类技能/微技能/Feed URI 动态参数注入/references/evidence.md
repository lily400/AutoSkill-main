# Feed URI 动态参数注入 Evidence

- family: 未分类技能
- skill_id: 16d43fc7-a942-5143-bc5e-8799de2381a8
- support_count: 1

## Evidence 1

- support_id: e00b492a-21fb-5848-b6dd-66d69c5cf830
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
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
