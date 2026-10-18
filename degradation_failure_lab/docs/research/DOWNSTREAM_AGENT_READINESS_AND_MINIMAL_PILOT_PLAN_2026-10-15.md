# Anything2Skill 下游 Agent 执行能力审计与最小实验方案

日期：2026-10-15（Asia/Shanghai）  
目标仓库：`D:/AS/AutoSkill-main`  
审计范围：只读代码与真实 Clean run 静态检查；未调用模型、未执行下游 Agent、未安装工具、未修改官方 Anything2Skill 源码或历史 run。

## Material Passport

- 材料：本地官方实现 `AutoSkill-main/`、实验工程 `degradation_failure_lab/`、五个指定 Clean run、47 份 canonical `SKILL.md`、既有 Clean 再审计侧车。
- 访问级别：本地源码、运行产物和已有分析文件；没有外部网络证据。
- 验证状态：`ANALYZED`，不是 `EXECUTED`。本报告中的“可测试”是实验设计判断，不是任务成功结果。
- 核心边界：静态文本错误不等于下游失败；`SKILL.md` 可解析不等于 Agent 已正确使用；LLM 自报成功不构成 Oracle。

## 1. 执行摘要与决策

**总决策：CONDITIONAL GO，但当前状态对真实下游任务仍是 NO-GO。**

仓库已经具备一条文本聊天链：加载 Agent Skill 目录、检索、可选 LLM 选择、把 Skill 的 Prompt 渲染进系统提示词、生成文本回复。五个 Clean run 的 47 份 canonical Skill 均存在、哈希与既有清单一致，并可被官方 `load_agent_skill_dir` 解析为 47 个唯一、非空的 Skill。

但仓库**没有**完成研究所需的工具执行 Agent：LLM 抽象只接受 `system + user` 并返回文本，没有 tool schema、tool-call 解码、动作循环、沙箱、任务 fixture 或最终状态 Oracle。因此，现有链路最多证明“Skill 可被检索并注入聊天上下文”，不能证明“Agent 使用 Skill 完成 qsv、Docker、Git 或 ripgrep 任务”。实验工程的 `verify/evaluation/aggregate` 检查的是运行产物、Schema、ID/行号/追踪关系和人工规则审查记录，不执行下游任务。

首个错误影响试点不建议机械沿用 Case001。当前 Windows 环境中 `qsv` 与 `docker` 均未找到，`git 2.53.0.windows.3` 与 `ripgrep 15.2.0` 可用。Case004 的已知错误“显式 `--source` 与 `--staged` 同时出现时误称来源变成 HEAD”能在一次性临时 Git 仓库中产生确定的不同状态，并有同 run 内的正确规则作对照。因此：

- **第一试点：Case004 git restore，run `r18307cee4f4c`。**
- 错误依赖 Skill：`d472e6a7-8895-56cb-9014-cb75cc3540b3`，`从指定 tree 恢复工作区文件`。
- 正常对照 Skill：`fd6ef816-81a2-5586-afb6-35aa6f45c10c`，`指定 git restore 恢复位置`。
- Case001 qsv select 是安装固定版本 qsv 后的第二候选；Case005 ripgrep 是可立即使用现有 CLI 的第二类候选，但 24 个同域 Skill 的检索竞争和互相矛盾会增加首轮归因难度。

下一轮的唯一优先任务应是：**在独立实验目录实现并离线自测一个仅允许白名单 Git 操作的最小 tool-execution harness、一次性仓库 fixture 和确定性 Oracle；先不调用付费模型。**

## 2. 证据基线与静态复核

五个真实 run：

| case_id | run_id | canonical 数 |
|---|---|---:|
| `case001_qsv_select` | `raecd75e08b34` | 4 |
| `case002_qsv_sort` | `rd9ced750fa54` | 3 |
| `case003_docker_cp` | `rab9a070dfa59` | 2 |
| `case004_git_restore` | `r18307cee4f4c` | 14 |
| `case005_ripgrep_guide` | `r64cee24fae18` | 24 |
| 合计 | 5 runs | **47** |

本轮直接复核结果：

- `results/analysis/five_case_clean_audit/skill_inventory.csv` 有 47 个数据行；47 个 `skill_path` 全部存在，47 个 SHA-256 全部与清单一致。
- 官方 `autoskill.management.formats.agent_skill.load_agent_skill_dir` 逐一解析 47 个目录：47 个唯一 ID、47 个非空 instructions、名称和 ID 均与清单一致。
- 五个 run 的 `SkillBank` 内共有 104 个物理 `SKILL.md`；canonical 仍是 `SkillBank/Users/docskill/*/SKILL.md` 的 47 个程序 Skill，不能把导航/可见树文件重复计数。
- 本轮没有读取错误的 `results/exports/` 作为其它案例证据；Skill 清单只作索引，每个路径和哈希均回到真实 run 核对。
- 工具发现：`git`、`rg`、`python`、`codex` 存在；`qsv`、`docker` 未找到。只执行了命令发现与版本查询，没有执行任务。

既有错误状态沿用 `results/analysis/five_case_clean_audit/error_traceability.csv` 的 `verification_status`；本报告只把 `CONFIRMED` 写为“已确认错误”，`UNKNOWN/INFERRED` 不升级为事实。

## 3. 当前下游 Agent 执行能力审计

### 3.1 能力矩阵

| 问题 | 结论 | 代码证据与解释 |
|---|---|---|
| 1. 是否存在可执行下游任务的 Agent | **NOT IMPLEMENTED**。存在文本聊天助手，不是工具执行 Agent | `UP/autoskill/interactive/session.py:557-704` 完成检索、注入和文本回复；`UP/autoskill/llm/base.py:13-41` 的接口只有 `complete/stream_complete(system,user,temperature)`，无 tools/tool_calls；全包搜索只发现文档读取、剪贴板和离线 Codex 反思所用的 subprocess，没有 qsv/Docker/Git/ripgrep 动作执行循环。 |
| 2. 实现、入口、模型配置 | **PARTIAL** | `AutoSkillRuntime.new_session` 在 `UP/autoskill/interactive/unified.py:65-80` 组装 `InteractiveSession`，`new_proxy_runtime/create_proxy_server` 在 `:82-107`；聊天会话类在 `interactive/session.py`。模型由 `UP/autoskill/llm/factory.py:108-240` 根据传入字典构造。顶层 CLI `UP/autoskill/cli.py:16-43` 只建空的 `offline` 命名空间并打印帮助；README 所称 `examples/interactive_chat.py`、`examples/openai_proxy.py` 在当前工作树不存在。没有为下游实验冻结的 executor 模型、预算或命令入口。`LAB/configs/generation/deepseek_flash.json:1-35` 只属于 Skill 生成，不是下游 Agent 配置。 |
| 3. 是否支持加载正式 SKILL.md | **IMPLEMENTED，但未接入实验** | `UP/autoskill/management/formats/agent_skill.py:262-355` 解析 frontmatter、`## Prompt` 和可选文件；本轮对 47 个 canonical 文件静态解析全通过。 |
| 4. 是否有完整 SkillBank 加载/检索 | **CORE IMPLEMENTED / LAB WIRING NOT IMPLEMENTED** | `LocalSkillStore._load_existing` 在 `UP/autoskill/management/stores/local.py:967-1080` 扫描 `Common`、外部库和 `Users/<user_id>`；`search` 在 `:614-705` 做 BM25/向量候选；工厂配置在 `management/stores/factory.py:93-227`。但 LAB 没有把某个 run 的 SkillBank 复制到可写工作区、设置 store path 和 `user_id=docskill`、再交给 executor 的代码。默认 `InteractiveConfig.user_id` 是 `u1`（`interactive/config.py:16-25`），直接指向 run 时不会在 user scope 看见所有者 `docskill` 的 Skill。 |
| 5. Agent 如何决定调用哪个 Skill | **文本检索/选择存在；动作调用不存在** | `retrieve_hits_by_scope` 在 `interactive/retrieval.py:61-132` 按 user/library scope 搜索；`LLMSkillSelector.select` 在 `interactive/selection.py:164-276` 用候选摘要让 LLM 选 ID，失败时退回关键词重叠。默认 `top_k=1`、`min_score=0.4`（`interactive/config.py:37-43`）。这只决定注入哪个文本，不会决定或执行哪个系统工具。 |
| 6. Skill 注入还是原生加载 | **显式文本注入，不是原生 runtime Skill** | `render_skills_context` 在 `UP/autoskill/render.py:53-117` 渲染名称、描述、trigger 和 Prompt；`InteractiveSession._build_assistant_inputs` 在 `interactive/session.py:1200-1224` 把其拼入 system prompt。启动扫描用 `include_files=False`（`local.py:995-1065`），不会加载 reference/script 内容。canonical 用户目录本身也只有 `SKILL.md`。 |
| 7. 下游任务数据和测试环境 | **NOT IMPLEMENTED** | LAB 非 run 文件只有生成案例、来源、规则、Schema、生成 wrapper 与研究报告，没有 task fixture、executor task、expected state 或 verifier。旧 `UP/research/robustness/runners/README.md:2-4` 明示仅为“设计稿，无实现代码”；`protocol/pilot_scope.md:25-27` 也声明 task instance、oracle、mutant、verifier 从后续任务另建。 |
| 8. 执行工具 | **外部环境部分可用，Agent 工具层 NOT IMPLEMENTED** | 当前命令发现：Git 与 ripgrep 可用；qsv、Docker 不可用。仓库没有把这些 CLI 包装成结构化、限目录、可审计的 Agent 工具。 |
| 9. 自动任务 Oracle | **NOT IMPLEMENTED** | 没有比较输出 CSV、容器文件、Git index/worktree 或 ripgrep 输出/源文件哈希的 verifier。旧研究目录只有契约说明，没有实现。 |
| 10. evaluation 是否判断真实任务结果 | **否** | `LAB/src/degradation_lab/artifacts.py:108-164` 检查哈希、模型调用、阶段文件、ID 链、canonical 文件和支持证据；`:153` 明确 `quality_status='SEPARATE_RULE_EVALUATION_REQUIRED'`。`evaluation.py:10-51` 校验 Schema、规则 ID、trace ID 与行号；`:71-108` 仅汇总人工状态并明确“不制造准确率”。CLI 命令集合 `src/degradation_lab/cli.py:11-70` 没有 downstream-run 或 oracle 子命令。 |

### 3.2 “能读取”到“能完成任务”的缺口

```text
已有：canonical SKILL.md
  -> parser
  -> LocalSkillStore
  -> BM25/vector retrieval
  -> optional LLM selector
  -> system-prompt text injection
  -> text completion

缺失：task fixture
  -> tool schemas / allowlist
  -> model tool-call loop
  -> isolated working directory
  -> action/state trace
  -> deterministic oracle
  -> A/B/C condition controller
  -> repeated-run aggregation
```

现有 `LLMSkillUsageJudge` 也不能替代真实使用证据。它让同类 LLM 根据 query/reply 判断 `used`（`UP/autoskill/interactive/usage_tracking.py:103-220`），解析失败则用关键词重叠（`:61-99`）。这可作诊断字段，不能作为“Agent 实际依据了目标规则”的主判据。

### 3.3 复用 run SkillBank 时的安全要求

不得把 LocalSkillStore 直接指向冻结 run 并允许其建立索引/usage 文件。`LocalSkillStore.__init__` 会创建根目录、向量/关键词状态并加载现有内容（`local.py:279-299`），使用统计也可能持久化。最小方案必须：

1. 从 run 中只读复制目标 canonical Skill 到 `downstream_pilot/frozen_skills/<condition>/Users/docskill/...`；
2. 记录源路径、源 SHA-256、复制后 SHA-256；
3. 原版条件 A 不修改字节；修正版条件 C 只在派生副本改目标错误；
4. runtime 的索引、日志和 usage 状态写到派生目录，永不回写 `runs/`。

## 4. 当前 evaluation 与真实任务 Oracle 的差距

| 现有检查 | 能证明 | 不能证明 | 最小补充 |
|---|---|---|---|
| `verify`/`inspect_run` | 生成运行完成、文件存在、哈希/ID/阶段链一致 | Skill 语义正确、被下游加载、工具动作正确 | executor run manifest + tool trace + final-state oracle |
| `evaluation-validate` | 人工规则记录引用了真实 rule/skill/trace/行号 | 人工判断正确；任务成功 | 独立 fixture expected state 与机器 verifier |
| `aggregate` | 汇总人工 review 状态并保留版本 | task success rate、错误因果效应 | 每次 trial 的 condition/task/model/budget/verdict；按预注册重复聚合 |
| AutoSkill usage judge | LLM/词汇判断某回复似乎用了 Skill | Skill 改变了命令或最终状态 | 精确注入哈希 + 目标 action feature + Oracle |

真实 Oracle 必须运行在 Agent 结束后，独立读取受控工作区；Agent 看不到 expected state 或 verifier 代码。任务成功定义为**所有内容、作用范围和副作用断言同时通过**，而不是自然语言声称成功。

## 5. 47 份 Skill 的下游可测试性清单

说明：

- canonical 根前缀均为 `LAB/runs/<case>/clean/<run>/SkillBank/Users/docskill/`；表中“路径”给出此前缀后的精确目录。
- “规则”采用 `rule_preservation.csv` 的规则 ID；`C/P/M/O/U` 分别表示 correct/partial/mixed/omitted/uncertain。规则清单是 analyst checklist，不是人工 gold。
- “错误”只列局部 `CONFIRMED` F 记录；47 个 Skill 共同存在的 Register 默认 CREATE、证据未逐断言对齐、部分模板领域错位在此不逐行重复。
- 优先级：`T0` 首个试点；`T1` 已有工具且适合错误/对照；`T2` 安装工具后可做；`T3` 复杂环境、参考型或弱 Oracle；`HOLD` 当前不宜单独测。
- `knowledge_reference` 只要求提供正确决策知识，不强制包含完整执行流程；可用“命令/分支选择正确率”或与操作 Skill 配对测试。

### 5.1 Case001 qsv select — `raecd75e08b34`（qsv 当前缺失）

| Skill（id8/type） | canonical 路径 | 规则 / 已确认错误 | 适合任务与 Oracle | 环境 / 优先级 |
|---|---|---|---|---|
| CSV 列选择与重排 (`f4c4df75`, session) | `csv-列选择与重排/SKILL.md` | R1a C, R1b C, R2a C, R2b P, R3a C, R3b C, R4a M, R4b C, R5a C, R5b O, R6 P, X01 O, X02 P, X03 C, X04 C, X05 P | 小 CSV 的离散/区间/末列/反转/重复列；Oracle 比较完整 CSV 字节与列序 | 需 qsv；**T2 正常对照** |
| 列排序与随机打乱 (`500c276a`, micro) | `列排序与随机打乱/SKILL.md` | R4b C, R5a C, R5b O | `--sort` 的列顺序；随机任务固定 seed 后比表头顺序 | 需 qsv；T2/T3 |
| 引用冲突列名进行 qsv select (`b0592fe3`, micro) | `引用冲突列名进行-qsv-select/SKILL.md` | R6 P, X01 O；F1-02 把“冲突时需引用”强化成“仅冲突时可引用” | 含空格/连字符列名与普通列名都引用；Oracle 比较输出列和退出码 | 需 qsv；shell quoting 跨环境，T3 |
| 正则表达式列选择 (`bd72bc3b`, micro) | `正则表达式列选择/SKILL.md` | R4a M, X01 O, X03 C；F1-01 排除分支却承诺输出匹配列；F1-04 新增精确列禁用条件 | 用 `!/SSN|account_no/` 生成脱敏 CSV；Oracle 要求敏感列缺失、其余列与行不变 | 需 qsv；**T2 错误影响候选** |

### 5.2 Case002 qsv sort — `rd9ced750fa54`（qsv 当前缺失）

| Skill（id8/type） | canonical 路径 | 规则 / 已确认错误 | 适合任务与 Oracle | 环境 / 优先级 |
|---|---|---|---|---|
| CSV 内存排序执行 (`353ba11e`, session) | `csv-内存排序执行/SKILL.md` | R1/R2/R3/R4b/R4c/R5/R6/X02 O；R4a/X03/X04/X05/X09/X12 P；X01 C | 基本 numeric/natural/reverse 排序；Oracle 独立解析 CSV 并比较稳定顺序 | 需 qsv；大量关键规则在 Clean 已缺，HOLD 作主试点 |
| 大文件外存排序切换 (`cc5a002d`, session) | `大文件外存排序切换/SKILL.md` | X01 C；F2-05 把建议强化成“小文件不得用外存” | 给定资源约束选择 sort/extsort；Oracle 判命令分支，不宜真造超大文件 | 需 qsv/extsort；T3 |
| 排序结果校验 (`7ab97840`, session) | `排序结果校验/SKILL.md` | 无映射规则；F2-06 仅由名称扩展多模式校验能力 | 要求选择合法的 sortcheck 调用；需先独立核实接口 | 当前来源证据不足，HOLD |

### 5.3 Case003 Docker cp — `rab9a070dfa59`（Docker 当前缺失）

| Skill（id8/type） | canonical 路径 | 规则 / 已确认错误 | 适合任务与 Oracle | 环境 / 优先级 |
|---|---|---|---|---|
| docker cp 符号链接复制策略选择 (`23370d93`, micro) | `docker-cp-符号链接复制策略选择/SKILL.md` | R7a C, R7b C | 本地 symlink 默认复制链接与 `-L` 复制目标；Oracle 检查目标类型/内容 | 需 Docker daemon、临时容器；T3 正常对照 |
| docker cp 路径语义判定 (`0be52a4b`, knowledge) | `docker-cp-路径语义判定/SKILL.md` | R4 O, R5 M, R6a/R6b/R7a/X03/X04/X05/X07 C, X06 M；F3-07 丢失“源为文件”条件 | 文件/目录 × 目标存在性 × 尾随 `/` 的矩阵；Oracle 检查退出码和目标树 | 需 Docker；错误分支可判但环境重，T3 |

### 5.4 Case004 git restore — `r18307cee4f4c`（Git 可用）

| Skill（id8/type） | canonical 路径 | 规则 / 已确认错误 | 适合任务与 Oracle | 环境 / 优先级 |
|---|---|---|---|---|
| git restore 命令语法与选项查阅 (`3810431b`, knowledge) | `git-restore-命令语法与选项查阅/SKILL.md` | R4a/R4b/R7a/R7b/X07 P | 从任务约束选择 pathspec-file/patch 语法；Oracle 判 argv，不要求其独立执行完整流程 | Git；T3 |
| Git Restore 默认恢复源解析 (`7b96215d`, knowledge) | `git-restore-默认恢复源解析/SKILL.md` | R1a M, R1b C, R4b P | 无显式 source 的 staged/非 staged 分支选择；Oracle 比较 index/worktree | Git；T1 |
| 从指定 tree 恢复工作区文件 (`d472e6a7`, session) | `从指定-tree-恢复工作区文件/SKILL.md` | R1a M, R1c M, R3a/R3b C；F4-09 显式 source + staged 时错误改为 HEAD；F4-10 把常见 source 名强化为必须 | 从旧 commit 同时恢复 index+worktree；Oracle 使正确 source=v1、HEAD=v2，直接区分 | Git；**T0 错误依赖主试点** |
| 从指定源恢复工作区路径 (`99f59c6f`, session) | `从指定源恢复工作区路径/SKILL.md` | R1b C, R1c M, R2a C, R6a O, R6b C, X10 P | 指定 source 只恢复工作树、默认 no-overlay 删除；Oracle 检查内容与路径集合 | Git；T1 |
| 合并基快捷语法解析 (`7147c9f5`, knowledge) | `合并基快捷语法解析/SKILL.md` | R3a/R3b C | 唯一/多 merge-base DAG 中选择合法 `A...B`；Oracle 用 `git merge-base --all` | Git；T2 正常参考 |
| 同时恢复工作区与索引 (`c0045ec2`, micro) | `同时恢复工作区与索引/SKILL.md` | R1a/R1c M, R2c C, R6a O, R6b C, X11 P | 两位置恢复，显式 source/默认 source 分层；Oracle 比较两棵状态 | Git；T1 |
| 强制启用 git restore 进度报告 (`44058e52`, micro) | `强制启用-git-restore-进度报告/SKILL.md` | X06 M | 非终端/quiet 下显式 progress 的 argv 决策；stderr 进度受规模影响 | Git；弱输出 Oracle，T3 |
| 恢复时重建冲突合并标记 (`a2921234`, micro) | `恢复时重建冲突合并标记/SKILL.md` | X01/X02 C | 构造未合并 index，`--merge` 重建 markers；Oracle 检查 index stages/文件 markers | Git；复杂 fixture，T2 |
| 恢复暂存区文件至 HEAD 版本 (`feccf35d`, micro) | `恢复暂存区文件至-head-版本/SKILL.md` | R1a M, R2b C | 仅恢复 index 到 HEAD，worktree 不变；Oracle 分别比较 blob/文件 | Git；T1 正常对照 |
| 恢复未合并路径时选择 ours/theirs 阶段 (`918e0187`, micro) | `恢复未合并路径时选择-ours-theirs-阶段/SKILL.md` | R5a M, R5b/X01 C；F4-11 把 index 未合并收窄成工作树必须有 markers | index 仍 unmerged 但工作树 markers 已手工消除时选 ours/theirs；Oracle 检查 stage2/3 内容 | Git；T2 |
| 恢复索引内容 (`ea0c6b32`, micro) | `恢复索引内容/SKILL.md` | R1a/R1c M, R2b/R2c/R6b C, R6a O | 只 index 或 index+worktree；Oracle 分别比较 | Git；T1 |
| 指定 git restore 恢复位置 (`fd6ef816`, session) | `指定-git-restore-恢复位置/SKILL.md` | R2a/R2b/R2c C, X05 M | 默认 worktree、staged-only、both 三分支；Oracle 比较 index/worktree | Git；**T0 正常规则对照** |
| 指定恢复源提交 (`68365646`, micro) | `指定恢复源提交/SKILL.md` | R1c M；F4-13 把合法 source 加上“默认源不满足才可用” | 用户明确指定等于 HEAD 或其它 commit 时仍应保留 source；Oracle 判 argv/状态 | Git；T1 |
| 静默恢复模式 (`7dca97c1`, micro) | `静默恢复模式/SKILL.md` | X05/X06 M；F4-12 quiet 后绝对无进度，漏掉显式 progress 覆盖 | `--quiet --progress` 决策；Oracle 主要判 argv，运行输出不稳定 | Git；T3 |

### 5.5 Case005 ripgrep — `r64cee24fae18`（rg 可用）

| Skill（id8/type） | canonical 路径 | 规则 / 已确认错误 | 适合任务与 Oracle | 环境 / 优先级 |
|---|---|---|---|---|
| Glob 过滤与覆盖顺序 (`acf646a2`, micro) | `glob-过滤与覆盖顺序/SKILL.md` | X16 C, X17 P | 多个 `-g` 的包含/排除覆盖；Oracle 比较文件集合和匹配行 | rg；T1 正常对照 |
| ripgrep 二进制文件搜索模式选择 (`20e03fce`, knowledge) | `ripgrep-二进制文件搜索模式选择/SKILL.md` | X10/X35-X38 C | 显式文件/递归、binary/text 模式选择；Oracle 比较退出码/stdout | rg；T2 |
| ripgrep 二进制检测行为解释 (`ce28cd7a`, knowledge) | `ripgrep-二进制检测行为解释/SKILL.md` | X39 C, X40 O | mmap/no-mmap 的行为选择题或配对任务 | rg；性能/平台干扰，T3 |
| ripgrep 基础行匹配搜索 (`d58844fa`, session) | `ripgrep-基础行匹配搜索/SKILL.md` | X01 C, X02 U, X03/X04 P；F5-23 声称仅单文件却给递归示例 | 给目录递归搜索；Oracle 比较匹配路径/行 | rg；T1 错误候选 |
| ripgrep 常用选项速查 (`262411b4`, knowledge) | `ripgrep-常用选项速查/SKILL.md` | X47-X49 C，X50-X57 O | i/S/c 的命令选择；不把遗漏选项强迫成完整流程 | rg；T2 对照 |
| ripgrep 忽略文件优先级与白名单配置 (`91670e33`, knowledge) | `ripgrep-忽略文件优先级与白名单配置/SKILL.md` | X07/X14 P, X15 C；F5-24 把一个例子泛化为必要条件 | 多层 ignore + `!` 白名单；Oracle 比较搜索文件集合 | rg；T1 错误候选 |
| ripgrep 忽略规则与过滤控制 (`5ba99044`, session) | `ripgrep-忽略规则与过滤控制/SKILL.md` | X06/X08-X11/X13 C | hidden/no-ignore/text/follow 分支；Oracle 文件集合与安全副作用 | rg；T1 正常对照 |
| ripgrep 捕获组替换引用 (`73f7abc9`, micro) | `ripgrep-捕获组替换引用/SKILL.md` | X21/X22 M, X23 P, X24 O；F5-19 把 `-o` 输出粒度误作替换范围 | 捕获组替换输出；Oracle 比较 stdout 且源文件哈希不变 | rg；T1 错误候选 |
| ripgrep 替换与配置预处理流程 (`a4245429`, macro) | `ripgrep-替换与配置预处理流程/SKILL.md` | R3 M；F5-16 声称 replace 可能改原文件 | 只预览替换、禁止改源；Oracle 比较 stdout 与源 SHA-256 | rg；T1，但复合 Skill 干扰较大 |
| ripgrep 替换匹配文本 (`81628702`, micro) | `ripgrep-替换匹配文本/SKILL.md` | R3/X21/X22 M；F5-20 禁止整行替换却又给该流程 | 整行覆盖模式替换；Oracle 比较 stdout/源哈希 | rg；T1 |
| ripgrep 替换预览与配置持久化 (`2921cff6`, session) | `ripgrep-替换预览与配置持久化/SKILL.md` | R3 M, R4 O；F5-21 把纯预览任务错误排除 | 无持久化需求的 replace preview；Oracle stdout + 源不变 | rg；T1 |
| ripgrep 自动编码处理 (`2c814928`, knowledge) | `ripgrep-自动编码处理/SKILL.md` | X29/X30 M；F5-17 把有限策略扩大为任意未知编码推断并保证匹配 | 无 BOM 非 UTF-8 fixture；Oracle 预设应漏匹配/需 `-E` | rg；T1 错误候选 |
| ripgrep 自动过滤规则说明 (`d90ef9b1`, knowledge) | `ripgrep-自动过滤规则说明/SKILL.md` | X06/X35 C, X07 P | 默认过滤解释后选择最小 override；Oracle 文件集合 | rg；T2 |
| ripgrep 自定义文件类型临时定义 (`db337ffa`, micro) | `ripgrep-自定义文件类型临时定义/SKILL.md` | R2/X19 C | 单命令 `--type-add` + `-t`；下一命令不应持久 | rg；T1 正常对照 |
| ripgrep 递归搜索与自动过滤 (`dc2d24fe`, session) | `ripgrep-递归搜索与自动过滤/SKILL.md` | X05/X06 C | 目录递归与默认过滤；Oracle 文件集合 | rg；T1 正常对照 |
| ripgrep 配置文件默认选项设置 (`556e78e5`, knowledge) | `ripgrep-配置文件默认选项设置/SKILL.md` | R4 O, R5 C, X25/X26 P, X27 O；F5-18 缺 `RIPGREP_CONFIG_PATH` 却声称保存后生效 | 临时配置文件是否被启用；Oracle 比较有/无 env 的 stdout | rg；T1 错误候选 |
| ripgrep 默认编码行为与漏匹配风险判断 (`17838585`, knowledge) | `ripgrep-默认编码行为与漏匹配风险判断/SKILL.md` | X29/X30 M, X31 C, X32 P | 为 UTF-16/非 UTF-8 fixture 选择 auto/显式编码 | rg；T1 对照 |
| 二进制搜索安全警告 (`333103a1`, safety) | `二进制搜索安全警告/SKILL.md` | X10 C | 遇二进制时是否避免把控制字符直接输出终端 | rg；安全决策可判，T2 |
| 启用隐藏文件与二进制搜索 (`088793ac`, micro) | `启用隐藏文件与二进制搜索/SKILL.md` | X09/X10 C；F5-25 错误保证一定命中 | 合法零匹配 fixture；Oracle 接受 rg exit 1 且空输出 | rg；T1 错误候选 |
| 手动过滤：glob 与文件类型 (`53070b07`, session) | `手动过滤-glob-与文件类型/SKILL.md` | X16/X18 C, X20 P | `-g/-t/-T` 文件集合 | rg；T1 |
| 指定编码搜索非 UTF-8 文件 (`1efdc8b0`, micro) | `指定编码搜索非-utf-8-文件/SKILL.md` | X30/X33 M, X31 C, X34 P；F5-22 `none` 分支错误继承 BOM 例外 | BOM 与 `-E none` 的原始字节分支 | rg；fixture 精细，T2 |
| 按文件类型过滤搜索 (`67355610`, session) | `按文件类型过滤搜索/SKILL.md` | R2/X18/X19 C | 自定义 type 后筛选；Oracle 文件集合 | rg；T1 正常对照 |
| 递归搜索与路径限定 (`bc7ca9e9`, session) | `递归搜索与路径限定/SKILL.md` | R1/X05/X06 C, X02 U；F5-26 无来源支持地拒绝多个不相关根 | 同时给两个根目录；Oracle 合并两根匹配 | rg；T1 错误候选 |
| 预处理器配置与使用流程 (`2776509a`, session) | `预处理器配置与使用流程/SKILL.md` | X41 C, X42/X44-X46 O, X43 P | 极简透传 preprocessor；Oracle stdout 和调用日志 | rg + 脚本 fixture；缺核心接口，HOLD |

## 6. 五案例比较与首个案例选择

| 案例 | 错误能否形成可观察差异 | 当前 CLI | Oracle 难度 | 主要混杂 | 结论 |
|---|---|---|---|---|---|
| C1 qsv select | 可以，但 F1-01 同一 Skill 同时给出正确命令和错误输出契约，未必改变动作 | 缺失 | 低 | 需安装 qsv；错误可能只影响解释不影响命令 | 第二候选 |
| C2 qsv sort | 多数核心规则 Clean 已遗漏，难把一次失败归到单一已知错误 | 缺失 | 中 | 前端缺失、参数组合多 | 不作首试点 |
| C3 Docker cp | F3-07 可测试 | 缺失 | 中高 | daemon、容器、Windows 路径/权限 | 不作首试点 |
| **C4 git restore** | **F4-09 会把目标从指定 commit 错换为 HEAD，最终字节可直接区分** | **可用** | **低** | 必须一次性仓库，避免真实项目 | **首选** |
| C5 ripgrep | 多个已知错误可测，源哈希 Oracle 很强 | 可用 | 低到中 | 24 个 Skill 检索竞争、正确/错误知识并存 | 后续并行候选 |

Case004 的关键来源在 `LAB/data/raw_sources/git/.../git-restore.txt:25-26,35-46,58-64`：只有**未指定** `--source` 时，`--staged` 才默认 HEAD；显式 `--source` 用于另一个 commit。原 Skill `.../从指定-tree-恢复工作区文件/SKILL.md:23-33,57-65` 却在显式 source 技能中写“若同时给出 --staged，则从 HEAD 恢复”，同时又在 `:28,59,75` 承诺来自指定 tree，构成可定位的内部矛盾。

## 7. 最小 Agent 下游对照实验

### 7.1 实验问题与单位

主问题：在同一模型、任务、工具、预算和 fixture 下，原版错误 Skill 是否使 Agent 丢掉显式 `--source`，从而把目标文件恢复为 HEAD 而非指定 commit？

实验单位是一场全新会话 + 一个全新一次性 Git 仓库。不同 trial 不共享消息、Skill usage、索引、工作区或模型缓存（若后端缓存不可关闭，必须记录）。

### 7.2 两个预注册任务

#### D_err：依赖目标错误

fixture：

1. commit `C1`：`target.txt = "v1\n"`；轻量 tag `wanted` 指向 C1。
2. commit `C2`（HEAD）：`target.txt = "v2\n"`。
3. index：`target.txt = "v3\n"`。
4. worktree：`target.txt = "v4\n"`。
5. `sentinel.txt` 保持不变；记录 HEAD、refs、index blob、两文件哈希。

给 Agent 的任务：

> 在当前一次性 Git 仓库中，把 `target.txt` 的暂存区和工作区都恢复为 tag `wanted` 指向的版本。不得改变 HEAD、提交历史、refs 或 `sentinel.txt`。完成后验证结果。

期望关键动作：

```text
git restore --source=wanted --staged --worktree -- target.txt
```

确定性期望状态：

| 断言 | 期望 |
|---|---|
| HEAD | 仍为 C2 |
| `git show :target.txt` | `v1\n` |
| 工作区 `target.txt` | `v1\n` |
| `git diff -- target.txt` | 空（worktree 与 index 相同） |
| `git diff --cached -- target.txt` | 显示相对 HEAD 的 v2→v1 变化 |
| `sentinel.txt`、refs、commit count | 不变 |

若 Agent 按错误规则省略 source，`--staged --worktree` 默认从 HEAD 恢复，index/worktree 会变为 `v2\n`；Oracle 可不依赖自然语言直接判错。

#### D_control：不依赖目标错误的正常规则

同一初始 fixture。给 Agent 的任务：

> 只把 `target.txt` 的暂存区恢复到 HEAD，工作区内容必须保持 `v4`，不得改变 HEAD、历史、refs 或其它文件。

期望动作是 `git restore --staged -- target.txt`；期望 index=`v2\n`、worktree=`v4\n`。该任务主要依赖正确的“指定恢复位置” Skill，目标 source 错误不应被触发。

### 7.3 条件 A/B/C

| 条件 | Agent 可见材料 | Skill 处理 |
|---|---|---|
| A 原版 Skill | system 基线、任务、白名单工具说明、A bundle | 从 frozen run 字节复制：错误目标 Skill + 正常控制 Skill，不改内容 |
| B 无 Skill | 与 A 相同，但不含任何 Skill context | 不加载 Skill；其它 system 文本保持字节级一致，避免另写“你没有技能” |
| C 局部修正 Skill | 与 A 相同，C bundle | 只修 F4-09：明确“显式 `--source` 始终决定来源；仅在未指定 source 时，staged 默认 HEAD，否则默认 index”。F4-10 等其它内容保持不变 |

C 必须放在派生目录，保存原 SHA、patch、修后 SHA；不得覆盖 run。它只是诊断对照，不称为新算法。

### 7.4 信息与权限控制

- Agent **不得**看到原始 git 文档、rules、既有审计、错误标签、condition 名、expected state 或 verifier 实现。
- 禁止网络；禁止访问真实仓库和 D 盘其它路径。
- 只允许当前 trial repo 内的受控文件读取/哈希，以及白名单 Git 子命令：`status`、`rev-parse`、`show`、`diff`、`restore`。fixture 构建器在 Agent 运行前可用 `init/config/add/commit/tag`，这些不暴露给 Agent。
- 禁止 `reset --hard`、`clean`、`checkout`、`commit`、`branch -f`、删除和任意 shell。工具层使用 argv 数组，不接受 shell 字符串。
- 每场限制相同：同一 model/version、temperature=0、同一 seed（若支持）、同一 token 上限、最多 8 次工具调用、60 秒墙钟时间、相同 context budget。

### 7.5 如何证明 Skill 被加载和使用

分三层记录，不混为一个布尔值：

1. **加载/暴露**（确定性）：记录 Skill ID、源路径、SHA-256、解析出的 name、Prompt SHA、最终 system prompt SHA；断言 A/C 的目标 ID 存在，B 不存在。
2. **检索/选择**（机制）：P0 先运行官方 loader/search/render 的静态集成测试，记录 hits、score、selected IDs、注入字符数。主因果试验为避免检索失败掩盖内容效应，按预注册任务把目标 Skill 与控制 Skill 固定为候选并要求相应 ID 入 context；自然检索作为后续外部有效性测试。
3. **行为采纳**（动作证据）：从工具 trace 机械提取 `has_source_arg`、`source_value`、`has_staged`、`has_worktree`、`pathspec`。D_err 中省略/错误 source 且最终变成 v2，是采用目标错误分支的机制证据。不得用 AutoSkill 的 LLM usage judge 或 Agent 自报代替。

### 7.6 重复、随机性与因果解释

- harness smoke 可每 cell 1 次，但只能判接线，不得下因果结论。
- 正式最小 pilot：2 个任务 × 3 条件 × 5 个全新会话 = 30 trials；condition 顺序用预生成固定随机表，日志保存顺序和 seed。
- 若后端在 temperature=0 仍非确定，报告 exact outcome 分布；不挑最好一次。
- 首要对比是 D_err 的 C−A；B 判断模型本身是否能做。D_control 要求 A/C 稳定，用于检查局部修正是否产生旁效应。

解释矩阵：

| D_err 结果 | 可支持的解释 |
|---|---|
| B、C 成功而 A 以“缺/错 source→v2”失败 | 对“原版 Skill 错误诱发失败”最强的最小机制证据 |
| B 失败、C 成功、A 失败 | 修正 Skill 提供必要帮助；仍需检查 A 的失败模式是否命中目标错误 |
| A、B、C 都失败 | Agent、工具或任务本身不足，不能归因于 Skill |
| A、B、C 都成功 | 已知文本错误在该任务/模型下未产生可测影响 |
| A 失败但不是 source 机制，C 成功 | 仅是相关性，必须审查 trace；不能自动归因 |

5 次重复只提供探索性机制证据，不提供普遍因果估计或统计显著性声明。

## 8. 下游评价指标与判分来源

| 类别 | 指标 | 机器来源 | 通过条件 |
|---|---|---|---|
| Skill 加载 | `skill_load_success` | loader 事件 + ID/name/SHA | 预期 ID、名称、哈希全部匹配 |
| Skill 暴露 | `context_injection_success` | system prompt 构建日志 | A/C 含目标 Prompt hash；B 不含 |
| Skill 选择 | `target_selected` | retrieval/selection trace | 目标任务选择目标 ID；控制任务选择控制 ID |
| 规则行为 | `source_arg_retained` | 结构化 tool call argv | D_err 含 `--source=wanted` 或等价 argv |
| 工具正确性 | `tool_call_valid` | allowlist validator、exit code、stderr | argv 合法、路径在 sandbox、命令成功 |
| 任务成功 | `task_success` | 独立 Git Oracle | 该 task 的全部内容/位置/副作用断言通过 |
| 非法操作 | `policy_violation` | tool gateway 拒绝日志 | 0 次越界/禁用命令；发生即 trial fail |
| 错误采用 | `target_error_adopted` | argv + final state | D_err 缺/错 source 且产生 HEAD(v2) 状态 |
| 修复改善 | `repair_delta` | 同 task 的 A/C 成功率与失败模式 | C>A 且差异由目标 action feature 解释 |
| 旁效应 | `control_stability` | D_control A/C | A/C 均保持高且失败模式不新增 |
| 可靠性 | exact repeat consistency | 5 个 trial 的 verdict/action tuple | 报完整分布，不只报均值 |
| 成本 | input/output tokens、model calls、tool calls、wall time | 模型响应 metadata、runner clock、trace | 每 trial 原样记录；缺失写 `UNKNOWN` |

`task_success` 是主终点。文本回复、LLM judge、退出码单独都不能覆盖最终状态 Oracle。

## 9. 最小实现方案

### 9.1 建议目录（全部独立于 `runs/`）

```text
degradation_failure_lab/downstream_pilot/
├── README.md
├── configs/
│   ├── executor.json              # model/version/temperature/budget
│   └── conditions.json            # A/B/C，不含隐藏答案
├── skills/
│   ├── original/Users/docskill/...
│   └── repaired/Users/docskill/...
├── tasks/
│   └── case004_git_restore/
│       ├── error_source_and_both.json
│       └── control_staged_only.json
├── fixtures/
│   └── git_restore.py             # 仅建一次性 repo
├── executor/
│   ├── run_trial.py               # 模型/tool loop
│   ├── skill_context.py           # 复用官方 parser/render
│   └── git_tool.py                # argv 白名单 + 根目录约束
├── oracles/
│   └── git_restore_oracle.py
├── schemas/
│   ├── trial.schema.json
│   └── verdict.schema.json
└── results/                       # 每 trial 独立目录；不提交敏感响应
```

具体命名可按现有 LAB 风格微调，但职责和写入边界不应合并进官方源码。

### 9.2 复用与新增边界

可直接复用：

- `load_agent_skill_dir` 的格式解析；
- `render_skills_context` 的文本渲染；
- 后续自然检索阶段可复用 `LocalSkillStore.search`、`retrieve_hits_by_scope`、`LLMSkillSelector`；
- LAB 现有 `inside/sha256/write` 一类安全 I/O 和 run identity 模式可参考，但不改历史 run。

必须新增在独立实验目录：

- tool-capable executor loop；
- 严格 argv/路径 allowlist；
- task/condition/trial manifest；
- disposable Git fixture；
- 独立 final-state Oracle；
- original/repaired Skill 派生和哈希审计；
- trial 聚合器。

不应复用为 Oracle：`inspect_run`、人工 evaluation、LLM usage judge。

### 9.3 分阶段输入、动作、输出和验收

#### P0：执行环境和 Skill 加载验证

- 输入：两个原版 canonical Skill 路径、局部 patch、Git 可执行路径。
- 动作：复制到派生 SkillBank；校验哈希；用官方 parser/render；验证 `user_id=docskill`；构造/销毁一次性 repo；运行 Oracle 自身正反 fixture。
- 输出：`environment.json`、`skill_manifest.json`、`oracle_selftest.json`。
- 验收：原版字节未改；C 只有目标句 diff；loader/render 全通过；Oracle 对正确状态 PASS、对 v2/只改一处/改 sentinel 均 FAIL。

#### P1：单任务端到端执行链

- 输入：D_control、scripted deterministic executor（不是模型）。
- 动作：通过同一 tool gateway 执行预定合法 action。
- 输出：完整 tool trace 与 verdict。
- 验收：证明 runner、沙箱、trace、Oracle 接线正确；不把 scripted PASS 写成 Agent 成绩。

#### P2：无 Skill vs 原版 Skill

- 输入：冻结 executor 模型、D_err/D_control、A/B。
- 动作：先各 1 次 smoke，再在预算获批后按 5 次重复。
- 输出：trial records、A/B 分布。
- 验收：所有条件除 Skill context 外相同；B 能力可见；失败有可定位状态。

#### P3：局部修正诊断

- 输入：C bundle 和同一任务/预算。
- 动作：完成 A/B/C 预注册顺序；比较目标 action feature 与 Oracle。
- 输出：机制对照表；不覆盖原版。
- 验收：只有在 C−A 改善且失败机制命中 `--source` 时，才写“错误与失败存在机制证据”。

#### P4：链路可靠后准备退化实验

- 输入：通过 P0-P3 的 runner/oracle、固定 task family。
- 动作：再决定 Case001 qsv 安装、Case005 扩展和退化文档条件；不在本报告实施 M1/M2/M3。
- 验收：先冻结任务与 Oracle，再生成或比较退化 Skill；不得用 test feedback 修同一 locked task。

### 9.4 环境结论

- 首选 Case004 不需安装新 CLI；使用现有 Git 即可。
- qsv 仅在进入 Case001 时按固定版本安装并记录哈希/版本；本轮不安装。
- Docker 需要 CLI + daemon + 可用镜像，成本最高，不是首轮阻塞项。
- 真正 Agent trial 还需要一个获准的模型后端。当前官方 interactive 支持多种 provider，但没有冻结的 executor 配置；若只有付费 API，必须另行获得预算与调用授权。本轮不调用。

## 10. 实验有效性风险

1. **处理未送达**：自然检索没选中目标 Skill。主试验固定候选/注入，另把自然检索作为后续问题。
2. **同域 Skill 冲突**：特别是 ripgrep 24 Skill；因此首轮选择只有两个目标 Skill 的 Git bundle。
3. **模型先验过强**：B 可能全成功。此时仍能判断 A 是否有害；不能用“Skill 没提升”证明 Skill 无质量问题。
4. **错误不触发**：Agent 可能服从正确示例而忽略错误句。结果应报告“本任务未观察到影响”，不能写“错误无害”。
5. **修正泄漏**：C 只能改 F4-09，不得润色其它句子、增加示例或预算。
6. **Windows/Git 差异**：强制 `core.autocrlf=false`，以 blob 字节和明确 LF fixture 判分；记录 Git 版本。
7. **污染真实仓库**：所有动作在系统临时目录下新建的 repo；Oracle 验证绝对路径位于 trial root。
8. **单次偶然**：smoke 只判接线；正式最小 pilot 至少 5 次/cell，并报告所有 trial。
9. **LLM 自评偏差**：usage judge 只作辅助日志；主结论来自 tool argv 和最终 Git 状态。
10. **小样本外推**：一个 Skill、一个模型、一个 Windows 环境只支持局部机制发现，不代表 47 Skill 总体成功率。

## 11. GO / CONDITIONAL GO / NO-GO

| 范围 | 决策 | 理由 |
|---|---|---|
| 现在直接让现有仓库跑真实下游 Agent 实验 | **NO-GO** | 无工具执行 Agent、任务 fixture、Oracle、条件控制和冻结 executor 配置 |
| 新增独立最小 harness 后做 Case004 小试点 | **CONDITIONAL GO** | Git 已可用；错误产生可判别状态；先通过 P0/P1 门槛并获得模型授权 |
| 现在全量测试 47 Skill | **NO-GO** | 工具环境不齐、职责不同、任务/Oracle 尚未建立，且会混淆检索与内容效应 |
| 现在进入退化文档或 M1/M2/M3 | **NO-GO** | 尚无可信下游测量链 |

## 12. 五个问题的明确回答

**Q1：当前仓库能否直接让 Agent 使用已有 SKILL.md 完成下游任务？**  
不能。它能解析、检索并把 Skill Prompt 注入文本聊天，但没有工具调用 Agent 和真实任务 Oracle；LAB 也没有把五个 run 接到该聊天链。

**Q2：最少还需要什么？**  
一个独立的 tool-call executor 入口、run Skill 的只读复制/哈希与 `docskill` 身份接线、受限 Git 工具网关、一次性 fixture、确定性 final-state Oracle、A/B/C trial controller、冻结的模型/预算配置。首选 Git 案例无需安装新 CLI；模型后端仍需明确授权。

**Q3：哪个案例最适合作为第一个下游任务实验？为什么？**  
Case004 git restore。Git 已安装；F4-09 将显式 source 错误覆盖为 HEAD，可用 v1/v2 的 index/worktree 字节差异直接判定；同 run 的“指定恢复位置”是正常对照；全部操作可封闭在一次性仓库。Case001 仍是 qsv 安装后的第二候选。

**Q4：如何证明失败与 SKILL.md 错误有关？**  
在相同模型、任务、工具、预算下比较 B（无 Skill）、A（原版）和 C（只修 F4-09）。只有当 B/C 成功、A 按 trace 丢失或错用 `--source` 并得到 HEAD 的 v2 状态，同时 D_control 的 A/C 稳定，才形成较强机制证据。全失败、非目标机制失败或单次差异都不足以归因。

**Q5：下一轮 Codex 的唯一优先任务是什么？**  
只在 `degradation_failure_lab/downstream_pilot/` 建立并离线自测 Case004 的白名单 Git executor harness、一次性 fixture 和 Oracle，产出 P0/P1 证据；不调用付费模型、不改官方源码、不运行 A/B/C 模型试验，直到这条测量链对正确/错误状态都能稳定判分。

完成本报告后停止；未进入真实 Agent 执行或方法改进。
