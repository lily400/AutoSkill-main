# Feed 覆盖与追加策略选择 Evidence

- family: 未分类技能
- skill_id: 341bd0da-1d52-5a40-87dd-44477cdec422
- support_count: 1

## Evidence 1

- support_id: b87aa6f1-8828-5df9-b664-49214c170785
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 15603:17155
- confidence: 0.80
- quote: The following is a list of the accepted keys and the setting that is used
as a fallback value if that key is not provided for a specific feed definition:

- `format`: the serialization format.

This setting is mandatory, there is no fallback value.
- `batch_item_count`: falls back to
`FEED_EXPORT_BATCH_ITEM_COUNT`.
- `encoding`: falls back to `FEED_EXPORT_ENCODING`.
- `fields`: falls back to `FEED_EXPORT_FIELDS`.
- `item_classes`: list of [item classes](items.html#topics-items) to export.

If undefined or empty, all items are exported.
- `item_filter`: a filter class to filter items to export.

`ItemFilter` is used be default.
- `indent`: falls back to `FEED_EXPORT_INDENT`.
- `item_export_kwargs`: [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) with keyword arguments for the corresponding [item exporter class](exporters.html#topics-exporters).
- `overwrite`: whether to overwrite the file if it already exists
(`True`) or append to its content (`False`).

The default value depends on the storage backend:
  - Local filesystem: `False`
  - FTP: `True`

Some FTP servers may not support appending to files (the
`APPE` FTP command).
  - S3: `True` (appending is not supported)
  - Google Cloud Storage (GCS): `True` (appending is not supported)
  - Standard output: `False` (overwriting is not supported)
- `store_empty`: falls back to `FEED_STORE_EMPTY`.
- `uri_params`: falls back to `FEED_URI_PARAMS`.
- `postprocessing`: list of plugins to use for post-processing.

The plugins will be used in the order of the list passed.
