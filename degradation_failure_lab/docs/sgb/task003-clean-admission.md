# Task003 准入审计：Sanctuary Endgame Scheduler

审计日期：2026-10-26。结论：**选择 `sanctuary_endgame_scheduler_002`，GO（任务契约、规则映射及隔离评分接入）；真实生成和 Agent 执行仍 BLOCKED，等待本任务预算授权及上游质量审核。** GO 不表示 Agent 已成功。

操作手册：[task003-clean-runbook.md](task003-clean-runbook.md)。本轮没有调用生成模型、启动真实 Agent、构造退化输入或追加预算。

## 1. 检索范围与候选比较

以 `configs/datasets/sgb.json`、`data/manifests/sgb/tasks.jsonl` 和固定发布 `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d` 为准。187 条记录包括 Code Repo 123、Code Doc 28、Domain Knowledge Doc 36。本轮逐项核验注册源文件和 official_assets 的内容哈希，未发现不匹配；完整筛选表见 `results/sgb/audits/task003-clean-20261026-001/candidate-screen.json`。该表记录执行目录、既有状态和本轮审核层次，不将静态完整性当作语义准入。

| 候选 | 结论 | 本轮核查的证据／主要风险 | 接入成本 |
|---|---|---|---|
| Scrapy024 | 排除 | `runs/eval/sgb/scrapy-task-024/` 已有多个真实批次 | 已接入 |
| FLA002 | 排除 | `f02d*`、`f02u*` 已运行；规则损失仍是已知研究案例 | 已接入 |
| Scrapy041 | 排除 | `s41d001/batch.started` 与结果存在；不能冒充尚未运行的新任务 | 已接入 |
| Shark Warranty `shark_warranty_safety_gate_001` | DEFER | 指令要求任意短 issue code，但原比较器对字符串、列表顺序精确比较；原参考自选 `MODEL_UNKNOWN` 等编码。未发现获审的输出编码契约／修订 Oracle。原文常量存在也不能解决此评分问题 | 中；先解决契约 |
| Currency `currency_budget_normalizer_001` | DEFER | 参考实现第 23–24 行明说换算一致性容差原文未明确，自取 `1e-6`；第 118 行另行解释 split budget 的含义；warning／violation 文本精确比较。未发现获审修订 | 中；先解决契约 |
| Roof Beam `roof_beam_count_and_order_validator_007` | DEFER | 任务只要求 concise human-readable message，Oracle 精确匹配参考自选 message、refs 文本；D 系列源表与说明的映射仍需逐型号核对。公开参考 8/8 只证明自洽，未发现契约消歧证据 | 中；先解决契约 |
| BeautifulSoup037 | DEFER | 已有 `docs/sgb/beautifulsoup037_runtime_readiness_20261024.md` 明确阻断真实评分；原测试有 `.name =` 源码写法限制和对象身份要求，现有 fixtures 不能替代可信后端 | 高 |
| Pydantic001 | DEFER（本轮严格隔离口径） | Annotated 方向规则清楚；已有工程示范。原评分器在 pytest 进程中执行候选，并检查真实类／元数据；尚未建立保持原断言的独立可信观察边界 | 中高 |
| Scrapy050 | 保留候选，未准入 | DEPTH_LIMIT=0 规则明确，但需 Scrapy 实际本地 crawl、子进程与 loopback 环境；原测试对 Spider 结构及 ProbeSpider 的检查需额外审核 | 中高 |
| Wall Setting `wall_setting_scheduler_002` | DEFER | 多角色、工作日、例外和权限阈值，约 997 行源文；尚未完成每项预期输出的独立规则审查 | 高审核成本 |
| Capacity Admission `capacity_aware_edge_admission_controller_006` | 保留候选，未准入 | 可用 JSON 隔离评分，但约 1717 行源文，涉及 21 条 edge、N3/N4 映射及容量计算；当前未完成全部规则链审核 | 高审核成本 |
| **Sanctuary002** | **GO，选中** | 单一 UTF-8 源文；4 个目标规则可直接定位；8 个原测试无自由文本解释评分；参考正例 8/8，三个常量变异分别 1/8、1/8、3/8；复用现有隔离 JSON 评分器 | 低至中；资产、绑定与少量参数化 |
| 其余 175 条 | 检索完成，未逐项新准入 | 完整筛选表保留全部身份、来源、既有审核状态及运行目录。多数仍是 `PENDING_RULE_TASK_ORACLE_REVIEW`；没有把未深入审核的条目判定为不可能，也没有为其授予 GO | 未评估到可执行程度 |

Shark／Currency／Roof 本轮仍暂缓；没有为了选第三题修改原测试或放宽既有标准。前三项排除基于当前运行记录，超出了用户最初提及的两项，避免把 Scrapy041 重复计数。

## 2. 选定任务身份与数据边界

| 项目 | 固定值 |
|---|---|
| task_id / task_key | `sanctuary_endgame_scheduler_002` / `t-febd929cffec` |
| generation case | `case003_san`（缩短名称以通过 Windows 路径门禁） |
| source_id | `sgb-0d13982799c95cfa` |
| 唯一源文件 | `data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md` |
| 源 SHA-256 | `7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c` |
| 原文大小 | 108565 bytes；321 行，若干长段落且规则重复出现 |
| 原 Oracle SHA-256 | `57eb8902f1d0a5601bef71f1affaa944c2b946427c0e2e40e9a58c5d48f437eb` |
| 原 testcases SHA-256 | `d582e7930e73db16a3392d406ed6493342ae9d8c1da47eba83aa2678f8bea15b` |
| 预留生成／下游 ID | `sn3g001` / `sn3e001`；均不是已完成运行 |

原任务位于 `.external/skillgenbench/5a8bd61d/skill_evaluation/domain_knowledge_doc/clbench_Empirical_Discovery_Simulation_Simulation_Environment/sanctuary_endgame_scheduler_002/`。`instruction.md`、原 task.toml、eval.py、testcases.json、test.sh 原字节均保留在本地适配资产中。`original_eval.py` 包含生成辅助逻辑，不执行、不作为可信评分入口。

此来源是 **SkillGenBench 的 task-curated release text**，有固定发布和内容哈希，不声称已独立核验出版社原始规则书。源文包含 board-game café 角色描述和问题上下文；这是输入本身的格式风险。未在该输入中发现本任务 `solve`、`solution_code`、`expected_output` 或 `scheduled_turns_after_trigger` 实现／答案字段。任务元数据、规则清单、测试、参考代码和预期输出不在上游 input manifest 内。

NoSkill 容器没有源文和 Skill。CleanSkill 仅挂载生成后冻结的包；两组接收同一原任务及同一条件式正文读取说明。任务容器没有 Oracle、参考答案、项目仓库或 Docker socket。候选执行只获得一个测试输入；可信评分器另起容器读取原测试和候选观察结果，不导入候选代码。

## 3. 源文—任务—Oracle 映射与契约判断

| 稳定规则 ID | 原文定位 | 任务未给出的内容 | 原断言敏感性 |
|---|---|---|---|
| `sanctuary-objectives-4` | 第 94–95 行；同段在 162、233、308 行重复 | 支持目标数为 **4** | 将 4 改为 5，原用例 1、3–8 失败 |
| `sanctuary-trigger-10` | 第 95 行 “10-point” | 首个条件 1/2 触发者 **10** 分 | 将 10 改为 5，原用例 1、3–8 失败 |
| `sanctuary-last-turn-5` | 第 95 行 “5-point” | 别人触发后在最后一回合满足 1/2 者 **5** 分 | 将 5 改为 10，原用例 1、3–6 失败 |
| `sanctuary-extra-turns` | 第 38、94–95 行 | 排除触发者，其余顺时针各一回合；仅条件 3 立即结束 | 所有用例均检查调度，尤其用例 2、5、7 |

任务公开了调度结构，却没有公开 4／10／5 三个常量。规则可影响评分不等于 Agent 必须依赖 Skill；模型可能已有知识，单次结果也可能随机不同。

**洗牌字段边界已按明确任务指令消歧。** 源文说触发结束后牌堆空时重新洗牌，语义可以覆盖更晚回合；任务 RULES 则明确括注 “on the trigger turn when (1)/(2) triggered and pile is empty”。原用例 3 要求 True，用例 6 的后续回合空牌堆要求 False，符合这个任务专属定义。接入没有改写来源或 Oracle；报告范围只覆盖此输出契约，不声称还原完整游戏规则。若研究目标改为完整规则书忠实度，应另立任务／Oracle 审核，不能混入本批。

**列表顺序另有一项明确的本地接口澄清。** 原任务把 `conditions_met` 写成条件编号列表但没有规定顺序，而原比较器按列表位置比较。两组共同的 runtime-note 明确要求按 1、2、3 升序，保留原题和 Oracle 字节。这是已公开条件编号的规范表示，不提供 4／10／5 等隐藏文档常量。准入结论适用于“原题＋这份固定运行说明”的本地契约；不能把未收到该澄清的历史运行当作相同协议。

8 个 expected_output 已逐例按上述契约人工核对，独立表见 `tests/test_sgb_sanctuary002.py`。用例 6 没有记录 C 的额外回合，但仍要求输出完整应调度队列；只对已记录 A、B 分配标记。该题未明确完整输入域：无触发、异常玩家序列、不同玩家人数、空弃牌堆、目标数大于 4 等没有完整覆盖，不据此扩大结论。

每个 pytest 参数项比较完整输出，只有 **8 项原始用例**。不同用例或同一用例内不同字段不能自动计为多个独立因果案例。规则变异夹具是工程敏感性检查，不是文档退化实验或 Agent 结果。

## 4. 接入能力：复用与必要增量

| 能力 | 状态与实现 |
|---|---|
| 源绑定、clean 输入、规则检查表 | 新增 `cases/sgb/case003_san/`；复用 SourceManager／CaseManager，原始来源不重复登记 |
| Anything2Skill 入口 | 复用 `scripts/lab.py run`；一次正式入口内部完成 ingest/extract/compile/register。没有新独立阶段 CLI |
| 生成配置 | 复用 `configs/generation/deepseek_flash.json`；只增加案例领域字段 |
| Skill 注册／冻结 | 注册由上游正式管线完成；复用公共 `pilot.py freeze` 和 `freeze_generation`，保留最终活动版本与全部包文件 |
| 任务适配 | 新增 `audited/sanctuary002.py`、任务资产及 `configs/tasks/sgb/...json`；仅更新注册表中的本任务一行 |
| 原断言隔离评分 | 参数化既有 `audited/fla.py` 的任务路径、setup 和用例数；默认仍是 FLA 9 项。bridge 数量由原 bundle 决定；worker 接收经绑定的原 setup |
| Agent、工具和隔离 | 复用 AuditedTerminus2、native export、Terminus 兼容层及网络守卫；只将新 task_id 加入已有预算身份白名单 |
| 对照与正文要求 | 复用公共两组 pilot；同一 runtime-note 在两组生效，有相关 Skill 时必须读完整正文。没有复用历史单组 required_read 脚本 |
| 预算账本／执行门禁 | 复用持久 ledger、冻结检查；新任务额外核验本次批准的生成 ID、下游 ID、配置哈希、批准证据和质量审核哈希；当前均阻断 |
| 汇总与差分归因 | 复用 pilot analyze 和上一任务已实现的 attribution CLI；新增本题空审核 spec，不能自动生成规则语义结论 |
| 操作辅助 | `scripts/sgb/sanctuary002.py` 提供 audit、acceptance、quality、authorization、history-start/check、report；Windows 自动转到已有 Linux 控制环境，解决 resource 等平台依赖 |

未创建新 Agent 循环、Oracle、通用安装器或冻结器，未改 Anything2Skill 核心算法。公共 FLA 评分的少量改动必须通过其原 9 项正反例回归；历史产物保留原字节。

本轮还实测了固定 Agent 镜像：Python 3.13.9，未安装 NumPy；该题可用标准库实现，runtime-note 已据实说明。候选评分 worker 则按发布 bundle 执行含 NumPy 的原 setup，并按原 Oracle 规范化 NumPy 标量与 tuple 后传送 JSON。原任务每用例 120 秒；复用隔离执行器的操作性单进程上限为 10 秒、可信 pytest 上限 30 秒。超时归为运行未完成，不伪装为普通断言失败；需要更长预算应另审运行配置。

## 5. 零模型验收与剩余门槛

已验证的容器：`harbor-p0-control-20261018`。复用 pinned Linux/amd64 Agent 镜像 `sha256:c928e232c35008c42b22727ecd2fe39ed79fe9cb36ebddca669daef309d6b4e4`、scorer 镜像 `sha256:b1c9205374a4ac830bef05b2715185845097c3457ab5f216d437381735c9c1c9`。这是本地固定运行环境，不冒称发布中未固定 digest 的 `light` 镜像。

`results/sgb/audits/task003-sanctuary-zero-20261026-001/acceptance.json`：正例 8/8；错误目标数 1/8；错误触发标记 1/8；错误最后回合标记 3/8；四项均匹配预期。各评分保留 candidate/scorer network 报告、命令、提交哈希、envelope、原 JUnit 和 bridge 收据。网络／挂载探针为受控工程动作，不能计为 Agent 自主读取。

最终单元／回归日志、历史保护和代码身份见 `results/sgb/audits/task003-clean-20261026-001/validation.json`。**实际生成后的 native 两组 prepare 仍待执行**：它依赖真实、工程完整且已完成人工质量记录的生成包（语义错误/遗漏/不确定不自动排除）。本轮没有伪造生成包来宣称该步已通过。

预算文件 `data/manifests/sgb/gates/t-febd929cffec.json` 当前 BLOCKED。提案：一次生成，现配置上限 150 HTTP／450000 观测总 token；一次两组下游，每组最多 6 HTTP、总共 12，每组输入总预留上限 100000、每次输出上限 2048、无自动重试。**这些是配置上限，不是授权余额。** 上游 token 阈值按响应后观测，不是预付费额度或绝对账单封顶；HTTP 次数是请求前门禁。未授权恢复、第二次生成、额外重复或预算扩张。

下一步是审核本手册并批准明确执行额度。批准后才可按阶段 3 开始真实生成；质量审核完成且下游额度获批后，才可 prepare 并运行这一对条件。环境异常和预算停止保留为未完成，不转写成普通任务失败。

## 6. 语义门禁与完成状态修复

本节更正原手册和 Task003 实现中的选择性门禁，不改变上面的任务身份、原 Oracle、源文和历史验收记录。

- check_review 现在检查真实审核者、任务/运行身份、目标规则覆盖及证据可信性；允许 correct、incorrect 和 uncertain。确认遗漏复用 incorrect + rule_omission，不要求不存在的最终正文锚点，但须提供有哈希绑定的检查范围/最终包审查报告。unreviewed 或引用不可信仍阻断正式执行。
- 工程有效且有语义缺陷的 CleanSkill 可以冻结，并在真实预算批准后测量下游；无可用产物、不安全或身份/哈希损坏仍停止。不修 Anything2Skill 核心，不造 Skill，不人工修好后仍标成原始 Clean。
- 最终报告 schema_version=2 分别记录 experiment_execution_status、skill_usage_status、每组 task_success、attribution_status，以及独立 comparability。已结束并有效评分的执行不因未读正文、任务失败或规则证据不足改成未完成。
- 七阶段名称齐全但证据 unknown 仍是归因证据不足。正文进入请求不等于理解、遵循或因果成立；继续保留 observed/inferred/hypothesis/intervention_supported，只有经受控干预且满足原差分验证规则才可提升为 intervention_supported。
- profile、审核、分析或归因文件缺失时尽可能给出明确缺失说明；错误哈希、身份错连和伪造记录仍拒绝。没有有效对照不能借其他历史运行拼接。

本次修复只运行确定性测试，未调用模型或启动 Agent；实际 gate 和授权均未调整。新回归与保护证据见 `results/sgb/audits/task003-semantics-fix-20261026-001/validation.json`。正式生成、真实包 native prepare 和正式 Agent 两组仍需原有独立授权与工程验收。
