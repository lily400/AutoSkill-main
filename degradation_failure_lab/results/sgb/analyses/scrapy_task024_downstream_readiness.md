# Scrapy Task-024 下游校准就绪报告

2026-10-23。**GO：工程接入完成，由用户启动真实 NoSkill/CleanSkill 校准。** 本轮真实模型 API 请求0次，真实模型任务运行0次；仅原生Harbor初始化、模型前停止探针、确定性正负夹具和假SDK传输测试。无正式退化实验。

## 1. 生成集合与冻结

实际来源：runs/case024_scrapy/clean/s24r005，exit_code=0，official status=completed。完整汇总为19个草稿、19个编译规格、15个注册/upsert技能；日志中的 skills=2 是局部暂存分组，不能视为全部产物。

SkillBank共有32个SKILL.md物理文件，其中15个是Users/docskill下的canonical程序包，其余为可见树副本及导航。安装集合严格取完整注册ID集合对应的全部15个canonical包；不重复安装视图/导航，不根据任务成绩挑选。每个canonical包实际只有SKILL.md，没有被遗漏的附属资源。

冻结根目录：runs/downstream/scrapy-task-024/s24d001。原包、冻结包、Harbor远端安装包的文件集合及SHA-256一致。完整原始文件路径、32个物理文件清单、包版本见 [skills_manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/runs/downstream/scrapy-task-024/s24d001/skills_manifest.json)。六次执行使用staged/NoSkill（空）或staged/CleanSkill（15包）。

| Skill | ID | 版本 | SKILL.md SHA-256 |
| --- | --- | --- | --- |
| Feed URI 动态参数注入 | 090a1758-18b6-52ae-b493-2519ea84762f | 0.1.0 | 42164497fe1b33bc58fcb99f0bcc2dc33ea3c553adb0503faec6f0c4f2c1abb9 |
| Feed 存储 URI 参数替换 | 100c7e33-dfd6-594b-929c-0a53ce77829e | 0.1.0 | 8ad000282197708dad39874d4e316344277ecbcb1140415cb0d24a9a17c90c61 |
| Feed 导出配置解析与回退 | 1ed8b5f3-d142-54b2-86a1-a18ac23b8fd9 | 0.1.0 | dee2a0a976085266947841720895ee99b65cc81829e8427099580588ad567c85 |
| Feed 导出压缩配置 | 22a119a0-0339-5040-bae2-b8b592879f9b | 0.1.0 | 79740f635a4a76ed87369a0ad404b97a6ca76e0647c287b1eef2abf7ad4ed21a |
| 本地文件系统 Feed 导出配置 | 27330983-d562-5773-89a1-69b722b401e1 | 0.1.0 | 70ec8e153ce49dd0152be0811079ff52598cf90d6315024fae8d5e39a3464662 |
| Feed 覆盖与追加策略选择 | 341bd0da-1d52-5a40-87dd-44477cdec422 | 0.1.0 | dfc87aee5d5de706a535ea5c02943e675f9331bf63698be127efb2eacfd65023 |
| 配置 FTP Feed 存储 | 34248732-50cd-510d-b3ed-a71e8ef808d1 | 0.1.0 | 1aa931b4be772891895f2654c1e8cd32b56661987cbdf6edc53b1a4ed25ce226 |
| 延迟文件交付时序处理 | 38bbf62a-9897-54df-bebe-1f4fee96a11c | 0.1.0 | d5eb93d9d0db0f394e1ef158cd701e034fb2db9765f591575e191557fce61fe4 |
| Scrapy S3 Feed 存储后端配置 | 3c445cfa-3f7b-50b1-b612-d9b3a9b462c0 | 0.1.0 | 4747d2bca63fa1d6b8cae85ab59c4709205c54d2f7d1a77fcd2fd7d6661c35a9 |
| Feed 存储 URI 参数化配置 | 7c6e4142-008c-527e-97cd-842ef4911d30 | 0.1.0 | 4c9aa7d53f2702f82745db6d210264a2197aeef506b8695eb52a037c0ed57693 |
| CSV 导出列字段控制 | 8cc3ce38-d0f7-54a5-9546-2056a0d42430 | 0.1.0 | 805994ca623ed893c1b9354f360c0ca0ae79735934c0d6d686c29770baa5231e |
| Feed 导出设置项参考 | 8cd10359-1f17-575a-aaf7-6dbcd9da0c79 | 0.1.0 | 48c66d333331db9324616ae5da79e36dd1c85c919e672a01178cf44d472c5a98 |
| 自定义 Feed 导出器扩展 | 945ee694-0375-5f27-a671-6805bddfe600 | 0.1.0 | 4a1a0f38c3d8a2beeb2f5882d225c08e704efcd8a9b1fd796019ccf9a5b15443 |
| 标准输出Feed导出 | d376a347-de32-572a-8a60-797627eb09ca | 0.1.0 | 299a8db767a6b6a4767600cb28df76447cc738cb81effefc95878856a66e6057 |
| 批量输出文件命名占位符配置 | e71e8e20-3578-5a41-a437-402eaeb0d5f6 | 0.1.0 | 6120b57fd85e8b59f67c1bb3a278517d38fb095760e033fbe8c3ba762e4941cf |

来源核验：注册provenance均指向唯一文档746b8660-57be-5a86-bc5c-fdd89bdae86d；s24r005恢复自s24m005，恢复种子中无最终Skill。该集合属于这一生成链，未从共享历史SkillBank导入。生成 artifact_manifest.json SHA-256=c1c05f7e9b6f18ca701b1576a5b120aef71a47c1cc39759a6576efcdad9a9275；冻结 execution_manifest.json SHA-256=7d0f2a35c2102acf5b9f68361fca61f1462b08a22a6d86f74acbdb823d001efa，覆盖975项代码、配置及资产。原始运行未修改。

SGB源身份5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d；Clean源SHA-256=a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d。A2S基准94c47ca488d4ba4117d20272e66d49b9877e68cf；沿用此前预处理修复及外部scrapy身份。此方法版本必须记录，不能冒充未改预处理的纯官方基线。本轮不再修改生成算法、提示词或Skill。

## 2. FTP目标规则的实际表达

- 341bd0da-1d52-5a40-87dd-44477cdec422「Feed 覆盖与追加策略选择」的canonical正文第33、63行明确写FTP默认True（覆盖）；第34、73、77行保留部分FTP服务器不支持APPE的条件，且与S3/GCS限制分开。
- 1ed8b5f3-d142-54b2-86a1-a18ac23b8fd9「Feed 导出配置解析与回退」第57行也有FTP True。
- 显式FTP overwrite=False对应追加，没有在同一候选中逐字完整说明；通用“采用显式配置”与APPE说明提供部分支持，不能据此声称全部规则保真已通过。
- 同一集合还存在其他后端描述风险，例如解析与回退包第70行把标准输出也列为“不支持追加”，与其他位置冲突；S3包存在可能诱导错误覆盖默认的措辞。全部保留，未人工修补。
- 原Task-024只判定默认overwrite返回值，不检验显式False或APPE服务器行为。任务19/19不能替代完整源规则保真评价。

## 3. 真实任务资产接入

实际预检来源为C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-15/scrapy024_preflight，原包及历史报告保持不变。D盘此前没有此任务；新增唯一执行入口downstream_eval/tasks/scrapy_task024_v1，复用冻结资产的便携子集，不另造Agent循环或Oracle。

- instruction.md按原字节复制，SHA-256=d349a7822e667628c4535ae278fc70b4e40c8831654516e7f11e737349cdee7c。
- 原eval.py SHA-256=dbde11a8dce8a699101792be3b48e85a672e91a0cdc6cc4de32862cffeeb3918；19项断言、期望值及判定逻辑保持字节不变。
- 复用原preflight.py的score_submission、worker/interface、oracle_bridge及离线pytest依赖；复制原始正确/FTP反转夹具。
- 已审查原harbor_entry.py；其输出被限制在原C盘包内，因此本接入使用Harbor原生artifact导出，再调用同一个score_submission控制端函数，结果统一留在D盘新运行目录。
- Task TOML保留原任务字段，只增加固定Agent运行镜像；Agent模型循环是固定Harbor的Terminus-2。复用CompatibleTerminus2、copy_packages和P1正文观察器，新增任务隔离检查与独立六任务预算。
- Harbor原生verifier在Trial配置中明确禁用；评分在Agent结束、容器停止后，由控制端独立调用原预检的两容器桥接评分。不能把这一成绩称为未经适配的官方Runner原生成绩。

## 4. 隔离与无模型验收

Harbor0.24.0，固定提交2de4605b9404eada7d341388291e6e469c90330b；LiteLLM=1.93.0，OpenAI SDK=2.24.0，httpx=0.28.1。复用已有Linux控制容器及依赖；Windows本机缺Harbor不构成本运行阻断。控制容器不是Agent任务容器，Docker socket和凭据只在可信控制端使用。

Agent镜像固定为sha256:c928e232c35008c42b22727ecd2fe39ed79fe9cb36ebddca669daef309d6b4e4。复用已有工具层并清除旧/work、/workspace；无Scrapy安装。Task容器只具有自己的日志/产物挂载，未挂审计目录、源文档、隐藏测试、答案、expected或Docker socket。docs为空，原任务指令仍保留其文档路径提示，但两条件均不提供DirectDoc；允许的信息差异只有完整Skill处理条件。预训练知识无法静态隔离，后续NoSkill校准测量其影响。

运行时核对Harbor no-network策略、侧车deny-all规则、实际mounts、镜像ID、源/Oracle不可见、零Scrapy和安装前后哈希。Agent结束后再次核对Skill哈希。评分候选容器只读提交和执行桥；只有独立可信评分容器持有Oracle与expected响应。

|验收|实际结果|证据|
| --- | --- | --- |
|7项新增单元/SDK假传输测试|7/7，真实网络被封锁|engineering/unit_tests.log、unit_tests.json|
|原生Harbor NoSkill探针|模型前停止；0安装包；0模型HTTP|engineering/attempt-001/NoSkill1/report.json|
|原生Harbor CleanSkill探针|15/15安装、发现、哈希和受控整正文曝光；0模型HTTP|engineering/attempt-001/CleanSkill1/report.json|
|正确夹具独立Oracle|19/19；FTP断言通过|NoSkill1/oracle/result.json|
|FTP反转夹具独立Oracle|18/19；唯一失败test_supported_backends[ftp://server/export.json-True]|CleanSkill1/oracle/result.json|
|两个条件公平性|模型、环境、权限、预算等规范化哈希一致|fairness.json|
|长期GPT凭据加载入口|DPAPI CheckOnly可用；0网络鉴权请求|既有Invoke-ProjectCredential.ps1|
|真实Agent读取/遵循/任务表现|NOT_RUN|不能从探针推出|

这里的NoSkill1/CleanSkill1工程探针由控制端在Agent模型前停止后注入确定性正负实现，只验证任务链路，**不是两个真实对照成绩**。既有23项合同及旧Windows正负测试未重跑；新增覆盖不累计为30项独立研究证据。

首次移植出现非root评分容器不能写新建JUnit输出目录的问题，原失败记录保留在probes/及probe-trials/。只在外部Docker适配器中对新建/results输出目录设可写权限，未改Oracle、预检原文件或候选提交；后续attempt-001两臂通过。

## 5. 六次真实运行命令

在已打开Docker Desktop的PowerShell中：

~~~powershell
cd D:\AS\AutoSkill-main\degradation_failure_lab
docker start harbor-p0-control-20261018
& .\scripts\Invoke-Scrapy024Calibration.ps1 -Experiment s24d001
~~~

这条命令使用已保存的DPAPI凭据，仅授权子进程的SCRAPY024_ALLOW_PAID；不在命令、JSON或日志写入密钥。按NoSkill1、CleanSkill1、NoSkill2、CleanSkill2、NoSkill3、CleanSkill3顺序串行运行。准确原生Trial配置在configs/<label>.json，全部已冻结。不会调用Anything2Skill、再次生成Skill、进入退化条件或追加Agent运行。

只做冻结核验的命令为：

~~~powershell
python -B scripts/scrapy024.py prepare --experiment s24d001
~~~

## 6. 预算、日志和停止条件

- 共6次Agent任务，每任务最多6次模型HTTP，总上限36次；成功、超时、传输失败及投递未知尝试都不退还额度。
- 同一模型openai/gpt-5.4-mini-2026-03-17，端点https://api.zhizengzeng.com/v1；temperature=0、reasoning_effort=none。
- 输入估计预留上限每请求20,000、每任务累计100,000；六任务合计最多600,000预留。每请求输出最多2048，六任务请求输出上限合计73,728。
- Token预留是本地估计控制，实际provider usage独立记录；不能把估计数当实际账单。
- 账户单价和实际人民币费用未知。以上是HTTP/Token限额，**没有可承诺的人民币金额硬上限**；本轮没有消费。当前命令由用户决定是否启动。
- 复用持久化Ledger及MeteredTransport，新增独立预算数据库，不借用旧Git额度。Ledger通用化时保留旧默认3臂/18次设置，新Scrapy显式声明6任务/36次。
- SDK和外层自动重试均关闭，重定向禁用；一次性batch.started与数据库租约禁止重复执行。环境、传输、预算或评分环境错误立即停止；普通任务错误与候选加载错误单列，不因答错而改Skill或增加尝试。
- outcomes/<label>/result.json记录任务成功、任务级19项及FTP专项结果、失败类别、Token、未知usage次数、工具次数和耗时；trials/保留原生轨迹、提交及P1观察日志；batch_results.json和budget.sqlite3给出累计记录。
- 整正文曝光采用保守标准：内核读取事件，加上冻结正文完整进入成功模型HTTP请求的messages。仅名称发现、文件存在、cat工具日志或probe成功都不算真实正文曝光。部分正文阅读仍保留原始轨迹，不能将“未满足整正文标准”直接等同“从未读过任何正文”。正文曝光也不证明遵循，需结合提交和Oracle解释。

## 7. 当前阻断与唯一下一步

**无已知工程阻断；唯一待办是用户运行上述固定六任务命令。** 当前模型端点连通性、账户额度与服务端实际行为未通过付费请求验证；首个请求异常即按实际类型停止，不自动重试。真实Clean/NoSkill结果仍待采集，3次/条件只是初步校准，不能声称统计显著性或正式退化实验准入。

最终预算状态：6个任务均NEW，真实模型预留次数0。官方生成源码、s24m005/s24r005历史记录、原始任务和Oracle未改动。工程GO不等于Agent任务成功。
