
# B0 Adapter 契约（设计稿，无实现代码）

B0 adapter 是研究控制层。它只调用现有官方 `autoskill4doc` CLI 或公开 Python API，不复制或修改官方源码、prompt、抽取逻辑、`SkillSpec`、store 行为和候选选择。

## 输入

当前 document、独立 `run_id`、隔离输出目录、官方 CLI/API 参数，以及已脱敏的 provider/model/embedding 配置。API key 只能来自进程环境或受控 secret store，不写入 manifest。

## 调用边界

首选公开 CLI：`python -m AutoSkill4Doc build --file <document> --store-path <isolated-store> ...`。若使用 Python API，只调用公开 pipeline 构建与 `build` 入口，不重排或替换内部阶段。

## 保存内容

输入副本及 SHA-256、代码与配置冻结 ID、脱敏参数、prompt 来源文件及哈希、window/chunk 摘要、官方中间产物、最终 Skill、时间、token、费用、重试、终止原因和失败阶段。接口未返回的信息记为 `unobserved`。

## Run manifest 最小字段

`run_id, method_id, workflow_id, document_id, document_hash, repo_commit, b0_freeze_id, provider, model, embeddings_provider, embeddings_model, sanitized_argv, config_hash, prompt_file_hashes, started_at, ended_at, status, failure_stage, retry_count, token_usage, cost, official_artifacts, final_skill_paths`

## 禁止行为

不得读取 verifier 反馈后重生成，不得按任务成绩选最佳候选，不得人工补规则，不得让不同 generation 共享 SkillBank，不得把 mock 运行登记为真实 B0 成功。
