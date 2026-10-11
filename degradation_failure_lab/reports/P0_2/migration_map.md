# P0.2 迁移映射

| 原路径 | 新路径或处理 | 说明 |
|---|---|---|
| `data/manifests/qsv_select_canonical.json` | `legacy/P0_1/data/manifests/qsv_select_canonical.json` | 退出现行目录；其职责合并到唯一 `data/manifests/qsv_select.json` |
| `data/manifests/qsv_select.json`（P0 原版） | `legacy/P0/data/manifests/qsv_select.json` | 原字节保留；现行同名清单改指 raw source |
| `data/manifests/qsv_auxiliary_files.json` | `legacy/P0/data/manifests/qsv_auxiliary_files.json` | P0 来源调查证据 |
| `data/manifests/qsv_select_rules.json` | `legacy/P0/data/manifests/qsv_select_rules.json` | 作为 case001 rules 的历史 provenance 保留 |
| `data/sources/qsv/<commit>/` | 原位保留 | P0 `source_manifest.json` 仍直接引用 |
| `data/legacy_bytes/` | 原位保留 | P0/P0.1 历史哈希兼容所需 |
| Git blob 中的 qsv 三份原始文件 | `data/raw_sources/qsv/<commit>/` | 唯一现行权威来源目录，使用原始 LF 字节 |
| `cases/case001_qsv_select/inputs/clean.json` 的 Legacy 路径 | `data/raw_sources/.../select.md` | Clean 与 SourceManager 指向同一文件 |
| `configs/clean_qsv_select*.json` | `legacy/P0/configs/` | P0 旧配置；现行只保留 environment + generation |
| `scripts/common.py`、`provider_adapter.py`、`prepare_sources.py`、`audit_extra.py`、`test_upstream.py` | `legacy/P0/scripts/` | P0 专用或一次性代码，不再参与正式调用 |
| `tests/test_wrapper.py` | `legacy/P0/tests/test_wrapper.py` | 旧包装层测试；现行覆盖合并在 `tests/test_framework.py` |
| `reports/audit/` 与 reports 根的 P0 文件 | `reports/P0/` | 与 P0.1、P0.2 报告分层 |
| `reports/P0_1/implementation_tools/` | `legacy/P0_1/implementation_tools/` | 一次性实施脚本与验收报告分离 |
| `scripts/run_clean.py`、`scripts/verify_run.py` | 原位薄转发 | 明确 deprecated；实际调用统一进入 `degradation_lab.cli` |

未列出的 `src/degradation_lab/` 现行模块、case001 定义、schemas、evaluations、results 与 P0 运行产物不做无关搬迁。
