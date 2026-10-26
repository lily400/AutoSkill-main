# Feed 压缩导出配置 Evidence

- family: 未分类技能
- skill_id: 4a141183-0f4c-5000-9f5c-660f26e01360
- support_count: 1

## Evidence 1

- support_id: f06edde2-fe5d-5f4b-aa06-9e85ad751bee
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 11437:13083
- confidence: 0.70
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
