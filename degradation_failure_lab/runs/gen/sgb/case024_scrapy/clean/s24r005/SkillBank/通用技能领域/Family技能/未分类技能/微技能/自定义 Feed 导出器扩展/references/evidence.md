# 自定义 Feed 导出器扩展 Evidence

- family: 未分类技能
- skill_id: 945ee694-0375-5f27-a671-6805bddfe600
- support_count: 1

## Evidence 1

- support_id: 99d5fb80-704c-5bce-83d3-973f5ed2eed8
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 1080:2737
- confidence: 0.70
- quote: But you can also extend the supported format through the
`FEED_EXPORTERS` setting.

JSON
- Value for the `format` key in the `FEEDS` setting: `json`
- Exporter used: [`JsonItemExporter`](exporters.html#scrapy.exporters.JsonItemExporter)
- See [this warning](exporters.html#json-with-large-data) if you’re using JSON with
large feeds.

JSON lines
- Value for the `format` key in the `FEEDS` setting: `jsonlines`
- Exporter used: [`JsonLinesItemExporter`](exporters.html#scrapy.exporters.JsonLinesItemExporter)

CSV
- Value for the `format` key in the `FEEDS` setting: `csv`
- Exporter used: [`CsvItemExporter`](exporters.html#scrapy.exporters.CsvItemExporter)
- To specify columns to export, their order and their column names, use
`FEED_EXPORT_FIELDS`. Other feed exporters can also use this
option, but it is important for CSV because unlike many other export
formats CSV uses a fixed header.

XML
- Value for the `format` key in the `FEEDS` setting: `xml`
- Exporter used: [`XmlItemExporter`](exporters.html#scrapy.exporters.XmlItemExporter)

Pickle
- Value for the `format` key in the `FEEDS` setting: `pickle`
- Exporter used: [`PickleItemExporter`](exporters.html#scrapy.exporters.PickleItemExporter)

Marshal
- Value for the `format` key in the `FEEDS` setting: `marshal`
- Exporter used: [`MarshalItemExporter`](exporters.html#scrapy.exporters.MarshalItemExporter)

Storages
When using the feed exports you define where to store the feed using one or multiple [URIs](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier)
(through the `FEEDS` setting). The feed exports supports multiple
storage backend types which are defined by the URI scheme.
