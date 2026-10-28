# Capacity006 完整执行报告

完成时间：2026-10-28T13:08:27+08:00（Asia/Shanghai）

**全流程已完成。** 最终生成身份 `e06r002`，正式配对 `e06f003`；NoSkill 与 CleanSkill 均为 1/8，整题均未通过。两臂基础设施正常，可纳入配对统计。

## 正式结果

| 条件 | 原始断言 | 整题通过 | 失败类别 | HTTP 请求 | 已观测输入 / 输出 tokens |
|---|---:|---|---|---:|---:|
| NoSkill1 | 1/8 | 否 | task_failure | 6 | 17971 / 2442 |
| CleanSkill1 | 1/8 | 否 | task_failure | 3 | 37424 / 1826 |

两臂通过的是同一个断言：`test_cl_case[2-case1]`（E6 已满载，应拒绝进入）。其余七项均失败。不存在本次配对中的断言改善或退化；这不是稳定效果估计。

21 项控制核验全部一致，配对审计为 `eligible`；候选程序 SHA 与原始 Verifier 评分绑定均通过。证据：[配对审计](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/capacity006-20261027/pair-audit.md>)、[完整审计 JSON](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/capacity006-20261027/pair-audit.json>)。

## 生成与冻结

使用固定 SkillGenBench 版本 `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d` 的配套 Clean 文档。输入 SHA256 为 `0e5060b3133dcd4b4d0ccf5a1687056b81f3168e6a8503cc4806ceae5f3460d2`。公开原文与本地文本只存在 CRLF/LF 换行差异，未加入私有增补。

Anything2Skill：1 份文档 → 89 个窗口 → 133 条支持证据 / 133 个草稿 → 133 个编译规范 → 66 个最终注册并冻结的 Skill。模型请求名为 `deepseek-flash`，下游为 `openai/gpt-5.4-mini-2026-03-17`。没有人工补写、挑选或改动最终 Skill。

通用 `verify` 原样保留为 `PARTIAL`：它按单批次检查四阶段和空初始库，并将编译稿直接与注册后的正文/证据比较。恢复链及 4 项上游注册合并使这些检查不适用。补充核验检查了所有父批次哈希、累计计数、真实四阶段请求，以及全部 66 个活动注册表正文、版本和证据，结果为 `PASS`；没有通过改写 Skill 消除差异。

证据：[父链和最终注册表核验](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/capacity006-20261027/lineage-verification.json>)、[原通用 PARTIAL 记录](<D:/AS/AutoSkill-main/degradation_failure_lab/results/exports/e06r002/verification.json>)、[冻结清单](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/skill-freezes/e06r002/skill_freeze.json>)、[66 个冻结 Skill 目录](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/e06f003/skills.md>)。

## Skill 是否被加载和读取

| 条件 | 安装 | 成功请求含索引 | 实际文件读取 | 完整正文进入成功请求 |
|---|---:|---:|---:|---:|
| NoSkill1 | 0 | 0 | 0 | 0 |
| CleanSkill1 | 66 | 66 | 3 | 2 |

CleanSkill 实际读取的三个 Skill：

- [容量削减事件下的边容量与准入判定](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/capacity_aware_edge_admission_controller_006/e06f003/skills/15dc5310-2210-53f1-a5fe-b75dd3ad5173/SKILL.md>)：完整正文已进入成功模型请求。
- [信号相位通行准入校验](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/capacity_aware_edge_admission_controller_006/e06f003/skills/17677650-7bed-5e92-9636-10946f5ad5ba/SKILL.md>)：有文件读取，但未证实完整正文交付。
- [信号相位激活判定](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/capacity_aware_edge_admission_controller_006/e06f003/skills/7c827cd0-f8c6-5eed-8530-349ad41c6fc5/SKILL.md>)：完整正文已进入成功模型请求。

因此，本例不是“66 个 Skill 没安装或只有索引而从未读正文”。读取与交付仍不能证明实际遵循规则。

## 观察到的失败断点

下表仅统计标识符的大小写不敏感精确出现次数对应的产物数，不等同于语义完备性或因果证明。

| 标识符 | 源窗口 | 支持证据 | 草稿 | 编译规范 | 冻结包 |
|---|---:|---:|---:|---:|---:|
| E1 | 6 | 8 | 2 | 2 | 0 |
| E2 | 12 | 17 | 11 | 11 | 2 |
| E4 | 2 | 2 | 0 | 0 | 0 |
| E6 | 2 | 2 | 0 | 0 | 0 |
| E9 | 14 | 11 | 6 | 6 | 5 |
| E20 | 5 | 7 | 0 | 0 | 0 |

E4、E6、E20 标识符在支持证据中存在，但未进入草稿；E1 在草稿和规范中出现，注册后未出现在冻结包。E9 容量例子则仍在最终包中，并且本次有一份包含该例子的正文完整交付给模型。

NoSkill 将所有边的 `baseline_capacity` 写成 1，并用缺少依据的信号逻辑代替固定相位表。见 [NoSkill 导出代码](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/capacity_aware_edge_admission_controller_006/e06f003/trials/audit-noskill1/submission-export/agent_output.py:45>)。

CleanSkill 新增了题目未提供的 `edge_definitions`、`edge_to_downstream`、`signal_nodes` 输入字段；缺少它们时，以当前占用或 0 代替基础容量，并跳过信号门控。见 [额外输入字段](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/capacity_aware_edge_admission_controller_006/e06f003/trials/audit-cleanskill1/submission-export/agent_output.py:13>)、[容量回退](<D:/AS/AutoSkill-main/degradation_failure_lab/runs/eval/sgb/capacity_aware_edge_admission_controller_006/e06f003/trials/audit-cleanskill1/submission-export/agent_output.py:28>)。它也没有将已交付 E9 示例中的固定容量写入实际默认地图。

可以观察到两段断点：上游任务所需静态绑定保留不完整；下游代码又依赖契约外输入并采用错误回退。没有补齐文档/Skill 的干预对照，因此不裁定哪一项是唯一或主要因果来源。

证据：[逐阶段标识符追踪](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/capacity006-20261027/edge-preservation.json>)、[读取与评分分析](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/analyses/e06f003/analysis.json>)。

## 预算、恢复及预检

| 生成身份 | 状态 | HTTP 尝试 | 已观测 tokens |
|---|---|---:|---:|
| e06g001 | FAILED | 4 | 15068 |
| e06g002 | FAILED | 99 | 438636 |
| e06r001 | FAILED | 311 | 1047072 |
| e06r002 | COMPLETED | 89 | 173585 |

生成合计 503 次尝试、1,674,361 个已观测 tokens，低于最终批准的 800 次 / 2.5M 观测 token 阈值。4 次失败尝试的服务端送达或计费未知，未虚构费用。下游合计 9/12 次请求，没有根据成绩重跑。缓存 tokens 属于输入 tokens 的子集，未重复加总。

`e06g001` 因 TLS EOF 失败；`e06g002`、`e06r001` 分别在旧观测阈值处停止。恢复保留所有原始批次和累计消耗，复用完成窗口、编译结果及缓存分类；未完成窗口的两次已知调用重放已明确记录。

`e06f001` 初次探针遇到分页生命周期故障，修复后预检通过。`e06f001` 和 `e06f002` 均因另一聊天修改共享代码而在模型调用前被拦截，二者未启动、HTTP 为 0，账本保留。协调停写后，新身份 `e06f003` 通过预检并完成唯一正式配对。

工程修改仅涉及精确恢复授权及累计预算检查、额度中止的检查点验证、受控分页探针生命周期、对应配置和回归。原 A2S 上游、源文、已有生成正文和原始任务断言未改。针对性代码回归共 64 项通过：恢复 21 项、授权/预算 9 项、Linux 观察/导出/使用证据 34 项。没有声称全仓测试全部通过。

原始八项测试未覆盖全部 21 条边、结束 tick 边界或非整数容量取整。源文部分信号列表与边端点还有不一致；本次已发布八例的结果不能外推为完整仿真器正确性。

## 正式队列

仅更新 Capacity006 的实际生成/配对绑定为 `e06r002 / e06f003`，保留失败结果并纳入统计。当前正式队列已完成 5/10 组配对。[正式汇总快照](<D:/AS/AutoSkill-main/degradation_failure_lab/results/sgb/audits/capacity006-20261027/cohort-after-e06f003/summary.json>)。

本轮只建立一次 Clean 基线，不包含文档退化、结果修复、重复试验或稳定因果效应估计。
