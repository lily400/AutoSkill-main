# SkillGenBench 运行时、接线与输出契约审计

审计日期：2026-10-15（Asia/Shanghai）。官方仓库：<https://github.com/QuantaAlpha/SkillGenBench>。审计提交：`5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。下列行号均为该提交的本地文件实际行号；网络缓存的 main 行号与本提交不同，不能混用。

审计方式：静态代码阅读、隔离 Python `--help`、pipeline `--dry-run`、从 AST 提取指定纯逻辑函数并以人工夹具运行。没有调用模型、没有启动 Docker、没有执行 Agent、没有安装依赖、没有改动官方源代码。`git status --short` 为空。离线测试源码和结果分别为 `runtime_contract_checks.py`、`runtime_contract_checks.json`。

## 裁决摘要

**可作为经过修复和协议加固的评测底座；当前公开代码不足以支持“下载后立即完整复现实验”“天然多技能库”“任务无关产物直接评测”“仅靠技能的信息隔离”“已证明技能实际加载成功”等强说法。** 原始程序的功能契约是：从一个任务映射到一个 Skill package，装入 Claude Code CLI，让有文件和 shell 工具的 Agent 生成解答，再执行测试。

正面证据：完整 package 复制确实包含 `references/`、`scripts/`；任务执行与验证已有接口；`noskill_claude` 可以使用同一 Claude Code harness；有 staging 元信息、stream-json、工具计数和逐试验记录。负面证据：多个独立 package 不被 resolver 接受；agnostic 输出目录断线；已有若干路径错误；原文 docs、tests、可选 groundtruth 与 agent 同容器可读；技能缺失时不 fail closed；触发判定不检查工具结果；主汇总的 `pass_rate` 是 any-success。

## 1. 输入、任务选择与生成契约

| 项目 | 代码证据 | 审计解释 |
|---|---|---|
| task-conditioned 输入 | `baseline/naive_prompt/generate_skill.py:119–144,232–263` | 枚举 `data_source/*/*/tasks/*/task.json`，读任务 `instruction.md`、任务 docs、collection shared docs/tools；模型可见 task ID、collection、明确任务。不可称为任务无关生成。 |
| task-agnostic 输入 | 同文件 `153–178,283–304` | 从 task.json 发现 collection，但模型 prompt 只给 shared docs/tools 和库元信息，没有任务 instruction。目录枚举依赖任务元数据，不等于把任务全文交给模型；隔离时仍宜先做独立 source manifest。 |
| 文档损失 | 同文件 `42–46,51–73,496–498` | 仅接收白名单文本后缀，UTF-8 解码失败跳过；按路径排序拼接并直接按字符截断，默认任务 docs 12,000、shared docs 8,000、tools 6,000 字符；不按 token、不保结构、不自动 OCR/读 PDF。应区分“退化输入效果”和 baseline 自带截断效果。 |
| 单次生成 | 同文件 `323–360,389–418` | 单 completion 生成 `SKILL.md`（失败可重试）；默认 temperature 0.2、max_tokens 4096，GPT-5/o1/o3 分支改 16384 completion tokens、low reasoning，温度报错重试 1。调用预算并非统一常量。 |
| 生成产物 | 同文件 `395–418,454–475` | 写根 `SKILL.md` 和 `meta.json`，不把输入 shared tools/docs 复制成输出 assets。生成器看见 helper script 并不意味着 runtime 能在 package 内找到它。 |
| 元数据变换 | `baseline/_shared/skill_md_helpers.py:32–97` | sanitizer 只保 name/description，删除其它顶层 YAML 字段，并合并多行值；这会丢失触发条件、依赖/运行时、输入等非 name/description 元数据。该行为属于 naive/shared helper，不是 resolver 强制对所有外部 package 执行。 |

关键来源：[naive generator](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/baseline/naive_prompt/generate_skill.py#L232-L304)，[文本读取](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/baseline/naive_prompt/generate_skill.py#L42-L73)，[frontmatter 改写](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/baseline/_shared/skill_md_helpers.py#L32-L97)。

## 2. 任务无关分支存在公开代码接线缺口

1. naive `--scope agnostic` 写到 `<method>/<model>/<run>/<source>/<collection>/agnostic/`（`generate_skill.py:529–537`）。
2. evaluator 的 `skill_base_dir` 只选择 `shared` 或 `tasks/<task_id>`，不处理 `agnostic`（`scripts/generated_skills_layout.py:208–212`）。
3. `scripts/run_eval.py:683–702` 没有 `--scope`；`scripts/pipeline.py:392–412` 不传 scope，也没有 agnostic 到 task/shared 的映射。
4. pipeline 的 agnostic 生成分支强制 `--all`，没有传用户 `--repo`/`--task-id` 选择器（`pipeline.py:293–307`）。选一个库做 pilot 会在该 source 的所有 collection 上生成，若实际执行会产生未预期费用。

安全实证：运行

```text
python -I -B scripts/pipeline.py --repo scikitimage --source code_doc --skill-method naive_prompt --scope agnostic --dry-run --model-name audit-model --run-id audit-run
```

仅打印命令、不运行生成和评测。输出 generation 命令含 `--all --scope agnostic`，evaluation 命令含 `--repo scikitimage` 且无 scope。人工 fixture 中已存在 `.../agnostic/SKILL.md`，实际 resolver 返回 `.../tasks/fixture-task`，`has_skill_package=False`。

因此修补应显式定义 `source_id → library_id → task_ids` 的共享 artifact 映射，并在评价时冻结 artifact 内容哈希；仅修改 README 或传 `--scope agnostic` 不足以修复。以每任务复制同一技能的方式临时兼容须保留同一 source hash/skill hash，防止误计为独立生成。

关键来源：[agnostic 写出](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/baseline/naive_prompt/generate_skill.py#L505-L542)，[resolver](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/generated_skills_layout.py#L184-L241)，[pipeline 分支](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/pipeline.py#L293-L307)。

## 3. 单 package、资产复制与 adapter 边界

- resolver 首先接受 leaf 根的 `SKILL.md`。若没有，兼容一个直接子目录里的 `SKILL.md`；两个这样的子目录会抛 `ValueError("Ambiguous generated skill packages ...")`，而不是自动组成技能库（`generated_skills_layout.py:134–177`）。离线测试已证实。根 `SKILL.md` 存在时优先选根 package；把多个子技能装进一个根包，不等于验证它们以独立技能被发现/调用。
- 成功解析后 `prepare_skill_for_claude` 拷贝整个 package，唯一忽略项是 `.DS_Store`、`__pycache__`（`claude_runner.py:136–186`；`generated_skills_layout.py:104–113`）。离线 fixture 的 `references/guide.md`、`scripts/helper.py` 均完整复制。**不能说基准只接收 SKILL.md 文本、一定丢 references。**
- staging root 挂到 `/root/.claude/skills:ro`；选中 package 同时挂 `/workspace/skill:ro`，prompt 指示按此路径读附属文件（`claude_runner.py:222–230,381–385`）。没有在这一段执行 package 依赖安装；资产存在与依赖可执行是两个条件。
- resolver 验证的是文件存在，未见 YAML schema、非空内容、引用完整性、脚本依赖、路径可移植性、token budget 的预校验（`generated_skills_layout.py:134–181`）。这些需 adapter/preflight 补充。
- `skill_base_dir` 在显式 run ID 目录不存在时仍尝试 legacy/旧目录（`generated_skills_layout.py:217–238`）。离线已证实 `run_id="missing-explicit-run"` 仍解析到 legacy skill。必须记录 resolved path+hash 并要求显式 run fail closed，否则易把旧技能误算进新实验。

Anything2Skill/AutoSkill adapter 的最低要求：保留原始 package 与 UUID/provenance；导出确定的 name/description/SKILL.md；保留被引用的 references/scripts；校验相对路径；冻结依赖；显式 task/source 映射。多技能结果须采用修改后的多包 loader/routing 或有说明的单包投影，不能将拼接、挑一个技能、扁平化 reference 当作“无损原生接入”。

关键来源：[package 解析](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/generated_skills_layout.py#L134-L181)，[整包 staging](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/claude_runner.py#L136-L186)。

## 4. Agent、模型与 baseline 是否真正固定

| 方法名/配置 | 公开实际行为 | 公平比较意义 |
|---|---|---|
| `noskill` | direct LLM 单次生成 Python；截断 docs digest 默认 8,000 字符，temperature 0.2/max 4096（`noskill_runner.py:36–38,54–76,101–112,128–168`） | 不可直接当作“相同 Agent 去掉技能”的唯一对照；工具、轮次、上下文和生成形式都变了。 |
| `noskill_claude` | 同 Claude Code runner，不预装技能，也不注入“先生成技能”（`skill_method_profiles.py:23–28`） | 应作为相同 executor 的主要 no-skill 对照。仍需保持 docs 可见性、预算、模型一致。 |
| `skillsbench_generate` | 无预装技能，指令要求 runtime 先写技能再做任务（`claude_runner.py:49–65,235–245,247–293`） | 属于 task-conditioned/self-generation，不能和预先冻结任务无关库混称同一设置。 |
| 未登记新方法 | profile 默认 `claude_agent_with_skill`（`skill_method_profiles.py:16–17,31–50`） | 可使用自定义方法名直接 `run_eval`，但 pipeline 先检查 `baseline/<method>/generate_skill.py` 存在，即便 skip generate（`pipeline.py:245–251`）。 |
| `--model-name` | eval 参数文案即 skill lookup/results directory；只设置路径查找变量（`run_eval.py:700–712,766–771`） | **不是强制 executor 模型开关**。实际 inference model 来自 `ANTHROPIC_MODEL`、`CCR_MODEL`、`MODEL_NAME` 环境/文件配置（`runtime_config.py:143–176,269–313,317–340`）。 |

Agent 可用工具是 `Bash,Edit,Write,Read,Glob,Grep`，有 staged skill 时再加 `Skill`（`claude_runner.py:47–48,422–468`）。默认外层超时 600 秒（`409–415,721–724`），命令未固定 max turns、temperature、总 token 或费用预算。CCR 分支使用代理转换 Anthropic→OpenAI；CLI 字面模型名 `claude-sonnet-4-5-20250514` 并不代表实际后端模型，后者由 BACKEND_MODEL 指定（`claude_runner.py:432–446`；`baseline/_shared/anthropic_proxy.py:155–188`）。代理会给 GPT-5/o1/o3 设置 low reasoning 和 completion 上限；不是所有模型相同原始协议。

Docker light 固定 Claude Code `2.1.85`，heavy 未固定 CLI 版本，二者 router、许多 Python 包、基础 image digest 都未完整冻结（`docker/Dockerfile.claude:3,32,44,54,67,127–135`；`Dockerfile.claude-heavy:3,28,54–55,89,160–167`）。浏览器/SpaCy 模型下载失败可以继续镜像构建（light `92–112`；heavy `125–145`）。这是“部分 pin”，不是完整环境重现承诺。应冻结 image digest、lockfile、CLI/router、实际 backend model ID 和预算清单。

公开 baseline 目录仅 `_shared/` 与 `naive_prompt/generate_skill.py`；批处理脚本枚举的 SkillNet-main、skill-creator-v2、evoskill、skillseekers 并无对应 generator 源码（`scripts/run_all_eval.sh:30`、本提交文件树）。不能把脚本中出现名称当作完整方法已发布/已经可运行。

关键来源：[runtime profiles](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/skill_method_profiles.py#L21-L50)，[执行命令](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/claude_runner.py#L409-L486)，[light Docker](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/docker/Dockerfile.claude#L127-L135)，[heavy Docker](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/docker/Dockerfile.claude-heavy#L160-L167)。

## 5. 原文与评价资产可见性：不能把挂载当作隔离

`claude_runner.py:337–355` 在 Agent 所在容器挂载：

```text
trial_dir                -> /workspace                   read/write
context_input_dir        -> /workspace/input             read-only
context_docs_dir         -> /workspace/docs              read-only
tests_dir                -> /workspace/tests             read-only
existing groundtruth_dir -> /workspace/groundtruth       read-only
```

若 `needs_reference_repo` 还挂整个参考仓库（`389–395`）。prompt 明示 Documentation at `/workspace/docs`（`190–203`）。只读限制写入，**不限制 Agent 读取**。Agent 有 Bash/Read/Glob/Grep；启动代码也没有划分 evaluator 用户权限或单独 verifier 容器。因此代码事实是：评价 docs/tests/存在的 groundtruth 可被 agent 读取；是否已读、是否偷看答案、每个任务 docs 是否等同原始完整 corpus，需要轨迹与数据内容核对，不能从挂载推断实际作弊已经发生。

对退化文档研究的直接威胁：如果只退化 `data_source` 中 generator 输入，但 evaluator 仍可读清洁 `context/docs`/reference repo，executor 可以绕过退化技能。需要明确实验条件：skill-only 时在 agent 执行阶段不挂源 corpus；raw-doc baseline 才给同一版本的文档；隐藏 tests/groundtruth 只在 agent 结束后加入 verifier。当前 Docker command 未限制网络（`332–399`），若需要防外部补全，还需相同网络规则/允许清单。

关键来源：[所有运行挂载](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/claude_runner.py#L332-L399)，[prompt 明示文档](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/claude_runner.py#L190-L230)。

## 6. 技能使用证据和统计量

**装载路径证据存在，实际成功使用证据不足。** `skill_staging_meta.json` 记录请求 run/model、expected/resolved package、staging path、package name/layout（`claude_runner.py:792–814`）。但 `parse_claude_log` 只要看到 `tool_use.name == "Skill"` 就置 true，不核对 skill name、成功响应、工具错误、是否读取 references、是否真正遵循（`592–633`）。离线输入一个调用不存在技能且明确 `is_error: true` 的 tool result，输出仍为 `skill_triggered=True`。故该变量应命名为 invocation observed；成功加载需配对 tool use/result、artifact hash 与返回内容。

缺失技能也不 fail closed：resolver 无产物则 staging 返回 None（`136–158`）；run_eval 只记录 `skill_available` 不拒绝（`741–746`）；执行 prompt 失去强制 Skill 指令；最终 `skill_required = skill_staged`（`claude_runner.py:962–969`）。一个原本标成 skill method 的试验可能实际上以无技能完成并通过。应把 generation failure / package missing / loading failure 与 task failure 分开计数。

`scripts/run_eval.py:522–534` 默认遇一通过即停；summary `pass_rate` 直接计算 `any(trial.pass)`，是 best-of-k / success-within-k 的 0/1，而非逐试验均值。即使 `--no-early-stop` 跑满全部，也不改变该定义。离线人为结果 False/True/False，3 次全部执行，reported pass_rate=1.0，真实 trial mean=1/3。后续源汇总平均该字段（`run_eval.py:639–661`）。主要指标须自定义为 task-level pass@1 或明确定义的 success@k，并给完整试验数、成本和失败原因；不要把原始 `pass_rate` 与别处的 pass@1 混用。

token 计数可回退字符估算且标 `token_source="estimated"`（`claude_runner.py:592–597,651–659`）；不要无区别用于精确成本结论。最终 pass 由 verifier passed 和 Skill invocation gate 合成；非零 agent rc 只追加 error，未直接在布尔通过式中排除（`960–971`）。执行失败与产物通过可能并存，需按预注册原则分类。

关键来源：[触发判定](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/claude_runner.py#L592-L661)，[最终通过式](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/claude_runner.py#L952-L971)，[pass_rate 定义](https://github.com/QuantaAlpha/SkillGenBench/blob/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/scripts/run_eval.py#L520-L539)。

## 7. 最小复现/接线阻断

1. `baseline/naive_prompt/generate_skill.py:28` 将 `REPO_ROOT/eval` 加到 sys.path，真实模块在 `scripts/`。在干净隔离 Python `python -I -B baseline/naive_prompt/generate_skill.py --help` 下直接 `ModuleNotFoundError: No module named 'generated_skills_layout'`（发生在第 30 行）。这不是缺 API key，也没进入模型调用。设置 PYTHONPATH 可绕过，但应作为明确环境修补披露。
2. `scripts/_common.sh:5–6` 把自身所在的 `scripts` 当 repo root 并 `cd`，随后 `PIPELINE="python3 scripts/pipeline.py"`（第 19 行）会指向 `scripts/scripts/pipeline.py`。这为批处理默认路径的静态确定性问题；本轮不执行 shell 批处理以避免其它 side effects。
3. task-agnostic 路径 mismatch、多包拒绝、显式 run legacy fallback 已有离线反例。
4. 缺失 paper baselines 是公开 release 覆盖范围问题，不是宣称论文实验没有做过；本轮仅能裁决公开代码复现可行性。

## 8. 最小可审计接入方案

先做无模型 preflight：修 importer/脚本 cwd；锁 task IDs、source/condition/artifact manifest；检查每任务引用确实指向 intended package；拒绝 fallback/missing/empty/invalid YAML/断引用；对多 package 明确 loader；把 tests/groundtruth 移到 verifier 阶段；固定 skill-only 与 raw-doc 可见性；固定 executor、镜像 digest 和预算。

再做小额人工批准后的少量真实 smoke：同一 agent 下 no-skill、raw-doc、naive-skill、候选-skill；检查正确包成功加载、引用可读/脚本依赖可用、任务结果文件实际通过 verifier、元数据和 trace 可追溯。此阶段之前不能声称 end-to-end already works。正式研究再加 clean/degraded paired input、source-level split/cluster CI、同预算对照，避免把 wrapper 修复和额外原文访问计为方法增益。

## 离线验证产物

`runtime_contract_checks.json` 中六项均由实际选取的上游函数运行，全部断言通过：

| 检查 | 实际观察 |
|---|---|
| 两个 nested packages | ValueError：Ambiguous generated skill packages |
| 仅 agnostic 产物 | evaluator lookup task path；available=false |
| 显式不存在 run | fallback legacy artifact |
| whole package staging | references/scripts 均保留 |
| Unknown skill 工具错误 | skill_triggered=true |
| 试验 False/True/False | reported pass_rate=1.0；算术平均 0.3333 |

这些是契约反例与文件复制验证，不是模型能力或 Docker e2e 运行成绩。

## 最终复审补充：45个文档来源的 agnostic 输入为空

在相同 SHA `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d` 下，对 `data_source/code_doc` 的9个 collection 和 `data_source/domain_knowledge_doc` 的36个 collection逐组只读检查：**45/45组的 `shared/materials/docs` 与 `shared/materials/tools` 均没有文件**。逐组绝对路径、相对路径、存在性、file_count和naive可读文本数已保存到 `agnostic_shared_materials_audit.json`；复现脚本为 `audit_agnostic_inputs.py`。

```text
python -I -B audit_2026-10-15/audit_agnostic_inputs.py
groups_total=45
groups_by_source_type={code_doc:9, domain_knowledge_doc:36}
groups_with_zero_shared_files=45
groups_with_empty_naive_agnostic_source_body=45
```

`baseline/naive_prompt/generate_skill.py:283–304` 的 agnostic prompt只读取上述shared docs/tools，`read_text_tree` 在路径不存在时返回空字符串（`:51–54`），再渲染为 `(none)`（`:300–304`）。因此**即使先解决JSON/import和agnostic输出路径问题，这45个文档来源的公开agnostic分支仍没有实际来源文档，只给库名/collection/source等元信息**。文件计数是直接观察；prompt为空的结论是代码路径推断，未运行任何模型。

这是独立于第2节输出路径错配的输入端断线。若要从task-local文档重建source-level corpus，须预先按来源冻结文档并集、排除task.json及当前任务提示、保留hash/边界，并披露为数据协议适配，不能称为“原样读取公开shared材料”。本次没有修复输入或修改上游。
