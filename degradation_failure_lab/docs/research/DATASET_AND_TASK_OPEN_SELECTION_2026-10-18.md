# 面向退化文档的鲁棒 Agent Skill：开放式数据集与任务选型审计

完成日期：2026-10-18；本轮检索与静态审计覆盖2026-10-17—18。研究对象是文档退化如何影响规则、证据整合与最终技能，随后如何影响任务；不是一般Agent排行榜，也不是本轮设计新生成算法。

## 1. 决策

**首选路线D：ConditionalQA作为自然文档与规则质量主集，Leezekun/SOPBench的固定政策子集作为机制与执行补充。保留原版Anything2Skill，条件性沿用Harbor + Terminus-2。** 两层都须形成实质证据，但不合并成一个总分。阶段一仍先做既有Git工程校准；正式研究层先核SOPBench library的一个2+1组，再扩大来源与任务。

这个推荐替代“默认从CL-bench或SkillGenBench中选主集”的倾向，理由是本轮已经找到：

- ConditionalQA有独立完整文档、可定位的逐题证据、条件答案、明确数据许可及真实共享规则2+1；它更能支撑自然文档中规则遗漏、条件丢失和错误合并的分析。
- SOPBench有可执行工具、约束表达式、初始数据库与动作图；固定政策后能建立规则到动作的映射，较适合检验局部规则错误传播。它的来源是程序导出的规范化SOP，不等于自然长文档，且原Oracle仍需补强。
- CL-bench的用途条款、任务内规则旁路、原生冲突与LLM判分使其不能无条件优先。SkillGenBench虽主题更贴近生成，但其文档子集、多任务关系、源码隔离和部分测试覆盖未满足当前机制研究需要。

**第二推荐：ConditionalQA + AppWorld。** AppWorld的独立状态判分更适合后续跨应用执行泛化，但桥接、来源隔离和protected派生物发布成本较高，分页规则必要性仍未证实，因此不作为最小组合的第一执行层。若SOPBench的Oracle或固定来源子集不能通过后续验收，切换这一组合，不从零造大量业务环境。

没有发现一个已经同时通过“自然复杂文档、完整Evidence–Rule–Action真值、同规则多任务、可靠执行Oracle、无旁路、明确许可、低成本接入”全部条件的数据集。**这是有缺口的明确选择，不是宣称存在完美数据集。**

## 2. 审计范围、证据与交付索引

本轮只检索公开资料、下载材料、读取代码/数据及做结构统计；未运行Agent或正式评测，未调用付费模型，未构造退化数据，未修改Anything2Skill或既有47份Skill。源码中的问题是静态发现，除明确继承上轮的探针结果外，不描述为已执行的攻击或失败。

证据标记：**S**=本轮实际文件及无模型统计；**H**=继承10月15–16日固定版本审计；**P**=作者论文/官方说明；**I**=工程或研究推断；**U**=未验证。事实与推断在正文分别限定。论文任务数、当前发布任务数、测试case数、来源数不互换。

工作目录：`C:/Users/lily/Documents/ChatGPT/回归解决退化文档/`。完整证据包如下：

|交付|文件|
|---|---|
|32项开放发现清单、十方向覆盖、官方论文/代码/下载入口、版本与许可|[开放检索清单](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/open_discovery_catalog.md)|
|先于最终比较制定的G1–G8准入协议|[准入协议](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/selection_protocol.md)|
|CL、ConditionalQA、ProofWriter与ShARC真实样本/源码|[自然规则审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/cl_rules_notes.md)|
|两种SOPBench与RuleArena审计|[SOP与政策审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/policy_workflow_notes.md)|
|AppWorld、UXL、AgentDocsBench及执行资源|[API与执行审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/api_execution_notes.md)|
|SafePyramid、PolicyBench、SkillEvolBench等补充审计|[其他新候选审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/root_candidate_notes.md)|
|原先Runner与Oracle完整审计|[前轮报告](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/degradation_failure_lab/docs/research/DOWNSTREAM_BENCHMARK_AND_ORACLE_OPEN_SELECTION_2026-10-16.md)|

清单中轻审条目明确标L，只承担发现和初筛，不用README代替第二轮审计。版本号、完整SHA、数据下载地址和许可见清单及对应notes。CL代码commit接口未取得，保留文件哈希；SafePyramid三行viewer样本未按revision锁定；这些限制不隐去。

## 3. 统一准入标准与候选矩阵

G1：源文、任务、评价真实可得，固定身份，代码与数据许可分开。G2：生成器可只看独立来源，不看题目、答案、测试或轨迹。G3：来源含可复用条件、步骤、约束而非仅实例事实。G4：判分可复核，标签、结果和副作用覆盖分别审。G5：可建来源—证据—规则—任务关系；2依赖+1对照是机制研究的附加门槛。G6：能控制Clean原文、答案和源码旁路。G7：文档结构/条件复杂度及可恢复信息足以支持研究。G8：保留题义的接入与重复成本可承担。

以下不用主观加权总分。“候选”表示推荐优先验收，不表示已完成运行准入。所有Harbor端到端可用性均U。

|候选|独立来源/生成 G2–G3|证据与共享规则 G5|Oracle G4 / 隔离 G6|研究代表性 G7 / 接入 G8|当前决定|
|---|---|---|---|---|---|
|ConditionalQA|完整自然文档可单独输入S|现成证据/条件；2+1已静态确认S|文本指标公开；漏答分母需包装；条件原文匹配错位S|长文、章节/表格好；文本提交低成本I|自然文档主集候选|
|SOPBench固定政策子集|规范化SOP可独立冻结；合成来源S|约束/动作图/初态；library 2+1 S|strict重放真实动作；空轨迹拒绝与副作用检查有缺口S|适合机制，源域仅7个；工具服务桥接中等I|机制/执行补充首选，须验收|
|AppWorld|独立API文档；应隔离源码/DB S|source/API可映射；2+1为必要性未证实候选|逐题DB预期集合较强；个别同模型更改仍有盲区S|真实仿真执行强，文档偏结构化；桥接/许可成本高|第二执行层|
|RuleArena|真实规则/表格S|Main Plus 2+1静态可定位S|独立数值程序，外部表与隐含排序目标需核|仅3领域来源，通常文本数值；低接入|数值规则备用补充|
|ProofWriter|合成短理论可独立输入S|形式proof与2+1强S|有标签，完整verifier未审；数据许可U|机制清楚，缺自然长文和真实动作|许可澄清后小型诊断|
|CL-bench|部分纯context；部分来源混历史S|同context统计充分；已查组有共享规则但无完整对照S|LLM judge；任务重述规则；clean冲突S；用途边界U|复杂度高，来源治理与Oracle成本高|不作当前主集，待澄清扩展|
|SkillGenBench|有doc/repo，但运行环境源码/答案可见H|doc64题；domain每context一题；cases非任务H|部分弱断言，默认多包不兼容H|一般生成评价可用，当前机制不足|保留比较子集，淘汰默认主集|
|Amazon SOP-Bench|SOP真实公开，任务可分离S|KYB等有多题，需核同规则S|部分工具查label，substring决策比较S|SOP丰富，真状态执行不足|内容备用，淘汰直接执行主集|
|AgentDocsBench|虚构SDK文档含逐题契约/完整实现S|有pagination/retry 2+1候选S|部分强断言，SDK可旁路/改写，覆盖漏项S|短、任务设计共源；薄适配|小型校准备选|
|UXL oneTBB|官方手册可单独取得，版本需冻结S|第二共享规则样本为regex文本S|执行样本有数值/资源断言但自报metricsS|现成Harbor；作者多数标ceiling P|软件泛化备选，不选主集|
|SafePyramid|policy可独立给生成器S|例外/干扰标签；未证实同policy 2+1|规则集合判分S，无动作状态|政策复杂；抽样未完整固版|规则识别补充|
|SkillEvolBench|种子技能/任务经验为主；少量短API文档S|同族≠同源规则，2+1 U|outcome+源码字符串process；trace可信度缺口S|与当前生成问题错位；许可U|暂缓正式采用|
|PolicyBench|147政策条款S|短条款可映射程序|完整fixtures私有S|需新建Oracle；不只是换接口|淘汰现成主集|
|SkillsBench / Terminal-Bench|自然来源逐题另筛H|目前抽查未完成共享规则组|现成执行，但答案可见/特定Oracle风险H|任务池强；当前格式版本各异|补充池，非文档默认主集|
|FlowBench / SkillForgeBench|工作流/技能派生来源P|未完成实际逐题关系核查|LLM模拟/LLM judge或完整包未定位|轻审，不与深审证据同等排名|不进入本轮首选|

必要条件没有过门时不以“规模大、顶会、看起来复杂”补分。纯文本任务不淘汰，但其分数只支持决策/知识应用。缺2+1的生成集仍可测一般内容质量，不能据此支持共享规则传播主张。

## 4. 重点候选真实样本

### 4.1 ConditionalQA：自然文档主层

固定代码/数据提交 `77bd295952daf415548b3244db10880d3d55cfe0`、发布目录v1_0。实际读取652文档；任务覆盖631个URL，train2338、dev285、test804。train/dev共2623题有公开答案，其中613题至少含一个条件答案；test文件不含金标。三个split来源URL不重叠。10284条evidence出现均能定位原文HTML块，但339次有重复块，不能总取第一个。来源朴素词数中位1021.5，范围206–8874；不是token数，也没有据此推断存在扫描图像版。[官方数据与许可](https://haitian-sun.github.io/conditionalqa/)

数据CC-BY-SA4由作者主页直接声明；仓库误拼名称`LISCENSE`是BSD软件条款，不代替数据许可。以下仅把**冻结历史文本当研究数据**，不作现行政策建议。

真实2+1：`documents.json`0基索引27，URL标识 `paternity-pay-leave`。

|节点|真实ID/位置|内容与依赖|
|---|---|---|
|来源证据|contents[51]/重复[58]，及[52]/重复[59]|连续任职门槛26周；qualifying week为预产期前15周，adoption另有规则|
|依赖T1|`train-20`|入职2个月、孩子20周后出生，问任职时长是否足够；金标no，证据指向上述两块|
|依赖T2|`train-41`|询问需受雇多久；金标26 weeks，同一证据规则|
|非依赖T0|`train-2`，contents[71]|已任职3年以上，问通知期限；依据独立通知规则，不依赖26周门槛|

样本：`audit_2026-10-17/cl_rules/conditionalqa_shared_rule_sample.json`。两处“15周”分别表达资格计算时点与通知期限；把它们仅按数字合并，正是需要内容评价捕获的错误。已有静态题意和证据支持，不等于已证明Agent必须通过Skill获取知识；预训练记忆与短答案猜测仍待对照。

原Oracle的限制很具体：[`evaluate.py:33`](https://github.com/haitian-sun/ConditionalQA/blob/77bd295952daf415548b3244db10880d3d55cfe0/evaluate.py#L33)漏答没有进入聚合分母；`:142–196`条件按原文HTML块精确匹配，`EM_with_conditions`还乘条件F1，并非严格整题全对。生成器可能正确释义而不复制原文，此时条件分数不能直接反映Skill语义质量。

可复用问题、场景、金标和逐题评分函数；新增可信包装负责固定ID覆盖/唯一性/分母。**条件语义对齐须新增人工标注或独立人工核验**；不能把金标条件注入生成器以解决错位。原始指标与新条件语义指标分开报告。该集没有真实业务工具、状态动作或副作用Oracle。

### 4.2 SOPBench（Leezekun）：机制与执行层

固定 `8790ed7406acbd22270f90bd1c4038de3fc5db8f`；代码MIT，数据CC-BY4。当前文件实际830题/7域，不以论文900+替代；library66题。工具真的读写仿真状态，具有constraints、constraints_original、directed_action_graph、initial_database等字段。[固定仓库](https://github.com/Leezekun/SOPBench/tree/8790ed7406acbd22270f90bd1c4038de3fc5db8f)、[论文](https://arxiv.org/abs/2503.08669v2)

**不能直接把每域一份文档配给全库。** `env/task.py:167–190`将每题约束替换目标action默认约束，并生成该题SOP；同borrow_book任务的规则集合、borrow_limit会变化。审计脚本静态筛出144题的结构及所有参数与默认代码policy相符，但这不是144题通过来源完整性/Oracle验收。`reference/prompts`的生成使用每域first_task；bank等五域首题结构不等于full，不能把reference自动当所有默认政策的完整说明。library18、university33是较窄待筛候选，也不是正式合格计数。

已人工定位的固定来源组是 `reference/prompts/library_system_prompt.md`，borrow规则在45–55行，pay_late_fee在71–74行附近；它是官方从代码导出的操作规范，未含实例答案，但不是独立现实手册。

|节点|真实索引/ID|共享规则证据|
|---|---|---|
|目标R|`user_book_not_borrowed`；source的borrow_book条目|所借书ID不得已存在用户borrowed中；其余前提还包括login、库存、restricted/membership与borrow_limit=2|
|依赖T1|`data/library_tasks.json` → `borrow_book[25]`，审计复合ID `library/borrow_book/25`|pepperoni借Beloved，初态未借、其他条件满足，应允许；正确程序需要检查规则再执行|
|依赖T2|同文件 `borrow_book[27]`|mario已借Beloved，其他条件可满足，此规则要求拒绝；可观察拒绝和无借书副作用|
|非依赖T0|同文件 `pay_late_fee[0]`|支付逾期费用，使用余额/费用规则，不调用borrow_book、不需要检查目标重复借书规则|

复合ID由domain/action/原数组0基索引构成，不伪称原生UUID。原题及初态已存 `sopbench_library_2plus1_samples.json`。目标规则误删未必损害正例T1，却会损害负例T2；误写成相反条件可能同时影响两题。**两题共享规则不意味着所有错误类型都让两题同向失败**，未来应按具体规则变异与分支预测影响，不能倒推结果。

Oracle读 `env/evaluator.py`：从初态构造strict环境，重放实际工具序列，比响应与最终DB，并检查任务动作图。优于只比文本，但有两项关键缺口：拒绝题的空调用轨迹可能满足默认布尔条件；DB是与同一调用序列strict重放结果比较，不是与任务唯一预期终态比较，额外合法动作未必被拒绝。这是静态风险，尚未运行探针。[评价代码](https://github.com/Leezekun/SOPBench/blob/8790ed7406acbd22270f90bd1c4038de3fc5db8f/env/evaluator.py#L119)

另有必须核验的边界：目标action成功不充分绑定用户指定对象；图参数fallback对0/False放宽；strict login写入状态与返回密码验证结果的顺序、先决图对失败工具返回的处理存在缺口。来源也不是天然无冲突：library余额说明用“more than”，实现用`>=`；本组三题不处在等额边界，但扩展时必须先裁决，不能将此当文档退化造成的错误。

正式采用需分别报告“应成功任务完成”“应拒绝时有证据的拒绝”“约束遵守”“不允许状态变更”，并先用正确/单规则错误/空轨迹/多做动作/错对象/零值参数/错误登录的固定轨迹验收Oracle。新增检查是扩展协议，原指标另保留。主实验宜用prompt模式、full工具及full默认约束配置，关闭constraint_hint；工具只强制必要innate约束。program模式强制所有业务条件会把Skill错误挡在环境层，混淆Skill质量。移除oracle工具列表、constraint_verdict/action_order提示与Clean SOP旁路；工具名/参数schema保留，业务规则只经Skill提供。没有完成这些工作前，不称“已直接接入”。

### 4.3 RuleArena与Amazon SOP-Bench：为什么没有取代首选

RuleArena固定 `59f60f6b4eb93a9b6d187ec781349d4f15618903`，已读airline规则、fee tables、compute_answer、auto_test、三个comp任务文件，以及tax部分。Main Plus行李政策能对应 `airline/comp_0/4`、`/8`，Main Cabin `/0`作对照（审计复合索引）。数值正确性可用独立程序核验，适合表格/数值规则补充；仅三领域、通常输出金额而非状态动作，不能独自证明真实Agent执行。必须把优惠影响的费用分量与完整结果分开，并核规则表、行李分配策略和参考程序的一致性，不能把“有Python答案”当全部标签正确。原auto_test允许金额substring匹配，micro规则评价还调用LLM解析CoT；需严格数值提交包装，不能声称原判分完全严格确定性。[官方仓库](https://github.com/SkyRiver-2000/RuleArena)

Amazon SOP-Bench固定 `f6d43858b94cf439854038101bce0eecd3e16eae`，与Leezekun项目不同。其SOP、工具与决策实例可获取，许可声明CC-BY-NC4；当前版本范围不与2025首版混记。实际读到aircraft_inspection工具直接按ID从带输出CSV取值，部分其他操作只查非空；不能据函数名推断真实状态转换。`evaluation/parser.py:515–517`默认fuzzy决策采用双向substring，`evaluator.py:333`调用该比较，决策正确不充分验证过程。[固定代码](https://github.com/amazon-science/SOP-Bench/tree/f6d43858b94cf439854038101bce0eecd3e16eae)

Amazon域内LICENSE.md另有关于训练、论文分发和生成数据标识的条件，不能只凭根CC-BY-NC徽章推导全部未来用途获准。其KYB税ID样本两道非法前缀题有共享规则，但合法TIN对照仍需同一税ID验证，只是不触发该分支，弱于SOP跨action非依赖控制。因此二者保留为规则内容/数值补充；不为覆盖更多名称而同时纳入最小正式组合。完整样本与边界在policy notes。

### 4.4 AppWorld：第二推荐的执行层

实际取得公开minimal `data-0.2.0.bundle`，SHA256 `c9299e6cafe92bce4592a3c117c047c973d1554a667c21dd81537e78ab2f532e`；仅按公开格式静态读取，没有安装环境或运行Agent。当前包732题/244scenarios，train90/dev57/test_normal168/test_challenge417；不是论文750。代码固定 `42b5bcf3cd334fee33f0c37c02070a9f5807add5`。[代码](https://github.com/StonyBrookNLP/appworld/tree/42b5bcf3cd334fee33f0c37c02070a9f5807add5)、[公开包](https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.2.0.bundle)

实际样本：Spotify API文档 `data/api_docs/standard/spotify.json` 的 `show_playlist_library` 定义分页参数。任务 `692c77d_1`对播放列表中喜欢的歌曲评分，`b7a9ee9_1`按播放列表歌曲关注艺术家；参考调用均遍历page_index0..9。控制 `ccb4494_1`针对队列中歌曲点赞，不用playlist API。逐题evaluation核新增/更新集合及允许变化模型，优于只看Agent声明成功。

但是两题reference都分页不证明别的合法接口无法完成，也未证明首屏外恰有必须操作的实体；规则必要性U。个别同模型更新字段也不在集合断言中。生成器只读API资料，不能读required_apis/solution/评价/初始DB；执行端须阻止源码和直接数据库旁路。

公开代码Apache与protected数据分开，后者含API文档、测试及派生物公开再发布加密条件。保留原Engine，经受限终端客户端/服务桥接Harbor比重写业务环境更合理；其原生执行器可作局部例外，不必为统一外壳重造AppWorld。适配成本高于SOP与文本提交，故列第二组合/后续泛化。

### 4.5 CL-bench与SkillGenBench：保留研究价值，取消默认优先

CL-bench固定HF revision `b28a5832a09b0d96c0cf4c22e90d7c60ede25b80`。实际1899题、500 contexts，621题带assistant历史。每context题数1–12；“同context文本相同”不保证无历史答案和来源旁路。低库存context `d2004304-78e2-4d30-8b80-4afc9a1ef8c0`的两题 `337005d4-a936-42ef-8813-3555b5e3d17f` / `b9e2d8ad-071c-4f68-8603-811056cf8c3d`确实涉及零库存最高优先级，但任务本身重述规则，未核不依赖的独立控制题；source内还存在`<`与`<=`冲突，rubric选后者。其推理脚本是chat completion，输出JSON不代表真实库存API执行。数据许可明确评估专用并列adapting/distilling限制；无参数Skill是否在允许范围仍须澄清，不自行宣布合法或禁止。[数据条款](https://huggingface.co/datasets/tencent/CL-bench/blob/b28a5832a09b0d96c0cf4c22e90d7c60ede25b80/LICENSE.txt)

SkillGenBench继承固定代码审计：187任务中28codedoc、36domain、123repo；doc64任务分45source/context groups，domain每context仅一个任务，多个test cases不能当不同任务。已有程序测试有价值，但两份scikit任务的硬编码输出/APIname注释探针可通过、Scrapy单规则错误可被部分case拦下，说明Oracle质量不能一概通过或一概否定。默认runner只接受单技能包形态、Agent环境能读docs/tests/groundtruth，且当前task-agnostic资料不齐。HF公开版本的许可证/文件身份另记录，不能把GitHub某文件问题推广到HF全库。[固定代码](https://github.com/QuantaAlpha/SkillGenBench/tree/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d)

二者仍适合挑选清楚来源、补隔离和Oracle后的扩展比较。当前课题需要的规则真值与影响映射，不会因为项目名带SkillGeneration就自动存在。

### 4.6 其他新候选的实质筛除

AgentDocsBench有15真实任务、16文档和可执行verifier，pagination/organization_sync与feature_flag可构成2+1候选；但文档含逐题实现、SDK可读改、organization_sync漏page_size/全部cache断言。UXL已有Harbor格式，C++真实执行样本较强，但oneTBB第二共享样本只是regex文本；作者标记41题中25ceiling，非本轮复现成绩。二者不优先于主组合。

PolicyBench公开147条款但fixtures私有，`COMPILE_OK_NO_FIXTURES`不能当正确。SkillEvolBench真实API样本 `E2-LS3-T2`有opaque cursor规则与outcome断言，process依赖源码字符串、trace文件可信度不足，且数据许可未明确。SafePyramid有条件/例外规则标签与集合评分，但只检验政策违反识别；同对话三政策不等于一源三任务。SkillForgeBench仅完成论文层核查，未定位完整可复现发布包，不能按作者任务规模升级。详见清单和root notes。

## 5. Evidence–Rule–Action真值如何建立

**没有一个候选直接提供“Anything2Skill中间候选→证据整合→最终SKILL.md”的完整真值。** 不应把下游任务正确当Skill正确；同样，Skill内容正确也不保证Agent读取、选择和执行正确。

|真值层|优先资源/已有标注|可无模型派生|仍需人工新建/核验|
|---|---|---|---|
|Document/Evidence|CQA的完整HTML块、URL、逐题evidences；SOP源规范|版本/哈希、块索引、重复块集合|作用域、跨段关系、真正支持该规则的证据；重复块消歧|
|Rule/Condition/Exception|SOP约束表达式及and/or/chain；CQA答案条件|规范结构、参数、条件图、语法候选|自然语言规则正确解释、边界/优先级/例外、冲突裁决；不能全靠生成模型自评|
|Action/State|SOP工具与动作图/初态；AppWorld目标集合测试|规则到检查工具/动作节点的候选映射|必要/允许/禁止动作、等价合法路径、额外副作用规范|
|Rule→多Task|CQA已核2+1，SOP已核library组|候选扇出和任务分组|必要性、替代路径、控制题不依赖性；具体错误类型影响方向|
|中间结构→最终Skill|现成数据均没有|生成日志、产物来源ID与字节哈希关联|逐条语义对齐、遗漏/新增/错误合并/条件删减；合理拆分合并不应按字面判错|
|形式依赖诊断|ProofWriter事实/规则ID与proof|规则到所有证明的依赖图|OWA/替代证明处理、Skill映射；没有现实Action|

ProofWriter实际样本 `AttNeg-OWA-D3-551`：rule4为blue→red，Q3 red、Q5 big的证明含rule4，Q1 blue直接由fact支持。它是强Evidence–Rule–Conclusion诊断，不是已有Action真值；官方数据许可U，故不列为必需第三集。

推荐最小标注单位：`source_id/version → evidence locations → rule_id → 前提/结论或动作/例外/顺序/参数 → task IDs及依赖理由 → oracle assertions`。同时记录来源冲突与规则可恢复性。先由人审核Clean规则，不将原任务rubric、模型答案或原A2S生成Skill直接当金标准。

独立内容评价至少分别计规则正确性、覆盖率、条件/例外完整性、证据支持、无依据新增、冲突处理及中间到最终丢失；执行评价另计完成、约束遵守、错误副作用、拒绝正确性及是否真实读Skill。LLM可未来辅助提出待审标签，不能成为未经校准的唯一真值。本轮未实施标签系统。

## 6. 任务路线A/B/C/D及工作量

以下是熟悉Python/容器的一名研究工程人员的人日估计I，不是已消耗时间或报价；不含模型调用、训练、集群排队及无法预估的依赖问题。来源/规则标注按实际数量另计。

|路线|可直接复用什么 / 改什么|偏差与语义界限|首个小组工程估计|扩展判断|
|---|---|---|---|---|
|A直接复用|原任务、场景、初态、标准答案/参考程序|以Skill替代原文已是新输入条件；原官方榜单协议与本研究分开|CQA可信文本提交包装0.5–1.5人日|优先复用内容；不存在整套零改动满足研究的候选|
|B保留题义适配|CQA answer.json；SOP固定policy+工具桥；AppWorld Engine桥；Harbor verifier接口|补Oracle、禁止旁路须披露；若删任务历史/拆claims就是题义改动|SOP单域3题约2–4人日，Oracle补强另1–3；AppWorld3题约3–6；UXL1题1–2|最主要工程路线，复用原环境，避免重造工具|
|C真实文档派生少量题|Git/qsv校准；确无非依赖控制时补一题|作者偏差、自造题难度不足、同人造题造Oracle；不能称原benchmark结果|一个CLI模板含正确/错误Oracle探针约1–2人日；新业务环境明显更高|仅补缺口；不应启动大量新题建设|
|D主集+补充|CQA自然文档层 + SOP执行机制层；AppWorld后续替换/泛化|分层得分，研究结论不互相替代；多域来源有效样本数单独计算|第一组跨两集工程约4–8人日，加约2–4人日初始人工规则审核|明确首选；最有利于将自然文档恢复与可执行性同时验证|

不需要自己造大量任务。CQA已有2623公开有标签题，SOP已有830题；真正新增工作集中在**选出来源一致的子集、补规则依赖/对照标签、修评价包装和隔离**。但“现成题很多”不代表全库均可直接复用，144匹配候选也不能当144独立来源。

来源/规则标注可按每篇0.5–2小时初审、每规则约10–20分钟结构与任务映射复核粗估；复杂冲突/动作图更久。先标5篇试算真实速度，再估总成本，不把该区间当承诺。内容评价中条件语义对齐不是免费派生。

## 7. Harbor + Terminus-2适配契约

继承固定Harbor `2de4605b9404eada7d341388291e6e469c90330b` 的源码结论，不宣称当前已跑通。它能发现多包SKILL.md，构建name/description/location目录，再由Agent主动读正文；不能把harness预读当Agent使用证据。[加载实现](https://github.com/harbor-framework/harbor/blob/2de4605b9404eada7d341388291e6e469c90330b/src/harbor/agents/terminus_2/terminus_2.py#L623)

统一保留每来源生成的全部canonical包，不能挑已知正确的一份，也不能将所有领域47份技能无差别混入每题。使用稳定目录/UUID映射，记录源包与安装包逐文件哈希。已审47份原Skill都是CRLF，而固定解析regex仅LF兼容；未来需在加载器内存解析处做兼容，不改原文件。若包带脚本，还要避开Windows上传换行转换或逐文件检查，不能承诺任意assets天然字节无损。

|数据集|Agent获得什么 / 如何提交|环境/工具新增|原Oracle复用及隔离|是否改Benchmark|
|---|---|---|---|---|
|CQA|原scenario+question，answer.json；Skill目录由Agent读取|只需文件提交，无业务工具|金标与evaluator只在separate verifier；固定全量ID；条件语义独立审核|Skill替代原文是新输入条件；条件ID/释义评分是扩展指标|
|SOP|原用户请求+工具schema+对应policy Skills；通过固定工具服务行动|持久状态服务或进程、受限CLI适配；禁止直接读写内部DB|复用strict重放，外加拒绝/副作用断言；可信工具日志由服务持有|挑固定policy子集、去规则提示、扩展Oracle均公开说明；不称原完整830分数|
|AppWorld|原任务+API接口；Skills源于独立API文档|保留原Engine，终端/MCP桥；固定初态/时钟/凭证|原状态tests独立执行，源码/gold不可见；遵守protected数据条款|题义可保留，输入知识条件变化；原生runner是可接受局部例外|
|RuleArena/PW/CL|原问题+结构化提交文件|文本；CL如要真实库存动作需另建环境|数值/标签可包装，CL原judge需校准或新Oracle|把文本题改业务动作属于新任务，不能只叫桥接|
|UXL/TB|现有instruction/环境，安装生成Skill|多数已有Harbor；需固定镜像/依赖|审每题可信tests与产物边界|源文访问/联网、oracle修改均单列协议|

Harbor separate verifier是显式选项，不能依赖默认shared环境。只移交候选产物及受信环境日志/状态，不能采用Agent自写reward。对有状态任务，可信sidecar持有初态/日志并生成只读快照；仅把Agent写的trace.json复制到verifier不解决伪造与旁路。源码审计支持接口可行性，端到端加载、工具生命周期和费用均待后续实测。

## 8. 两阶段最小验证与正式扩展

### 阶段一：一个Git恢复任务先验证工程链路

沿用前审具体建议：固定Git源文提交 `a52a24e03c8c711f1d5e252fba78f9276908129b`，构造HEAD/index/worktree彼此不同的本地fixture；要求从明确的旧commit恢复指定路径的index与worktree，同时保持HEAD和无关文件不变。目标语义为显式`--source`配合`--staged --worktree`，合法等价操作按最终状态判，不按命令字符串判。[官方独立测试](https://github.com/git/git/blob/a52a24e03c8c711f1d5e252fba78f9276908129b/t/t2070-restore.sh#L37)

未来步骤与验收：

1. 先用正确操作及漏source、漏index、漏worktree、改HEAD/无关文件等最小错误结果验收Oracle；不先耗费模型测一个有漏洞的判分器。
2. 从冻结源文经原版Anything2Skill生成该来源全部包；现有14份Git Skill仅可先校准安装，不冒称新跑完整生成链路。保留原字节与所有包，验证CRLF兼容、发现记录及真实读取轨迹。
3. 用人工核准Gold Skill作执行正控，再比较同模型/同预算A0无Skill与A1原生成全部Skill。Gold只作诊断，不混作A2S结果。记录实际工具行动与状态Oracle；一个任务结果不是正式鲁棒性结论。

**本轮没有实施上述步骤。** Git/qsv/rg是工程校准，不因熟悉、便宜或跑通而自动成为论文主数据。

### 阶段二：先真实组，再扩样本

第一批候选：CQA的train-20/train-41/train-2；SOPBench的library/borrow_book/25、/27及pay_late_fee/0。先做原始来源—标签一致性、任务旁路与Oracle敏感性检查，再开始任何Clean/Degraded对照。

建议正式扩展顺序（I，样本量是计划而非已存在合格集）：

1. **来源验收**：CQA先5篇、SOP先library单域；人工确认每规则的条件/例外与证据。不要为了形成2+1硬改既有题义。
2. **自然文档层**：从CQA公开train/dev按来源选20–30篇、约80–150原题作为第一批研究子集，覆盖条件、例外、表格、多段证据；再按预注册分层扩展。若控制题确实缺失，少量补题并标记来源，原题分数另报。
3. **执行机制层**：先审核library18与university33候选，再审其余默认policy匹配项。全库144仅作搜索起点，最终数量由source完整性/Oracle/旁路审查决定。增加任务初态不是增加独立来源；7域不能包装成数百文档泛化证据。
4. **独立泛化层**：主组合结果可解释后，再加AppWorld的小批跨应用任务或UXL可信CPU执行题；不一开始铺开十几个框架。CL用途明确且通过来源/Oracle清理后，才加入复杂context外部验证。

划分至少按source/policy family隔离，近重复文档、同规则改参数族、同scenario不同难度不能随机散到开发与测试两边。共享规则传播在同源任务组内测；跨来源泛化在冻结未参与调参的来源上测；汇总应以来源/规则族聚类，而非把大量case当独立观测。

未来退化研究需区分：解析层损失、规则证据仍可恢复、关键信息已不可恢复、Clean原生冲突。保留一条“固定解析器→生成器”主线及DirectDoc控制，避免把OCR提升说成Skill构建提升。预先冻结来源可见性、任务预算、内容评价规则和错误分类；不在测试答案上调生成提示。此处只规定数据与评价边界，不构造退化或设计新算法。

可复用组件：source/version/hash manifest、源文白名单、原A2S调用与日志、全包安装/发现/读取记录、Harbor任务生命周期/独立verifier、统一结果记录、内容标注schema与来源级分组。更换数据集需替换：文档解析器、任务输入/提交schema、工具环境/状态导出、专属Oracle及规则对齐标注。整体框架不需重写，业务语义适配不能省略。

## 9. 充分证据、待实测与停止条件

**已充分支持的静态结论**：存在比已知候选更适合特定研究层的新资源；CQA独立来源/证据/2+1和许可真实；SOP有可执行规则结构及固定library组；默认policy与逐题policy会不同；AppWorld公开包与状态Oracle真实；CL/SGB及新候选确有已列的隔离/覆盖/许可限制。主推荐依据这些必要条件而非基准分数。

**仍未验证**：原A2S是否能从这些来源生成完整正确的多包Skill；Agent是否读且依赖这些Skill；规则错误是否按预测传播；修包装后的Oracle能否拒绝全部指定错误/副作用；固定子集最终规模；真实运行耗时/费用；无Skill知识饱和；Clean/Degraded效应和任何新方法优越性。任何“优于CL/SGB”仅指本课题资源适配性，不是已测性能排名。

后续正式进入实验前的停止/转向条件：来源与任务policy无法一致就剔除该组；Oracle对空轨迹/关键错误不敏感就先修评价；无Skill已饱和且无法找到知识需求就换组；来源可见性无法隔离就不用于Skill-only因果主张。失败样本保留在筛选日志，不悄悄换题后只报成功。

## 10. 对用户12个问题的直接回答

1. **新候选有哪些？** ConditionalQA、两种SOPBench、RuleArena、ProofWriter、ShARC、AppWorld/UXL/AgentDocsBench的新一轮深入资源、SafePyramid、PolicyBench、SkillEvolBench、SkillForgeBench、FlowBench、DocPrompting、RuleBench、两种ExtractBench、ThinkingBox、Integration Bench、MDCR等；哪些是首次发现、哪些为旧项升级，清单与证据级别分别标明。
2. **有没有比CL-bench、SkillGenBench更合适的？** 有：CQA在自然来源—证据—条件标注上更直接；固定policy SOPBench在规则—动作结构和同规则任务组上更直接。不是宣称二者全方面无缺陷。
3. **退化文档到Skill生成首选哪一个？** 以本课题自然文档、证据整合和条件恢复为优先，选ConditionalQA作主数据层；它必须配执行补充，不能独自支持可执行性结论。
4. **结构化Evidence–Rule–Action真值首选？** SOPBench固定政策子集最接近，已有约束/动作图/初态；自然语言证据对齐仍要补。ProofWriter仅是Evidence–Rule–Conclusion更完备，不冒称Action。
5. **真实Agent使用Skill任务首选？** 本课题第一执行组用SOPBench library固定政策任务；若强调跨应用终态与广泛真实仿真能力，AppWorld为第二执行层。均须先通过可见性及Oracle验收。
6. **一个集能全部满足吗？** 没有已核全部满足者。
7. **最佳组合？** 明确选D：ConditionalQA主层 + 经准入的SOPBench机制/执行子集；第二组合是CQA + AppWorld。
8. **哪些复用、适配、新建？** 复用原题/初态/标签/程序；适配提交接口、可信判分、隔离和工具桥；新建少量规则映射、必要控制及副作用断言，不新建大量任务。
9. **哪个更利于方法创新？** CQA提供自然证据缺失/条件错误/合并冲突研究空间，SOP提供可控动作机制，两层组合优于单一排行榜。已有SOP编译研究存在，创新应落在退化恢复与证据可信构建，不能泛称首次把SOP转程序。[相关方法](https://arxiv.org/abs/2607.11346v3)
10. **现在最小验证任务？** 既有Git显式旧source、同时恢复index/worktree、保留HEAD与无关文件的一个本地任务；它验证完整工程链路。紧接着的第一个正式机制组为SOPBench library 2+1。
11. **扩展可复用什么？** 原A2S、source manifest、全包安装/读取、Harbor生命周期、独立verifier框架、结果/规则标注schema；环境、Oracle和语义映射按集替换。
12. **证据与实测界限？** 数据、代码、静态映射和具体缺口已查；A2S产物质量、读取依赖、规则传播、端到端成本与鲁棒性效果均待实测。本轮止于报告和审计材料，不实施方案。
