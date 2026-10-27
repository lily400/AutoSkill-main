# SGB 逐实验授权机制改造验收

日期：2026-10-27。项目：`D:/AS/AutoSkill-main/degradation_failure_lab`。

改造已安装；没有发送真实模型请求，没有执行付费 run。`m01f004` 仅做了授权预览，尚未创建授权记录或实验目录。

## 结果

- `authorize_downstream.py --approve` 为每个 task/experiment 创建独立、不可覆盖的授权记录：`data/manifests/sgb/downstream_authorizations/<task>/<experiment>.json`。继续检查注册绑定、生成授权、真实生成结果与固定协议；不再改写共享 gate 的历史 downstream 字段。
- 授权严格绑定 task、generator、experiment、任务配置 SHA-256、条件、每组 6 次和全局 12 次 HTTP。重复授权同一匹配记录不改变字节；不匹配则拒绝。
- JSON 任务 prepare 在创建实验输出或调用运行时预检之前检查授权，复制为 `authorization.json`，写入 profile 引用；原记录、副本和实现进入 execution_manifest 与新账本。任务快照固定 UTF-8/LF，保证 Windows 授权、Linux prepare 的哈希一致。
- JSON 任务 run 在 Trial 准入之前核对授权、冻结副本、profile 与 cap；不再根据共享 gate 的历史实验号决定新的下游授权。
- 历史其他实验的 batch.started 不阻挡新 ID；目标实验自身的重复执行和预算重置保护仍在。已 prepare 的旧协议实验不能事后补签授权，应使用新 ID。

## 零模型验证

Linux 控制环境中新增 7 项测试全部通过，覆盖 CLI 预览与独立授权、幂等和拒绝覆盖、严格字段匹配、无授权拒绝 prepare、新授权的 prepare/冻结/空账本创建、运行前篡改阻断，以及 6/6/12 和不可重建账本。

原有相关回归测试执行 61 项，其中 60 项通过。唯一失败是 `test_clean_cohort.ConfiguredJSON.test_exact_generation_gate_blocks_before_credentials`：原测试要求错误文本包含 `execution gate`，当前真实错误为 `BLOCKED: exact generation identity/configuration/budget is not authorized`。已用归档的旧源码复现同一失败；实际拒绝授权正确。这项无关的旧消息断言未修改。

prepare 回归使用真实 prepare 逻辑及临时目录，Docker 镜像检查/工程探针用夹具替代；运行入口的执行端被 mock，不会付费执行。既有预算/runner 测试使用 fake SDK/transport 或临时账本。未执行真实生产 m01f004 prepare，留给提供的 PowerShell 命令。

真实项目只读检查确认：m01f002 重跑被阻止，m01f003 re-prepare 被阻止，两者均不能补签新的逐实验授权；m01f004 授权预览通过。PowerShell 脚本语法检查通过。

## 历史保全

按用户确认，修改共享源码之前保存了 3 份原始文件：`source-before/`。逐文件 SHA-256 见 `source_manifest.json`。旧 experiment 目录、账本、结果、execution_manifest 和共享 gate 没有修改。

共核对 19 个已有实验及共享 gate 的 3,423 个历史文件，全部与改造前哈希一致。m01f002 仍为第三次 UNKNOWN / error_type=BudgetStop，halt=BudgetStop，NoSkill1=STOPPED，CleanSkill1=NEW。

共享源码已升级，所以旧 execution_manifest 对其中 2 个源码路径的直接校验会产生差异；旧文件原字节可在 source-before 中按原 SHA-256 核验。此快照只用于历史核验，不用于恢复旧实验执行。

## 文件

生产代码仅修改 `scripts/sgb/authorize_downstream.py`、`downstream_eval/sgb/pilot.py`、`downstream_eval/sgb/task_adapters/audited/json_task.py`，新增共享授权模块 `downstream_eval/sgb/downstream_authorization.py`。未修改 request_budget、p1_observer、模型设置、Oracle 或 Skill。

新增回归测试：`tests/test_sgb_downstream_authorization.py`。完整命令和机制说明：`docs/sgb/experiment_authorization.md`。可直接执行的授权 + prepare 脚本：`scripts/sgb/m01f004_authorize_prepare.ps1`；脚本不包含付费 run。

结构化验证记录见 `validation.json`。本次没有修复此前审计提到的传输异常诊断覆盖问题；这不属于本次授权改造。
