# Feed 存储后端 URI 配置 Evidence

- family: 未分类技能
- skill_id: d5862d9c-e48d-5b19-9342-c94d0fbc3157
- support_count: 1

## Evidence 1

- support_id: 2bc10936-fbaf-5264-9653-8283586424ae
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 1080:2737
- confidence: 0.80
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
