# P0 历史材料

本目录保存 P0 时使用的配置、来源调查清单和一次性工程脚本。它们用于解释与复核 `runs/p0_qsv_select_clean_001`、`runs/p0_qsv_select_clean_002`，不是现行实验入口。

- 原始运行内的 `wrapper_snapshot/`、SKILL.md、中间阶段、HTTP 记录和注册证据仍留在各自 run 目录，未移动、未重生成。
- 旧来源路径 `data/sources/` 和精确字节备份 `data/legacy_bytes/` 因旧运行验证依赖而原位保留。
- 新实验不得从本目录读取配置或来源；统一使用 `scripts/lab.py`、`configs/generation/` 和 `data/catalog.json`。
