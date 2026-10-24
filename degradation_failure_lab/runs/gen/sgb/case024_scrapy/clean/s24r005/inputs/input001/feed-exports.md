# Feed exports — Scrapy 2.14.1 documentation

- Feed exports
- [Edit on GitHub](https://github.com/scrapy/scrapy/blob/master/docs/topics/feed-exports.rst)

---

# Feed exports

One of the most frequently required features when implementing scrapers is
being able to store the scraped data properly and, quite often, that means
generating an “export file” with the scraped data (commonly called “export
feed”) to be consumed by other systems.

Scrapy provides this functionality out of the box with the Feed Exports, which
allows you to generate feeds with the scraped items, using multiple
serialization formats and storage backends.

This page provides detailed documentation for all feed export features. If you
are looking for a step-by-step guide, check out [Zyte’s export guides](https://docs.zyte.com/web-scraping/guides/export/index.html#exporting-scraped-data).

## Serialization formats

For serializing the scraped data, the feed exports use the [Item exporters](exporters.html#topics-exporters). These formats are supported out of the box:

- JSON
- JSON lines
- CSV
- XML

But you can also extend the supported format through the
`FEED_EXPORTERS` setting.

### JSON

- Value for the `format` key in the `FEEDS` setting: `json`
- Exporter used: [`JsonItemExporter`](exporters.html#scrapy.exporters.JsonItemExporter)
- See [this warning](exporters.html#json-with-large-data) if you’re using JSON with
large feeds.

### JSON lines

- Value for the `format` key in the `FEEDS` setting: `jsonlines`
- Exporter used: [`JsonLinesItemExporter`](exporters.html#scrapy.exporters.JsonLinesItemExporter)

### CSV

- Value for the `format` key in the `FEEDS` setting: `csv`
- Exporter used: [`CsvItemExporter`](exporters.html#scrapy.exporters.CsvItemExporter)
- To specify columns to export, their order and their column names, use
`FEED_EXPORT_FIELDS`. Other feed exporters can also use this
option, but it is important for CSV because unlike many other export
formats CSV uses a fixed header.

### XML

- Value for the `format` key in the `FEEDS` setting: `xml`
- Exporter used: [`XmlItemExporter`](exporters.html#scrapy.exporters.XmlItemExporter)

### Pickle

- Value for the `format` key in the `FEEDS` setting: `pickle`
- Exporter used: [`PickleItemExporter`](exporters.html#scrapy.exporters.PickleItemExporter)

### Marshal

- Value for the `format` key in the `FEEDS` setting: `marshal`
- Exporter used: [`MarshalItemExporter`](exporters.html#scrapy.exporters.MarshalItemExporter)

## Storages

When using the feed exports you define where to store the feed using one or multiple [URIs](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier)
(through the `FEEDS` setting). The feed exports supports multiple
storage backend types which are defined by the URI scheme.

The storages backends supported out of the box are:

- Local filesystem
- FTP
- S3 (requires [boto3](https://github.com/boto/boto3))
- Google Cloud Storage (GCS) (requires [google-cloud-storage](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python))
- Standard output

Some storage backends may be unavailable if the required external libraries are
not available. For example, the S3 backend is only available if the [boto3](https://github.com/boto/boto3)
library is installed.

## Storage URI parameters

The storage URI can also contain parameters that get replaced when the feed is
being created. These parameters are:

- `%(time)s` - gets replaced by a timestamp when the feed is being created
- `%(name)s` - gets replaced by the spider name

Any other named parameter gets replaced by the spider attribute of the same
name. For example, `%(site_id)s` would get replaced by the `spider.site_id`
attribute the moment the feed is being created.

Here are some examples to illustrate:

- Store in FTP using one directory per spider:
  - `ftp://user:password@ftp.example.com/scraping/feeds/%(name)s/%(time)s.json`
- Store in S3 using one directory per spider:
  - `s3://mybucket/scraping/feeds/%(name)s/%(time)s.json`

[Spider arguments](spiders.html#spiderargs) become spider attributes, hence
they can also be used as storage URI parameters.

## Storage backends

### Local filesystem

The feeds are stored in the local filesystem.

- URI scheme: `file`
- Example URI: `file:///tmp/export.csv`
- Required external libraries: none

Note that for the local filesystem storage (only) you can omit the scheme if
you specify an absolute path like `/tmp/export.csv` (Unix systems only).
Alternatively you can also use a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path) object.

### FTP

The feeds are stored in a FTP server.

- URI scheme: `ftp`
- Example URI: `ftp://user:pass@ftp.example.com/path/to/export.csv`
- Required external libraries: none

FTP supports two different connection modes: [active or passive](https://stackoverflow.com/a/1699163). Scrapy uses the passive connection
mode by default. To use the active connection mode instead, set the
`FEED_STORAGE_FTP_ACTIVE` setting to `True`.

The default value for the `overwrite` key in the `FEEDS` for this
storage backend is: `True`.

The value `True` in `overwrite` will cause you to lose the
previous version of your data.

This storage backend uses delayed file delivery.

### S3

The feeds are stored on [Amazon S3](https://aws.amazon.com/s3/).

- URI scheme: `s3`
- Example URIs:
  - `s3://mybucket/path/to/export.csv`
  - `s3://aws_key:aws_secret@mybucket/path/to/export.csv`
- Required external libraries: [boto3](https://github.com/boto/boto3) >= 1.20.0

The AWS credentials can be passed as user/password in the URI, or they can be
passed through the following settings:

- [`AWS_ACCESS_KEY_ID`](settings.html#std-setting-AWS_ACCESS_KEY_ID)
- [`AWS_SECRET_ACCESS_KEY`](settings.html#std-setting-AWS_SECRET_ACCESS_KEY)
- [`AWS_SESSION_TOKEN`](settings.html#std-setting-AWS_SESSION_TOKEN) (only needed for [temporary security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html))

You can also define a custom ACL, custom endpoint, and region name for exported
feeds using these settings:

- `FEED_STORAGE_S3_ACL`
- [`AWS_ENDPOINT_URL`](settings.html#std-setting-AWS_ENDPOINT_URL)
- [`AWS_REGION_NAME`](settings.html#std-setting-AWS_REGION_NAME)

The default value for the `overwrite` key in the `FEEDS` for this
storage backend is: `True`.

The value `True` in `overwrite` will cause you to lose the
previous version of your data.

This storage backend uses delayed file delivery.

### Google Cloud Storage (GCS)

The feeds are stored on [Google Cloud Storage](https://cloud.google.com/storage/).

- URI scheme: `gs`
- Example URIs:
  - `gs://mybucket/path/to/export.csv`
- Required external libraries: [google-cloud-storage](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python).

For more information about authentication, please refer to [Google Cloud documentation](https://cloud.google.com/docs/authentication).

You can set a *Project ID* and *Access Control List (ACL)* through the following settings:

- [`FEED_STORAGE_GCS_ACL`](settings.html#std-setting-FEED_STORAGE_GCS_ACL)
- [`GCS_PROJECT_ID`](settings.html#std-setting-GCS_PROJECT_ID)

The default value for the `overwrite` key in the `FEEDS` for this
storage backend is: `True`.

The value `True` in `overwrite` will cause you to lose the
previous version of your data.

This storage backend uses delayed file delivery.

### Standard output

The feeds are written to the standard output of the Scrapy process.

- URI scheme: `stdout`
- Example URI: `stdout:`
- Required external libraries: none

### Delayed file delivery

As indicated above, some of the described storage backends use delayed file
delivery.

These storage backends do not upload items to the feed URI as those items are
scraped. Instead, Scrapy writes items into a temporary local file, and only
once all the file contents have been written (i.e. at the end of the crawl) is
that file uploaded to the feed URI.

If you want item delivery to start earlier when using one of these storage
backends, use `FEED_EXPORT_BATCH_ITEM_COUNT` to split the output items
in multiple files, with the specified maximum item count per file. That way, as
soon as a file reaches the maximum item count, that file is delivered to the
feed URI, allowing item delivery to start way before the end of the crawl.

## Item filtering

You can filter items that you want to allow for a particular feed by using the
`item_classes` option in feeds options. Only items of
the specified types will be added to the feed.

The `item_classes` option is implemented by the `ItemFilter`
class, which is the default value of the `item_filter` feed option.

You can create your own custom filtering class by implementing `ItemFilter`’s
method `accepts` and taking `feed_options` as an argument.

For instance:

```
class MyCustomFilter:
    def __init__(self, feed_options):
        self.feed_options = feed_options

    def accepts(self, item):
        if "field1" in item and item["field1"] == "expected_data":
            return True
        return False
```

You can assign your custom filtering class to the `item_filter` option of a feed.
See `FEEDS` for examples.

### ItemFilter

***class*scrapy.extensions.feedexport.ItemFilter(*feed_options: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)] | [None](https://docs.python.org/3/library/constants.html#None)*)[[source]](../_modules/scrapy/extensions/feedexport.html#ItemFilter)**

This will be used by FeedExporter to decide if an item should be allowed
to be exported to a particular feed.

**Parameters:**

**feed_options** ([*dict*](https://docs.python.org/3/library/stdtypes.html#dict)) – feed specific options passed from FeedExporter

**accepts(*item: [Any](https://docs.python.org/3/library/typing.html#typing.Any)*) → [bool](https://docs.python.org/3/library/functions.html#bool)[[source]](../_modules/scrapy/extensions/feedexport.html#ItemFilter.accepts)**

Return `True` if item should be exported or `False` otherwise.

**Parameters:**

**item** ([Scrapy items](items.html#topics-items)) – scraped item which user wants to check if is acceptable

**Returns:**

True if accepted, False otherwise

**Return type:**

[bool](https://docs.python.org/3/library/functions.html#bool)

## Post-Processing

Scrapy provides an option to activate plugins to post-process feeds before they are exported
to feed storages. In addition to using builtin plugins, you
can create your own plugins.

These plugins can be activated through the `postprocessing` option of a feed.
The option must be passed a list of post-processing plugins in the order you want
the feed to be processed. These plugins can be declared either as an import string
or with the imported class of the plugin. Parameters to plugins can be passed
through the feed options. See feed options for examples.

### Built-in Plugins

***class*scrapy.extensions.postprocessing.GzipPlugin(*file: [BinaryIO](https://docs.python.org/3/library/typing.html#typing.BinaryIO)*, *feed_options: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*)[[source]](../_modules/scrapy/extensions/postprocessing.html#GzipPlugin)**

Compresses received data using [gzip](https://en.wikipedia.org/wiki/Gzip).

Accepted `feed_options` parameters:

- gzip_compresslevel
- gzip_mtime
- gzip_filename

See [`gzip.GzipFile`](https://docs.python.org/3/library/gzip.html#gzip.GzipFile) for more info about parameters.

***class*scrapy.extensions.postprocessing.LZMAPlugin(*file: [BinaryIO](https://docs.python.org/3/library/typing.html#typing.BinaryIO)*, *feed_options: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*)[[source]](../_modules/scrapy/extensions/postprocessing.html#LZMAPlugin)**

Compresses received data using [lzma](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov_chain_algorithm).

Accepted `feed_options` parameters:

- lzma_format
- lzma_check
- lzma_preset
- lzma_filters

`lzma_filters` cannot be used in pypy version 7.3.1 and older.

See [`lzma.LZMAFile`](https://docs.python.org/3/library/lzma.html#lzma.LZMAFile) for more info about parameters.

***class*scrapy.extensions.postprocessing.Bz2Plugin(*file: [BinaryIO](https://docs.python.org/3/library/typing.html#typing.BinaryIO)*, *feed_options: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*)[[source]](../_modules/scrapy/extensions/postprocessing.html#Bz2Plugin)**

Compresses received data using [bz2](https://en.wikipedia.org/wiki/Bzip2).

Accepted `feed_options` parameters:

- bz2_compresslevel

See [`bz2.BZ2File`](https://docs.python.org/3/library/bz2.html#bz2.BZ2File) for more info about parameters.

### Custom Plugins

Each plugin is a class that must implement the following methods:

**__init__(*self*, *file*, *feed_options*)**

Initialize the plugin.

**Parameters:**

- **file** – file-like object having at least the write, tell and close methods implemented
- **feed_options** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – feed-specific options

**write(*self*, *data*)**

Process and write data ([`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes) or [`memoryview`](https://docs.python.org/3/library/stdtypes.html#memoryview)) into the plugin’s target file.
It must return number of bytes written.

**close(*self*)**

Clean up the plugin.

For example, you might want to close a file wrapper that you might have
used to compress data written into the file received in the `__init__`
method.

Do not close the file from the `__init__` method.

To pass a parameter to your plugin, use feed options. You
can then access those parameters from the `__init__` method of your plugin.

## Settings

These are the settings used for configuring the feed exports:

- `FEEDS` (mandatory)
- `FEED_EXPORT_ENCODING`
- `FEED_STORE_EMPTY`
- `FEED_EXPORT_FIELDS`
- `FEED_EXPORT_INDENT`
- `FEED_STORAGES`
- `FEED_STORAGE_FTP_ACTIVE`
- `FEED_STORAGE_S3_ACL`
- `FEED_EXPORTERS`
- `FEED_EXPORT_BATCH_ITEM_COUNT`

### FEEDS

Default: `{}`

A dictionary in which every key is a feed URI (or a [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
object) and each value is a nested dictionary containing configuration
parameters for the specific feed.

This setting is required for enabling the feed export feature.

See Storage backends for supported URI schemes.

For instance:

```
{
    'items.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'item_classes': [MyItemClass1, 'myproject.items.MyItemClass2'],
        'fields': None,
        'indent': 4,
        'item_export_kwargs': {
           'export_empty_fields': True,
        },
    },
    '/home/user/documents/items.xml': {
        'format': 'xml',
        'fields': ['name', 'price'],
        'item_filter': MyCustomFilter1,
        'encoding': 'latin1',
        'indent': 8,
    },
    pathlib.Path('items.csv.gz'): {
        'format': 'csv',
        'fields': ['price', 'name'],
        'item_filter': 'myproject.filters.MyCustomFilter2',
        'postprocessing': [MyPlugin1, 'scrapy.extensions.postprocessing.GzipPlugin'],
        'gzip_compresslevel': 5,
    },
}
```

The following is a list of the accepted keys and the setting that is used
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

### FEED_EXPORT_ENCODING

Default: `"utf-8"` ([fallback](settings.html#default-settings): `None`)

The encoding to be used for the feed.

If set to `None`, it uses UTF-8 for everything except JSON output, which uses
safe numeric encoding (`\uXXXX` sequences) for historic reasons.

Use `"utf-8"` if you want UTF-8 for JSON too.

Changed in version 2.8: The [`startproject`](commands.html#std-command-startproject) command now sets this setting to
`"utf-8"` in the generated `settings.py` file.

### FEED_EXPORT_FIELDS

Default: `None`

Use the `FEED_EXPORT_FIELDS` setting to define the fields to export, their
order and their output names. See [`BaseItemExporter.fields_to_export`](exporters.html#scrapy.exporters.BaseItemExporter.fields_to_export) for more information.

### FEED_EXPORT_INDENT

Default: `0`

Amount of spaces used to indent the output on each level. If `FEED_EXPORT_INDENT`
is a non-negative integer, then array elements and object members will be pretty-printed
with that indent level. An indent level of `0` (the default), or negative,
will put each item on a new line. `None` selects the most compact representation.

Currently implemented only by [`JsonItemExporter`](exporters.html#scrapy.exporters.JsonItemExporter)
and [`XmlItemExporter`](exporters.html#scrapy.exporters.XmlItemExporter), i.e. when you are exporting
to `.json` or `.xml`.

### FEED_STORE_EMPTY

Default: `True`

Whether to export empty feeds (i.e. feeds with no items).
If `False`, and there are no items to export, no new files are created and
existing files are not modified, even if the overwrite feed option is enabled.

### FEED_STORAGES

Default: `{}`

A dict containing additional feed storage backends supported by your project.
The keys are URI schemes and the values are paths to storage classes.

### FEED_STORAGE_FTP_ACTIVE

Default: `False`

Whether to use the active connection mode when exporting feeds to an FTP server
(`True`) or use the passive connection mode instead (`False`, default).

For information about FTP connection modes, see [What is the difference between
active and passive FTP?](https://stackoverflow.com/a/1699163).

### FEED_STORAGE_S3_ACL

Default: `''` (empty string)

A string containing a custom ACL for feeds exported to Amazon S3 by your project.

For a complete list of available values, access the [Canned ACL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl) section on Amazon S3 docs.

### FEED_STORAGES_BASE

Default:

```
{
    "": "scrapy.extensions.feedexport.FileFeedStorage",
    "file": "scrapy.extensions.feedexport.FileFeedStorage",
    "stdout": "scrapy.extensions.feedexport.StdoutFeedStorage",
    "s3": "scrapy.extensions.feedexport.S3FeedStorage",
    "ftp": "scrapy.extensions.feedexport.FTPFeedStorage",
}
```

A dict containing the built-in feed storage backends supported by Scrapy. You
can disable any of these backends by assigning `None` to their URI scheme in
`FEED_STORAGES`. E.g., to disable the built-in FTP storage backend
(without replacement), place this in your `settings.py`:

```
FEED_STORAGES = {
    "ftp": None,
}
```

### FEED_EXPORTERS

Default: `{}`

A dict containing additional exporters supported by your project. The keys are
serialization formats and the values are paths to [Item exporter](exporters.html#topics-exporters) classes.

### FEED_EXPORTERS_BASE

Default:

```
{
    "json": "scrapy.exporters.JsonItemExporter",
    "jsonlines": "scrapy.exporters.JsonLinesItemExporter",
    "jsonl": "scrapy.exporters.JsonLinesItemExporter",
    "jl": "scrapy.exporters.JsonLinesItemExporter",
    "csv": "scrapy.exporters.CsvItemExporter",
    "xml": "scrapy.exporters.XmlItemExporter",
    "marshal": "scrapy.exporters.MarshalItemExporter",
    "pickle": "scrapy.exporters.PickleItemExporter",
}
```

A dict containing the built-in feed exporters supported by Scrapy. You can
disable any of these exporters by assigning `None` to their serialization
format in `FEED_EXPORTERS`. E.g., to disable the built-in CSV exporter
(without replacement), place this in your `settings.py`:

```
FEED_EXPORTERS = {
    "csv": None,
}
```

### FEED_EXPORT_BATCH_ITEM_COUNT

Default: `0`

If assigned an integer number higher than `0`, Scrapy generates multiple output files
storing up to the specified number of items in each output file.

When generating multiple output files, you must use at least one of the following
placeholders in the feed URI to indicate how the different output file names are
generated:

- `%(batch_time)s` - gets replaced by a timestamp when the feed is being created
(e.g. `2020-03-28T14-45-08.237134`)
- `%(batch_id)d` - gets replaced by the 1-based sequence number of the batch.

Use [printf-style string formatting](https://docs.python.org/3/library/stdtypes.html#old-string-formatting) to
alter the number format. For example, to make the batch ID a 5-digit
number by introducing leading zeroes as needed, use `%(batch_id)05d`
(e.g. `3` becomes `00003`, `123` becomes `00123`).

For instance, if your settings include:

```
FEED_EXPORT_BATCH_ITEM_COUNT = 100
```

And your [`crawl`](commands.html#std-command-crawl) command line is:

```
scrapy crawl spidername -o "dirname/%(batch_id)d-filename%(batch_time)s.json"
```

The command line above can generate a directory tree like:

```
->projectname
-->dirname
--->1-filename2020-03-28T14-45-08.237134.json
--->2-filename2020-03-28T14-45-09.148903.json
--->3-filename2020-03-28T14-45-10.046092.json
```

Where the first and second files contain exactly 100 items. The last one contains
100 items or fewer.

### FEED_URI_PARAMS

Default: `None`

A string with the import path of a function to set the parameters to apply with
[printf-style string formatting](https://docs.python.org/3/library/stdtypes.html#old-string-formatting) to the
feed URI.

The function signature should be as follows:

**scrapy.extensions.feedexport.uri_params(*params*, *spider*)**

Return a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) of key-value pairs to apply to the feed URI using
[printf-style string formatting](https://docs.python.org/3/library/stdtypes.html#old-string-formatting).

**Parameters:**

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

For example, to include the [`name`](spiders.html#scrapy.Spider.name) of the
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
