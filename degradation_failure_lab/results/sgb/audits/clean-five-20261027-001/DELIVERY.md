**最终执行结果已完成：10题/20条正式Agent结果。** 见 [EXECUTION.md](EXECUTION.md)。Scrapy050已按用户批准的v2观察协议恢复准入，原7/8保留；下文隔离说明为已解决的历史发现。

# 五任务审核、配置与执行交付

更新日期：2026-10-28。原五项已全部完成审核：三项准入，两项排除并替换。替换后五个任务位均为技术 READY，配置已写好。

审核与适配阶段没有付费模型调用。用户随后已授权先进行这五项的上游 A2S 提取；实际提取结果将单独写入本目录的 upstream-results.json，不与零模型 fixture 混淆。下游须等待 Capacity006 窗口正式配对完成后再启动。

Capacity006 协调窗口内已停写共享代码与配置并核验无漂移；该窗口现已结束，e06f003 已完成并审计。结束后仅因 Referee 传输故障更新其生成身份和有界重提取配置；未修改任何已完成实验或 Skill。

## 2026-10-28 实际执行进度

五题上游全部完成并原样冻结：Pydantic001=17，Scrapy050=6，Pydantic004=17，Reviews CSV=64，Referee=7。含失败批次共632次HTTP、2,052,378个已观测tokens，1次传输失败的服务端计费/未返回tokens未知。详见 [实际用量与哈希](upstream-results.json)。

Reviews 的通用检查保留 PARTIAL；64个最终包与最终注册表一致的补充核验 PASS，变化的1个正文有上游自动去重合并记录，见 [最终注册表核验](upstream/r07g001/final-registry-verification.json)。这不等同于内容质量通过。Referee 首批 r09g001 因 IncompleteRead 失败，8个部分包不纳入正式统计；r09g002 用新空库重新提取并通过核验，未改源文/算法。重提取限制100请求/30万observed tokens，两批实际合计66次、243474 tokens，低于原单题上限；见 [故障与预算记录](referee-infrastructure-retry.json)。

Capacity006 完成条件已满足。五题下游按原授权逐题各进行一组 NoSkill/CleanSkill；每臂6次、配对12次HTTP。最新评分另存执行报告，不把工程 fixture 算作真实实验。


**真实运行后的准入更正：** Scrapy050 两臂原始7/8均保留，但原 Verifier 对合法 CrawlSpider 实现的注入 parse 计数失效；独立零模型诊断显示两臂都实际抓取4页、深度3。该边界在初审中漏检，现已将该题从正式统计隔离，不将原分数强改为8/8。证据见 [隔离决定](scrapy050-quarantine.json) 和 [诊断](diagnostics/scrapy050-callback/results.json)。该隔离决定随后经用户批准的v2观察修正解决，详见scrapy050-resolution.json；原隔离记录和7/8分数不删除。

## 任务结论

| 原任务 | 审核结论 | 正式任务位 / 配置 |
|---|---|---|
| pydantic-task-001 | READY | 16项发布断言；复用现有 Pydantic 正反例，新增隔离对象/日志观察；保留日志为候选自报的限制。 |
| scrapy-task-050 | READY，批准后的观察v2 | 8项发布断言；固定可实际爬取的离线依赖并运行有界 loopback 探针。原测试替换 parse，所以覆盖配置与报告语义，不能声称独立验证提交的链接遍历实现。 |
| pydantic-task-004 | READY | 20项发布断言；与001共用对象观察家族，覆盖 dict、模型实例、嵌套验证、序列化和错误。 |
| ops_pack_gate_a_egress_veto_002 | REJECTED | 原文有局部规则，但缺少参考实现强制的全局 BLOCK 优先级、同分钟重叠抽象及固定重排步长；参考还忽略题面 requests。补这些会提供目标策略。替换为 reviews_csv_conformance_validator_007。 |
| shark_warranty_safety_gate_001 | REJECTED | 原文充电温度单位矛盾，题面未规定精确 issue 编码/顺序，参考自行选择解释和天数换算；不能靠配置保证原始精确比较公平。替换为 referee_attempt_decision_router_009。 |

| 正式接入任务 | case | A2S run | 下游配对 ID |
|---|---|---|---|
| pydantic-task-001 | case001_pyd | p01g001 | p01f001 |
| scrapy-task-050 | case050_scrapy | s50g001 | s50f001 |
| pydantic-task-004 | case004_pyd | p04g001 | p04f001 |
| reviews_csv_conformance_validator_007 | case103_reviews | r07g001 | r07f001 |
| referee_attempt_decision_router_009 | case104_referee | r09g002 | r09f001 |

[pydantic-task-001 配置](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/tasks/sgb/pydantic-task-001.json>)  
[scrapy-task-050 配置](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/tasks/sgb/scrapy-task-050.json>)  
[pydantic-task-004 配置](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/tasks/sgb/pydantic-task-004.json>)  
[reviews_csv_conformance_validator_007 配置](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/tasks/sgb/reviews_csv_conformance_validator_007.json>)  
[referee_attempt_decision_router_009 配置](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/tasks/sgb/referee_attempt_decision_router_009.json>)  

[统一十任务队列](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/sgb/clean10.json>)；[逐项审核与排除证据](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/admission.json>)。

## 规则与来源核对

- Pydantic001：validators.md 652–668行明确 Annotated 中 before/wrap 从右到左、after 从左到右。题面本身已披露变换和部分顺序要求，因此它是 API 使用与排序校准任务，不应将其解释成隐藏领域常量任务。
- Pydantic004：unions.md 337–356行要求 callable discriminator 处理字典及模型实例；其余 Tag、嵌套联合和 TypeAdapter 来源均保留在两个原始文档中。题面、测试和文档之间未发现需要注入答案才能解决的冲突。
- Scrapy050：depth.md 100行的条件检查及 settings.md 481–488行明确零表示不限制深度。原发布 eval.py 104–201行明确探针继承提交类、替换 parse；本轮保留该范围，不改原测试来扩大覆盖。
- Reviews CSV：context.md 304–328行提供必需列、大小写、最小行数和 ERROR 模板。题面只承诺简短成功消息，原比较器却精确匹配成功句，因此在两臂共同 runtime-note 中补充无规则常量的成功消息/诊断格式；未给出列清单、合法值或行数阈值。
- Referee Router：context.md 112–116、138–151、313–316行提供故障、卡片类别与路由、更新规则。两臂共同说明仅约定多类别时按原卡片列出顺序选首个适用类别、无专门类别时使用原卡片回退类别，没有提供故障判定答案。
- ops 的缺口对应其 context.md 143–146、184、995–999行与 solution_code 的 BLOCK_PRIORITY/同分钟逻辑；shark 温度冲突位于 context.md 206–207行，其他真实电池/维护规则仍保留。二者文档与历史未修写。

两个替代任务属于保留原断言、显式澄清输出接口的实验协议。它们的结果适用于本实验内部两臂比较，不能冒充未经适配的官方 SGB 默认环境成绩。源文档全部保持原始字节，A2S 输入只包含登记的 Markdown，不包含 task.json、solution_code、测试或本轮说明。

## 实际工程修改

新增内容主要是五套任务资产与case/config/fixture/gate；资产中的题面和Oracle是逐字校验后复制的文件。没有开发第二套Agent、Harbor、SkillBank或预算系统。

1. 新增 code_task.py、code_worker.py、code_bridge.py：在既有原生 Agent/提交导出/独立评分上，为两个Pydantic任务和Scrapy050提供有限对象观察。候选容器看不到Oracle、期望值或可信评分输出；可信容器不导入候选代码。
2. 延伸现有 downstream_authorization 与 authorize_downstream，使同一精确授权机制支持 JSON 和对象两类配置；同样冻结task/config/run/条件/6次每臂与12次总限额。既有授权记录不覆盖，账本不重置。
3. 共用 FLA 评分桥仅修复 setup_code 末尾空白比较；没有改规则。Pydantic001旧工程演示仍校验固定原资产，不因正式适配登记而失效。
4. 新增薄包装 Invoke-CleanTask.ps1，按队列调用现有 authorize_generation、lab.py、authorize_downstream、Invoke-Pilot.ps1 和 cohort；不重新实现执行过程。不带 -Approve 时只做相应授权预览；有既存生成/实验身份时拒绝重跑。
5. 更新十任务索引，显式记录两个替换；将当前实际 m01f004 配对纳入索引，先前基础设施中止单独保留。Capacity 的已完成 e06r002 生成沿用原样产物，不再提取。
6. 新增可审阅的 clean_five.json 提取预算配置，模型和A2S pipeline参数不变。上游授权仍绑定配置SHA，未授权时BLOCKED；执行预算没有因“技术READY”自动开放。

[完整修改文件/哈希](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/changes.json>)；[逐行差异](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/changes.diff>)；[共享停写窗口基线](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/shared-readonly-window.json>)。

## 零模型验证

- 相关去重单元回归122项通过；Linux专有 resource 评分组件在控制容器验证，Windows相应项不伪装通过。
- 五任务原始正反例评分桥验收10项通过预期：Pydantic001 16/16与14/16；Pydantic004 20/20与18/20；Scrapy050 8/8与6/8；Reviews CSV 7/7与3/7；Referee Router 8/8与7/8。这里的数字是fixture断言数，不是Agent任务成功率。
- 五任务两臂原生Harbor零模型传输预检共10项最终通过，验证正文读取、导出和评分；借用了一个历史包仅测试传输，记录 real_agent_outcome=false，不声称已得到各任务真实CleanSkill。一项初始预检因egress侧车exit137失败，保留原记录，零模型复检通过，没有发送模型请求。
- 三个对象任务六组正反例，其原始pytest与观察桥的测试数和失败项一致；另增加合法Pydantic子类、第二次finding返回不一致结果两类边界，共8组原始/桥接对照一致。后者正确保留第一次与第二次调用差异，避免错误放行。
- Scrapy原镜像的2.13.0 + Twisted26.4.0实际无法启动爬虫。仅为050构建新镜像，固定Twisted25.5.0，记录PyPI wheel SHA和镜像ID，离线构建、不修原测试、不改其他任务环境。

[测试汇总](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/test-summary.json>)；[最终评分桥验收](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/release-scoring-acceptance.json>)；[原生传输验收](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/native-acceptance.json>)；[原始/桥接对照](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/direct-fixture-check/results.json>)；[新增边界对照](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/edge-cases/results.json>)；[Scrapy运行环境构建日志](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/scrapy-runtime-build.log>)；
Twisted固定版本的官方发布信息见 [Twisted releases](https://github.com/twisted/twisted/releases)；本实验是否可用以本地真实爬取验收为准。

## 完整性与统计状态

A2S上游166个登记文件零漂移。初始保护清单25,677项中8项发生变化，全部位于当时已在运行的e06r002：本轮快照时间为2026-10-27 14:20 UTC，该运行14:22 UTC完成，其最终1,645文件清单全部匹配。其余保护产物未变；本轮没有发起或改写该Capacity生成。

旧版本按保存的before字节及既有changes.diff恢复，只有SHA精确匹配历史执行清单才登记别名，不推测历史实现，也不用别名授权执行。原始文件没有覆盖。

当前技术队列为10 READY；在本轮新模型执行前，已有4组配对通过协议与追溯核验：Sanctuary sn3e001、Scrapy024 c24f002、Scrapy041 c41f002、monitoring m01f004。本轮新五项真实配对尚未启动，工程fixture不进入成功率。Capacity006由另一窗口完成；本聊天等待其实际两臂终态后再启动下游。

[完整性记录](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/clean-five-20261027-001/integrity.json>)；[正式队列核验](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/clean-five-release-20261027-001/summary.json>)。

## 执行与授权

每项正常路径为：源文档与门禁核验 → A2S真实生成 → 原样Skill冻结 → 最终零模型prepare → Terminus-2两臂各一次 → 独立原Oracle → 分析和十任务汇总。准备时会再次核验真实包、全部索引和Token预算；本轮借包传输测试不能替代这个门禁。

每个新任务的提取上限为600次HTTP、observed-total停止阈值2,400,000；五项合计HTTP上限3,000、observed-total阈值合计12,000,000。Token是响应后观察阈值，最后一个响应可越界，不是严格硬上限。上限旨在避免长文档像已有Capacity提取那样在小额度下反复中断，不代表预计都会用满。

五个下游配对合计最多60次HTTP；同一clean-pair-v1，每臂6次、输入累计100k、单请求输出2048、重试0。没有自动追加预算或重跑；金额因账户实际单价未知不虚构估价。

用户2026-10-28已授权先进行上述五项上游提取。共享窗口内只写对应新gate和各自run产物，已核对它们不属于Capacity冻结清单。下游等待Capacity正式配对完成。手动执行的准确命令见同目录 RUN.md；不要在已有运行上重复执行generate/evaluate。

尚未验证的部分是这五项真实生成产物的最终质量、真实Skill总索引是否适配固定输入预算以及实际下游模型结果。预算、Skill加载和Oracle门禁会在正式prepare/运行时继续检查；不会删改Skill、扩大预算或修改原测试来提高通过率。
