
# B0 Smoke Test

## 结论

真实官方 B0 链路已跑通，状态为 `completed`，错误数为 0。该结果只证明连接和落盘链路可工作，不属于论文结果、正式 Pilot 数据或 H1 证据。

## 运行配置

- 固定解释器：`D:\anoconda1\envs\autoskill\python.exe`
- 入口：`python -m AutoSkill4Doc build`
- LLM：`dashscope / qwen-plus`
- Embedding：`dashscope / text-embedding-v4`
- 输入：`runs/smoke-b0-stage0/input/smoke.md`
- 隔离 store：`runs/smoke-b0-stage0/artifact_store`
- 凭据值：未记录。

## 结果

- 完成文档：1
- ingest window：1
- support：1
- draft：1
- 最终活动 Skill：1，名称 `CSV Duplicate Row Removal`
- intermediate run：`20260927T212656_0f72acc1`
- intermediate 状态：`completed`
- 中间清单文件：11
- store 文件：49
- 可见子 Skill：1
- 结构化错误：0

官方流水线完成 ingest、extract、compile 和 register，并生成 runtime registry、staging、visible tree 以及最终 `SKILL.md`。控制台捕获中的中文路径存在显示编码问题，磁盘上的中文目录名完整。

## Evidence

- `runs/smoke-b0-stage0/run_manifest.json`
- `runs/smoke-b0-stage0/stdout.log`
- `runs/smoke-b0-stage0/stderr.log`
- `runs/smoke-b0-stage0/artifact_store/Users/docskill/csv-duplicate-row-removal/SKILL.md`

Token、费用和模型内部重试没有由当前官方输出提供，标记为 `unobserved`。
