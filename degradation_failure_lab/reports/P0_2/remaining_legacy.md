# P0.2 保留的 Legacy 文件

| 保留位置 | 保留原因 | 是否可用于新实验 |
|---|---|---|
| `runs/p0_qsv_select_clean_001/` | 真实失败运行，包含请求、异常、中间产物与 wrapper snapshot | 否，只读验证 |
| `runs/p0_qsv_select_clean_002/` | 真实成功运行，包含正式 SKILL.md、注册和 provenance | 否，只读验证 |
| `data/sources/qsv/<commit>/` | 两个 P0 source_manifest 直接引用；移动会破坏旧运行解析 | 否 |
| `data/legacy_bytes/` | 证明 CRLF 检出仅为换行差异，并恢复旧清单/产物的原始 Git 字节 | 否 |
| `data/legacy_byte_index.json` | 连接旧路径工作区哈希、期望哈希、Git commit 与归档字节 | 否 |
| `legacy/P0/configs/` | P0 当时真实配置，运行目录另有 config 快照 | 否 |
| `legacy/P0/data/manifests/` | P0 来源与规则调查记录，保持原哈希 | 否 |
| `legacy/P0/scripts/` | P0 来源准备、审计和上游测试工具 | 否 |
| `legacy/P0_1/implementation_tools/` | P0.1 一次性安装、恢复与报告脚本 | 否 |
| `reports/P0/`、`reports/P0_1/` | 阶段报告、日志与审计原证据 | 否 |
| `scripts/run_clean.py`、`scripts/verify_run.py` | 旧命令兼容；仅转发到现行 CLI，避免复制业务逻辑 | 不作为正式入口 |

`data/raw_sources/.../select.md` 与 `data/legacy_bytes/.../select.md` 字节相同，但不能合并：前者是现行稳定路径，后者是 `legacy_byte_index.json` 已记录的历史证据路径。`data/sources/.../select.md` 字节不同（CRLF），也不能用删除或重写掩盖。
