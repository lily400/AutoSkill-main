# s24m005 部分成功及 SSL 中断审计

审计日期：2026-10-23。本轮真实模型 HTTP 请求 **0 次**。未恢复、重试或重跑历史流水线。随后按用户“修改代码支持断点”的授权，只修改实验室适配代码并执行无网络夹具测试；官方源码和历史运行保持不变。

**已证实：**s24m004 的真实 Plan 身份为 default；s24m005 为 scrapy。21 个生成窗口的正文和 span 相同。s24m005 前 7 个窗口产生并保存 7 个草稿及 7 条 support；第 8 个窗口的 Plan（HTTP016）因 SSL EOF 中断，最终 Skill 为 0。**证据支持但未证实：**领域身份配置是非空候选出现的解释之一，与此前身份对照方向一致；两次完整运行还有运行身份、路径和时间变化，不能证明唯一因果。**未知：**EOF 由本地代理、链路还是远端引起，失败请求是否已被服务端处理或计费。

## 1. 实际配置及代码差异

| 项目 | s24m004 | s24m005 |
| --- | --- | --- |
| case.json pipeline_overrides.domain_type | 无 | scrapy |
| config.json pipeline.domain_type | 无 | scrapy |
| 真实 Plan System Prompt 领域行 | externally provided as default | externally provided as scrapy |
| taxonomy.domain_type / taxonomy_id | default / default，21 条 Plan | scrapy / scrapy，8 次 Plan 尝试 |
| document.domain | 空字符串 | 空字符串 |
| document.metadata.domain_type / taxonomy_id | default / default | scrapy / scrapy |
| metadata.profile_id | default::未分类技能 | scrapy::未分类技能 |
| metadata.domain_root_id / family_source | default / default | default / default |
| sections / windows | 36 / 21 | 36 / 21 |
| HTTP 尝试 / 成功完成响应 | 22 / 22 | 16 / 15 |
| Outline / Plan / Expand | 1 / 21 / 0 | 1 / 8（最后一次失败）/ 7 |
| 原始 Plan 候选 / 保存草稿 / 最终规格 | 0 / 0 / 0 | 7 / 7 / 0 |
| 日志报告 Token | 84,180 | 66,540，失败请求 usage 未知 |
| 官方 summary.status / 外层退出码 | completed / 2 | failed / 2 |

模型和请求参数逐条核对一致：deepseek-flash，temperature=0，stream=false，max_tokens=16384，thinking.type=disabled；事件记录的端点均为 https://api.deepseek.com/v1/chat/completions。成功响应的指纹均为 e72d3c7f663d3e1383b00b3884cb4501；HTTP016 没有响应指纹。

两份 config.json 的唯一字段差异为 /pipeline/domain_type；两份 case.json 的唯一字段差异为 /pipeline_overrides/domain_type。原始请求以各自 http/NNN/request.json 为证，不按命令推断：
[s24m004 第2窗口真实请求](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m004/http/003/request.json)；
[s24m005 第2窗口真实请求](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/http/003/request.json)；
[s24m005 第8窗口真实请求](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/http/016/request.json)。

所有 8 对实际 Plan 请求的 excerpt、section（含标题、上下文、span）、max_candidates 相同。除上述领域行和 taxonomy 身份外，实际请求还改变 document.doc_id、metadata.lab_run_id、execution_path/source_file、resume_key、profile_id。这些是两次完整运行的实际差异，不能称为逐字节单因素实验。document.domain 仍为空不代表外部 scrapy 配置没有生效；domain_root_id/default 家族回退也不能覆盖真实 system/taxonomy 字段。

两个运行的 upstream_before/after 四份清单完全相同，覆盖 166 个文件；当前官方目录逐文件哈希仍匹配。两份历史 wrapper_manifest 完全相同（10 文件）。因此两次运行之间未观察到已清单化源码变化。**本次新增断点功能后的实验室 wrapper 是新版本**，不冒充历史 wrapper；官方目录没有改动。来源文档 SHA-256 均为 a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d。

配置路径：历史 [runner.resolve](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/wrapper_snapshot/degradation_lab/runner.py:59) 合并 case 的 pipeline_overrides；[原适配器传入配置](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/wrapper_snapshot/degradation_lab/adapter.py:135) 将 **cfg.pipeline 交给官方公开入口。领域配置这次确实进入完整流水线。

## 2. 七个草稿与 support 的保存

原生检查点根目录：

[20261023T202941_561c266d 检查点](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/SkillBank/.runtime/intermediate_runs/20261023T202941_561c266d)

下表所有草稿均在 extract/windows/<doc_id>/<window_id>.json 的 skill_drafts 中原样保存，并存在完全相同的 extract/result.json 副本；每个草稿的 support_ids 均能找到同文档、同窗口 support，窗口 support 与全局 support 内容一致。

| 窗口 | Plan/Expand HTTP | 草稿名称及类型 | draft_id | support_id |
| --- | --- | --- | --- | --- |
| 2 | 003/004 | 配置 Feed 导出序列化格式 (session_skill) | 1da7ac96-9d58-5ee1-bfed-cc6209ba94e9 | 5c283b79-f33d-554e-a0bf-103bf87b1392 |
| 3 | 005/006 | 配置 Feed 导出格式与存储 (session_skill) | 3b63bb9e-0066-5805-bb78-f5d7488867c0 | a0011b8b-ff3b-5102-a9b6-cd215fc0f281 |
| 3 | 005/007 | CSV 导出列字段控制 (micro_skill) | 615b7112-76c8-50cd-b80f-7c8a2d8a6738 | be556a49-e292-5624-8f41-9295470db478 |
| 3 | 005/008 | 自定义 Feed 导出器扩展 (micro_skill) | f2eb0d55-c842-536c-ba36-445ebb05920a | 99d5fb80-704c-5bce-83d3-973f5ed2eed8 |
| 5 | 010/011 | Feed 存储 URI 参数替换 (micro_skill) | a49a5b07-6c22-5a7d-bd2f-1edc564a88b1 | 83479ffa-741b-57ff-90ce-1a475311b002 |
| 6 | 012/013 | Feed 存储 URI 参数化配置 (micro_skill) | e619efeb-0752-5917-a34e-67e7cc694436 | c0747914-b67b-51ab-98ed-14261db6d75a |
| 7 | 014/015 | 本地文件系统 Feed 导出配置 (knowledge_reference) | 43e48c8e-a955-5bf3-b83c-aea5fc28ecbb | 33ddb24e-13cd-5d13-b474-c4e86340464b |

草稿所在窗口文件：
- 窗口 2：[e7a2f0c6-6a45-5300-a8e2-33698b083c57.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/SkillBank/.runtime/intermediate_runs/20261023T202941_561c266d/extract/windows/746b8660-57be-5a86-bc5c-fdd89bdae86d/e7a2f0c6-6a45-5300-a8e2-33698b083c57.json)
- 窗口 3：[ec7333ab-7789-5c91-8198-c58e0a938f37.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/SkillBank/.runtime/intermediate_runs/20261023T202941_561c266d/extract/windows/746b8660-57be-5a86-bc5c-fdd89bdae86d/ec7333ab-7789-5c91-8198-c58e0a938f37.json)
- 窗口 5：[2ba801a6-b145-5048-a547-15f3ccac9f93.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/SkillBank/.runtime/intermediate_runs/20261023T202941_561c266d/extract/windows/746b8660-57be-5a86-bc5c-fdd89bdae86d/2ba801a6-b145-5048-a547-15f3ccac9f93.json)
- 窗口 6：[601fd9d3-3489-5cf6-90f1-00e4a49d0fe5.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/SkillBank/.runtime/intermediate_runs/20261023T202941_561c266d/extract/windows/746b8660-57be-5a86-bc5c-fdd89bdae86d/601fd9d3-3489-5cf6-90f1-00e4a49d0fe5.json)
- 窗口 7：[5a26d374-042e-5afe-bc53-91153ef7ccbb.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/SkillBank/.runtime/intermediate_runs/20261023T202941_561c266d/extract/windows/746b8660-57be-5a86-bc5c-fdd89bdae86d/5a26d374-042e-5afe-bc53-91153ef7ccbb.json)

窗口 1、4 合法空候选；窗口 2/3/5/6/7 分别为 1/3/1/1/1 个候选。所有 7 次 Expand 响应也保存在 HTTP004、006、007、008、011、013、015，未见后续替换或删除窗口草稿的证据。

注意：extract/documents/<doc_id>.json 与 extract/aggregate/<doc_id>.json 是文档失败标记，supports/skill_drafts 数组为空；并非所有汇总文件都保存了草稿。官方 [write_extract_error](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/store/intermediate.py:418) 明确这样写失败快照；窗口检查点和 extract/result.json 中仍有 7/7。官方 [跳过未完成文档的编译](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/pipeline.py:1369) 将该文档记为 skipped，故没有生成规格或注册 Skill。注册和编译的外层函数及空结果文件存在，不等于其模型阶段实际执行。

SkillBank 内实际 SKILL.md 文件数为 0；spec/upsert/lifecycle/provenance 均为 0。7 个草稿不能算 7 个最终 Skill。intermediate.current_stage=register_completed 只是最后写入阶段名，completed_stages 只有 ingest，status 仍 failed。

FTP overwrite 目标规则的完整上下文位于**窗口18**，这次尚未执行其 Plan。第8窗口仅涉及 FTP URI 和主动/被动连接模式；7 个现有草稿不能证明目标规则提取成功。

## 3. HTTP016 SSL 失败

证据：[HTTP016 事件](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/http/016/event.json)；
[日志第34–35行](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/pipeline.log:34)；
[网络配置快照](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/network_diagnostics.json)。

- UTC 2026-10-23 12:31:04.132008 开始，耗时 5.047 秒。
- window_id=048437eb-be39-5ac9-996f-ed6d287dc99e，span=4549..4967；正文 SHA-256=43bebffd40286c971c02b8007c5fccae7e08e6eea8d26ff7a78576b2fcaf86f7。
- 实际调用栈经过 _plan_unit_skills；不是 Expand、编译或注册失败。
- exception_type=URLError，reason_type=SSLEOFError；原始错误为 SSL: UNEXPECTED_EOF_WHILE_READING / EOF occurred in violation of protocol。
- request.json 已保存，SHA-256=4846680c42328b22f78f3c179a827a202d350522538e3438148ed7f2727d9414；event.json SHA-256=f8d4de51ff34d39954e9cacc9e97e2273cc48003728a1271fc64fe87904b7ba6。
- **没有 response.json 或已保存的部分响应**，没有 HTTP 状态码、response_id、finish_reason、usage。不能推断服务端未收到请求或未计费。
- proxy_mode=system；检测到 HTTPS 系统代理 127.0.0.1:7897。此路径是潜在故障点，但不能据 EOF 单独归因于代理，也不能断言远端故障、证书错误、配额或 Token 限制。
- 客户端把 urlopen 和 response.read 包在同一调用中，现有事件没有内部 traceback，不能区分 TLS 握手中断与读取阶段中断。
- transport_retry_eligible=true 仅说明自定义传输层白名单允许此异常；实际 transport_retries=0、attempt_index=1、retry_of=null，未重试。官方 extractor 的字符串重试分类不包含该 SSL EOF 文本，所以文档错误中的 retryable=false 属于另一层判断。extract_retries=1 本可额外尝试一次，但本异常未命中该分类。

成功响应累计 input=59,526、output=7,014、total=66,540。这是已记录 usage，不能作为包含失败请求的完整计费量。summary 的两条相同 extraction error 是错误汇总重复，并非两次 HTTP016。剩余13窗口没有发出请求；未完成列表包括失败窗口，共14个。

## 4. exit_code=2 的直接来源

历史 [adapter.execute 第140行](D:/AS/AutoSkill-main/degradation_failure_lab/runs/case024_scrapy/clean/s24m005/wrapper_snapshot/degradation_lab/adapter.py:140)：
只有 total_skill_specs>0、errors 为空且 status=completed，才退出 0；否则返回 2。

因此 s24m004 是官方完成但零规格，外层判为 2；s24m005 是提取中断、未完成且零规格，外层同样判为 2。不是 SSL 库直接返回退出码2，也不是七个草稿被语义验证拒绝。

## 5. 能否恢复，以及本次新增入口

**审计时已有的底层能力：**官方根据同一 store 内的 resume_key 寻找未完成检查点，读取成功窗口。[检查点发现与复用 ingest](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/pipeline.py:501)、[窗口筛选](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/pipeline.py:1005) 和 [从窗口恢复草稿/support](D:/AS/AutoSkill-main/AutoSkill-main/AutoSkill4Doc/store/intermediate.py:661) 支持跳过前7窗口。原 lab.py run 则拒绝同 run-id，并要求空 SkillBank；换新 ID 普通重跑会重新付费。

**按用户后续授权新增：**原目录 src/degradation_lab/resume.py、runner.py、adapter.py、cli.py 接通一个 resume 子命令。只复制到新目录；保留原输入路径、运行元数据和 resume_key，避免重新切窗或改变请求。官方检查点查找不匹配就报错，不回退全量执行；请求观察器另行拒绝 Outline 和已完成窗口。原模型、提示词及领域配置保持冻结。累计预算继承16次尝试及66540个已知 Token；失败 POST 的未知计费明确记录。新 HTTP 日志与父运行分开，以 resume.json 关联。

11 项无模型测试覆盖：真实检查点副本中仅调度8–21窗口、7个草稿/support保留、下一条请求与历史HTTP016请求体完全一致、再次SSL中断可再次准备恢复、禁止重置预算、断点身份不匹配时0请求停止、禁止已完成窗口/Outline、拒绝半成品窗口成功请求重发、目标目录不可覆盖、CLI连接及普通run空库限制。测试封锁 socket 与 urllib，SSL 通过确定性假传输注入；不构成真实网络恢复成功证据。

本入口当前限单文档提取阶段，且中断点必须是尚未成功返回的 Plan；窗口内已有成功 Plan/Expand 但没有完整窗口检查点时拒绝自动恢复，不能承诺任意位置精确恢复。重发失败HTTP016本身仍可能重复服务端已处理但客户端未收到的工作。SSL 网络故障尚未修复。

复现本地测试：
~~~powershell
python -B -m unittest discover -s tests -p test_resume.py -v
~~~

## 6. 下一步唯一优先任务与边界

由用户运行新入口，从第8窗口继续，而不是重新运行 run：

~~~powershell
cd D:\AS\AutoSkill-main\degradation_failure_lab
python -B scripts/lab.py resume --run s24m005 --run-id s24r005
~~~

此命令会真实调用剩余提取及后续编译/注册模型。新目录为 runs/case024_scrapy/clean/s24r005；运行前已确认该目录不存在，Windows 路径长度预检通过。本轮没有执行该命令。若再次失败，保留新目录并从最近中断运行以另一个新run-id恢复；若遇到不受支持的窗口内部断点、哈希或身份不匹配，停止，不做全量重跑兜底。

历史完整性复核：s24m004 的 134 项、s24m005 的 97 项原始 artifact_manifest 哈希全部匹配；官方 166 个文件仍匹配快照。未修改原始文档、原始HTTP记录、草稿、历史配置、Oracle或官方生成算法。没有真实恢复结果、没有正式Clean Skill生成成功结论。
