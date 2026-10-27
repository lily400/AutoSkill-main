# Task003 Sanctuary002：真实 Clean 全流程执行报告

本次已完成真实生成恢复链、质量记录、最终 Skill 冻结、真实包原生零模型验收、一对 NoSkill/CleanSkill 执行、独立原 Oracle 评分及差分归因。没有修改 Anything2Skill 核心、Agent 或 Oracle。

| 条件 | 原 Oracle | 整题成功 | HTTP | 输入 token | 输出 token |
|---|---:|---|---:|---:|---:|
| NoSkill1 | 0/8 | false | 6 | 20142 | 1982 |
| CleanSkill1 | 8/8 | true | 3 | 22029 | 1685 |

两组均 infra_ok=true，候选提交绑定通过，原 8 个断言全部完成，errors=skipped=0。账本两组 DONE、总 9/12 HTTP、halt=null。配置公平性及差分审查 eligible；8 项断言均 FAIL→PASS，整题差分 possible_help。每组仅一次，不估计稳定成功率。

## 来源与生成链

- 原 clean 源文 SHA256：7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c。输入只有该文档，无测试/参考实现。
- sn3g001：提取和编译已完成，注册时达到原 450000 token 阈值而停止；94 HTTP、452392 已观测 token，包含一次失败 HTTP。它是上游额度中止，不是普通下游任务失败。
- 用户明确批准门禁持久变更和完整真实执行，并允许必要额度调整。记录保存在 results/sgb/authorizations/；没有伪造批准来源。
- sn3r001：沿现有安全恢复器复用完成阶段和 9 条分类缓存，追加 30 HTTP、61899 token；父子累计 124 HTTP、514291 已观测 token，累计上限调整为 300 HTTP / 1000000 token。未清零计数或覆盖原运行。
- 1 个文档、13 个窗口、35 条支持证据、35 个草稿、35 个编译 spec；最终活动包 21 个 Skill，公共冻结器已校验完整父子链、最终注册版本、来源及逐文件哈希。

通用单运行 verify 的原始状态保留为 PARTIAL：恢复运行继承阶段、SkillBank 非空，且官方注册去重合并改变了一个非目标 Skill 的正文和 support 集合。没有把这些检查强行改成 PASS。详细原检查与最终活动包校验见 generation-lineage-validation.json；下游使用的是未经修改的公共冻结器认可的最终活动包。

## 规则、读取与行为

三条数值规则经来源比对为 correct；额外回合的完整顺时针表达为 uncertain，未排除该样本或修补正文。Reviewer 为 Codex assistant，明确不是独立人工签审。完整记录见 evaluations/case003_san/clean/sn3r001/pre_downstream.json 和 results/sgb/upstream/sn3r001/manual-quality-audit.md。

CleanSkill 在 episode 1 访问两份相关 SKILL.md；相关 4/10/5 片段进入成功请求 2，随后工具动作 3 写出正确的阈值 4 和标记 10/5。NoSkill 实际提交用了 1 和 2/1。上述代码及时间关系是可校验事实。

使用审计状态仍是 FILE_ACCESSED_BODY_CONTEXT_NOT_FULLY_CONFIRMED：安装/索引为 21，文件访问为 2，完整正文进入成功请求的确认数为 0。不能把规则片段的动作前交付升级为全部正文交付、理解或行为依赖。要求正文读取的协议存在观测限制，但不抹去完整执行与有效评分。

差分仅表明该配对中可能帮助。数值规则解释改进属于有机制证据的候选假设；未做受控规则干预或重复运行，不能宣称稳定收益或已验证因果。四条规则均保留源文→窗口→support→draft→spec→registered→skill 的实体与哈希映射，含显式不确定性。

源文/Skill 的洗牌描述比任务 pile_recycled 的 trigger-turn-only 契约更宽；本次 CleanSkill 按任务契约实现且通过。该范围区别保留，不作为源文错误或已证实失败原因。

## 工程验收与保护

真实包原生 prepare 两组 PASS、模型调用 0；模型运行只启动一次配对。NoSkill staged 目录为空，没有本次源文或 Skill。固定镜像、工具权限、同一 runtime-note、模型、原 Oracle 和预算保持可比。

Windows→Linux 审核曾遇到 resource 及快照源码路径问题。使用既有 Linux 控制环境，并复制 166 份同哈希源码建立临时控制侧路径别名；不挂载给 Agent，不改校验函数、源文或历史快照。记录见 controller-source-path-map.json。

历史保护快照中的全部旧文件校验通过，run_index 只追加；冻结执行文件及两次生成的 artifact manifests 均验证通过。既有修改为已授权 gate、本次归因 spec 和 run_index 的追加，另有新恢复配置和新产物。未提交/推送 Git，未构造退化文档。

费用只报告实际请求和观测 token。提供商真实账单未提供；SDK 的参考成本不当作实际支付金额，失败 HTTP 的未观测使用量也不补成零。

## 复核入口

- results/sgb/baselines/sn3e001/baseline.json、baseline.md：框架正式四状态报告。
- results/sgb/analyses/sn3e001/：逐组评分、读取及成本观测。
- results/sgb/attributions/sn3e001-v1/report.json、report.md：配对资格、逐断言差分、14 个哈希绑定证据和候选归因。
- runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/：Skill 冻结、ledger、原生轨迹、提交与原 Oracle。
- final-acceptance.json：最终保护和验收；operator-scripts/：本次操作脚本，均有已存在输出保护，不能用于重启已有试验。

已停止新增调用。后续重复、规则干预或 Degraded 实验另行设计；本次结果不扩展为完整游戏规则或整个 SkillGenBench 的效果估计。

Completed UTC: 2026-10-26T15:57:39.118939+00:00
