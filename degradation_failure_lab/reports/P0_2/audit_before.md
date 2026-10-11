# P0.2 整理前审计

审计日期：2026-10-11。审计对象为 `degradation_failure_lab` 的实际文件内容、代码引用、Git blob、运行清单与离线测试，不按文件名推断职责。

## 主要问题

| 问题 | 整理前证据 | 影响 |
|---|---|---|
| 现行原文引用 Legacy | `data/catalog.json` 指向 `qsv_select_canonical.json`，其 `local_path` 是 `data/legacy_bytes/.../select.md` | 新案例会把历史备份误当权威来源 |
| 同一 source_id 有两份现行候选清单 | `qsv_select.json` 指向 `data/sources`，`qsv_select_canonical.json` 指向 `legacy_bytes` | 维护者需猜测哪份生效 |
| Windows 换行转换 | `data/sources/.../select.md` 为 4,974 字节、SHA-256 `017958...`；Git blob 为 4,795 字节、SHA-256 `74e7ac...` | 工作区字节不满足来源清单 |
| 辅助来源也被转换 | `Cargo.toml` 和 `LICENSE-MIT` 工作区哈希与原始 Git blob 哈希不同 | 许可证/版本证据缺少统一原字节位置 |
| 旧配置与共享配置并列 | `configs/clean_qsv_select*.json` 与 `configs/generation/deepseek_flash.json` 同时存在 | 无法一眼分辨现行配置 |
| 旧脚本与公共包并列 | `scripts/common.py`、`provider_adapter.py`、来源审计脚本与 `src/degradation_lab/` 同时存在 | 容易误建第二套执行路径 |
| 报告阶段混放 | P0 报告和 `reports/audit/` 位于 reports 根，P0.1 已单独分组 | 历史与现行维护面不清晰 |

## 字节与历史用途结论

- qsv commit：`257ae7b38738688138dc430c2ccb4eef8766f3fc`。
- qsv `select.md` 的 Git blob：`1fb480611b98b1b741a948043fee12358ee7701c`。
- 经核验原始 SHA-256：`74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。
- P0 的两个 `source_manifest.json` 都引用 `data/sources/.../select.md`，因此该旧路径不能删除或移动。
- P0.1 的现行 case001 引用 `data/legacy_bytes/.../select.md`，需改为新的 `data/raw_sources/.../select.md`。
- P0 运行内没有原文快照；`legacy_byte_index.json` 与 `legacy_bytes` 是旧清单哈希验证的必要证据。

## 整理前依赖关系

```text
现行 P0.1: catalog → qsv_select_canonical.json → data/legacy_bytes/.../select.md
历史 P0: run/source_manifest.json → data/sources/.../select.md
历史哈希兼容: data/sources CRLF → legacy_byte_index.json → data/legacy_bytes LF
旧命令: scripts/run_clean.py / verify_run.py → src/degradation_lab
正式命令: scripts/lab.py → src/degradation_lab
```

## 迁移约束

不修改 `runs/p0_qsv_select_clean_001/002`、不重生成 SKILL.md、不改官方仓库、不删除旧来源路径或 `legacy_bytes`，只把现行引用改到统一 raw source，并把可安全移动的旧配置、旧脚本和报告归档。
