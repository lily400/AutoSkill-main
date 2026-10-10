# degradation_failure_lab — P0.1 多案例实验框架

研究文档退化如何影响官方 Anything2Skill 的提取、编译与最终技能质量。
只包装官方 API，不修改官方源码、算法、提示词或编译机制。当前正式案例仅
`case001_qsv_select`；本轮没有新增付费模型调用、真实退化输入或来源数据规模。

P0 的真实 Clean 基线仍成立：成功运行 `p0_qsv_select_clean_002` 有两个正式程序技能，
失败尝试 `001` 完整保留。工程验证与内容质量分开，不能以 SKILL.md 存在代替内容正确。
实际验收见 [P0.1 报告](reports/P0_1/P0_1_report.md)，原判断见 [原始质量报告](reports/quality_review.md)。

## 环境与公开入口

- Python：`D:\anoconda1\envs\autoskill\python.exe`，只需标准库。
- 官方源码：`D:\Baseline-anthing2skill\AutoSkill-main\AutoSkill-main`。
- 路径配置：`configs/environment.json`；可用 `ANYTHING2SKILL_SOURCE` 环境变量覆盖源码路径。
- 生成配置：`configs/generation/deepseek_flash.json`；模型与服务来自配置，不在核心代码中写死。
- 当前已审计的观察路径支持官方 `openai` 兼容客户端及本地 `hashing` embedding；
  不宣称已经支持 Anthropic、GLM 私有协议或远程 embedding 的调用统计。
- 密钥仅取配置指定的环境变量，当前为 `DEEPSEEK_API_KEY`。不读取上游 `.env`。
- 公共入口 `scripts/lab.py`，无需每个案例复制 Python 脚本。

```powershell
Set-Location 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab'
$py = 'D:\anoconda1\envs\autoskill\python.exe'
& $py -B scripts\lab.py list
& $py -B scripts\lab.py validate
& $py -B scripts\lab.py plan --case case001_qsv_select --condition clean --repeat 1
& $py -B scripts\lab.py verify --run p0_qsv_select_clean_002 --out results\exports\p0_qsv_select_clean_002
& $py -B scripts\lab.py verify --run p0_qsv_select_clean_001 --out results\exports\p0_qsv_select_clean_001
# 失败的历史生成会返回 1，这是实际失败状态，不是重构回归。
& $py -B scripts\lab.py aggregate --out results\aggregates\current
& $py -B -m unittest discover -s tests -v
```

以下命令会调用真实模型，本轮没有执行：

```powershell
& $py -B scripts\lab.py run --case case001_qsv_select --condition clean --repeat 1
```

`plan` 校验全部输入并输出计划，不建立运行、不访问网络。
`run` 在完整批次预检后顺序执行，每次独立 SkillBank；默认 run_id 为时间戳加 UUID。
`--run-id` 仅允许单次运行且全项目不能重复；已有运行拒绝覆盖。
`--case` 可接收多个案例；省略 `--condition` 时使用案例定义中的全部条件。
`scripts/run_clean.py` 是 case001/clean 的旧便利入口，真实调用转到公共 runner；
旧 `--config/--manifest` 单案例生成接口已退出使用，改用 case.json 的配置/输入引用。
`scripts/verify_run.py --run <旧运行路径>` 仍可用，改为写入外部 results/exports，保持历史文件不变。
P0 专用 `prepare_sources.py/audit_extra.py/test_upstream.py` 保留为历史工具；新增案例不复制它们。

## 五层身份与引用

| 层 | 身份与位置 | 引用 |
|---|---|---|
| Dataset / Source | dataset_id；全局唯一 source_id；data/catalog.json 注册清单 | 原文路径、完整 commit、许可证、SHA-256 |
| Case | 全局 case_id；cases/<case_id>/case.json | dataset_id、source_ids、共享配置 |
| Condition | condition_id 在案例内唯一；conditions.json | 已物化输入清单、operator 名称与参数 |
| Run | 全局唯一 run_id | case_id、condition_id、输入/配置快照、独立 SkillBank |
| Evaluation | evaluation_id 在运行内唯一；records 各有 record_id | rule_id、多个 skill_id、来源及阶段证据 |

rule_id 在案例内唯一，完整规则身份为 `(case_id, rule_id)`；保留 P0 的 R1–R7。
condition 的完整身份为 `(case_id, condition_id)`。skill_id 使用官方 UUID，
window/support/draft/spec 的 ID 分别使用官方字段，不能与案例或运行 ID 混用。
一个 Source 可被多个 Case 引用；一个 Case 可含多份 Source；每个 Condition 必须列出所有来源的输入。

每案例三份定义：`case.json`、`rules.json`、`conditions.json`，以及每条件一份 `inputs/*.json`。
公开 JSON Schema 位于 `schemas/`；`src/degradation_lab/schema.py` 对其使用的关键词严格验证，
额外检查引用、ID 重复、原文/输入哈希、证据行号与路径越界。不依赖 jsonschema 包。
Clean 输入须与原文同哈希，operator=null。Degraded 输入须不同于原文，并记录算子身份与参数；
框架只读已准备的输入，不实现或执行任何退化算子，也不自动证明退化强度符合参数。

规则清单只用于评价，不作为生成输入。未来增添新来源须先保存未经修改的固定版本文件，
按 `source.schema.json` 新建清单并加入 data/catalog.json；来源类别不得伪称论文快照。
已有 qsv 来源仍是 RECONSTRUCTED_OFFICIAL_SOURCE；检查表仍是 CUSTOM_TEST_DATA。

## 运行、证据与评价

新路径：`runs/<case_id>/<condition_id>/<run_id>/`。运行保存原始输入字节副本、父级来源清单、
案例/条件/规则/配置快照、环境路径、包装层源码快照、官方代码前后哈希、状态与异常。
官方产物保留在 `SkillBank/.runtime/`，注册/丢弃/真实合并决策按官方结果原样保存。
HTTP 观察只记录正文和调用栈，不记录授权头；成功响应原样传回官方客户端。
费用接口未提供时 cost=null，不制造估算。预算按请求前检查，单次响应可能越过 token 阈值。

外部导出位于 `results/exports/<run_id>/`：所有候选 Draft/Support/Spec、注册结果、
来源→窗口→Support→Draft→Spec→正式 SKILL.md 路径和输入行对齐。
未注册的 Spec 明确 registered=false；导航与程序技能分别统计。
上游 span 使用标准化文本坐标，导出的行号是输入文件精确行匹配；
未来退化输入的行号不会被假称为原始 Clean 文档行号。

评价位于 `evaluations/<case_id>/<condition_id>/<run_id>/<evaluation_id>.json`。
status 为 unreviewed/correct/incorrect/uncertain，method 为 manual/automatic。
可记录多规则、多技能映射、阶段实体、生成行号及错误类型；自动检查不能授予语义正确。
`rule_preservation` 与 `generated_addition` 分开，避免 R4 原规则正确被新增错误覆盖。
多次审核保留独立 evaluation_id，不自动压成一个成功率。

```powershell
& $py -B scripts\lab.py evaluation-init --run <真实运行ID> --evaluation-id review001
# 编辑新增 JSON 中的审核记录；原始生成技能不修改。
& $py -B scripts\lab.py evaluation-validate --file evaluations\<case>\<condition>\<run>\review001.json
& $py -B scripts\lab.py aggregate --case <case_id> --out results\aggregates\<摘要名称>
```

## 历史兼容与 Git 保存

旧目录 `p0_qsv_select_clean_001/002` 没有搬迁、重生成、覆盖或改写。
`runs/legacy_index.json` 仅将它们关联到 case001/clean。
P0 没有运行内原文副本，原来的全局来源、实际请求、TextUnit 和中间阶段均保留。

审计发现本轮开始前 Windows Git 检出已将原文及 5 份 wrapper_snapshot 文件转换成 CRLF，
原 Git blob 仍精确匹配 P0 清单。`data/legacy_bytes/` 独立保存这 6 份原字节，
`data/legacy_byte_index.json` 记录当时工作区哈希、Git commit 与恢复哈希；
只允许验证已证明的换行差异，后续实质变化仍失败。原文件完全不改动。
新 case001 输入引用 `qsv_select_canonical.json` 的恢复原文；来源身份、版本和哈希不变。
`.gitattributes` 对新增 raw_sources、condition_inputs、legacy_bytes 和 runs/case*/ 设置 -text，
保护以后检出的字节；不改变旧 P0 路径的 Git 文本属性，避免把整份历史误列为修改。
未来新原文建议保存到 data/raw_sources/<repository>/<commit>/，清单引用真实相对路径即可。

两次 P0 完整历史继续保留在 Git。本轮新增定义、评价、代码和审计报告可提交。
新 `runs/case*/` 完整大产物与可再导出的 results/exports、results/aggregates 默认忽略，
轻量 results/run_index.jsonl、人工评价和精选报告可跟踪。重要实验应显式将完整目录
及 artifact_manifest 归档到持久存储，或显式 git add -f 所选运行；不存在自动无限提交或自动删除。
本轮没有提交 Git 或删除旧记录。旧上游 tests 的 7 项失败保留原日志，未冒充新回归。

## 增加 case002：三种条件，各三次

完整文件与实际命令示例见 [case002 操作说明](reports/P0_1/case002_example.md)。
该说明没有向正式注册表添加 case002，没有创建真实退化文档，也没有运行九次模型。
当前测试中的 case002 仅存在于临时目录，全部标记 fixture，汇总默认排除。

下一阶段最小入口是：先建立一个有来源和固定哈希的退化输入与 conditions 定义，
通过 validate/plan，再按相同公共配置执行一对新的 clean/degraded run 并进行规则级审核。
本轮在框架验收后停止。
