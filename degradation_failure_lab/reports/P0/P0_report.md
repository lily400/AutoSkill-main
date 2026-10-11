# Stage P0 实施与验收报告

日期：2026-10-10。实验目录：`D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab`。

实际目录概览见根目录 README；完整逐文件目录树见 `reports/project_tree.txt`，全部交付文件摘要见 `reports/delivery_manifest.json`。

## 验收结论

**PASS：已拥有一条可重新运行、输入版本固定、实际调用模型、由官方 Anything2Skill 生成正式 SKILL.md 且关键证据链通过验证的工程基线。** 成功案例为 `p0_qsv_select_clean_002`，输入仅一份真实 qsv 文档。第一次失败尝试独立保存，没有拿失败产物替代正式技能。

PASS 的范围是本次单文档生成和追踪。不是论文完整实验复现，不是逐字节确定性重现，也不是技能内容全部正确。内容中的缺失、过度推断、上游测试失败和尚未执行的 qsv 验证均在下文列出。下一阶段可以使用这个工程接口；需要先固定本报告成功配置，并将 Clean 本身的内容缺陷纳入分析，不能假设 Clean 输出无错。

## 1. 本地及官方版本审计

| 项目 | 核查结果 |
|---|---|
| 真正源码目录 | `D:\Baseline-anthing2skill\AutoSkill-main\AutoSkill-main` |
| Git 根目录 | `D:\Baseline-anthing2skill\AutoSkill-main`，不是上面这个嵌套源码目录 |
| 本地 HEAD | `19b660299c557431044cc07788c6232d1deb2f99`，提交标题“删除版本2.0”；不能直接当作上游 SHA |
| 查询时官方 main | `94c47ca488d4ba4117d20272e66d49b9877e68cf` |
| 文件比对 | 官方树 10,048 个 blob；本地 169 个对应文件逐字节一致，0 个差异，9,879 个官方文件本地缺失；本地生成代码没有额外非上游文件 |
| 缺失内容 | 主要包含 SkillBank、data、examples 及其他子项目；文档生成所需 AutoSkill4Doc、autoskill、测试与配置已存在 |
| 本地额外材料 | `test_doc.md` 为简短自建 CSV 测试文本；预先存在的 `research/` 为自建研究目录，未当作论文来源，未修改 |
| 上游保护 | 164 个生成模块、提示词、taxonomy、测试和包配置文件有运行前后 SHA-256 比对；两次生成均一致；结束时另检查 Git 跟踪文件差异 |

具体证据：`reports/audit/official_comparison.json`、`official_tree.json`、`local_environment.json`、每次运行的 `upstream_before.json` / `upstream_after.json`。

公开入口是包导出的 `AutoSkill4Doc.extract_from_doc`。CLI 是 `python -m AutoSkill4Doc build` 或安装后的 `autoskill4doc build`；`pyproject.toml` 指向 `AutoSkill4Doc.extract:main`。不存在此前可能想当然假设的 `AutoSkill4Doc/api.py` 或 `cli.py`。

## 2. 从代码确认的调用链

成功运行实际调用公共 Python API，`official_call_trace.json` 与每次 HTTP 的上游调用栈共同证明以下链条被执行。

| 阶段 | 上游文件与入口 | 主要数据与作用 |
|---|---|---|
| 公共入口 | `AutoSkill4Doc/extract.py:325 extract_from_doc` | 校验真实 provider、解析 taxonomy/family，构造默认 pipeline，调用 build |
| 编排 | `AutoSkill4Doc/pipeline.py:460 DocumentBuildPipeline.build` | 新建/恢复中间运行，依次 ingest、extract、compile、register；本次未恢复旧运行 |
| 文件读取 | `document/file_loader.py:84 load_file_units` | 读取固定路径，输出 title/text/source_file；本次先独立做了解析预检 |
| 文档规范化 | `ingest.py:1135 _build_text_unit`、`:1165 _build_record` | TextUnit、DocumentRecord、章节和内容哈希；_build_text_unit 会 strip 首尾空白，本次只去掉末尾一个换行 |
| 章节/窗口 | `ingest.py:687 _outline_matches_from_llm`；`document/windowing.py:633 build_windows_for_record` | 默认 LLM 大纲判断、规则窗口构建；保留窗口 doc_id、window_id、span 与章节关系 |
| 技能提取 | `stages/extractor.py:857 _plan_unit_skills`、`:896 _expand_planned_skill`、`:996 _build_support_and_draft` | 每窗口先 plan 再 expand，得到 SupportRecord 和 SkillDraft；本次第一窗口产生 4 个候选，第二窗口 0 个 |
| 正式编译 | `stages/compiler.py:244 _compile_group`、`:621 compile`、`:793 compile_skills` | 依据合同和 taxonomy 分组，构造 SkillSpec、来源绑定和结构化 skill_body |
| 注册/协调 | `store/versioning.py:2811 register_versions`、`:2390 VersionManager.reconcile`、`:1253 classify_change` | 检索候选、keep/discard 或版本变更决策、层次/重复处理、生命周期与 provenance |
| 正式库写入 | `store/versioning.py:967 _sync_store_skills`，调用 SDK 的正式存储路径 | 生成 `Users/docskill/<slug>/SKILL.md` |
| 分组暂存 | `store/staging.py:404 write_registration_staging` | 保留注册后的分组快照 |
| 可见树 | `store/visible_tree.py:104 sync_visible_skill_tree` | 生成程序技能副本、证据引用、领域/family 导航与索引 |

Pipeline 有流式 `_resume_or_extract`、`_resume_or_stream_compile`、`_resume_or_stream_register` 分支；正式非 dry-run 执行会走这些分支并保存节点快照。本包装调用完整 build，不把仅 ingest、dry-run 或单独编译冒充正式完成。

**数据结构实际字段与联系：**

- `models.py:494 TextUnit`：unit_id、title、text、source_file、metadata；是标准化输入单元。
- `models.py:412 DocumentRecord`：doc_id、raw_text、sections、checksum/content_hash、metadata；窗口和 support 用 doc_id 关联它。
- `models.py:543 StrictWindow`：window_id、doc_id、section_heading、paragraph 范围、text、span、metadata。
- `models.py:618 SupportRecord`：support_id、doc_id、skill_id、excerpt、relation_type、span；metadata 保存 window_id。
- `models.py:684 SkillDraft`：draft_id、doc_id、目标、触发条件、步骤、约束、例子和 support_ids。
- `models.py:849 SkillSpec`：skill_id、skill_body、结构化合同、support_ids、版本和状态；metadata.source_draft_ids 指向原 Draft。
- Registry 保存 documents/supports/skills 及生命周期、版本、变更和 provenance；SkillBank 是正式存储与可见树的集合，不能仅按目录下文件数量计算技能数。
- 正式 SKILL.md 的 id 与注册 skill_id 一致；可见树的 evidence_manifest 再关联 SupportRecord 和 DocumentRecord。

原始字节与官方规范化文本分开保存。**官方 span 不被直接解释为原始 Markdown 的字节或行偏移。** 包装另存逐行精确匹配的 `window_source_alignment.json`，未匹配的规范化行也保留，避免伪造精确位置。

## 3. 输入、输出与环境

官方读取器直接处理 Markdown、文本及 JSON/JSONL 的文本内容；Word 需要外部 textutil/antiword/catdoc；PDF/图片等已知二进制类型被跳过。本地本阶段只验证 Markdown，未声称其他格式运行成功。输入扫描会排除官方生成的可见技能目录，避免回读输出。

Python 3.10.21 可用，实际包导入、原有测试和真实生成均已运行。项目声明依赖为空；没有 requests、PyYAML、dotenv 并不阻塞这条使用标准库的路径。当前终端有 DEEPSEEK_API_KEY 和 ARK_API_KEY，后者未使用；OPENAI_API_KEY 和 DASHSCOPE_API_KEY 未配置。官方自动选择逻辑不识别 DEEPSEEK_API_KEY，故包装明确从该环境变量注入内存中的 SDK 配置。未读取或改写本地 .env。

实际模型是 `deepseek-flash`，服务地址 `https://api.deepseek.com/v1/chat/completions`。成功配置关闭模型推理，使用官方内置 hashing/256 embeddings、单 worker、max_documents=1、每窗口最多 4 候选、recommended strict windows、LLM 大纲。每次运行最多 32 次 HTTP 请求、观测 token 阈值 200,000；首次失败配置上限为 24 次。token 阈值在下一次请求前检查，不是供应商结算的硬封顶。所有温度与注册阶段预算沿用官方逻辑。

DeepSeek 官方说明其推理默认开启；上游注册对空检索结果的判断固定 256 tokens，层级判断 128 tokens。第一轮真实证据表明部分短预算请求 finish_reason=length 且 content 为空。通过上游 `connector_factory` 扩展补充非推理参数解决兼容问题，未修改官方文件、提示词或注册预算。适配器字段差异测试通过。参考：[DeepSeek 推理模式说明](https://api-docs.deepseek.com/guides/thinking_mode/)。

## 4. 论文原始数据追查与重建

检查范围包括本地目录、上游 main 完整 Git tree、两个公开分支、Release/Tag、README、论文 v3 正文/参考文献和作者组织的关联仓库列表，并查看了 SkillGym README 与公开数据卡。

- 本地初始没有 data、examples 或 SkillBank；tests 存在。test_doc.md 和 research 材料均不能证明属于论文语料。
- 官方 main 有 `data/train`、`data/eval`，抽查 JSON 是 messages 对话数据；没有证据表明它们是论文 qsv 帮助文档快照。`SkillBank/DocSkill/README.md` 明确这是生成的技能树。examples 是代码使用示例，不是来源语料。Git tree 没有 qsv 命名路径。
- 官方 Release 列表为空；另一公开分支 `codex-upload-cbt-dir-20260421`（`60c994bcc78dcdcb10e2a9767078d2c563e44883`）未找到 qsv 命名路径或 data 树。相关 API 响应已保存。
- 论文 v3 指向 qsv 官方文档网站，参考文献访问日期为 2026-06-08；未找到可验证的文件清单、Git commit、哈希或原始语料下载包。没有额外公开附录快照入口被核实。
- SkillGym 的公开资源是技能、任务模板、环境及轨迹等；没有发现将其标为 Anything2Skill 论文原始 qsv 文档的依据。未下载其大型数据集。
- 原始来源文档、任务定义、测试输入、标准答案和预生成技能是不同对象：本轮不将对话答案、示例代码或现成 SKILL.md 换名当作输入文档。

上述是有范围的“未找到可验证原始快照”，不是断言作者从未公开过任何位置的数据。证据存于 `reports/audit/`。文献：[论文 v3](https://arxiv.org/html/2606.09316v3)，[固定上游](https://github.com/ECNU-ICALK/AutoSkill/tree/94c47ca488d4ba4117d20272e66d49b9877e68cf)，[SkillGym](https://github.com/ECNU-ICALK/SkillGym)。

采用最小重建：直接下载 qsv 固定提交下 `docs/help/select.md` 的原始字节，外加相同提交的 LICENSE-MIT 和 Cargo.toml 作为许可/版本证据。没有人为编造 qsv 内容，没有下载其他帮助文档。

| 来源字段 | 值 |
|---|---|
| source_id | qsv-select-257ae7b38738 |
| source_repository | https://github.com/dathere/qsv |
| source_commit | 257ae7b38738688138dc430c2ccb4eef8766f3fc |
| source_path | docs/help/select.md |
| source_url | https://raw.githubusercontent.com/dathere/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/docs/help/select.md |
| sha256 | 74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384 |
| license | MIT；原始 LICENSE-MIT 随文件保存 |
| document_type / command | official_cli_help_markdown / qsv select |
| 数据类别 | RECONSTRUCTED_OFFICIAL_SOURCE；paper_snapshot_verified=false |
| downloaded_at | 精确 UTC 时间保存在 data/manifests/qsv_select.json 及每次运行的清单副本 |

该文件包含足够的命令示例和参数规则，因此没有增加第二份文档。命令可执行文件准备检查：同提交 Cargo.toml 标记 qsv 24.0.0；官方 24.0.0 有 Windows x64 GNU/MSVC 发布包，URL、大小和发布摘要均已记录。本次固定文档和 `src/cmd/select.rs` 的 Git blob 与 24.0.0 发布标签一致。整仓库提交不相同，不能声称二进制由这个较新的提交构建。本机 PATH 未找到 qsv/rustc/cargo；未安装或执行。后续可下载经过摘要校验的 24.0.0 发布包验证 select 行为；若要求整个仓库提交完全一致的二进制，需要配置满足 Rust 1.99 的构建环境。详见 `qsv_binary_readiness.json`。

## 5. 实际执行命令与两次运行

工作目录均为独立实验根目录，Python 路径如下；调用时环境变量已存在，没有把密钥放入命令。

```powershell
& 'D:\anoconda1\envs\autoskill\python.exe' -B 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\scripts\prepare_sources.py'
& 'D:\anoconda1\envs\autoskill\python.exe' -B 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\scripts\audit_extra.py'

# 第一次真实尝试；当时脚本默认读取 clean_qsv_select.json。
& 'D:\anoconda1\envs\autoskill\python.exe' -B 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\scripts\run_clean.py' --run-id p0_qsv_select_clean_001

# 成功运行；使用新空库，未恢复或复制第一次的 Draft/Spec。
& 'D:\anoconda1\envs\autoskill\python.exe' -B 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\scripts\run_clean.py' --config 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\configs\clean_qsv_select_non_thinking.json' --run-id p0_qsv_select_clean_002

& 'D:\anoconda1\envs\autoskill\python.exe' -B 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\scripts\verify_run.py' --run 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\runs\p0_qsv_select_clean_002'
& 'D:\anoconda1\envs\autoskill\python.exe' -B -m unittest discover -s 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\tests' -v
& 'D:\anoconda1\envs\autoskill\python.exe' -B 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\scripts\test_upstream.py'
```

`invocation.json` 保存每次运行的原始 argv、工作目录、Python 版本和空库证明；wrapper_snapshot 保存该次包装脚本。旧 run-id 拒绝复用；复跑请省略 run-id 或使用新名称。

| 结果 | clean_001 | clean_002 |
|---|---:|---:|
| 输入真实文档 | 1 | 同一份 1 |
| TextUnit / DocumentRecord | 1 / 1 | 1 / 1 |
| StrictWindow | 7 | 2 |
| SupportRecord / SkillDraft / SkillSpec | 3 / 3 / 3 | 4 / 4 / 4 |
| 正式注册程序技能 | 0 | 2 |
| HTTP 尝试 / 成功 | 21 / 19 | 15 / 15 |
| 已报告 input tokens | 59,495 | 47,194 |
| 已报告 output tokens | 36,605 | 8,433 |
| 已报告 total tokens | 96,100 | 55,627 |
| 最终状态 | PARTIAL，注册 empty LLM output | PASS，completed、errors=[] |

两轮都是真实调用；合计 36 次 HTTP 尝试、34 次成功，接口报告 151,727 tokens。第一轮两次网络失败由上游重试，费用未知；真实接口未返回结算金额，因此 billed_cost=null，不伪造价格或费用。两次窗口数不同来自模型配置/输出不同，不可当作 Clean/Degraded 实验对。

成功运行时间为 12:23:01–12:24:19 UTC（北京时间 20:23:01–20:24:19）。官方 4 个注册判断中，两个 create，另两个 discard：

- CSV 列选择与重排：create。
- 敏感列排除：create。
- 列排序与随机打乱：因同批次通用技能已覆盖而 discard。
- 选择器语法冲突转义：因同批次通用技能已覆盖而 discard。

没有发生需要报告的跨旧库 merge；没有另外运行 `canonical-merge` CLI。保留了官方 keep/discard 决策和分组 staging，不能把 discard 改称 merge。

## 6. 实际产物与追踪

正式文件的完整路径：

```text
D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\runs\p0_qsv_select_clean_002\SkillBank\Users\docskill\csv-列选择与重排\SKILL.md
D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab\runs\p0_qsv_select_clean_002\SkillBank\Users\docskill\敏感列排除\SKILL.md
```

另有两个可见副本，位于 `SkillBank/通用技能领域/Family技能/qsv-select/二级技能/`，各带 `references/evidence.md` 和 `evidence_manifest.json`。领域与 family 的 `总技能/SKILL.md` 是导航产物。因此物理上有 6 个 SKILL.md，独立来源支持的程序技能仅 2 个。目录使用“通用技能领域”来自上游默认 taxonomy 展示名称，并不表示本包装另设研究领域。

官方自动保存：

| 路径（相对成功 run） | 实际内容 |
|---|---|
| SkillBank/.runtime/intermediate_runs/<official_run_id>/ingest/result.json | TextUnit、DocumentRecord、StrictWindow |
| 同运行 extract/windows、documents、aggregate、result.json | 分窗口输出、SupportRecord、SkillDraft、聚合与错误 |
| 同运行 compile/documents、result.json | SkillSpec 及编译后 supports/drafts |
| 同运行 register/decisions、documents、result.json | create/discard、注册结果、生命周期、版本、provenance |
| 同运行 status.json、final/summary.json | 阶段完成/失败与最终摘要 |
| SkillBank/.runtime/document_registry/ | 注册的文档、证据、技能及版本记录 |
| SkillBank/.runtime/staging/ | 两个注册技能的分组暂存结果 |
| SkillBank/.runtime/library_manifest.json | 可见树索引 |
| SkillBank/Users/docskill、中文可见树 | 正式技能、可见副本、来源引用、导航 |

包装补充保存：源快照及 provenance 清单、无密钥运行配置、argv、Python 信息、模型请求/响应/usage、原始客户端调用栈、解析预检、标准输出日志、异常、源码前后摘要、完整文件哈希清单、结构化 exports、技能 ID 对应表、原文行匹配、规则审核与测试记录。所有要求的文档侧中间结构均已取得；不可见的服务端内部状态与账单金额不作伪造。输出 JSON 中的 model 别名无法独立保证未来模型权重不变。

证据链示例：`source_id + SHA256 → doc 83df504e-ec88-5282-8168-b2b1e35829c7 → window 492febe3-ac09-5817-91e4-195334c0eaf0 → support 69a12244-23ce-507b-96b6-a3cd30c9c606 → draft d5b50768-a930-5fec-b2b7-43823c8be1dd → skill 3aab94b4-5f80-54ee-89cd-136656f9e5d6 → 正式 SKILL.md + 官方 evidence_manifest`。第二技能同样可追踪，详见 `exports/traceability.json`。

## 7. 验证结果与限制

`verification.json` 的检查全部通过：来源与哈希、真实 HTTP/各模型阶段、公共入口调用、无 mock、非空技能、ID 对应、编译正文和证据引用保留、Draft→Support/Spec→Draft、窗口/文档关系、注册 provenance、官方证据文件、空库、无跳过/无恢复，以及 164 个上游文件未变。HTTP 响应返回值摘要与记录文件一致。

包装层 4 个测试全部通过：真实来源哈希及类别、独立空库与碰撞拒绝、拒绝 mock/明文密钥配置、模型参数适配器仅增加 thinking 字段。

上游文档测试执行 153 项，146 通过、7 失败。在独立的字节相同临时源码副本中再次运行，仍为 7 项失败。不能宣称上游测试全绿。失败包括：恢复注册预期未抛异常、并行结果顺序、Windows 默认路径断言、4 项版本/变更判断断言。源码保持原样。本轮单文档单 worker、显式空库和实际记录可证明当前案例完成，但这些失败限制对多文档、恢复和复杂合并的推广。

首次原有测试自动在源码默认 SkillBank 中生成了一个检索缓存。该目录初始不存在；核实文件唯一性和本次测试时间后，已把它归档到 `reports/upstream_test_side_effect/`，再清理本次创建的文件与空目录。官方源文件未修改；后续测试脚本采用临时副本隔离。两次真实生成始终使用各自 run 的 SkillBank，从未使用该测试缓存。

内容审核结果见 `quality_review.md`：5 组关键规则主要语义正确；引用规则的 shell 执行待审核；通用选项缺失；敏感列技能增加了来源不支持的限定；存在 Therapist 模板残留。未把 SKILL.md 文件存在等同于高质量。未安装 qsv，未执行命令，未做大规模基准。

来源准备过程中已修复实验包装自身的 UTF-8 默认解码问题，并将不存在的 LICENSE 下载路径改为实际的 LICENSE-MIT；这些不是上游算法改动。最终源文件均保留下载原始字节。

## 8. 后续是否需要修改上游

**不需要修改官方生成代码即可开展 Clean/Degraded 输入对照。** 当前接口接受显式清单、验证实际文件哈希、每次建立独立库并保留相同证据链。下一阶段须保持成功配置、模型适配器、embedding、taxonomy、预算和上游文件版本一致，为每个输入记录原始来源及变换关系。

目前不应扩大解释为“已经拥有无错的高质量技能生成器”或“论文指标可复现”。阻塞当前 P0 的推理参数问题已经在配置兼容层解决；原始论文快照未核实、上游测试失败、内容缺陷、qsv 尚未安装和模型别名可能变化，均作为后续实验的明确限制保留。本轮到此停止，不构造退化、不设计图算法、不扩展数据规模。
