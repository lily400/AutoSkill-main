# 研究总审计：文档退化、Skill 生成与下游 Agent 表现

审计日期：2026-10-25（Asia/Shanghai）。审计对象：D:/AS/AutoSkill-main/degradation_failure_lab 当前本地工作树。Git HEAD：6fac24ebd24954ae5c5f97393a64d343015aa0c0。未访问远程仓库或外部论文网站。

**总判断：研究问题合理，已有可复用的实验执行骨架和真实探索结果；尚未形成支持“文档退化通过特定 Skill 缺陷影响任务表现”的完整证据。已有基础足以推进一个受控退化小试点，无须无限增加 Clean 任务。**

**下一步唯一任务：以 Scrapy024 的 FTP 默认 overwrite=True 规则为锚点，完成一轮最小受控退化试点。** 同一任务内先冻结简短协议、补齐必要条件绑定并完成零模型验收，再在当前隔离环境中运行新的 NoSkill / CleanSkill / DegradedSkill 对照。详见第八节；不是直接重放历史 ID，也不是立即启动大规模实验。本轮只审计和写本报告，没有实施该任务。

## 1. 审计范围、证据等级和研究边界

### 1.1 本轮实际执行

只读检查代码、JSON/JSONL、日志、SQLite 账本（mode=ro）、产物字节和 SHA-256。未执行测试、模型请求、Agent、Skill 生成、退化构造或容器实验；未修改代码、配置、预算、门禁和历史文件。本报告是唯一新增交付文件。

当前本地工作树已有 10 个 tracked 修改，另有未跟踪的 041 case、共享 pilot/freeze/usage 模块、配置、测试和实验产物。这些均是审计开始前存在的成果；不能只用 HEAD 判断当前能力，也不能称它们都已提交。

本轮重新计算并核对：

- common-pilot 历史保护清单的 **2,124 个文件：全部匹配**；
- common-pilot validation 所列 **14 个代码/文档指纹、6 个证据指纹：全部匹配**；
- s41d001 及两个 workflow-check 各自的 **45 个冻结 Skill 文件和 manifest：全部匹配**；
- s41d001 账本：4 次 HTTP，两个条件 DONE；workflow-check-001/002：各 0 次 HTTP、条件 NEW；
- 保存的最终测试日志确为 **80 项通过**。这是历史测试证据，本轮没有重跑；Windows 11 项包含重叠覆盖，不能相加为 91 项独立测试。[E01][E02]

其他生成清单按当前文件复核：s24r005 489 项、r13fe557951 366 项、s41r002 427 项、s41r003 988 项均匹配。哈希证明字节与保存记录一致，不证明规则语义正确或当时环境绝对安全。[E03][E04]

### 1.2 证据标签

- **事实 F**：本轮读取的代码/产物，或明确标识的历史真实运行记录。
- **静态推断 S**：从当前调用关系判断，未在本轮运行。
- **研究建议 R**：未来应采用的设计，不代表已实现或已获模型预算。
- **待验证 H**：现有证据不足；不将 UNKNOWN 写成 FAIL 或 PASS。

研究链路应拆成五个可分别观测的环节：

~~~text
同源文档条件 → 实际窗口/证据 → 最终冻结 Skill 规则
                                 ↓
                     可发现 → 正文进入上下文 → 外显动作
                                                   ↓
                                            独立 Oracle
~~~

研究中“高质量”至少包括规则正确、条件/例外完整、来源可支持、适用范围正确；技能数量、注册成功、任务得分不能单独替代这些指标。

当前生成属于 **source-only、task-curated**：生成器不接收题目答案，但来源集合由官方任务包策划。041 的四个文档属于同一任务包，不是四个独立任务或四个独立实验样本。可以研究这个范围内的生成效果；不能自动宣称完全任务无关的通用语料学习。未来若多个任务复用同一来源集合，应冻结一个来源×条件×独立生成重复的 bundle，并让这些任务共同使用；不要按任务重新生成后当成独立来源。[E05][E06]

## 2. 当前真实进度

### 2.1 分任务、分阶段

| 阶段 | Scrapy024 | Scrapy041 | Pydantic001 / BeautifulSoup037 | 旧五个 Clean case 与 GCH |
|---|---|---|---|---|
| 数据/任务/Oracle 映射 | feed-exports 与 19 项原断言接入；主目标 FTP 默认值 | 四文档、任务键、10 项原断言接入；兼容评分运行时 2.13.0 | Pyd001 有源/case和工程 Oracle；BS037 有离线接口，真实评分入口未实现 | 五 case 有来源；GCH144/164 有 clean/相关删除/无关删除输入与任务 |
| 导入/窗口/提取/编译/注册 | s24m005→s24r005 完成，19 draft/spec、15 最终包 | r13fe557951→s41r002→s41r003 完成，35 窗口、50 draft/spec、45 最终包 | 未找到真实生成记录 | 五 case 有最终生成；GCH 六臂均真实完成 |
| Skill 质量 | 有 FTP 规则定位和其他后端缺陷；非全部规则合格 | 已证实目标 allow_offsite 规则丢失、一次合并内容不一致 | 无生成质量结论 | 有旧人工报告/词项分析，非完整统一语义标注 |
| 版本冻结 | s24d001 的 15 包和输入/配置/hash | s41d001 的 45 包、来源及 live registry 元数据 | 工程资产冻结不等于 Skill 冻结 | 各生成 run 有快照；GCH 有部署/任务记录 |
| 真实下游 | 6 次 Agent，27 次 HTTP | 2 次 Agent，4 次 HTTP | 均不能计为真实模型试验 | Git Gold 1 次；GCH 六次 Agent 共 18 次 HTTP |
| NoSkill / CleanSkill | 已有各 3 次，旧网络策略，探索性证据 | 已有各 1 次，新网络隔离；Clean 正文读取 0 | 尚无真实对照 | Git A0/A1 未跑；GCH 三文档条件但缺 NoSkill |
| 失败分析 | 断言、提交、读取、请求可追溯；未形成因果验证 | 提供/读取与任务成功可区分；该对照无任务失败 | 仅工程错误/夹具分析 | GCH164-c01 有可见/隐藏评分分歧，不能直接归因退化 |
| 文档退化 | 无完整退化→生成→Agent 试验；有局部内容呈现微实验 | 仅 clean | 未开始 | **GCH 已开展早期真实退化试点**；不能写全项目未开始 |
| 机制干预 | 领域身份/单窗口形式 A/B 已做，非最终 Skill repair/damage/sham | 未做 | 未做 | 未找到完成的规则修补/反向破坏/sham 下游干预链 |
| 推广性 | 与041同属Scrapy生态 | 不是第二个独立领域 | 工程准备不能补作实证样本 | GCH与旧case提供探索素材，尚无统一协议的跨来源机制验证 |

依据：[E03]–[E16]。表中“未找到”限本轮本地 runs、results、注册表和对应报告核查范围，不等于不可实现。

### 2.2 Scrapy024：不能丢掉已有 NoSkill，也不能追溯升级隔离

实际运行根目录：runs/eval/sgb/scrapy-task-024/s24d001。原始 batch_results.json、逐臂 result、请求与轨迹共同支持：

| trial | 原 Oracle | 整题通过 | FTP 专项断言 | 观察到访问的 Skill 数 | 完整正文进成功请求数 | HTTP |
|---|---:|---|---|---:|---:|---:|
| NoSkill1 | 18/19 | 否 | 失败 | 0 | 0 | 4 |
| CleanSkill1 | 19/19 | 是 | 通过 | 5 | 2 | 4 |
| NoSkill2 | 14/19 | 否 | 通过 | 0 | 0 | 5 |
| CleanSkill2 | 19/19 | 是 | 通过 | 1 | 1 | 5 |
| NoSkill3 | 13/19 | 否 | 失败 | 0 | 0 | 4 |
| CleanSkill3 | 17/19 | 否 | 通过 | 0 | 0 | 5 |

六次当时均 infra_ok=true，无 native exception。NoSkill 整题 0/3，Clean 2/3；**FTP 专项为 1/3 对 3/3**，两种指标不能混用。[E03]

CleanSkill2 完整读取的 341bd0da-1d52-5a40-87dd-44477cdec422 在第33、63行写出 FTP True，随后提交通过 FTP 断言。CleanSkill1 的两个完整正文属于 S3/标准输出技能，不能把“读过任意 Skill”自动算作“读过目标 FTP 规则”。CleanSkill3 未观测到完整正文也通过 FTP，表明知识补偿或索引作用需要保留为解释。[E03]

这些是有价值的链路和初步效果观察，但运行采用旧 no-network 策略，DNS/ICMP 等隔离不满足当前标准。**存在历史访问通道，不等于已有证据证明读取答案；本次没有找到其实际利用这些通道的证明。** 旧结果保留、单列；新隔离下的正式比较必须重新建立同期对照，不覆盖原六次。[E07]

### 2.3 Scrapy041：链路真实完成，目标规则测量却不敏感

最终生成 s41r003：offsite 2 窗口/3 draft/3 spec；downloader 4/4/4；request-response 25/35/35；spider 4/8/8。跨文档协调后最终45包，不能把各文档 upsert 数简单相加。恢复链累计201次 HTTP、752,311 个已观测 Token；是一次生成的断点续跑，不是三次独立生成。[E04][E06]

s41d001 两组模型均为 openai/gpt-5.4-mini-2026-03-17、temperature=0、reasoning=none；每组2次请求，均原 Oracle 10/10。两份提交 SHA-256 完全相同：
74a8d078e1daaddfd82fa7d97c959ce0d6d655ee6236fe5fcb02d3e4e0a01a07。

NoSkill 输入/输出 Token 为2631/429；Clean为13866/488；合计17,414，6400 cached input 已包含在输入中。不存在可据此确认的实际金额账单。[E02]

Clean 的45包已安装、已发现，索引确实进入成功请求；model_read_ids为空，完整正文匹配数为0。两臂均在首次答复写出正确 metadata，不能说 Skill 正文帮助完成任务，也不能说索引完全没有作用。未观察到正文读取是自然加载策略下的有效结果，不应为了展示效果删除该 trial。[E02][E08]

两个 workflow-check-20261025-001/002 是真实容器、零模型工程验收，账本均0次；不是额外的 Clean 重复。当前共享工作流经过这些验证，但新增共享入口本身尚无新的付费试验；历史 s41d001 使用其重构前入口。[E01]

### 2.4 其他工作：已做、未做的边界

- **Pydantic001**：demonstration.json 保存原 Oracle 正例16/16、交换顺序负例14/16，model_calls=0、real_generation_runs=0、real_agent_runs=0。属于工程示范；原 Oracle 的 candidate-reported logs 和较宽松顺序检查仍有限。[E09]
- **BeautifulSoup037**：有 adapter/scoring/exports/smoke 和离线合同。实际 Agent 构造仍抛 OFFLINE_ONLY，scorer 后端仍抛 NOT_IMPLEMENTED；不能计为第三个已跑通任务。[E10]
- **旧五 Clean**：raecd75e08b34（qsv select）、rd9ced750fa54（qsv sort）、rab9a070dfa59（docker cp）、r18307cee4f4c（git restore）、r64cee24fae18（ripgrep）有生成完成记录；另有保留的失败/恢复历史。不能把五个生成 case 算成五个已验证下游任务。[E11]
- **Git 旧下游**：p1-c-recovery-20261019-001 仅 Gold 跑1次、2HTTP、2755 tokens、Oracle 1.0，正文读取0；NoSkill A0与自动Skill A1未跑。父 smoke 为启动导入失败、HTTP0。[E12]
- **GCH144**：c00/g5096b80fec23、c01/ge8fd1fce11e3、c02/g51e170757750，最终7/4/7 Skills，三臂下游成功。
- **GCH164**：c00/g56a1f8969fff、c01/g142d4e60d9a0、c02/g74da73df31d9，最终8/11/9 Skills；c00/c02成功；c01隐藏5/5但可见/手工评分 AssertionError，合取任务结果失败。六臂总生成260HTTP、Agent18HTTP，正文读取均空；144-c00 有观察器日志恢复，不能当作重新运行。c01/c02是 paragraph_delete_v1 相关/无关删除，已有真实退化试点，但旧网络、缺NoSkill、未读取正文及评分语义分歧限制机制解释。[E13]

### 2.5 与旧报告不一致之处

1. 024旧 readiness 报告“真实运行待执行”已被 s24d001 六次记录更新；旧路径由归档/relocations追踪，不判文件丢失。
2. 041注册表同时保留 NOT_RUN 字段和 CLEAN_PILOT_COMPLETED / s41r003 / s41d001，adapter.json亦有旧字段。以实际 run 为准；这是状态元数据漂移，应小幅同步，非重新做实验的理由。
3. 旧 README 的“只支持单文档恢复”和“无下游自动评分”已落后于当前实现。
4. 旧五case报告所述“其他四份导出与case001重复”不能继续列为现存故障：本轮逐项比较当前四组各11个JSON，与case001完全相同的文件数均为0。
5. “全项目尚无退化实验”错误；正确说法是 **SGB主线未完成受控退化闭环，GCH有早期探索试点**。[E01][E05][E11][E13][E14]

## 3. 框架审计：哪里可靠，哪里尚不足

### 3.1 上游真实调用链与适用性

当前调用为 scripts/lab.py → degradation_lab.cli → ExperimentRunner → official adapter → AutoSkill4Doc.extract_from_doc。runner把本条件输入复制到独立 run/inputs，创建空 SkillBank，保存配置、输入清单、代码/提示词快照和调用记录；adapter实际向生成器传该输入目录及来源元数据。rules.json 是分析清单，不在这一调用的文档输入中。[E15]

041选择的是 **每份文档保留身份、共享本次任务来源包的 SkillBank**。四文档分别导入/窗口提取；整体完成提取后分别编译，再注册到同一运行级 registry。不是四份原文作为一个无边界大 prompt，也不是四个隔离 bank 最后人工拼接。

SkillBank不只存文件：注册阶段有相似检索、变更分类和协调，实际 s41r003 有跨 downloader/request-response 的 merge/update。它支持协调，不保证语义正确。恢复从前一轮复制 checkpoint/state；当前恢复代码拒绝部分不明确状态，保留旧 run，不把每次恢复当空银行重来。[E04][E06][E15]

适用性限定：

- 这些英文技术 Markdown 能进入当前文本流程；**能处理不等于每一段都获得同等提取机会**。
- 当前A2S与两次最终运行保存的166个上游文件匹配，但包含此前已有 lab-preprocess-v1 的两文件预处理修补。domain_type=scrapy 由case显式覆盖。论文必须称为这个冻结实现/配置，不能称完全未改原版。
- domain identity/内容形式微实验表明前端呈现和领域身份会影响候选；不是只凭“默认类型不行”推定所有领域。当前不应临时调阈值、关键词、prompt或merge算法来使目标题通过。
- 独立空bank应按来源包×条件×生成重复隔离；同一次多文档处理保持bank连续；恢复保持原状态；下游重复复用冻结包。[E06][E15][E16]

### 3.2 已证实的质量问题及定位边界

**041目标规则丢失：真实证据，不是仅看最终关键词。**

source的 offsite.md:57–63、downloader-middleware.md:651–654支持放行规则。s41r003保存的35个window.text中，完整放行条件未在这两份文档的窗口中保留；仅 request-response 的窗口37645b12-7e47-58bd-80b3-e52ca212fd93包含特殊metadata键列表中的 allow_offsite。support fea089cf-a808-5831-a38f-7d84b3b0a457仍有该键，50个draft、50个spec及45个最终包均不再有它。结合最终offsite正文未写该例外，可判目标规则没有完整传到最终技能。[E04][E06]

因此最早可定位缺口包括前端窗口暴露，键名在形成draft时也未显式保留；**不能统一归咎“注册把规则合没了”**。为什么相应段落未进入选中窗口，需要更细的section/filter日志分析；本轮不把“窗口没看见”进一步猜成具体阈值原因。

**041合并不一致：真实产物。** Skill 76394f52-1f81-5c91-8ae3-fd51b942c5e1 的名称/触发/示例仍指中间件注册，说明/正文转成请求指纹定制；另有34个包保留 Therapist 风格标题。前者是可能影响发现和执行的形式缺陷，后者是模板残留；没有下游错误动作证据时，不把它们直接写成失败原因。[E04][E06]

**024并非所有规则都错。** FTP默认True在最终两个包中存在；同包对stdout追加的说法存在冲突。原024只判默认overwrite等19断言，不覆盖FTP显式False与真实APPE服务器行为。必须按规则分析，不能给整包简单贴“正确/错误”标签。[E03]

**来源追踪可用，但语义对应未系统填写。** artifacts.py已有window/support/draft/spec/skill链和输入行匹配；evaluation.py支持原子规则、来源行、trace引用和生成行的人工记录及校验。然而当前未找到正式 evaluations/*.json 记录。041冻结已用最终live registry纠正注册汇总旧版本/旧supports，不改Skill正文。旧artifacts导出主要沿spec关联，跨文档merge后分析应同时核对最终live registry，不能只信旧聚合字段。[E04][E08][E17]

### 3.3 Agent、Oracle和信息边界

| 边界 | 当前可支持的判断 | 限制 |
|---|---|---|
| 上游输入 | 当前adapter只加载run/inputs；已保存实际模型请求。041的201个请求定向扫描未见任务键、eval.py、groundtruth、目标具体URL等 | 关键词扫描不是完整无泄露证明；上游为受信任本地进程，不是文件沙箱。本轮未发现任务答案混入实际输入 |
| Skill交付 | 安装文件hash、索引内容、成功HTTP payload、文件读取分别记录 | registry成功≠交付；bootstrap为读frontmatter而cat文件≠模型读正文 |
| 041 Agent文件隔离 | 独立任务工作区；源文档/隐藏测试/Oracle/参考答案/库源码不挂给Agent；api_key_forwarded=false | 控制器可信且持密钥/宿主Docker权限，不能把控制器权限误报成Agent权限 |
| 当前网络 | Docker实际none namespace、接口/路由/权限以及双栈负例；s41d001 Agent/候选/评分共6份报告PASS | 不外推到旧024/GCH，不是内核漏洞或恶意宿主的形式证明 |
| 041候选/Oracle隔离 | 候选在独立非root、只读rootfs、无网络容器收集普通Scrapy对象；可信评分容器只接收JSON观测及提交源码，执行原10项断言 | 普通对象/边界用例已验证；任意自省、自定义对象、跨测试全局状态的完全等价性未证明 |
| Oracle能力 | 024原19项，041原10项；041正确/错误/异常17场景验收 | 官方Oracle本身覆盖有限，原分数不能冒充全部任务语义或真实爬取验证 |

当前网络真实验收覆盖IPv4/IPv6 TCP、UDP、DNS/53、ICMP、ICMPv6、raw、packet、vsock；loopback本地通信保留。旧sidecar即使切public，main仍不接入其网络。证据包括Docker inspect、内核状态、受控可达正对照与隔离负例，非只读策略名称。[E07][E18]

041官方原运行时2.12.0没有目标allow_offsite分支，适配固定2.13.0，原eval.py字节不改。真实中间件方法诊断证实metadata放行、缺失拒绝、dont_filter也可放行；后者仍被官方题目拒绝。这是内存方法调用、network_requests=0；**真实爬虫/HTTP拦截为UNKNOWN**。[E18]

041 Oracle逐项寻找Spider、allowed_domains、请求，没有完全强制它们属于同一个Spider；中间件修改禁令主要做静态AST字符串检查。其对象桥把非标准对象编码为opaque。因此需分别报告“官方得分”和“目标规则外显动作”，保留原分数，不能私自修改断言后仍称原Oracle。[E19]

### 3.4 预算、门禁和异常处理

当前上游run入口仍检查case指定gate的status=PASS；041 gate中的150次/Agent0是旧授权记录字段，不是全部后续实际预算。续跑真实配置、resume.json、execution.json保存了后续累计额度及使用量，下游另有授权与账本。不能用旧proposal或gate静态字段推定历史越权，也不能把PASS理解为网络/Oracle已验收。[E15][E23]

上游在下一请求前检查累计HTTP和已观测Token，恢复继承父历史；Token是停止阈值，不是硬账单上限，缺usage可能低估，失败POST是否已计费未知。下游Ledger持久预留每次尝试，未知/失败不退款，batch.started防重复启动；HTTP请求数、输入估计、实际usage分别记录。异常/预算不足应保留为独立状态，不把部分生成或候选存在当作完成。freeze_generation会拒绝非completed、有错误或身份不匹配的生成来源。[E08][E23]

本轮没有更改任何门禁或预算，也没有新增审批流程。未来试点预算应写在自己的配置中，不借用已耗用的历史额度。

### 3.5 按严重程度排序

本轮未发现足以推翻 s41d001 的新增已发生 P0 隔离故障。以下等级按其会阻断的**结论**划分，不表示所有实验都已作废。

| 等级 | 问题与事实状态 | 影响 | 最小必要处理 |
|---|---|---|---|
| P0（历史正式结果准入） | 旧024/GCH真实运行采用可通DNS/ICMP的旧策略；实际答案泄露未证实 | 不能纳入“经当前严格隔离验收”的正式主分析 | 保留探索结果；新试点用当前网络入口和新ID、同期对照。无需删历史或重跑所有探索 |
| P0（若声称机制因果） | 目前没有完成的文档退化→规则改变→相关正文曝光→错误动作→特定断言→干预反转闭环 | 现有成功率差或缺陷共现不能证明机制 | 最小规则证据表＋预注册微试点；后续有信号才repair/sham |
| P1 | 041完整目标条件在window已缺失；最终规则缺失；两组均成功且正文0读 | Clean目标规则有缺失下限、任务有知识补偿/满分上限，作为首个损伤诊断样本信息量低 | 保留为负/边界案例；首个试点优先024，不为041手补答案或调算法 |
| P1 | 新公共pilot只接受一NoSkill一CleanSkill；041 skill_conditions只有CleanSkill；024入口仍有固定s24r005与六臂签名 | 配置名称改成Degraded并不能自动正确装载，DirectDoc也未正式接通 | 实施试点时仅扩展条件→冻结包绑定/必要024薄接口与验证，不重写Agent或Oracle |
| P1 | 观测可证明交付/部分读取，缺按目标规则对齐的统一动作标签；读过任意Skill不等于读目标规则 | 无法自动支持规则级关联 | 使用现有request/tool/submission/JUnit填小型规则表；缺证据标UNKNOWN |
| P1（未来统计） | summary只给success_rate_among_scorable；041将缺提交、candidate_timeout等列为unscorable | 若未来忽略这些分母会造成选择偏差；当前041两臂不受影响 | 预注册全分母、Agent自身失败与基础设施错误区分，分开报告条件成功率/失败率/infra率 |
| P1（外推） | 同库任务、生成重试/恢复、多个断言和多个Skill相互依赖；来源集合任务策划 | 不能把187登记项、45Skill或10断言当独立N | 来源家族为聚类单位；分离生成重复与执行重复；限定结论范围 |
| P2 | 上游规则清单/人工质量协议存在，但正式评价记录未填；跨文档最终registry与聚合spec可不同步 | 分析不完整、可能错用旧版本支持 | 分析以冻结最终包和live registry为准，复用evaluation验证，不新建大系统 |
| P2 | 注册表/adapter/README及预算proposal保留旧状态；新增共享代码本地未提交 | 容易误判进度或误启动旧命令 | 后续小幅状态同步；当前按run身份/ledger/manifest审计，不手改历史 |
| P2 | 无正式多来源统计、执行顺序未随机化、温度0不消除随机性、金额未知 | 不支持显著性/稳定性/成本优势 | 后续预注册重复与顺序；分别报告已观测tokens、未知usage、实际账单 |
| P3 | 自动归因模型、全自动选题、通用任意Oracle接口、可视化平台 | 非当前闭环所必需 | 暂不开发 |

依据：[E01]–[E20]。P0“机制证据缺失”是论文主张的阻塞，不是要求把已有工程成果判失败。

## 4. 失败归因：现在应做到的最小程度

本地旧研究设计已列11类失败和repair/damage/sham协议；它是方案，不是已实现的自动归因系统。与《Agent Skills Can Be Harmful》的联系，本轮只依据本地文献核查卡：成对轨迹、功能失败与效率变化分类值得借鉴；未取得该论文原文的本地副本，不复核其具体数值/完整分类，更不把SkillTriage视为本项目现成可调用组件。[E21][E22]

| 层次 | 已有 | 缺口 | 可接受证据/结论 |
|---|---|---|---|
| 失败分类 | native异常、HTTP/预算、候选hash、评分stdout/JUnit、failure_category | 部分类别将Agent错误和infra混合；需统一研究标签 | 可说失败位于提交/执行/环境/评分；不自动归于Skill |
| Skill质量 | 原文行、窗口/support/spec、最终文件、人工报告；041遗漏实证 | 规则/条件/例外统一标注和复核未完成 | “规则遗漏/冲突已观察到”；词项缺失只能作定位线索 |
| 行为关联 | 安装、index、文件访问、成功request正文、工具、提交 | 缺目标规则片段→具体外显动作→assertion连接；部分/分页读需人工核对 | 024 Clean2可建立规则可见与正确动作关联；不等于因果 |
| 因果验证 | 旧协议；领域/呈现单窗口微实验 | 无目标最终Skill repair/damage/sham的配对下游验证 | 只有执行干预并排除路由/长度/其他规则改变，才讨论局部机制 |

**推荐先把最小协议直接写入下一个试点，不先开发完整归因系统。** 当前日志基本够用：对每个预注册规则填一行，字段如下：

~~~text
source_bundle / condition / generation_run / trial_id
rule_id + 条件、动作、默认值、例外
source_hash + 原文行
window_id + 实际请求片段；support_id；draft_id；spec_id
final_skill_id/version/hash + 对应行；缺失/错误/完整/UNKNOWN
索引暴露；目标片段是否进入成功模型请求；tool/action编号
提交hash + 对应代码行；Oracle断言名/原始结果
第一个可定位失效环节；并存问题；证据路径；审阅者/分歧
~~~

已确认目标规则缺失却任务通过：报告“知识补偿或其他信息通道足以完成，具体机制UNKNOWN”；未读取正文却失败：不能说正文中的错误规则诱发错误；有错误规则且失败但无动作证据：只报共现；无效基础设施试次单列，不能计成功，也不能静默删掉。

自然加载主分析保留所有预定trial，即使未读正文。若后续需要“给定规则已暴露”的诊断，另设显式正文暴露条件，并在Clean/Degraded两边使用同一策略；它回答不同问题，不能混入自然加载成绩。不要仅筛选“成功读取”的trial后称随机对照，因为读取行为本身可能被退化影响。[E08][E17][E20][E21]

## 5. 各实验条件的必要性与公平性

| 条件 | 回答的问题 | 何时用 | 当前状态 |
|---|---|---|---|
| NoSkill | 没有所生成技能时，任务靠已有知识/指令/工具做到什么程度 | 首个新隔离试点同期加入；无需为老024凭空补“缺失”对照 | 024各3次、041各1次已存在；GCH缺 |
| CleanSkill | 固定干净来源和生成方法时的工作流基线 | 所有退化比较的配对基线；冻结后不修补 | 024/041可复用包 |
| DegradedSkill | 文档处理改变是否传播到Skill和下游 | **现在应做的小规模下一步** | GCH有早期实例；SGB公共pilot还需最小条件接线 |
| DirectDoc | 同样文档退化在直接读取与预先生成Skill两条工作流中是否不同 | 首个受控试点验证流程后、正式宣称Skill特有风险前 | SGB正式路径未实现；现有说明/设计不算运行 |

明确决策：

1. **已有Clean足以支持小规模退化试点设计和启动准备。** 024有正确目标规则、正负Oracle、自然读取与任务差异，比041更有诊断价值。现有证据不足以跳过新环境的验收，也不足以直接做论文规模退化。
2. **NoSkill不是全项目缺失。** 新024试点需同期NoSkill用于新隔离/新协议校准；这是控制环境变化，不是重复补做已经存在的旧结果。
3. **DirectDoc对最窄问题“退化是否影响A2S+Agent”不是逻辑必要项；对最终解释“预生成Skill是否放大/缓冲退化、相较直接读文档为何不同”是必要对照。** 建议列入最终论文计划，但不阻塞首个三条件试点。
4. DirectDoc应提供同条件完整源文集合、固定读取/检索工具和在线预算；不能把Clean原文偷偷提供给DegradedSkill，也不能为与短Skill等长而截断DirectDoc关键证据。生成成本和执行成本分开；没有匹配总算力时不称等算力对照。
5. repair/damage/sham只在有可定位规则差异、可验证正文/动作链且任务对该规则有敏感性的候选上实施；不要求“差异显著”才允许诊断，也不为找显著性反复挑例。先锁开发例/验证例和所有筛选理由。
6. repair只恢复源文支持的通用规则；保持ID、名称、description、索引位置/路由等不变，检查所有重复规则位置；damage从确认正确的版本开始；sham匹配编辑位置/近似长度但语义不变。人工修补是机制干预，不能冒充Anything2Skill自动生成的Clean/Degraded主成绩。[E21]

公平性应冻结模型标识/响应实际模型、提示词、库/镜像、网络、预算、超时、工具、任务初态、官方指令和Oracle。NoSkill/Clean/Degraded唯一资料处理差异必须清楚；允许索引/正文长度和实际花费不同，那是工作流效应的一部分。执行顺序预先随机交错、每trial独立工作区；不得把前次提交/交互状态带入后次。预算耗尽、无Skill生成、未读正文也保留在预注册的全流程结果中，另做分阶段分析。

## 6. 从当前进度到论文实验的阶段计划

顺序采用 **Stage 0 → Stage 2（最小协议）→ Stage 1（同期控制）与Stage 3合并执行 → Stage 4 → Stage 5 → Stage 6**。先规定如何解释失败，再消费预算；新Clean/NoSkill作为同一次退化小试点的控制，不单开一轮无限扩充基线。Stage 6的分母、指标、来源划分应在Stage 2预注册，最后才汇总统计。

以下预算均为未来计划单位，不是本轮执行授权；实际HTTP、Token与金额不是同一种额度。温度0不保证确定性，断点恢复不计独立重复。

### Stage 0：研究框架和有效性核查【当前必须；本报告已完成静态/历史部分】

| 项目 | 内容 |
|---|---|
| 目标 | 确定哪些证据可保留，哪些必须在新协议中重新验证 |
| 已有基础 | 当前网络修复、024/041独立评分、冻结/预算/日志与本报告 |
| 待办 | 在下一次实际启动前核对新实验绑定的代码/镜像/规则资产；只对变化的执行路径做必要零模型验收 |
| 复用 | network_isolation、runner、scorer正负夹具、runtime lock、原始历史记录 |
| 新增代码 | 审计本身不需要；只处理试点实际阻塞的条件绑定/记录问题 |
| 模型/Agent | 本阶段不需要模型；未来验收可用确定性容器流程，不能算真实Agent结果 |
| 预算/重复 | 模型0；对实际待用入口一次有效零模型正负验收，失败保留 |
| 交付 | 本报告；未来新实验的readiness、manifest及隔离报告 |
| 验收 | 指令/Oracle/候选hash一致；正确提交通过、目标错误拒绝；隐私文件边界与全部网络准入通过；账本模型0 |
| 停止/进入 | 任一隔离/Oracle绑定失败先停止；通过后进入同一小试点，不扩展全数据集 |

### Stage 2：最小失败分析协议【当前必须；在下次试点内完成】

| 项目 | 内容 |
|---|---|
| 目标 | 对目标规则建立可核查的五段证据链，避免事后讲故事 |
| 已有基础 | 024的FTP断言、正确冻结正文、Clean2读取证据；evaluation与observer已有 |
| 待办 | 固定一个rule_id、目标/非目标断言、质量标签、正文曝光判据、失败分母和停止策略；把旧024六臂及041两臂填成小表作协议检验 |
| 复用 | rules.json、artifacts.py、evaluation.py、skill_usage.py、request/tool日志、candidate、JUnit |
| 新增代码 | 优先人工表/JSON；现有字段足够则0。只有缺失必要关联时增加小型导出字段，不建自动裁判 |
| 模型/Agent | 协议与历史回填模型0 |
| 预算/重复 | 模型0；每条关键判断需原始证据定位，争议显式保留 |
| 交付 | 一份试点protocol（含预算计划）和一张rule_trace表；不重复生成多套报告 |
| 验收 | 8个旧trial各有真实ID、分数、可见性与UNKNOWN；所有目标来源/Skill行和断言可定位；不得用成功推断使用 |
| 停止/进入 | 若关键日志缺失，只对那个字段标UNKNOWN；不因此无限回填历史。协议冻结后进入Stage1/3 |

### Stage 1：必要的Clean和NoSkill控制【当前必须；与Stage3同批，不新开选题工程】

| 项目 | 内容 |
|---|---|
| 目标 | 给新隔离环境和新条件协议建立同期参考 |
| 已有基础 | 024完整15包、正确目标规则、现成Agent/Oracle |
| 待办 | 新ID绑定当前公共隔离；复用未修改s24r005冻结包；核对其生成版本/设置可与退化臂一致；使用同一任务初态、预算与评分 |
| 复用 | s24r005、s24d001原始包作为只读来源；新的冻结目录；024 scorer/runner/observer |
| 新增代码 | 024必要的薄绑定、明确generator/condition映射；不继续使用固定六臂历史入口强行塞新条件 |
| 模型/Agent | 需要新的同期NoSkill和Clean Agent各1次；不默认重新生成Clean |
| 预算/重复 | 首轮2个trial，每trial最多6HTTP，共最多12；计入Stage3合计18，不能重复累计成额外预算 |
| 交付 | 新试点NoSkill/Clean原始轨迹、独立评分、Skill使用证据 |
| 验收 | 两条件公平性与运行有效性通过，记录成功/失败均可；Clean正文不读本身是结果，不伪造读取 |
| 停止/进入 | 环境/评分异常中止并保留；自然加载不足时不临时加指令重跑，按协议决定后续诊断 |

如旧生成配置无法与退化运行保持同一冻结方法版本，才需要独立新Clean生成。应先确认这一条件再花钱；不能因为目录旧就自动重跑。

### Stage 3：单规则、小规模受控退化【当前唯一优先的实际实验任务】

| 项目 | 内容 |
|---|---|
| 目标 | 检验文档操作是否改变目标规则的传递，以及是否出现外显动作/评分变化 |
| 已有基础 | 024目标正确的Clean包、明确Oracle、已实现的degraded输入manifest校验；GCH退化经验 |
| 待办 | 仅选一种可解释的结构/证据呈现退化，冻结操作及diff；保留目标事实，预先列出扰动哪些重复支持位置及非目标变化；未动副本作为真实补偿保留，不事后删除；独立空bank生成1个Degraded包；补最小三条件绑定，冻结后执行 |
| 复用 | case/conditions/input schemas、runner导入/恢复、freeze_generation、公共网络/预算/Oracle/observer；不手改最终Skill |
| 新增代码 | 必要的条件→各自generator/run/bundle映射和验收；固定输入变体可作为数据文件，不要求先开发通用退化引擎 |
| 模型/Agent | 最多1次新的Degraded完整生成；再运行1个Degraded Agent，与Stage1合为3个trial |
| 预算/重复 | Agent合计最多18HTTP。上游单独申请一次有上限生成预算：历史024累计81HTTP/264,685已观测tokens可作量级参考，不保证新运行够用；禁止无限恢复/重试。首轮每条件1次，仅工程/探索 |
| 交付 | 1个输入操作/diff/可恢复性记录；独立Degraded生成与冻结；3个trial原始结果；统一rule_trace/小结 |
| 验收 | 输入预定义差异100%可定位；非目标事实检查完成；无跨条件bank污染；三臂身份/hash正确；目标规则各层能标保留/遗漏/错误/UNKNOWN；模型和评分异常不冒充效果 |
| 停止/进入 | 一轮完成即停并检查。若规则/行为不变，记录零效应；若没读目标正文，记录自然加载瓶颈；若先有infra故障，先修该点。不得换多个退化直到“找到失败” |

**验收不要求Degraded必须失败。** 成功观察到不变、补偿或零效应也可以完成这轮试点。若采用删除唯一规则，则应另标“不可恢复信息损失”条件，不能称结构可恢复退化；GCH段落删除不能无条件充当本试点的语义模板。

此轮复用一次Clean生成和一次Degraded生成，生成随机性与处理效果未分离。它用于验证测量链；进入正式比较前需给两个条件均增加独立生成重复，不能只在一个固定bundle上大量重复Agent。

### Stage 4：机制验证和DirectDoc【后续必要；按论文主张选择规模】

| 项目 | 内容 |
|---|---|
| 目标 | 区分生成规则损失、发现/读取变化与规则遵循；比较直接读文档和预生成Skill的退化差异 |
| 已有基础 | Stage3可定位候选；旧11类协议/repair/damage/sham设计 |
| 待办 | 接入同条件DirectDoc Clean/Degraded；对选定规则做Original/Repair/Sham，必要时Clean/Damage/CleanSham；锁名称/索引/非目标规则；使用未参与挑补丁的验证实例 |
| 复用 | 同Agent、隔离、Oracle、预算、文件交付、请求及动作日志；无需新的Agent框架 |
| 新增代码 | DirectDoc的资料安装/暴露与hash检查；局部干预diff和操作清单。先人工构造核查，后按重复需要写脚本 |
| 模型/Agent | 需要；不调用模型自动“判因果”替代独立证据 |
| 预算/重复 | 按已观察方差事前定上限。工程诊断可先每臂1次；稳定性验证必须成对重复、固定最大次数，不按显著性不停追加 |
| 交付 | DirectDoc配对结果；干预diff/hash；目标与非目标动作/断言结果及全部失败记录 |
| 验收 | 同源同条件；资料权限和在线预算可比；正文/规则曝光有证据；patch仅改变预定语义；sham不改变目标规则；评分对象绑定通过 |
| 停止/进入 | 无可定位候选时不强造repair效果；若sham同样改善，或路由/多规则同时变，限制机制解释。保留零效应后决定扩展或收窄主张 |

局部repair改善只支持artifact级干预；要说“自然文档退化经该规则产生损失”，还需文档操作先导致该规则变化，并排除其他共同改变。一次修改奏效不是自然中介比例估计。

### Stage 5：任务与来源扩展【后续必要；大规模迁移为可选】

| 项目 | 内容 |
|---|---|
| 目标 | 判断试点发现是否跨规则、来源和领域成立 |
| 已有基础 | 187身份登记、28 CodeDoc/36 Domain文档候选及旧审计；Pyd001工程入口 |
| 待办 | 依据预注册准入选少量不同来源家族；先核实规则/任务/Oracle依赖，保留选中/排除理由；划分开发与验证来源 |
| 复用 | sources/tasks registry、已有数据审计、公共pilot、独立评分模式、规则表 |
| 新增代码 | 每任务只写必需的提交/对象观察与评分适配；无法普遍用024布尔桥；不重构公共目录 |
| 模型/Agent | 准入先零模型，再有预算的Clean/NoSkill与退化 |
| 预算/重复 | 分批封顶；首批少量来源用于估计源间方差。最终N由精度/功效目标决定，不能承诺“凑够几个任务即论文成立” |
| 交付 | 来源分组、规则依赖矩阵、纳排表、新任务验收与完整条件结果 |
| 验收 | 每题正负Oracle有效；每来源有完整配对条件和冻结；无同源当独立来源；未完成/被拒任务可追溯 |
| 停止/进入 | Oracle/规则依赖不足则不纳入主分析；新任务仍普遍NoSkill满分/不读取时收窄结论或改研究场景，不靠扩大数量掩盖 |

Pydantic001可作工程候选，但其评分语义需先核实；不能仅因已有demo就优先认定科研价值。041保留为不敏感/补偿案例，不删除。BeautifulSoup037无需现在为了“第三题”强行接完。

### Stage 6：统计和论文证据【方案当前预注册，执行后续必要】

| 项目 | 内容 |
|---|---|
| 目标 | 给出可重复、范围明确的质量变化、工作流变化与机制证据 |
| 已有基础 | 逐trial结果、Token/HTTP/耗时、冻结/来源链；既有研究设计 |
| 待办 | 全流程分母、可评分分母和infra分开；规则级质量与动作级指标；来源等权配对差；生成重复/Agent重复嵌套；报告区间、成本与有效性威胁 |
| 复用 | scoring/results.py原记录、evaluation导出、账本、request日志；分析另写结果，不回写历史 |
| 新增代码 | 小型汇总/统计脚本，输入只读；先预注册指标，避免开发通用分析平台 |
| 模型/Agent | 汇总不需要；补实验只能按事前补齐规则与新授权 |
| 预算/重复 | 根据Stage3/5方差估计制定独立来源、生成与执行重复；没有可用方差前不给虚假的固定功效承诺 |
| 交付 | 主结果表、逐来源图、失败/成本/规则传播表、干预表、复现清单及限制 |
| 验收 | 所有图表反查到run/hash；planned/started/completed/scorable分母可重建；恢复不算新生成；缓存token不重复累加；无选择性删例 |
| 停止/完成 | 样本不足则明确个案性结论；只有完成预注册覆盖与精度目标才报告广泛效应，不从1对结果推显著性 |

论文主指标建议：文档条件对冻结规则保留/正确性的影响；自然加载工作流的任务和目标动作变化；错误/缺失发生层次；DirectDoc与Skill路径的配对退化损失差；必要干预的选择性变化。来源数量很少时逐来源报告，不用大量同源trial伪造窄置信区间。

## 7. 当前证据可以与不可以支持什么

**可以支持：**

- 两个Scrapy任务确实完成了真实Clean生成、冻结、独立评分与Agent运行；公共结构复用是实际代码和零模型验收支持的，不是只有规划。
- 024观察到NoSkill与Clean结果/读取的差异；041观察到完整目标规则未进入最终Skill、Agent未读正文但任务通过。
- 多文档共享bank发生了真实跨文档协调，也出现了形式不一致；保存的中间产物允许定位部分规则丢失环节。
- GCH已有段落删除试点和不同结果，当前不能把该差异解释为Skill正文错误的因果效应。
- 当前网络隔离已在指定运行时得到实际验证；历史完整性和冻结的关键字节本轮重新核对通过。

**尚不能支持：**

- 文档退化必然降低技能质量或任务成功率；
- 024的2/3对0/3是稳定、显著或仅由FTP Skill产生的提升；
- 041“Skill没有用”、或高分证明其Skill质量高；
- 某条Skill缺陷是某次失败的唯一原因，或已测出自然中介效应；
- DirectDoc与Skill路径哪种更鲁棒/更便宜；
- 当前方法对187题、多个领域均有效；
- 已经实现一种新的高质量生成/恢复算法或证明论文新颖性。

**当前不需要修改Anything2Skill核心算法。** 已观察到的缺陷值得记录；先用固定方法完成一个可解释的退化/行为测量单元。若以后出现可重复的、定位到同一环节的失败，再用开发来源提出修改，并在独立来源验证；不能为提高当前试点分数回头修改冻结技能。

## 8. 唯一下一步的具体任务与完成定义

### 三个最严重的问题

1. **机制链尚未闭合。** 缺陷、读取和评分分别有证据，但没有完成的受控退化与局部机制验证。
2. **可用历史证据分属不同有效性条件。** 024/GCH有诊断信号却采用旧网络；041新隔离可靠却目标规则缺失、正文未读且双方满分。不能把这些拼成一组同条件因果实验。
3. **正式退化的条件绑定和分析协议还不完整。** 公共入口目前仅NoSkill/Clean，规则级关联与失败分母尚未冻结；直接改条件名开跑有错装包/误解释风险。

### 下一项：Scrapy024 FTP默认值的最小受控退化试点

选择024是因为它已经具备“原文规则、正确Clean正文、敏感Oracle、自然读取记录和任务差异”，比另开一个完全未知任务节约适配与生成预算。选择用于探索会带来诊断性选例偏差，后续验证集不能只选出过效果的任务。

最小范围：

1. 冻结一份短协议，回填已有8个Scrapy trial的目标证据表；不开发完整自动归因系统。
2. 只补024三条件所需的公共绑定：NoSkill空资料、Clean固定s24r005、Degraded绑定新的完成生成；独立SkillBank，哈希校验，使用当前网络。
3. 一种可恢复文档呈现退化、一轮新Degraded生成；不改目标事实、任务、Oracle、A2S算法或Clean正文。若实际选择不可恢复删除，必须更名为信息损失条件。
4. 零模型验证正确/目标错误候选、三条件资料隔离/安装与现有网络；之后在新ID下运行NoSkill/Clean/Degraded各1次，预算如Stage1/3，完成即停。
5. 输出完整输入diff、生成/冻结、三条轨迹和评分，以及一个统一规则表/小结。失败和零效应同样保留。

完成标准是 **预定三条件被正确执行或按预注册停止策略明确终止，所有关键身份/信息边界可核查，目标规则的阶段变化、正文可见性、外显动作和断言均有事实或UNKNOWN标注**。不是要求制造一次失败，也不是要求证明统计显著。

它优先于继续增加Clean任务，因为现有024已能承担诊断；优先于开发完整归因系统，因为当前日志足以做一条规则的人工证据链；优先于大规模退化，因为条件接线、资料敏感性及分母策略还需在小试点中检验。

完成之后：有可定位规则/行为差异则进入预注册的局部repair/sham及DirectDoc诊断；若无变化或未读取，先报告零效应/加载瓶颈，再决定一次明确的曝光诊断或不同来源验证。不得自动扩预算、换多个退化直到失败、自动扩任务。

**本报告到此完成审计。没有启动上述下一步。**

## 9. 本地证据导航

以下路径是本轮实际读取的主要证据。链接到旧报告时仅表示其历史说明；实际进度以相应run/原始日志为准。

**E01**：[results/sgb/audits/common-pilot-workflow-20261025-001/validation.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/common-pilot-workflow-20261025-001/validation.json>)；[results/sgb/audits/common-pilot-workflow-20261025-001/all-tests-final.log](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/common-pilot-workflow-20261025-001/all-tests-final.log>)；[results/sgb/audits/common-pilot-workflow-20261025-001/history-before.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/common-pilot-workflow-20261025-001/history-before.json>)。

**E02**：[runs/eval/sgb/scrapy-task-041/s41d001/batch_results.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-041/s41d001/batch_results.json>)；[runs/eval/sgb/scrapy-task-041/s41d001/profile.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-041/s41d001/profile.json>)；[results/sgb/audits/scrapy041-clean-pilot-20261025-001/analysis.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-clean-pilot-20261025-001/analysis.json>)。

**E03**：[runs/eval/sgb/scrapy-task-024/s24d001/batch_results.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-024/s24d001/batch_results.json>)；[runs/eval/sgb/scrapy-task-024/s24d001/skills/341bd0da-1d52-5a40-87dd-44477cdec422/SKILL.md](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-024/s24d001/skills/341bd0da-1d52-5a40-87dd-44477cdec422/SKILL.md>)；[runs/gen/sgb/case024_scrapy/clean/s24r005/execution.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gen/sgb/case024_scrapy/clean/s24r005/execution.json>)。

**E04**：[runs/gen/sgb/case041_scrapy/clean/s41r003/official_result.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gen/sgb/case041_scrapy/clean/s41r003/official_result.json>)；[runs/gen/sgb/case041_scrapy/clean/s41r003/artifact_manifest.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gen/sgb/case041_scrapy/clean/s41r003/artifact_manifest.json>)；[runs/gen/sgb/case041_scrapy/clean/s41r003/SkillBank/.runtime/intermediate_runs/20261025T161852_1c08ddef/ingest/result.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gen/sgb/case041_scrapy/clean/s41r003/SkillBank/.runtime/intermediate_runs/20261025T161852_1c08ddef/ingest/result.json>)；[runs/eval/sgb/scrapy-task-041/s41d001/skills/76394f52-1f81-5c91-8ae3-fd51b942c5e1/SKILL.md](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-041/s41d001/skills/76394f52-1f81-5c91-8ae3-fd51b942c5e1/SKILL.md>)。

**E05**：[data/manifests/sgb/tasks.jsonl](<D:/AS/AutoSkill-main/degradation_failure_lab/data/manifests/sgb/tasks.jsonl>)；[cases/sgb/case041_scrapy/case.json](<D:/AS/AutoSkill-main/degradation_failure_lab/cases/sgb/case041_scrapy/case.json>)；[configs/tasks/sgb/scrapy-task-041.json](<D:/AS/AutoSkill-main/degradation_failure_lab/configs/tasks/sgb/scrapy-task-041.json>)。

**E06**：[results/sgb/audits/scrapy041-clean-preflight-20261025-001/report.md](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-clean-preflight-20261025-001/report.md>)；[results/sgb/audits/scrapy041-clean-pilot-20261025-001/report.md](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-clean-pilot-20261025-001/report.md>)；[results/sgb/audits/scrapy041-clean-pilot-20261025-001/live-registry-correction.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-clean-pilot-20261025-001/live-registry-correction.json>)。

**E07**：[results/sgb/audits/network-isolation-20261025-001/report.md](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/network-isolation-20261025-001/report.md>)；[results/sgb/audits/network-isolation-20261025-001/attempt-002/isolated-network.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/network-isolation-20261025-001/attempt-002/isolated-network.json>)；[results/sgb/audits/network-isolation-20261025-001/attempt-002/positive-control.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/network-isolation-20261025-001/attempt-002/positive-control.json>)。

**E08**：[downstream_eval/integration/skill_usage.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/skill_usage.py>)；[downstream_eval/integration/skill_freeze.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/skill_freeze.py>)；[downstream_eval/integration/p1_observer.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py>)；[results/sgb/analyses/s41d001/CleanSkill1-skill-usage.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/s41d001/CleanSkill1-skill-usage.json>)。

**E09**：[results/sgb/audits/pydantic001-demo-20261024-001/demonstration.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/pydantic001-demo-20261024-001/demonstration.json>)。

**E10**：[downstream_eval/sgb/beautifulsoup_agent.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup_agent.py>)；[downstream_eval/sgb/task_adapters/beautifulsoup037/scoring.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/task_adapters/beautifulsoup037/scoring.py>)；[docs/sgb/downstream_m3_compatibility_audit_20261024.md](<D:/AS/AutoSkill-main/degradation_failure_lab/docs/sgb/downstream_m3_compatibility_audit_20261024.md>)。

**E11**：[results/run_index.jsonl](<D:/AS/AutoSkill-main/degradation_failure_lab/results/run_index.jsonl>)；[docs/research/FIVE_CASE_CLEAN_SKILL_QUALITY_AUDIT.md](<D:/AS/AutoSkill-main/degradation_failure_lab/docs/research/FIVE_CASE_CLEAN_SKILL_QUALITY_AUDIT.md>)。

**E12**：[runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/experiment-result.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/experiment-result.json>)。

**E13**：[runs/gitchameleon/import-20261022-001/pilot_batch.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gitchameleon/import-20261022-001/pilot_batch.json>)；[runs/gitchameleon/import-20261022-001/pilot_metrics.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gitchameleon/import-20261022-001/pilot_metrics.json>)；[cases/case164_gch/conditions.json](<D:/AS/AutoSkill-main/degradation_failure_lab/cases/case164_gch/conditions.json>)；[data/manifests/gitchameleon_fidelity.json](<D:/AS/AutoSkill-main/degradation_failure_lab/data/manifests/gitchameleon_fidelity.json>)。

**E14**：[src/degradation_lab/resume.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/resume.py>)；[README.md](<D:/AS/AutoSkill-main/degradation_failure_lab/README.md>)；[docs/sgb/README.md](<D:/AS/AutoSkill-main/degradation_failure_lab/docs/sgb/README.md>)。

**E15**：[src/degradation_lab/runner.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/runner.py>)；[src/degradation_lab/adapter.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/adapter.py>)；[cases/sgb/case024_scrapy/case.json](<D:/AS/AutoSkill-main/degradation_failure_lab/cases/sgb/case024_scrapy/case.json>)；[runs/gen/sgb/case041_scrapy/clean/s41r003/upstream_before.json](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/gen/sgb/case041_scrapy/clean/s41r003/upstream_before.json>)。

**E16**：[results/sgb/analyses/s24m003/domain_identity_ablation_report.md](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/s24m003/domain_identity_ablation_report.md>)；[results/sgb/analyses/s24m003/domain_identity_replication_report.md](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/s24m003/domain_identity_replication_report.md>)；[results/sgb/analyses/s24m003/content_form_ablation_report.md](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/s24m003/content_form_ablation_report.md>)。

**E17**：[src/degradation_lab/evaluation.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/evaluation.py>)；[src/degradation_lab/artifacts.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/artifacts.py>)；[cases/sgb/case024_scrapy/rules.json](<D:/AS/AutoSkill-main/degradation_failure_lab/cases/sgb/case024_scrapy/rules.json>)；[cases/sgb/case041_scrapy/rules.json](<D:/AS/AutoSkill-main/degradation_failure_lab/cases/sgb/case041_scrapy/rules.json>)。

**E18**：[results/sgb/audits/scrapy041-adapter-20261025-001/attempt-001/acceptance.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-adapter-20261025-001/attempt-001/acceptance.json>)；[results/sgb/audits/scrapy041-adapter-20261025-001/attempt-001/middleware-diagnostic/result.json](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-adapter-20261025-001/attempt-001/middleware-diagnostic/result.json>)；[downstream_eval/tasks/sgb/code_doc/scrapy-task-041/runtime.lock.json](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/sgb/code_doc/scrapy-task-041/runtime.lock.json>)。

**E19**：[downstream_eval/tasks/sgb/code_doc/scrapy-task-041/scorer/oracle/eval.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/sgb/code_doc/scrapy-task-041/scorer/oracle/eval.py>)；[downstream_eval/tasks/sgb/code_doc/scrapy-task-041/scorer/worker.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/sgb/code_doc/scrapy-task-041/scorer/worker.py>)；[downstream_eval/sgb/task_adapters/scrapy041/scoring.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/task_adapters/scrapy041/scoring.py>)。

**E20**：[downstream_eval/scoring/results.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/scoring/results.py>)；[downstream_eval/sgb/pilot.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/pilot.py>)；[downstream_eval/sgb/task_adapters/scrapy041/adapter.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/task_adapters/scrapy041/adapter.py>)；[downstream_eval/sgb/scrapy024.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/scrapy024.py>)。

**E21**：[docs/sgb/research/audit_20261015/research_design_review.md](<D:/AS/AutoSkill-main/degradation_failure_lab/docs/sgb/research/audit_20261015/research_design_review.md>)。

**E22**：[C:/Users/lily/Documents/ChatGPT/回归解决退化文档/research_reassessment_2026-10-10/02_文献核查与比较矩阵.md](<C:/Users/lily/Documents/ChatGPT/回归解决退化文档/research_reassessment_2026-10-10/02_文献核查与比较矩阵.md>)。

**E23**：[downstream_eval/integration/request_budget.py](<D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py>)；[src/degradation_lab/adapter.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/adapter.py>)；[src/degradation_lab/resume.py](<D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/resume.py>)；[data/manifests/sgb/gates/t-8d3bed6236cf.json](<D:/AS/AutoSkill-main/degradation_failure_lab/data/manifests/sgb/gates/t-8d3bed6236cf.json>)。


[E01]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/common-pilot-workflow-20261025-001/validation.json>
[E02]: <D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-041/s41d001/batch_results.json>
[E03]: <D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-024/s24d001/batch_results.json>
[E04]: <D:/AS/AutoSkill-main/degradation_failure_lab/runs/gen/sgb/case041_scrapy/clean/s41r003/official_result.json>
[E05]: <D:/AS/AutoSkill-main/degradation_failure_lab/data/manifests/sgb/tasks.jsonl>
[E06]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-clean-preflight-20261025-001/report.md>
[E07]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/network-isolation-20261025-001/report.md>
[E08]: <D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/skill_usage.py>
[E09]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/pydantic001-demo-20261024-001/demonstration.json>
[E10]: <D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup_agent.py>
[E11]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/run_index.jsonl>
[E12]: <D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-c-recovery-20261019-001/experiment-result.json>
[E13]: <D:/AS/AutoSkill-main/degradation_failure_lab/runs/gitchameleon/import-20261022-001/pilot_batch.json>
[E14]: <D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/resume.py>
[E15]: <D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/runner.py>
[E16]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/s24m003/domain_identity_ablation_report.md>
[E17]: <D:/AS/AutoSkill-main/degradation_failure_lab/src/degradation_lab/evaluation.py>
[E18]: <D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/scrapy041-adapter-20261025-001/attempt-001/acceptance.json>
[E19]: <D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/sgb/code_doc/scrapy-task-041/scorer/oracle/eval.py>
[E20]: <D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/scoring/results.py>
[E21]: <D:/AS/AutoSkill-main/degradation_failure_lab/docs/sgb/research/audit_20261015/research_design_review.md>
[E22]: <C:/Users/lily/Documents/ChatGPT/回归解决退化文档/research_reassessment_2026-10-10/02_文献核查与比较矩阵.md>
[E23]: <D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py>
