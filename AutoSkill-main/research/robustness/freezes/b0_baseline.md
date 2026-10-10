
# B0 Baseline Freeze

- `freeze_id`: `freeze-b0-stage0-v1`
- 本地 commit：`19b660299c557431044cc07788c6232d1deb2f99`
- 官方 upstream：`ECNU-ICALK/AutoSkill@94c47ca488d4ba4117d20272e66d49b9877e68cf`
- 定义：当前被冻结的官方 AutoSkill/AutoSkill4Doc 原生文档到技能流程。冻结只记录版本与配置，不复制源码。

## 入口与真实链路

- CLI：`autoskill4doc build ...` 或 `python -m AutoSkill4Doc build ...`，入口为 `AutoSkill4Doc.extract:main`。
- Python：构建 `DocumentBuildPipeline` 后调用公开 `build(...)`。
- 实际链路：文件加载 → `ingest_document`/结构化与 window 规划 → `extract_skills` → `compile_skills` → `register_versions` → registry/runtime store 与可见 Skill 树。
- 非 dry-run 会在 `.runtime/intermediate_runs` 保存阶段状态并支持恢复；最终注册包含 registry、staging、library manifest 和可见 `SKILL.md` 产物。

## 输入格式

文本优先：UTF-8 文本、Markdown、JSON/JSONL 等可直接读取；`.doc/.docx` 依赖本地转换工具；PDF、图片、音频、视频、压缩包等已知二进制格式会跳过。可输入单文件或目录，目录按排序后的路径扫描并排除生成产物和隐藏运行目录。

## 当前默认配置

| 配置 | 冻结值 |
|---|---|
| Python | `D:\anoconda1\envs\autoskill\python.exe` / 3.10.21 |
| extract strategy | `recommended`，当前归一为 strict |
| max chars per window | 6000 |
| overlap chars | 300 |
| max candidates per window | 5 |
| max windows per document | 0（不限） |
| document workers | 1 |
| extract retries | 3 |
| retry base backoff | 1.0 秒，指数退避 |
| outline mode | `llm` |
| store | `<repo_root>/SkillBank/DocSkill`；实验 adapter 必须显式改为隔离 store |
| registry | `<store>/.runtime/document_registry` |
| LLM provider/model | smoke 实测自动检测为 `dashscope / qwen-plus` |
| embeddings | smoke 实测为 `dashscope / text-embedding-v4` |

## Prompt、window 与关键文件哈希

| 文件 | SHA-256 |
|---|---|
| `AutoSkill4Doc/prompts.py` | `CF622C6B7AB7141A9B2923F9B099079C6353CBE83C0E1D8584ABA813A3E66405` |
| `AutoSkill4Doc/stages/extractor.py` | `41F1170216871E53CE066F6BB1D6E9A55BF6495A382DDFFAAF8676C0E2D83501` |
| `AutoSkill4Doc/stages/compiler.py` | `47425AAF4564B9D02C9BF0CC90055FFDA8EF3241ADAFEA2F0F600319CE024B81` |
| `AutoSkill4Doc/store/versioning.py` | `14C80507B8EEC00C9F096E9DFD6F8660FE30DC2D2EC30F5974536CA81919339B` |
| `AutoSkill4Doc/document/windowing.py` | `5B9689B3D0E27DFF48CDB4B62F35516C4EEB4681ED13F110480009EB6E279408` |
| `AutoSkill4Doc/document/file_loader.py` | `9DC3BF54AFF346C4A5E7764022CE89665095C43DD61C7FCE6FC7A992482BB555` |
| `AutoSkill4Doc/core/provider_config.py` | `25A16524F68AB5C62233CBABA0469E8F794E3DCBCA590CA9C587023E8CCEF808` |
| `AutoSkill4Doc/core/llm_utils.py` | `82B9450B6BFB7B5BA1AC7114C336416D32C9884C5DB4E4278FF1077ADB554FD8` |
| `AutoSkill4Doc/pipeline.py` | `13E18FBB4762EE6B3262C089A122CEB68A5539402D6519B84CA602EDDB59B829` |
| `AutoSkill4Doc/extract.py` | `DDAEFB3F880E97EAEFDE63476C72CDA67D950D3060903D68B9F2921E34E6C289` |
| `AutoSkill4Doc/models.py` | `813377B45532E49A7CE96F980FE4E38BD336E60D8FA7C36ABCCDE6E0928C57E0` |

Prompt 主构建器位于 `AutoSkill4Doc/prompts.py`；抽取、编译和版本管理阶段还会使用各阶段代码中的固定提示与修复提示。实验期间不得覆盖这些提示。

## 中间产物与 provenance

中间运行目录保存 `status.json`、ingest、extract（document/window/audit/aggregate）、compile、register（document/decision/result）和 `final/summary.json`。registry 分别保存 document、support、skill 等实体及 manifest。`DocumentRecord`、`SupportRecord` 和 `SkillSpec` 的标识、span、source file、content hash、window metadata 与 provenance links 构成官方可观测来源信息。

## 失败行为

CLI 对 partial/failed 返回非零退出码。非 dry-run 记录失败阶段和中间状态；adapter 必须原样封存，不得自动用 verifier 反馈修复。生成失败进入后续端到端分母。

## 禁止修改范围

`AutoSkill4Doc/**`、`autoskill/**`、`tests/**`、`pyproject.toml` 以及其中的 prompt、模型和 `SkillSpec`。研究逻辑只允许新增在 `research/robustness/**`。
