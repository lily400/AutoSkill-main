# Task003 Sanctuary002：语义门禁与执行状态修复验收

本轮已修复实际 Python 实现及两份 Task003 文档；未启动正式实验。修复前工作树为空，当前调用链与先前定向审计一致。修复仅涉及下列六个文件，未重构公共框架。

## 修改范围及行为

| 文件/函数 | 修复前 | 修复后 |
|---|---|---|
| `downstream_eval/sgb/task_adapters/audited/sanctuary002.py::check_review` | 将所有目标规则为 correct 作为必要条件；错误/不确定也被当作未完成 | 校验审核是否完成、真实 reviewer、精确 case/condition/run、目标规则完整覆盖、来源/实体/行号/哈希；保留 correct/incorrect/uncertain 原值 |
| 同文件 `review_findings` | 无独立语义结果展示 | 保留原始判定和错误类型；确认遗漏仅展示为 omitted，仍以现有 schema 的 incorrect + rule_omission 存储 |
| 同文件 `check_authorization` / `paid_batch` | 下游批准经 check_review 间接强制所有规则 correct | 仍绑定审核文件实际哈希、配置、批准来源、预算及精确任务运行；不再否决已完成的语义缺陷审核。补充 generation case/condition/repeat 精确绑定 |
| `scripts/sgb/sanctuary002.py::quality` | 返回 PASS，易被误解为内容正确 | 返回 review_status=reviewed、原始 semantic_findings 及审核哈希 |
| 同文件 `baseline_report` / report CLI | COMPLETE 同时依赖 ledger、可比性、七阶段名称、目标正文动作前暴露及完整正文读入；缺辅助文件直接失败 | schema_version=2，执行、使用、功能成败、归因、比较资格分别记录；缺辅助材料尽可能输出真实部分报告，身份/哈希矛盾仍拒绝 |
| `tests/test_sgb_sanctuary002.py` | 包含“错误追加必须阻断”等错误业务断言 | 42 项定向测试，使用临时夹具和真实校验函数；改正旧断言，覆盖完整性、缺失材料与四状态独立性 |
| `tests/test_skill_freeze.py` | 五项原冻结回归 | 保留原五项，增加空活动注册、生成失败、不安全包三项拒绝测试；冻结实现不变 |
| `docs/sgb/task003-clean-runbook.md`、`task003-clean-admission.md` | 将正确、读取及归因条件混入执行完成标准 | 同步新状态、已完成但存在缺陷的审核、遗漏证据格式、部分报告、授权停止点；原任务/模型/预算提案不变 |

遗漏没有可定位的最终正文，不要求伪造锚点。必须保留来源规则及检查理由，并使用现有 `provenance.file/sha256` 绑定人工检查报告，说明已检查的全部最终包及哈希、范围和遗漏证据。机器校验结构、引用与哈希；报告是否充分支持语义判断仍由审核者负责，不把关键词匹配当作语义证明。uncertain 可以没有确定正文锚点，但必须有可信来源及非空说明。unreviewed、删除目标记录、不可信引用仍阻断正式执行。

## 输出状态及验证场景

| 场景 | experiment_execution_status | task_success | skill_usage / attribution |
|---|---|---|---|
| 两组有结束记录、绑定提交及有效原 Oracle 评分，未读正文 | completed | 保留真实 true/false | 使用状态独立；机制证据不足不抹去执行 |
| 两组评分完整，部分规则阶段缺证据 | completed | 原值 | insufficient_evidence 或 pending_review |
| 七阶段名称齐全但全部 unknown | completed | 原值 | insufficient_evidence，不能因名称齐全升级 |
| 正文进入请求但两组都失败 | completed | false/false | 读入不证明理解/遵循，不自动添加因果声明 |
| 两组完成但模型不同 | completed | 原值 | comparability=ineligible，attribution=not_comparable，差分 unresolved |
| 缺某组执行/评分 | partial | 缺有效评分的一组为 null | 不借其他历史运行配对 |
| 没有启动记录 | not_started | null/null | 不补造失败分数 |
| 原 Oracle 有效评分存在，但 native 结束标记缺失 | partial | 已有效评分可保留 true/false | 不将已有评分抹去，也不宣称完整执行 |
| profile/review/analysis/spec/export 缺失 | 尽可能依据剩余执行事实 | 只保留有效评分 | 记录缺失；报告允许部分交付 |
| 候选/来源/冻结证据哈希冲突，错误任务/Oracle/运行引用 | 拒绝生成报告 | 不转写为普通失败 | 完整性异常不能通过 partial 降级掩盖 |

`comparability` 继续独立使用 eligible/ineligible/unknown。已审核归因不等于因果成立；保留原 observed/inferred/hypothesis/intervention_supported 契约，只有满足原受控干预差分验证的声明可使用 intervention_supported。原始观测中，正文在动作后才出现、受控探针读取、只有索引、日志缺失均分别保留。

报告不再输出含义混杂的顶层 COMPLETE；消费者应读取 schema_version=2 的各字段。历史报告未迁移或覆盖。报告仍拒绝覆盖现有输出目录；轮询使用 status，不能为刷新报告重跑实验。

## 测试命令、真实结果与限制

最终验收采用随报告保存的 `reproduce/zero_model_regression.py`。它只调用 unittest，禁止 socket connect/DNS；fixture=True 的临时上游目录只有源码形状占位文件，不含可执行生成逻辑，不作为正式 Skill。测试中的批准、ledger 和提交只属于临时夹具；真实 paid backend 被替换为 spy，SDK 测试使用 MockTransport。正式生成、Agent、正式 ledger 均未执行。

本轮实际命令在 PowerShell 中执行如下；脚本原样复制到本报告的 reproduce 目录，原始 JSON 日志保存在 logs 中。

```powershell
$Task003Fix = 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\task003-fix'
Get-Content -LiteralPath (Join-Path $Task003Fix 'zero_model_regression.py') -Raw | docker exec -i --env PYTHONDONTWRITEBYTECODE=1 --env LITELLM_LOCAL_MODEL_COST_MAP=True harbor-p0-control-20261018 /opt/harbor-venv/bin/python -B - --platform linux | Set-Content -LiteralPath (Join-Path $Task003Fix 'release-linux.json') -Encoding UTF8
if ($LASTEXITCODE -ne 0) { throw 'Release Linux regression failed; preserve the log' }
& D:\anoconda1\python.exe -B (Join-Path $Task003Fix 'zero_model_regression.py') --platform windows | Set-Content -LiteralPath (Join-Path $Task003Fix 'release-windows.json') -Encoding UTF8
if ($LASTEXITCODE -ne 0) { throw 'Release Windows regression failed; preserve the log' }
```

要从交付副本复跑，可将 `$Task003Fix` 设为本报告目录下的 `reproduce`。不要因此增加实验预算或调用模型。脚本的 selector 列表及以下日志给出每项实际命令对应的 unittest discovery 范围。

| 环境/selector | 测试数 | 最终结果 |
|---|---:|---|
| Linux `test_sgb_sanctuary002.py` | 42 | 全通过 |
| Linux `test_pilot_workflow.py` | 11 | 全通过 |
| Linux `test_sgb_runner.py` | 22 | 全通过 |
| Linux `test_request_budget.py` | 11 | 全通过 |
| Linux `test_network_isolation.py` | 10 | 全通过 |
| Linux `test_sgb_task_contract.py` | 12 | 全通过 |
| Linux `test_framework.Framework.test_new_run_evaluation_contract` | 1 | 通过 |
| Windows `test_attribution.py`，含完整 HistoricalAttribution | 27 | 全通过 |
| Windows `test_skill_usage.py` | 9 | 全通过 |
| Windows `test_skill_freeze.py` | 8 | 全通过 |
| 合计 | 153 | 0 失败、0 错误、0 跳过 |

控制环境为现有 `harbor-p0-control-20261018` / `harbor-p0-control:2de4605-uv0824-py3139`，Python 3.13.9；原生环境为 `D:\anoconda1\python.exe` 3.13.9。未新建实验容器或运行实验评分重放。

其他真实执行记录也保留，不能只挑最终绿色结果：

- 修复前红测试：2 个测试、3 个子场景错误，复现 incorrect/uncertain 被阻断及缺分析文件无法报告。这是预期失败，不计为通过。
- 开发中 31 项、40 项，以及首次 release 42 项定向运行均为零失败/错误；未将重复运行累计进上述 153 项。
- 一次原生 Windows `test_network_isolation.py` 为 10 项中 1 失败：本轮统一网络拦截器阻断了 asyncio proactor 创建本地 socketpair，在抵达待测 native admission 分支前报错。该失败日志保留为 `logs/windows-regression.json`，没有删除测试或更改产品网络限制；相同网络模块在 Linux 全部通过，最终套件也在 Linux 执行。
- 本轮完整历史归因在原生 Windows 路径完整通过，没有中止。先前只读审计的 Linux/9P 历史遍历中止不计为本轮通过证据。
- 未运行全仓库所有测试；其他基准、真实模型连通、真实生成、真实包 native prepare/网络内核探针及正式两组 Agent 不属于本轮确定性验收，未执行。本次网络测试验证拒绝分支/控制逻辑，不冒充真实包 prepare 已通过。

静态检查命令：

```powershell
& 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\task003-fix\static_checks.ps1'
& D:\anoconda1\python.exe -B 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\task003-fix\verify_integrity.py'
git -C D:\AS\AutoSkill-main diff --check
git -C D:\AS\AutoSkill-main diff --stat
```

四个修改后 Python 文件 AST 解析通过；手册 25 个 PowerShell 块只做解析、零语法错误，未执行其中的实验命令。`git diff --check` 通过；Git 给出既有 autocrlf 的 LF/CRLF 提示，非 whitespace 错误。完整 diff 保存在 `changes.patch`，初始工作树为空，未 commit/push。

## 保护核验

`integrity.json` 记录修改前 20,376 个文件哈希与当前比较：只有计划内六个文件变化，19,151 个已有 runs/results/evaluations 文件零改动。新建本审计目录，不覆盖旧审计目录。源文和原 Oracle 身份由定向测试实际验证，源 SHA-256 保持 `7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c`，原 Oracle 为 `57eb8902f1d0a5601bef71f1affaa944c2b946427c0e2e40e9a58c5d48f437eb`。

以下实现未修改且有对应回归覆盖：`evaluation-validate`/`validate_evaluation`、`freeze_generation`、通用 `audit_pair`/`export_report`、公共 pilot/runner、Skill usage、预算模块 `Ledger.finish`。网络隔离实现、配置、批准文件、正式 ledger、源文、测试数据和历史产物哈希均未改变。新代码仍拒绝审核/批准/配置/来源/提交哈希矛盾，未把“无可用 Skill”或不安全包伪装为 CleanSkill。

实际 gate `data/manifests/sgb/gates/t-febd929cffec.json` 与修复前哈希相同，生成与下游均为 BLOCKED。150 HTTP/450000 观测 token、6+6 HTTP 等仍只是原配置提案，不是已获授权额度。

## 当前可执行性与剩余事项

本次定向修复及适用确定性回归已完成，未发现阻碍本次交付的未修复失败。Sanctuary002 还不能被称为“正式 Clean 实验已验收可开跑”：真实生成包尚不存在，真实包 native prepare 仍待执行，正式预算未授权。

后续需要分别批准一次精确配置的生成及一对下游试验。生成后先完成真实质量记录、工程有效的冻结、精确审核哈希绑定和原有 native prepare 验收，再按手册执行。语义缺陷保留测量，不先修好正文或伪造包。新增重复、干预或退化实验均不在本轮授权内。

审核本修复后再推进上述事项。本轮到此停止。
