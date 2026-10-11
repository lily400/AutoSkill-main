# P0.3 GitHub 精简分支记录

- 基线：`master` 提交 `c820a0ee341b3c46b34ec4be0294516fe5aa764e`。
- GitHub 历史归档分支：`archive/p0-p02-full-20261011`；创建时指向相同完整提交。
- 工作分支：`refactor/p03-slim-experiment-lab`，不直接覆盖 master。
- 清理范围：本次只修改 `degradation_failure_lab/`；官方 Anything2Skill 源码不改。
- 移除当前工作树中的旧 P0 两次完整 runs、历史审计 reports、旧数据字节副本、legacy 脚本与配置、旧评价和两个弃用入口；旧内容仍可通过归档提交访问。
- 现行 `src/degradation_lab/artifacts.py` 不再读取扁平 P0 运行及旧换行字节索引；`evaluation.py` 不再对 P0 报告位置作特殊回退；测试专注多案例夹具而不依赖已移走的历史文件。
- case001 的 R1–R7 内容与源证据未改动，移除仅供历史 P0 文件的 provenance 引用。
- **验证限制**：GitHub 端的树结构与变更可核验；当前工具环境无法直接访问 Windows 固定路径 `D:\Baseline-anthing2skill`，因此不能声称已跑完本地 Python 单元测试或 P0 历史恢复验证。合并前必须在本地执行 `lab.py validate`、`plan` 与 `unittest`，必要时先处理发现的错误。
- 尚无新框架真实付费模型端到端运行，因此不宣称生成结果已验证。
