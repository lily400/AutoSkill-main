# 从零开始的多案例实验目录（v3）

此目录没有历史运行结果。runs、reports、comparisons 最初为空，只有你执行命令后才产生内容。
官方路径仍为 D:\Baseline-anthing2skill\AutoSkill-main\AutoSkill-main。
本目录路径为 D:\Baseline-anthing2skill\AutoSkill-main\skill-robustness-lab。

## 手动复制

先把现有 skill-robustness-lab 改名为 skill-robustness-lab_old（重名则另起备份名），保留备份。
在原位置新建 skill-robustness-lab，然后把本目录全部内容复制进去。不要合并旧 runs、reports、comparisons，
也不要复制旧顶层 data、evaluation、tests、configs/run_one*.json。旧 tests 依赖历史运行，本清爽版不附带它们。
官方源码目录无需移动或修改。密钥仍从原官方目录的 .env 只读获取。

## 目录职责

| 路径 | 用途 |
|---|---|
| configs/environment.json | 只保存本机框架、Python、凭据文件路径 |
| configs/methods/chunk.json | 通用chunk生成参数，供所有案例选择 |
| configs/methods/strict.json | 通用strict生成参数，供单独的方法对照 |
| cases/case001/case.json | 案例身份、任务名称、文件路径、冻结哈希 |
| cases/case001/clean/source.md | CSV开发样例的干净输入文档 |
| cases/case001/evaluation/contract.json | 人工整理的13项原文核对标准，属于测试设计 |
| cases/case001/evaluation/fixtures.json | 人工整理的11个开发测试输入及期望输出，未执行 |
| cases/case001/degradation/variants/ | 未来退化文档，初始为空 |
| cases/case001/degradation/recipes/ | 未来退化来源、参数、seed、编辑位置，初始为空 |
| scripts/ | 8个通用Python文件，见下面说明 |
| runs/ | 每次独立运行证据；初始为空 |
| reports/ | 审计报告；初始为空 |
| comparisons/ | 干净/退化配对报告；初始为空 |

每个案例的路径和哈希都写在其 case.json 中。case001 的 ready 只表示输入设计已冻结，绝不代表
技能生成成功、语义正确或任务执行通过。contract 与 fixtures 都是根据 source.md 设计的检查材料，
不是已经运行得到的结果；生成时只把 source.md 传给官方CLI。

## 代码文件

- run_case.py：你使用的入口。合并环境配置、方法参数和指定案例，不混用案例文件。
- run_one.py：内部执行引擎，负责官方调用、快照、状态和封存。不要直接运行它。
- official_entry.py：安装记录器，再运行未修改的官方 AutoSkill4Doc 模块。
- trace_http.py：记录实际DashScope聊天/嵌入请求响应，脱敏已知密钥。只支持已核查的非流式JSON接口。
- evidence.py：共享的哈希、封存和生成结构核对函数。
- audit_run.py：只读核查一个run，另写reports。
- compare_runs.py：校验干净/退化配对；没有执行结果时分数保持null。
- case_tools.py：创建新案例草稿、冻结输入设计；不会调用模型或生成技能。

## 第一次运行

PowerShell先进入目录，之后所有命令都在此目录执行：

```powershell
Set-Location 'D:\Baseline-anthing2skill\AutoSkill-main\skill-robustness-lab'
& 'D:\anoconda1\python.exe' -B '.\scripts\run_case.py' --case case001 --method chunk --preflight-only
& 'D:\anoconda1\python.exe' -B '.\scripts\run_case.py' --case case001 --method chunk
```

第一条Python命令只做环境检查；它也会新建一个run，status明确为preflight_only，official和trace没有模型产物。
第二条才调用真实模型并生成技能。两次run不同是正常的，每个run的case_ref.json和status.json都会说明来源。
程序运行过程中会打印RUN_DIR，完整进度保存在logs/build.log。缺凭据、失败或超时都保留记录。

chunk与strict是不同方法，不要给干净用chunk、退化用strict后比较。本版本尚未在Windows上真实生成；
实际生成后仍需逐条核对技能正文。现阶段还未实现下游执行器与独立判题，execution/status.json明确not_run。

## 增加case002

```powershell
& 'D:\anoconda1\python.exe' -B '.\scripts\case_tools.py' init case002 --title '你的第二个任务名称'
```

它创建cases/case002同样的目录，case.json状态为draft，原文和评测是待填写模板，没有伪造第二个案例。
自行填写clean/source.md、evaluation/contract.json、evaluation/fixtures.json及case.json中的task信息。
contract.rules中每项包含id和从该文档摘出的source_text；fixtures.cases中每项包含id、input、expect及outputs。
写完以后：

```powershell
& 'D:\anoconda1\python.exe' -B '.\scripts\case_tools.py' freeze case002
& 'D:\anoconda1\python.exe' -B '.\scripts\run_case.py' --case case002 --method chunk --preflight-only
& 'D:\anoconda1\python.exe' -B '.\scripts\run_case.py' --case case002 --method chunk
```

冻结会生成哈希并检查原文摘录存在、规则/测试非空。它不判断测试答案是否正确，需要人工核对。
ready案例不要直接改；修改任务或测试应建立新案例版本，不能篡改旧run或沿用旧基线。

## 运行后才会出现的文件

run目录包含case_ref.json、status.json、checksums.json、input、config、logs、trace、official、evaluation、execution、tmp。
config是运行时快照，含解析后的配置、框架哈希/源码副本、Python包版本、变体、比较指纹和本次实验脚本副本。
official内为完整store/registry及中间产物。新run自动生成audit.json和rule_review_template.json；原文匹配只判输入覆盖，
不自动给语义分数。失败也保留，不能只筛成功运行。

后续运行退化版本时，在该案例degradation/recipes中放配方JSON，再用run_case.py的--variant和--baseline-run。
配方说明见cases/README.md。不同案例共用代码和模型配置，但各自保存输入设计；每个run用case_ref.json关联案例。
