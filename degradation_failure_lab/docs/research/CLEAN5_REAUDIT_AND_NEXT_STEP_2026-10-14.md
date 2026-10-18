# Anything2Skill 五个 Clean 案例再审计与下一步决策

任务日期：2026-10-14；完成日期：2026-10-15（Asia/Shanghai）。保留用户指定的报告文件名。

本报告按用户后续指示，以**已经生成的结果**为分析主体，不排查已经解决的网络问题，不重新运行生成。本轮只新增报告，没有修改官方代码、包装层、配置、来源、规则、历史 runs、exports 或正式 SKILL.md，也没有调用付费模型或执行下游 Agent 实验。

## 1. 执行摘要与明确决策

**总决策：CONDITIONAL GO，限于保留原版基线和开展小范围机制验证；现在直接进行五案例全量退化效果实验为 NO-GO。** 当前证据足以提出改进方法的假设，尚不足以确认哪种改进有独立研究价值。优先完成一个可证伪的规则级机制验证，再决定方法开发；不先把官方管线全面修好。

必须先纠正研究对象：当前完成的五案是 qsv select、qsv sort、Docker cp、**git restore**、ripgrep。它们有 53 个 Draft、53 个 Spec、47 个正式 canonical Skill。历史 git reset 与旧 ripgrep 失败运行不等于当前案例；“五案只有三个完成”仅是旧批次结论，不能套到现行结果。

最严重的三个生成问题：

1. **Clean 规则已经在 Window 前端消失。** qsv sort 的核心参数交互规则仍在 Document，但没有进入实际窗口；因此对这些原文规则继续施加退化，不能直接测到一个有充分暴露的“正确 Clean → 退化后错误”过程。它们更适合研究前端证据丢失。
2. **条件、否定和输出契约在提取中发生语义偏移，并被保留到正式技能。** select 的排除分支与“输出匹配列”契约矛盾；Docker 的错误条件丢掉“源为文件”；restore 把 staged 的默认源写成覆盖显式 source；ripgrep 的部分技能错误描述替换会修改文件。这里既有输入缺失，也有正确证据已可见但仍被错误归纳，必须分开归因。
3. **Register 不能被当作可靠质量门。** 当前 47 个 CREATE 对应截断且非完整 JSON 的回复；6 个 DISCARD 有完整决策，但 restore 的两个 patch 候选互相指认重复而双双消失。结构有效的判断也可能在批次层面破坏能力覆盖。没有观察到跨文档历史技能合并。

另有一个独立的工程问题：现有 `results/exports/` 四个非 Case001 目录，每个目录11份、共44份JSON均复制了Case001内容。已在本报告中隔离，转而依据各run实际阶段JSON与正式技能分析。**网络不再列为当前阻塞，导出错配也不解释模型语义错误。**

| 案例 | 本轮决策 | 可进入的最小范围 | 当前不应进入的范围 |
|---|---|---|---|
| Case001 qsv select | CONDITIONAL GO，首选试点 | 枚举、末列的文本保留实例；区间为待独立判定候选；另设已错规则诊断层 | 把缺失的通用参数或已矛盾的正则契约当作正确 Clean 对照 |
| Case002 qsv sort | NO-GO，针对现有主要参数规则的增量退化实验 | 作为结构筛选丢失的诊断样本；或另行预定义前端方法对照 | 对已在 Clean Window 中缺失的 R1–R6 继续破坏并据零差异判定鲁棒 |
| Case003 Docker cp | CONDITIONAL GO，限定分支 | 本地符号链接及来源明确、窗口完整的复制分支 | 把两份技能视为完整 Docker cp 手册或完整执行流程 |
| Case004 git restore | CONDITIONAL GO，新案例独立计数 | 唯一 merge-base 等保留规则；默认源与显式源须先独立判分 | 使用历史 reset 产物评价 restore；把双 patch DISCARD 当作合并成功 |
| Case005 ripgrep | CONDITIONAL GO，仅限已审定的局部规则 | 字面量、临时类型等可独立判断的规则 | 整份教程一次性纳入；把正确和错误技能并存的规则合并判为通过 |
| 历史 Case004 git reset | STOP，缺原运行结果 | 历史记录说明 | 任何当前最终质量或退化效果评价 |

**基线策略：保留 B0；只把身份、日志和导出隔离等外部工程修复记为 B0+。修改 Window、Compile、注册解析/准入或候选选择，均须作为独立变体。** 本轮不实施任何版本。

**下一步唯一优先任务：冻结 Case001 的一个最小、独立的规则验证集及准入表。** 从 R1 枚举/区间与 R3 末列中选可确定判分的原子规则，核验来源、窗口暴露和有限任务 Oracle，明确相关/无关任务依赖。交付一个能判定后续实验是否有测量能力的验证单元；当前不批量退化、不扩数据、不开发三套方法。

## 2. 审计边界、工作树与证据等级

自动定位的实际Git工作树为 `D:/AS/AutoSkill-main`。审计开始时HEAD为 `d092a30d93a3fb746aeff3ea7c9baed949e0fca2`（提交时间2026-10-13T14:25:36+08:00）；交付时HEAD为 `ace65737e8d0be08eda1c47d5a8e62f119989ded`（提交时间2026-10-14T22:12:44+08:00）。本轮没有执行提交。聊天工作目录不是Git仓库。外层仓库内：

- `UP = D:/AS/AutoSkill-main/AutoSkill-main`：本地官方实现目录。
- `LAB = D:/AS/AutoSkill-main/degradation_failure_lab`：实验工程。
- 下文 `cases/`、`runs/`、`results/`、`data/`、`docs/research/` 均相对 LAB；代码引用显式写 `UP/`。

开始审计时已有改动：`results/run_index.jsonl`为modified；`docs/research/FIVE_CASE_CLEAN_SKILL_QUALITY_AUDIT.md`与`results/analysis/`未跟踪。交付时它们已由上述新提交纳入版本管理；两HEAD的diff只涉及这些15个文件，没有官方源码、包装代码或配置变更。报告按各文件的实际内容核查，不把是否已提交当作真实性证明，也不把它们误算为本轮产物。HEAD标识读到的仓库版本，**不是每次历史运行当时的Git HEAD**。五次运行保存的上游164文件指纹可与当前源码核对，但不能代替完整历史提交与工作树provenance。

| 标签 | 证据来源 | 可以支持什么 |
|---|---|---|
| [S] | 冻结原文、inputs 与 SHA-256 | 本地指定来源的文本规则与身份；不证明它等于论文原始数据快照 |
| [A] | 官方阶段 result、decisions、注册元数据 | 真实落盘的 Window/Draft/Spec/注册动作及关联 |
| [F] | canonical 正式 SKILL.md、可见树 | 最终交付文本、文件组织；不证明 Agent 实际会执行正确 |
| [H] | 已保存的模型请求/响应 | 被检查的模型输入与输出、finish_reason；本轮只为关键归因做必要复核，不排网络 |
| [C] | 当前实现代码 | 可定位的筛选、渲染、解析与应用逻辑；不自动证明所有历史运行都触发该分支 |
| [R] | 既有报告及 analysis CSV/JSON | 待核对线索与索引；未经重新核对的数字不升级为本轮观察 |
| [I] | 研究判断 | 准入、潜在下游影响、方法假设；不是已经测得的因果效果 |

确认级别使用 `CONFIRMED / PLAUSIBLE / UNKNOWN`。CONFIRMED 默认指来源与产物之间可直接证明的文本或工程事实；**不表示已经获得 CLI 执行反例**。缺来源支持、内部矛盾、运行时错误是三个不同判断。本轮没有任何下游执行成功率、显著性结果或阶段因果贡献率。

本轮全量阅读 47 份 canonical 技能；对代表性原子规则做源文—窗口—草稿—Spec—Final 追踪。既有报告的 156 个审核单元、129 个 CONFIRMED 错误记录等，不作为本轮独立全量原子审核计数，更不直接计算准确率。当前 `rules.json` 的 `annotation_status=analyst_checklist`、复合规则和部分单行锚点均不足以充当独立金标准。

## 3. 当前五案例真实状态

五案均为 `condition_id=clean`、`execution.exit_code=0`、`official_result.status=completed`、`errors=[]`。下面的数量由实际阶段数组和注册文件复算，不使用错配的 exports。它们可用于完整产物的定性质量评价；这不等于完成语义准入或下游任务验证。[A]

| case_id | run_id | Document / Section / Window | Extract Support / Draft / Spec | CREATE / DISCARD / Final | HTTP尝试/成功 | 已记录Token（prompt + completion） |
|---|---|---:|---:|---:|---:|---:|
| case001_qsv_select | raecd75e08b34 | 1 / 7 / 2 | 4 / 4 / 4 | 4 / 0 / 4 | 18 / 18 | 49,171 + 8,301 = 57,472 |
| case002_qsv_sort | rd9ced750fa54 | 1 / 6 / 1 | 3 / 3 / 3 | 3 / 0 / 3 | 13 / 10 | 24,846 + 5,039 = 29,885 |
| case003_docker_cp | rab9a070dfa59 | 1 / 6 / 1 | 2 / 2 / 2 | 2 / 0 / 2 | 9 / 8 | 24,081 + 4,898 = 28,979 |
| case004_git_restore | r18307cee4f4c | 1 / 8 / 10 | 17 / 17 / 17 | 14 / 3 / 14 | 67 / 67 | 166,690 + 30,984 = 197,674 |
| case005_ripgrep_guide | r64cee24fae18 | 1 / 16 / 12 | 27 / 27 / 27 | 24 / 3 / 24 | 96 / 96 | 270,547 + 54,389 = 324,936 |
| 合计 | 5次完成运行 | 5 / 43 / 26 | 53 / 53 / 53 | 47 / 6 / 47 | 203 / 199 | 535,335 + 103,611 = 638,946 |

定位：每案 `runs/<case_id>/clean/<run_id>/{invocation.json,execution.json,official_result.json,model_calls.json,config.json}`；计数字段为 `official_result.total_documents / total_windows / total_support_records / total_skill_drafts / total_skill_specs / upserted_count`，并与 `ingest/result.json.windows`、`extract/result.json.skill_drafts`、`compile/result.json.skill_specs`、`register/result.json.skill_specs` 交叉检查。`model_calls[].usage` 复算上述观测Token。未返回usage的请求是否收费及总金额仍UNKNOWN。

三个旧短案例中 C2/C3 各有3/1次未成功传输记录；它们已完成后续生成。本轮不继续诊断这些历史失败，也不拿请求失败数作为语义错误数。当前正式技能均为注册状态 `active`、版本 `0.1.0`；canonical根为各run的 `SkillBank/Users/docskill/`。具体程序文件见第5节及第11节索引。[A/F]

| 案例 | 固定源文相对LAB路径 | SHA-256（原文实体＝run输入＝input_manifest＝sources声明） |
|---|---|---|
| C1 | `data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md` | `74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384` |
| C2 | 同一qsv commit目录下 `sort.md` | `05bfbd4f41c7a4e55c3aeab71f5bbe8dd38659f4d00c5970c557df1f3feac693` |
| C3 | `data/raw_sources/docker/e4078058de0a9f4d5cb65f946f4b8a090e19fffe/container_cp.md` | `808ca152d4ea8bb4dbb12d31dcff15e9d3c958b85eaab4ccd4026cef1f14f764` |
| C4 | `data/raw_sources/git/a52a24e03c8c711f1d5e252fba78f9276908129b/git-restore.txt` | `2afb2f9183ad599a490c32fd174df66b0532abbe252887bc5c8b57d82a60f468` |
| C5 | `data/raw_sources/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/GUIDE.md` | `9dd96f163700ab5b41296cef3555b535c80c19e2ea25c7925c21b133d96d9537` |

这些是固定的重建官方来源，manifest标记 `RECONSTRUCTED_OFFICIAL_SOURCE`、`paper_snapshot_verified=false`。不能声称本轮验证了它们与论文数据快照完全相同。[S]

共同模型配置为 `deepseek-flash`、temperature=0、thinking disabled、stream=false、max_tokens=16384、timeout=180s、max_input_chars=100000；已保存请求/返回标签一致，但服务端权重版本UNKNOWN。共同生成设置包括 recommended extraction、LLM outline、每unit最多4候选、max_units_per_document=0、max_documents=1、workers=1、extract_retries=1、backoff=1s、chunk=6000、overlap=300、section=10000、retrieval_threshold=0.3、10 requests/60s、hashing embedding 256维。domain/domain_type/family_name随案例不同；不能称提示上下文完全相同。[A/H：每run/config.json与保存的请求字段。]

外部HTTP/Token上限依次为 C1–C3 `32 / 200000`、C4 `100 / 200000`、C5 `150 / 450000`。五案不是相同预算的横向性能对比。每run的10文件wrapper快照均匹配自己的manifest，但C5与C1–C4的 `adapter.py / provider_adapter.py / runner.py` 版本不同；当前包装层匹配C5。这个差异需记录，不扩展为网络排障。上游164个已记录文件则五run前后及当前哈希一致；未覆盖文件和历史完整Git状态仍UNKNOWN。

### 3.1 历史身份隔离

原任务列出的旧五次运行中，C1/C2/C3 与当前主样本相同；旧 `case004_git_reset/rfad98180a468`、`case005_ripgrep_guide/r8ac019d9b468` 的目录当前缺失。旧报告分别记 SSL EOF 与请求次数预算中止，但本轮不能把这种历史叙述称作原始日志重放。当前 `case004_git_restore/r18307cee4f4c` 和 `case005_ripgrep_guide/r64cee24fae18` 是不同的结果对象。

现存另一 ripgrep 运行 `r0c7bea4cc4ac` 为未完成记录；不能与成功主样本拼接草稿、共享 Token 分母或计为完整最终样本。用户已说明网络问题解决，本报告只保留完成/未完成的身份区分，不研究故障恢复。

### 3.2 当前导出身份检查

`results/exports/{r18307cee4f4c,r64cee24fae18,rab9a070dfa59,rd9ced750fa54}/verification.json` 的 `case_id` 均为 `case001_qsv_select`，`run_id` 均为 `raecd75e08b34`。各目录同名 `skill_files.json` 的 SHA-256 均为：

`c8c1745f3ee679ce71a63787c7a576c1e63cd1b235a5522e8cf641e07a095188`

每个目录11份、共44份文件的逐字节相同核查见第11节。这里的PASS只是Case001的副本，不能用来确认其它案例。错配发生时间、执行人和具体复制来源UNKNOWN；不能仅凭这一结果归罪于官方算法或断言导出函数必然有bug。[A/F：本轮文件读取与哈希；C：`LAB/src/degradation_lab/artifacts.py:167` 是导出入口，不是错误发生证明。]

因此本报告使用 `results/analysis/five_case_clean_audit/skill_inventory.csv` 作为路径索引，再直接核对其指向的实际阶段文件和 canonical 文件。隔离现有错误副本已经足以继续当前质量分析，无需重跑模型、重导出或修复代码。

## 4. 阶段链和完整性矩阵

```mermaid
flowchart LR
 S[冻结来源与输入快照] --> D[Document / Section]
 D --> W[Evidence Window 与标题元数据]
 W --> P[Plan 候选]
 P --> E[Expand]
 E --> DR[Skill Draft]
 DR --> SU[Support Record]
 SU --> CO[Document-level Compile]
 CO --> SP[Spec]
 SP --> RE[Registry-level Reconciliation]
 RE --> F[canonical SKILL.md]
 F --> V[Visible Skill Tree]
```

这是数据依赖链，不表示 Support 在独立模型阶段验证了 Draft。当前 Support 主要提供来源关联，不能替代逐断言语义支持证明。

| 案例 / run | Ingest/Window | Plan/Expand/Support | Compile | Register | Final/Visible | 能评价的范围 |
|---|---|---|---|---|---|---|
| C1 / raecd75e08b34 | 完成；2 W；参数表缺失 | 完成；4 D；有正则契约方向偏移 | 4 个一对一 Spec；错误保留 | 4 CREATE；有效根决策缺失 | 4 canonical；有导航/副本 | 完整文本质量，非任务成功 |
| C2 / rd9ced750fa54 | 完成；1 W；主要参数交互缺失 | 完成；3 D；外存范围收窄、校验能力无源扩展 | 3 个一对一 Spec | 3 CREATE；有效根决策缺失 | 3 canonical | 完整文本质量；参数退化主效应不可直接准入 |
| C3 / rab9a070dfa59 | 完成；1 W；核心嵌套分支保留，全局前提缺失 | 完成；2 D；文件源条件被概括掉 | 2 个一对一 Spec | 2 CREATE；有效根决策缺失 | 2 canonical，其中有知识参考 | 局部分支质量 |
| C4 restore / r18307cee4f4c | 完成；10 W；部分选项正文缺失 | 完成；17 D；显式 source/default 混淆 | 17 个一对一 Spec；无多草稿合并样本 | 14 CREATE + 3 DISCARD；patch 对双丢 | 14 canonical | 新 restore 质量，不能外推 reset |
| C5 / r64cee24fae18 | 完成；12 W；局部前提、例外缺失 | 完成；27 D；同主题有正确和矛盾结果 | 27 个一对一 Spec | 24 CREATE + 3 DISCARD | 24 canonical | 当前完整 run 的局部规则质量 |
| 旧 reset / rfad98180a468 | [R]称完成 Ingest | [R]称 Extract 中断；当前原件缺失 | UNKNOWN / 无可审原件 | UNKNOWN / 无可审原件 | 无可评价最终物 | 只保留历史背景 |
| 旧 rg / r8ac019d9b468 | [R]称完成 Ingest | [R]称保留20 Draft；当前原件缺失 | UNKNOWN / 无可审原件 | UNKNOWN / 无可审原件 | 无可评价最终物 | 不与新 rg 混合 |

### 4.1 Ingest / Window：丢失发生在哪里

五份 `Document.raw_text` 保留输入正文；问题集中在 Section→Window 的选择。`UP/AutoSkill4Doc/document/windowing.py:143–157` 按空行形成段，`:270–284` 保留带锚点/过程信号的段，或长度不超过 320 的普通段；`:114` 的 bullet 正则从整段开头匹配，不能因为段落后部有操作列表就认定会保留。长 Markdown 参数表可能因此整段被筛掉。稀疏回退 `:427–449` 仍用筛选后的 blocks，不会恢复已丢原文。[C；C1/C2 的实际缺失另由 A/S 确认。]

`build_windows_for_record` 默认 `max_chars=2400`（`:633–638`）；不能把生成配置的 `max_chars_per_chunk=6000` 当成这些窗口的实际上限。`UP/AutoSkill4Doc/ingest.py:1116–1121` 的调用需要与默认参数一起解释。规则筛除、窗口分组、outline 与 token 截断是不同机制，不以“窗口太短”笼统解释全部损失。

标题和 metadata 也属于证据暴露：正文没有某项操作说明，不等于模型完全看不到该主题；只有标题时，应标“有主题提示、缺行为条件”，不能标“完整规则已提供”。C1/C2 参数交互的缺失在正文和元数据两侧核对；C5错误替换候选正文只有搜索/过滤，而上下文标题提示了其它主题。字符覆盖仅作排查线索，不作为规则保真分数。

当前 C5 的 12 W 不是历史失败 run 的 23 W。旧报告关于失败 outline 后误识别代码注释的诊断，不能自动套用本次成功结果；如要归因于具体 outline 选择，需要本次记录，不能靠案例名相同推断。

### 4.2 Plan / Expand：最早可见偏移不等于模型内部原因

Plan 负责候选目标、粒度、资产类型和调用边界；Expand 把目标写为过程、约束和输出。候选有条目不等于保留了原子规则，知识参考也不应被强制当作完整操作流程。C1 正则方向冲突可以追到 Plan；Docker 的无条件 Caution 在 Draft/Expand 才出现；restore 的显式 source 例外在展开阶段被覆盖。第 5 节逐条给出证据。

对缺来源支持的限制，例如“只有内存放不下才允许 extsort”，判为来源范围被无依据收窄；不据此声称实际工具不支持某命令。对于正确 Window 内仍生成错误条件的案例，能排除“该条件完全未提供”这一局部解释，但不能据单次记录估计 LLM 的固有错误概率或因果贡献率。

### 4.3 Compile：本批只能评价一对一编译与渲染

53 个 Spec 的 `source_draft_ids` 均为单元素；没有真实多草稿合并样本。被追踪的语义错误未在 Compile 修复；不能写成“已经证明多草稿合并算法失败”。名称与描述更清楚、结构字段更齐全，与操作语义纠错是两回事。

`UP/AutoSkill4Doc/stages/compiler.py:126–139` 本地 renderer 固定输出 `Example Therapist Responses / Client / Therapist`，`:143–170` 拼接 prompt 与字段。因此最终领域不合适的标签可定位到渲染，不能一概解释为模型把 CLI 当成心理咨询。当前 39/47 正式文件含此标题；这是模板问题，尚无证据证明它是下游失败的主要原因。

### 4.4 Register / SkillBank：保存、准入和批次覆盖分开评价

`UP/AutoSkill4Doc/store/versioning.py:2403–2406` 先读取已有库并 refresh；`:2436–2453` 执行检索并传入批内 peers。五案开始时为空库，本批 `existing_hits=0` 不等于检索根本没有执行，也不等于同批候选互相不可见。此后先收集决策、再应用，不能将首次注册当作历史跨文档合并实验。

hits0 的输出预算固定为 256（`:68–75`）；根 JSON 解析失败时，`UP/autoskill/utils/json.py:23–78` 可取内部可解析片段；`UP/AutoSkill4Doc/core/llm_utils.py:167–170` 将非字典变成 `{}`；`versioning.py:1378–1384` 将非法 action 设为 CREATE，并回退原 Spec。被检查的 47 次 CREATE 是此链路，不能称有效准入通过，也不能反推它们本来都该被 DISCARD。

另外，compact 注册输入 `versioning.py:711–739` 不带完整 prompt、examples、output_contract；来源 excerpt 仅截前 180 字符（`:696`）。因此不能说注册模型已看到完整输出冲突而故意忽略。修复预算/解析、扩大可见证据、增加语义约束是不同干预，不能同时改完再把收益归为某一模块。

### 4.5 Final 与 Visible Tree

47 份 canonical 与47份可见子技能副本以及10份导航文件，共104个物理 SKILL.md。导航、family汇总与副本不增加独立程序技能数。直接计数 `register/result.json.skill_specs[].asset_type` 得到15 session_skill、18 micro_skill、12 knowledge_reference、1 macro_protocol、1 safety_rule，不能把47视为47个完整可执行流程。

最终文件保留 Spec 正文，证明持久化没有悄悄修正错误；版本/状态标识表示系统生命周期，不是外部语义认证。正确和错误技能并存时，读取整个库或动态路由可能遇到不同规则。可见树路径与标题只能支持组织可用性判断，实际检索命中、执行遵循和任务损害仍 UNKNOWN。

## 5. 代表性原子规则追踪

下表 `R1a/R1b` 等是本报告对现有复合检查项的分析拆分，**没有改写 rules.json**；`SUP-*` 是补充来源断言，不能伪装成原有规则 ID。对缺失规则不存在“关联到某个已经遗漏它的候选”的可靠 ID 时，明确写无映射。

### 5.1 路径与ID约定

路径前缀 `RUN1`—`RUN5` 分别为第3节五个 `runs/<case_id>/clean/<run_id>` 目录。`F1`—`F5` 为相应 `RUNn/SkillBank/Users/docskill`；`I1`—`I5` 为对应中间目录：

| 前缀 | `RUNn/SkillBank/.runtime/intermediate_runs/` 下目录 | Document ID |
|---|---|---|
| I1 | `20261011T153331_26f9a7a9` | `9c83d04d-0209-59d7-8e84-066c2d8161fe` |
| I2 | `20261011T222240_1c1d949c` | `e52fb956-42d7-5d59-b850-b7c9b757c5d9` |
| I3 | `20261011T222517_541bbc3a` | `f743e24b-67d6-533d-a213-19a964b22100` |
| I4 | `20261012T212141_eff933c6` | `6ff1f7e2-2ebb-58f5-9608-f2c0a8e4f0ba` |
| I5 | `20261013T155409_98c2c7bc` | `e4ff9b9e-5d4b-58b9-866f-add5974b54db` |

下表Source文件是第3节对应冻结源文；JSON Pointer用零基数组索引，HTTP号是 `RUNn/http/NNN/{request,response}.json`，模型文本需解码content。D/S的完整UUID映射见5.3；各条均只涉及该表指定run，不能跨run拼接。

### 5.2 规则—阶段—最终结果表

| 追踪项、case/run、原规则ID | Source Evidence → Actual Window | Plan → Expanded Draft → Compiled Spec | Final 与最早可观察问题 | 确认程度、缺证、潜在下游影响 |
|---|---|---|---|---|
| T01 C1/raecd75e08b34，R1a 枚举 | select:27–30，`1,4`为第一和第四列；I1/ingest/result.json:295保留原文，W=`245afa09…` | H002 slot1规划选择；D=`def5f116…`，extract:617–618明确例子；S=`f4c4df75…`，compile:792–793保留 | F1/csv-列选择与重排/SKILL.md:52、92–93正确；**无观察到错误** | CONFIRMED正确实例；未执行qsv。R1区间另为子项，不把这一正向证据扩展为全规则细节完整 |
| T02 C1/raecd75e08b34，R2b同名索引 | select:57–60明确`Foo[2]`是第三个同名列；同W正文保留 | D=`def5f116…`仅保留语法与“重复名称索引”；S仍未解释计数，extract:587/638、compile:724 | F1/csv-列选择与重排/SKILL.md:33、62仅有语法；最早可见为**Window→Draft的解释遗漏**，Plan未展开不等于不可逆丢失 | CONFIRMED partial，非命令写错；缺执行证据，可能影响同名列选择 |
| T03 C1/raecd75e08b34，R4a正则排除 | select:87–90是排除匹配列；W=`245afa09…`完整保留 | H002 `skills[1].success_artifact`仅写“输出匹配正则的列”；D=`0e55a3de…` output_contract（extract:740）；S=`bd72bc3b…`（compile:903）不变 | F1/正则表达式列选择/SKILL.md:34/58排除步骤正确，:80契约反向；最早**Plan**，一直传播到Final | CONFIRMED内部冲突；缺执行证据，可能影响敏感列排除及结果验收。不是整个技能所有步骤错误 |
| T04 C1/raecd75e08b34，R5b seed类型与R7a/b/c | select:163整数、:173–175输出/表头/单字符delimiter；I1/ingest/result.json:187/213的sections保留，两个Window正文和相关metadata不含这些约束 | H002 user内容也缺；R5候选仍有seed示例，但无类型；R7无可映射候选；不是强行给遗漏规则找一个“支持ID” | 四份Final均未补R7；F1/列排序与随机打乱/SKILL.md:50/56有seed但无整数；最早**Document→Window** | CONFIRMED遗漏；类型与三通用项须分开计分。可能影响无表头/分隔符/输出文件任务；未测影响 |
| T05 C2/rd9ced750fa54，R1–R6（以R1优先级为锚） | sort:41/43/44/52/56/66；I2/ingest:133/158/183仍有表；唯一W=`939e2088…`（:264）无主要交互/条件；R4仅剩random标签 | H002计划内存排序/外存/校验；D=`3e450260…`只列模式名，S=`353ba11e…`未恢复natural覆盖numeric等 | F2/csv-内存排序执行/SKILL.md:24/43/49只概括“指定方式”；其余两Final也不补；最早**Document→Window** | CONFIRMED核心条件缺失；不说random一词完全消失。缺工具执行；这些规则不准入E1退化主分析 |
| T06 C2/rd9ced750fa54，SUP-EXTSORT | sort:16–18只给“可能放不进内存时用extsort”的单向建议；W完整保留 | H002 `skills[1].do_not_use_when`新增可装内存应sort；D=`740004e0…`再加“仅在”，S=`cc5a002d…`保留 | F2/大文件外存排序切换/SKILL.md:42、59–64；最早**Plan范围收窄** | CONFIRMED来源未支持的限制；不是已证工具行为错误；可能误路由合法外存任务 |
| T07 C2/rd9ced750fa54，SUP-SORTCHECK | sort:3只有交叉引用，无校验接口；W保留名称 | H002 `skills[2]`由名称创建校验目标/通过失败契约；D=`542ae1df…`再补自然/数值/唯一/随机等范围，S=`7ab97840…`保留 | F2/排序结果校验/SKILL.md:27–32；**Plan无支持目标，Expand扩大能力范围** | CONFIRMED本来源支持不足；实际sortcheck接口UNKNOWN；潜在错误验收，不声称实测失败 |
| T08 C3/rab9a070dfa59，R5文件源条件 | container_cp:57–61只对文件源报错，:67–70允许目录源创建目标；I3/ingest `windows[0].text`，W=`770febe2…`完整 | H002 `skills[0]`无明确错误；D=`94ede446…` `cautions[0]`丢“文件源”；S=`0be52a4b…` `cautions[0]`不变 | F3/docker-cp-路径语义判定/SKILL.md:32–38分支正确，:86无条件报错；最早**Expand/Draft** | CONFIRMED同技能矛盾；已排除本Window缺前提的解释。可能误拒合法目录复制；运行后果未测 |
| T09 C3/rab9a070dfa59，R7本地symlink | container_cp:81–83默认链接本身、-L跟随；同W完整 | D=`d9e1ef03…`和S=`23370d93…`保留本地来源限定与两分支 | F3/docker-cp-符号链接复制策略选择/SKILL.md:30；**正确对照** | CONFIRMED文本忠实；未执行；适合限定范围准入而不是推断完整Docker流程正确 |
| T10 C4/r18307cee4f4c，R1的显式source例外 | git-restore:35–42含If not specified；I4/ingest `windows[4].text`，W=`0f0b837e…`完整 | H011 slots1/2区分显式/默认源；D=`c8f5869c…` `workflow_steps[1]`将staged直接→HEAD；S=`d472e6a7…`位于compile `skill_specs[5]` | F4/从指定-tree-恢复工作区文件/SKILL.md:27/58与:28/59冲突；最早**Expand/Draft** | CONFIRMED条件漂移；没运行restore；潜在恢复错误版本，不能用reset记录补证 |
| T11 C4/r18307cee4f4c，R4交互patch | git-restore:48–56；W=`0f0b837e…`与`7065d033…`都保留完整规则 | D=`bda7c828…`/`145d0db4…`，S=`4f818099…`/`eb09b547…`均保留；H054/H055完整DISCARD各称另一候选可替代 | 两份register/decisions均discard，Final无专门patch操作技能；语法参考仍有patch；最早**Register批次双丢** | CONFIRMED专门候选丢失；并非Compile合并失败或patch全部消失；实际Agent能否从残留重建UNKNOWN |
| T12 C5/r64cee24fae18，R3替换不改文件 | GUIDE:536–538明确never modify；Document保留，12个Window正文均缺这句显式否定；另一个替换窗口仍含输出替换语义；错误候选W=`4a5c4fa0…`仅搜索/过滤正文 | H007 `skills[3]`跨主题规划，有文件修改暗示；D=`3a0e9055…` `cautions[0]`明确可能改文件；S=`a4245429…` compile `skill_specs[7]`保留 | F5/ripgrep-替换与配置预处理流程/SKILL.md:66错误；其它两替换Final又正确；**显式否定句先未入Window，Draft首次明确相反断言** | CONFIRMED文本错误/跨技能冲突；不能把Plan暗示当完整断言，不能断言删句单独导致错误；未测任务风险 |
| T13 C5/r64cee24fae18，R4配置启用 | GUIDE:547–550要求环境变量；Document保留，所有Window正文缺RIPGREP_CONFIG_PATH；配置W=`70484645…`仅格式 | I5/extract `skill_drafts[18].examples[0].output`声称保存后生效；compile `skill_specs[19]`仍然如此，S=`556e78e5…` | F5/ripgrep-配置文件默认选项设置/SKILL.md:16/86/110；**Window前提遗漏＋Draft不充分保证** | CONFIRMED；缺实际环境测试。可能导致配置未启用而误以为已应用 |
| T14 C5/r64cee24fae18，SUP-ENCODING（旧审计X29，非原六项） | GUIDE:642–667具体ASCII/UTF-16 BOM边界；W=`fb0b641f…`止于行为列表冒号，下一W=`0bd66aa5…`才有细则 | H029 `skills[0]`已泛化自动推断且保证有匹配；D=`cf57ec96…`，S=`2c814928…`；另一个窗口生成了正确编码参考 | F5/ripgrep-自动编码处理/SKILL.md:24/42/49/65错误泛化；默认编码行为与漏匹配风险判断文件正确；最早**Plan** | CONFIRMED局部证据不足与跨技能冲突；不能说整份输入都缺编码知识，也不能证明模型内部具体推理原因 |
| T15 历史case004_git_reset/rfad98180a468，原规则ID UNKNOWN | 旧源/原run当前不可直接访问；现行restore的R1–R9不能借用 | [R]旧报告称W3展开中断；原始Plan/Draft不可重审 | 无可评价正式Final；**未完成历史例，不做语义成败归类** | UNKNOWN；缺原input/HTTP/stage/Final。只满足缺证边界说明，不计任何最终质量分母 |

T01/T09为正确保留，T04/T05为Ingest丢失，T03/T06/T14为Plan偏移，T08/T10为Expand错误，T03/T08/T10/T12为传播到正式技能，T15为未完成且缺证例。它们满足阶段覆盖，但不是随机抽样，也不支持错误频率或贡献率估计。

T12的正向旁证在 `I5/ingest/result.json#/windows/5/text`，Window ID `0cd51647-dd75-58c3-88af-08e530de2205`：仍说明修改输出及只替换输出中匹配部分。因此不能把整套窗口概括成“完全没有替换语义”，也不能从先后顺序推断删掉一句否定就是错误的充分原因。

### 5.3 关键实体映射与Support含义

| 追踪项 | Draft ID → Spec/正式skill ID | Extract Support ID |
|---|---|---|
| T01/T02 | `def5f116-bce7-54b1-afcd-cbfb3db8c337` → `f4c4df75-6ea6-5d4d-b30c-d7e825084300` | `819cec2f-0f64-5faa-baec-06919fde83af` |
| T03 | `0e55a3de-b1dc-50cf-93fb-2259c51f7403` → `bd72bc3b-8c84-59c2-9fd4-5caba1a5350b` | `76983d71-789e-5f48-b781-ff2ec59ba71b` |
| T04 seed技能 | `89f8089b-9739-5ad3-ae4e-f2298dd209c8` → `500c276a-5f59-5af9-86f5-4c0fbf4ad1be` | `df120f38-3d43-51b7-a677-74f37e20013f` |
| T05 | `3e450260-60ae-5f6e-9f31-b68874db4af9` → `353ba11e-1351-58c3-bb24-f91c7e24da8d` | `e3a9b88d-57eb-556f-b008-f905272777f7` |
| T06 | `740004e0-dbb4-5493-95b1-f06253756552` → `cc5a002d-6830-5192-b841-d8233e6ce4e3` | `3afebf9e-2810-5f4f-ac21-11e1a450191a` |
| T07 | `542ae1df-a500-5424-b9cf-f43c219fc254` → `7ab97840-0c8c-5685-88d2-36bdb1faefea` | `fc70e9a3-1dcd-5a3f-aebb-9f7a9f0dfb78` |
| T08 | `94ede446-63eb-59cd-8484-f6be4a4e6055` → `0be52a4b-b68d-5166-a0c1-668834d1f64a` | `49d718ba-5350-5ed1-9b11-565cd8657fbd` |
| T09 | `d9e1ef03-59a6-5d0c-a0fd-bfddb5ca00d7` → `23370d93-9d3f-5142-bfed-e6ff22cb9b36` | `baeb1e83-f43b-50f7-a46d-a0c734012431` |
| T10 | `c8f5869c-7a3e-56d5-b5a9-7dbac725b3e4` → `d472e6a7-8895-56cb-9014-cb75cc3540b3` | `2da7e481-6e59-5046-94c7-4fd7d9142474` |
| T11-A | `bda7c828-2661-5fbe-931c-5332efc2022c` → `4f818099-0f3d-5f99-83e5-df551a9bf486`（未注册） | `74e3a6cb-13a1-531b-a2d2-99fb901ca1b6` |
| T11-B | `145d0db4-219a-5331-8de0-1e0f2614aa5f` → `eb09b547-e592-5aab-9788-a88cbf862adb`（未注册） | `12e19787-59a2-53fd-a9a2-0ebe62acec09` |
| T12 | `3a0e9055-0af5-570d-8653-24963ff63c9a` → `a4245429-7e5f-5215-b208-20f621b76667` | `9a7e358c-0a14-50a6-abab-32dfc6a5d1d2` |
| T13 | `5366f3c0-cc42-5928-8b47-6f75d9b7bc73` → `556e78e5-fde6-567c-a379-e2b65df28a06` | `e945be3f-8a59-508d-8056-edebb41ebe70` |
| T14 | `cf57ec96-dbbb-5e6a-983e-0c10befa56f3` → `2c814928-5d5a-5b76-b753-698a489a180e` | `85232dc1-72f6-51ec-8fb2-bff9ce702df7` |

本轮逐项比较53条Extract Support的excerpt与各Draft关联Window正文，53/53逐字相等，每Draft只关联一个Support。这确认**整窗证据关联**，不确认窗内每句话支持Draft的每个断言。T08是尤其明确的反例：同一窗正确包含文件源前提，Support仍能关联那个删掉前提的Caution。模型confidence及relation标签未有独立校准，不能把它们当真值概率。

### 5.4 全量Final阅读后的案例补充

除代表链之外，C1的引用技能还把“冲突时需引用”加强为“仅冲突时引用”（F1/引用冲突列名进行-qsv-select/SKILL.md:56）；其shell转义变化的行为等价性UNKNOWN。C2三份技能虽可读，但均未补足参数组合，不能仅靠技能名覆盖判定可执行性。

C3目录`/.`与本地symlink分支有正确保留；不创建父目录、所有权、容器运行/停止等全局前提未进入唯一窗口。知识参考型路径说明不承担完整复制命令流程，但其中的无条件错误仍应判为错误。

C4的默认源、恢复位置、唯一merge-base、部分显式source实例与强制progress有正确内容；ours/theirs将未合并状态收窄为有冲突标记、quiet绝对无进度与另一progress技能冲突。后两项本轮读到Final，未逐项追溯最早阶段，故不新增“Plan必然导致”的归因。source/目标相近技能的职责有重叠也有差别，不能全部按名称相似判冗余。

C5的-F、临时type-add、部分glob优先级、二进制模式及详细编码参考有正确内容。其它Final风险包括-o作用域表达、none与BOM例外合并、合法零匹配不被输出契约接受、单文件边界与递归示例冲突、预处理缺具体接口。本轮不将这些阅读发现全部升级为已独立追踪的首发阶段。尤其T12/T14同时存在正确技能，整库质量应记mixed，不能用正确条目抵消错误条目或反过来全盘判错。

## 6. 工程故障、原生缺陷与研究机制

| 问题 | 分类与证据强度 | 处理决定 | 不应作出的推论 |
|---|---|---|---|
| 四个目录导出内容错配 C1 | A 基础设施；CONFIRMED 文件身份/哈希 | MUST_FIX：评价入口必须隔离，或未来在新目录正确导出；本轮已用实际结果绕开 | 不推断是谁复制，也不归罪于生成模型 |
| 旧 reset/rg 原始目录缺失 | A provenance；CONFIRMED 当前不存在 | STOP 这些历史 run 的直接最终质量评价；保留旧报告标签 | 不用恢复后的新案例替代旧原件 |
| 网络中断 | A 历史基础设施；用户说明已解决 | DEFER，不再排查，不作为当前五案质量解释 | 不把历史失败计入当前语义错误率 |
| 每案例不同调用预算、模型服务版本未固定 | A 实验设计/复现 | MUST_FIX 未来同来源、各条件/方法的预算与身份冻结；记录服务标签局限 | 不能以相同模型名声称权重固定；不能比较原始总Token判方法效率 |
| 参数表/前提/例外筛除 | B 原生Window行为；局部CONFIRMED | KEEP_BASELINE；修改筛选或结构解析为 SEPARATE_VARIANT | 不是人为文档退化，也不证明所有表格都丢失 |
| 可见规则仍条件误读、否定与契约冲突 | B 提取语义；局部CONFIRMED | KEEP_BASELINE；可成为方法研究对象 | 不宣称实际Agent已失败 |
| Support引用整窗、confidence未经校准 | B 证据表示限制；CONFIRMED结构 | KEEP_BASELINE；逐断言证据/一致性为候选变体 | support_count或conflict=0不等于语义正确 |
| 一对一编译未修复错误 | B 当前观察；CONFIRMED传播 | KEEP_BASELINE；新编译约束为 SEPARATE_VARIANT | 不声称多Draft合并失败 |
| 截断解析后默认CREATE | B 官方实现健壮性缺陷；CONFIRMED | KEEP_BASELINE作为原版行为；严格解析/预算修订为 SEPARATE_VARIANT | 不把改后版本叫完全原版；不将47份技能一律视为语义错误 |
| patch候选互相DISCARD | B 批次准入一致性缺陷；CONFIRMED本批 | KEEP_BASELINE；联合选择为 SEPARATE_VARIANT | 不是跨文档MERGE失败；不是所有patch痕迹消失 |
| therapist模板残留 | B renderer缺陷；CONFIRMED代码与Final | DEFER；如改则单独标记版本，不作方法创新主体 | 不先断言其造成工具风险 |
| Schema PASS替代语义评价、规则分母未独立冻结 | A 评价有效性问题；CONFIRMED当前代码边界 | MUST_FIX 评价协议，不修改生成产物 | 不把旧审计计数当人类gold或任务成功率 |
| 转义在指定shell中的行为、sortcheck接口能力、最终检索损害 | 未证实 | DEFER / UNKNOWN，按需用独立环境核验 | 不把来源不支持写成已实测错误 |

最值得研究的三个机制依次是：

1. **证据暴露与条件绑定丢失。** 可干预变量为表格展平、标题/正文断开、条件与动作距离；先固定文本语义和信息量，记录哪些原子关系进入 Window。独立真值来自固定源文及人工审核，不从生成技能倒推。
2. **条件—动作—输出在跨阶段转换中失配。** Docker 文件源条件、select 正则包含/排除、restore 显式与默认源是具体反例。控制来源、窗口和模型预算，可比较同一信息在自由字段与受约束表示下的保真；语义错误是否影响任务需额外 Oracle。
3. **错误/缺口冻结为可复用资产并影响多个任务。** 当前只看到错误进入正式文件，以及批次去重后专门能力消失；尚未看到实际多任务传播。必须固定一个技能版本、两个依赖任务和一个不依赖任务，并用局部干预区分共同失败与规则传播。不能仅凭两次失败共现宣称传播因果。

注册JSON健壮性是必要的实现诊断，但单独提高Token或严格解析不构成有说服力的方法创新。批次联合覆盖选择可能是后续子问题，当前不再另开第四条方法路线。

## 7. 当 Clean 已不可靠时，什么仍可研究

令 `W(D)` 为实际窗口加上模型可见元数据。若原子规则 r 在 Clean 的 `W(D)` 中没有足够证据，且局部退化后 `W(D')=W(D)`，则生成器没有接收到该项干预的差异。此时不能把技能无变化解释为 r 的鲁棒性；也不能从已有错误推断退化贡献。[I，信息暴露条件判断。]

但这不意味着任何文档级总效应都不可估计：退化若改变切分、标题或窗口组合，仍可影响其它证据；那估计的是前端中介的整体效应，不能命名为“仅该规则语义损坏的效果”。源文真实不可恢复的唯一条件删除也不能要求模型凭空恢复；应评估识别不确定、限制适用范围和拒绝错误操作。

**预先定义三层样本，不事后删掉难例：**

- `E1：Clean充分暴露且规则正确`，用于增量退化损害的主分析。C1枚举/末列、C3局部symlink可候选；仍须独立审核。
- `E2：Clean充分暴露但技能错误`，用于条件误读与方法纠错，不要求出现进一步下降；C1正则、C3文件源条件等属于此层。
- `E3：Clean未充分暴露`，用于窗口保真与信息可达性诊断；C2主要参数、C5配置启用可候选。不要拿它与E1混合后宣称退化无害。

准入依据在退化和方法比较之前固定。不能按退化后是否完成、是否保留规则、或改进方法是否成功来选择样本。对方法端到端比较应保留共同来源总体，并按这三层分别报告；不能让每种方法自行选择对自己有利的规则分母。

E1准入应在独立开发记录上确定；正式比较的Clean与degraded均按预先固定的重复生成协议取样，不以用于筛选的单次成功Clean输出充当唯一对照，以免混入生成随机性与回归均值。若只研究当前冻结资产，结论限定为该资产的条件性案例效应，不外推生成器平均退化效应。

排除主效应层的条件包括：来源身份不明；规则无独立真值；原文歧义未解决；Clean未暴露目标规则；历史原件缺失；最终入口不确定；无下游判分基础。排除理由必须先登记。生成失败和无技能结果仍属于方法产出，应按预先政策报告可用率及条件性质量；不能只对成功技能算分后隐藏失败。

替代方案：缩小至已暴露规则；把前端缺失作为独立研究层；或使用结构保留前端作为明确标记的变体。三者分别改变研究范围、分析层和算法条件，不可混称为“修复了原版后继续同一实验”。

## 8. 基线版本决策

| 版本 | 定义 | 当前决策 |
|---|---|---|
| B0 | 固定本地原版源码指纹、来源、模型请求配置、窗口/编译/注册行为；保留真实缺陷 | 必须保留。当前结果可作探索性原版基线，不能称质量合格或与论文设置完全一致 |
| B0+ | 仅外部实验工程：正确身份映射、不可混用导出、阶段计数、原始响应保存、可复现环境记录；不改变模型可见内容/有效回答选择/生成算法 | 可建立，当前不实施。若只是评价侧隔离文件，甚至不需要重新生成 |
| B1及其它变体 | Window结构处理、Compile约束、Register严格解析/重试/预算、候选联合选择、renderer改动等会改变最终提示或输出行为的修改 | 必须单独命名、记录patch和成本，与B0并列；不可静默归入“纯工程修复” |

这里的B0首先指**本地Anything2Skill实现快照**。当前164文件一致性证明的是本地运行间未变，外层HEAD也是用户实验仓库的身份；本轮没有独立核到嵌套实现对应的官方发布commit。正式论文应补充上游commit或发布归档哈希及差异清单，否则使用 `B0(local snapshot)` 的准确名称，不宣称精确复现了论文发布版本。补充身份记录不需要修算法。

网络恢复或可靠传输可作为运行环境条件，但语义相关重试、换模型、提高注册输出预算、从多次回答择优都改变生成分布；即使称“bug fix”，也应单独记录实验条件。不同 run 的包装层和预算已有变化，当前不允许直接把它们当作严格同配置重复。

原版与改进版可比较的前提：同一冻结来源及退化字节、相同允许证据、同等总预算、同一执行器与评价协议；B0与变体分别留存输出，不覆盖旧run；预注册失败/缺失处理与入口选择；生成重复与下游重复分开。多个任务共享一个冻结Skill时，以生成run作为聚类单位，47个技能不是47个独立文档样本。

防止事后改基线：看结果前冻结版本和参数；新增修改必须新版本；保留全部失败与成本；任何根据Clean诊断作的选择都公开为开发集决策，再用未见来源验证。当前五来源（其中qsv两份同工具）足够找机制，不足以支撑跨领域总体结论。

## 9. 方向 A 与方向 B 的取舍

| 维度 | A：退化风险与错误传播 | B：低质量文档到可靠技能的方法 |
|---|---|---|
| 当前证据 | 已看到Clean缺失/矛盾与持久化；没有退化干预和任务传播 | 已有可定位反例，足以提出机制假设；没有收益、泛化和消融 |
| 关键问题 | 退化相对Clean造成多少额外损害，技能是否改变/放大损害 | 在相同可用证据与预算下，如何减少丢规则和条件失配 |
| 主要混杂 | Clean地板效应、窗口暴露不同、生成随机性、入口与证据泄漏 | 额外文档/Token/验证反馈、复杂方法只比弱prompt、过拟合五文档 |
| 必要对照 | 若主张相对直接读文档的损害：DirectDoc/FrozenSkill必须有 | 方法主比较为B0/轻量前端/受约束变体；DirectDoc不是每个组件实验的必需项 |
| 创新风险 | 只报告“坏技能会出错”已有直接近邻；需有受控文档退化与冻结传播机制 | 证据准入、程序IR、反馈修复、RL编辑已有近邻；需证明特定机制贡献 |
| 本次选择 | **先做一个有限机制验证**，不把它扩为全套风险基准工程 | 先书面提出可证伪假设，不开始实现；通过最小验证后选一个方法 |

### 9.1 DirectDoc / FrozenSkill 到底何时必要

只证明“Window丢了一条规则”“最终Skill与源文冲突”，不需要双路径。若研究问题包含“相对直接读文档是否损害更大/不同”，就必须同时测 `DirectDoc(clean/degraded)` 与 `FrozenSkill(clean/degraded)`，比较两条路径各自相对Clean的变化，不能只比较两种Clean的绝对表现。

DirectDoc读取该条件的完整源文，FrozenSkill只能读取预先冻结的技能入口。若把 `references/evidence.md` 或 evidence manifest 的整窗quote一并开放，就变成Skill+源证据混合条件；应单独命名。Anything2Skill论文采用Skill与RAG结合，因此纯FrozenSkill实验是本研究为隔离机制定义的部署模式，不能冒充原论文完整推理系统复现。[论文§3.3及推理描述](https://arxiv.org/html/2606.09316v1)。

只有双路径仍不能证明冻结错误传播：还需在新研究副本上局部修复/破坏同一规则、同格式sham对照，以及依赖/非依赖任务的响应差异；这些均是未来设计，本轮未实施。

### 9.2 相关工作核对与新颖性边界

- **SkillAlchemy**：通过对比证据发现隐含要求，以支持范围将过程归为General/Scoped/Exclude，再依语法编译；这已覆盖“来源支持＋范围准入”的基本思想。单加检查器或证据分数不能作为新意。依据论文§3.3–3.5及作者实现说明：[论文](https://arxiv.org/html/2608.23417v1)、[TECHNICAL.md](https://github.com/agentsope/SkillAlchemy/blob/master/TECHNICAL.md)。
- **Skill-α**：将生成表示为渐进编辑，以固定worker在同一锚定query下的编辑前后反馈训练策略；本研究若引入执行奖励或局部编辑，不能声称首次。其执行收益不自动等于源文规则忠实。依据§4与训练/消融说明：[论文](https://arxiv.org/html/2608.01678v1)。
- **Workflow-to-Skill / text2flow** 已研究程序结构、中间表示、语义对齐及修订。新意不能停留在“加图、加条件字段、让多个Agent检查”。[W2S](https://arxiv.org/abs/2606.06893)、[text2flow正式论文](https://aclanthology.org/2026.findings-eacl.158/)。
- 已有技能诱发失败的差分分析，因此方向A需要退化暴露和冻结依赖链上的额外证据。[Agent Skills Can Be Harmful](https://arxiv.org/abs/2608.11888)。这些检索是近邻核查，不是穷尽检索或新颖性认证。

### 9.3 至多三个方法假设

下面是研究候选，**不是三项开发任务**。目前优先级为 M2 > M1 > M3；选择以最小验证结果为准。

#### M1：在预算内保留条件依赖闭包的证据选择

1. **真实失败链**：sort参数表、Docker全局前提、ripgrep配置启用段从Document到Window丢失，后续缺乏完整规则。
2. **输入/表示/输出**：只输入同一受损文档；表示为来源跨度、标题/表格行/代码块、条件—动作依赖及unknown字段；选择一个动作时同时分配其前提和例外的预算，输出带来源映射的窗口包。依赖识别不保证正确，不能以gold关系作测试时输入。
3. **区别于Anything2Skill**：检验显式依赖闭包能否优于固定锚点和段长筛选；不是简单放大窗口或取消长度限制。
4. **区别于SkillAlchemy**：限定同一受损源、固定上下文预算，不通过开放检索获取新证据；关注暴露过程的依赖完整性，而非支持范围准入本身。
5. **区别于Skill-α**：不学习全文技能编辑或依赖worker奖励，先控制前端证据选择。
6. **监督/反馈**：开发集需人工条件—动作关系；测试gold只作评价。可选轻量关系分类器的训练数据单列，不能免费使用测试Clean文档。
7. **轻量基线**：Markdown/AsciiDoc保结构切分、固定滑窗、完整短文、表格转键值、同Token的标题邻接扩展。
8. **消融**：去闭包、去例外绑定、随机等长邻接、固定相同Token；分别测试布局扰动和真正信息删除。
9. **超越prompt的必要条件**：有可重复的依赖选择算法与预算分配；若只是提示“不要丢条件”，不足以成立。
10. **否定标准**：简单保结构切分达到相同收益；同预算收益消失；只在这五份文档有效；或恢复缺失仅靠额外Clean信息。出现这些结果应降为工程基线，不包装成方法论文。

#### M2：保持分支作用域的条件—动作—输出编译

1. **真实失败链**：select排除步骤与统一输出契约冲突；Docker文件源条件在Caution泛化；restore默认源覆盖显式source。均有可定位的字段间语义失配。
2. **输入/表示/输出**：同一可见受损证据与候选Draft；中间表示包含适用谓词、动作、否定/优先级、输出谓词、来源跨度和未知项。编译器从同一分支表示生成步骤/限制/输出，检查可判定子集中的矛盾并输出受限Skill或保留不确定性。自然语言到表示的正确性仍需单独测量。
3. **区别于Anything2Skill**：现有独立字符串字段能同时容纳相反断言；假设是共享分支语义及受约束编译减少字段漂移，不是再换一个自由文本审稿prompt。
4. **区别于SkillAlchemy**：不只问每个候选是否有支持，还要求被准入的条件在多个生成字段和版本中不被丢失；证据准入本身作为强对照。
5. **区别于Skill-α**：使用可检查的局部语义约束，而非通过下游奖励学习任意编辑；如后来训练解析器，应另计监督，不借其RL概念改名。
6. **监督/反馈**：开发集人工分支/作用域标注；测试时只读允许输入。真实工具反馈是可选独立实验臂，不与纯文档路线混合。
7. **轻量基线**：同模型自检prompt、层次JSON保留原条件、静态字段一致性检查、原文引用式Skill、简单规则分支模板。
8. **消融**：去作用域、去输出约束、去来源锚点；固定结构只换自由renderer；固定抽取结果只测试编译，以分离抽取与编译收益。
9. **超越prompt的必要条件**：有类型/作用域约束、明确的变换规则与失败状态，并能在可判定子集内检查保持性质。增加字段或checker本身不算新算法。
10. **否定标准**：自检/层次JSON同样好；受约束输出靠删掉难规则抬高准确率；保真改善却可用覆盖/下游成功下降；主要错误来自初始语义解析且编译约束无增益。应按共同来源分母和coverage-risk同时报告。

#### M3：证据不充分时保留竞争解释并限制可执行范围

1. **真实失败链**：ripgrep配置缺启用前提、auto被泛化、sortcheck只出现名称却被补出多模式校验能力。单一猜测被写成确定操作。
2. **输入/表示/输出**：受损源与存在歧义的规则单元；建立有限候选解释集合和各自证据/冲突，只有候选共同支持的动作进入可执行部分，分歧保留unknown或局部拒绝。候选集合覆盖不保证穷尽，禁止据此宣称形式安全。
3. **区别于Anything2Skill**：从单Draft及未校准confidence转为显式竞争解释与动作分歧；不得把多个温度采样的一致意见当独立证据。
4. **区别于SkillAlchemy**：其范围准入已处理不足/冲突；本候选只有在竞争解释的行为分歧带来额外可测收益时才有区别。“证据不足拒绝”本身不新。
5. **区别于Skill-α**：不依赖学习型局部编辑奖励；若需要执行探针区分候选，反馈预算必须单列且给基线同样机会。
6. **监督/反馈**：需要独立歧义/可恢复性标注及开发集阈值；可选执行探针不得读测试答案。完全删除唯一依据时，正确目标是unknown而不是恢复真值。
7. **轻量基线**：证据充分性分类＋阈值拒绝、SkillAlchemy式Scoped/Exclude、单候选保守模板、同预算多样本投票。
8. **消融**：单候选、无行为分歧、无范围限制、匹配拒绝率；评价正确覆盖和错误风险曲线，而非仅对接受项算准确率。
9. **超越prompt的必要条件**：明确候选构造/比较及选择性输出规则，验证它优于简单拒绝与投票；多Agent讨论不是创新证明。
10. **否定标准**：收益全由更高拒绝率或更多Token造成；候选漏掉正确解释；在信息保留条件下也频繁拒绝；简单准入机制等效。届时停止该路线。

## 10. 唯一优先任务、停止规则与未解决问题

**唯一优先任务仍是：Case001最小规则验证集与准入表。** 它应给出事前冻结的原子规则、完整源锚点、Clean窗口暴露、正式技能是否忠实、依赖任务/非依赖任务、确定性期望输出与失败判据。R1的枚举/区间可拆分，R3可作不依赖的对照；具体题目和执行环境在下一轮决定。本轮不生成fixtures、不安装qsv、不写Oracle、不施加退化。

这一步直接决定后续走向：若能验证受损输入改变规则并影响依赖任务，继续方向A的最小双路径机制试点，再据瓶颈选择M2或M1；若任务根本不依赖文档/技能、Clean暴露不足或真值含糊，则缩小/替换规则，不通过修补所有基线缺陷维持原方案。

停止规则：

1. 无法确认case/run/source/final身份：停止该样本质量评价；不用错误exports或相邻case补证。
2. 目标规则在Clean已未暴露：停止其E1增量退化主分析；转E3或另选事前准入规则。
3. 无独立真值/Oracle或来源歧义：只作定性结果，不报任务成功率。
4. 无法匹配证据与预算：不将差异归于方法；若给额外文档/工具反馈，单独实验条件。
5. 只有Schema/文件/生命周期状态，没有语义或执行证据：不宣布任务成功。
6. 改进只优于弱prompt、只改善被挑中的规则、或收益由拒绝/额外信息解释：否定或降级方法创新主张。
7. 本报告交付即停止，不自动修代码、补跑Clean、调用API或进入算法实施。

仍UNKNOWN：模型服务端固定权重版本；完整历史运行Git身份；导出错配操作历史；缺失run的原始细节；指定shell下的引用等价；具体工具版本下的任务行为；实际技能检索/路由与执行损害；受控退化效应、重复方差、跨文档合并效果，以及新方法在未见来源上的收益。

## 11. 旧结论复核、证据索引与只读性

### 11.1 必检历史报告：哪些确认、哪些已过时

| 既有文件（均在LAB/docs/research） | 本轮处理与结论 |
|---|---|
| `CLEAN_MULTI_CASE_GENERATION_AUDIT.md`，§3/§4/§7 | 旧三完成/两失败属于原run集合；当前另有restore/rg完成结果。旧九次注册截断在同三run直接复核成立，现行五run扩为47次回退CREATE。旧错配线索在当前四目录逐文件复核仍成立 |
| `CLEAN_MULTI_CASE_RULE_TRACE.md`，§3–§7/§9 | C1–C3代表规则从实际Source/阶段/Final重新核；§6是reset、§7是旧rg，不能用它们评价当前restore/新rg。报告:9明确其旧rg是r8ac019d9b468 |
| `CASE001_GENERATION_AUDIT.md:7–11`、§4/§5 | R7窗口缺失、正则契约冲突、H012–015截断由同run直接重核；工程PASS不是语义通过的边界仍成立 |
| `NEXT_STAGE_READINESS_DECISION.md`，§2/§3/§6 | 双路径、独立Oracle及冻结入口是历史设计建议，不是已完成实验。本轮直接读evaluation.py，只见人工记录/Schema与关联校验，未据旧环境检查宣布当前qsv必然不存在 |
| `CASE004_SOURCE_REPLACEMENT_2026-10-12.md:3–5` | 新restore来源commit/hash与当前源/run匹配。该报告当时称旧runs未动，但当前旧reset目录已不存在；状态以本轮文件系统为准，不推测何时删除 |
| `CASE004_GIT_RESET_SSL_FAILURE_AND_RECOVERY_AUDIT.md:10–13` | 当时第二次ra960b6759d7c有3 Draft、H8 Plan失败，第一次rfad已删除；当前两目录都缺失。上述失败细节只标[R]，不当作本轮直接证据，且用户已说明网络解决 |
| 另检 `FIVE_CASE_CLEAN_SKILL_QUALITY_AUDIT.md` 与 `results/analysis/five_case_clean_audit/` | 当前五完成、53→53→47、代表错误及文件路径作为线索，关键计数和规则经本轮直接核。旧156规则单元及汇总错误数未在本轮独立全量重标，不据其给准确率 |

**对原任务五条历史发现的最终裁定**：仅三个正式注册——历史集合成立、当前集合不成立；Git SSL EOF——当前原件不可审、仅历史报告；旧rg预算停止——当前旧原件不可审，不影响新run完成；九次Register截断——原三run直接确认，当前扩大为47；跨案例导出错配——当前直接确认44个错配JSON，未修复或覆盖。

### 11.2 当前Register的可定位响应集合

每项都读取保存的request、response和decision，并以candidate skill ID对应；只是离线解析，没有调用服务。`create`组均为max_tokens=256、completion finish_reason=length、严格根JSON无效、官方纯解析返回`[]`；`discard`组均为完整JSON、finish_reason=stop。报告把“模型原文开头也写create”和“程序最后是解析回退create”同时保留。

| case / run | CREATE响应HTTP序号 | 完整DISCARD响应HTTP序号 |
|---|---|---|
| C1 / raecd75e08b34 | 012–015 | 无 |
| C2 / rd9ced750fa54 | 011–013 | 无 |
| C3 / rab9a070dfa59 | 007、009 | 无 |
| C4 / r18307cee4f4c | 046–053、056–061 | 054、055、062 |
| C5 / r64cee24fae18 | 068–069、071–079、081–084、086–094 | 070、080、085 |

完整文件为 `RUNn/http/NNN/request.json` 的 `max_tokens`及user候选、`response.json` 的 `choices[0].finish_reason / choices[0].message.content`，和 `In/register/decisions/<skill_id>.json`。例如 C1 H012 对应 `f4c4df75-6ea6-5d4d-b30c-d7e825084300.json`。当前CSV `register_decision_audit.csv` 可作53条路径目录，但有效性判断来自其指向的原文件重新读取。

C4第三个DISCARD是 `039a48d6-70fe-5e3c-907c-4903bf7d77f0`（联合恢复目标），不能等同patch双丢；已有其它联合恢复技能。C5三个DISCARD针对手动过滤/glob/整行替换候选，不是文件随机遗失。没有MERGE、REVISE、STRENGTHEN等有效历史库变更样本，不能评价这些能力。

### 11.3 本轮直接核查清单与复现定位

- 当前Git根、起止HEAD与开始时status：第2节；只读Git调用，未checkout/reset/commit；交付时status只新增本报告。
- 五源与各run输入、source/input manifests的SHA：第3节。原始文件存在，五输入一致；历史缺失对象单列。
- 5个Document、43个Section、26个Window、53 Draft/Support/Spec、47 Final计数：第3节字段与第5节中间目录。
- 53 Spec的 `metadata.source_draft_ids` 均单元素且唯一覆盖53 Draft；`compile/documents/<doc_id>.json.group_count` 为4/3/2/17/27。Extract与Compile内Draft按ID对齐内容未变，数组顺序不作语义变化。
- 53个Extract Support整窗excerpt比较、关键来源锚点与代表规则链：第5节；没有把引用关系当逐句蕴含。
- 47份canonical完整阅读；47份 `## Prompt` 执行正文逐字等于对应Spec.skill_body。**整份SKILL.md并不等于Spec**，另含YAML与包装；渲染代码 `UP/autoskill/management/formats/agent_skill.py:140–173`。
- 39份therapist标题由实际文件内容复计；其它导航文件不计入此分母。代码来源见§4.3。
- 44个错配导出：对四个非C1目录中的 `documents.json / registration.json / skill_drafts.json / skill_files.json / skill_specs.json / support_records.json / text_units.json / traceability.json / verification.json / window_source_alignment.json / windows.json`，每案11/11与C1同名字节相等。
- `LAB/src/degradation_lab/evaluation.py:10–50` 检验schema、ID、来源/关联与行号；`:54–69` 初始化人工待审；不是自动CLI Oracle。没有据此宣称下游测试已完成。
- 164个已记录上游文件：每run `upstream_before.json / upstream_after.json` 与当前实体一致；各run自己的10文件wrapper_snapshot匹配wrapper_manifest，但历史/当前包装版本差异已在第3节公开。

只读性检查以工具动作边界、历史指纹和交付前Git状态复核为依据；本轮唯一新增仓库文件为本报告。对既有未跟踪analysis文件不执行重新生成，不修改旧CSV。不存在本轮新增模型账单、Skill生成结果、退化输入或下游任务产物。

方法说明：本轮应用 scientific-critical-thinking 的证据分级、混杂与可证伪性审查原则。方法库参考为 Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*，核对 arXiv 当前条目为v2；该库不是本任务性能证据。[参考](https://doi.org/10.48550/arXiv.2609.00065)。

**停止声明：本轮只完成结果审计和研究决策；没有声称执行过退化、改进算法或下游Agent实验。**
