# Scrapy024 Clean 提取失败：s24m001 零模型调用事后诊断

审查完成日期：2026-10-23（Asia/Shanghai）；原运行日期：2026-10-22。对象：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m001`。

**结论：18 个 Plan 请求均成功返回合法的 `{"skills": []}`，因此没有候选进入 Expand、Draft 或 SkillSpec。适配器随后因 `total_skill_specs=0` 将本次运行记为 `exit_code=2`。现有证据不支持“token 或请求次数限制导致失败”。**

另确认两类独立问题：目标规则的完整上下文在进入 Plan 前已经丢失；两个不同窗口共用一个 ID，导致检查点不能独立表示它们。前者影响 Clean 输入保真，后者影响证据与续跑可靠性。它们不能直接解释模型为何对全部 18 个窗口选择空列表。

本轮新增模型/HTTP 请求 **0**；未执行生成、Agent、Oracle 或正式退化实验；未修改原运行、官方源码、原始 Oracle 或历史报告。下一步应先完成**零调用的文档到窗口保真与窗口身份检查**，暂不直接重跑 18 次提取。

## 1. 证据恢复与边界

本文区分：**已保存事实**（实际请求、响应、产物）；**确定性离线重放/源码推断**（从固定源码抽取纯函数，输入既有数据）；**待验证假设**（模型内部判断原因）。离线重放不是新的真实模型运行。

| 核查项 | 结果与证据 |
|---|---|
| 原运行完整性 | 原 `artifact_manifest.json` 的 121 项全部匹配；含 manifest 共 122 个文件，诊断前后逐文件 SHA-256 相同。见 `evidence/run_inventory_before.json`、`run_inventory_after.json`。 |
| 运行器快照 | `wrapper_manifest.json` 所列 10 个快照文件全部匹配。分析退出码使用本次运行的 `wrapper_snapshot/`，不是当前开发版。 |
| 原版源码 | 原运行 `upstream_before.json` 与 `upstream_after.json` 相同；164 个记录文件与当前可读上游、固定克隆 `AutoSkill-official-94c47ca` 均逐字节相同。固定基准为 `94c47ca488d4ba4117d20272e66d49b9877e68cf`。这是文件核对结论，不额外宣称 D 盘目录的 Git HEAD 状态。 |
| Clean 来源 | SkillGenBench `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d` 发布快照的 task-curated `feed-exports.md`，不是已验证完整保真的最新官方手册。来源记录见 `data/manifests/sgb_scrapy024_provenance.json`。 |
| 请求与响应 | `http/001` 至 `http/019` 各有 `request.json`、`response.json`、`event.json`；19 个响应文件哈希均与事件记录相同，事件标记 `returned_body_unchanged=true`。没有补造响应。 |
| 中间状态 | `SkillBank/.runtime/intermediate_runs/20261022T215553_a402e3b9/` 下保存 ingest、extract、compile、register 结果与状态。18 个输入窗口保存于 ingest，但逐窗提取摘要只有 17 份，原因见第 2 节。 |
| 缺口 | 没有模型对“为什么返回空列表”的解释/推理文本；没有提供方实际账单；两个撞 ID 窗口各自独立的提取摘要无法从被覆盖的路径恢复，但其不同输入和各自 HTTP 响应仍完整。 |

实际源文件为 `runs/case024_scrapy/clean/s24m001/inputs/input001/feed-exports.md`，原始字节 SHA-256：

```text
a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d
```

按 Python 通用换行读取、转 UTF-8 后的 SHA-256 为 `146fb31cfd581caf9db541241170395ce73e47148e105f9ccd8965d27e157042`。ingest 的 `raw_text` 只比该规范化文本少最后一个 LF，长度 24,629 字符，哈希为 `17dd35bd2491dc078ccbc0783844256f3ba57dc66420fbabcbbbc7797f4f1660`。这不是目标规则缺失的原因。

本报告附有仅依赖 Python 标准库的 `diagnose_offline.py`。它禁止 socket、子进程和输出目录以外的写入，不导入 SDK、不加载凭据。执行输出为 `evidence/findings.json`。脚本首轮发现源文件末尾 LF 与 ingest `raw_text` 不同，随后将该规范化明确记录并完成检查；未因此修改任何源材料。

## 2. 18 个窗口是否不同、是否逐个调用

**18 个窗口文本 SHA-256 全部不同，18 个完整 Plan 请求文件哈希也全部不同。** 将每次请求的 `excerpt` 与 `section.span` 同时匹配到 ingest 窗口，每次恰好匹配一个窗口；全部 18 个窗口各调用一次，未发现漏发、重复全文输入或错误循环。以下序号从 1 开始；原请求 `001` 是 Outline。

| 窗口 | HTTP | window_id | 文本 SHA-256 前 16 位 | 输入 tokens | 输出 tokens |
|---:|---:|---|---|---:|---:|
| 1 | 002 | d86b75e4-70ba-54c6-8a4b-0d0ec4d0d20b | 57f4e7848a318ea0 | 3354 | 5 |
| 2 | 003 | 77c7847e-bb60-568e-86a7-c42c792cc860 | 95666106aff732f5 | 3593 | 5 |
| 3 | 004 | b467a680-a444-539a-baec-262ed0b26ec9 | 440039a09e3899d3 | 3652 | 5 |
| 4 | 005 | 0f823f69-3873-5cb2-817c-89e8f4850baa | e32d01ee7f178bc7 | 3625 | 5 |
| 5 | 006 | 414f7da6-3023-5c2a-93d6-d0595a641d72 | 60886fe84437eb32 | 3636 | 5 |
| 6 | 007 | d5e899c9-37ff-5f44-ab9e-8d1ae9bddfb9 | 5929f2e2c716ddc2 | 3634 | 5 |
| 7 | 008 | 76b75304-a227-5a7a-a778-719476b5f149 | eef271396e5e8615 | 3651 | 5 |
| 8 | 009 | b20c5d95-f076-588e-93d0-4f2abad08203 | bc9a17620402e6f4 | 3664 | 5 |
| 9 | 010 | 0f799620-5476-5609-8e5c-2667ebf1e366 | 1c73ae2637abfdcc | 3628 | 5 |
| 10 | 011 | 54f55cce-755a-5454-89dd-decf76d85506 | 3d4eb39df68a5f8f | 3638 | 5 |
| 11 | 012 | 4d033c5d-209b-5d82-a2ea-ff8871dd6761 | 55d49aa41b4b3183 | 3621 | 5 |
| 12 | 013 | a359c78f-e161-5d57-b141-bdd1b1426f19 | d3c3a998d17afbc9 | 3587 | 5 |
| 13 | 014 | 6857ef71-864c-5229-90dd-9169b499c571 | ee598461055f3bd0 | 4245 | 5 |
| 14 | 015 | 3072cbc5-83ac-585a-88b6-23dede41bb01 | 01cb7735cf4c6339 | 4198 | 5 |
| 15 | 016 | 7d644ee8-c499-5631-9272-b93a193b7d02 | fe74bdec411e4d9b | 4019 | 5 |
| 16 | 017 | ebc96826-a2c0-5ac3-8aa4-4fac54ec92ac | 33e41ef45928a5ba | 3707 | 5 |
| 17 | 018 | d5494dda-f37d-5060-914b-78d61316c07c | 996bc47803e5c8ff | 3557 | 5 |
| 18 | 019 | b20c5d95-f076-588e-93d0-4f2abad08203 | c183c2af804ef737 | 3617 | 5 |

完整 64 位哈希、请求/响应哈希、窗口长度、声明 span、chunk 序号及 token 数在 `evidence/window_request_map.csv`；实际窗口文本保存在 `evidence/windows/`。这些文件从已有 ingest 数据直接导出，没有重新生成窗口。

### 确认存在 ID 冲突

第 8 和第 18 个窗口共用 `b20c5d95-f076-588e-93d0-4f2abad08203`，但分别是 chunk 1 和 chunk 3，文本长 562/342 字符，声明 span 为 `[4831,5393)` / `[23259,23601)`。两者均为 heading=`Feed exports`、局部 paragraph 27–29、strategy=`strict`。

`AutoSkill4Doc/document/windowing.py:472` 的 UUID key 只有 `doc_id:heading:paragraph_start:paragraph_end:strategy`，没有 chunk、span 或文本哈希。按保存字段离线计算 UUID 可复现冲突。`store/intermediate.py:287`、`:301` 又以该 ID 作为唯一文件名，因此最终只有 17 份逐窗摘要。aggregate 记录 expected IDs 长度 18、processed IDs 长度 17，却标记 `complete=true`。

本次新运行中两份文本分别通过 HTTP 009 和 019 发出，因此**冲突没有造成此次漏发，也不是 18 个空列表的直接原因**。但 `pipeline.py:1007` 起按 ID 集合判断已处理窗口，续跑可能将另一个不同窗口误当作已完成；`intermediate.py:556` 起按 ID 读取结果，也无法独立恢复两份摘要。此项是源码支持的续跑风险，未在本轮启动续跑验证。

### 原文映射不能直接使用窗口 span

18 个声明 span 中只有 1 个能直接切出完全相同的原始文本。`windowing.py:552` 起将子节重新拼接，`:188` 起按拼接文本分块，`:143` 起由局部偏移构造 span；这些偏移不能普遍当作原文件位置。

本轮另对 109 个窗口段落做保留词序的空白规范化匹配：100 个唯一定位，9 个存在多个原文候选，没有无法匹配的段落。`evidence/source_alignment.json` 保留全部候选位置，不强行给重复文本指定唯一来源。窗口可能共享段落，这与重复发送整个窗口不同。

## 3. FTP 目标规则是否进入实际输入

**目标值片段进入 HTTP 015；完整的“FTP 后端默认 overwrite=True”参数规则及例外没有完整进入任何一次 Plan 请求。** 原文完整存在，损失发生在 ingest/windowing 路径。

| 原文位置 | 内容 | 实际请求核查 |
|---|---|---|
| 124–137 | FTP 小节与 `overwrite` 默认 `True` | Outline 选择了 FTP，但最终 sections 没有 FTP 小节；FTP URI 和该小节的完整上下文未进入 Plan。 |
| 438–439 | `overwrite` 控制覆盖/追加，True/False 语义 | 所有 19 个保存请求的 user 内容中均无该定义。 |
| 441–443 | 默认值表：Local=False、FTP=True | 窗口 14 / HTTP 015 的 `excerpt` 中真实存在；唯一原文匹配为 441–443 行。 |
| 445–446 | FTP 服务器可能不支持 APPE 追加 | 所有保存请求的 user 内容中均无 `APPE`。 |

HTTP 015 中实际相邻内容为：

```text
- `item_filter`: a filter class to filter items to export.

The default value depends on the storage backend:
  - Local filesystem: `False`
  - FTP: `True`

The plugins will be used in the order of the list passed.
```

因此不能仅凭搜到 `FTP: True` 就判定目标规则保真通过。`overwrite` 定义被移除后，该表甚至紧接在 `item_filter` 后，存在作用域误配风险；是否实际诱发模型误解仍是待验证假设。

### 3.1 FTP 小节在正文过滤阶段丢失

已保存的 Outline 响应 `http/001/response.json` 选择 candidate 13（FTP），level=3；该候选的 `line_index=-1` 是规则候选的通用标记，并不是丢失原因。`ingest.py:758` 起用候选保存的 start/end 建节，不依赖这个 line_index。

`ingest.py:109` 的 `_looks_like_front_matter_heading` 将较短的字母标题与 preview 中的 `@` 组合视为作者信息。FTP 正文前 240 字符含示例 `ftp://user:pass@ftp.example.com/path/to/export.csv`，标题 `FTP` 符合该条件；`:528` 随即跳过整个小节。

对原函数及原 preview 的零网络 AST 重放返回 `True`，与保存的 sections 缺失 FTP 相符。此为**确定性源码/输入证据**；本次运行没有逐分支日志，不将离线重放冒充历史分支遥测。不能将此损失归因于 Outline 没选中 FTP。

窗口 9 / HTTP 010 与窗口 11 / HTTP 012 含相同字面的“this storage backend ... True”，但相邻内容分别为 S3 与 GCS 配置。原文有重复段落，不能据此声称 FTP 的重复支持位置 136–137 被保留。

### 3.2 参数定义和例外被段落长度筛选移除

`windowing.py:277` 起保留命中 anchor/process signal 的段落，否则只保留长度不超过 320 的段落。`:257` 的 bullet 判断只匹配段落开头，不会因为中间某行是列表项而命中。

| FEEDS 中的原段落 | 字符数 | process signal | 原筛选结果 | 已存窗口 |
|---|---:|---|---|---|
| 以 `` `ItemFilter` is used be default. `` 开头，包含 438–439 行 overwrite 定义 | 379 | False | 丢弃 | 全部缺失 |
| 441–443 行默认值表 | 95 | False | 保留 | HTTP 015 |
| 以 `Some FTP servers...` 开头，包含 APPE、其他后端和后续设置 | 413 | False | 丢弃 | 全部缺失 |

原函数离线重放与已存窗口一致，详情在 `evidence/findings.json` 的 `rule_block_filter_replay`。这也说明只改 `section_outline_mode=rule` 或只改 domain 并不能自动解决问题；`chunk` 分支同样经过 `_build_paragraph_blocks`，不能未经验证就宣称切到 chunk 可恢复全部正文。

## 4. 全部提取为空的直接原因、prompt 与 schema

19 次实际响应均为 `deepseek-flash`。HTTP 002–019 的 `message.content` 逐字相同：

```json
{"skills": []}
```

它们是非空字符串、合法 JSON，每次 completion_tokens=5、finish_reason=`stop`，没有 reasoning_content。18 份响应的内容相同，不代表输入相同。未发现截断、空响应、格式错误、命名候选被丢弃或验证器拒绝候选。

确定的代码路径：

1. `core/llm_utils.py:28` 获取文本，随后 JSON 解析成功；没有触发 JSON repair 请求。
2. `stages/extractor.py:877` 得到 `raw_skills=[]`，`:881` 的候选循环不执行，返回空列表。
3. `stages/extractor.py:978` 命中 `if not planned: return []`，不调用 Expand。
4. 没有候选进入 `:1010` 的必填字段检查或 `:1022` 的执行内容检查；不能称“候选全部被过滤”。
5. `stages/compiler.py:635` 由空 drafts 得到空分组，`:654` 没有迭代，编译器没有调用模型。

`official_call_trace.json` 记录 Plan 18 次，没有 `_expand_planned_skill`；extract/compile 的错误数组为空。新增 `evidence/offline_parser_replay.json` 对全部 18 个保存响应重放上述解析和早返回分支，并用 spy 禁止进入 Expand，18 次均符合该路径。

### 实际配置与提示词

实际配置来自本次 `config.json`，传输请求以 `http/*/request.json` 为准：

| 参数 | 本次值 |
|---|---|
| provider / endpoint | DeepSeek；OpenAI 兼容接口 `https://api.deepseek.com/v1/chat/completions` |
| model | `deepseek-flash`（请求及响应一致；未保存不可变模型版本号，不能补称固定日期版本） |
| temperature / stream / thinking | 0 / false / disabled |
| max_tokens / max_input_chars / timeout | 16,384 / 100,000 / 180 秒 |
| extraction / outline | recommended（映射 strict）/ llm |
| max_candidates_per_unit / max_units_per_document | 4 / 0（不限制窗口数） |
| extract_workers / extract_retries / backoff | 1 / 1 / 1 秒；本次未发生重试 |
| max_chars_per_chunk / overlap / max_section_chars | 6,000 / 300 / 10,000；这些配置不等于当前 strict 窗口是等长 6,000 字符切片 |
| retrieval_score_threshold | 0.3；没有候选进入后续路径，不能将该值解释为本次 Plan 为空的过滤阈值 |
| embeddings | 本地 hashing，256 维，无 embedding API 调用 |
| domain / taxonomy / family | 空字符串 / default / 未分类技能；case 无 pipeline override |
| 外部总量上限 | 150 HTTP、450,000 已观察 tokens |

18 个 Plan 的 system prompt 相同，UTF-8 SHA-256 为 `295ee9cd6633d30897b2028a7a53a4e9b06a399c40c29b78d99413f515629be6`；全文保存于 `evidence/plan_system_prompt.txt`，taxonomy 保存于 `plan_taxonomy.json`。原提示词生成位置为 `AutoSkill4Doc/prompts.py:59` 起。所有已存消息中的 U+FFFD 替换字符计数为 0，不能把终端偶发显示乱码视为请求编码损坏。

输出约定是 `{"skills": [...]}`、最多 4 项，允许 0 项。每项字段包括 slot、name、description、asset_type、可选 asset_node_id、granularity、objective、domain/task_family/method_family/stage、可选路由字段、why_distinct、confidence。没有在 HTTP 中设置 `response_format`/JSON Schema；这里是提示词约定和本地解析规则，不是服务端强制的非空 schema。

提示词要求保守、偏好可执行 reusable contract；同时带有 therapist、session-phase、treatment flow 等表述。它也明确允许 `knowledge_reference`，所以不能据此认定软件文档必然无法处理。**“保守策略及领域表述不匹配”和“正文上下文损失”是有依据的解释方向，但模型没有说明为什么选择零候选，现有证据无法量化或独立确认各因素的因果贡献。** 本轮未进行任何新模型对照来验证这些假设。

## 5. exit_code=2、SkillBank 与 registry

本次运行器快照 `wrapper_snapshot/degradation_lab/adapter.py:140`：

```python
exit_code = 0 if result.get('total_skill_specs',0)>0 and not result.get('errors') and result.get('status')=='completed' else 2
```

`official_result.json` 的实际值是 `status="completed"`、`errors=[]`、`total_skill_specs=0`。因此**直接失败条件为 SkillSpec 数量不大于零**。SDK 四阶段执行完毕；外层将零产物标记 FAILED。这不是根据退出码猜测。

`exception.json` 不存在；异常分支默认的 exit_code 是 1，不符合本次路径。`execution.json` 记录的是适配器内部 exit_code=2；CLI 快照 `cli.py:81` 使用 `int(any(...exit_code...))` 聚合，若通过该 CLI 返回 shell，则其进程返回值为 1。后者是源码推断，没有保存用户 shell 的 `$LASTEXITCODE`，不将其声称为实测。

最终状态：

- supports=0、drafts=0、specs=0、upserted_count=0；canonical 提取包为 0。
- registry 的 documents=1，supports/skills/lifecycles/change_logs/provenance_links/version_history 均为 0。
- visible_tree 的 parent_paths/child_paths 均为空；library manifest 的 domains/profiles/families 为空。
- 物理上存在一份 `SkillBank/通用技能领域/总技能/SKILL.md`，tag=`kind:domain_root`、版本 0.1.0、Prompt 和 Family 目录为空，其 domain_manifest 的 families=[]。它是导航骨架，不能计作从 Scrapy 文档提取的可用 Skill。

compile 和 register 各执行了本地空结果收尾，未产生额外模型调用。没有因验证器拒绝所有候选而失败，也没有真实下游 Agent 或 Oracle 结果可报告。

## 6. 已花费调用量、重试与停止机制

| 阶段 | HTTP 次数 | prompt tokens | completion tokens | total tokens |
|---|---:|---:|---:|---:|
| Outline | 1 | 6,290 | 510 | 6,800 |
| Plan | 18 | 66,626 | 90 | 66,716 |
| Expand | 0 | 0 | 0 | 0 |
| compile / register 模型调用 | 0 | 0 | 0 | 0 |
| **合计** | **19** | **72,916** | **600** | **73,516** |

以上来自保存响应的 API usage，并与 `execution.json` 汇总一致。cached prompt tokens 共 31,744，已包含在 prompt_tokens 内，不能再次相加；缓存命中不等于重复全文请求。实际收费金额未知，运行记录 `billed_cost=null`，未使用推测价格生成精确费用。

19 个 logical_call_id 均不同，attempt_index 全为 1，retry_of 全为 null，network_diagnostics 的 transport_retries=0。全文重复 Plan 请求率为 **0/18=0%**，无漏窗。ID 冲突涉及 2/18 窗口、一个重复 ID；不要把这一比例写成请求重复率。

运行起止时间差约 74.19 秒。没有 HTTP 429、预算耗尽、超时、输出 length 截断或模型错误的保存记录；19 次均 success、finish_reason=stop。已观察调用数 19/150、tokens 73,516/450,000，也没有触及运行器上限。因此目前没有证据支持费用、token 配额或请求次数限额是这次零候选的直接原因；这不构成对提供方账户全部配额的独立查询。

现有防护：适配器在每次发送前检查调用次数与累计已观察 tokens（`adapter.py:76`）；原版有 10 次/60 秒限速。token 检查可能被下一份响应越过，运行记录已说明这一局限。合法空列表被视为成功处理一个窗口，不会触发错误重试，也没有连续空 Plan 的诊断暂停机制。因此当前流程会继续扫描其余不同窗口，直到全部完成再由外层判定零 Skill。

本次 18 次是完整覆盖的不同输入，不是可直接认定浪费的重复请求；但在已发现保真问题后照原配置整批重跑，或为“追问原因”另起模型调用，都没有必要。空的 compile/register 仅有少量本地开销，没有隐藏的后续收费步骤。

## 7. 最小修复与成本防护建议（本轮未实施）

| 优先级 | 建议 | 验收与边界 |
|---|---|---|
| P0 | 发送前增加独立的源文→实际窗口保真门禁 | 不只搜 FTP=True；核查参数名、覆盖/追加语义、FTP 后端归属、适用条件和 APPE 例外是否在可定位上下文中。当前保存输入应明确报 FAIL，不能通过人工补写 Clean 源文规避。 |
| P0 | 检查同 ID 是否对应不同文本/位置 | 当前第 8/18 窗口必须被检测；保留原 ID，外部日志用文档哈希、窗口序号、文本哈希及位置复合标识。检查点不可靠时禁止盲目续跑，保留旧 run。仅添加旁路日志不能自动修复官方续跑内部的 ID 冲突。 |
| P0 | 分开记录 EMPTY_PLAN、INVALID_JSON、FILTERED、TRANSPORT_ERROR、ZERO_CANONICAL | 18 个现有响应离线重放应归为 EMPTY_PLAN；导航 SKILL.md 不计成功产物。成功状态同时记录 pipeline_completed 与 usable_skill_count。 |
| P1 | 用外层调度设置阶段调用硬上限和失败停止 | 小试预先指定一个窗口及一次 Plan 请求；显式限制 HTTP 尝试数，格式修复/重试也计入上限。连续空结果可以暂停诊断，不直接把早期目录窗口为空当作文档一定无效。 |
| P1 | 完整记录模型、prompt、输入、输出和 token 预算 | 复用现有 request/response/event 保存机制；保留输出上限与剩余预算的检查，不能仅在新请求前查看已用量后假定不会超额。未知账单继续标未知。 |
| P1 | 将源文保真缺陷和模型空计划分开处理 | 修复前先用原保存响应验证解析器，无需收费；不能通过临时换模型、改提示词、补规则或手修 Skill 来制造成功。 |

**原版路径约束：** 修复 FTP 作者误判、长段落丢弃或窗口 ID 生成若需要改官方 ingest/windowing，就属于生成路径变更。本轮没有做这类修改。后续若必须实施，应在独立适配/修订分支中保存差异、单独命名实验条件，不能继续把它标为未经修改的原版结果。只有经零模型验证确实保真的公开输入/配置路径，才可在固定原版代码下进一步测试；目前没有证据保证某个配置开关足以解决上述两处损失。

若坚持当前固定原版默认路径，应保留 s24m001 为“Clean 文档经原版处理时上下文丢失且零 Skill”的有效失败观察，而不是删除它或用修复结果覆盖。是否调整输入接口/公开配置、接受适配条件或改用另一任务，应在继续收费前明确。

## 8. 修复后的一次受控验证计划与停止条件

1. **先完成零调用门禁。** 使用本次冻结文档与既有 Outline 响应做本地检查，核实原始字节未变、规则上下文完整、窗口身份不冲突、映射可追溯。重用 18 份现有空响应检验解析与状态分类。门禁失败就停止，不启动收费请求。
2. **冻结变更类别。** 记录属于旁路观测、原版公开配置还是修改生成路径。后两者须保留独立配置/代码哈希和新的 run ID，不能覆盖 s24m001，也不能冒称与本次默认基线完全相同。
3. **确认后只试一个预先选定窗口。** 仅当步骤 1 已得到完整包含目标规则的合法输入时，使用固定的原版 Plan 提示词及事先确认的模型配置，外部硬上限为 1 次 HTTP、无自动重试。保存精确请求/响应、模型返回名称、usage 和状态。该试验只验证 Plan，不能算端到端校准通过；如果公开原版路径无法产生保真输入，则这一步保持阻塞。
4. **立即判定并停止。** 仍返回 `skills=[]`：记 EMPTY_PLAN，保留模型判断原因未知，不继续扫描、不自动改 prompt/model；格式或传输错误：分别归类，不用新模型“解释”。非空：记录候选与目标规则的关联，随后再决定是否开展有单独预算的 Expand→compile→register 验证。
5. **进入 Agent 前另设门槛。** 只有生成并冻结了真实 canonical Skill，才接现有安装器、正文曝光观察器及独立 Oracle；真实 Agent 阅读与六次校准均未在本轮验证。不得把一次非空 Plan 或导航骨架当作 CleanSkill 条件已准备完成。

## 附：零模型复现与证据索引

以下命令只分析已有文件，不运行 `lab.py run`，不需要任何 API 密钥：

```powershell
Set-Location 'D:\AS\AutoSkill-main\degradation_failure_lab'
python -B results/analysis/s24m001/diagnose_offline.py `
  --run 'D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m001' `
  --upstream 'D:\AS\AutoSkill-main\AutoSkill-main' `
  --out 'D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m001\recheck'
```

本轮实际离线分析在可写 C 盘审计暂存目录执行，另加 `--fixed-clone 'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\AutoSkill-official-94c47ca'`，因此同时完成了 164 文件固定克隆核对。上述复现命令省略可选 clone 检查，仍核对原运行记录的上游哈希；需要复现该项时加回同一参数。

| 新增证据 | 用途 |
|---|---|
| `evidence/findings.json` | 汇总、哈希、规则过滤重放、计数与完整性结果 |
| `evidence/window_request_map.csv` | 18 窗口完整哈希、ID、请求映射、token 与目标片段标志 |
| `evidence/windows/` | 从既有 ingest 导出的 18 份真实窗口文本，序号避免撞 ID 覆盖 |
| `evidence/source_alignment.json` | 109 段的全部原文候选位置与歧义标记 |
| `evidence/http_analysis.json` | 19 个调用的请求/响应哈希、解析结果、usage、重试字段 |
| `evidence/offline_parser_replay.json` | 18 份原始空响应的本地解析与早返回核验 |
| `evidence/outline_evidence.json` | 已保存 Outline 候选及响应解析，证明 FTP 曾被选中 |
| `evidence/plan_system_prompt.txt`、`plan_taxonomy.json` | 实际 Plan 输入约定 |
| `evidence/run_inventory_before.json`、`run_inventory_after.json` | 原运行 122 文件前后不变的证据 |

原始请求、响应、日志与 SDK 中间产物仍以 s24m001 原目录为准；新增证据是可重算的审计派生文件。**本轮工作到报告交付为止；继续模型验证须等待用户确认。**
