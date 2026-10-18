# SkillGenBench 文档数据与 Oracle 全量审计备忘录

审计对象为官方 GitHub 工作树 `SkillGenBench`，提交 `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。Hugging Face 数据集 API 返回版本 `4e23915c65f0f1e7c8bacea00feb33974d936ef9`，更新时间 `2026-05-06T15:07:36Z`。**下述全量字节/解析统计来自 GitHub 快照；不可据此声称 HF 全量文件字节相同**。两者目录命名已有差异，另见主报告的快照比对。

## 审计覆盖和证据等级

- **已检查（全量）**：187 个 `task.toml`、全部仓库 JSON/TOML/Python 的标准解析；187 任务结构；64 文档任务的文档路径、文件字节 hash、字符/词/行/标题长度、任务说明和有效 verifier 的 AST/导入/断言/测试函数清单；64 个 shell runner 的同字节性；36 Domain 的全部 308 测试用例结构及参考函数调用。
- **已检查（语义）**：28 Code Doc 的任务要求和判定断言、关键控制流；36 Domain 共同 comparator、全部任务类型/规则定位元数据、参考实现与公开期望的一致性。对 NeuroKit 文档骨架、SoundFile 共享规则候选、Scikit-image 固定 fixture 及 Domain 输入混入任务元数据作专项审阅。
- **已执行（离线确定性）**：36 Domain 的公开 `solution_code`，逐例调用未经修改的公共 `assert_close`，共 308 cases。已先审查函数调用/导入，仅执行纯函数参考；不运行 `original_eval.py`。主代理另执行 Scikit-image 和 NaN 诊断，结果见其 `oracle_*probe*` 文件。
- **未验证**：官方 Linux/Docker shell 全链路、Agent 与 Skill 加载、任何付费模型、所有长上下文中每条规则的完备性、参考答案是否逐条符合源文。**静态“包完整”不等于环境中“Oracle 已可执行”，参考代码通过不等于源文和 Oracle 都正确。**

## 数量不是同一统计单位

|量|Code Doc|Domain Knowledge Doc|文档类合计|
|---|---:|---:|---:|
|官方任务|28|36|64|
|公开 collection/source 组|9 Python 库|36 CLBench context UUID|45|
|叙述性文档文件路径实例|70|36|106|
|SHA256 字节不同的页面/片段/context 文件|37|36|73|
|按文档 hash 集合去重的任务输入集合|24|36|60|
|每任务叙述性文件数|1–5|1|1–5|
|附带 `materials/docs/task.json` 描述符|0|36|36|
|有效 runner/active Python 文件存在且语法有效|28|36|64|
|在官方容器内确认执行成功|未执行|未执行|未执行|

**独立原始出版物数未知。73 是页面/片段/上下文文件的字节去重数，不能报告成 73 篇独立原始文档。** Domain 的 `context.md` 常拼接 System Context、User Questions、Artifacts 或多个 chunk；其内部可能包含多份材料。45 是可用于分组的公开来源/上下文簇；36 个 CLBench UUID 虽不同，但属于同一父语料体系，不保证统计独立。Code Repo 补充部分为 123 任务/32 来源组；其任务局部 README 统计不能替代完整 repository 计数。

|来源组|任务数|字节不同文档数|任务 ID|
|---|---:|---:|---|
|beautifulsoup4|1|4|037|
|librosa|1|1|001|
|moviepy|1|1|001|
|neurokit2|7|9|012,014,017,024,038,044,046|
|pillow|2|2|001,002|
|pydantic|3|4|001,004,005|
|scikitimage|2|2|001,002|
|scrapy|3|7|024,041,050|
|soundfile|8|7|007,010,012,015,020,021,022,023|

Code Doc 的完整 ID 为 `<来源>-task-<编号>`。36 Domain 来源组各只有 **1** 个官方下游任务；完整逐组 ID、原 context UUID、规则定位和长度见 `sgb_document_tasks_only.json` 与 `sgb_source_groups.json`。Domain 有 18 个命名主题各取两份上下文：Finance、Healthcare、Humanities、Legal Advisory、Lifestyle、Management、Science、Experimental/Observational/Simulation、Instructional/Operational/Workflow、Game/Legal/Mathematical/Programming/Technical；主题重复不是共同原始文档。

长度按 UTF-8 解码、保留工作树 CRLF 计字符；另记录 LF 规范化字符和 hash。词数为 whitespace split，**不是模型 token**。

|长度|Code Doc|Domain Knowledge Doc|
|---|---:|---:|
|单文件字符 min/median/max|159 / 1,423.5 / 67,593|16,323 / 61,061 / 179,801|
|每任务文档集合字符 min/median/max|300 / 7,020.5 / 136,431|16,323 / 61,061 / 179,801|
|按路径总字符|758,715|2,376,438|
|按独特字节文件总字符|437,140|2,376,438|
|独特文件 whitespace words|45,883|349,554|

主要语言是英文；SoundFile 源码页少量 CJK 字符不构成第二语言样本。领域包含图像、音频、爬虫、数据校验、神经信号以及上述 18 类领域/规则推理。没有公开原始 PDF 页面几何或版面标注；可做 Markdown 结构/顺序/链接可访问性/相关干扰，不能将合成格式扰动泛称真实 PDF 版面退化。

## 输入充分性与任务泄漏

1. **NeuroKit2 七任务的 Clean 文档不完整。** 其 `functions/signal.md`、`stats.md`、`complexity.md`、`eeg.md`、`markov.md`、`microstates.md`、`ecg.md` 主要只有函数标题/名称，无签名、参数和返回值语义。`resources.md` 和 `resources/recording.md` 是外部链接列表。复杂 Oracle 要求的分解 shape、energy 规则、微状态调用约定等不能视作已由这些文本充分支持。Agent 通过预训练或安装库源代码弥补，是另一证据路径。
2. **SoundFile 文档集合中有真实源码。** 五任务 007/010/012/015/020 共享四文件集合，包括 `_modules/soundfile.md` 的实现与 docstring；不是单纯 API 手册。一份页面超过六万字符，代码与文字混合。021/022/023 则为单个短小任务提示性质摘录。
3. **Domain 的 `materials/docs/task.json` 不是原始知识文档。** 它含具体 question、expected output schema、info_locations、reasoning_steps、domain_knowledge_needed、anti_contamination。将整个 docs 目录无区别交给生成器会引入任务与规则定位提示。任务无关模式应明确只使用 `context.md`；任务条件化模式必须对全部方法提供相同附加信息，并说明即使不提供 instruction，官方已按任务挑选文档。
4. **公开 Domain `testcases.json` 含 `solution_code`。** 36 个全部如此。该文件必须隔离于生成和 Agent 执行材料，人工 Gold 也仅用于诊断。公开可得不能作为允许测试泄漏的理由。
5. 多数短 Code Doc 任务的 instruction 已给函数和具体操作，NoSkill 可能高分；即使 Skill 无文档支持，任务成功仍不能证明提取有效。相反长 Domain 文档可能有规则条件/例外/跨 chunk 冲突，适合退化但须先逐规则证实信息充分。
6. **Domain 也有明确缺失原始规则的样本。** `risk_interpretation_gatekeeper_002` 的 `context.md:112` 用一个方括号占位句替代了风险评分细则；参考实现要求的 .521/.173/.241/.065 权重、.447/.250 归一化和 .705/.515 阈值在整个 generation source bundle 均不存在。其 info_locations 声称应在该段找到评分规则，但实际段落没有规则。这一任务不能作为“源文充分的Clean”样本来裁决生成器。
7. 已观察文本抽取/拼接痕迹：`balanced_ternary_mux_sim_and_structure_check_007` context含368个 U+0005 控制字符；两个手册/判决类 context含form-feed页分隔符；多份context包含字面量 `\\n` 和长度超过4000的单行（reviews_csv单行最长16384字符）。form-feed不必然损坏语义，字面量转义也可能是嵌入artifact；应先标注并保留原始版本，不能默默全部清洗再称原版Clean。

## JSON/TOML 与 Oracle 缺陷

### 标准解析

全库扫描：451 TOML 通过；426 JSON 中 237 通过、189 严格失败；305 Python 中 274 通过、31 含 NUL 失败。

- **全部 187 个 generation `tasks/<id>/task.json` 末尾有多余逗号。** `scikitimage-task-001/002` 均在末项 `expected_output_file` 后有逗号；不是两个孤例。36 Domain 置于 `materials/docs` 内的任务描述 JSON 本身可以解析。需查实际调用链是严格 `json.loads`、容错 parser 还是使用 TOML；严格失败本身不等于所有路径均已失败。
- Domain `spectrum_concentration_estimator_008/tests/testcases.json` 有非标准 `NaN`，默认 Python `json.loads` 接受，但标准 JSON parser 应拒绝；共同 comparator 的 `math.isclose(nan,nan)` 返回 False，使第 7 case 参考正确输出也无法匹配自己。
- Code Repo 的 Scrapy_gtb01 `gt.json` 实为多行 JSON，按单 JSON 文档失败，需按实际读取方式判断；31 `tests/test_script.py` 为普通 Python 中含实际 NUL，不是压缩包，不能编译。这些属于补充 Code Repo 风险，不能计入文档64任务的 Python 语法失败。

### 有效 Oracle 路径

64 文档 `test.sh` 完全同字节（SHA256 `2ad84cb7df6840331626a506a5e106ddb79de898da1737bf21471f1d3b8d472a`）：设置 `TEST_ROOT_DIR=/workspace`，优先 pytest `tests/eval.py`；必要时 pip 安装 pytest，安装失败被 `|| true` 吞下；pytest 退出码决定 reward，并最终 `exit 0`。因此必须看 `reward.txt`/CTRF 和测试日志，不能看 shell exit0 就认定通过。

36 Domain `eval.py` 同字节，执行候选函数并递归比较：dict key 集相同、list 长度/顺序相同、str/bool精确、数值 rel_tol=1e-5/abs_tol=1e-8。它不是 LLM judge，也不检查 Skill 格式、生成方法或 Agent 品牌。备份的 `original_eval.py` 含 OpenAI 客户端，但上述 runner 不调用它；本审计从未运行该文件。

28 Code Doc 都检验提交代码或运行结果，不是仅文件名/格式。然而 9 个固定 fixture 小任务（librosa001、moviepy001、pillow001/002、scikitimage001/002、soundfile021/022/023）主要“固定输入结果等于运行时 reference + 源码字符串出现 API 名”，不能保证真实调用；源码 token 检查也可能拒绝语义等价表达。主代理已在两个 scikitimage 任务实证硬编码输出配 API 注释也能通过。

Scikitimage001 的常数 template 方差0，带/不带 padding 的 peak 均 `[0,0]`；不适合检验 peak 坐标语义。002 的 Oracle 固定 `/255`、threshold_rel=.01/min_distance=1，而提供文本未完整指定参数，须先解决任务契约才做生成质量试验。

### 全部 Domain 公开参考一致性（实际离线执行）

环境：Windows Python3.13.9、NumPy2.3.5。**36 任务/308 cases，302 cases 通过，33 任务全部通过，3 任务参考和预期不一致**。

|任务|结果|失败解释|
|---|---:|---|
|lockdate_compliance_gate_001|6/10|case2 日期解析 ValueError；case3/8/10 blocks 列表不符|
|risk_interpretation_gatekeeper_002|6/7|case7 risk_score 0.491 vs 0.488|
|spectrum_concentration_estimator_008|6/7|case7 concentration_uM NaN 不自等|

前两项不能直接断言 expected 错，也可能参考实现错或源文不唯一；必须先人工裁决。不一致足以禁止将这些失败归因生成方法。NaN 是 comparator 的确定性缺陷。`gatekeeper_minireport_003` 参考代码使用进程随机化 `hash(seed)` 生成声称 deterministic 的 token，但全部9 cases的 token均None，批准路径未覆盖。33任务参考全过不代表反例完备或真实文档规则均已得到验证。

## 共享规则与退化适用性裁决

**公开正式规则→多任务依赖映射为0；满足“同源同规则至少2依赖+1非依赖，且因果验证”的已证实来源组为0。不能用同库多任务代替该结论。** 这不是证明绝不可能，而是当前证据不达标。

- Domain 每个原始 context UUID 只有1个官方任务，直接无法满足组内2+1。一个任务内7–10 cases是该函数测试输入，不是三个独立任务。可扩展为规则保持的新变体，但须标为扩展数据并保持同源聚类。
- Pydantic 001/004/005 分别validator顺序/discriminator/config边界；Scrapy 024/041/050 分别feed overwrite/offsite/depth；共享库名并无共同关键规则证据。
- NeuroKit 虽共享 signal/stats 文档，但文档是索引骨架，无法支持可定位的共同操作语义。
- **SoundFile 仅保留一个操作级候选**：cursor以frame计数，默认seek从头定位，而whence=1相对当前位置；010（seek500并按当前位置截断）/023（read8→seek-3 relative→read5）作依赖候选，007（format/subtype校验）作控制。证据：010的 `_modules/soundfile.md` 821–874行、023的 `seek_overlap.md` 3–6行，Oracle对cursor有要求。但两任务官方输入集合不同，010 instruction已经写明seek500；023 fixed-fixture判分弱，尚无共同冻结Skill/局部修复反事实。因此不能计入满足来源，只能是后续扩展验证候选。

可恢复退化应保留全部目标规则事实和至少一个可访问支持路径，只扰动标题层级、跨段布局、引用可访问性、证据分散和干扰；删除唯一阈值/唯一例外是知识不可恢复缺失，应单独标注信息损失对照。没有原始页面布局的材料只支持文本结构扰动。

## 数据充分性与下一步建议

- 单链路试点：**有条件足够**，优先 `scrapy-task-024`（文档提供具体默认值、Oracle为纯函数），再选 `reviews_csv_conformance_validator_007`（真实长SOP、参考7/7通过）；`soundfile-task-010`可用于调用/持久化链路校准，但instruction已给操作，先测NoSkill天花板。Scikit-image两任务仅作为Oracle诊断反例，不作首个“文档规则损失”证明。
- 多来源退化描述分析：有条件；以9库+36context簇报告，并保留同属CLBench父源和18主题的相关性。每来源多个任务/退化seed/重复运行不能当独立文档增加N。
- 多退化类别比较、方法开发/测试、跨源泛化：需预注册来源分割与留出父源/库，并报告来源级配对差和按来源cluster bootstrap CI，或层级模型（来源随机效应、任务嵌套、退化/路径固定效应）。仅9个代码文档库时区间会宽；不能把187任务给出窄普通二项式CI。
- 共享规则传播/双向局部因果干预：**原数据不够直接支撑**。最小扩展是在通过Oracle门槛的原长文档内建立规则→至少两个不同函数/任务与一个无关控制、人工源文验证；保持官方任务成绩单独报告。现有5 Clean来源可作外部补充，但同样需新建确定性Oracle与2+1映射。
- 不建议为增加样本首先扩CodeRepo：类型从文档退化变为代码仓库理解，依赖重且存在31 Python语法问题。无需新建完整Agent框架；关键是隔离材料、冻结Skill集合、直接文档对照和可解释Oracle。

## 可复现文件与命令

- `scan_sgb_data.py`：全量结构/格式/文档hash与AST扫描，只写审计输出目录。
- `probe_domain_reference.py`：已审参考纯函数与公共comparator的一致性；无付费调用。
- `annotate_sgb_data.py`：写入区分 OBSERVED/INFERRED/UNVERIFIED 的人工判定。
- `sgb_task_inventory.jsonl`、`sgb_task_inventory.csv`：187逐行任务，包含用户要求全部15字段及补充证据。
- `sgb_document_tasks_only.json`：64文档任务详细记录；`sgb_source_groups.json`：77全类来源组；`sgb_document_files.json`：原始文件路径级长度/hash。
- `sgb_data_summary.json`、`domain_reference_probe_results.json`：汇总与逐case离线结果。

```powershell
python .\audit_2026-10-15\scan_sgb_data.py --repo .\audit_2026-10-15\SkillGenBench --output .\audit_2026-10-15
python .\audit_2026-10-15\probe_domain_reference.py
python .\audit_2026-10-15\annotate_sgb_data.py
```

这些命令不构成官方Benchmark执行。观察、推断、未验证必须保留；没有完整执行证据的64个Oracle不能标“64个已确认可运行”。
