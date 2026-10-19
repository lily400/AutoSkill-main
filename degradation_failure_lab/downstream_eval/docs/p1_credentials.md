# 智增增凭据：Windows 当前用户 DPAPI

凭据按“当前进程 `ZHIZENGZENG_API_KEY` → 当前 Windows 用户的 DPAPI 文件 → 隐藏输入并加密保存”的顺序加载。无需安装依赖，不设置 Windows 用户级或机器级明文环境变量。

加密文件位于 `%LOCALAPPDATA%\AutoSkill\credentials\zhizengzeng.dpapi`，不在项目或 Git 仓库内。目录和文件禁用权限继承，仅允许当前用户 SID 完全控制；读取前核验权限和所有者。文件损坏、权限异常或无法解密时停止，不静默重新输入。DPAPI 绑定当前 Windows 用户及其 Windows 环境，不提供跨用户/跨机器迁移。

## 首次设置或更新 Key（不会发起请求）

在本机 PowerShell 中执行，隐藏输入一把新生成的 Key；不要在命令行、聊天或日志中粘贴 Key：

```powershell
& 'D:\AS\AutoSkill-main\degradation_failure_lab\downstream_eval\integration\Test-P1Connectivity.ps1' -SetCredential
```

`-SetCredential` 总是要求安全输入，不从已有环境变量复制密钥。之后，同一 Windows 用户打开新 PowerShell 即可自动读取。若进程已有 `ZHIZENGZENG_API_KEY`，它优先于加密文件；更新后如需立即使用保存的新 Key，请打开一个未设置旧变量的新窗口。

## 零请求检查

```powershell
& 'D:\AS\AutoSkill-main\degradation_failure_lab\downstream_eval\integration\Test-P1Connectivity.ps1' -CheckOnly
```

不带参数也是该模式。检查凭据能否在 Windows 加载，以及控制容器是否意外持久化密钥；不把真实凭据传入容器，不调用 API，不覆盖历史连通性报告。两种凭据来源都不存在时才隐藏输入并保存。

## 后续单条命令启动已批准的实验

凭据自动加载不代表批准模型调用。必须先取得对应 Trial 的付费批准，并由调用者单独设置 `P1_ALLOW_PAID=1`；脚本从不设置该门禁。随后，指定已有零模型准备产生的一个 TrialConfig：

```powershell
& 'D:\AS\AutoSkill-main\degradation_failure_lab\downstream_eval\integration\Test-P1Connectivity.ps1' -TrialConfig '/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/<已准备的p1运行ID>/configs/A1.json'
```

将占位符替换为已经核验的真实运行 ID；不要直接复用旧的 OpenAI 配置 `p1-ready-008`。可选 A0、A1、Gold，每次仅转发一个指定配置给原有 `harbor trials start --config`，不生成配置、不循环三组、不创建另一套 Runner。模型、预算、独立 verifier 和官方实现均保持原样。现有 `p1_observer.py` 继续在每次模型调用前检查门禁。

只有实际启动请求/Trial 的 `docker exec` 子进程才通过 `--env ZHIZENGZENG_API_KEY` 接收密钥；参数仅含变量名。子进程结束后恢复 Windows 原进程变量，释放安全字符串缓冲；不向任务容器额外注入密钥，不写 Dockerfile、镜像或配置文件。

## 再次测试模型连通性（必须另获批准，本次未运行）

```powershell
& 'D:\AS\AutoSkill-main\degradation_failure_lab\downstream_eval\integration\Test-P1Connectivity.ps1' -SendOnce -RunId 'p1-connectivity-<另行批准的新ID>'
```

仍使用现有固定模型与端点、16 Token 上限、零重试和持久化单次请求锁。历史请求锁不删除、不复用。仅有 Key 或执行 `-SetCredential`/`-CheckOnly` 都不会发请求。

## 假密钥回归

```powershell
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File 'D:\AS\AutoSkill-main\degradation_failure_lab\tests\Test-ZhizengzengCredential.ps1'
```

测试使用独立临时目录，绝不覆盖生产凭据；仅执行假密钥容器比对。所有发送请求/启动 Trial 的分支均使用 Docker 桩测试，不连接模型。Windows PowerShell 5.1 和 PowerShell 7 分别实测 31 项断言通过，真实模型请求均为 0。
