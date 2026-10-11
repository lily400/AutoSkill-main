# Legacy P0 source checkout

本目录只因 P0 的 `source_manifest.json` 仍引用这些路径而保留。Windows Git 检出把三个文本文件转换为 CRLF；旧运行验证通过 `data/legacy_byte_index.json` 与 `data/legacy_bytes/` 核对其 LF Git 原字节。

现行案例禁止使用本目录。权威来源位于 `data/raw_sources/`。
