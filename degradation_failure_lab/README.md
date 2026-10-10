# degradation_failure_lab — Stage P0

本项目固定 Anything2Skill 的真实文档→技能流程，为后续 Clean/Degraded 配对实验提供工程基线。本阶段只使用一份 qsv 官方 `select.md`；未实现退化算子、下游基准或新提取算法。

**验收：PASS（工程流程及证据链）。** 成功运行是 `runs/p0_qsv_select_clean_002/`，生成两个独立程序技能。内容并非全部合格，详见 `reports/quality_review.md`。第一次真实尝试因模型推理预算不兼容而在注册阶段失败，完整保留于 `runs/p0_qsv_select_clean_001/`。

## 固定来源与运行环境

- 官方源码：`D:\Baseline-anthing2skill\AutoSkill-main\AutoSkill-main`。
- 实验项目：`D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab`，与源码目录平级。
- Python：`D:\anoconda1\envs\autoskill\python.exe`，3.10.21；生成路径只依赖标准库，无需安装 requests、PyYAML、dotenv 或供应商 SDK。
- 本地父仓库提交：`19b660299c557431044cc07788c6232d1deb2f99`；对应已核对的上游提交：`94c47ca488d4ba4117d20272e66d49b9877e68cf`。本地现存 169 个上游文件与该提交字节一致，164 个生成代码/测试/包配置文件另有运行前后 SHA-256 清单。
- qsv 提交：`257ae7b38738688138dc430c2ccb4eef8766f3fc`；原路径 `docs/help/select.md`；MIT 许可证。
- 数据类别：**RECONSTRUCTED_OFFICIAL_SOURCE**。没有证据证明这是论文原始快照。原文含有指向 master 的链接，因要求保存原始字节而未改写；本实验只读取已固定的单份文件，不沿这些链接获取输入。
- 实际服务：DeepSeek；模型请求与响应标识 `deepseek-flash`；SDK 的适配器名称是 `openai`，不代表调用了 OpenAI 服务。
- 向量表示：上游内置 `hashing`，256 维；不是语义 embedding 服务，也不是 mock LLM。该选择是当前 P0 配置，不是声称复现论文模型/embedding 设置。

## 使用

所有命令在 PowerShell 中执行。密钥只从环境变量 `DEEPSEEK_API_KEY` 读取。不要写进配置、脚本、命令参数或报告。本项目不读取源码目录中的 `.env`。

```powershell
Set-Location 'D:\Baseline-anthing2skill\AutoSkill-main\degradation_failure_lab'
& 'D:\anoconda1\envs\autoskill\python.exe' -B scripts\prepare_sources.py
& 'D:\anoconda1\envs\autoskill\python.exe' -B scripts\audit_extra.py
& 'D:\anoconda1\envs\autoskill\python.exe' -B -m unittest discover -s tests -v

# 付费真实调用：不指定 run-id 时自动建立新目录；不会续接旧 SkillBank。
& 'D:\anoconda1\envs\autoskill\python.exe' -B scripts\run_clean.py --config configs\clean_qsv_select_non_thinking.json

# 对已经完成的本次成功运行进行只读检查与导出，不调用模型。
& 'D:\anoconda1\envs\autoskill\python.exe' -B scripts\verify_run.py --run runs\p0_qsv_select_clean_002

# 在字节一致的临时源码副本内运行原有测试，避免测试的默认缓存写回源码目录。
& 'D:\anoconda1\envs\autoskill\python.exe' -B scripts\test_upstream.py
```

`run_clean.py --manifest <清单路径>` 预留另一份输入清单的接口；清单须标记 `variant: clean` 或 `degraded`，提供输入路径、来源 ID 和实际哈希。本轮仅运行 clean，不提供退化算子。配对实验须保持代码、模型配置和预算相同，使用两个全新 SkillBank，并额外记录退化来源关联。

## 模型兼容包装的边界

上游注册阶段固定使用 256-token 决策预算，层级判断另有 128-token 预算。DeepSeek 默认推理模式使第一轮某些请求耗尽预算而无正文。

成功配置通过上游正式支持的 `connector_factory` 接口调用 `provider_adapter:build`。这个 25 行左右的适配器继承官方 `OpenAIChatLLM`，只向官方构造的请求增加 `thinking: {type: disabled}`。提示词、输入文档、temperature、各阶段 token 上限、解析器、重试、编译器、注册和写库逻辑均由上游执行。单元测试逐字段验证唯一差异为 thinking 参数。HTTP 观察包装原样转交请求并原样返回官方客户端的响应，相关摘要和调用栈保存在运行目录。

## 目录

```text
degradation_failure_lab/
├─ README.md
├─ .gitignore
├─ configs/                         # 第一轮及成功的非推理配置，均无密钥
├─ data/
│  ├─ sources/qsv/<commit>/          # 原始 select.md、LICENSE-MIT、Cargo.toml
│  └─ manifests/                    # 来源、哈希与独立规则检查表
├─ scripts/                         # 来源获取、官方 API 包装、导出验证、测试隔离
├─ tests/test_wrapper.py
├─ runs/
│  ├─ p0_qsv_select_clean_001/       # 失败尝试，提取/编译完成，注册失败
│  └─ p0_qsv_select_clean_002/       # 成功运行及完整中间表示
└─ reports/
   ├─ P0_report.md                  # 实际工程审计与验收
   ├─ quality_review.md             # 规则覆盖与不受来源支持的内容
   ├─ audit/                        # 固定官方树、分支、数据入口、环境、版本比较
   ├─ upstream_tests*.log           # 上游 153 测试 / 7 失败
   ├─ wrapper_tests.log             # 包装层测试
   └─ upstream_test_side_effect/    # 已从上游移除的本次测试缓存的归档
```

成功运行内：`http/` 保存请求正文、响应和调用栈；`SkillBank/.runtime/intermediate_runs/` 保存官方各阶段快照；`SkillBank/.runtime/document_registry/` 保存注册与来源记录；`SkillBank/.runtime/staging/` 保存分组暂存；`SkillBank/Users/docskill/` 保存两个正式技能；中文可见树另含两个技能副本及两个导航技能。`exports/` 只复制和关联已有结构，不重新生成技能。

复现含义是重新执行同一官方路径并可核对输入、参数和产物。远程模型别名和采样结果可能变化，不能承诺 SKILL.md 字节一致。本轮没有复现论文成功率，也没有运行 qsv 命令来证明技能可执行性。
