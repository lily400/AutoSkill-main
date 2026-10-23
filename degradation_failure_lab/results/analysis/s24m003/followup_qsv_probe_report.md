# s24m003 第二阶段诊断：历史qsv单次Plan正对照

日期：2026-10-23（Asia/Shanghai）。

**已证实：本任务仅执行1次HTTP模型请求，逐字节复用历史qsv HTTP002保存的请求体，得到合法JSON及3个非空候选；原版Plan本地解析也保留3个。新响应的system_fingerprint与Scrapy s24m003相同。证据支持但未证实：调查可以进一步聚焦Scrapy输入及领域元数据，当前不支持“该服务条件下所有软件文档都无法产出候选”的解释。未知：Scrapy为什么选空、各输入差异的因果贡献，以及候选或最终Skill的质量。现有证据不足以直接修改提取提示词、策略或准入算法。**

本次只复现了“历史qsv输入可以产生非空Plan”的性质，未复现同样的4候选，也未执行Expand、compile、register、Agent或Oracle。授权的1次请求已经用完，完成报告后停止。

## 1. 路径核验及实际执行范围

用户指定的仓库根、当前源码、实验目录和两份历史运行均存在，实际工作未切换工作树：

- 仓库根：D:\AS\AutoSkill-main。
- 当前源码：D:\AS\AutoSkill-main\AutoSkill-main。
- 实验目录：D:\AS\AutoSkill-main\degradation_failure_lab。
- Scrapy运行S：runs/case024_scrapy/clean/s24m003。
- qsv历史Q：runs/case001_qsv_select/clean/raecd75e08b34。

指定的上一轮报告路径少了一层目录：results/analysis/s24m003_zero_candidate_root_cause.md不存在；实际文件是[上一轮报告](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/s24m003_zero_candidate_root_cause.md)。本轮先核对该文件及evidence索引，复用既有21窗审计，没有重新诊断整套工程、重建报告或将同名文件内容视为已知。

所有新增文件集中在本报告同级的qsv_probe_001目录；最终报告即本文件。阶段A只读预检0次模型请求，阶段B唯一探针1次，阶段C只读比对与报告0次。

## 2. 冻结的历史正对照

### 2.1 准确来源与哈希

真实来源是Q/http/002/request.json、response.json和event.json，不是依据报告重新编写的请求。

| 对象 | SHA-256 |
|---|---|
| 历史请求文件及本次实际请求体 | e346e5e435b94d0c92e0fb3b1705281e31996a4d0399c9c7b7ec702dce65c2fe |
| 历史响应文件 | 778fe551dc895de75f56bd8aa57da1ec5c74234eefd4c513ce2d2f4b10147773 |
| system prompt文本 | 572a28771d6c510d52ee1c458bbd3ce66d8efa011408ffd8ba55ad7fa70eb37c |
| user message文本 | 8c6b0063bd47587399189078ccfeade5204a5ae279878ae7e452d7970b297598 |
| qsv窗口excerpt | 158b9003da6d2bcb05c81c4013d86ab7feaa3a7c5f7878cdc54fe956295ba268 |

原始文件：[历史请求](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/http/002/request.json)、[历史响应](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case001_qsv_select/clean/raecd75e08b34/http/002/response.json)。

qsv_probe_001/historical_request.json、historical_response.json是这些已有文件的逐字节副本；system_prompt.txt、user_message.txt和historical_content.txt分别保存实际原文。历史事件仅保存非秘密字段。Authorization头、密钥及环境变量秘密从未落盘。

保存的历史请求是运行器记录的payload快照，不是TLS抓包；本次以该快照字节直接作为POST body。已确认它与原文件、本次live_001/request.json完全相同，因此system/user及所有请求参数保持原样，而非手工重建。新probe身份只写到外部attempt/result，不修改user中原有qsv文档/run元数据。

### 2.2 实际请求配置

- endpoint：https://api.deepseek.com/v1/chat/completions，来自历史event.json。
- model：deepseek-flash，请求及响应均同名；这是模型别名，不是不可变权重版本证明。
- temperature=0.0、max_tokens=16384、stream=false、thinking.type=disabled。
- 除messages外全部请求参数逐字段匹配历史文件；没有增加response_format、候选提示或非空要求。
- timeout=180秒，来自历史配置，是客户端超时，不改写请求体。
- 使用标准库urllib及当前系统代理处理，保留原客户端的系统代理方式，额外禁止重定向/重试；历史具体代理内部状态未完整记录，不能声称网络路径在两日期逐跳相同。

历史原始content是合法JSON，4个候选分别为“CSV列选择与重排”“正则表达式列选择”“列排序与随机打乱”“列名冲突引用”，资产类型为1个session_skill及3个micro_skill。可见evidence_span_hint能关联qsv文档中列选择、regex、sort、quote示例；逐项保存于historical_candidates.json。

历史system_fingerprint为aeb56401ca74e127821c4f9126dcb669；usage为4102输入、957输出、总5059 tokens。历史用量仅作参考，未当成本次实际用量。

## 3. 阶段A：差异复核及单次调用可行性

### 3.1 qsv与Scrapy的字符串差异

比较对象是历史Q/http002与实际S/http019，而不是Scrapy目录窗口或摘要。

| 字段 | qsv历史正例 | Scrapy目标请求 | 判断 |
|---|---|---|---|
| system prompt | domain type=qsv | domain type=default | 已证实：模板仅该一行不同 |
| document.domain | qsv | 空字符串 | 已证实 |
| taxonomy.domain_type/taxonomy_id | qsv/qsv | default/default | 已证实，其余taxonomy字段/类型树相同 |
| document其他字段 | qsv文档ID、select标题、原run和来源metadata | Scrapy文档ID、feed-exports标题及自身metadata | 已证实，不能当作同输入对照 |
| section | select、操作示例相关子节 | Feed exports、含FEEDS/FTP的较宽子节列表 | 已证实 |
| excerpt | 2362字符，直接展示多条qsv select命令 | 1552字符，overwrite含义、默认值和APPE条件参考块 | 文本性质差异已证实；作用机制未证实 |
| max_candidates | 4 | 4 | 已证实：一致 |
| model及请求参数 | deepseek-flash及原参数 | 相同 | 已证实 |
| endpoint | api.deepseek.com/v1/chat/completions | 相同 | 已证实 |
| 历史fingerprint | aeb56401ca74e127821c4f9126dcb669 | e72d3c7f663d3e1383b00b3884cb4501 | 标识差异已证实，具体部署含义未知 |

comparison.json保存两次document、section、excerpt和max_candidates实际值；system_prompt.diff保存准确模板diff，不重复上一轮完整审计。

**证据支持但未证实**：直接可执行的命令示例可能更贴近“可调用、operational”的资产描述；领域身份可能影响模型判断。**未知**：哪项导致Scrapy为空、两项是否交互。不得由运行结果差异直接认定原因。

已有FTP规则已完整进入HTTP019及21次原始空数组、没有本地过滤的结论继续复用，未推翻或重新推测。

### 3.2 为什么使用独立诊断脚本

旧单窗口工具固定Scrapy输入及历史164项源码清单，直接使用会遇到输入绑定/已原地修复后的版本核对问题。因此本轮没有改旧工具或生产源码；仅在qsv_probe_001新建一次性probe.py，复用已验收的本地JSON/Plan解析合同，重新绑定本次原始qsv请求和当前166项源码。

脚本不调用lab.py run或SDK生成入口：

1. 请求体从冻结文件读入，发送前检查原始请求、system/user、参数和完整性哈希。
2. live_001目录排他创建，先写一次预算占用标记；即使超时或失败，相同目录再次启动也拒绝。
3. 唯一post_once调用只执行一次opener.open，未使用SDK客户端/自动重试层。
4. 安装NoRedirect，HTTP错误或重定向不会产生第二次模型请求；无repair、Outline、Expand、compile或register。
5. 请求体先存盘；响应原始字节先存盘，随后才作严格JSON和原版Plan本地解析。后者使用保存响应stub，不连接模型。
6. Authorization仅在发送时于内存构造，不序列化请求头。若服务回显密钥，写入前脱敏并单独标记；本次未发生脱敏。
7. 默认命令仅离线校验；只有本任务授权后显式执行--execute。生产执行固定live_001，没有循环或换输出目录重发的分支。

contract_tests.json记录11项本地测试全部通过，测试进程audit hook禁止socket和子进程。覆盖：历史非空JSON本地解析、空数组、非法JSON、截断、name过滤、超时、HTTP错误、密钥回显脱敏，以及真实post_once函数在fake opener下只open一次、无重定向、传输失败无第二次open、请求字节一致。所有夹具调用都是模拟传输，不计真实模型请求。

这些证据满足上限核验后，才执行阶段B；没有通过完整case运行代替探针。

## 4. 唯一真实探针结果

- probe ID：s24m003-followup-qsv-plan-001。
- 实际响应创建时间（按响应created换算北京时间）：2026-10-23T17:55:05+08:00。
- 模型请求尝试：**1次，成功响应1次**；重试0、repair0、其他模型阶段0。
- HTTP状态200；finish_reason=stop。
- 原始content为合法JSON；**raw candidates=3，原版Plan本地接受=3**。
- 请求SHA与历史完全相同；没有改prompt、domain、taxonomy或文档。
- 原始响应SHA-256：a96c71b46dcbafddc44484a61373d9e3ac43b431c11f03c76ebf235fb75c2b33。
- model=deepseek-flash。
- system_fingerprint=e72d3c7f663d3e1383b00b3884cb4501，**与Scrapy s24m003一致，与qsv历史成功的旧指纹不同**。

可核查文件：[实际请求](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/qsv_probe_001/live_001/request.json)、[原始响应](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/qsv_probe_001/live_001/response.raw.json)、[判定结果](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m003/qsv_probe_001/live_001/result.json)。

返回候选：

| 名称 | 资产类型 | 可见evidence_span_hint |
|---|---|---|
| CSV 列选择与重排 | session_skill | Select columns from CSV data efficiently. |
| 列排序与随机化变换 | micro_skill | --sort / --random --seed 42 |
| 选择器语法引用 | knowledge_reference | Select Options / 引号转义冲突列名 |

其中一个候选是knowledge_reference。**已证实：当前服务及该Plan模板在qsv身份/内容条件下能够返回参考类候选，原版Plan解析也接受它。** 这不能推出所有API参数参考块均会被认可，也不能证明该候选已通过后续完整Skill验证。证据提示只是响应可见内容，未将混合/概括提示强称为逐字原文引用。

### 4.1 实际token与费用

| 项目 | 历史Q/http002 | 本次唯一探针 |
|---|---:|---:|
| prompt tokens | 4102 | **4102** |
| completion tokens | 957 | **812** |
| total tokens | 5059 | **4914** |
| cached prompt tokens（已含在输入中） | 1152 | 256 |
| 候选数 | 4 | **3** |

本次耗时约5.45秒。实际token来自这一次原始响应usage；缓存不重复相加。价格与账单未可靠确认，人民币金额未知。没有以历史5059冒充本次实际用量。

非空性质复现成功，候选数量/内容没有精确复现。单次结果不能估计稳定成功率、证明统计因果或决定哪次候选质量更高。

## 5. 根据三类结果解释证据

| 结果类别 | 本次是否发生 | 可支持与不可支持 |
|---|---|---|
| qsv非空 | **是：3候选、合法JSON、stop** | 当前条件下历史qsv输入仍能产出候选；可进一步聚焦Scrapy输入和元数据。不能认定Scrapy文档必然有问题、default就是根因、FTP规则不适合Skill或改某条prompt必然奏效 |
| qsv也为空 | 否 | 若发生，会表明失败并非只在Scrapy输入上观察到、历史成功不能直接复现，应调查服务/稳定性。不能直接认定权重更换、提供方故障或算法缺陷；单次失败不是统计证据 |
| 失败、截断或非法JSON | 否 | 应单独归为传输/响应/格式问题，不与合法空数组混为一谈，也不重试 |

**已证实**：当前同名模型、该端点以及返回e72d3…指纹的服务条件，至少对这份qsv请求有非空输出。可以排除“这个指纹下所有请求都固定返回空数组”“原模板完全无法处理软件文档”“当前Plan解析器总把非空候选清空”等普遍解释。

**证据支持但未证实**：Scrapy参数参考材料、默认领域身份及窗口组织更值得调查。qsv与Scrapy使用同一返回指纹，使服务条件更可比，但**指纹相同不证明所有服务端条件、路由和随机因素完全一致**。

**未知**：Scrapy空Plan的完整因果根因；document.domain、taxonomy身份、操作示例密度、参考块形式、章节粒度各自的效应；当前候选/未来Skill的质量。qsv非空不能排除Scrapy材料因素，也不能证明它是唯一原因。

治疗领域措辞仍属于适配风险假设；相同模板产生qsv候选，且出现knowledge_reference，进一步削弱了“这些措辞或参考资产类型会普遍禁止技术文档提取”的绝对判断。它是否对Scrapy有特定影响仍未验证。

## 6. 下一步最小单因素实验建议

**当前没有足够证据修改Anything2Skill提示词、候选生成策略或准入逻辑。** 应先检查已观察到、可通过公开配置改变的外部领域身份因素。

建议下一轮另行批准后，对Scrapy实际HTTP019做domain_type单因素Plan对照：

- 基准臂：原HTTP019的完整请求。
- 对照臂：只将外部domain_type从default变为scrapy，由未修改的taxonomy/prompt构造器生成对应字段。
- 保持1552字符excerpt、document.domain、section、其他document/metadata、max_candidates、模型、endpoint、temperature、max_tokens、thinking和所有其他参数不变。
- 同一外部配置因子会确定性影响system中的领域身份行及taxonomy.domain_type/taxonomy_id；需离线列出允许diff，禁止混入document.domain/family_name等其他修改。它检验的是领域身份这一组合配置效应，不能进一步拆解为某个字段的单独效应。
- 不改候选定义，不加入“必须返回非空”指令，不添加人工FTP规则，不触发Expand/compile/register。

**下一轮最小可解释执行单元建议两个单请求：同期原请求与仅domain_type改变的请求各一次。** 这超过本轮已用完的1次授权，因此本轮不准备执行或发送任何一臂。已有Scrapy空响应可作零成本阴性参考；如果未来只批准一个新请求，领域身份变更只能算较弱的探索，不能把历史/当前时间差当作已经控制。

判定同时记录原生候选数及是否明确涵盖FTP overwrite默认规则；不能把无关feed候选、泛泛标题或nonempty本身当作目标规则已被表达。若只有变更臂非空，只支持领域身份敏感性的初步证据，仍需重复/控制；两臂都空也不能据此直接改准入算法。

改变技术文档prompt或候选策略只能作为后续独立方法版本研究，不得冒充未经修改的官方基线。本轮没有做这些修改。

## 7. 对研究方案的影响与停止条件

本次达成的是诊断正对照：历史成功qsv输入仍能产生非空Plan。它没有生成正式canonical Skill，没有验证Scrapy的Clean Skill，也没有验证Agent实际读取或任务表现。

**决策：CONDITIONAL GO，继续小规模单因素诊断；暂不启动正式退化实验，也不据本探针修改算法。** Scrapy输入保真已经解决，但Clean路径仍未产出合格目标Skill，尚需查清是否与身份/内容条件有关。不要将21个不同窗口当成21次独立Agent校准，也不要将1个非空Plan当成Skill/任务成功率。

明确停止条件：

1. 本任务1次模型HTTP授权已全部使用，立即停止；不得补发、换模型或为得到4候选重试。
2. 后续任一输入/参数/哈希不一致、凭据缺失或无法证明次数上限，应在零调用阶段停止。
3. 单次响应为空、截断、非法或失败，都记录对应状态，不自动修复/重试。
4. 后续修改prompt、模型、准入或开始Expand/Agent，均须另立方案及明确授权。

## 8. 源码、原始记录和秘密保护

protected_before.json与最终复核确认：

- 当前U下166项已记录源码/备份文件未变，保留此前预处理修复状态。
- qsv历史170个文件、Scrapy s24m003的135个文件逐文件未变。
- 上一轮报告及复用的解析helper未变。
- 没有改生产源码、冻结原件、历史请求/响应、case配置或正式实验。
- 检查真实凭据字节未出现在任何新证据文件中；没有保存Authorization头或秘密变量值。实际响应无需脱敏，wire响应SHA与保存响应SHA相同。

新目录内容：

| 文件 | 用途 |
|---|---|
| path_check.json | 固定路径及上一轮报告路径差一层的事实 |
| historical_request.json、historical_response.json、historical_event.json | 从真实HTTP002冻结的请求、响应及非秘密事件字段 |
| system_prompt.txt、user_message.txt、historical_content.txt | 原始文本 |
| historical_candidates.json | 原4候选名称、类型、提示及源文匹配 |
| comparison.json、system_prompt.diff | qsv与Scrapy实际document/section/excerpt、参数和身份差异 |
| probe_spec.json、protected_before.json | 本次绑定、哈希、1次上限及保护清单 |
| probe.py、test_probe.py、contract_tests.json/log | 一次性脚本及11项零网络合同测试 |
| preflight.json | 阶段A通过、脚本SHA、凭据可用布尔值及脱敏代理信息 |
| live_001/request.json、response.raw.json、attempt.json、result.json | 唯一真实请求、原始响应、预算占用及判定 |
| post_probe_summary.json | 实际3候选、指纹、usage、完整性及结论边界 |

**实际执行完成：1次HTTP模型探针，3个候选，4914 tokens；其他模型调用0次。停止。**
