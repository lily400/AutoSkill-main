# P1 容器内单次模型连通性检查（2026-10-19）

**结果：FAIL，HTTP 401 AuthenticationError。** 固定控制容器完成一次实际模型请求，未返回 API_OK、模型标识或 Token usage。后续重复执行已由单次锁拦截，没有第二次模型请求；不能把之前 PowerShell 成功时的 16 token 填为本次用量。本次实际费用未报告，不能记成零费用。

## 配置与实际请求

当前 `p1_smoke.json` 入场时已是智增增地址和 `ZHIZENGZENG_API_KEY`，本轮保持这两个设置。配置没有写入密钥。

- Harbor 模型名：`openai/gpt-5.4-mini-2026-03-17`；实际发送的 model 去掉 LiteLLM 的 `openai/` 路由前缀，为 `gpt-5.4-mini-2026-03-17`。
- base_url：`https://api.zhizengzeng.com/v1`；Chat Completions 路径 `/chat/completions`；格式 `openai_chat_completions`。
- 消息：`Reply only API_OK`；temperature=0、reasoning_effort=none；最小测试将输出上限降至 16 token，单请求超时 45 秒。
- 使用固定 Harbor 的 LiteLLM 官方方法函数体，关闭外层 Tenacity 重试；SDK max_retries=0，并在发送边界限制一次。`request.started` 排他创建后不删除、不覆盖。

你提供的成功 PowerShell 附件确认同一模型/端点，并使用 `Authorization = Bearer $env:ZHIZENGZENG_API_KEY`。附件没有包含完整可独立复现的成功请求体，因此不能宣称所有原始参数逐项一致。本次请求参数与所提供 P1 配置一致，仅按最小测试要求降低输出上限。

## 凭据安全与离线对照

由于 Codex 进程、Windows 用户/机器级环境和控制容器均无密钥，由用户在本地 PowerShell 执行安全脚本。若原进程已有环境变量就直接复用；否则以 Read-Host -AsSecureString 隐藏输入，仅临时设置进程变量。Docker 通过 `--env ZHIZENGZENG_API_KEY` 继承环境，不在 argv 中写入值。结束后恢复原进程变量并释放安全输入缓冲；不将密钥注入任务容器。

模型调用不启用请求内容/认证头调试日志；捕获异常只保存类型和 HTTP 状态。服务端任意回复不会直接落盘，只允许固定 API_OK。当前控制进程未残留密钥，`P1_ALLOW_PAID` 仍未设置，配置授权仍为 AWAITING_USER_APPROVAL。没有启动 Terminus-2、A0/A1/Gold 或生成任务。

成功请求使用已有环境变量，后来的执行进入了重新输入分支。不能仅凭提示符变化确认是否同一窗口；两次密钥值尚未建立相同证据；HTTP 401 不能单独证明原成功密钥失效。没有保存失败时的密钥或摘要，因此不能事后比较那个输入。`-CheckOnly` 可从原成功窗口做带随机盐的同值比较，只输出布尔值，不输出/保存密钥或摘要，不调用模型，不解除单次锁。

离线对照状态：{"credential_present": true, "container_matches_source": true, "new_model_requests": 0, "P1_ALLOW_PAID_changed": false, "saved_authorization_header_matches_env": true}

## 版本、测试与已知环境差异

Harbor 0.24.0、LiteLLM 1.93.0、OpenAI SDK 2.24.0。Harbor 提交 `2de4605b9404eada7d341388291e6e469c90330b`、uv.lock SHA-256 与原锁一致，92 个已安装包版本全部匹配冻结锁。六项连通性离线测试通过，包括真实模块入口、HTTP 前参数转换、凭据显式传递、零重试及重复锁阻断；既有下游回归 12/12 通过。

当前控制镜像 tag 与锁相同，但实际 ID 为 `sha256:8326adaa60a40c4dac1aa2f86daa9593d6c0e682cb49da565cc3919d0459c5ec`，不同于历史锁中的 `sha256:4a1b0a3e10c5f0c9637aec69bdab3fd53640b19ef5f2009a712bd941430715e6`；旧 ID 已不在本机。未擅自修改锁或重建 Runner。正式 P1 前需审查并恢复/重新冻结这一环境差异；它目前不是已证实的 401 原因。

第一次本地 launcher 因缺少 src 导入路径在请求前停止，未发送；已增加同入口的无密钥预检并修复。之后发生一次已落盘 401。再次执行看到 FileExistsError 是单次锁生效；现在预检会在提示密钥前返回 ALREADY_ATTEMPTED，避免重复输入。Windows 原生 asyncio 单测进程曾卡住并被中止；正式离线结果来自固定 Linux 控制环境。

## 第三方价格核查

[智增增官方价格说明](https://doc.zhizengzeng.com/doc-3979947) 的表头明确是官方参考价，并说明国外模型另有约 5% 费用、区分开发版和企业版，还给出充值 100 到上游 95 的示例。公开规则已查到，但本账户具体费率、费用如何叠加、充值汇率和账单未核验。

原配置的 0.75 / 0.075 / 4.5 USD 每百万输入/缓存输入/输出 token 现仅保留在 reference_price_usd_per_million_tokens。实际 price_usd_per_million_tokens 与 pricing_verified_date 改为 null，并明确标注账户费率未核实；原预算 0.446184 USD 是 OpenAI 参考计算，不能当作第三方实际费用。既有准备和观测代码已能处理未知费用，避免给出错误的实际预算或因空费率崩溃。Token/时限预算与付费授权门禁未改。

## 执行命令与结果

从本机原 PowerShell 执行过（密钥不在命令里）：

```powershell
& 'D:\AS\AutoSkill-main\degradation_failure_lab\downstream_eval\integration\Test-P1Connectivity.ps1'
```

脚本最终实际模型调用：

```powershell
docker exec --env ZHIZENGZENG_API_KEY harbor-p0-control-20261018 python -B -m downstream_eval.integration.model_connectivity --run-id p1-connectivity-20261019-001 --send-once
```

调用一次：HTTP 401；result.json 的 request_attempts=1；returned_model、usage、actual_billed_cost 均未知。不要重跑该命令，也不要删除请求锁。

零请求验证：

```powershell
docker exec harbor-p0-control-20261018 python -B -m unittest discover -s tests -p test_model_connectivity.py -v
docker exec harbor-p0-control-20261018 python -B -m unittest discover -s tests -p test_downstream.py -v
& 'D:\AS\AutoSkill-main\degradation_failure_lab\downstream_eval\integration\Test-P1Connectivity.ps1' -CheckOnly
```

前两条已通过；最后一条是否已执行以 credential-check.json 为准。合成随机值的 CheckOnly 自检在独立 fixture 中通过，不冒充真实凭据或模型调用证据。

## 剩余阻断与下一步

1. 鉴权未通过。先在原成功窗口做 -CheckOnly，检查保存的 Authorization 是否匹配该窗口当前环境变量，以及容器是否收到相同值。通过只能证明传递一致，不能把 401 自动改判成成功。
2. 一个实际请求名额已用完。若需重测，必须由用户明确允许新增一次请求；本轮不自动重试、不删除锁、不切换模型/端点尝试。
3. 第三方账户实际价格、控制镜像 ID 差异尚待核实；旧 p1-ready-008 三组配置仍是历史 OpenAI 配置，不能直接作为智增增实验配置复用。
4. 连通性通过后，还需以当前供应商设置重新冻结并仅做零模型校验，再获得 Gold 人工确认及三组付费授权。当前只授权本次最小连通性请求。

结果和原始安全日志：`D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/git-restore-explicit-source-both-v1/p1-connectivity-20261019-001`。核心文件 result.json、audit.json、pricing-check.json、runtime.stdout.log、测试 stdout/stderr、commands.md。原版 Anything2Skill、canonical SKILL.md 和 runner.lock.json 未修改。
