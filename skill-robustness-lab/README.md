# 文档退化技能生成实验工程 v4

当前阶段：数据规范化与官方生成环境预检查。论文判断：**当前不可投稿**。本工程尚无真实DashScope生成或生成技能执行结果。离线参考实现结果不能作为模型表现。

本轮严格依次完成论文审查、数据规范、工程修改。详见 `docs/01_论文可行性审查.md`、`docs/02_统一数据规范.md`、`docs/03_工程交付与实验边界.md`。机器可读字段在 `schemas`，逐文件作用与代码定位在 `docs/04_实现证据.md`，全部目录在 `docs/目录树.txt`。

## Windows 从零运行

使用用户确认的环境，全部核心校验依赖Python标准库，不需要安装python-dotenv。

```powershell
Set-Location 'D:\Baseline-anthing2skill\AutoSkill-main\skill-robustness-lab'
$Py = 'D:\anoconda1\envs\autoskill\python.exe'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'

# 完整离线检查，包括两个官方CLI预检查，不读取密钥、不调用模型。
& $Py -B '.\scripts\check_offline.py' --preflight
if ($LASTEXITCODE -ne 0) { throw 'Offline verification failed' }

# 仅参考实现/判题器开发回归。每次真实本地运行产生新的execution与judgment。
& $Py -B '.\scripts\execution_tools.py' reference --case case001
& $Py -B '.\scripts\validate_results.py'
```

压缩包含本次实际离线检查记录。已有封存记录不要修改，也不应为了清爽删除失败记录。preflight的kind是preflight，不能作正式clean基线。

## 真实生成 命令已提供但本次未执行

`configs/environment.json`保存官方目录、Python可执行文件和`.env`路径；`.env`只读取`DASHSCOPE_API_KEY`，不复制内容。也可在本机环境变量配置同名key。`python_executable`亦接受环境目录并解析为其中的python.exe。

```powershell
& $Py -B '.\scripts\run_case.py' --case case001 --method chunk --repeat-id 1
# 另一个官方窗口设置，应完整单列比较。
& $Py -B '.\scripts\run_case.py' --case case001 --method strict --repeat-id 1
```

生成输出会显示`RUN_DIR`。保存实际请求、响应、服务端model/usage（如返回）、官方分阶段产物、日志、代码/环境快照及seal。没有偷偷修复或替代官方失败；官方Python文件不修改。`structural_pass`仅检查结构和产物，`semantic_status=pending`，`execution_status=not_run`。

有真实且审核通过的退化文档后，先将clean与全部计划变体一起纳入新的数据发布版并冻结，再运行clean与degraded。不要在已有clean运行之后编辑当前seal添加变体。下列占位符不是项目中存在的数据：

```powershell
& $Py -B '.\scripts\run_case.py' --case case001 --method chunk --variant-id '<已登记并审核的variant_id>' --baseline-run '<真实clean生成run_id>' --repeat-id 1
& $Py -B '.\scripts\compare_runs.py' '<真实clean生成run_id>' '<真实degraded生成run_id>'
& $Py -B '.\scripts\audit_run.py' '<真实生成run_id>'
```

clean生成失败仍可作为完整总体的配对一侧；preflight、错误来源、不同repeat/方法/代码/环境/标准或被篡改的run会拒绝。比较器只判断配对资格，不计算尚未产生的任务成功率。

## 执行接口

```powershell
& $Py -B '.\scripts\execution_tools.py' plan --run '<真实生成run_id>' --task 'case001-v2.example'
```

这只创建用户明确请求的`not_run`执行计划。通用Agent执行器尚未实现；不运行模型生成的任意脚本。后续执行器须在受控环境内仅获得task输入、冻结技能和工具；judge在另一个控制过程读取`standards`。单纯目录隔离不是OS沙箱。

## 数据与冻结

- 真实研究输入仅case001的clean开发样例；source原字节不变。11个原fixture迁移为11个独立task，全部development。
- `standards`存规则和预期答案，`runs`存生成证据，`executions`存真实执行，`judgments`存独立判题。不要向执行器暴露工程根、archive、日志、代码快照或标准。
- `catalog/freeze.json`封存完整固定数据和judge/reference代码；已冻结数据的缺失、新增、修改都报错。`validate_data.py --freeze`已有seal时只核验，不能重封存篡改。
- 新来源、标准修订或退化集合需要新的发布目录/版本、重新分组审核和新seal。保留旧目录、旧seal及其run；在新发布中修改真实材料、明确升级相关ID，再由数据负责人核验后首次冻结。不要在本版直接删seal“解锁”。
- `pending`是未审核，`not_run`是未执行，`null`是未获得值；都不是失败或0分。
- `archive/original_v3`保存收到的17个原文件用于追溯，不属于当前注册数据，旧脚本不要执行。

## 已通过与未通过的边界

已通过：44项离线测试、1案例/1来源/1开发族/1clean变体/11task结构校验、参考实现11/11开发fixture、chunk和strict官方导入与帮助预检查、证据封存核验。测试中的合成错误仅存在临时目录，不计入研究样本。

待真实运行：DashScope凭据/网络/模型响应、完整官方生成、实际上下文与截断归因、技能语义、生成技能执行、无技能/参考技能对照、退化损失、方法改善、置信区间。没有B1/B2/B3生成器、训练模块或已验证双路径。
