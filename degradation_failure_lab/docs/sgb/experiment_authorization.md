# SGB 逐实验下游授权

适用于 `downstream_eval.sgb.task_adapters.audited.json_task` 注册的 SGB JSON 任务。

`authorize_downstream.py --approve` 会创建：

```text
data/manifests/sgb/downstream_authorizations/<task_id>/<experiment_id>.json
```

记录绑定 task、generator、experiment、任务配置 SHA-256、NoSkill/CleanSkill 条件、每组 6 次与全局 12 次 HTTP 上限。创建前仍检查注册任务、生成授权、真实生成结果及固定协议。不修改共享 generation gate 的历史 `downstream` 字段。

同一记录只能创建一次：同内容重复授权保持原字节，不匹配则拒绝。已 prepare 或已启动但没有新式记录的旧实验不能事后补授权，请使用新 ID。其他历史实验的 `batch.started` 不阻挡新 ID；目标实验自己的保护仍有效。

prepare 在任何模型/容器预检之前要求精确授权，把原始授权字节复制为实验内的 `authorization.json`，在 profile 记录来源和 SHA-256；原记录、副本及授权实现均进入执行冻结清单与新账本。run 在准入前校验这份绑定；复制其他实验的授权、修改 HTTP 上限、改动原记录或冻结副本都会拒绝。

注册、授权、prepare 都不允许重置旧账本。请求预算仍是每组 6 次、全局 12 次，`num_retries=0`；UNKNOWN、halt、一次性 batch 标记及 Trial lease 的逻辑不变。

旧共享源码已在 `docs/sgb/authorization_upgrade_20261027/source-before/` 按原相对路径保存，SHA-256 在相邻 `source_manifest.json` 中。旧实验目录、旧 gate、旧 execution_manifest 和旧账本均不改写。旧 manifest 对共享源码路径的校验会因源码升级产生差异；可用保存的原字节核验历史版本，不能据此重新运行旧实验。

## Monitoring001 / m01f004

以下脚本只授权并 prepare，使用已完成的 `m01g001`，不会调用模型：

```powershell
Set-Location -LiteralPath 'D:\AS\AutoSkill-main\degradation_failure_lab'

python -B .\scripts\sgb\authorize_downstream.py `
  --task monitoring_gap_brief_classifier_001 `
  --generator-run m01g001 `
  --experiment m01f004 `
  --approve
if ($LASTEXITCODE -ne 0) { throw '授权失败；停止，不进入 prepare。' }

& .\scripts\sgb\Invoke-Pilot.ps1 `
  -Phase prepare `
  -Task monitoring_gap_brief_classifier_001 `
  -GeneratorRun m01g001 `
  -Experiment m01f004
if ($LASTEXITCODE -ne 0) { throw 'prepare 失败；保留记录，不执行 run。' }
```

prepare 成功后，若决定执行付费实验，再单独执行下面命令。它通过现有凭据加载器运行，不需要手填密钥；本次改造不执行此命令：

```powershell
& .\scripts\sgb\Invoke-Pilot.ps1 `
  -Phase run `
  -Task monitoring_gap_brief_classifier_001 `
  -Experiment m01f004
if ($LASTEXITCODE -ne 0) { throw '实验已停止；保留账本和日志，不重试同一 ID。' }
```
