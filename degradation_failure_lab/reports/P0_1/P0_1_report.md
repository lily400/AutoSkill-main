# P0.1 实际交付报告

验收：**PASS（多案例框架重构与离线验收）**。
真实 P0 Clean 基线继续有效，非本轮重新生成。本轮新真实运行 0，付费模型调用 0。
正式案例只有 case001_qsv_select；没有生成退化输入或扩充真实来源数据。

## 版本、入口与边界

项目：`D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab`；Python：`D:\anoconda1\envs\autoskill\python.exe`。
本地父仓库当前提交：eeb80f05f2be41a48423eaaf83e5a5d9b751f573。
P0 已审计的官方参考提交：94c47ca488d4ba4117d20272e66d49b9877e68cf。
本轮没有重新查询远程 latest；164 个官方生成代码、提示词、测试及配置文件与 P0/本轮开始时一致。
Git 对 AutoSkill-main 的状态检查无新增改动。完整证明在 preservation.json。

真实生成入口：scripts/lab.py → cli.main → ExperimentRunner.run/prepare → adapter.execute →
官方 AutoSkill/AutoSkillConfig + AutoSkill4Doc.extract_from_doc（extract.py:325）→
build_default_document_pipeline → DocumentBuildPipeline.build → ingest_document → extract_skills →
compile_skills → register_versions → 官方注册表、版本决定和 SkillBank 写入。
文档解析为官方 document/file_loader.py 的 load_file_units。
阶段实现分别为 ingest.py、stages/extractor.py、stages/compiler.py、store/versioning.py；
正式符号位置也保留在旧 reports/audit/code_symbol_locations.json。
新增 wrapper 使用 P0 的原样 HTTP 观察逻辑；模型参数扩展仍走官方 connector_factory。
测试逐字段证明请求只多了 thinking 参数，不改提示词、各阶段 token 预算或响应正文。

支持范围：官方 OpenAI 兼容协议、任意配置的服务/模型名称、官方 hashing embedding。
没有实现其他供应商私有传输协议的统一调用统计。顺序批量执行，无并发调度器。
退化算子未实现；仅校验已经物化的输入、父级原文哈希和条件标签。

## 重构前后

| 重构前 | 当前 |
|---|---|
| source_manifest + 单份 qsv 配置 | Dataset/Source 注册 + 独立 Case/Condition 定义 + 共享生成配置 |
| scripts/run_clean.py 内全部编排 | src/degradation_lab 通用包；旧脚本转到公共 runner |
| runs/<P0 run_id> | 新 runs/<case>/<condition>/<run>；旧路径通过 legacy_index 保留 |
| verify 固定 qsv/model/user/single-document | 根据运行快照读取任意来源、模型、用户、多个文档及技能 |
| verify 改写历史 exports/manifest | 只读历史，外部 sidecar 导出 |
| Markdown 规则审核 | 保留原 Markdown + 原判断的结构化初始评价 |
| 没有多案例批次入口 | 同一 plan/run 支持多个 case、condition、repeat |

主要目录：

```text
degradation_failure_lab/
├─ README.md / .gitignore / .gitattributes
├─ configs/environment.json / generation/deepseek_flash.json
│  └─ clean_qsv_select*.json                 原 P0 配置保留
├─ data/catalog.json / manifests/ / sources/ 原来源与检查表不动
│  ├─ legacy_bytes/                        经 Git 精确核对的 6 份原字节
│  └─ legacy_byte_index.json                换行恢复证据
├─ cases/case001_qsv_select/
│  ├─ case.json / rules.json / conditions.json
│  └─ inputs/clean.json
├─ schemas/                                7 份严格字段 schema
├─ src/degradation_lab/
│  ├─ io.py / schema.py / catalog.py
│  ├─ runner.py / adapter.py / provider_adapter.py
│  └─ artifacts.py / evaluation.py / cli.py / __init__.py
├─ scripts/lab.py / run_clean.py / verify_run.py
│  └─ 其余 P0 获取/审计/隔离测试工具保留
├─ runs/legacy_index.json
│  ├─ p0_qsv_select_clean_001/               未移动、未覆盖
│  └─ p0_qsv_select_clean_002/               未移动、未覆盖
├─ evaluations/case001_qsv_select/clean/p0_qsv_select_clean_002/p0_initial_review.json
├─ results/exports/<P0 run_id>/             本轮新增只读导出
│  └─ aggregates/P0_1/                     runs.json / rule_results.json / CSV
├─ tests/test_wrapper.py / test_framework.py
└─ reports/P0_1/                            审计、日志、哈希证明、示例、完整树
```

完整逐文件树见 project_tree.txt，不用折叠目录代替实际清单。

## 公共代码的实际职责

| 文件 | 实际功能 |
|---|---|
| catalog.py | SourceManager 发现并验证来源；CaseManager 校验案例、规则、条件与输入引用 |
| schema.py + schemas/ | 严格类型、必需/未知字段、枚举和 ID；引用/哈希/证据位置由 manager 补充 |
| runner.py | 全批次预检、独立目录、输入/源码/配置快照、全局 run_id 防重、密钥检查和轻量 ledger |
| adapter.py | 真正调用官方公开 API，保留原样 HTTP 观察和官方调用栈；不是提取算法 |
| provider_adapter.py | 保留公开 connector_factory 的 thinking 参数扩展 |
| artifacts.py | 兼容旧/新 run，只读验证，所有候选与正式技能的 trace 导出，导航统计 |
| evaluation.py | 多规则/多技能评价合同、证据/实体验证、初始化 unreviewed、规则级 JSON/CSV 汇总 |
| cli.py / scripts/lab.py | list、validate、plan、run、verify、evaluation-init/validate、aggregate 公共命令 |

完整关联为 dataset → source → case → condition/input → run → 官方文档/窗口/support/draft/spec/skill。
Evaluation 引用 case/condition/run/rule，并允许多个最终 skill_id 与阶段实体。
Rule/Condition ID 按案例限定，Run ID 全局唯一，Skill ID 取官方 UUID；没有混用这些 ID。

## case001 与两次历史记录

旧规则 R1–R7 的 ID、英文内容和原 lines 数组逐字保留；有原检查表哈希验证。
规则、评价不传入生成模型。qsv 来源版本仍为 257ae7b38738688138dc430c2ccb4eef8766f3fc，
docs/help/select.md 原始 SHA-256 仍为 74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384。
类别仍 RECONSTRUCTED_OFFICIAL_SOURCE，不是已确认论文原始快照。

成功 002：通用验证 **PASS，24/24**。
2 窗口 / 4 Support / 4 Draft / 4 Spec / 2 正式程序技能，另外有可见副本和导航。
失败 001：通用读取 **PARTIAL**，官方状态 failed；保留 3 个编译 Spec 及注册 empty LLM output 异常，未伪装成功。
旧报告、两次运行、原始数据和 P0 配置共 287 个既有文件的本轮前后字节哈希均未改变。

正式技能仍在：
- runs/p0_qsv_select_clean_002/SkillBank/Users/docskill/csv-列选择与重排/SKILL.md
- runs/p0_qsv_select_clean_002/SkillBank/Users/docskill/敏感列排除/SKILL.md

原质量判断保留：R1–R5 主要命令规则正确；R6 引用要求已表达但 PowerShell 行为未审核；
R7 缺失；R4 额外“仅共享或发布时使用”限制不受来源支持。结构化为 7 条保留记录及 1 条新增错误记录，
审核来源明确为 P0 助手对照原文，未声称用户人工批准。模板残留等全局问题仍在原质量报告。
汇总实际为 2 个历史 run、15 条规则审核行：001 的 7 条 unreviewed，002 的 8 条记录。
不能将这 15 条行数当作 15 条独立原始规则或论文成功率。

## 已发现问题及处理

1. 重构前 Git 工作区 LF→CRLF：原文和 5 份 wrapper 快照受影响；已从固定本地提交读取 Git blob，
   每份原字节精确匹配 P0 清单，独立保存，不覆盖原文件。验证报告逐文件显示恢复方式。
   不是把 hash 改成新的工作区 hash。未来快照用限定的新路径 -text 保护，不把旧历史误列为修改。
2. 旧 verifier 固定模型与来源并写回历史：已改为运行配置驱动与外部 sidecar。
3. 新包装层开发时的落盘顺序问题：状态须先写再计算 artifact_manifest；已修正并有异常路径哈希测试。
4. 既有上游测试 153 项 / 7 失败：仅引用原隔离日志，本轮未重跑或修复；不是本轮新增回归。
5. 本轮未发起新的付费模型运行。新多案例编排、官方解析及 API 签名已经离线测试；
   新目录形态的一次真实付费端到端运行仍需下一次获授权实验实际产生。没有把 fixture 冒称真实生成。

## 验证及下一入口

本轮最终 **22 项包装/框架测试全部通过**，测试中禁止 urllib 网络调用。
共享来源、case002 加载、多个输入、三个不同条件各三次独立准备、全局 ID 防重、SkillBank 隔离、
严格 schema、原规则不变、非 qsv/model/user 的 trace 导出、失败/密钥记录、评价/聚合均验证。
三种退化条件九次 fixture 仅在 TemporaryDirectory，未写入正式案例或真实 runs。

所有最终实际命令与退出码在 commands.json，日志 command_01..08.log；初次审计与修改方案
在 audit_and_plan.md，第一次发现 EOL 问题及恢复证明见 eol_recovery.json。
core 文件哈希前后均一致，未修改、删除或重构官方生成实现。

已经具备多案例**顺序批量编排能力**。未来增加 case002 的完整 JSON、三份条件清单、
九次真实运行命令、保存路径及规则汇总命令见 case002_example.md。
无需为案例复制 Python 运行/验证脚本或核心配置。输入不齐时 validate/plan 明确失败，不自动制造材料。

下一阶段最小实验：保留本公共配置，准备并审核一个真实退化输入清单，
先 validate/plan，再执行 case001 的全新 clean 与该 degraded 条件各一次，逐规则评价。
本轮到此停止，不运行真实退化实验、不扩充数据、不设计改进算法。
