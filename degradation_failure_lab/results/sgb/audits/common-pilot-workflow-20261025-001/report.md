# 公共Skill实验工作流与使用记录

结论：本轮代码修改完成，保持现有目录职责分层。80项相关回归测试通过；最终配置驱动入口在真实隔离容器中完成零模型验收。本轮模型请求为0。

## 代码结构

- scripts/sgb/pilot.py：统一命令解析与运行时入口，支持register、plan、freeze、prepare、run、status、analyze。
- scripts/sgb/Invoke-Pilot.ps1：复用既有DPAPI加载器，仅run阶段加载已保存凭据。
- scripts/sgb/scrapy041.py：缩减为兼容包装，旧prepare/run命令仍有入口，工作流逻辑不再复制。
- downstream_eval/sgb/pilot.py：公共实验编排、任务配置绑定、只读状态和结果分析。
- downstream_eval/integration/skill_freeze.py：公共冻结器。校验真实生成及完整续跑链，读取最终实时活动注册表，核对版本/来源、复制原字节并生成清单。
- downstream_eval/integration/skill_probe.py：从已有041实现抽取的零模型正文分页可读性检查。
- downstream_eval/integration/skill_usage.py：纯日志分析，不初始化模型或Agent，区分安装、发现、索引提供、文件访问、完整正文上下文及行为使用。
- downstream_eval/sgb/runner.py：增加自动保存outcomes/<条件>/skill_usage.json，并在结果中附上状态、数量和行为使用判定。
- configs/tasks/sgb/scrapy-task-041.json：041任务/case/适配器/固定运行时/profile/正负例映射。
- configs/downstream_runtime.json：全项目共用的控制容器、项目挂载路径、Python入口。
- tests/test_skill_usage.py、test_skill_freeze.py、test_pilot_workflow.py：公共能力回归。
- README追加公共入口说明，原有README字节保持不变。

没有重写Anything2Skill生成算法、Harbor Agent循环或官方Oracle。任务特殊提交和评分仍放在task_adapters目录。task_contract.py既有离线夹具证明范围不扩大。

## 加载/使用证据

每个Skill分别记录：
1. installed与discovered：实际安装和框架发现。
2. index_in_successful_model_request：名称、描述、路径进入成功模型请求。
3. model_file_access_observed：正式模型执行期间观察到文件访问。
4. full_body_in_successful_model_request：完整冻结正文与成功模型请求匹配；比较忽略终端空白和ANSI，文件原字节另由哈希核对。
5. behavioral_use：UNKNOWN。读过、上下文包含或任务通过均不直接证明依据该规则执行。
6. controlled_probe_file_access_observed：零模型控制读取，与正式模型读取分开。

缺失日志保持未知；counts只数已确认true的项。未确认完整正文不等于没有收到片段，当前不自动判定分段覆盖是否构成完整正文。后续需要规则-动作层面的人工/任务专有审查，不能伪造used=true。

旧s41d001已回填到独立分析目录results/sgb/analyses/s41d001。CleanSkill结论为INDEX_ONLY_OBSERVED：安装45、发现45、索引入成功请求45、正文文件访问0、完整正文上下文0、行为使用UNKNOWN。原有outcomes、分数、账本和原观察日志不改写。

## 冻结与任务环境

之前已有041专用冻结函数，本轮抽取成公共freeze_generation；以后使用统一freeze或prepare，不再每任务重新写冻结脚本。最终实时注册表为版本/来源权威，避免使用跨文档更新前的陈旧汇总快照。活动ID与导出ID不一致时明确失败并要求核验，不静默丢弃技能。当前支持已有文档生成registry格式，不宣称能自动识别任意第三方SkillBank布局。

prepare统一完成原始技能冻结、两组staging、profile、原生配置、一致性检查、镜像核对、真实零模型预检、执行清单及独立账本。run复用已有任务适配器和公共runner，拒绝旧ID重启。status --watch读取账本；analyze生成独立报告和可浏览的skills.md。

配置运行时后，基础Agent镜像、工具、网络隔离、安装/观测/预算等公共机制可复用。任务指令、提交接口、依赖版本和Oracle对象语义仍须依据官方资产接入并固定；新任务不保证只改任务名就能运行。需要实现或复用verify_assets、execution_config、configure、native_trial、grade_export、paid_batch任务钩子，并提供runtime.lock和正负例，注册后做零模型验收。

register只声明配置绑定，不声称真实任务已通过。全数据集静态完整性校验在注册时执行；日常加载核对注册表哈希、所选任务的11份官方资产和4份源文档及manifest，避免反复校验其他186个任务。新增任务的源文档与目标规则之间的语义依赖仍需研究审计，不能由文件名或自动评分替代。

## 冻结Skill在哪里看

本次实际部署的45个技能原文：
runs/eval/sgb/scrapy-task-041/s41d001/skills/<UUID>/SKILL.md

版本/来源：
runs/eval/sgb/scrapy-task-041/s41d001/skills_manifest.json

冻结文件哈希：
runs/eval/sgb/scrapy-task-041/s41d001/skill_freeze.json

按名称浏览并点开正文：
results/sgb/analyses/s41d001/skills.md

逐Skill加载/使用证据：
results/sgb/analyses/s41d001/CleanSkill1-skill-usage.json

公共freeze验证复制出的45份正文与本次历史冻结原文一致，未人工修复质量缺陷。

## 验证与历史保护

- 最终80项Linux回归通过，证据all-tests-final.log；其中包含新用例：缺失证据不作未读、索引不冒充正文、失败HTTP不作送达、控制读取不计模型读取、正文截断、源/输出篡改、旧ID保护、所选源验证、误触发HTTP阻断等。
- Windows流程测试11项通过，证据workflow-tests-final.log。
- 公共冻结器对真实s41r003冻结45个Skill，保留合并后0.1.1版本及跨文档来源。
- 最终真实容器零模型验收：runs/eval/sgb/scrapy-task-041/workflow-check-20261025-002/readiness.json为PASS，两组均停在模型请求前；正文安装/索引/分页可读性和独立Oracle正负例通过。
- 验证用账本两个arm均NEW、HTTP尝试0；本轮未启动真实Agent推理或付费试点。验证目录用于工程验收，后续正式实验采用新ID并重新prepare。
- 原s41d001仍只有4次请求；两次本轮准备验收均0次。
- 2124份既有历史文件哈希全部不变。仅041任务注册行新增pilot_config绑定，其他任务行逐字节不变。
- 旧公共源码已保存在本目录before快照。历史执行清单保留当时哈希，不为适配新代码而改写；不能用旧readiness重启历史实验。
- 当前为本地未提交变更；没有提交、推送或自动接入其他任务。

完整命令及配置说明见README的“公共 Skill 实验入口（配置一次，重复使用）”。
