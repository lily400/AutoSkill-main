# Case001 生成结果审计（Stage 1）

审计日期：2026-10-11。运行：`raecd75e08b34`。性质：Codex 基于本地实际材料的初步语义分析，**不是独立人工金标准审核，也不是下游任务成功率实验**。

## 1. 结论与边界

工程结果为 PASS，24 项检查在本轮无模型、无导出写入的复核中仍全部通过；实际为 1 Document、2 Window、4 SupportRecord、4 SkillDraft、4 SkillSpec、4 注册技能。但存在三个不能由 PASS 排除的问题：

1. 原文完整保存在输入与 Document 中，窗口规划却丢弃了一个描述段落和三个参数/选项表块。R7 的信息在进入 Extract 模型前已消失。
2. 若干示例保留了选择器字符串，却丢失精确行为说明；正则技能的排除操作与无条件输出契约有冲突。
3. 注册阶段 HTTP 012–015 的模型内容全部截断。离线重放官方解析函数得到的都是空数组，随后默认 `create`，不能称为四次完整有效的模型注册审查。

原文、来源清单、运行、导出、官方源码、已有 SKILL.md 均未由本轮改写。没有调用模型、重跑生成、安装软件或实现任务执行器/Oracle。发现的代码问题只记录。

## 2. 证据路径与材料分类

下文简称必须按本节展开；行号为当前 UTF-8 文件的一基行号，JSON 字段路径用于补充定位。窗口 span 不是原文行号，也不能作为连续原文引文。

| 简称 | 实际绝对路径 / 含义 |
|---|---|
| LAB | `D:/AS/AutoSkill-main/degradation_failure_lab` |
| UP | `D:/AS/AutoSkill-main/AutoSkill-main`，本地官方源码 |
| SRC | [原始 select.md](D:/AS/AutoSkill-main/degradation_failure_lab/data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/select.md) |
| RUN | `D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34` |
| MID | `D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/.runtime/intermediate_runs/20261011T153331_26f9a7a9` |
| EXP | `D:/AS/AutoSkill-main/degradation_failure_lab/results/exports/raecd75e08b34`，实验包装层生成的只读关联副本 |
| CORE | [正式 CSV 列选择与重排](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/csv-列选择与重排/SKILL.md) |
| REGEX | [正式正则表达式列选择](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/正则表达式列选择/SKILL.md) |
| ORDER | [正式列排序与随机打乱](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/列排序与随机打乱/SKILL.md) |
| QUOTE | [正式引用冲突列名](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/SkillBank/Users/docskill/引用冲突列名进行-qsv-select/SKILL.md) |

材料不能混用：

- **来源原文**：SRC；`LAB/data/catalog.json` L6 明示不是已确认的论文快照。`LAB/data/manifests/qsv_select.json` L3–17 固定来源 commit、路径和哈希，分类 `RECONSTRUCTED_OFFICIAL_SOURCE`，`paper_snapshot_verified=false`。没有在本轮联网核验其下载过程；论文快照对应性为 UNKNOWN。
- **实验输入快照**：`RUN/inputs/input001/select.md`。原文与快照实测均为 4795 bytes、179 行、SHA-256 `74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。`RUN/input_manifest.json` 记录原路径、执行路径及父来源哈希。
- **官方中间数据**：MID 的 ingest/extract/compile/register 结果、窗口节点；`RUN/SkillBank/.runtime/document_registry/` 的 document/support/skill/provenance 等。JSON 序列化、窗口过滤与结构化渲染也参与产出，不能把整份 JSON 都称为模型自由生成文本。模型原始内容在 `RUN/http/001..018/response.json` 的 `choices[0].message.content`。
- **正式程序技能**：CORE、REGEX、ORDER、QUOTE（Users/docskill）。正式注册状态来自 register 与 registry，不能根据同名可见目录自行计数。
- **官方可见树与证据**：`RUN/SkillBank/通用技能领域/Family技能/qsv-select/` 下 4 个技能展示副本及 references；另有 family/domain 两个总导航。共 10 个物理 SKILL.md，但只有 4 个唯一程序技能。可见副本带额外标签/路由信息，并非与 Users 文件逐字相同的第二份独立技能。
- **我们的导出/关联**：EXP 的 11 个 JSON。documents、text_units、windows、support_records、skill_drafts、skill_specs、registration 已逐对象与官方对应结果比较，均相等；traceability、window_source_alignment、skill_files、verification 是包装层构造，不是官方新增语义证据。

`cases/case001_qsv_select/{case,conditions,rules}.json` 和 `inputs/clean.json`、上述 catalog/manifest、当前配置及运行快照均已读取。`rules.json` L4–5 为 `CUSTOM_TEST_DATA`、空 provenance；每项为 `annotation_status=analyst_checklist`。这准确表明 R1–R7 是审核清单，不意味着七项覆盖全部规则或已完成独立审核。

## 3. 逐阶段工程核查

| 阶段 | 实际结果 | 依据 / 限制 |
|---|---|---|
| 输入 / Ingest | 1 TextUnit、1 Document、7 sections、2 Window；无跳过 | `RUN/parsed_text_units.json`；`MID/ingest/result.json` 的 text_units/documents/windows；`RUN/pipeline.log` L3–4。Document ID 为 `9c83d04d-0209-59d7-8e84-066c2d8161fe` |
| Extract | W1 生成 4 supports / 4 drafts；W2 为 0 / 0，complete=true、failed=false | 两个 `MID/extract/windows/<doc_id>/<window_id>.json`；pipeline.log L5–14；HTTP 002 计划、003–006 展开、007 空计划 |
| Compile | 4 SkillSpec，每个只关联自己的一个 draft / support | `MID/compile/result.json` 与 compile/documents；HTTP 008–011。不是四个独立来源证据 |
| Register | 4 action=create、hits=0、branch=hits0、reason=create；4 active、0.1.0 | `MID/register/decisions/<skill_id>.json` L2–6 与 hits/branch；pipeline.log L23–38、42–45 |
| Registry / 可见树 | 4 lifecycle、change log、version history、provenance link、upsert；3 微技能关联 CORE | `MID/register/result.json` 的 skill_specs/provenance_links/upserted_store_skills；HTTP 016–018 是 parent attach；compile 中 hierarchy_status=unresolved 不代表最终仍未关联 |
| 工程验证 | PASS，24/24；counts=1/2/4/4/4/4 | 本轮执行现有只读 verify（不带 --out）；`EXP/verification.json` L6–44。quality_status 明确为 SEPARATE_RULE_EVALUATION_REQUIRED |

配置实读 `LAB/configs/generation/deepseek_flash.json`，运行 `RUN/config.json` 另合并 qsv/domain/family/max_documents。模型为 deepseek-flash，thinking disabled，本地 hashing embeddings；窗口策略 recommended 实际映射 strict。HTTP 18/18 成功，均记录返回 deepseek-flash，累计 57472 tokens（49171 prompt、8301 completion；`RUN/execution.json` L5–13）。费用 UNKNOWN（API 未提供），本轮没有新模型调用。

`RUN/official_result.json` L73–93、124，MID/status 的 unresolved/failed 记录与 register/errors 均未记录未解决节点或异常；未发现顶层 exception.json。这只说明已保存的错误通道为空，不说明输出无截断、无遗漏、无语义错误。

### 3.1 为什么第二个窗口没有产出

- W1=`245afa09-be7e-56de-9a7a-f895fd5aa81a`；W2=`7ad0d07f-a2a3-5552-a285-2e102136d0f9`。见 `EXP/windows.json` L3、45。
- W1 实际 text 含 SRC L3–135 中的示例，但不连续完整覆盖该范围；描述段落 SRC L16–20 已不在 text。W2 实际 text 主要为 SRC L137–179 中的链接、usage 命令和 HTML 锚点，**没有 SRC L154、162–164、172–175 的表格信息**。`EXP/windows.json` L12、54 可以直接核对。
- 表格并未在文件读取或 Document 建立时丢失：`EXP/documents.json` L9 raw_text，L109 arguments、L135 select-options、L161 common-options 的 section.text 均保留；L31 的描述段落也保留。
- 已无模型重放当前官方 windowing：由已保存的 DocumentRecord 重建 planning section 和 windows，结果与 `MID/ingest/result.json.windows` 逐对象完全相等。

| 被筛掉的 planning paragraph index | 字符数 | 内容 | 本地重放条件 |
|---|---:|---|---|
| 5 | 342 | 描述段落：列名需要 header 等前提 | anchor_hits=[]，process_signal=false，长度 >320 |
| 48 | 443 | Arguments 标题与参数表 | 同上 |
| 50 | 458 | Select Options 标题与选项表 | 同上 |
| 52 | 628 | Common Options 标题与选项表 | 同上 |

确切代码位置：`UP/AutoSkill4Doc/document/windowing.py` L143–158 按空行拆块，L552–600 合并子节，L270–285 仅保留含 anchor/process signal 或长度 <=320 的块。L626–629 将 recommended 映射 strict。标记集合 L42–105 主要为治疗/咨询过程词；此次 CLI 表格没有命中。窗口 text 在 L459 拼接保留块，span 却取最小/最大边界（L460–461），所以 span 包含缺口，不表示其间原文均被送入模型。

HTTP 007 的 request.messages[user].content.excerpt 与 W2 实际 text 相符；response.json L1 为 `{"skills": []}`，finish_reason=stop。该窗口结果 L8–12 为 supports=[]、skill_drafts=[]、failed=false、complete=true、error={}。结合保守提取策略和该有限内容，**零产出是合理的空计划，不是已证实的提取故障**。需要记录的问题是进入 Extract 之前的窗口信息筛除；不能声称模型读到了完整选项表后决定忽略 R7。模型的内部决策原因为 UNKNOWN。

### 3.2 注册截断与默认路径

HTTP 012–015 的 response.choices[0].finish_reason 都是 `length`，completion_tokens 都为 256，content 不是完整合法 JSON；相应 request.max_tokens=256（012/request.json L15，其余同字段）。配置文件的 max_tokens=16384 不覆盖官方特定阶段预算；`UP/AutoSkill4Doc/store/versioning.py` L68–75、101–117 指定 hits0=256、full=768、hierarchy=128。

本轮只对保存的文本调用官方 `autoskill.utils.json.json_from_llm_text`，四次返回值均为 Python list `[]`：其容错扫描在不完整根对象中选中了完整的 `target_skill_ids: []` 子片段。代码位置 `UP/autoskill/utils/json.py` L35–78、81–95。随后 `maybe_json_dict`（`UP/AutoSkill4Doc/core/llm_utils.py` L167–170）把非 dict 转为 {}，`classify_change`（versioning.py L1371–1384）在 action 缺失时默认 create、resolved_skill 回退原 spec、reason 回退 action。四份保存 decision 的 action/reason=create、无 matched IDs 与此路径一致；未见修复 HTTP 调用。

因此可以明确报告“截断响应 + 容错解析得到空数组 + 默认创建路径”，不能把开头可见的 create 字样当作完整决策对象被采用。HTTP 成功与产生注册文件仍是真实工程事实；此次 fallback 是否改变了本应由完整决策得到的结果为 UNKNOWN。没有重试付费调用，没有修复官方代码。

### 3.3 Evidence Manifest 的证据粒度

4 个 manifest 分别位于可见树的 `二级技能/CSV 列选择与重排/references/evidence_manifest.json` 和 `微技能/{正则表达式列选择,列排序与随机打乱,引用冲突列名进行 qsv select}/references/evidence_manifest.json`（完整父路径为 RUN/SkillBank/通用技能领域/Family技能/qsv-select）。每份 L5 为技能 ID，L7 support_count=1，L10 support ID，L15–21 span/relation/confidence/quote，L40 window_id。本地比较确认 4 份 quote 都等于各自 SupportRecord.excerpt，也都等于同一个 W1.text。

`UP/AutoSkill4Doc/stages/extractor.py` L1099–1105 把整个 unit_text 放入 excerpt。因此 confidence=0.8–0.9 不是句子级正确性概率；4 个 support ID 不是四个独立规则证据。R7 没有任何这样的 support。

`LAB/src/degradation_lab/artifacts.py` L90–101 的对齐是窗口每个非空行对输入的顺序精确匹配，不验证生成陈述的蕴含，也不检查原文所有行是否进入窗口。W1 匹配 82 行（最小3、最大135），W2 匹配12行（137–179），W2 标题 `Usage [↩](#nav)` 为 unmatched_normalized_lines；这些统计不应解释为语义覆盖率。

## 4. ID 词典与规则级审计矩阵

| 链 | SupportRecord ID | SkillDraft ID | SkillSpec / 正式 skill ID | 最终文件 |
|---|---|---|---|---|
| C1 | `819cec2f-0f64-5faa-baec-06919fde83af`（S1） | `def5f116-bce7-54b1-afcd-cbfb3db8c337`（D1） | `f4c4df75-6ea6-5d4d-b30c-d7e825084300`（K1） | CORE |
| C2 | `76983d71-789e-5f48-b781-ff2ec59ba71b`（S2） | `0e55a3de-b1dc-50cf-93fb-2259c51f7403`（D2） | `bd72bc3b-8c84-59c2-9fd4-5caba1a5350b`（K2） | REGEX |
| C3 | `df120f38-3d43-51b7-a677-74f37e20013f`（S3） | `89f8089b-9739-5ad3-ae4e-f2298dd209c8`（D3） | `500c276a-5f59-5af9-86f5-4c0fbf4ad1be`（K3） | ORDER |
| C4 | `01b26d5a-543b-550f-9b28-34d3399135f3`（S4） | `1bb58b76-1f3a-555d-ae51-b3173a8dcbc6`（D4） | `b0592fe3-a3d5-539a-af63-d33035c20003`（K4） | QUOTE |

Support 官方原件为 `RUN/SkillBank/.runtime/document_registry/supports/<support_id>.json`；draft 官方原件在 `MID/extract/result.json.skill_drafts`，spec 在 `MID/compile/result.json.skill_specs`，注册决策为 `MID/register/decisions/<skill_id>.json`。以下引用 EXP 数组副本行号便于阅读，已核对其对象等于官方对象。

判断口径：correct=行为含义明确保留；omitted=相关信息不见；contradicted=有相反陈述或契约冲突；unsupported=原文不支持的额外断言；uncertain=只保留字符串/表示层未验证等。部分原子项可以有不同判断，不能把复合项硬压成单一准确率。所有 correct 都仅指文档语义保留，不指已经运行成功。

| rule_id | 原始规则（明确支持） | 是否需要原子化 | Window | SupportRecord | SkillDraft | SkillSpec | 最终技能 | 初步判断 | 证据依据（详见下一节） | 审核局限 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | `1,4` 第1及4列；`1-4` 第1至4列 | 是：枚举与闭区间两行为；共享机制还需细分 | W1 | S1（其余 support 重复同一整窗） | D1 | K1 | CORE | uncertain：R1a correct，R1b 解释 omitted | SRC L27–36；S1.excerpt/EXP support L12；draft L34–35、74–75；spec L34–35、74–75；CORE L52–53、92–93 | 不能仅凭出现 `1-4` 判定精确范围含义已完整保留；人工确认保留标准 |
| R2 | `!1-2` 排除前2列；`Foo[2]` 第3个同名 Foo | 是：反选与重复名的索引体系独立 | W1 | S1 | D1 | K1 | CORE | uncertain：具体位置解释 omitted | SRC L51–60；support L12；draft L37、44、95；spec L37、44、6；CORE L33、55、62 | 不能把保留 Foo[2] 字符串当作已保留零起点重复名索引；执行 UNKNOWN |
| R3 | `_` 末列；`_-1` 反转列序 | 是：末列引用与逆向范围 | W1 | S1 | D1 | K1 | CORE | correct（所述两行为） | SRC L63–72；support L12；draft L38–39、84–85、95；spec L38–39、84–85、6；CORE L33、56–57、102–103 | 单独 `_` 执行未验证；不推广至越界/空CSV等未给出的情形 |
| R4 | `!/regex/` 排除匹配列；--sort 按字节字典序排所选列 | 是：正则反选与排序非同一操作 | W1；表格精确定义不在 W2 | S1/S2（反选）、S3（排序） | D1/D2/D3 | K1/K2/K3 | CORE/REGEX/ORDER | contradicted（REGEX 无条件输出契约）；操作主句/排序 correct | SRC L87–102、154、164；support L12/68/124；draft L174、197、292、308；spec L162、185、268、284；REGEX L34、58、80；ORDER L31、48、61 | 排除分支不能“输出匹配列”；是否实际误执行 UNKNOWN；无header排序需另核实 |
| R5 | --random 打乱所选列；--seed 整数随机种子 | 是：排列操作、种子类型、复现边界分开 | W1 有示例；整数表格不在任何窗口 | S1/S3（示例）；类型无 support | D1/D3 | K1/K3 | CORE/ORDER | uncertain：random correct；整数类型 omitted | SRC L105–120、162–163；support L12/124；draft L293–294、312、324；spec L269–270、288、300；ORDER L49–50、66、82 | seed=42 是示例，不是类型约束；固定种子不等于跨版本固定排列 |
| R6 | 空格或选择器冲突字符需引用 | 是：空格/冲突条件与 shell/选择器两层引用需区分 | W1 有冲突示例；L154 表格缺失 | S1/S4 | D1/D4 | K1/K4 | CORE/QUOTE | uncertain：一般条件保留，精确转义未验证 | SRC L129–132、154；support L12/180；draft L413–425、435–437；spec L381–389、399–401；CORE L63、QUOTE L28、56–57、72 | SRC 命令中有真实反斜杠，生成示例删去；未查 pinned qsv parser/测试，不能断言是修复或错误 |
| R7 | --no-headers 首行不作表头；--delimiter 读入分隔符单字符；--output 写文件非stdout | 是：三项相互独立，且delimiter只定义读入 | 无（W2 span 跨过这些位置，但 text 不含） | NONE | NONE | NONE | NONE（4个正式技能均未表达） | omitted | SRC L173–175；Document section 保留/EXP documents L161；windows L54；4 draft/spec/正式文件逐项核查无该行为 | 已定位窗口阶段信息缺失，但无法推出若完整送入模型必定生成；不能将delimiter扩大为输出格式设置 |

## 5. 原子语义、遗漏与附加断言

### R1 / R2：示例字符串与行为解释不同

R1a 在 CORE 的前言示例及 Example 1 明确“第一和第四列 → 1,4”，相符。R1b 仅为“按范围选择列：1-4 或 3-”，没有原文“first 4 columns”的明确结果说明；属于语义压缩/解释遗漏候选，不是已发现把逗号与连字符颠倒。R2a 只写“排除列：!1-2”；R2b 只写“重复名称索引（如 Foo[2]）”和组合命令，不说明第三个 Foo。没有证据表明模型把 Foo[2] 写成第二个，但缺失正是后续容易发生 off-by-one 的风险。两类信息损失已可在 HTTP 003 的展开结果中看到；不是注册阶段新引入。

### R3：适合作为目标规则无关的对照

“末列特殊字符 _”和“反转列顺序：_-1”在 draft/spec/正式文件均表达，未见反向矛盾。两者仍需分别判分；本轮不把它们推广为任意逆向区间或单列/空文件的完整规范。

### R4：同一技能内部的相反契约

REGEX L34、58 要求 `!/pattern/` 排除匹配列，L80 的 Output Contract 却无条件写“输出匹配正则的列”。在排除任务上应输出不匹配列，两处不能同时成立。HTTP 002 计划的 success_artifact 已有该不完整契约，HTTP 004 展开继续保留，HTTP 009 Compile 和最终文件延续；因此错误最早可观察于 Extract 规划，不是仅凭 ID 关联推测 Compile 新造错误。

同技能 L38、51–52 将“列名无规律/需要精确指定列”当禁用条件，原文未规定这一禁止；精确正则可以实现精确匹配。标为 unsupported 的范围收窄候选，仍需人工确认是否仅是建议性路由。L76 的敏感数据检查不是原文支持的全面去敏保证；不要将按列名排除扩张为识别所有内容敏感信息。示例正则无锚定，不能自动改成精确名称匹配规则。

ORDER 的 --sort 保留“按列名字节值而非列内容”，与原文列排序示例和 byte-values 定义一致；“按列名”是结合列选择上下文的解释，未执行核实 no-headers 时的排序依据。排序不是行排序，也不是自然语言 locale 排序。

### R5：种子不等于完整随机 Oracle

ORDER 明确保留列打乱，而非打乱行/列内值；没有出现 `--seed` 整数类型要求。生成的“可复现”是 seed 示例的合理推断，但原文未规定随机算法、版本稳定性及 seed 有效范围。固定 seed 跨版本排列的身份为 UNKNOWN。只核对“输出是一种排列”可能让未随机打乱的原序也通过，不能用于检验种子规则是否正确。

### R6：不要掩盖转义表示差异

SRC L132 的本地文本在双引号前带反斜杠；QUOTE L72/91 和 CORE L63 的正文示例为外层单引号、内层双引号，不带该反斜杠。JSON/YAML 中的 `\"` 还可能只是序列化转义，必须对解码后的值和传入 argv 分开核对。一般引用条件没有明显反向错误，但本轮缺少目标 qsv 版本和实际 argv/输出证据，精确命令为 uncertain，不将有空格示例当作任意特殊字符的全覆盖规则。

### R7：完整遗漏，不是原文不含

三个 common options 在原文和 Document 中都存在，4 个 SupportRecord、4 个 draft、4 个 spec 和4个正式 SKILL.md 中都没有相应操作定义。该遗漏优先归于窗口阶段可观测的信息筛除，后续提取/编译的反事实能力仍 UNKNOWN。R7 不适合作为本次 R1 试点的任务前提，否则 Clean 基线已有系统性缺口会混入目标机制。

### 模板残留与父子冗余

四份正式文件均有 `Example Therapist Responses`、`Client/Input`、`Therapist/Output`（CORE L88、REGEX L82、ORDER L72、QUOTE L67）。官方 Extract prompt 包含 therapist/intervention 模板（HTTP 007/request.messages[system]），默认 windowing 标记也偏咨询领域。这是真实模板残留，不是 qsv 操作规则。中文生成相对于英文来源、重复示例、CORE 已含微技能操作而另有三个微技能，都会改变上下文长度和路由；不能把未来路径差异仅归为“冻结”本身。

## 6. 四个技能的主要风险汇总

| 正式技能 | 主要正确性风险 | 已知最早观察点 / 非结论 |
|---|---|---|
| CORE | R1范围解释、R2前两列/第三同名列细节缺失；R5种子类型、R7三选项缺失；可执行前提/CSV输入路径未完整示范 | 前三者在 HTTP003 已有；R7在窗口阶段缺失。未观察到1,4被明确写错；不能声称任务会失败 |
| REGEX | 排除操作与 Output Contract 冲突；“精确列需求禁用正则”的无来源限制 | HTTP002/004→009→正式文件。未运行，因此实际选/排失败率 UNKNOWN |
| ORDER | --seed整数约束缺失；“可复现”没有限定软件版本；无header和同时使用sort/random未定义 | seed类型在窗口未提供；复现断言在HTTP005已见。不要自行补同时开关优先级 |
| QUOTE | shell引用与选择器引用没有分层；原文/生成命令反斜杠差异未验证；范围条件可过度概括 | HTTP006 示例已有差异，后续保留。不能断言命令成功或失败 |

## 7. 可以定位的阶段与 UNKNOWN

可定位：原始字节完整→Document仍完整→窗口缺失表块；正则契约冲突首次出现在Extract模型计划/展开；精确索引解释在展开中消失；注册响应截断并触发默认创建；spec内容在最终Users文件中保留。本轮查了实际代码和响应，不是只用README或ID关联。

不能定位为因果结论：哪个模型内部推理导致遗漏；完整窗口是否会消除R7遗漏；若注册响应不截断是否仍创建相同四技能；任何错误是否影响下游任务；多任务相关失败是否由同一规则传播。以上均为 UNKNOWN，须下一阶段的控制实验和局部修复/破坏双向干预。

尚需人工确认：原子规则和保留判据；R1b/R2代码示例是否足以算语义保留；R4禁用条件的规范性；R6精确转义；固定qsv版本的命令行为。R1–R7外的完整规则覆盖、来源下载真实性和论文快照身份未在本轮独立核验。

## 8. 只记录的代码问题与能力边界

- 官方 windowing 的长度/咨询信号筛选会删除此次CLI关键参数表：代码与保存产物已无模型复现，不修改官方源码。
- 官方容错JSON解析可把截断决策中的局部数组当完整结果；classify_change 对空对象默认create：已离线复现，不修改官方源码，也不修改既有生成参数。
- 包装层 `LAB/src/degradation_lab/artifacts.py` L108–146 的检查不要求 finish_reason=stop、不校验注册响应根对象schema、也不验证逐规则语义；PASS在本例可同时伴随上述现象。只记录，不能重定义已有PASS。
- `LAB/src/degradation_lab/evaluation.py` L10–52 校验人工规则记录/关联，L55–68初始化，L71–108汇总；`schemas/evaluation.schema.json` 仅rule_preservation/generated_addition。**没有下游Agent、CSV任务执行或Oracle评价**。
- 只读 verify 不带 --out 已执行；没有用 export_run 覆盖现有导出。11个导出齐全，无缺失文件需要补写。

实验准入决定与任务设计见同目录另两份报告；本审计不提供“七规则准确率”或已验证研究效果分数。
