> 后续 Docker 实机验收已完成：见 [2026-10-18 实机报告](docker_validation_2026-10-18.md)。下文保留首次离线阶段记录。

# P0 工程架构与真实工作树审计

## 审计结论

审计于 2026-10-18 在真实 Git 工作树完成。根目录为 `D:/AS/AutoSkill-main`，分支 `master`，HEAD 为 `ace65737e8d0be08eda1c47d5a8e62f119989ded`。实际研究主目录是根下 `degradation_failure_lab/`；文档工作区中同名目录只有审计文档，不是本次实现落点。

官方 Anything2Skill 位于内层 `AutoSkill-main/`。旧 `AutoSkill-main/research/robustness/` 保留了协议、来源、B0 冻结和历史 smoke 记录，其 runners 只有说明文档，tasks/skills/verifiers/executions 多为 `.gitkeep`。没有发现可直接复用的 Harbor、Terminus-2 或 Git 状态 Oracle 实现。旧审计中的 `oracle_probes.py` 属于其他 Benchmark 的语义审查，不是本任务的执行器。

审计前已有六组未提交审计文档/目录，全部保留。没有删除、迁移旧目录、冻结文件或历史结果。修改前的精确状态和文件哈希存于最终运行目录中的 `repository_before.json`；受保护文件复核见 `protected_files.json`。

## 修改前真实目录与用途

```text
AutoSkill-main/                         # Git 根
├── .git/
├── .idea/
├── AutoSkill-main/                     # 官方实现与旧研究资料
│   ├── AutoSkill4Doc/                  # 官方文档技能生成
│   ├── autoskill/                      # 官方运行和存储模块
│   ├── tests/
│   ├── README.md / README.zh-CN.md / STATUS.md
│   └── research/robustness/            # 历史协议/B0冻结/smoke；不迁移
└── degradation_failure_lab/           # 当前研究主目录
    ├── README.md / .gitignore / .gitattributes
    ├── cases/                         # 5 个真实 Clean 来源案例
    ├── configs/                       # 路径、生成配置
    ├── data/                          # catalog/manifests/raw_sources
    ├── docs/research/                 # 已有研究与审计资料
    ├── results/                       # 导出、汇总、run index
    ├── runs/case*/                    # 原始生成运行，含冻结 SkillBank
    ├── schemas/
    ├── scripts/lab.py                 # 统一入口
    ├── src/degradation_lab/
    │   ├── catalog.py / io.py / schema.py
    │   ├── runner.py / adapter.py / provider_adapter.py
    │   ├── artifacts.py / evaluation.py / cli.py
    │   └── __init__.py
    └── tests/test_framework.py         # 18 个已有测试
```

| 现有模块 | 已实现功能 | 本轮复用/保留 |
|---|---|---|
| `catalog.py` | 来源版本、路径、哈希、case/condition 关系校验 | 保留；下游直接引用同一来源 manifest |
| `io.py` | JSON、路径边界、SHA、inventory、时间 | 复用，未改 |
| `artifacts.py` | 定位生成运行、读取四阶段注册数据和 canonical 身份 | 复用 `load_run`，未重新实现生成导出器 |
| `runner.py` / `adapter.py` | 官方生成、预算、模型观察和运行隔离 | 保留，不进入下游执行链 |
| `evaluation.py` | 规则人工评价和汇总 | 保留；不拿规则审核代替 Git 状态判分 |
| `schema.py` | 现有来源、case、规则等 JSON 协议 | 保留；没有把下游结果伪装成生成运行 |
| `scripts/lab.py` / `cli.py` | 统一命令入口 | 只在 CLI 加一个零模型子命令 |
| 旧 `research/robustness` | 研究协议、冻结和历史示例；执行目录多为空壳 | 原位保留，不重复迁移 |

冻结来源包含 Git `a52a24e03c8c711f1d5e252fba78f9276908129b` 的 `git-restore.txt`，以及 qsv select/sort、docker cp、ripgrep 的现有来源。Git canonical 位于 `runs/case004_git_restore/clean/r18307cee4f4c/SkillBank/Users/docskill/<原目录>/SKILL.md`；来源管理仍以 `data/manifests/git_restore.json` 为准。

## 修改后的结构

```text
degradation_failure_lab/
├── 原有模块和冻结数据                  # 原位保留
├── scripts/lab.py                     # 原文件不改；调用修改后的 cli.py
├── src/degradation_lab/cli.py          # 加 downstream-check
├── tests/
│   ├── test_framework.py              # 原样保留
│   └── test_downstream.py             # 新增离线测试
├── .external/                         # ignored 外部依赖，不属于研究源码
│   ├── harbor-2de4605/                # 经 blob 校验的源码子集；不是已安装 Harbor
│   └── git-a52a24e/t/t2070-restore.sh  # 固定官方语义证据
├── downstream_eval/
│   ├── README.md / __init__.py
│   ├── configs/
│   │   ├── runner.lock.json
│   │   └── git_restore_pilot.json
│   ├── integration/
│   │   ├── harbor_adapter.py          # 固定源码检查、官方方法探针、环境检查
│   │   ├── skill_install.py           # canonical 身份、无损复制、发现校验
│   │   └── terminus_compat.py         # 官方 Agent 的最小内存换行兼容子类
│   ├── checks.py                     # 零模型验收编排与日志
│   ├── tasks/git_restore_explicit_source_both_v1/
│   │   ├── task.toml / instruction.md
│   │   ├── fixture.py / oracle.py
│   │   ├── environment/Dockerfile
│   │   └── tests/Dockerfile / test.sh / verify.py
│   └── docs/
│       ├── architecture.md
│       ├── validation_report.md
│       └── change_list.md
└── runs/downstream/git-restore-explicit-source-both-v1/<run_id>/
    ├── result.json / preflight.json / skills.json / oracle.json / harbor.json
    ├── staged_skills/<UUID>/SKILL.md
    ├── installed_skills/<UUID>/SKILL.md
    ├── available_skills.xml
    ├── oracle/repeat-<n>/<case>/repo/ + trusted-initial.json + oracle-result.json
    ├── harbor_task/                   # 物化任务；环境和 tests 获得各自的代码
    └── *.log / artifact_manifest.json / 审计记录
```

没有另建 results 或 generation manifest 系统。下游结果统一进入现有 `runs/` 的专用命名空间，避免和 `runs/case*/` 的生成记录混淆；不向生成 `run_index.jsonl` 写入虚假的生成事件。

## 实际调用链和官方边界

```text
scripts/lab.py → degradation_lab.cli.main → downstream_eval.checks.run_checks
  ├─ existing io + source manifest/hash
  ├─ harbor_adapter.preflight → 固定文件 SHA/环境/安装身份
  ├─ skill_install → existing artifacts.load_run → 官方注册 ID + 冻结哈希
  │    → UUID staged/installed 目录 → 官方 resolve_skills 方法
  │    → 官方 Terminus2._build_skills_section → Bash find/cat → XML + ID 集合
  ├─ fixture.build → Git plumbing + 固定身份/时间 → 可信初态
  │    → 正解/真实错误操作 → oracle.evaluate → 逐断言结果
  └─ materialize_task → 官方 task.toml + artifact + separate verifier
       → 条件满足时 harbor trials start --agent oracle → rewards/日志
```

官方职责：任务 schema、环境、artifact 下载/清空目标/上传、separate verifier 生命周期、`oracle` Agent 和 Terminus-2 解析/索引方法。新增职责：冻结 Skill 身份校验、UUID 映射、换行输入兼容、Git fixture/Oracle、离线验收和报告。没有另造 Agent 推理框架。

上游代码依据固定 [Harbor 提交](https://github.com/harbor-framework/harbor/tree/2de4605b9404eada7d341388291e6e469c90330b)。关键接口为 `src/harbor/skills.py`、`agents/terminus_2/terminus_2.py`、`models/task/config.py`、`models/task/verifier_mode.py`、`trial/artifact_handler.py` 和 `verifier/verifier.py`。源码子集的 SHA-256/Git blob SHA-1/URL 固定在 `runner.lock.json`，不会接受任意同名缓存文件。

官方 `ArtifactHandler.upload_artifacts` 对目录先调用 `empty_dirs`，再上传，避免覆盖上传保留被删除的哨兵。新任务另提供 `tests/Dockerfile`，由固定版本的 `resolve_verifier_environment_definition` 选择为可信判分镜像；该镜像不预建 `/work/repo`。这些结论来自固定源码，容器行为尚未实测。

## Skill 安装和发现契约

1. 读取真实生成运行的 register 阶段 ID 集合，和已有 `skill_files.json`、canonical ID 集合交叉核验。
2. 每个包逐文件核对原始 `artifact_manifest.json`。拒绝缺失、额外未登记文件、重复 ID、symlink 和不可完整清点的包。
3. 使用 UUID 作目录名复制，不改变任何文件字节。已存在目的目录直接拒绝，阻止静默覆盖。
4. 官方 resolver 对同名目录是 last-wins；本轮以 UUID 避免该覆盖风险，并验证最终 ID 集合。
5. 官方扫描只接受 `root/<dir>/SKILL.md` 深度。运行原方法的真实 find/cat，核对中文 name/description、location 与预期 ID。
6. 只规范 parser 的内存输入。索引只含官方抽取的 name/description/location，额外 frontmatter 字段仍完整留在原文件里。

本地安装、parser 和 XML 索引是已验证层次。容器内安装、初始 prompt 交付、模型主动读取正文和遵循规则分开记录，后三者不能由本地发现探针推断。

## Oracle 与 artifact 契约

隔离仓库中四版本不同。提交由 `hash-object/mktree/commit-tree/update-ref` 构建，禁止外部配置、模板 hooks、签名、filter 与凭证影响初态。目标是 `target.txt`，无关 tracked 文件是 `unrelated.txt`，untracked 哨兵是 `sentinel.txt`。

传输整个仓库目录，保留隐藏 `.git` 和二进制 index。判分读取 worktree SHA/执行位、index v2 的校验和/路径/blob/mode/stage/flags，以及除 index 外全部 `.git` 文件哈希。允许 index 的 stat cache 更新，不以 index 原始字节整体相等代替语义判定。额外提交对象、refs、配置、hooks、无关文件、哨兵及额外文件均触发失败。

可信预期来自受控构建侧，放在 Agent repo 之外；separate verifier 用自身的 `fixture.py` 重建。Agent artifact 只作为待检输入，不执行其中 Git 或脚本。Oracle 有文件类型、大小、总量与 index 边界限制；symlink 实测在当前 Windows 被权限阻断，Linux 路径仍需验证。POSIX worktree mode 也需要容器实测；index mode 已有真实错误例覆盖。

## 扩展与保留清单

- 保留：官方全部代码、旧研究目录、47 份 canonical、来源原文、生成日志、导出结果及六组已有未提交审计资料。
- 复用：统一 CLI、JSON/路径/hash 工具、生成运行定位/注册信息、来源 manifest、现有 runs 目录。
- 新增：一个下游模块、一个任务环境及专用 Oracle、配置、测试、报告和独立运行记录。
- 废弃/删除：无。没有以本轮接入为由删除历史结果或改名迁移。

后续 ConditionalQA/SOPBench 需新增任务数据映射、环境、instruction 和任务专用 Oracle；共用 UUID Skill 安装、官方 Harbor 调度、身份/日志字段及结果汇总。没有提前创建伪适配器。来源及生成方法仍使用现有框架；Clean/Degraded 条件由配置和已有来源协议追踪，当前仅运行 clean。
