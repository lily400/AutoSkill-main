# Feed 导出压缩配置 Evidence

- family: 未分类技能
- skill_id: 22a119a0-0339-5040-bae2-b8b592879f9b
- support_count: 1

## Evidence 1

- support_id: 689128f7-7ebb-535a-977f-ed9e58baf613
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 11437:13083
- confidence: 0.60
- quote: Accepted `feed_options` parameters:

- gzip_compresslevel
- gzip_mtime
- gzip_filename

See [`gzip.GzipFile`](https://docs.python.org/3/library/gzip.html#gzip.GzipFile) for more info about parameters.

Compresses received data using [lzma](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov_chain_algorithm).

Accepted `feed_options` parameters:

- lzma_format
- lzma_check
- lzma_preset
- lzma_filters

`lzma_filters` cannot be used in pypy version 7.3.1 and older.

See [`lzma.LZMAFile`](https://docs.python.org/3/library/lzma.html#lzma.LZMAFile) for more info about parameters.

Compresses received data using [bz2](https://en.wikipedia.org/wiki/Bzip2).

Accepted `feed_options` parameters:

- bz2_compresslevel

See [`bz2.BZ2File`](https://docs.python.org/3/library/bz2.html#bz2.BZ2File) for more info about parameters.
