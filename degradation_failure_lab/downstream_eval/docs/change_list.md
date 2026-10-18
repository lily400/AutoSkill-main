> 后续 Docker 实机验收已完成：见 [2026-10-18 实机报告](docker_validation_2026-10-18.md)。下文保留首次离线阶段记录。

# 本轮逐文件变更清单

以下清单针对真实 Git 工作树。原有未提交研究资料、全部官方文件、冻结来源/Skill/生成结果和旧测试均保留。没有废弃或删除任何历史文件。

| 文件（相对研究主目录） | 原有/新增/修改 | 用途 | 为什么需要 |
|---|---|---|---|
| `downstream_eval/__init__.py` | 新增 | 定义下游模块包 | 将下游代码接到现有 Python 入口 |
| `downstream_eval/README.md` | 新增 | 运行边界、命令和环境恢复步骤 | 区分零模型证据与真实 Agent |
| `downstream_eval/configs/runner.lock.json` | 新增 | 固定 commit、依赖、源码 SHA 和路径 | 防止无审计升级/缓存漂移 |
| `downstream_eval/configs/git_restore_pilot.json` | 新增 | 来源/生成运行/任务/结果目录引用 | 复用冻结来源，不写死机器路径 |
| `downstream_eval/integration/harbor_adapter.py` | 新增 | 环境检查、依赖身份与官方方法探针 | 执行真实官方算法并保留完整安装阻断 |
| `downstream_eval/integration/skill_install.py` | 新增 | 14 Skill 集合、冻结哈希、UUID复制/发现；tar远程契约 | 防覆盖、丢失、资产或换行变化 |
| `downstream_eval/integration/terminus_compat.py` | 新增 | 官方 Terminus2 的内存换行兼容子类 | 兼容 CRLF，保留原文件及官方代码 |
| `downstream_eval/checks.py` | 新增 | 零模型编排、36个状态案例、任务物化和原生probe条件入口 | 统一日志并复用现有入口和 runs |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/fixture.py` | 新增 | 隔离、固定初态和四版本Git构建 | 保证可复现且不碰用户仓库 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/oracle.py` | 新增 | 纯字节/index/ref/副作用判分 | 不信任Agent自报结果和配置 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/instruction.md` | 新增 | 带commit占位符的任务要求 | 提供合法输入且不泄漏命令 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/task.toml` | 新增 | 官方artifact/separate verifier配置 | 复用Harbor原生机制 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/environment/Dockerfile` | 新增 | Agent任务镜像定义 | 构造任务但不放入Oracle |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/tests/Dockerfile` | 新增 | 独立可信verifier镜像 | 避免Agent环境污染及基准残留 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/tests/test.sh` | 新增 | 官方verifier执行入口 | 按Harbor奖励契约输出 |
| `downstream_eval/tasks/git_restore_explicit_source_both_v1/tests/verify.py` | 新增 | 重建可信预期、判分和reward落盘 | 预期独立于Agent artifact |
| `downstream_eval/docs/architecture.md` | 新增 | 审计树、模块职责和调用链 | 证明落点与复用依据 |
| `downstream_eval/docs/validation_report.md` | 新增 | 实际检查、全哈希、逐断言和阻断 | 不把静态/宿主成功夸大为Agent成功 |
| `downstream_eval/docs/change_list.md` | 新增 | 逐文件变更分类 | 便于逐项审阅 |
| `tests/test_downstream.py` | 新增 | 11项离线测试 | 换行/中文/资产/覆盖/fixture/Oracle/传输/隔离 |
| `src/degradation_lab/cli.py` | 修改 | 添加 downstream-check 子命令 | 保持统一实验入口 |
| `.gitignore` | 修改 | 忽略 .external 和 runs/downstream | 分开依赖/生成产物和研究源码 |
| `.gitattributes` | 修改 | 新容器shell脚本固定LF | 保证Linux脚本入口；既有冻结字节规则不变 |
| `README.md` | 修改 | 增加零模型入口链接 | 让现有实验手册可发现新模块 |

配置使用 JSON，复用现有 JSON I/O，不为示意 YAML 文件额外实现配置系统；未创建空目录/伪适配器或重复 check_skills/check_oracle 脚本。

运行生成的文件：`runs/downstream/.../p0-acceptance-002/` 内的 `result/preflight/skills/oracle/harbor.json`、XML、staged/installed包、逐例repo/可信初态/断言、物化Harbor任务、stdout/stderr/unittest日志、审计/保护性校验、source_manifest/artifact_manifest。各文件来源见目录内清单；均为本轮产物，不复制原始生成运行。

外部依赖：`.external/harbor-2de4605/` 的12个固定官方文件及provenance，`.external/git-a52a24e/t/t2070-restore.sh`。这些是忽略的受控源码子集，不是安装成功记录。每个依赖文件的来源URL、Git blob SHA和SHA-256见版本锁。没有把整个Harbor仓库复制进研究源码。

宿主文档工作区的暂存/部署/报告脚本仅用于本轮操作，未成为研究框架的第二入口。实际可持续入口仍为 scripts/lab.py，回归测试仍使用 unittest。
