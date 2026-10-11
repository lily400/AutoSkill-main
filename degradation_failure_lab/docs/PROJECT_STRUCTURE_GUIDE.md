# degradation_failure_lab 项目结构与唯一运行路径

本文只用 `case001_qsv_select` 说明从 qsv 官方 `select.md` 到正式 `SKILL.md` 的真实路径。标签含义如下：

- **[Anything2Skill 原版]**：官方仓库提供的代码或阶段产物语义。
- **[本研究新增]**：本项目的目录、校验、运行隔离、观察与评价代码。
- **[运行自动产物]**：执行后生成，不作为手工维护的配置。
- **[历史兼容]**：只用于读取、解释或验证 P0/P0.1，不得注册为新案例输入。

## 1. 原始 select.md 放在哪里

**[本研究新增]** 唯一现行原文是：

```text
data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md
```

该文件直接由本仓库中已核验的 qsv Git blob 字节建立，长度 4,795 字节，SHA-256 为 `74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。同目录的 `Cargo.toml` 和 `LICENSE-MIT` 是版本及许可证证据，不作为额外生成文档。

**[历史兼容]** `data/sources/.../select.md` 是 P0 运行仍引用的 Windows CRLF 检出副本；`data/legacy_bytes/.../select.md` 是 P0.1 为验证旧清单保存的 LF Git 原字节。两者都不能由现行 catalog 注册。

## 2. 哪个 JSON 记录来源及哈希

**[本研究新增]** `data/manifests/qsv_select.json` 记录 `source_id`、远程仓库、完整 commit、上游相对路径、许可证、字节数、SHA-256、分类和 `local_path`。`data/catalog.json` 把该清单注册到 dataset `qsv`。

现行注册关系只有一条：

```text
data/catalog.json
  → data/manifests/qsv_select.json
  → data/raw_sources/qsv/<commit>/select.md
```

旧的 `qsv_select_canonical.json` 已退出；P0 原始 `qsv_select.json` 按原字节移入 `legacy/P0/data/manifests/`。

## 3. case001 如何引用来源

**[本研究新增]** `cases/case001_qsv_select/case.json` 通过 `dataset_id: qsv` 和 `source_ids: [qsv-select-257ae7b38738]` 引用来源，不写第二份文件路径。它同时选择共享生成配置，并在 `pipeline_overrides` 中填写 qsv 的 domain、domain_type 和 family_name。

`src/degradation_lab/catalog.py` 中的 `SourceManager` 先解析 catalog 和来源清单，再验证原文的路径、SHA-256、字节数和 commit 格式；`CaseManager` 再验证案例中的 source_id 确实属于所选 dataset。

## 4. clean.json 是什么

**[本研究新增]** `cases/case001_qsv_select/inputs/clean.json` 是条件输入清单，不是原文副本。它记录 `input_id`、父 `source_id`、父 SHA-256、实际输入路径和输入 SHA-256。

对 Clean 条件，`CaseManager` 要求该路径与来源清单的 `local_path` 完全相同，且哈希相同。因此 case001 不再把原文复制到案例目录，也不再把 `legacy_bytes` 当成正式输入。

未来 Degraded 条件的已物化文件必须放在 `data/condition_inputs/`；框架读取它，但不在运行时生成退化内容。

## 5. lab.py 如何读取案例

**[本研究新增]** `scripts/lab.py` 只做两件事：把 `src/` 加入 Python 导入路径，然后调用 `degradation_lab.cli.main()`。正式命令只有 `list`、`validate`、`plan`、`run`、`verify`、`evaluation-init`、`evaluation-validate` 和 `aggregate`。

`cli.py` 解析命令后先使用 `CaseManager` 校验 catalog、case、condition、rules 和 inputs，再把已校验的 manager 交给 `ExperimentRunner`。`plan` 只校验和打印计划；`run` 才可能访问模型服务。

## 6. runner.py 做什么

**[本研究新增]** `src/degradation_lab/runner.py` 负责：

1. 合并共享生成配置和 case 的 pipeline overrides；
2. 在任何付费请求前完成整批预检；
3. 创建 `runs/<case>/<condition>/<run_id>/` 和空的独立 `SkillBank`；
4. 把输入字节、来源/案例/规则/条件/配置、环境路径和包装层源码快照保存到本次运行；
5. 记录官方源码运行前哈希；
6. 调用 `adapter.execute()`；
7. 将运行索引追加到 `results/run_index.jsonl`。

每个 run_id 全项目唯一，已有目录不会被覆盖。

## 7. adapter.py 怎样调用官方 Anything2Skill

**[本研究新增]** `src/degradation_lab/adapter.py` 从运行快照读取配置和输入，通过 `configs/environment.json` 定位官方源码，然后导入官方 `AutoSkill`、`AutoSkillConfig`、`extract_from_doc` 和 `load_file_units`。

它建立独立本地 store，并调用：

```text
AutoSkill4Doc.extract_from_doc(..., dry_run=False, continue_on_error=False)
```

adapter 只做输入快照、HTTP 正文观察、密钥脱敏、调用阶段记录和官方代码前后哈希检查；它不改官方 prompt、候选提取、编译或注册算法。`src/degradation_lab/provider_adapter.py` 是唯一现行 provider 扩展。

## 8. 官方 Ingest、Extract、Compile、Register 分别产生什么

以下阶段均为 **[Anything2Skill 原版]**，文件属于 **[运行自动产物]**，保存在本次运行的 `SkillBank/.runtime/intermediate_runs/<official_run_id>/`：

| 阶段 | 主要实际产物 |
|---|---|
| Ingest | `ingest/result.json`；包含 text_units、documents、windows、skipped_documents 和 errors |
| Extract | `extract/result.json` 及窗口/文档分片；包含 documents、windows、support_records、skill_drafts 和 errors |
| Compile | `compile/result.json`；把 drafts 与 supports 编译为 skill_specs，同时保留错误 |
| Register | `register/result.json` 及 decisions；包含生命周期、变更、版本历史、provenance_links、upserted_store_skills、staging_runs 和 visible_tree |

P0 成功运行 `p0_qsv_select_clean_002` 的实际统计是 1 个 document、2 个 windows、4 个 supports、4 个 drafts、4 个 specs，最终注册 2 个程序技能。该统计只描述历史 P0，不代表 P0.2 新运行。

## 9. 正式 SKILL.md 保存在哪里

**[Anything2Skill 原版] [运行自动产物]** 对新运行，正式程序技能位于：

```text
runs/case001_qsv_select/clean/<run_id>/SkillBank/Users/<user>/<skill>/SKILL.md
```

官方还会在 `SkillBank/通用技能领域/` 生成可见树中的父技能、二级技能和导航技能。程序技能身份以 Register 阶段的 `upserted_store_skills` 与 `Users/.../SKILL.md` 中的 id 对应关系为准，不能仅按文件数量判断成功。

**[历史兼容]** P0 成功运行仍在 `runs/p0_qsv_select_clean_002/`；失败运行 `001` 的真实失败状态也保留，均不迁入新分层路径以免改写历史证据。

## 10. artifacts.py、evaluation.py 如何读取和分析结果

**[本研究新增]** `artifacts.py` 只读加载新旧运行。它从官方四阶段快照重建 Source → Window → Support → Draft → Spec → SKILL.md 链路，核验模型调用、来源/输入/产物哈希、官方代码不变、正式技能与证据引用，并可把派生 JSON 写到 `results/exports/`。它不会改运行目录。

**[本研究新增]** `evaluation.py` 把规则级人工判断保存到 `evaluations/<case>/<condition>/<run>/<evaluation_id>.json`，验证 rule_id、skill_id、阶段实体和证据行号。`aggregate` 将工程状态与质量判断分开导出到 `results/aggregates/`，不会把存在 SKILL.md 自动判为语义正确。

## 文件职责表

| 相对路径 | 文件作用 | 类型 | 是否为现行入口 | 新增案例是否需要修改 |
|---|---|---|---|---|
| `README.md` | 项目入口、正式命令和边界 | [本研究新增] | 是（阅读） | 否 |
| `data/catalog.json` | dataset 到来源清单的唯一注册表 | [本研究新增] | 是（数据） | 仅新增 dataset/source 时 |
| `data/manifests/qsv_select.json` | qsv select 来源身份、路径与哈希 | [本研究新增] | 是（数据） | 复用来源时否 |
| `data/raw_sources/qsv/<commit>/select.md` | 唯一现行原文 | [本研究新增] | 是（数据） | 复用来源时否 |
| `cases/case001_qsv_select/case.json` | 案例身份、source_ids 与配置引用 | [本研究新增] | 是（案例） | 新案例新建同类文件 |
| `cases/case001_qsv_select/conditions.json` | 条件身份、类型、输入清单引用 | [本研究新增] | 是（案例） | 新案例新建同类文件 |
| `cases/case001_qsv_select/inputs/clean.json` | Clean 输入引用，不复制原文 | [本研究新增] | 是（案例） | 新案例新建同类文件 |
| `cases/case001_qsv_select/rules.json` | 评价规则与来源证据行 | [本研究新增] | 是（评价定义） | 新案例新建同类文件 |
| `configs/environment.json` | 官方源码位置 | [本研究新增] | 是（环境） | 否 |
| `configs/generation/deepseek_flash.json` | 共享模型、预算和 pipeline 配置 | [本研究新增] | 是（配置） | 通常否 |
| `scripts/lab.py` | 唯一正式 CLI 入口 | [本研究新增] | 是 | 否 |
| `src/degradation_lab/catalog.py` | SourceManager 与 CaseManager | [本研究新增] | 否 | 否 |
| `src/degradation_lab/runner.py` | 计划、运行隔离和快照 | [本研究新增] | 否 | 否 |
| `src/degradation_lab/adapter.py` | 调用官方 API 并记录透明证据 | [本研究新增] | 否 | 否 |
| `src/degradation_lab/provider_adapter.py` | 唯一 provider 扩展 | [本研究新增] | 否 | 否 |
| `src/degradation_lab/artifacts.py` | 只读验证与追踪链导出 | [本研究新增] | 否 | 否 |
| `src/degradation_lab/evaluation.py` | 评价记录验证与聚合 | [本研究新增] | 否 | 否 |
| `runs/<case>/<condition>/<run_id>/` | 新运行的完整隔离快照 | [运行自动产物] | 否 | 自动生成 |
| `runs/p0_qsv_select_clean_001/002/` | P0 真实失败/成功运行 | [历史兼容] | 否 | 否 |
| `legacy/P0/` | 旧配置、调查清单和脚本 | [历史兼容] | 否 | 否 |
| `legacy/P0_1/` | 一次性重构工具 | [历史兼容] | 否 | 否 |
| `../AutoSkill-main/AutoSkill4Doc/` | 官方文档构建管线 | [Anything2Skill 原版] | 由 adapter 调用 | 否 |

## 新增 case002 的教程（不实际创建）

以下步骤说明未来如何新增案例；P0.2 没有创建正式 `case002`。

1. 若 case002 复用 qsv select，同一 `source_id` 已在 `data/catalog.json` 注册，不复制 `select.md`，也不新增第二份来源清单。若使用新来源，先把固定原始字节放入 `data/raw_sources/<repository>/<commit>/`，新建一份来源清单并注册到 catalog。
2. 新建 `cases/case002_<name>/case.json`、`rules.json`、`conditions.json` 和 `inputs/clean.json`。Clean 的 `path` 直接指向来源清单的 `local_path`。
3. 若需要退化条件，将已物化输入放入 `data/condition_inputs/case002_<name>/`，再在 `conditions.json` 和对应 `inputs/<condition>.json` 中记录 operator、参数、父哈希和输入哈希。
4. 执行离线检查：

   ```powershell
   & $py -B scripts\lab.py validate
   & $py -B scripts\lab.py plan --case case002_<name> --condition clean --repeat 1
   ```

5. 只有在输入、预算和凭证均确认后才执行 `lab.py run`。无需复制 `run_clean.py`、`verify_run.py`、`provider_adapter.py`，也无需修改 `src/degradation_lab/`。

现有测试会在临时目录注册 fixture case002、多个条件和多个运行，并验证公共代码无需变化；fixture 不进入正式 catalog，也不冒充真实模型实验。
