# 运行目录

- `p0_qsv_select_clean_001/`、`p0_qsv_select_clean_002/` 是不可改写的 P0 历史运行；`legacy_index.json` 提供案例身份映射。
- 新运行统一写入 `<case_id>/<condition_id>/<run_id>/`，每次拥有独立输入快照和 SkillBank。
- 派生验证文件写入 `results/exports/`，不回写历史运行。
