# R3：BeautifulSoup Task-037 运行时就绪性与隔离审计

日期：2026-10-24（Asia/Shanghai）。项目：`D:\AS\AutoSkill-main`。性质：只读审计；用户要求的本报告是唯一允许新增的项目文件。本轮没有实施修复，没有执行 Docker 命令、模型 API、Harbor Trial、Oracle 或任何会写测试夹具/账本的单元测试。

## 1. 最终判定

**BLOCKED_NEEDS_FIX**。

当前已具备来源校验、配置转换和离线接口契约证据，尚未形成能启动 BeautifulSoup Agent、执行独立判分并可靠记录零模型证据的完整运行链。明确缺口包括：Agent 构造函数无条件拒绝；没有判分执行后端；通用 P1 预算仍限定旧 Git 试点；判分进程直接导入候选代码；原 Oracle 强制 `.name =` 的文本模式；公共批次入口固定使用 paid 模式及模型结果标记，不能直接充当无模型 smoke 入口。

这里的判定不否定 R2 的离线目标，也不表示应删除现有关闭保护。应先准备最小的无模型探针与判分后端，再单独申请运行时验证。真实付费 Agent 执行仍需更后面的独立准入。

### 1.1 当前实物状态

- 当前分支 `master`，HEAD `3073a1a1a7119603ccb2ac738fae269a8223c0d9`。本轮开始有 17 个 tracked 修改、880 个 tracked 删除、2,412 个未跟踪文件；暂存区为空。它们都是此前已有工作。
- BeautifulSoup 归档目录目前只有 `adapter.json` 和 `offline_adapter.json`；没有持久化的 `task.toml`、`instruction.md`、`environment/` 或运行 profile。`prepare()` 能在新外部工作目录派生这些文件，但本轮没有调用它。证据：[downstream_eval/tasks/sgb/code_doc/beautifulsoup4-task-037/adapter.json](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/sgb/code_doc/beautifulsoup4-task-037/adapter.json)、[downstream_eval/tasks/sgb/code_doc/beautifulsoup4-task-037/offline_adapter.json](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/tasks/sgb/code_doc/beautifulsoup4-task-037/offline_adapter.json)、[downstream_eval/sgb/beautifulsoup037.py:97](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:97)。
- 本轮只读执行 `verify_assets()`：11 项官方资产、4 份来源及其 manifest/快照哈希、15 个原始测试名核验通过；固定 Harbor 的本地 Git HEAD 与锁定提交一致，12 项锁定源码核验通过，`uv.lock` SHA256 与锁文件一致。证据：[downstream_eval/sgb/beautifulsoup037.py:20](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:20)、[downstream_eval/integration/harbor_adapter.py:23](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/harbor_adapter.py:23)。
- 登记仍为 `oracle_status=REVISION_REQUIRED`、`execution_status=BLOCKED`、`generation_case_id=null`、`legacy_runs=[]`；没有 BeautifulSoup 的正式 `runs/eval/sgb/` 任务目录。不能把原始任务 TOML 的 `enabled` 或离线 `OFFLINE_PREPARED` 当作运行准入。证据：[data/manifests/sgb/tasks.jsonl](D:/AS/AutoSkill-main/degradation_failure_lab/data/manifests/sgb/tasks.jsonl)（task_key `t-7f902c444353`）。

## 2. 实际调用链及断点

### 2.1 已实现的离线链

`beautifulsoup037.prepare(root, new_external_workspace, explicit profile/packages/images)` → `verify_assets` → `execution_config` → 构造 Harbor 1.4 TOML、原字节复制 instruction、按条件复制 Skill → `runner.trial_config(..., mode='probe')` → `validate_prepared` → 输出 `NOT_RUN` 报告。

该链不建立实验预算、不创建 `batch.started`、不调用 Trial、不启动判分器；`generator_identity_verified=False`、`task_success=None`、`model_api_results=False`。`validate_prepared()` 中的 `agent_visible_files` 是派生文件集声明，不是容器权限或镜像内容扫描结果。证据：[downstream_eval/sgb/beautifulsoup037.py:97](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:97)、[downstream_eval/sgb/beautifulsoup037.py:152](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:152)。

### 2.2 公共 Runner 的计划运行链

`runner.execute_batch(root, output, config, run_trial, grade, exposure, task_success)` → profile/执行 manifest/账本校验 → 为全部 label 构造 **paid** 配置 → 独占创建 `batch.started` → `Ledger.begin` → `run_trial` → 保存 native → `grade` → `exposure` → 结果与账本 finish。

BeautifulSoup 没有生产调用者将这几个回调绑定为完整执行入口；当前调用在测试中，`run_trial`、判分后端、异步执行器和 exposure 都被替换。证据：[downstream_eval/sgb/runner.py:149](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:149)、[tests/test_sgb_beautifulsoup037.py:250](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py:250)；限定搜索了 `downstream_eval/sgb/`、`scripts/sgb/` 与对应测试。

如果按现有配置调用 Harbor：`Trial.create` → 加载 Task → `SingleStepTrial.__init__` → `Trial.__init__._init_agent` → AgentFactory → `OfflineBeautifulSoupTerminus2.__init__` 无条件 `RuntimeError`。该拒绝发生在正常环境 setup 之前；不要通过正式批次试探，因为 Runner 在这之前已写 marker 并准入账本。证据：[.external/harbor-full/src/harbor/trial/trial.py:362](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py:362)、[.external/harbor-full/src/harbor/trial/trial.py:198](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py:198)、[.external/harbor-full/src/harbor/trial/trial.py:1200](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py:1200)、[downstream_eval/sgb/beautifulsoup_agent.py:5](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup_agent.py:5)。

### 2.3 判分链只实现到接口

`beautifulsoup037.grade_export` → `runner.collect_submission(artifacts_dir, 'agent_output.py')` → `scoring_plan` → 调用方提供的 `execute(plan)` → `normalize_score` → 增补原 Oracle 与候选 SHA256。

`execute` 当前没有任务运行后端实现；测试传入 Mock。计划中的独立镜像、只读挂载、网络策略、超时、依赖预检和结果读取均未实际生效。`preflight_required=True` 是数据字段，不能证明预检被执行。证据：[downstream_eval/sgb/beautifulsoup037.py:194](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:194)、[downstream_eval/sgb/beautifulsoup037.py:243](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:243)、[tests/test_sgb_beautifulsoup037.py:271](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py:271)。

## 3. 运行环境与固定 Harbor 兼容性

| 项目 | 已有证据 | 当前边界与阻断 |
|---|---|---|
| 固定代码身份 | Harbor 0.24.0，commit `2de4605b9404eada7d341388291e6e469c90330b`；12 项 source_files 与 uv.lock 本轮只读核验通过 | 固定源码不等于安装环境、可变 venv、Docker 镜像仍与其一致 |
| TaskConfig | 派生字符串明确 schema 1.4、`/workspace`、no-network、显式提交物 artifacts、separate verifier；R2 对固定 TaskConfig 源码做过校验 | R2 测试使用内存包命名空间绕过缺失的安装元数据；不是已安装 SDK 的 TrialConfig/AgentFactory 验证。当前宿主 Python 3.13.9，未发现 Harbor 包；未检查控制容器 |
| 任务包 | 有预构建镜像时 Harbor 允许省略 Dockerfile；新派生包保留空 environment/ | 仓库内未保存可直接启动的派生包；镜像引用仍需显式提供 |
| 镜像身份 | `_image` 仅接受带 64 位 sha256 的字符串 | 测试镜像是 `fixture-*-not-built` 加重复数字，未构建、未查询。未证明镜像存在、平台正确、内部无文档/答案 |
| 依赖来源 | 原始 Dockerfile 指定 bs4 4.12.3、pytest 8.4.1、pytest-json-ctrf 0.3.5；计划要求预装 bs4/pytest | 原始 base 是可变 `python:3.10-slim`，还有未固定包与安装网络步骤，不能作为完整可复现锁；缺传递依赖、离线制品哈希及实际镜像清单 |
| 控制端与任务 Python | 锁要求 Harbor Python >=3.12；原任务共享 light 环境为 Python 3.10 | 两者是不同角色，不应直接认定任务 Python 3.10 必然不兼容。需分别固定控制端 SDK 和 Agent/Verifier Python/依赖 |
| 终端与观测工具 | Terminus 使用 TmuxSession；P1 使用 inotifywait、stdbuf、find/cat | 计划只列 bs4/pytest，未证明 tmux、inotify-tools、coreutils 等可用；tmux 与原 test.sh 都含运行时安装回退，不应靠 smoke 时联网补齐 |
| Docker 生命周期 | 固定实现可自动准备 sidecar、build、compose up，开始前 down 同 session 的旧资源 | `force_build=False` 不等于无 build/pull；缺失 sidecar 或镜像必须停止，不能隐式补建。必须用新 session，避开既有 P0/Scrapy 名称 |

证据：[downstream_eval/configs/runner.lock.json](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/configs/runner.lock.json)；[tests/test_sgb_beautifulsoup037.py:117](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py:117)；[.external/harbor-full/src/harbor/models/task/config.py:425](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/models/task/config.py:425)；[.external/harbor-full/src/harbor/environments/docker/docker.py:1010](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/environments/docker/docker.py:1010)；[.external/harbor-full/src/harbor/agents/terminus_2/tmux_session.py:99](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/agents/terminus_2/tmux_session.py:99)；[.external/skillgenbench/5a8bd61d/docker/Dockerfile.claude:3](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/docker/Dockerfile.claude:3)；[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/test.sh:8](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/test.sh:8)。

### 3.1 路径关系与控制端挂载

- `/workspace`：目标任务工作目录，提交应在 `/workspace/agent_output.py`；`/workspace/input`、`/workspace/docs` 是原指令声明。离线派生没有复制干净文档，也没有证明镜像内这些目录存在或为空。
- `/workspace/skill`：原 instruction 声明的 Skill 路径；当前派生没有设置别名或显式桥接。
- `/harbor/skills`：固定 Harbor 有 injected Skills 且未设置 `environment.skills_dir` 时的默认注入位置，Terminus 通过该位置生成索引；NoSkill 没有注入时 effective skills_dir 可为 None。P1 又硬编码检查 `/harbor/skills`。不能只把 task TOML 改到 `/workspace/skill`，否则 P1 哈希/读取观测仍可能检查另一目录。
- 最小选择是明确以 `/harbor/skills` 为实际注入与索引路径，在新的派生指令/适配说明中统一约定；如必须兼容旧路径，需明确受控别名并证明没有第二份或旧 Skill。原 instruction 字节和原始快照继续保留，不在本轮更改。
- profile/manifest 的 `database`、`staged_root`、Task.path 和判分挂载来源由 `str(Path(...))` 写入，属于运行上下文内绝对路径。Windows 准备结果不能直接假定在 Linux 控制端可见；必须同平台重新派生新记录，或验证独立的新路径映射。`prepare` 还要求输出在仓库外。当前没有这样的正式 BeautifulSoup 运行记录。
- Scrapy launcher 固定了 C 盘旧 preflight、既有控制容器名和 D 盘 Linux 挂载路径；BeautifulSoup 没有引用它，不应直接复用其启动器。

证据：[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md:19](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md:19)；[.external/harbor-full/src/harbor/models/trial/paths.py:46](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/models/trial/paths.py:46)；[.external/harbor-full/src/harbor/trial/trial.py:1677](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py:1677)；[.external/harbor-full/src/harbor/trial/trial.py:1694](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py:1694)；[.external/harbor-full/src/harbor/agents/terminus_2/terminus_2.py:640](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/agents/terminus_2/terminus_2.py:640)；[downstream_eval/integration/p1_observer.py:204](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py:204)；[scripts/sgb/scrapy024.py:18](D:/AS/AutoSkill-main/degradation_failure_lab/scripts/sgb/scrapy024.py:18)。

## 4. 文档泄漏与 Agent 可见性

当前没有运行中的 BeautifulSoup Agent 可供本轮检查；下表是实际输入构造与固定框架源码支持的边界，不是容器内访问实测。

| 输入/通道 | 允许范围 | 当前证据与审计结果 |
|---|---|---|
| 任务指令 | 全部条件一致的题面、函数签名、提交位置 | 只复制原 instruction；它说明需求与路径，但未给出 `.name =` 解法。不能将已披露需求本身当泄漏 |
| `/workspace/input` | 任务必需输入，不含答案或其他条件材料 | 此任务无需额外语料；派生未复制 input；镜像预置内容未知 |
| `/workspace/docs` / context/docs | 仅在实验明确允许、且与条件一致时可见 | 原任务包含四份干净文档；本研究默认不应直接暴露这些上游生成原文。派生没有复制，但尚无镜像/挂载扫描，仍是实验有效性阻断 |
| Skill 包与索引 | 只允许本条件的已登记、冻结 Skill；NoSkill 必须为空 | 仅主机复制哈希已验证。当前包与 generator 都是离线夹具，未绑定真实生成来源；远端 hash、索引集合、正文读取与试后完整性尚未验证 |
| bs4 及依赖源码、help/docstring | 必需运行依赖通常可见，但属于可能补偿文档退化的信息 | 镜像将含库源码；预训练知识、源码与帮助可能让任务不依赖 Skill。须固定依赖版本、记录同条件暴露，并确认是否含四份原文；不能宣称机制完全排除了补偿 |
| tests、solution、heldout、原始答案 | Agent 阶段禁止可见 | 派生未复制；原始 tests 保持控制端路径。仅配置中写 separate 不足以证明隔离，独立后端尚不存在 |
| 环境变量 | 最小运行配置及本条件信息 | raw config 没有指定额外环境挂载，但镜像 ENV、task/trial env 与 SDK extra_env 仍可进入会话；未实测。不要记录凭据值，也不要转发无关文档路径或主机凭据 |
| 主机挂载与日志 | 仅新 trial 独立日志/提交物位置；禁止仓库、原文根、其他 trial、Docker socket | 固定 Harbor 默认挂 agent/verifier 日志与 publish 目录，也允许额外 mounts。需实测 mount allowlist，尤其确认新日志为空、不会带入旧判分/其他条件证据 |
| 镜像预置文件与网络 | 不含文档、答案、旧 Skill；deny-all egress | `_image` 的格式校验不检查内容。P1 的缺 `/tests` 检查也不等于检查 `/workspace/tests`，更不会扫描全部镜像。需任务专属目录与四份原文哈希检查、网络探针 |

### 4.1 有静态证据的危险复用途径

官方 SGB `claude_runner.start_eval_container()` 会将 `context_docs_dir` 挂到 `/workspace/docs`，将 `tests_dir` 挂到 `/workspace/tests`，并把 DOCS_DIR/TEST_ROOT_DIR 传入同一容器。只读挂载仍然允许读取。**如果把该启动器直接接入本研究，干净原文和隐藏测试会对 Agent 可见，构成明确的实验有效性阻断。** 当前 BeautifulSoup 离线适配没有调用它，本轮不声称已经发生泄漏。

证据：[.external/skillgenbench/5a8bd61d/scripts/claude_runner.py:309](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/scripts/claude_runner.py:309)（337–348 行）；[downstream_eval/sgb/beautifulsoup037.py:128](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:128)；[.external/harbor-full/src/harbor/trial/trial.py:1938](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/trial.py:1938)；[downstream_eval/integration/p1_observer.py:172](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py:172)。

## 5. 提交物和判分器独立性

### 5.1 收集协议：路径可表达，传输可靠性未证明

原指令要求 `/workspace/agent_output.py`；派生 artifact 显式映射到 host trial 的 `artifacts/workspace/agent_output.py`。固定 Harbor 的 `SingleStepTrial._run` 会收集 artifacts；即使 native verifier 被关闭，也不会因此跳过收集。separate 模式正常流程随后停止 Agent 环境。Docker 的停止可执行 compose down，即使 delete=False 也不能理解为容器必然一直运行。

`collect_submission` 对整个 artifacts_dir 按文件名 rglob，只检查数量是否为 1；没有核对精确 source/destination、Harbor artifact manifest 的 `status=ok`、文件类型/来源或原始导出哈希。官方下载是 best-effort，失败会写 `status=failed`。当前缺文件被归为 `submission_missing`，而 Runner 默认不将此类别计入 infrastructure error，因此真实下载失败可能与 Agent 未提交混淆。

最小修复是任务收集适配核对指定 artifact manifest 条目与精确文件路径：下载失败/来源不明→unscorable，确证 Agent 未生成文件→按预定任务失败规则；重复文件继续拒绝。随后以受控文件实测上传、下载及候选 SHA256，不改官方采集实现。

证据：[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md:24](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md:24)；[downstream_eval/sgb/beautifulsoup037.py:121](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:121)；[.external/harbor-full/src/harbor/trial/single_step.py:37](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/single_step.py:37)；[.external/harbor-full/src/harbor/trial/artifact_handler.py:24](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/artifact_handler.py:24)、[.external/harbor-full/src/harbor/trial/artifact_handler.py:234](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/artifact_handler.py:234)；[.external/harbor-full/src/harbor/environments/docker/docker.py:1188](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/environments/docker/docker.py:1188)；[downstream_eval/sgb/runner.py:115](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:115)、[downstream_eval/sgb/runner.py:174](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:174)。

### 5.2 separate 声明不能代替真实独立判分器

`runner.trial_config` 设置 `verifier.disable=True`；固定 Harbor `SingleStepTrial._run_verifier` 因此直接返回，不会仅因 task TOML 中 separate/environment 声明就启动 native verifier。真正的判分应由 `grade_export(..., execute=...)` 的独立后端完成。

scoring_plan 的四个挂载分别是：候选 → `/workspace/agent_output.py`（只读），原 `eval.py` 与 `test.sh` → `/workspace/tests/`（只读），新结果目录 → `/logs/verifier`（可写）。使用原 shell、`TEST_ROOT_DIR=/workspace`、新增 PYTEST_ADDOPTS 产出完整 JUnit，禁用自动插件。原 shell 结束总是 exit 0，CTRF 缺失时仅造一条汇总，因此解析器必须结合 reward 和完整 15 项 JUnit，不能只看 shell 返回码或 CTRF 1/1。

当前后端没有实现目录新建/拒绝复用、镜像/依赖实检、只读挂载执行、UID/权限、网络、超时终止、结果回收或退出码语义；这些字段是接口要求而非执行事实。不能借 Scrapy 的响应桥接替代：这里 Oracle 在 pytest 进程中操作真实 Tag 对象，且检查对象身份、属性和文档树位置。

证据：[downstream_eval/sgb/runner.py:104](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:104)；[.external/harbor-full/src/harbor/trial/single_step.py:88](D:/AS/AutoSkill-main/degradation_failure_lab/.external/harbor-full/src/harbor/trial/single_step.py:88)；[downstream_eval/sgb/beautifulsoup037.py:194](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:194)、[downstream_eval/sgb/beautifulsoup037.py:219](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:219)；[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/test.sh:18](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/test.sh:18)；[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/eval.py:22](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/eval.py:22)。

### 5.3 Oracle 导入隔离存在设计缺口

原 eval.py 在第 11 行直接 `import agent_output`。按当前计划，候选代码与可信断言在同一个 Python 进程/权限域执行，Oracle 文件可读，结果目录可写。只读 Oracle 挂载能保护磁盘字节，不能阻止读取测试、同进程状态/函数污染或结果文件伪造。当前解析器对测试名和 reward 的一致性检查，不构成报告真实性或候选隔离证明。

最小下一步是先规定候选与可信断言的信任边界，并设计一个任务专属、版本化的隔离验证方案；不能为通过 smoke 而关闭原断言或沿用当前直接导入即声称隔离完成。若方案需要新桥接/新 checker，应保留原 Oracle 原字节与独立版本身份，另行审查授权。当前必须阻断将其用于可靠成功率或机制结论。

### 5.4 原 Oracle 存在语义假阴性

`test_uses_tag_name_assignment` 对完整源码匹配 `.name` 与正则 `\.name\s*=`，会拒绝仅用 `setattr(tag, 'name', new_name); return tag` 的等价原位重命名实现；匹配整个源码也不能证明实际执行了该赋值。这一文本约束比题面行为要求更强。

这属于静态可证明的评价口径问题；具体版本中是否满足全部行为断言仍需受控正负例执行。应先明确研究指标是“原 benchmark 含语法约束的得分”还是“行为正确率”。保留原分数及其限制；如需要行为指标，另立版本化 scorer，不能改写现有 Oracle/历史 manifest。

证据：[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/eval.py:165](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/eval.py:165)、[.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md:5](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md:5)。本轮没有执行该反例或创建样例文件。

### 5.5 现有正负证据的边界

R2 的 `evidence()` 人工生成 testcase/failure/error XML，`batch()` 使用 `AsyncMock`、Mock 判分后端、替代 asyncio.run 与假的 trial；所谓正负只验证解析和状态分类。测试候选文件甚至标明 `Fixture only; never imported`。因此没有已执行的正确 BeautifulSoup 实现、错误实现或独立 Oracle 运行证据，也没有判分可信性校准。证据：[tests/test_sgb_beautifulsoup037.py:61](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py:61)、[tests/test_sgb_beautifulsoup037.py:250](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py:250)。

## 6. 实验身份、预算与历史冻结身份

### 6.1 已有保护

- Scrapy 将 `s24r005`、`scrapy024-s24r005-<s24dNNN>`、scope `scrapy-task-024/s24r005/initial-calibration` 保留在专属入口。`calibration_output` 拒绝旧位置同实验及新位置 batch.started。历史 `s24d001/batch.started` 本轮确认仍存在。
- 公共 ExecutionConfig 的任务/实验/生成/预算/Agent/条件字段没有 Scrapy 默认值；profile 必须匹配 task/experiment、条件顺序及本输出目录 budget 路径。
- `verify_ledger` 用 SQLite mode=ro 读取已有 policy，并核对 scope、trials、order、limits、budget 与 frozen file 集。Ledger.begin 继续核对冻结文件、单次准入、顺序与停止状态；missing ledger 不会被公共校验重建。
- BeautifulSoup 前缀固定自身 task，scope 还必须包含显式 generator。使用原 Scrapy scope/账本应被 profile 与 policy 检查拒绝，不能将两者当兼容预算。

证据：[downstream_eval/sgb/scrapy024.py:25](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/scrapy024.py:25)、[downstream_eval/sgb/scrapy024.py:34](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/scrapy024.py:34)；[downstream_eval/sgb/runner.py:21](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:21)、[downstream_eval/sgb/runner.py:55](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:55)、[downstream_eval/sgb/runner.py:134](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:134)；[downstream_eval/integration/request_budget.py:110](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py:110)。

### 6.2 真实执行前仍需补齐的身份约束

1. **真实生成身份没有验证。** 本轮只在内存中用 `generator_run_id='s24r005'`、scope `beautifulsoup4-task-037/s24r005/audit-only` 构造 config，当前代码接受它。此检查没有打开账本、没有运行任务，证明只是字符串前缀绑定，不证明该生成运行来自 BeautifulSoup；不意味着旧 Scrapy 账本可通过 policy 校验。真实准入须验证生成 run 的 case/source/condition、注册 ID、package hash、导出和原文来源；可复用已有 canonical_packages/load_run 校验，不接受改标签代替来源证明。
2. **不能只删除 Offline Agent 的 raise。** 其基类 P1 的 `_budget_ledger` 调用 `ledger_for_profile`，只接受 `/opt/harbor-venv/p1-budgets/p1-c-20261019-001*.sqlite3` 与六请求预算。需要 BeautifulSoup 的显式任务/实验 budget 适配；不能换路径指向旧 Git 试点来通过检查。R2 的 probe 夹具也不是完整 paid profile，未提供 paid 分支需要的 approval_environment_variable、budget.num_retries、frozen_agent_image_id 等。
3. **公共批次不是通用无模型入口。** 它固定 mode='paid'，保存 `model_api_results=True`，不读取 OFFLINE_ONLY/allow_model_execution/readiness，也不自己执行 Scrapy paid_batch 的外层审批与 runtime_versions 检查。现有关闭 Agent 保护了正常 BeautifulSoup 路径，但低层函数自身不是足够的执行准入；R2 的 Mock 批次也据此写出了模型结果标记（仅临时夹具，非历史污染）。smoke 必须使用单独入口与明确 `model_calls=0/task_success=null`，不能借正式 paid_batch 运行。
4. **冻结清单不自动建立。** BeautifulSoup prepare 不创建 execution_manifest 或 ledger；公共 verify_frozen/verify_ledger 校验调用方提供的清单，不验证清单是否覆盖全部关键资产，也没有非空检查。正式执行入口应建立新的、完整的代码/资产/条件/来源身份清单，不得复用空测试清单或旧实验记录。

证据：[downstream_eval/sgb/beautifulsoup037.py:67](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py:67)；[downstream_eval/integration/p1_observer.py:95](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py:95)、[downstream_eval/integration/p1_observer.py:274](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/p1_observer.py:274)；[downstream_eval/integration/request_budget.py:242](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/integration/request_budget.py:242)；[tests/test_sgb_beautifulsoup037.py:43](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py:43)；[downstream_eval/sgb/runner.py:123](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:123)、[downstream_eval/sgb/runner.py:149](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py:149)；[downstream_eval/sgb/scrapy024.py:205](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/scrapy024.py:205)。

锁文件中的 `allow_model_execution=false` 仍保留。本轮在 downstream_eval/src 的 Python 源码中未发现对这一字段的消费，不能把该元数据单独当成防模型调用的技术屏障。没有读取或加载任何凭据。

### 6.3 新旧代码身份

当前 R1/R2 候选代码没有正式提交；不能仅凭 HEAD 代表它。原 Scrapy execution manifest 仍引用历史入口/哈希，当前代码与历史运行身份必须分开。后续只能创建新实验/新的执行身份；不得更新旧清单以让新代码冒充当时版本。原路径恢复仍需使用既有 relocation/provenance 和冻结备份，不能绕过哈希检查。

本轮仅原始字节读取现有账本和 manifest 计算哈希，没有 SQLite 连接、begin、snapshot 或 finish，也没有为 BeautifulSoup 分配研究预算。

## 7. 最小执行前检查表

证据标签：**静态**＝当前代码可证明；**离线**＝R2 已跑测试证明的接口范围，本轮只重读测试；**运行时**＝需容器/完整 SDK；**Agent**＝需后续真实模型 Agent；**缺陷**＝当前明确缺口。

| 检查项 | 当前状态 | 证据 | 是否阻断真实执行 | 下一步 |
|---|---|---|---|---|
| 任务配置 | 静态/离线通过；仓库内只有两份元数据 | §2.1、§3；prepare/TaskConfig 测试 | 是，缺正式派生包/profile | 在新上下文用真实镜像和明确身份重新准备 |
| 固定 Harbor 兼容性 | 源码/uv.lock 身份通过；完整 SDK 未证 | §3；12 项源码哈希 | 是 | 在固定 Linux 控制端核验安装来源、完整依赖锁匹配与真实模型配置 schema |
| 运行环境与依赖 | 运行时未证，镜像测试值不可执行 | §3、§3.1 | 是 | 仅核验已存在镜像、平台、依赖/工具及 sidecar；缺失即停 |
| 文档与 Skill 可见性 | 派生不复制原文；镜像/目录/索引未知 | §4；native upload + P1 hash/index | 是，实验有效性 | NoSkill/Skill 两条件做目录、挂载、原文哈希与索引检查 |
| 隐藏测试隔离 | 设计为后置判分，尚无后端；官方 launcher 会直接暴露 | §4.1、§5.2 | 是 | Agent 时间段证明 tests/solution/原文不可读，再启动独立 grader |
| 提交物收集 | 静态映射明确；缺 artifact manifest 核验 | §5.1 | 是 | 核对固定条目/status，受控文件传输 SHA 一致 |
| 独立判分器 | 缺陷：execute backend 缺失 | §2.3、§5.2 | 是 | 实现最小隔离执行与证据回收，再跑真实正负样例 |
| Oracle 导入隔离 | 缺陷：同进程导入；还有语法假阴性 | §5.3、§5.4 | 是（可信评价）；原 Oracle 对照运行需注明限制 | 先定信任边界与评价口径，保留原 Oracle，另审版本化适配 |
| 实验身份与预算 | 基础拒绝保护存在；生成来源、专属 Agent budget 未接入 | §6 | 是；环境-only smoke 可用明确夹具，不分配 paid 预算 | 新 smoke 身份；真实执行另绑定真实生成 run 和新账本 |
| 结果记录 | 离线可区分阶段；公共 paid 批次标记不适合 smoke | §5.5、§6.2 | 是 | 独立 engineering 记录，明确 0 模型调用、非真实任务成功 |

## 8. 阻断清单、最小动作与停止条件

| ID / 证据层级 | 最小必要动作（本轮未实施） | 验证预期 | 失败即停止 |
|---|---|---|---|
| B1 启动断点【静态、缺口】 | 保留 Offline Agent；新增独立的无模型探针入口，先只用原生环境与官方 Skill 方法，不进入 paid batch | 无模型初始化/HTTP；能走通环境与传输证据 | 触发 Offline 拒绝、SDK/模型网络或试图使用正式账本 |
| B2 环境/依赖【运行时】 | 选定控制端与两种镜像 digest、平台、离线依赖/工具清单，检查 sidecar 已就绪 | SDK 版本/来源匹配；bs4/pytest/tmux/inotify 可用；无临时安装 | 需要自动 pull/build/联网安装，版本漂移或镜像内容不明 |
| B3 路径/泄漏【静态+运行时】 | 统一 Skill 路径；检查 Windows/Linux 控制路径可见；全新 NoSkill/Skill 环境逐项验权 | NoSkill 无 Skill/索引；Skill ID/hash/索引一致；四份原文与 tests/solution 不可读 | 任一禁止路径、原文哈希、旧 Skill、跨条件文件或异常 mount 可读 |
| B4 判分后端【缺口+运行时】 | 绑定独立 execute(plan)，强制 fresh output、只读资产、网络/权限/超时与完整 JUnit/reward 读取 | 每次新环境；原 Oracle 字节不变；结果来源可追溯 | 复用旧结果、缺日志、缺/重复测试、超时未清理、安装回退 |
| B5 Oracle 信任/口径【缺陷】 | 先审候选与断言的隔离；保留原得分，明确 syntax 与 behavior 指标 | 不能由候选读隐藏测试或伪造可信判分；等价实现差异有解释 | 仍是同进程无限制导入却声称隔离，或悄悄移除原断言 |
| B6 artifact 归因【静态缺口+运行时】 | 任务收集器核对 source/destination/status 与导出 SHA | 下载失败是基础设施错误，真实未提交按明确任务规则记录 | 收集来源不明、重复、哈希变、manifest failed 却判答错 |
| B7 身份/预算【静态+真实执行前置】 | 显式新实验/生成/条件身份，新增预算适配与完整冻结集合；真实生成须核对 case/source/register/hash | 拒绝 Scrapy/Git 账本与错误生成来源；不重用历史 marker | 需要修改旧 manifest/预算才能运行，或只改标签就接受错误来源 |
| B8 正负校准【运行时】 | 使用独立新样例：直接原位改名、破坏内容/属性/位置的错误例、setattr 等价例 | 正确原例 15/15；错误例至少一项失败；等价例的语法拒绝被单独报告 | 全部都通过/都失败、只出现 CTRF 1/1、候选可影响 Oracle/结果 |
| B9 记录和模式【静态缺陷】 | smoke 入口显式零模型、独立工程记录，不调用当前固定 paid 的 execute_batch | model_calls/HTTP=0；task_success=null；不进入成功率汇总 | 标为真实 model_api_results/Agent success，或消耗研究预算 |
| B10 实验有效性【Agent，后续】 | 只在 B1–B9 满足后，另行授权最小真实 Agent 校准；记录索引、实际读取、成功 HTTP 中正文和独立输出判分 | 能区分可见、读取、正文进入模型和真实任务结果 | 仅凭索引/受控 cat 就宣称模型使用或规则遵循，或出现干净原文旁路 |

B10 不是本轮可执行工作，也不是环境 smoke 的前置；它是宣称真实 Skill 作用与真实 Agent 性能之前必须补的证据。真实 BeautifulSoup Skill 的生成/来源验证同样不能由 smoke 夹具替代。

## 9. 下一阶段无模型运行时测试的最小计划（需单独授权）

### S0：先补最小代码与审查，仍不运行

准备 B1 的环境探针入口、B4 的后端、B6 的提交物证据核对，以及 B9 的工程记录。不要删除当前 Offline 入口，不重用 paid execute_batch，不为探针接旧预算。原 Oracle 的语法/导入限制另立审查项，不能因环境 smoke 通过就解除该项阻断。

### S1：固定控制上下文与已存在镜像

在新、短路径的独立工程工作目录准备输入，统一在选定 Linux 控制上下文解析路径。以后单独授权的操作包括：查询 Docker/镜像身份与平台、检查完整 SDK/uv.lock/安装来源、检查所有 task/sidecar 镜像及离线依赖。先检查，缺任何镜像或包立即停，另申请 build/pull；不把 Harbor.start 的自动构建能力当作授权。

控制端不加载真实模型凭据，安装模型/HTTP tripwire，禁用 SDK 隐式远程元数据获取。任何真实模型 SDK 请求、未知外联或 HTTP attempts 非零都停止。独立 session/container 名称不得与 `harbor-p0-control-20261018` 或现有 Scrapy 资源重复。

### S2：两个隔离条件的目录、权限和 Skill 检查

后续明确授权仅创建全新的 smoke 容器/网络/临时日志，并允许对这些新资源清理；不操作历史容器。先不实例化 Terminus 模型客户端，使用 Harbor 环境 API 与精确官方 Skill 发现方法：

1. NoSkill：检查工作目录与所有 mount/ENV 来源，Skill 目录及索引为空；禁止文档/测试/答案/旧运行/主机根与 Docker socket。
2. Skill：注入明确标为 fixture 的冻结测试包，校验远端逐文件哈希和 ID/metadata 索引，受控读取正文后再次核对；不得将此记录为真实生成 Skill 或模型读取。
3. 对四份干净文档的来源哈希、已知路径、镜像预置内容及允许依赖源码做针对性扫描；对阻断网络做受控探针。发现禁止输入即停止，不在原镜像中删文件“修好”。

原生 Trial 如用于验证工厂/生命周期，必须在后续授权中明确写出“无模型受控 Trial”，不能在本轮或本计划未获授权时调用 Trial.create。仅环境/API 探针通过也不能替代此项。

### S3：真实传输与独立 Oracle 对照

控制端注入固定候选，使用官方 artifact 通道导出；检查确切 manifest 条目和 SHA。随后在另一个无网络 verifier 环境执行原 test.sh，使用全新结果目录，记录原始 stdout/stderr、returncode、reward、完整 JUnit 和 Oracle/候选 hash。先做 B8 三类受控样例，再做一次超时/缺依赖/缺提交的受控失败，以确认错误归因。禁止调用模型。

直接 import 的原 Oracle 仅作为有明确限制的 benchmark 对照；在 B5 关闭前，不能据此声称对抗性判分隔离完成，也不能开启正式成功率评估。

### S4：归档工程证据并停止

记录 `run_kind=runtime_smoke`、完整版本/镜像/路径身份、网络与挂载证据、`model_calls=0`、`actual_http_attempts=0`、`real_agent_outcome=false`、`task_success=null`。所有记录在新工程位置，不能覆盖 runs/results/manifest/研究账本。单独报告环境 smoke 与 Oracle 对照状态；通过后仍等待真实 Agent 阶段授权。

## 10. 本轮检查清单与证据边界

| 本轮实际动作 | 结果/边界 |
|---|---|
| Git status、HEAD、branch、cached diff、index 原始 SHA | 已记录候选基线；只读 `--no-optional-locks`；未更新索引/提交 |
| 指定模块、两份任务元数据、两组测试、固定 Harbor task/Trial/Agent/Docker/artifact 源码逐项读取 | 已追踪调用与阻断；没有以文件名推断可执行性 |
| 原始 SGB task/instruction/eval/test.sh、共享 Dockerfile 和官方 launcher 读取 | 明确共享依赖来源、测试直导入、语法限制与官方 launcher 的原文/测试挂载 |
| `verify_assets()` 与锁文件/uv.lock 哈希 | 只读通过 11 官方资产、4 来源、15 测试清单、12 固定源码；没有跑 Oracle |
| 内存构造错误生成来源别名 | `s24r005` 在 BS 文本 scope 下可被接受，证明缺实际来源绑定；没有创建文件/预算 |
| 测试证据审阅 | R2 会话执行记录为 50 项中 49 通过、1 跳过；本轮未重跑。当前源码确认 16 项 BS 测试使用 fixture/Mock；不等价真实正负判分 |
| 未进行的验证 | 没有 Docker 命令、SDK Trial/Agent 初始化、网络/模型请求、容器目录检查、真实提交物传输或原 Oracle 执行 |

当前内存核验使用 `python -B` 禁止 bytecode，阻断 socket/DNS/子进程，并将 Path.write_text/write_bytes 设为拒绝；没有运行会建立临时夹具、SQLite 或历史记录的测试。只有报告写入步骤解除其唯一目标文件的写入限制。

## 11. 关键身份与本轮文件变更

| 文件 | 本轮读取的 SHA256 |
|---|---|
| [downstream_eval/sgb/runner.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/runner.py) | `d3da5477d25fb9a134d8b1cd90232188d1fd6b8db8c360c1350c917512cfa234` |
| [downstream_eval/sgb/beautifulsoup037.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup037.py) | `2b26beb4ab0804a651f3cb6b144727c464438ea329af46dd444488ca4b4658e1` |
| [downstream_eval/sgb/beautifulsoup_agent.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/beautifulsoup_agent.py) | `ca2943d7fbd1656ba532dd5d29d7a73b3376c743f459c8d5d3b7bee1366ade9c` |
| [downstream_eval/sgb/scrapy024.py](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/sgb/scrapy024.py) | `75b69e42d40cf2f70c82649c9990325729dabc299748189daa7954ceb37b5bea` |
| [tests/test_sgb_runner.py](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_runner.py) | `1edf9050b815c26f6f9989653b2e50ca3708d011d176bc6a3486464436a7b8cc` |
| [tests/test_sgb_beautifulsoup037.py](D:/AS/AutoSkill-main/degradation_failure_lab/tests/test_sgb_beautifulsoup037.py) | `cc124f8c465439db8cff5f6a36e7f669ccbbd50bcfa5b36ce36c5bd006c29271` |
| [downstream_eval/configs/runner.lock.json](D:/AS/AutoSkill-main/degradation_failure_lab/downstream_eval/configs/runner.lock.json) | `7faeb805a64e722a0a8a05ac8404a220707336d85be180a5913563b5a0638fd2` |
| [.gitattributes](D:/AS/AutoSkill-main/degradation_failure_lab/.gitattributes) | `f121360a29c132f30ba9dfdbd39abe0f914b77c1985aeb635a0a64fde129d4fa` |
| [.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/task.toml](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/task.toml) | `0c37f064dca6812e687607d3940614cbef11b8477670fc8135504b30b6241691` |
| [.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/instruction.md) | `c2c2d3658874209a470e72d2fcd9b0f0f2d5c56a3352465772820026487efbbb` |
| [.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/eval.py](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/eval.py) | `c7ee6d37d069c02aa9c6059ed6dcc28857ad44dcdd002d73642fa4838a4c7e6c` |
| [.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/test.sh](D:/AS/AutoSkill-main/degradation_failure_lab/.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/beautifulsoup4/beautifulsoup4-task-037/tests/test.sh) | `2ad84cb7df6840331626a506a5e106ddb79de898da1737bf21471f1d3b8d472a` |
| [runs/eval/sgb/scrapy-task-024/s24d001/budget.sqlite3](D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-024/s24d001/budget.sqlite3) | `3676ad026cc373b6cea265177eda48205190ae8b89ed55b7fc6af8362aba6d09` |
| [runs/eval/sgb/scrapy-task-024/s24d001/execution_manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/scrapy-task-024/s24d001/execution_manifest.json) | `7d0f2a35c2102acf5b9f68361fca61f1462b08a22a6d86f74acbdb823d001efa` |

本轮开始的全部代码/资产字节摘要（排除所有 .git、IDE 自动状态 .idea，并排除本报告路径）：30,115 个文件，1,672,212,110 字节，2 个 Linux reparse 链接；摘要 `e1a662a77b1fc1764b28f9e579e7fbf6c8780a51293e46a1e64b281f9f3fdbb6`。IDE 状态不作为研究资产，未还原或编辑。本报告之外的项目代码、官方实现、快照、Oracle、清单、账本和历史结果不应有任何本轮变更；交付前按同一范围复核。

开始时不含报告的 Git 状态摘要：`040fb76fcd3bb13277aa6432ae1001c3ecf8b00dfbae98ba175878a0a6db725b`；Git index SHA256：`2454cc749f587b0fee24774c9da654cd6ab0219b121b13a4ee457ee5e32acf33`。本轮唯一新增文件应为本报告；不暂存、不提交、不推送。

**后续顺序：先准备最小探针/判分/记录修复并审查，再申请 S1–S4 无模型运行时验证；当前不进入真实 Agent 执行。报告交付后停止。**

交付核验结果：报告生成后复核通过；排除本报告、所有 .git 及单独排除的 IDE 自动状态 .idea，30,115 个既有文件、1,672,212,110 字节及 2 个链接的摘要与本轮开始完全一致。Git 状态仅新增本报告，原有 17 修改/880 删除/2,412 未跟踪均保留，交付时未跟踪为 2,413；暂存区、index SHA256 与 HEAD 不变。该核验没有运行任何 Docker、模型、Trial 或测试。
