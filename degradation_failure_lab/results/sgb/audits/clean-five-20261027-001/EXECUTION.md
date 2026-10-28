# Clean 十任务执行与失败诊断

完成时间：2026-10-28T08:39:06.301494+00:00。五个新增任务已完成上游和两臂各一次；另一窗口 Capacity006 完成后才启动本窗口下游。累计10个不同任务、20条正式Agent结果，10组配对均eligible。

**主结果：NoSkill 3/10，CleanSkill 4/10。** 这是逐题二元成功率；Clean赢2题、NoSkill赢1题、平7题。每题只有一次配对，不能推断稳定提升或退化效果。本阶段未做文档退化。

Scrapy050使用用户明确批准的response_received-v2观察修正；原始两臂7/8仍保留，修正后两臂8/8。修正只影响观测，不改原测试、提交、Skill或模型轨迹，新增模型请求0。

## 本窗口五题

| 任务 | A2S身份 | 最终Skill | NoSkill断言 | CleanSkill断言 | 整题结果N/C | 下游HTTP |
|---|---|---:|---:|---:|---|---:|
| pydantic-task-001 | p01g001 | 17 | 5/16 | 7/16 | 失败/失败 | 7 |
| scrapy-task-050 | s50g001 | 6 | 8/8 | 8/8 | 通过/通过 | 6 |
| pydantic-task-004 | p04g001 | 17 | 20/20 | 20/20 | 通过/通过 | 5 |
| reviews_csv_conformance_validator_007 | r07g001 | 64 | 0/7 | 1/7 | 失败/失败 | 10 |
| referee_attempt_decision_router_009 | r09g002 | 7 | 0/8 | 0/8 | 失败/失败 | 11 |

注：Scrapy050该表为批准后的修正观测；原始7/8见原执行目录。禁止把不同任务断言数合并成任务成功率。

## 十任务统一统计

| 任务 | NoSkill | CleanSkill |
|---|---:|---:|
| sanctuary_endgame_scheduler_002 | 0 | 1 |
| scrapy-task-024 | 0 | 1 |
| scrapy-task-041 | 1 | 0 |
| monitoring_gap_brief_classifier_001 | 0 | 0 |
| capacity_aware_edge_admission_controller_006 | 0 | 0 |
| pydantic-task-001 | 0 | 0 |
| scrapy-task-050 | 1 | 1 |
| pydantic-task-004 | 1 | 1 |
| reviews_csv_conformance_validator_007 | 0 | 0 |
| referee_attempt_decision_router_009 | 0 | 0 |

正式汇总：[summary.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/clean-five-final-20261028-004/summary.json)。Sanctuary、Scrapy024、Scrapy041、Monitoring和Capacity沿用已核验历史配对；其余五组为本轮真实新执行。早期Sanctuary缺少failure_kind字段，保留historical_unclassified，不回填虚构分类。

## 真实用量

- 上游含失败批次：632次HTTP，2,052,378个已观测tokens。失败请求1次，其未返回tokens及服务端计费未知。
- 下游五组：39次HTTP，输入197,981、输出15,946 tokens。缓存131,456属于输入子集，未重复累计。
- 原两臂账本全部DONE，39次HTTP均有响应，本轮下游无基础设施失败。Reviews与Referee的NoSkill到达6回合上限仍未确认完成，应归budget_exhausted；历史Monitoring的CleanSkill同样如此，Capacity的NoSkill在第6回合只提出首次完成、尚未双确认，也归budget_exhausted。四条均保留原task_failure记录并在正式总表派生修正，不重跑模型。单纯用满6次、但已经双确认完成的情况不会误判为耗尽。
- Referee首批r09g001因IncompleteRead失败，部分8包不进入正式统计。r09g002在新空库完成，实际30次/115367tokens；两批累计66次/243474已观测tokens，低于原单题600次/240万阈值。新批次100次/30万有界限制未触发。
- 用户批准050修正后的所有动作都是零模型评分、回归、索引和诊断，没有新增生成或Agent调用。API未给出金额，不虚构人民币或美元费用。

## Skill链路与失败模式

| 任务 | 安装/索引 | 实际文件读取 | 完整正文进入成功请求 |
|---|---:|---:|---:|
| pydantic-task-001 | 17/17 | 3 | 3 |
| scrapy-task-050 | 6/6 | 2 | 2 |
| pydantic-task-004 | 17/17 | 2 | 2 |
| reviews_csv_conformance_validator_007 | 64/64 | 2 | 2 |
| referee_attempt_decision_router_009 | 7/7 | 5 | 1 |

NoSkill对应各项均0。安装、读取或正文交付不能证明Agent实际遵循规则。

- **筛选/窗口遗漏：** Scrapy050的depth.md未产草稿，六个最终包均未出现DEPTH_LIMIT/DEPTH_PRIORITY/DEPTH_STATS_VERBOSE/DepthMiddleware。Pydantic004独立TypeAdapter文档也未产草稿，但联合类型文档保留了TypeAdapter相关Skill，不能声称该知识完全丢失。
- **固定输出模板在窗口阶段未保留：** Reviews源文含完整ERROR模板，两个精确关键句在窗口、支持引文、草稿和冻结包中均未检出。Clean读取的CSV包保留了六列、允许值和20行下限，代码采用这些知识，但错误响应模板不符。此处记录可观察断点，不裁定唯一因果来源。详见diagnostics/reviews007-preservation/results.json。
- **执行/推理错误：** Pydantic001 NoSkill向Pydantic实例直接赋未声明日志属性；Clean用object.__setattr__规避该错误，但before再乘2、after再乘2造成4*x+10，且校验顺序仍错。新增通过两项断言，但两臂整题都失败。
- **输出字面保真与规则使用：** Referee两臂0/8。NoSkill把接收者写为Recorder；Clean改为源文要求的Tournament Director，但理由类别使用小写而非要求的原文字符串，另有优先级/脚部动作处理问题。Clean读取5包，完整正文仅1包进入成功请求；不能把0/8等同于没有加载或完全没有采用知识。
- **注册合并不等于人工补写：** Reviews 64包的通用verify保留PARTIAL（与编译前正文/支持集合比较），补充核验对最终注册快照、版本、引文和冻结哈希全部PASS；变化的1个正文可追溯至上游重复项合并。见upstream/r07g001/final-registry-verification.json。
- **评分缺陷：** Scrapy050原parse替换方案对合法CrawlSpider给7/8，却给不递归Spider8/8。批准后的观察器保留提交回调，按真实response_received计数，两臂4页/深度3；深度1和不递归反例分别2页/深度1、1页/深度0，被修正评分拒绝。

## 追溯与验证

- 所有五组各21项控制核验一致，完整报告位于results/sgb/attributions/clean-five-<配对ID>/。正式总表10组protocol VERIFIED、comparability eligible、生成身份匹配。
- 评分与分类回归：Linux基线15/15，评分修正后19/19，最终25/25；通用runner最终24/24；含原分数/请求用量保留、证据篡改拒绝、候选错绑拒绝、用户授权必需。Windows基线14项通过、1项因缺resource模块失败；未用平台失败修改研究代码。
- 旧保护文件25,677项仅8项与初始快照不同，均为快照时另一窗口正在完成的e06r002产物；其最终清单已核验。A2S上游166个登记文件零漂移。六批生成的原始artifact_manifest全部通过，新执行全量哈希已封存execution-seal.json。
- 旧版cohort.py在修改前已归档，历史哈希别名登记；没有回写原实验、重置预算、修改Skill或原始SGB测试。

## 主要文件

- upstream-results.json：生成身份、来源冻结、哈希与实际用量。
- downstream-results.json：五组原始评分、Skill使用、控制审计、两臂账本和050修正并列。
- execution-seal.json：执行与历史保护的哈希封存。
- final-cohort-reference.json：正式十题汇总及配置SHA；最终为clean-five-final-20261028-004。
- scrapy050-resolution.json：用户批准与原始/修正分数关联。
- results/sgb/rescores/s50f001-callback-signals-v2/：正式零模型重评分、观察器、原断言JUnit、审批记录和完整清单。
- replacement-screen/pydantic005/：未采用的零模型备选筛查，不计入正式任务，也未启动付费模型。

## 最终代码与统计修正

本次执行后的功能修改为downstream_eval/sgb/cohort.py（显式重评分索引与历史分类派生）、downstream_eval/scoring/results.py（Terminus双确认/回合耗尽识别）、downstream_eval/sgb/runner.py（使用冻结profile传入上限）、downstream_eval/sgb/task_adapters/audited/code_task.py（配置化的批准观察器及哈希门禁）、tests/test_clean_cohort.py（必要回归）、Scrapy050绑定配置、clean10与历史索引，以及由既有register_task维护的tasks.jsonl和configs/datasets/sgb.json。Referee有界重提取仅另加预算配置并更新case配置指向；全部文件与前后哈希详见changes.json。未改Agent实现、SkillBank、Harbor、预算系统、源文档或原始SGB测试。

正式分类共4条回合耗尽，其余失败按任务失败或保留早期缺失标签；没有把基础设施故障伪装成Agent失败。原始分数、原始failure_kind、核验依据与修正协议均可分别追踪。

默认通用入口已通过既有register_task注册并锁定批准的v2观察器哈希，纳入freeze_files；旧绑定/旧实现已归档。五任务零模型回归6/6通过；实际默认入口对原CrawlSpider8/8、非递归反例7/8，且拒绝被改动的观察器哈希。原正确/规则反例门禁也维持8/8与6/8。
