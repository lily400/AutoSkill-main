# s24m002 事后核查：运行仍使用未修复预处理

日期：2026-10-23。**本轮新增模型 API 调用 0 次。** 分析对象为已经结束的 `s24m002`，没有执行 `lab.py run`、加载密钥或重新发送历史请求。

**结论：s24m002 使用的是 `D:\AS\AutoSkill-main\AutoSkill-main` 中的原版预处理，上一轮独立修复副本没有接入这条运行命令。** 该结论由实际调用栈、运行前后源码哈希、导入路径检查及保存的 sections/windows 精确离线重放共同支持，并非仅由 windows=18 推断。

本次再次向模型发送了18个缺少完整目标规则的窗口，因此它没有检验“修复后的完整输入能否提取候选”。18次模型为什么选择空数组仍无直接解释证据。正确的下一步已经具备独立单窗口入口，见第6节；本轮停止在准备和零模型验证处。

## 1. 本次究竟使用哪份代码，补丁是否接入

为便于定位，以下定义路径缩写：

- L：`D:\AS\AutoSkill-main\degradation_failure_lab`。
- R1：`L\runs\case024_scrapy\clean\s24m001`。
- R2：`L\runs\case024_scrapy\clean\s24m002`。
- U：`D:\AS\AutoSkill-main\AutoSkill-main`。
- A1：`L\results\analysis\s24m001`。
- A2：`L\results\analysis\s24m002`，本轮新增报告和证据目录。

### 1.1 历史实际入口与导入链

R2/invocation.json 保存的命令为：

```text
D:\anoconda1\envs\autoskill\python.exe -B scripts/lab.py run --case case024_scrapy --condition clean --repeat 1 --run-id s24m002
```

代码链及证据如下：

| 环节 | 实际文件/函数 | 已核实行为 |
|---|---|---|
| lab.py入口 | `L\scripts\lab.py:5–6` | 把 `L\src` 插到sys.path首位，导入degradation_lab.cli.main；不是从审计目录运行单窗口工具。 |
| CLI | `R2\wrapper_snapshot\degradation_lab\cli.py:65–81 main` | run子命令逐计划调用ExperimentRunner.run，无window-ID、窗口正文或只Plan参数。 |
| 源码路径解析 | 同快照 `io.py:37–61 resolve_upstream`；`runner.py:78–108 prepare` | 优先读取ANYTHING2SKILL_SOURCE，否则取configs/environment.json；将解析路径冻结到run/environment.json，并记录upstream_before。 |
| 本次冻结结果 | `R2\environment.json` | upstream_path明确为U。当前configs/environment.json是`../AutoSkill-main`，当前审计进程也解析到U。历史环境变量原值未保存，不能由当前值倒推；历史最终解析路径已保存。 |
| 实际SDK导入 | 同快照 `adapter.py:14、25–29 execute` | 使用run/environment.json，把U插到sys.path首位，导入AutoSkill4Doc.extract_from_doc和file_loader。135–139调用完整extract_from_doc。没有自动应用补丁。 |
| 历史执行栈 | `R2\http\001\event.json`、`official_call_trace.json` | Outline调用栈明确包含`U\AutoSkill4Doc\ingest.py`的_outline_matches_from_llm、_parse_sections_with_fallback；Plan和pipeline也来自U。 |
| 当前只读导入核对 | `A2\evidence_verified\import_paths.json` | inspect确认front_matter、build_windows、paragraph_filter、window_identity的__file__/函数行号均来自U，且SHA为原版。没有调用run/execute。 |

历史观察器没有选择build_windows_for_record/_window_from_blocks作为profile记录目标，所以**不存在这两个函数的独立历史call trace**。本轮用同一源码、实际源文和保存的Outline响应，重放原函数后，sections和windows与R2保存值逐字段完全一致；见summary.json中的replay_matches_s24m002_exactly=true。这是确定性重放证据，不冒充历史逐分支遥测。

当前10个degradation_lab文件也逐个匹配R2/wrapper_manifest.json。`scripts/lab.py`本身未被旧运行器复制进wrapper_snapshot；其历史入口由argv证明，具体入口代码由当前文件确认。这一证据边界不影响已保存的SDK路径与代码哈希结论。

### 1.2 上一轮修复在哪里

独立修复的真实源码位于当前可访问的：

```text
C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\scrapy024_preflight\calibration_evidence\s24m001_round2_staging\round2\work\patched_upstream\AutoSkill4Doc\ingest.py
C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\scrapy024_preflight\calibration_evidence\s24m001_round2_staging\round2\work\patched_upstream\AutoSkill4Doc\document\windowing.py
```

补丁、重建脚本、测试和验收证据已归档在：

```text
A1\round2\preprocessing.patch
A1\round2\patch_manifest.json
A1\round2\prepare_copy.py
A1\round2\test_preprocessing.py
A1\round2\patched_ok\tests.json
A1\round2\patched_ok\windows.json
```

官方固定提交是 `94c47ca488d4ba4117d20272e66d49b9877e68cf`。本轮核对R2记录的164项代码：与R1记录、当前U文件及C盘固定Git克隆逐字节一致。修复副本的164项中恰好只有以下两文件不同，与上一轮补丁清单一致。

| 文件 | R1/R2记录、当前U及固定克隆SHA-256 | 独立修复副本SHA-256 |
|---|---|---|
| AutoSkill4Doc/ingest.py | `4bf23bba2b6eaab39dd3aa39b1cb33dc9f60528d9b6a577c2fdb28e2a389925f` | `b9b1f0ac8a7096ae41567902dbd4e031439a784f780eb269e46b9f66148730b2` |
| AutoSkill4Doc/document/windowing.py | `a4431d5bc5a06c4e6a101a530f90fdcd9ab7466107e64c006873dc6ba1df1ec2` | `5542cf56ac5e99bea393c754f40dc69c9a361f5a72fa11b28593f792c290f855` |

因此是**补丁保留在独立副本，但完整run路径仍指向官方目录**。当前CLI/runner没有发现应用preprocessing.patch或选择patched_upstream的逻辑，也没有发现漏复制“部分修复”到U：两项都仍为原版。无需假设旧模块缓存导致本次结果；现有证据已经解释了源码选择。不能据这些记录证明Python历史进程内每个字节码对象的全部来源，但没有修复版实际生效的证据。

上一轮独立修复有意未修改U，原报告也注明lab-preprocess-v1不是未修改的官方端到端基线。**独立副本测试通过不会改变普通lab.py run的默认源码路径。** 本轮保持这个边界，没有将补丁写入官方版本，也没有改全局环境配置。

## 2. s24m002的真实输入

原文路径为R2/inputs/input001/feed-exports.md，字节SHA-256：

```text
a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d
```

与R1相同，属于SkillGenBench `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d` 发布快照的task-curated材料。源文完整存在，缺失发生在处理路径。没有本轮补写Clean材料。

实际ingest保存在：

```text
R2\SkillBank\.runtime\intermediate_runs\20261023T162038_57654e82\ingest\result.json
```

本轮对18个保存请求逐一匹配excerpt+section.span，每项只匹配一个实际窗口；逐窗文本、完整SHA和请求SHA在`A2/evidence_verified/window_request_checks.{json,csv}`，正文另存`windows/01.txt`至18.txt。不是只凭日志数量推断。

| 核查项 | s24m002结果 |
|---|---|
| sections/windows/unique IDs | 35 / 18 / 17 |
| 窗口正文SHA | 18个均不同；正文非空；与s24m001逐一相同 |
| FTP小节 | Outline仍选中candidate13，但最终sections没有FTP |
| FTP重复支持136–137 | 随FTP节丢失；其他后端中同句default=True不能当作FTP语境证据 |
| overwrite定义438–439 | 18份真实Plan excerpt全部缺失 |
| 默认值表441–443 | 在窗口14、HTTP015出现；前邻是item_filter，完整参数作用域缺失 |
| APPE例外445–446及后端限制447–449 | 18份真实Plan excerpt全部缺失APPE及完整目标块 |
| 完整438–449块进入Plan | **0/18** |
| ID冲突 | 第8和18窗口共用`42cb3c04-f531-5c16-9db5-496fb3d79a7d`，正文不同；HTTP009/019均确实发出 |

R1与R2的文档ID不同，窗口ID随之变化，不能用“新ID”认定身份修复生效。冲突在R2仍存在；检查点只保存17个唯一窗口路径，aggregate.expected_window_ids有18项、processed_window_ids17项，仍标complete=true。

两次sections并非所有字段相同：本次Outline把Storage URI parameters改为level3，并调整若干parent/sibling/heading_path字段，共11个section有差异；**35个section的标题、正文及span相同，18个窗口正文也全部相同**。详情见section_differences.json。不能将两次完整模型请求视为逐字相同：元数据/run路径与层级提示确有差别。

本轮确定性复核原过滤函数得到：

| 输入 | 结果与代码 |
|---|---|
| FTP正文前240字符，含ftp://user:pass@host | `U\AutoSkill4Doc\ingest.py:109–126 _looks_like_front_matter_heading`返回True；`:528`跳过整节 |
| 包含overwrite定义的379字符段落 | `U\AutoSkill4Doc\document\windowing.py:257–285`：段落开头不是列表，中部列表不命中旧正则；process_signal=False、长度>320，保留0块 |
| 95字符默认表 | 旧process_signal=False但长度≤320，保留1块 |
| 包含APPE例外的413字符段落 | process_signal=False、长度>320，保留0块 |

filter_replay.json保留真实输入和输出；原版全链路离线重放精确匹配R2保存值。规则保真失败与模型选择空数组是两个结论，不能把前者直接当作全部空数组的唯一原因。

## 3. 为什么仍然18次空候选，为什么跑完全部窗口

19份request/response/event都存在且哈希核对通过，没有请求正文证据缺口。HTTP001是Outline，HTTP002–019才是Plan。18份原始响应的唯一choice均为：

```json
{"skills": []}
```

每次finish_reason=stop、completion_tokens=5，HTTP成功。未发现截断、解析失败、HTTP429或非空候选被丢弃。各窗口正文不同，不是循环重复发送同一窗口；ID冲突没有造成本次漏发。

直接路径是：`U/AutoSkill4Doc/stages/extractor.py:857–894 _plan_unit_skills`解析出空skills，不进入候选循环；`:978 if not planned: return []`结束该窗口，无Expand，supports/drafts为0。**模型内部为何在每个窗口都作此选择没有保存的解释，仍未知。** 保守prompt和领域措辞可能不匹配技术文档，以及目标上下文丢失，都只是有依据的调查方向，尚未独立验证其因果贡献。

原配置`max_units_per_document=0`表示不限制；pipeline.py:1153起继续迭代windows_to_run。合法空数组是成功处理窗口，不抛异常，`continue_on_error=False`也不触发停止。原版没有“连续空Plan停止”的条件，所以覆盖全部18个窗口后才返回零产物。配置extract_retries=1允许错误重试，但本次均为合法响应，实际重试0。外层150次HTTP/450,000已观察tokens上限没有触发。

不能靠把max_units设为1来替代本计划：完整路径仍可能先Outline，选到非目标窗口，并自动进行后续流程。本轮也没有改变原运行循环来隐藏失败。

## 4. 成本记录

| 阶段 | 已有HTTP次数 | prompt tokens | completion tokens | total tokens |
|---|---:|---:|---:|---:|
| Outline | 1 | 6,290 | 510 | 6,800 |
| Plan | 18 | 66,572 | 90 | 66,662 |
| Expand/compile/register模型 | 0 | 0 | 0 | 0 |
| **合计** | **19** | **72,862** | **600** | **73,462** |

API usage逐项加总与execution.json一致；cached prompt tokens=37,760，已在prompt_tokens中，不能重复相加。19个logical_call_id不同、attempt_index全为1、retry_of全null；network_diagnostics记录transport_retries=0。18个完整窗口正文的重复发送率0/18。

本次历史消耗为73,462 tokens，s24m001为73,516，两者不能混写。账单/单价没有可信记录，billed_cost=null，人民币金额未知。本轮新增API、token消耗均为0。

## 5. exit_code=2和后续阶段的准确状态

直接代码是**本次快照** `R2/wrapper_snapshot/degradation_lab/adapter.py:140`：

```python
exit_code = 0 if result.get('total_skill_specs',0)>0 and not result.get('errors') and result.get('status')=='completed' else 2
```

实际official_result为status=completed、errors=[]、total_skill_specs=0，所以外层记exit_code=2、FAILED。不是异常退出猜测；exception.json不存在，异常分支默认码1未走到。

必须纠正“后续阶段根本没有执行”的笼统说法：

- **Expand没有执行**：没有候选进入该分支，调用轨迹没有_expand_planned_skill。
- **compile接口执行过**：official_call_trace有compile_skills；compile/result.json里supports/drafts/specs/errors全空，空分组没有模型调用。
- **register接口执行过**：调用轨迹有register_versions、sync_visible_skill_tree；register/result.json中specs/upserts/hierarchy/lifecycle等全0，完成本地空结果收尾。
- SDK.completed_stages列出ingest/extract/compile/register；这代表流程完成，不代表生成了可用Skill。导航骨架SKILL.md不算canonical提取结果。

execution.json的2是适配器结果；cli.py:81聚合`int(any(...exit_code...))`，若正常返回这条CLI，shell码会是1。历史shell的LASTEXITCODE没有保存，不将源码推断称为shell实测。

## 6. 下一次正确的单窗口入口：只准备，不执行

**直接复用已归档入口，不再执行完整lab.py run，也无需把修复补丁写入官方目录。**

```text
入口：A1\round2\single_window_probe.py
输入：A1\round2\patched_ok\single_window_request.json
窗口：A1\round2\patched_ok\single_window.txt
配置：A1\round2\patched_ok\single_window_config.json
```

这是上一轮修复副本真实产出的第18个窗口，1552字符，完整保留438–449块及accepted-keys上下文，8段均有唯一源文定位。源文仍来源R1，未更名冒充R2；本轮已确认R1/R2源文字节相同，且冻结probe的system prompt、model/temperature/stream/max_tokens/thinking参数与R2实际Plan请求一致。

| 冻结对象 | SHA-256 |
|---|---|
| 窗口正文 | `50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07` |
| 请求体文件 | `a3265af49b00d88538f90c49f56c71a88aec0ba87e1cf79da7d83d4ff1de81f1` |
| 原版system prompt | `295ee9cd6633d30897b2028a7a53a4e9b06a399c40c29b78d99413f515629be6` |

模型仍为deepseek-flash（别名，非可验证不可变权重版本），temperature0、streamfalse、thinking disabled、max_tokens16384、timeout180秒。prompt和原生Plan解析不改；输入处理标记为lab-preprocess-v1，不能标为未经修改的端到端基线。

### 6.1 当前可运行的零调用检查

```powershell
Set-Location 'D:\AS\AutoSkill-main\degradation_failure_lab'
python -B results/analysis/s24m001/round2/single_window_probe.py --bundle results/analysis/s24m001/round2/patched_ok
```

本轮已执行，得到OFFLINE_READY、model_calls=0。**execution_authorized仍为false；该配置字段是授权状态记录，真正执行由后续批准及显式--execute控制，不能把它误当作程序自动审批锁。**

### 6.2 获批后才可执行的唯一命令

凭据保持现有安全加载入口；本轮不读取密钥。下列命令只供用户后续批准一次调用后使用，当前未执行：

```powershell
Set-Location 'D:\AS\AutoSkill-main\degradation_failure_lab'
python -B results/analysis/s24m001/round2/single_window_probe.py `
  --bundle results/analysis/s24m001/round2/patched_ok `
  --out results/analysis/s24m002/single_window_live_001 `
  --execute
```

输出目录必须不存在。请求前先验源文/窗口/请求/prompt和164项源码哈希；只POST冻结请求一次。禁止redirect跟随，HTTP重试和JSON修复均为0；没有Outline、窗口循环、Expand、compile、register入口。超时、HTTP失败、空Plan和解析失败都立即返回；同输出目录第二次启动因排他创建而拒绝。

保存request.json、原始response.raw.json（先存后解析）、attempt.json中的window/request/prompt哈希，以及result.json里的usage/model/耗时/候选与失败分类；HTTP错误另存原错误体。网络代理环境不自动继承，若直连失败就记录传输失败，不自动换路线或重发。一次超时可能已在服务端处理，不能因结果未知自动重试。

保证范围为**本入口的一次执行及同一输出目录最多一次API尝试**；人工改目录重新运行属于新的执行，须另行确认。配置在入口中直接读取，普通lab.py run不会自动使用它。

### 6.3 本轮无模型验收与判断边界

- 原有 `A1/round2/test_single_window_probe.py` 本轮重验 **9/9通过**：空数组、解析错误、schema异常、name过滤、非空待语义审查、超时、HTTP429/redirect、截断、封装错误；fake transport记录每例一次调用，重用输出目录拒绝。
- 新增 `A2/test_probe_transport.py` **2/2通过**：直接测试真实post_once函数、用本地fake opener拦截网络，确认POST内容就是冻结body、只open一次、包含NoRedirect处理器；传输错误无第二次open。
- 两类测试均装有audit hook禁止socket/subprocess，**没有真实模型响应**。原30项预处理/兼容测试只复用上一轮已验收记录，本轮未重复运行。
- 仍返回EMPTY_PLAN：本次可排除已知目标上下文丢失，但一次观察不能独立区分prompt偏保守与模型能力/判断；保留原因未知。
- JSON_PARSE_FAILURE、SCHEMA_MISMATCH、CANDIDATE_FILTERED、TRANSPORT_ERROR分别记录。NONEMPTY_PLAN只表示有候选，还须独立审查是否明确表达FTP overwrite默认及例外；不得自动算Skill成功或继续Expand。

最小下一步是这个**已经冻结保真输入的一次原版Plan请求**。本轮到此停止；s24m002不构成修复版失败证据，也没有新的CleanSkill生成或Agent校准结果。

## 7. 复现与证据完整性

本轮分析在现有C盘审计暂存目录执行，最终新增A2目录；R1/R2及A1不改。`A2/evidence_verified/integrity.json`验证原运行各122文件未变、A1原有84文件未变。原始artifact_manifest中的121条和wrapper_manifest全部通过。

| 新证据 | 用途 |
|---|---|
| evidence_verified/code_comparison.json | 原版/记录/固定克隆与修复副本SHA |
| evidence_verified/import_paths.json | 实际本地导入函数路径与哈希；不启动模型 |
| evidence_verified/summary.json | 逐项计数、精确重放、成本和原运行状态 |
| evidence_verified/window_request_checks.json、csv | 18窗与真实请求映射及完整哈希 |
| evidence_verified/windows/ | 18份历史实际正文派生导出 |
| evidence_verified/filter_replay.json | FTP preview作者误判及三个段落筛选输出 |
| evidence_verified/section_differences.json | 两次Outline层级/元数据差异 |
| probe_contract/tests.json、transport_contract/tests.json | 9+2项本轮本地合同测试 |

零调用复现分析（out需换成不存在的目录；patched参数指向上面已验证的独立副本）：

```powershell
python -B 'D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m002\analyze_s24m002.py' `
  --lab 'D:\AS\AutoSkill-main\degradation_failure_lab' `
  --patched 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\scrapy024_preflight\calibration_evidence\s24m001_round2_staging\round2\work\patched_upstream' `
  --fixed-clone 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\AutoSkill-official-94c47ca' `
  --out 'D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m002\recheck_evidence'
```

分析脚本只重放保存的Outline返回值，audit hook禁止网络/子进程及输出目录外写入，不调用lab.run、extract_from_doc或真实模型客户端。首轮CSV导出把usage的缓存详情字段展开到固定三列造成列不匹配，随后仅修正导出选择；最终evidence_verified完整运行通过。该审计脚本错误没有改变历史数据或产生API请求。
