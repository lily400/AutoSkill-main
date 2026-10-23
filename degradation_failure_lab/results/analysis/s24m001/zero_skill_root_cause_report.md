# Scrapy024 第二轮：零候选根因与证据链

日期：2026-10-23。**本轮模型 API 请求 0；没有生成 Skill、运行 Agent 或修改官方固定源码。**

结论：已证实并在独立副本修复三项问题：技术 URI 的 `@` 触发作者误判、段落中部列表未被识别导致参数上下文丢失、跨 chunk 的窗口 ID 冲突。修复副本的 30 项预处理/兼容测试及 9 项单请求合同测试通过。**这些结果不解释全部 18 次空 Plan 的模型决策，也不等于 Skill 提取成功。**

**CONDITIONAL GO：只具备开展一次经批准的单窗口 Plan 诊断的条件；尚不具备宣称正式 CleanSkill 校准成功的条件。** 本轮到离线修复和请求冻结结束。

## 1. 证据范围与版本

- 原运行 R：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m001`。
- 原版 U：`D:\AS\AutoSkill-main\AutoSkill-main`；固定提交 `94c47ca488d4ba4117d20272e66d49b9877e68cf`。当前可读 164 个文件与运行记录、C 盘固定 Git 克隆一致；克隆 HEAD 也核实为该提交，不以此冒称 D 盘目录具有已验证的 Git HEAD。
- 审计 A：`D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m001`。
- 前次报告实际位于 [zero_skill_extraction_diagnosis.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m001/zero_skill_extraction_diagnosis.md)，保留不动。其逐请求表、成本表、原始证据目录继续复用。
- Clean 原件：`R\inputs\input001\feed-exports.md`，原始 SHA-256 `a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d`。它来自 SkillGenBench `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d` 的 task-curated 发布材料，不是最新官方手册保真认证。
- 本轮验证原 `artifact_manifest.json` 的 121 项，以及未列入自身清单的 manifest，共 122 个原运行文件。完整性结果见 `A\round2\integrity.json`。不存在补造模型响应。

本轮实际离线执行在 C 盘现有 `audit_2026-10-15/scrapy024_preflight/calibration_evidence/s24m001_round2_staging/`，新增报告和可重算证据归档到 A。版本名为 **lab-preprocess-v1**：改了预处理，保持原版 Plan prompt、候选解析和模型请求参数。它不是未经修改的端到端官方基线。

## 2. 实际执行链

下表未带包名前缀的代码路径均位于 `U\AutoSkill4Doc`；`autoskill/` 路径相对 U；行号来自未修改固定源码。R 中路径是原运行产物，A/round2 中是本轮离线派生证据。**Outline 发生在最终 sections/windows 之前**，不能按“先生成 windows 再 Outline”理解历史执行顺序。

| 阶段 | 输入及转换代码 | 输出、丢失情况与证据 |
|---|---|---|
| 文件→文本/标题 | `document/file_loader.py:84–146 load_file_units`、`:185–215 _read_any_file_as_text`；`ingest.py:1165–1230 _build_record`。输入 R/inputs/input001/feed-exports.md | title 是相对路径 `input001\feed-exports.md`；源文中的页面标题仍是正文前缀。LF 规范化及末尾 strip 后 raw_text 24,629 字符；目标规则仍完整。实际 DocumentRecord 在 R/SkillBank/.runtime/intermediate_runs/20261022T215553_a402e3b9/ingest/result.json。 |
| 标题候选→Outline | `ingest.py:226–239 _detect_headings`、`:653–672 _merged_outline_candidates`、`:687–783 _outline_matches_from_llm`、`:1016–1037 _parse_sections_with_fallback` | 43 个规则标题候选合并21个启发式候选，实际请求64项（上限64），1次HTTP001；响应选36个标题，包括candidate13 FTP、level=3。43个规则候选preview为空，另外21个有局部preview；不是整份文档的无损输入。R/http/001/{request,response}.json、A/round2/outline_comparison.json。 |
| Outline→sections | `ingest.py:496–556 _build_sections_from_headings`；`:109–126 _looks_like_front_matter_heading` | FTP 已被 Outline 选中，但正文前 240 字符中的 URI user-info `@` 被当作作者线索，`:528` 跳过整节；原始 sections 为 35。candidate 的 line_index=-1 不构成原因，建节用 start/end。保存的 sections 与本轮完整函数重放完全一致。 |
| sections→规划分块 | `windowing.py:552–624 _build_planning_section/_planning_sections`、`:188–226 _split_long_section` | 按根章节拼接、按 max_section_chars=10000 分块。拼接后 span 属于组合文本坐标；不能直接当作原文件偏移。没有历史逐块快照，本轮可确定性重算，证据类别为离线重放。 |
| 分块→段落保留 | `windowing.py:143–158 _paragraphs_from_section`、`:257–285 _has_process_signal/_build_paragraph_blocks` | 两个 379/413 字符的段落未命中 process/anchor，且超过 320，丢失 overwrite 定义和 APPE 例外。95 字符默认表留下。历史没有每个 if 分支遥测；本轮基线重放与实际窗口一致。A/round2/baseline_filter_trace.json。 |
| 保留段落→windows | `windowing.py:288–450` 分组、邻接、合并、strict/fallback；`:452–502 _window_from_blocks`；`:633–715 build_windows_for_record` | 18 个窗口正文哈希不同，ID 只有 17 个；8/18 撞 ID。严格窗口选择还会舍弃已通过段落筛选的内容，不等于保留段落的全集。原 18 窗口见 ingest/result.json，本轮 baseline_ok/windows.json 完全一致。 |
| window→Plan 输入 | `stages/extractor.py:756–795 _build_unit_payload`、`:797–855 _complete_extract_json`、`:857–898 _plan_unit_skills`；`prompts.py:39–113 build_offline_extract_prompt` | 18 个窗口逐一成为 HTTP 002–019 的 user.excerpt，同时传标题、section/span、metadata、taxonomy；确实含正文，不是只发 ID。每个 excerpt+span 仅匹配一个历史窗口；A/round2/baseline_ok/historical_plan_checks.json。没有完整目标规则的请求。 |
| 模型→解析→Plan 候选 | `core/llm_utils.py:28` 起获取/解析，`autoskill/utils/json.py:23–81` 容错 JSON 解析；extractor:877–897 | 18 份真实 raw response 的 content 都为 `{"skills": []}`，单 choice、finish_reason=stop、completion_tokens=5。合法空数组直接返回零计划；没有非空候选被过滤，没有 JSON repair。原响应均保存，本轮逐份复核。 |
| Plan→Expand/supports/drafts | `extractor.py:951–994 _extract_unit_skills` 的 978 行空计划早返回；`:996–1023 _build_support_and_draft` | Expand 0 次，supports/drafts 0；必填字段/执行内容验证根本没有接收到历史候选。R/official_call_trace.json、extract/result.json；前次 A/evidence/offline_parser_replay.json 可复用。 |
| drafts→compile→register | `stages/compiler.py:635–654` 空分组迭代；R 内 compile/register/result.json | 空结果本地收尾，模型调用 0，specs/upserts 0。registry 仅 documents=1；导航树无实际技能。物理 domain_root/SKILL.md 只是空导航骨架，不能计为提取成功。 |
| SDK→外层退出 | **R/wrapper_snapshot/degradation_lab/adapter.py:132–162**，尤其 140；同快照 cli.py:81 | official_result.status=completed、errors=[]、total_skill_specs=0 → 适配器 exit_code=2、FAILED。异常分支默认码1，没有 exception.json。若由该 CLI 返回 shell，则聚合为1；没有历史 shell LASTEXITCODE，不能把适配器2一概说成 shell 实测2。 |

本轮使用固定源码和保存的 Outline 响应，断言 stub 收到的 system 与 user JSON 等于历史 HTTP 001；然后重放实际章节和窗口函数。**旧 sections/windows 逐字段精确一致**，强于仅按最终空结果反推路径，但仍不是恢复不存在的历史分支日志。

36个所选标题中，Storage backends没有直属正文（紧接Local filesystem标题），FTP则被错误过滤；另加入页面标题前缀section，因此原sections为35，修复为36。Outline未选中的页面标题、编号步骤和启发式重复候选列在outline_comparison.json；“没选作标题”不等于其正文被删除，编号步骤仍可位于父节内。当前没有证据把Outline选择本身列为FTP规则缺失的根因。

配置补充：`ingest.py:1117–1121` 调用窗口函数时仅传 strategy 与 max_section_chars，所以当前窗口构造使用函数默认 **max_chars=2400**。配置里的 extractor `max_chars_per_chunk=6000` 不等于这些 strict 窗口的切块大小。recommended 映射 strict；max_units=0 未限制窗口数。

## 3. 为什么全部 Plan 为空：已知与未知

| 分类 | 当前结论 |
|---|---|
| 已证实的预处理缺陷 | FTP 作者误判；长段落中列表识别失败。能确定目标信息丢失，不能确定这解释了所有窗口的模型选择。 |
| 已证实的身份缺陷 | 8/18 ID 同为 `b20c5d95-f076-588e-93d0-4f2abad08203`。原 key 缺位置与内容；17 个检查点覆盖18个输入。两次 HTTP 均真实发出，所以它不是本次漏发或空计划的原因。续跑误跳过的风险由 pipeline.py:1007–1024 的 ID 集合逻辑支持。 |
| 已确认的提示词/准入事实 | prompt 明确允许空数组，偏保守可调用契约；含 therapist/session/treatment 等领域措辞，同时允许 knowledge_reference。存在适配风险，**尚无证据证明提示词错误直接导致18次为空**。 |
| 已确认的解析/验证事实 | 历史没有解析故障或“所有非空候选被拒绝”。Plan 只做列表/字典、非空 name 等检查，截取前4项；没有 confidence 硬阈值。Expand 后需 name/description/prompt，以及 workflow/intervention/constraints/cautions 任一执行内容。 |
| 有支持但未确认的假设 | 上下文损失、保守准入提示、心理治疗措辞、默认 taxonomy 与技术文档不匹配可能影响选择；各自贡献和模型内部理由未知。 |
| 无法确定 | 完整输入下同模型同 prompt 是否产出候选；非空候选能否表达规则、Expand 后能否形成合格 canonical Skill。模型只返回空数组，没有解释文本；未记录不可变模型版本或提供方账单。 |

新增本地 `NativeAdmissionTest` 证明：knowledge_reference 在没有 workflow、但有 constraints 时可进入 support/draft；缺少所有执行/约束内容才被拒绝。这不代表任何模型已经生成该候选，也不使用参考 Skill 来推定应当成功。

源材料带来的技术定义、默认值、条件、例外可以构成约束型资产，原代码没有强制必须多步骤操作程序。是否被模型认为“足够 operational”仍待单窗口检验。

## 4. 开销、停止与实验语义

历史 Outline 1 次：6,290 输入 +510 输出；Plan 18 次：66,626 输入 +90 输出；总 **19 次 HTTP、73,516 tokens**。cached prompt 31,744 已在输入量中；重试0；完整请求重复率0/18。响应全部成功，无429、length截断或额度超限证据。真实收费未知。

合法空 Plan 属于成功处理窗口，原版继续覆盖其余窗口。没有“连续空列表则停止”分支；18次各处理不同输入，不能称为同一输入错误重试。compile/register 只有本地空收尾，没有隐藏收费。

外层已有150请求/450,000已观察tokens上限、原版限速10/60秒；按已用tokens事前检查可能被下一次响应越过。未来成本保护应先做本轮保真门禁，再做**单窗口独立诊断**。若增加连续空值暂停，必须标记为提前终止的诊断，不将未扫描窗口记为失败或冒充完整基线结果。本轮未改原运行循环/退出逻辑。

## 5. 两个实验问题与下一步

**A：目标规则是否进入输入？** 历史原版路径 FAIL；lab-preprocess-v1 的实际序列化请求已通过完整438–449行保真门禁，原文件未补写。局限见 [plan_input_fidelity_report.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m001/plan_input_fidelity_report.md)。

**B：完整规则进入原版 Plan 后能否产生候选？** 尚未验证；18次旧响应不能回答。离线测试也不能回答。

唯一优先下一步：用户批准后，对冻结的第18个修复窗口调用一次原版 Plan prompt，记录原始响应并停止。无换模型、改 prompt、重试、Expand 或整批重跑。即使非空也只完成 Plan 诊断；要进入真实 Agent 校准仍需后续生成和独立验收。详见 [single_window_test_plan.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m001/single_window_test_plan.md)。
