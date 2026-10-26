# Feed URI 参数生成器 Evidence

- family: 未分类技能
- skill_id: 2d611108-970f-5e54-8821-4b26efe3a8bc
- support_count: 1

## Evidence 1

- support_id: 69af7ccd-7dcc-5566-acc1-bd351539652e
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 23265:23913
- confidence: 0.70
- quote: **Parameters:**

- **params** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) –

default key-value pairs

Specifically:
  - `batch_id`: ID of the file batch. See
`FEED_EXPORT_BATCH_ITEM_COUNT`.

If `FEED_EXPORT_BATCH_ITEM_COUNT` is `0`, `batch_id`
is always `1`.
  - `batch_time`: UTC date and time, in ISO format with `:`
replaced with `-`.

See `FEED_EXPORT_BATCH_ITEM_COUNT`.
  - `time`: `batch_time`, with microseconds set to `0`.
- **spider** ([*scrapy.Spider*](spiders.html#scrapy.Spider)) – source spider of the feed items

The function should return a new dictionary, modifying
the received `params` in-place is deprecated.
