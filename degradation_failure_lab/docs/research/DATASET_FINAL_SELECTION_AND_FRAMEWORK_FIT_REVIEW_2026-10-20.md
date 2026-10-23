# 数据集最终选型与框架适配独立复审

日期：2026-10-20。项目：`D:/AS/AutoSkill-main`。研究目录：`degradation_failure_lab`。

本报告覆盖前一轮“ConditionalQA 与 SOPBench 原始数据核查”要求，以及本轮最终选型、任务难度和相关 Skill 提取研究的评测设计要求。只进行了阅读、固定版本最小数据获取、无模型加载/评分探针和报告撰写；没有运行 Agent、模型、embedding 或付费实验，没有修改官方生成器、canonical Skill、正式 Oracle 和历史账本。

## 1. 决策先行：撤回直接采用旧组合的建议

**不再推荐 ConditionalQA 为主数据集、SOPBench 原样充当主执行层。优先开展“真实软件文档＋可执行任务环境”的准入核验；当前首个工程准入候选是官方 Box 文档＋Agent-Diff，Calendar复杂规则族是下一步定向复审对象。ConditionalQA 降为自然政策文档的规则编译泛化验证集；SOPBench 仅保留为政策机制辅助集。Git restore 继续用于工程校准。**

这是一项明确的“下一步验证谁”的排序，**不是宣告已经找到通过验收的主数据集**。Agent-Diff 也有原生 Oracle 漏检、文档与模拟器不完全一致、格式适配未通过的问题；当前没有任何候选通过本研究的全部硬门槛。Box `box_131/box_141/box_117` 只能先做接口与 Oracle 验收，不能直接升格为论文主任务。复杂任务仍须证明真实知识依赖，不能凭调用数或任务名判断。

最关键的三个阻断问题：

1. **任务是否真的给 Skill 留有作用空间。** train-41 的数字抽取、普通 Git 恢复、Box 建 Hub 等可能靠常识、既有 API 知识、正常工具说明和试错完成；目前没有新增任务的 A0/DirectDoc/Skill 对比或自主采用证据。
2. **Oracle 是否判断独立用户目标。** CQA 漏答可被排除分母；SOPBench 错用户、错对象、双重扣费可通过；Agent-Diff 已查断言漏检目标关联和额外删除。原生评分不能直接当研究真值。
3. **正确来源能否完整进入原版生成链。** CQA、SOP 和 Box 的无模型窗口探针都发现信息覆盖风险；Box 原始 JSON 甚至简单包成 Markdown 仍丢目标契约。当前真实配置的 LLM outline 和最终 Skill 尚未验证。

因此应先做有限的来源/工具/Oracle验收与任务知识依赖校准，再决定正式样本；不立即扩大生成数量或消耗模型预算。

## 2. 研究对象、证据层级与因果边界

研究对象是：源文档退化是否在原版 Anything2Skill 的提取、编译、合并、注册中造成规则遗漏、条件/范围失真或证据不足；这些错误何时被自主 Agent 发现、读取并采用，继而改变真实任务结果。完整链路为：

```text
冻结来源 D → 仅改变来源的 C/R/U 版本 → 原版 Anything2Skill → 完整冻结 Skill 包
                                                        ↓
任务与初态固定 → 同一 Agent/工具 → 自主发现与读取 → 行为 → 独立目标 Oracle
冻结来源 D 的同版本 ─────────── DirectDoc 对照 ───────────┘
```

C=clean，R=目标规则相关退化，U=无关规则退化；这是研究设计符号，不是原始数据字段。格式破坏、遗漏、否定反转和参数改写分开报告，不能汇总成语义不清的单一强度。两条依赖任务必须通过规则的前提/结论证明；引用同段文字仅是候选筛选。

证据标记：**F**=本轮直接读原始文件/源码并核对；**T**=无模型离线探针；**H**=审阅历史真实运行，未重跑；**P**=官方论文/发布说明；**I**=拟设计，未实施；**U**=尚未验证。下文结论均受其证据层级约束。

四类指标分开：①源规则→生成产物保真；②索引/正文/规则跨度暴露及采用；③业务目标与副作用；④干预后的因果响应。访问文件≠进入模型输入，行为一致≠因果采用；没有正文读取也不能排除 index description 的作用。

**任务难度不是步骤数。** 应考察版本特定参数、跨段条件组合、例外、作用范围、对象选择、跨步骤不变量及失败恢复。十次机械重复调用可以很简单；一次带复杂边界的决策可以很难。不能为了让 Skill 显得必要而禁用正常查询、正常报错或所有替代操作。

## 3. 已有框架实际实现到哪里

已完整审阅 [上一份选型报告](D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/DATASET_AND_TASK_SELECTION_AUDIT.md)，并结合 clean 生成/质量报告、SkillGenBench 可行性审计、下游 readiness 与最新 Gold 原始报告检查代码。上一报告的推荐是待检验结论，不作为本报告的真值。当前根仓库HEAD为 `a379e54e1233bd3f3011869f70eaf7fed8762982`；正式生成代码的逐文件SHA记录于本轮probe_results。报告保存前工作树已有`.idea/vcs.xml`修改及暂存的上一份选型报告，本轮未处理这些已有工作。

### 3.1 生成结构

```text
lab adapter.execute
  → load_file_units → TextUnit
  → ingest(DocumentRecord / sections / outline / windows)
  → extract(plan → expand → SupportRecord + SkillDraft)
  → compile(按文档和能力身份分组 → SkillSpec)
  → register(合并、去重、版本、生命周期、visible tree)
  → canonical SKILL.md 及其完整资源包
```

关键源码：`degradation_lab/adapter.py:31,135`；原版 `AutoSkill4Doc/extract.py:325,404,438`；`ingest.py:785,873,997,1116`；`stages/extractor.py:857,896,1284`；`stages/compiler.py:143,185,306,480`；`store/versioning.py:941,1377`。完整绝对路径与 SHA 见 [生成审计](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/generator/notes.md) 和 [探针结果](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/generator/probe_results.json)。

当前 `configs/generation/deepseek_flash.json` 使用 recommended、LLM outline、每 unit 至多4候选、max_units=0、fallback chunk6000/overlap300、max_section_chars10000、独立空库。**推荐窗口目标默认2400字符，不是配置中的6000；2400也不是所有情况下的硬上限。** 单大块可能更长。max_units=0 不意味着全来源被模型覆盖。

SupportRecord 的 excerpt/span/confidence 是生成器输出，不是外部规则正确标签。一个来源可生成0/1/多个 Skill；不能按目标题事后挑最佳包，不能预设一文档一 Skill。必须保留解析、窗口、support、draft、spec、registry 的阶段映射，区分错误首次出现位置。

原版提示允许 policy/workflow，taxonomy 包含 knowledge_reference/safety_rule，编译契约包含触发、禁用条件、流程、约束、输出。它并非只支持软件教程；但提示中残留 counseling/therapist 语境，且纯摘要可能被编译过滤或诱导补造流程。**字段支持只证明形式许可，不证明稳定生成有用 Skill。** 软件/API操作指南最贴近动作契约；SOP决策程序次之；普通事实文档和单数字查找较弱。

### 3.2 下游和 Gold

复用路径为完整包安装与冻结校验→原生 Terminus-2 发现→终端执行→Harbor separate verifier。关键文件：

- [skill_install.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/skill_install.py:17)：canonical ID、清单和逐文件哈希；完整复制包。
- [p1_observer.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py:204)：索引核验、文件事件、终端可见帧；`:35`的全文字符串判断尚非规则跨度采用证明。
- [harbor_adapter.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/harbor_adapter.py:76)：强制 separate verifier。
- [Git Oracle](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/git_restore_explicit_source_both_v1/oracle.py:90)：工作区字节、Git index、refs及副作用；属于 Git 专用，不可直接复用为数据库 Oracle。
- [request_budget.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py:266)：已有持久预算与停止机制，但现有续跑条件含任务专属判断；新任务须新 scope，不能沿用旧停止账本。

最新 [Gold 恢复报告](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/report.md)【H】：Harbor0.24.0，commit `2de4605b9404eada7d341388291e6e469c90330b`；Gold真实2次HTTP200、2755tokens、九项断言全通过。安装/发现1包，首请求有索引，正文未内联；kernel读取日志为空，model_read_ids/full_body_visible_ids均空。A0/A1 **NOT_RUN**，Gold因使用诊断停止。索引含指定源与同时恢复两个位置提示，既有知识也可解释正确动作。因此只证明运行和验证链已通，不能证明生成 Skill 的正负效应。

历史五 clean 来源和47份 canonical 的存在也不是生成准确率；需要按外部规则逐条验证。当前框架缺：通用 source/rule/task manifest、DirectDoc访问与跨度观测、新环境及独立目标Oracle、跨任务知识依赖验收。基础设施成熟不等于科学链路已闭合。

## 4. ConditionalQA：真实结构、样本与适用边界

固定官方版本 `77bd295952daf415548b3244db10880d3d55cfe0`。本地 `audit_2026-10-17/cl_rules/cqa_documents.json` 等缓存与固定commit归档四份JSON的**完整值一致，字节不同**；评价代码换行归一化后相同。历史 `cqa_commit.json` 实为API限流错误，不能当版本凭据。核验见 [archive_identity.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/cqa/archive_identity.json)。官方 [数据/代码](https://github.com/haitian-sun/ConditionalQA/tree/77bd295952daf415548b3244db10880d3d55cfe0) 与 [论文](https://aclanthology.org/2022.acl-long.253/)；若仓库URL大小写跳转，以固定commit归档内容为准。

### 4.1 文档和题目不是同一种记录

`documents.json` 是652个对象的数组；每条只有 `title,url,contents`。`contents` 是有序 HTML **片段字符串数组**，包括标题、段落、列表项，既不是完整原始网页DOM，也不是已标注原子规则表。块之间的标题、列表和作用域关系非常重要。文档记录不含任务答案，完全可单独交给生成器；不能混入 train/dev/evidence 标签。**本报告的CQA文档索引和全部块号均从0开始；如块51指contents[51]。**

以下是真实文档字段投影，`contents` 仅保留原始第47、48、51、52块，**数组已截断，不能把这里的新数组下标当原始位置**：

```json
{
  "title": "Paternity pay and leave",
  "url": "https://www.gov.uk/paternity-pay-leave",
  "contents": [
    "<h2>Paternity Leave</h2>",
    "<p>You must:</p>",
    "<li>have been continuously employed by your employer for at least 26 weeks up to any day in the ‘qualifying week’</li>",
    "<p>The ‘qualifying week’ is the 15th week before the baby is due. This is different if you adopt.</p>"
  ]
}
```

真实完整 train-20（保留原始字段和值）：

```json
{
  "url": "https://www.gov.uk/paternity-pay-leave",
  "scenario": "I recently got a new job, and have worked there for two months. My wife is due to have a baby in 20 weeks.",
  "question": "Will I qualify for paternity leave even though I have only worked for my employer for two months?",
  "not_answerable": false,
  "answers": [
    [
      "no",
      []
    ]
  ],
  "evidences": [
    "<p>When you take time off because your partner’s having a baby, adopting a child or having a baby through a surrogacy arrangement you might be eligible for:</p>",
    "<li>Paternity Pay</li>",
    "<p>You must be taking time off to look after the child and be one of the following:</p>",
    "<li>the father</li>",
    "<p>You must:</p>",
    "<li>have been continuously employed by your employer for at least 26 weeks up to any day in the ‘qualifying week’</li>",
    "<p>The ‘qualifying week’ is the 15th week before the baby is due. This is different if you adopt.</p>"
  ],
  "id": "train-20"
}
```

字段用途：`url`连接来源；`scenario`给个案事实，`question`给待回答问题；`not_answerable`是任务标志；`answers`为多个 `[答案字符串, 条件HTML字符串列表]`；`evidences`为支持证据的复制文本；`id`为官方任务ID。条件是平面列表，没有显式 AND/OR/例外树；证据不是块索引，重复文本会造成定位歧义。test_no_answer只有url/scenario/question/id，表示隐藏标签，不是804道无答案题。官方 scorer 实际读取 id/answers，不能只靠not_answerable字段判无答案。

### 4.2 实际规模

|统计|实际值|研究含义|
|---|---:|---|
|来源记录/独立URL|652/652|同属政府政策域，URL独立不等于领域完全独立|
|train/dev/test|2338/285/804|test无公开答案；公开标签总2623|
|train/dev来源|436/59|三split来源URL无交集；标签来源495|
|带条件答案|613/2623=23.37%|需优先人工审核，但不是自动合格率|
|无答案/是非/多答案|105/1355/562|类别重叠，不可相加当总数|
|至少3道带标签题的来源|477/495=96.36%|可形成2+1的数量上界，不证明语义依赖|
|至少2道条件题的来源|173/495=34.95%|更有价值的筛选入口|
|文档HTML字符数|中位6513.5；1320–52466|不含块间分隔符，不是tokens|
|块数|中位86；20–559|足以包含跨段条件与例外|
|每文档全部任务数|中位5.5；0–14|21来源没有任务|
|词面共享证据候选2+1|1482簇/408来源|≥45字符证据共享；不是规则簇真值|
|共享条件文本候选2+1|105簇/58来源|仍须逐条证明前提、例外与控制独立性|

完整计算与筛选定义见 [stats.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/cqa/stats.json)。当前逐条深查两个2+1规则组；通过研究专用Oracle验收的任务为0，不是认为所有任务不可用。

### 4.3 paternity 旧2+1复核

来源为 `documents[27]`（数组第28条）`paternity-pay-leave`，110块、HTML合计8243字符；只加换行拼接为8352字符/8439UTF8字节，可见文本合计7353。关联恰好5题：train-2/20/35/41/69，均train，无dev/test。

目标 R26 在第47块Paternity leave标题下：第51块要求持续雇佣至少26周；第52块定义qualifying week为预产期前15周。第48块“You must”及49–50的员工/通知条件属于同组，不能孤立读数字。

|任务|实际依赖|破坏规则的理论影响|
|---|---|---|
|train-20|已工作2个月，预产期20周后；到qualifying week再过5周仍不足26周；gold=no|把26改小会消除这条拒绝理由；其他资格未完全确定，不能直接改gold为无条件yes|
|train-41|直接问需要雇佣多久；gold=26 weeks|数值失真会影响答案，但主要是知识抽取，Skill程序性很弱|
|train-2|通知雇主的提前15周规则，第71块|不依赖26周就业门槛；同为“15周”不能认作同规则|

第58–59块在Pay范围重复26周和qualifying week，81块为收养匹配周，106块为代孕规则。前者是可恢复线索，后两者不能无条件跨范围套用。只破坏51块不等于消除所有信息；应记录“局部冗余补偿”，不能事后删除重复证据以制造效果。train-35涉及更多条件，但有leave/pay范围问题，尚不能不经审查升级。

### 4.4 更有价值的辅助决策组

`apply-special-guardian`，63块，真实任务dev-0/2/15/20。目标第4块：重要决定需要所有有parental responsibility者同意；第5块改姓、第7块出国超过3个月是适用分支；第9块不能获得同意时可申请法院C2裁决。这是替代路径，不能把“全体同意”和“法院裁决”错误编成必须同时满足。

- **dev-2**：为16岁被监护人改姓；原gold=yes，条件为第4和9块。
- **dev-15**：带10岁侄子去Boston一年；原gold=yes，条件为第4、7、9块。还依赖一年>三个月、特殊监护人身份。
- **dev-0**：法院多久回复申请；gold=within 10 days，对应第41块，不依赖同意规则。

把everyone改成one影响前两题的合法条件，未必改变yes字面答案；删法院替代路径可能造成过度拒绝。第19块同意、第22块C2属于其他范围，可能给模型线索但不自动构成等价证据。数据见 [真实四题](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/cqa/guardian_tasks_raw.json) 和 [逐块来源](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/cqa/guardian_blocks_numbered.txt)。这是较好的“条件决策Skill”辅助样例，仍不是原生真实业务操作。

### 4.5 官方评分缺陷与定位

本轮直接执行原版 `cqa_evaluate.py`【T】，结果见 [scorer_probes.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/cqa/scorer_probes.json)：

- 漏交三题中的一题，其余正确，所有汇总指标仍1.0；`evaluate:34–43`只计出现预测，漏答不进分母。
- 单一extractive小子集会因空类别在57–67行除零。
- “26 weeks”与“twenty six weeks”EM=0、F1=.4；HTML条件为字符串集合匹配，同义条件可能0。
- 无答案ref=[]、pred=[]记1；pred=[["",[]]]记0，格式必须规范。
- 答案正确而条件全漏：普通EM可1，conditional0；漏三条件之一conditional EM也可.8，名称不等于严格全对。
- 正确条件另加相反条件仍有部分分；没有逻辑矛盾检测。答案多猜会受数量惩罚，但不是完整决策正确性判断。

原代码能复用词面答案评分作为次指标；必须在外部包装固定expected IDs、漏答0、重复/未知ID拒绝、空类别N/A、限制预测数量。主指标需规则条件/范围/例外的人工真值或可核查结构化标签；两名审核者独立标注并裁决，不能仅用同一个模型判断生成物。源码77–80的id覆盖、107–130的答案排列匹配、153–198的条件集合评分也须注意。

**结论：可建立“政策→生成规则Skill→回答→严格答案Oracle”的完整辅助链；不能声称原生提供“自然政策→多步真实操作”的链。** 若输出仅重述政策，研究主张应限于编译知识保真和条件问答；不得借SOPBench的执行结果补成同一来源的因果链。

## 5. SOPBench：有动作，但原始政策和评价都不能直接用

版本 `Leezekun/SOPBench@8790ed7406acbd22270f90bd1c4038de3fc5db8f`；[官方固定源码](https://github.com/Leezekun/SOPBench/tree/8790ed7406acbd22270f90bd1c4038de3fc5db8f)，[论文](https://arxiv.org/abs/2503.08669v2)。本地原始根目录：`C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-17/leezekun-sop/SOPBench-8790ed7406acbd22270f90bd1c4038de3fc5db8f`。

### 5.1 原始JSON、SOP与工具

`data/library_tasks.json` 是 action→任务数组。`library/borrow_book/25`是本报告使用的定位符，指该数组零基25，**不是数据里原有id字段**。以下是该任务真实字段投影；为长度省略了initial_database、constraints、directed_action_graph，完整三条原始任务见 [raw_samples_complete.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/raw_samples_complete.json)。密码为公开合成fixture值。

```json
{
  "constraint_parameters": {
    "borrow_limit": 2,
    "max_reservation_slots": 3
  },
  "user_known": {
    "book_title": "Beloved",
    "username": "pepperoni",
    "password": "paikzmzhaa991"
  },
  "constraints_original": [
    "and",
    [
      [
        "single",
        "logged_in_user",
        {
          "username": "username"
        }
      ],
      [
        "single",
        "internal_check_book_available",
        {
          "book_title": "book_title"
        }
      ],
      [
        "single",
        "user_book_not_borrowed",
        {
          "username": "username",
          "book_title": "book_title"
        }
      ],
      [
        "or",
        [
          [
            "single",
            "not internal_is_restricted",
            {
              "book_title": "book_title"
            }
          ],
          [
            "single",
            "valid_membership",
            {
              "username": "username"
            }
          ]
        ]
      ],
      [
        "single",
        "within_borrow_limit",
        {
          "username": "username"
        }
      ]
    ]
  ],
  "action_should_succeed": true,
  "user_instruction": "You are trying to borrow the book titled \"book_title\" by logging into your account with the username \"username\" and the password \"password\", and set its return date.",
  "user_prompt": "Hi, I'd like to log into my library account with my username and password. My username is \"pepperoni\" and my password is \"paikzmzhaa991\". Once I'm logged in, I'd like to borrow the book titled \"Beloved\" and set its return date. Can you assist me with this process?",
  "user_goal": "borrow_book"
}
```

|原始字段|用途与可见性|
|---|---|
|initial_database|账号、图书、库存、会员、余额、日期等完整初态；不能全量给Actor|
|constraint_parameters|borrow_limit=2、max_reservation_slots=3等规则参数|
|user_known|任务给用户的账号与目标对象参数|
|constraints_original|未展开的and/or/chain/gate/single政策表达式，用来生成文字|
|constraints|展开后的约束/查询依赖，用于执行与评价|
|directed_action_graph|允许的验证/操作前置依赖；不是唯一标准轨迹|
|action_should_succeed|该初态下应允许还是拒绝的标签|
|user_instruction|含占位符的原始意图模板|
|user_prompt|实例化的用户请求|
|user_goal|目标action名称；不是包含完整对象绑定的最终状态真值|

本字段表针对所示library记录；其他域部分记录没有user_goal，官方初始化使用外层action key补齐，不能将此表当830条任务的完全一致schema。

没有独立gold final database。SOP文件 `reference/prompts/library_system_prompt.md` 为6569字符、6625字节、138行。实际borrow片段44–52行：

```text
* borrow_book:
ALL of these conditions must be met:
• The user with "username" is logged in previously with the correct credentials to perform this action.
• The book "book_title" has a count value of **more than 0**.
• The book's ID (retrieved using "book_title" from the "book_title_to_id" section) **must not exist** in the "borrowed" of the user "username".
• ANY ONE of these conditions must be met:
  • The book "book_title" has its restricted status set to **false**.
  • The user "username" must have a 'membership' field that is a date on or after the interaction_time.
• The user "username" must have less than 2 books in their "borrowed".
```

实际初始化输出的公开工具schema之一（原样）：

```json
{
  "function": {
    "name": "borrow_book",
    "description": "Allows a user to borrow a book and sets its return date. Returns true or false for successful book borrowing.",
    "strict": true,
    "parameters": {
      "type": "object",
      "properties": {
        "username": {
          "type": "string",
          "description": "a string of letters, numbers, and symbols to represent their username"
        },
        "book_title": {
          "type": "string",
          "description": "the title of the book to be borrowed, returned, or managed."
        }
      },
      "additionalProperties": false,
      "required": [
        "username",
        "book_title"
      ]
    }
  },
  "type": "function"
}
```

共31个公开工具：14业务动作、17辅助查询；`internal_get_database`默认隐藏。schema说明操作与参数，并不等于完整业务政策。但**SOP和图引用的 `internal_get_interaction_date` 也未出现在实际31个schema中**。restricted书的会员分支需要比较交互日，须先确认公开可达信息/工具路径；不能把直接调用底层方法的通过当Agent接口验收。见 [实际31工具](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/actual_visible_tool_schemas.json)。

来源并非独立自然SOP：reference README及导出脚本39–57选择各域首task生成提示；`env/task.py:167–193`按任务覆盖约束与参数并渲染，253–258注入系统提示。**同域不代表同政策。** 原生系统提示已含完整clean规则，若不改外层实验协议，再放Skill就有严重旁路。`run_simulation.py:150–155`的按oracle动作图筛工具及hint/verdict/order增强也会泄漏。应关闭这些增强，保持固定全工具接口，保留正常查询与错误信息。

prompt模式与Program/Strict模式要分开：后者硬编码完整规则，可能挡住错误Skill导致的违规尝试，不能用最终无错误证明Skill正确；prompt模式borrow innate为空，违规调用可改状态，适合观察传播但更依赖独立Oracle。

### 5.2 真正的2+1与非对称影响

目标规则 Rdup：借书前，书ID不得已存在该用户borrowed中；实现位于 `library.py:379–381`，约束绑定位于 `library_assistant.py:208–214`。以下三个任务政策/参数均属于发布library默认一致子集。

|原始定位|初态和共享依赖|正确目标|
|---|---|---|
|borrow_book[25]|pepperoni、Beloved=93TC00Q；借阅空、库存1、会员10月10日=交互日、0<2；Rdup=true|成功借该书，库存0，borrowed[93TC00Q]=October 24th, 2024；无其他业务变动|
|borrow_book[27]|mario已借93TC00Q，到期10月10日；库存1、会员10月11日、1<2；唯Rdup=false|查明重复后拒绝；库存与到期日不变；须有明确拒绝和依据|
|pay_late_fee[0]|pepperoni余额30、late_book_count=2、单价3|只扣6，余额24；原实现late_book_count仍2，不能凭直觉改成0|

前两题还依赖认证、库存、会员或非restricted分支、借阅上限。负对照约束只有登录/余额充足，不要求Rdup。删除Rdup通常只改变27的允许判断，25可继续正确；反转为“必须已借”才可能同时让25误拒、27误允。语义依赖不意味着模型一定依赖文档：不重复借书是强常识，return规则也给线索。

25的9调用正确参考含未公开日期方法，属于**底层方法级**结果；27已验证只用公开3工具后拒绝；fee为公开4调用。都由审计构造，不是数据发布的唯一gold trace。

### 5.3 原生Oracle实测反例

`env/evaluator.py:105–152`在Strict环境重放**Actor自己所选同一轨迹**，比较响应与最终DB；268–271主要以action名称确认goal，没有完整绑定目标用户/对象；276–300核对图和约束。它确实看数据库，但不是独立正确业务状态。

|离线输入|原生success|结论|
|---|---|---|
|25空轨迹|false|能拒绝部分空执行|
|27空轨迹|true|应拒绝的任务无需查验或答复也通过|
|25借错Pride and Prejudice|true|7个公开工具；错对象漏检|
|25为mario借错书|true|7个公开工具；错用户/对象漏检|
|fee正常支付后额外充值50，余额74|true|5个公开工具；额外业务动作漏检|
|fee双重支付，余额18|true|7个公开工具；重复扣费漏检|
|fee错误密码返回false后继续扣费|true|4个公开工具；认证缺陷与评价缺陷互相掩盖|

所有核心假阳性已用公开schema范围的轨迹重验；不依赖隐藏日期方法。其他方法级结果和AST函数级0/false参数反例另标范围。`library.py:426–431`先设置登录用户再返回密码判断，Strict重放共享该缺陷；`evaluator.py:171`按期望值truthiness决定比较，0/false可绕过比较。以上不代表真实模型错误率。完整输入/响应/终态见 [probes.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/probes.json)。

必须新增独立业务目标、用户/对象绑定、授权成功、动作次数、全状态副作用白名单、拒绝理由与事实验证。可复用约束树、动作图、原环境与重放作为诊断次指标。不能只补一句“检查最终DB”而仍与错误同轨迹重放比较。SOP余额条款“more than”与实现`>=`还存在clean边界冲突，正式扩展前必须裁定，不能归因于退化。

### 5.4 规模重算

|域|任务|整政策+参数结构簇|重复簇|重复簇覆盖任务|默认政策+参数|实际发布SOP匹配|发布SOP匹配且全参数默认|
|---|---:|---:|---:|---:|---:|---:|---:|
|bank|134|66|28|96|29|2|2|
|dmv|97|35|25|87|23|3|3|
|healthcare|124|76|22|70|14|4|2|
|hotel|195|121|38|112|18|3|3|
|library|66|30|13|49|18|26|18|
|online_market|172|81|40|131|9|4|1|
|university|42|8|3|37|33|33|33|
|总计|830|417|169|582|144|75|62|

144/830=17.35%只是代码默认一致；发布文档逐字一致75/830=9.04%，再要求全部参数默认62/830=7.47%。library保守18/66=27.27%，不是18题已通过语义/Oracle验收。417结构簇不等于417个自然来源；只有7个程序渲染域模板。150种原子表达式形式不是150条已验证共享规则。当前深查1组2+1，研究Oracle验收数0。定义与任务索引见 [inventory.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/inventory.json)。

**结论：修复协议后可独立形成“生成SOP→Skill→业务操作→专用Oracle”的机制链，但不具独立自然文档代表性。** 与CQA可共享干预和分析框架、分别验证假设，不能拼成一条自然政策执行链，不能混算总成功率。

## 6. Anything2Skill 输入兼容性：已测与未测

本轮调用原版loader、rule-only分节和recommended窗口；用网络/子进程禁用保护，未创建LLM/embedding client。**当前正式outline=llm，以下不是完整推荐配置生成实测**。真实outline可能改善或恶化覆盖，必须后续核查实际产物。

|来源/表示|实际结果【T】|判断|
|---|---|---|
|CQA整个documents.json|5714109字符被当1文档，229窗口|不能把652来源合并使用|
|CQA原始单doc dict传data=|empty text异常|contents不会映射到text/raw_text，需适配|
|单doc JSON文件|9234字符，0strict窗口；fallback6000/3534|合法可读，不是完全不能生成；结构语义未解决|
|保序CQA Markdown|7761字符、21sections、12windows|可加载；29/110块文本未在任何excerpt出现|
|SOP原始Markdown|6569字符、7sections、7windows|borrow/pay规则入窗，后半若干动作和AND/OR总说明未入窗|
|Box官方v2025原始JSON|255158字符、1section、3windows|目标operations/action未入窗|
|Box请求契约ref展开后包成Markdown JSON代码块|7613字符、4sections、1window仅356字符|目标契约仍漏；简单加Markdown围栏不够|

CQA转换保留块序、标题相对层级、列表和可见文本，另保存原始块→偏移；链接/内联样式等可能损失。目标51/52同窗，但全局排除46和另一条件60缺失。29/110是文字出现诊断，不是规则遗漏率：metadata、重复文本和跨块作用域需单审；也不能由分窗直接断言最终Skill错误。

Box必须通用地将schema渲染为保层级文本，保留每个对象的required、oneOf、enum、nullable、默认/省略含义、错误响应及JSON Pointer，并处理本地ref。不能按测试题手工写教程，更不能重写官方算法来得到好结果。输入转换是工程适配；自然来源缺失、任务只是事实查找、同政策假设不成立是数据/方法不匹配，格式转换不能解决。

各类完整来源均可能包含多个技能。DirectDoc和Skill必须从**同一冻结表示**分支；不能DirectDoc获得完整文档而Skill只给目标摘要。若来源本身包含示例、重复说明，应保留并标记语义等价证据；局部退化仍有可恢复信息是要研究的机制，不是应隐藏的干扰。

## 7. 开放检索得到的新候选：Agent-Diff＋官方技术文档

这不是只读论文后推荐。本轮获取并打开了224条原始任务、all/train/test三份文件（train/test两split）、Box初态、四域文档、Box实现、assertion engine、API评测封装和测试文件，实际执行了无模型评分反例。

固定版本：Agent-Diff `3bb9c40707df23d89e5dbc0e40c424ba38c69ff8`；Box官方OpenAPI `a4f3e23d5bd01d9f4398bc1a764d410df3e607a7`。本地根目录为 `C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/` 下 `agent-diff` 与 `box-openapi`。许可分别MIT、Apache2.0。下载为最小稀疏内容；未启动服务/数据库或真实Agent。

### 7.1 原始任务与规模

真实 `all_numbered.jsonl` 的box_131整条记录如下（`answer/info`本来就是编码JSON的字符串，保留这种结构）：

```json
{
  "#": 75,
  "question": "Create a Hub named 'Economic Data' and add the 'macroeconomics' folder to it.",
  "answer": "{\"assertions\":[{\"diff_type\":\"added\",\"entity\":\"box_hubs\",\"where\":{\"title\":{\"eq\":\"Economic Data\"}},\"expected_count\":1},{\"diff_type\":\"added\",\"entity\":\"box_hub_items\",\"where\":{\"item_id\":{\"eq\":\"1973339758\"}},\"expected_count\":1}],\"ignore_fields\":{\"global\":[\"created_at\",\"modified_at\",\"content_created_at\",\"content_modified_at\",\"purged_at\",\"trashed_at\",\"etag\",\"sequence_id\",\"sha1\",\"file_version\",\"path_collection\",\"created_by\",\"modified_by\",\"owned_by\"]}}",
  "test_id": "box_131",
  "test_name": "Level 2: Hub Setup",
  "service": "box",
  "task_horizon": 3,
  "operation_type": "C+search",
  "entity_scope": "single",
  "information_availability": "implicit",
  "prompt_ambiguity": "low",
  "info": "{\"service\":\"box\",\"seed_template\":\"box_default\",\"impersonate_user_id\":\"27512847635\",\"eval_type\":\"actionEval\",\"tools_required\":[\"POST /hubs\",\"GET /search\",\"POST /hubs/{id}/manage_items\"]}"
}
```

`question`才是Actor任务；`answer`是评价断言，`info`含seed_template、impersonate_user_id、eval_type、tools_required。后者尤其不能全量给Actor，否则泄漏正确接口路径。`#`是行序号，`test_id`是真实ID；task_horizon等为任务元数据，不是已验证的最短调用数。初态在 `backend/seeds/box/box_default.json`，不是答案字符串。

重算224题：Slack59、Box48、Linear57、Calendar60；train179/test45。随包文档有Box26、Calendar37、Linear19、Slack27个endpoint条目，共109；README的108端点统计与当前文件口径不同，不能混用。93组工具元数据有≥2任务，只是共享端点候选；Box13题涉及Hub，7题涉及manage_items。当前仅深查一组Box共享契约2+1，不能声称已有93条语义规则簇。四服务也不等于109个独立来源。数据与探针见 [agentdiff_stats_and_probes.json](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/agentdiff_stats_and_probes.json)。

### 7.2 官方来源与模拟器一致性

Box官方 `openapi-v2025.0.json` 有24paths，包含POST /hubs及manage_items；基础 `openapi.json` info.version=2024.0有187paths，包含POST /folders。两者同commit但不同API版本文件，构成一个有来源清单的Box文档包，不能说v2025单文件覆盖所有任务。基础文件Git blob与固定树匹配 `0e76798a73008a10829ad4ffad9bf7e5ae3f0798`。

目标请求契约路径为：`paths[/hubs/{hub_id}/manage_items].post`→`requestBody.content["application/json"].schema`→HubItemsManageRequest→properties.operations.items→HubItemOperation→properties.item→HubItemReference.oneOf。固定文件1967、6494、6554、6607行；action枚举add/remove，操作元素required为action/item，引用分支要求type/id，header box-version=2025.0。**父对象未声明operations required**，不能擅自补上。随包简化文档将其标必填且只写file/folder，官方还支持web_link；二者不是同一原始真值。

模拟器 `backend/src/services/box/api/routes.py:2024–2115`有add实现，但remove返回未实现；官方响应207与模拟返回行为也须逐项对齐。`database/operations.py:1708`负责关联。原始官方规则比程序渲染SOP更独立，但源文本—模拟器偏差可能造成clean错误。当前限定add/file/folder子集仅减少风险，**未完成服务端端到端一致性验收**。

### 7.3 Oracle同样有缺口

直接调用原版AssertionEngine输入合成diff【T】：box_131正确新增通过；空diff失败；**加到错误Hub仍通过、正确新增后删除无关文件仍通过**；box_141任意8个错误文件加到错误Hub仍通过。原因是真实answer断言只查存在/数量，没有完整绑定新Hub、正确集合及全部副作用。

评测API静态调用链 `platform/api/routes.py:635–774`→compiler→`core.py:140–147`→`assertion.py:403`。API使用可信diff，但没有额外全局unexpected-change惩罚；strict只限制匹配行的字段，不能理解成所有未声明变化都失败。这些是**底层反例＋端点静态证据，不是服务E2E攻击或真实Agent实验**。必须重写外部任务目标断言，不能直接采用论文式“state diff天然可靠”的推断。

### 7.4 为什么仍排优先候选

它同时提供真实软件接口的独立官方文档、可执行沙箱、多个共享操作任务及可信快照框架，比CQA更接近动作Skill，比SOP更接近真实外部技术文档。代价是schema适配、模拟器一致性与专用Oracle。**目前只是更值得验证，尚不比旧方案“更已验收”。** 文档复杂、接口新也不保证现代模型不会；论文中的with-docs结果不等于我们当前模型的自主Skill效应。[官方论文](https://arxiv.org/abs/2602.11224)、[固定代码](https://github.com/agent-diff-bench/agent-diff/tree/3bb9c40707df23d89e5dbc0e40c424ba38c69ff8)、[Box规范](https://github.com/box/box-openapi/tree/a4f3e23d5bd01d9f4398bc1a764d410df3e607a7)。

## 8. Skill 提取研究如何选评测任务：可借鉴的方法与不能照搬的协议

这是针对用户补充问题进行的定向核查，不是论文名单。完整证据包括 [提取评测复核](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/related_evaluation_extraction.md) 与 [Skill使用评测复核](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/related_evaluation_skill_use.md)。前者含当前原版README及固定SkillGenBench runner/真实任务检查，后者含SkillsBench真实任务、Dockerfile与verifier检查；论文结果均未本地复现。

### 8.1 最贴近本项目的四类设计

|研究及版本|评测数据/任务怎么来|如何判断Skill作用|值得借鉴及不能直接照搬|
|---|---|---|---|
|Anything2Skill，2606.09316v1，§4|qsv官方文档的表格处理任务；gh官方指南，110来源→179Skill|同gpt5.4比较Base、Skill、RAG(top3)、Skill+RAG|优先操作手册→真实产物方向；其Skill检索注入不等于自主文件读取；未定位完整公开任务/verifier包|
|SkillGenBench，2605.18693v1，§3.3–3.4|固定仓库/文档→知识图→场景→任务/测试→模型筛选及人工审核；187题中28 CodeDoc、36 DomainDoc|task-conditioned与task-agnostic，固定执行器/产物验证，pass@3|先冻结来源库再跨任务复用值得借鉴；任务筛选、强制Skill和信息隔离存在不能照搬之处|
|SkillRefine/PIMS-Bench，2609.30674v1，Method/Experiments|真实软件手册、专家CASE、COM接口；140任务，40构建/100留出，五层结构难度|NoKnowledge、DocOnly、SkillBase、SkillRefine；冻结库跨四backbone；按需read_skill；格式/solver检查及(table,row,column,value)操作元组match F1|复杂协调、留出和四臂最贴近；含专家与Oracle修订，不是纯文档；商业PIMS/Xpress及公开任务包未取得|
|SkillsBench，2602.12670v4，§3/Appendix M|87专家工作任务、8域；真实终态与确定性测试，按人工工作量分层|with/no/self-generated Skill，标准渐进披露；任务不点名Skill|自主选择、终态Oracle值得借鉴；现有Skill有效性不是来源提取因果，也不自动证明跨题共享规则|

论文链接：[Anything2Skill](https://arxiv.org/html/2606.09316v1#S4)、[SkillGenBench](https://arxiv.org/html/2605.18693v1#S3)、[SkillRefine](https://arxiv.org/html/2609.30674v1)、[SkillsBench](https://arxiv.org/html/2602.12670v4)。Anything2Skill首页链接ECNU-ICALK/AutoSkill，与当前方法线一致；3月AutoSkill论文主要是对话提取与库存分析，不能混为6月文档提取评测。qsv/gh原始完整评测包在本次范围内未找到，不能用论文成功率反推出任务数量和Oracle。

**SkillGenBench特别值得学习，也特别不能直接套用。** 论文Stage4将无语料成功率≥20%或全语料≥50%的题退回改写，Stage5再用测试反馈优化参考Skill。这刻意形成挑战分布，不能据此估自然任务整体收益；我们的DirectDoc对照若也按DirectDoc失败筛题，便改变了要比较的任务分布。本地Git再次核验HEAD为 `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`，`git cat-file -t`确认为commit；身份不只依靠sgb_tree.json字段。实际读到的 [claude_runner.py:223](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-15/SkillGenBench/scripts/claude_runner.py:223) 要求先调用Skill；339–355挂载原docs、tests及可选groundtruth。默认noskill模式也未必无外部文档。我们应复用经审查的数据，保持现有自主Terminus和separate verifier，不能复制默认runner便宣称自主因果。[固定提交](https://github.com/QuantaAlpha/SkillGenBench/tree/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d)。

实际读到的soundfile-task-010在题目直接写seek500、无参数truncate、重开验证的顺序；023要求读8、相对回退3、再读5。看似技术任务且同库，也不自动证明同一条未泄漏规则的依赖。28道CodeDoc应作为定向复查池，不能因有test.sh全盘准入；无需重新启动大规模候选罗列。

SkillsBench官方贡献规范则明确：强模型无Skill能成功并不自动淘汰任务，可靠性/效率也可受益；任务写终态而不是解题步骤。当前网页版本与论文版本不同，代码main未固定commit，因此本报告仅作设计参考。实际JAX任务verifier核对数值/形状/ID唯一性，不检验用了Skill；Dockerfile把reference复制进/app/reference，隔离仍需runner确认。成熟benchmark的“确定性”同样不能免除隐藏边界审计。[官方贡献规范](https://github.com/benchflow-ai/skillsbench/blob/main/CONTRIBUTING.md)、[实际JAX任务](https://github.com/benchflow-ai/skillsbench/blob/main/tasks/jax-computing-basics/task.md)。

### 8.2 其他研究提供的具体提醒

- **DocPrompting**从社区tldr和StackOverflow需求出发，再连接manual/API；tldr按命令不交分割，CoNaLa要求每个dev/test样本至少含一个训练未见函数并避免帖子重叠，并非所有函数完全不交。tldr9187对/1879命令主要是文本评分，CoNaLa仅100测试题具执行测试；`oracle_man`是文档ID，不是业务Oracle。可借真实需求和源映射，不可称其已证明持久Skill提取。[论文v3 §4–5](https://arxiv.org/html/2207.05987v3#S4)、[官方数据](https://github.com/shuyanzhou/docprompting#data)。
- **SkillNet-Gym**最新版159合成任务，把2–5技能组成DAG，并构造执行/测试工件；可借链、分叉、汇合的语义依赖设计。但其文档可能按已有Skill反向搜集或合成surrogate，且按指定GLM-5.1的三次无Skill试跑筛选，不能视为对所有模型都必须依赖Skill，也不能当自然文档→Skill的现成真值。尚未逐题审查自然来源比例。[v3 §5/附录14.1](https://arxiv.org/html/2603.04448v3#S5)。
- **Agent Skills Can Be Harmful**用同任务、同初态、同模型的匹配运行定位Skill功能失败和成本回退；307精选案例不能估总体发生率，单次差分也不是源退化因果。可借“错误规则→动作偏移→失败断言”的证据表，加入修复/反向/sham和重复。[v1 §III–V](https://arxiv.org/html/2608.11888v1)。
- **SkillJack**对150条AppWorld-format轨迹研究污染传播，但论文ASR是路由与正则/LLM风险代理，明确不是业务环境执行。可借分阶段测量，不能用路由命中替代任务失败；论文给出的代码链接本次404，未称复现。[v1 §4.1](https://arxiv.org/html/2608.03509v1#S4)。

文献对本项目最直接的启发是：**从真实可验证工作需求选题，按规则依赖结构分层，先冻结库再评测未参与构建的任务；不要靠“长任务”“无Skill必败”或强制读取来证明Skill价值。** 源、生成物、使用与结果四层都要独立测量。原版A2S的qsv方向更容易复用当前文件Oracle，但在原始任务包取得前，只能是后续候选，不编造“官方qsv题”。

### 8.3 回到实际任务：已经找到的复杂候选及其缺口

本轮继续从Agent-Diff原始224题中抽查8条完整记录，见 [复杂任务笔记](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/complexity_followup.md) 与 [原始JSON](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/complexity_candidates_raw.json)。**发现更强候选，不等于已证明它们需要Skill。**

|真实候选|有价值的依赖结构|为什么暂不能准入|
|---|---|---|
|calendar_177|八周周五系列；只延后6月29日实例、只取消7月6日；授予权限并另建独立事件|原断言未绑定recurringEventId/originalStartTime，两个取消断言可同时0，未完整验证八次规则|
|calendar_178|每月第一周二系列；两次不同例外；最终删除整个系列|最后删除遮蔽中间错误；必须可信事件记录与独立实例集合检查|
|calendar_184（控制）|只建一次性事件Emberglass Kiln Glow|不依赖parent/instance作用域；仍需核对正确时区和目标日历|
|box_155|CSV首行domain分组、目录/移动/标签；只将≥2文件的子目录加入Hub；排序manifest|原Oracle未检查成员、分组、移动、标签和manifest内容；CSV正文真值未取得|
|box_163|size条件标签、全量fomc集合入Hub、目录存在性、报告/评论一致性|原Oracle只检存在/非null等；缺成员集合和分支；本轮seed仅确认size676600、4个fomc文件|
|box_117（控制）|普通创建文件夹|不依赖Hub操作契约；适合控制而非主题任务|

Calendar177/178共享的真正操作知识是：系列parent ID用于枚举instances；若用PATCH/DELETE直接改/取消单次occurrence，应使用instance ID而非误操作整系列，并保持其他实例。正确编辑parent recurrence中的EXDATE等业务等价方式也应接受。其来源在随包Calendar文档`GET .../instances`的description与eventId说明；[Google官方周期事件指南](https://developers.google.com/workspace/calendar/api/guides/recurringevents)也说明实例、parent及originalStartTime。官方网页本次已读但未做本地版本快照；Calendar seed/实现尚未核查，因此这组是**复杂主任务优先核验方向**，不是完整已冻结实验包。

源规则退化理论上会使177改错/删错整系列；178可能提前删系列但终态看似正确；184无影响。Oracle应接受业务等价合法实现（例如正确的例外表达），不能强制必须调用instances来制造依赖。常规响应、schema及已有知识可能提供绕行，需实际校准。Box155/163更长，但共享Hub契约仍可能从报错恢复；额外步骤不自动增加该规则的知识需求。

因此最终排序是：**先用Box小组验收工程，再审Calendar实例作用域等复杂规则族的知识依赖；CQA作独立泛化，SOP为机制备选。** 不把小组跑通当任务选型完成，也不因发现复杂题就跳过Oracle。


## 9. 统一准入矩阵与选择顺序

|候选|独立真实来源|可复用操作/决策|共享规则任务|实际执行|研究Oracle|当前角色|
|---|---|---|---|---|---|---|
|官方API文档＋Agent-Diff|有；技术规范，非长篇自然政策|强候选；仍需生成验收|端点候选多，语义深查很少|本地模拟器存在，未本轮E2E|原生有反例，需加强|优先主方案准入核验|
|ConditionalQA|有，652政策URL|条件决策可行，简单问答弱|两个真组深查，词面候选多|原生仅回答|需严格包装及语义标签|自然文档泛化辅助|
|SOPBench|程序渲染7域|规则和动作明确|政策须分簇；一真组|有，部分公开接口不闭合|已证严重假阳性|受控机制备选|
|AppWorld|应用API文档与模拟环境同源|多步应用操作强|本轮未重做规则簇审计|官方执行环境较完整|仍需对所选目标检查|Agent-Diff失败后的主执行候选复审|
|SkillGenBench|文档/仓库来源混合|提取任务最贴近|按来源复用可借鉴|部分任务可运行|此前已发现需逐题审查|协议优先借鉴，筛子集而非全盘采用|
|SkillsBench/有害Skill研究|通常从已有Skill出发|任务实践性强|任务Skill对不等于同源规则簇|执行可验|因任务而异|自主使用/负效应设计参考|
|Git/Terminal-Bench|真实技术文档可外配|多步操作可用|需另做规则映射|当前Git链已通|Git现有9断言可复用该任务|工程校准，常见命令知识旁路强|
|τ-bench/τ²-bench|业务政策多为环境内规范|条件、多轮决策强|政策族可复用|依赖用户模拟等额外环节|状态与策略仍须审计|不是自然来源问题的直接解|
|PIMS/SkillRefine|软件手册等更贴近|专业任务强|需核查公开评测包|专有软件门槛|公开可复现性未证|研究设计参考，暂不主用|
|DS-1000/DocPrompting类|真实库/工具文档可链接|程序生成/接口知识|需重建规则簇|可执行输出或答案验证|题目特定|后备任务构造范式|

没有依据把全部候选Oracle说成可靠或不可靠。AppWorld本轮只补读官方论文与历史审计，未做与本轮三者同深度的源码验收；[AppWorld](https://arxiv.org/abs/2407.18901)、[τ-bench](https://arxiv.org/abs/2406.12045)、[τ²-bench](https://arxiv.org/abs/2506.07982)、[DS-1000](https://ds1000-code-gen.github.io/)提供进一步入口。RoTBench重点在工具扰动，RuleArena在规则决策，CL-bench在上下文学习；改变工具接口或只做QA均不能直接替代本研究来源退化链。此次不因Harbor接入方便而推荐Terminal-Bench为主。

## 10. 前两位方案：具体最小实验与适用限度

以下全为【I】，保留原始任务，不声称已产生Skill或成功运行。三题是**工程和机制试点，不是正式论文样本量**。研究主方案须通过第11节知识依赖门槛后扩展到复杂规则族。

### 方案一：Agent-Diff＋Box官方来源包；CQA另作泛化

**来源/版本：**第7节固定的两份Box官方规范；最终按独立于题目的“Hub及文件/文件夹查询管理域”完整范围冻结，含输入、响应、错误、示例、引用。当前只做过子集转换诊断，正式完整渲染尚未实现。输入为确定性schema→保层级Markdown，每段有外部Pointer映射；原版生成算法不变。

**共享目标规则：**新增Hub成员须对目标hub_id使用manage_items，operations元素以action=add并携带与对象类别一致的item{type,id}；不是把源文件移动到一个普通文件夹。前提是已创建Hub且已定位正确源对象。两个任务共享“add关联契约”，一个folder、一个file分别使用不同类型分支；不能把所有输入参数统称同一个原子规则。

|真实任务|正确状态（专用Oracle拟定，不是原生answer全文）|其他依赖|
|---|---|---|
|box_131：创建Economic Data Hub并加入macroeconomics文件夹|恰好一个新Hub；成员关联到该新Hub、folder1973339758、type=folder；原文件夹父级不变|查找、建Hub、版本header、关联目标|
|box_141：建Model Evaluations Hub，加入agent-diff-research内全部模型评测JSON|一个新Hub，成员集合精确为原seed中该文件夹1173971943的8文件且都关联新Hub；无额外成员，无源文件变更|文件夹定位、枚举/筛选、可能分页、多对象操作|
|box_117：在investments中新建Analysis_2026|一个新folder，name精确、parent_id=5610825569，无Hub变化|搜索+POST /folders；不依赖manage_items|

8个已核对源文件ID为8647156721、2466872085、2713928524、4373646747、3094163556、2112512450、1238342109、2211626350；完整名称见统计JSON。原始题与answer见 [真实2+1](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/alternatives/agentdiff_raw_2plus1.json)。

**正确Oracle：**从服务端可信前后快照绑定actor用户与新建对象，精确目标集合、关系、类型和业务字段；新增/修改/删除全量差异白名单，只忽略经证明非业务性的时间等字段；错误hub、错误文件、漏一/多一、无关删除、只建Hub未加成员、空轨迹均失败。box_141的文件含义筛选仍需人工确认seed文件集合，不能只看≥8。

**Agent可见：**原始question、正常账号上下文、固定中性全API调用设施；不可见answer、tools_required、seed全DB、verifier、后端源码。保留正常响应/错误，记录其中规则信息。完整生成包全量安装并哈希；不得只选目标Skill。DirectDoc挂载同版本source-only文档及中性索引；Skill臂不挂clean来源。A0无这两种材料。通过HTTP代理或终端CLI访问隔离本地服务，不使用真实Box账号/线上变更。

**C/R/U：**C保留完整契约；R1去除目标add枚举/操作结构的某处，测冗余补偿；R2对预先列明的全部等价表达做相同局部语义破坏，单独报告；U同量破坏不涉及三任务的web_link/其他独立操作说明，先人工确认不影响file/folder子集。不得仅改一段说明却忽略正确curl示例，然后宣称“规则已不可恢复”。删除或错误action可能使131/141均缺成员；117理论不受影响。工具报错和预训练可恢复，实际影响未知。

**局部修复/反向破坏/sham：**在审计副本而非canonical上，仅修目标规则并保持其他正文、索引和资源固定；反向向clean副本注入同类型错误；sham只改格式。对规则被编译成多处/多个Skill时，以预先登记的完整位置集合干预，避免只改一份留下正确副本。

**读取/采用：**记录索引、正文、resources、目标Pointer映射跨度进入模型请求的时间，关联后续API参数/目标选择；先按全部随机分配trial估计效果，再作探索性读取分层。修补只改善依赖任务、负对照和sham稳定，才支持目标机制；读过+成功不够。

**风险/停止：**当前两Hub题可能很简单；只用于工程验收。在独立选型校准集发现A0近天花板或正常工具总能补齐时，应将该族预先归为低知识依赖层，并增加复杂族，不能在正式分配后因不读Skill或没有效应删掉trial。正式实验的零效应与工具补偿均保留。若官方规则与模拟器不一致或正确动作不能通过专用Oracle，先停止，不把infra失败算Skill退化。更复杂原始任务方向见第8节；未验收不补造成功结论。

### 方案二：SOPBench固定政策机制子集＋CQA独立自然文档辅助

**来源/任务：**固定library原始Markdown，borrow_book25/27＋pay_late_fee0；Rdup、初态和正确状态均见5.2，不重写题目，不按题目生成SOP。source-only Markdown直接交原版加载；完整包安装与DirectDoc同方案一。此方案排名第二是因为规则允许/拒绝可精确干预，不是因为具备真实自然SOP。

**先决条件：**公开工具所需日期信息路径必须闭合；原生提示中的完整clean政策、按答案筛工具及约束提示不得同时暴露；Actor只见原user_prompt和中性工具。业务状态/实现放独立服务。若必须修改官方任务语义或工具业务行为才能跑，应另列“研究者改编任务”，不得仍称原生SOPBench验收。

**Oracle：**25绑定pepperoni/Beloved/到期日/库存；27验证合法拒绝及重复事实、无状态副作用；fee绑定pepperoni、只扣6一次、其他字段按原实现不变。认证成功必须来自可信响应，不能读state_tracker标志作为唯一依据。要求空拒绝、错书、错用户、额外充值、双扣、错误密码所有反例失败。Actor自己提交的状态/轨迹不能作为唯一真值。

**C/R/U：**C原文；R删除或反转Rdup分开；U房间预约不相关条款，长度和破坏形式配对。删除主要影响27，不要求25也变错；反转可诊断两相反分支；fee不应变化。冗余解释、常识和正常查询均记录。局部修补、反向破坏、sham及读取分析同方案一。

**停止：**臂间额外clean政策泄漏、公开接口不闭合、目标Oracle未通过反例，均阻止升级。Program模式的保护作用须单列研究；A0常识足够用于独立校准和分层，不是正式实验结果排除理由。即使全部试点通过，也只能支持“程序规定政策的机制效应”；需CQA独立泛化，不能将两个域拼成一条自然文档执行链。

## 11. 知识依赖验收：回应“任务太简单就不需要Skill”

不能在看见退化效应后才保留有利题，也不能只挑读取过Skill的trial。拟采用**独立校准集→冻结准入规则→未参与选型的正式任务/来源**流程。一个规则族应有多个表面不同的真实任务，至少覆盖正确使用、例外/拒绝或作用域区别、非依赖控制；替换数字不是自动独立任务。

第一阶段后续获准时先比较四种信息条件：A0（无来源/Skill）、D-C（clean DirectDoc）、S-C（原版clean生成完整包）、G（人工审核正确规则包，仅诊断）。环境、模型、预算、正常帮助和错误固定；不强制读文件。D-C对A0测试外部知识是否有价值；S-C对D-C测试预编译影响；G对S-C定位生成质量；读取/采用记录测试信息是否实际进入决策。Skill无需绝对不可替代，但应有可测的可靠性、成本或错误传播差异。

|校准结果|解释和动作|
|---|---|
|A0稳定接近满分，其他臂无可靠成本/稳定性收益|任务可能已被内部知识/接口覆盖；不作主要成功率效应样本，保留为低依赖对照|
|A0低，D-C/G也低|更可能任务、工具、推理能力或Oracle问题；不能当“很需要Skill”的证据|
|D-C/G可解，S-C差|可能编译/检索/读取失效；是可研究失败，不能删掉clean失败美化结果|
|S-C成功且不读正文|审查index是否已含目标规则，再区分先验知识与索引效应；不直接归因为正文|
|已暴露错误规则，局部修补/反向破坏无方向响应|尚无传播因果证据；可能工具保护、信息冗余、替代路径|
|依赖任务随规则干预变化，控制与sham稳定|支持局部机制，仍需跨来源重复与不确定区间|

不要对3题单次pilot设“90%通过”一类伪精确阈值。正式校准前预注册模型/预算、重复数、可接受效应量与区间、任务排除原因。若用A0表现筛选知识敏感子集，必须另报全集表现、筛选规则和比例，并在独立保留集确认，不能把所选效应外推到全部任务。

更值得筛的任务特征：版本特定而非通用语法；同时涉及多个有真实相互关系的条件；例外会改变允许/拒绝；父对象与子对象作用域不同；中间动作必须保持不变量且最终Oracle能识别；同Skill可迁移到另一对象/情境。不得为“难”而增加无关浏览、调用或冗长输入。

## 12. 最少工程增量、成本与实施顺序

所有增量放在研究适配层，**不改变原版Anything2Skill**。

|工作|直接复用|最少新增|
|---|---|---|
|来源与生成|原公共入口、独立空库、阶段产物、canonical注册|source-only转换、版本hash、Pointer/block→rule映射、实际入窗审计|
|任务与环境|Harbor/Terminus容器和终端循环|dataset adapter、固定fixture、隔离API/工具桥、可信快照/事件导出|
|Oracle|separate verifier隔离与结果保存|逐任务目标/关系/副作用/拒绝断言、正反例及不可篡改输入|
|信息条件|完整包冻结安装与索引|DirectDoc只读路径和发现协议、跨臂泄漏检查、metadata/正文/span可见性|
|实验记录|预算持久原则、原始请求与轨迹|新独立budget scope、通用assertion结果协议、规则族/来源/重复层级manifest|

估计（工程人日，非实测，不含模型实验和多域人工标注）：CQA严格答案接口1–2；共享DirectDoc/span1–2；library受控3题约3–6，若日期接口/认证缺陷需变更则另估；Agent-Diff Box三题约4–8，包含来源schema转换、服务隔离/快照、Oracle与反例，若本地环境或版本一致性不通过则停止重估。Calendar复杂时序Oracle额外成本未验证，不能承诺与Box三题相同。

优先级：

1. **先审阅报告并冻结研究准入协议。** 明确允许哪些格式转换、真实规则真值、Actor可见信息、难度/知识依赖评价和失败归类。
2. **获准实施后先做零模型任务与Oracle验收。** Box3题为最小服务/快照/目标验证；同时从复杂任务族人工建立规则依赖证据，避免工程跑通后才发现题太简单。CQA辅助先用guardian组，不用train-41作为核心。
3. **通过后才申请有界模型校准。** 先clean实际窗口、完整生成包质量及A0/D-C/S-C/G；不能用rule-only探针替代实际outline覆盖。当前旧Gold停止账本不续跑。
4. **再进入C/R/U与机制干预。** 不预先大规模生成退化数据。每个候选方案3任务×3版本×2路径=18主trial，加3A0/3G=24；Skill有3次pipeline生成而非3次HTTP。此数量仅为计算模板，尚不包括重复、修补、反向破坏、sham，也不是本轮授权。

正式扩展按来源/规则族分层，任务嵌套在规则族中，生成重复与执行重复分开。报告配对效应和区间；同一来源几十次重试不能替代多来源。Agent-Diff4服务、SOP7域不足以自行证明宽泛文档泛化；CQA增加自然文本覆盖，但各数据集分别估计，不加权拼成一个总体成功率。

## 13. 最终问题逐项回答与否证条件

1. **旧CQA＋SOP组合不是当前最优主方案。** CQA无法独立承担操作结果；SOP自然来源弱、原生Oracle和接口有缺口。
2. **调整主辅关系。** CQA是自然条件规则泛化集；SOP是受控政策机制备选；主候选转向真实技术文档＋执行环境。
3. **Agent-Diff更贴近完整链，但不是现成答案。** 其原始任务可获取、官方来源可冻结，仍必须补Oracle和来源一致性，并证明复杂任务知识依赖。
4. **建议一个主执行数据集＋一个自然文档泛化集。** 不必同时建设两个主环境；第三个SOP机制集仅在确有机制价值时启用。
5. **组合必要性在验证不同假设，而非补齐各自断链。** 主执行集测动作和状态传播；CQA测自然政策的条件/例外保真。每组都要独立完成自己的完整链。
6. **最利于跨任务传播的是共享规则族，不是某个名字。** 要有同一规则的不同前提/对象/范围实例，以及不依赖规则的控制。
7. **最可能不读Skill的是常见Git、数字查找、普通CRUD和常识SOP。** 复杂任务也可能不读；需实际暴露和干预证据。
8. **当前框架最易复用Git；但科研适配优先。** 新环境复用Harbor外壳，业务Oracle必须专用。
9. **最小先验收Box131/141/117，SOP25/27/fee0是备选机制组。** 前者不直接作为论文主题；复杂任务族应先人工核查再知识校准。
10. **首候选失败时不强行救推荐。** 若Agent-Diff在固定工具子集仍无法对齐真实来源或复杂目标不可验证，转审AppWorld的规则簇与Oracle；SOP只保留窄机制结论，不能替代自然操作主张。
11. **硬准入：** 来源/初态/任务/工具版本固定；无答案泄漏；规则依赖可被独立定义；合法参考路径可执行；Oracle全部正反例通过；actual clean窗口可核查；观测链有受控正负校准；已预注册知识依赖分层、旁路记录和分析。不能要求先观察到正效应才允许纳入正式数据。
12. **研究问题不用为数据集改成一般QA或工具鲁棒性。** 需要调整的是任务选择、适配和评价；若自主Agent总体不采用Skill，或错误可被正常工具信息恢复，应接受“传播条件不成立/存在缓冲”的研究结果，而非强制使用制造成功。

## 14. 证据索引、可复现边界与待验证清单

本轮证据根目录：[audit_final_review_2026-10-20](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20)。

|证据|文件/入口|
|---|---|
|CQA全量统计、真实样本、逐块证据、scorer反例|[cqa/notes.md](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/cqa/notes.md)、stats.json、audit.py、scorer_probes.json、archive_identity.json|
|SOP全量政策匹配、真实任务、环境/公开接口反例|[sop/notes.md](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/sop/notes.md)、inventory.json、probe.py、probes.json、source_hashes.json|
|原版加载/窗口、源码SHA和转换映射|[generator/notes.md](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/generator/notes.md)、probe.py、probe_results.json、paternity_block_map.json|
|Box官方规范原始契约与输入失败探针|[generator/box_notes.md](C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_final_review_2026-10-20/generator/box_notes.md)、box_probe.py、box_probe_results.json、box_base_source_check.json|
|Agent-Diff原始2+1、seed查验、assertion反例|alternatives/agentdiff_raw_2plus1.json、agentdiff_stats_and_probes.json、probe_agentdiff.py|
|历史工程状态|[最新Gold](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/report.md)、原始observer/request/assertions文件|

固定源码下载只为审计；未运行其安装脚本或模型SDK。首次Git/API获取失败、限流和后续固定URL获取都不作为“文件已验证”的替代；只有实际读取、commit树/值核验与哈希才计入F。Box基础规范通过固定URL取得并验证Git blob。审计探针是人工构造输入测试，不能计为Agent成功率或实验效应量。

**未验证：**任何新来源生成Skill的稳定性；当前LLM-outline真实覆盖；新任务服务E2E；复杂任务的共享规则全量真值；新增Oracle；现用模型的无Skill基线、自然读取和因果采用；全部来源/任务的可用比例。所有拟新增接口、阈值、干预和预算均需用户审核后实施。

方法说明：本报告使用 scientific-critical-thinking 技能组织证据层级和因果审查；引用 Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)。此方法引用不是数据集适配性证据。

**本轮到此为研究和审计交付，不自动进入工程实施或模型实验。**
