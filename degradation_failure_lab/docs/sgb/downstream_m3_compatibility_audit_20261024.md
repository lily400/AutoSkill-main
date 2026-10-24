# SGB 下游目录整理后 M3 整体兼容性审查

日期：2026-10-24。项目：D:\AS\AutoSkill-main。本文相对路径以 degradation_failure_lab/ 为根。

**结论：PASS_WITH_FINDINGS（主要离线入口通过，存在兼容边界与历史重放限制）。**

M2-1/M2-2 的当前文件身份与上轮交付一致。管理 API、BeautifulSoup 新旧导入、reload、任务模块 monkeypatch、带项目搜索路径的旧 smoke 冷启动、Scrapy 到公共 Runner 的分派通过定向验收。不能据此宣布所有加载方式完全兼容，亦不能宣布真实 Agent/运行时通过或三类全部任务已通用化。

本轮仅新增本报告这一交付文件。既有代码、测试、配置、任务资产、历史运行、账本、manifest、锁文件和 .gitattributes 保持只读；不实施下一批迁移，不继续 S0.3。

## 1. 基线、范围与证据分级

### 1.1 本地基线

- 当前分支 master；HEAD：3073a1a1a7119603ccb2ac738fae269a8223c0d9。
- 开始时 Git 状态：18 项既有 tracked 修改、880 项既有 tracked 删除、2,427 个未跟踪文件。它们均先于本轮存在。
- index SHA256：2454cc749f587b0fee24774c9da654cd6ab0219b121b13a4ee457ee5e32acf33；暂存差异为空。
- 原始 porcelain 状态 SHA256：c7cec2ad8db1b5541aa3115e499a21563fd280045cfeb1b6f8e565a9f7e4334a。
- 初始全树扫描：30,130 个普通文件、1,672,399,681 字节、2 个 reparse link。集合摘要 4357f7d1e4c5ee84c7159d700de02f38b56fe95ff0e966e8ea677df312d2b72c。排除各 .git/.idea 目录及本报告路径；HEAD/index 另行核验。
- 目录规划依据：docs/sgb/downstream_directory_reorganization_plan_20261024.md 第 2.2、4.1、9、10 节。没有使用远程旧文件替换候选工作树，也没有 fetch/pull。

### 1.2 分级

- **T：本轮实测**。原始字节/hash、只读解析、受控离线测试或命令实测，需同时注明环境与范围。
- **S：静态判断**。根据当前源码、导入、字符串配置和调用关系推断，未启动相应流程。
- **U：未验证/跳过**。需要本轮禁止的运行时、模型或更大的导入链；不得记作通过。

本轮离线进程使用 -B/sys.dont_write_bytecode，拒绝项目内写入、网络连接、子进程启动和模型/Agent 栈导入；仅允许固定 Harbor 的静态 schema。测试临时夹具在项目外创建并清理，不在真实 runs/results 或预算账本中操作。Windows 沙箱临时目录权限在前轮已确认不适用于这些夹具，因此本轮安全测试通过已批准的沙箱外进程运行，进程内保护保持启用。

## 2. M2 后实际目录与调用关系

### 2.1 当前结构

~~~text
degradation_failure_lab/
├── downstream_eval/
│   ├── sgb/
│   │   ├── __init__.py                 # 两行：说明 + 三个管理函数导出
│   │   ├── management.py               # plan / prepare / aggregate 的真实实现
│   │   ├── runner.py                   # 当前 SGB 批次协调；未迁移
│   │   ├── scrapy024.py                # Scrapy 专属入口；未迁移
│   │   ├── scrapy_agent.py             # Scrapy 专属 Agent；未迁移
│   │   ├── beautifulsoup_agent.py      # 原位保留 OFFLINE_ONLY 拒绝
│   │   ├── beautifulsoup037.py         # adapter 模块别名入口
│   │   ├── beautifulsoup_scoring.py     # scoring 模块别名入口
│   │   ├── beautifulsoup_exports.py     # exports 模块别名入口
│   │   ├── beautifulsoup_smoke.py       # 模块别名 + 旧命令 main 转发
│   │   ├── pydantic001.py              # 原工程 demo；未迁移
│   │   └── task_adapters/
│   │       ├── __init__.py             # 仅说明字符串，无主动导入
│   │       └── beautifulsoup037/
│   │           ├── __init__.py         # 仅说明字符串，无主动导入
│   │           ├── adapter.py          # 来源、配置、离线准备、判分接口
│   │           ├── scoring.py          # 专属提交/证据解析，执行接口仍拒绝
│   │           ├── exports.py          # fixture-only 会话收据
│   │           └── smoke.py            # 静态工程探针
│   ├── integration/                    # 原外部框架工具与 P1 混合策略；原位
│   ├── scoring/results.py              # 结果协议与统计；原位
│   ├── tasks/sgb/{code_repo,code_doc,domain_knowledge_doc}/
│   │                                    # 原任务配置与资产，不是研究源码包
│   ├── configs/                        # 锁与旧 profile 原位
│   └── checks.py / p1.py / gitchameleon_pilot.py
├── scripts/
│   ├── lab.py
│   └── sgb/{scrapy024.py,Invoke-Scrapy024Calibration.ps1,pydantic001.py}
├── src/degradation_lab/                # cli / sgb / io / artifacts / relocations 等原位
├── tests/                             # 现有平铺测试；本轮没有迁移或新增测试文件
├── data/manifests/sgb/                 # 来源、登记、relocation
├── runs/{gen/sgb,eval/sgb}/             # 历史身份与产物
├── results/sgb/                        # 历史报告与分析
└── docs/sgb/                           # 本报告所在位置
~~~

BeautifulSoup 的研究源码目录当前恰有 __init__.py、adapter.py、exports.py、scoring.py、smoke.py 五个文件；其 tasks/sgb/code_doc/beautifulsoup4-task-037/ 仍只有 adapter.json 与 offline_adapter.json。源码归组没有产生一个已就绪的真实任务环境。

### 2.2 实际调用链

~~~mermaid
flowchart TB
  C["scripts/lab.py → degradation_lab.cli"] --> P["sgb.__init__ 导出"]
  P --> M["management.plan / prepare / aggregate"]
  M --> R["degradation_lab.sgb：登记/来源/完整性"]
  M --> H["历史 legacy_runs → results.trial_record / summarize"]
  M --> O["准备/分析报告；真实 root 上会写 results"]

  L["旧 BeautifulSoup Python 模块"] --> A["sys.modules 别名 → task_adapters.beautifulsoup037"]
  SM["旧 smoke 冷启动 -m"] --> MAIN["新 smoke.main → probe"]
  MAIN --> STATIC["adapter.validate_prepared / verify_assets；静态源码与主机文件校验"]
  STATIC --> ENG["项目外工程记录；NOT_RUN，task_success=null"]

  S["Scrapy PS/主机入口 → sgb.scrapy024.paid_batch"] --> RUN["sgb.runner.execute_batch"]
  RUN --> N["scrapy024.native_trial → 官方 Harbor Trial"]
  RUN --> G["scrapy024.grade_export → 任务专属 preflight"]
  RUN --> REC["结果/观测/预算记录"]
  A -. "仅配置与 Mock 复用；生产 Trial 未接入" .-> RUN
  A --> STOP["fixture 收据；scorer NOT_IMPLEMENTED；Offline Agent 拒绝"]
~~~

实线表示源码调用关系，不表示本轮执行这些节点。本轮没有以真实 root 调用 management.prepare/aggregate，没有启动图中的 Harbor、任务 scorer 或付费批次。

## 3. 旧入口兼容性矩阵

| 接口 | 当前实现/结果 | 证据 | 等级与边界 |
|---|---|---|---|
| from downstream_eval.sgb import plan, prepare, aggregate | 导出对象就是 management 同名函数 | M21Compatibility.test_compat_exports_and_signatures；现有 test_sgb.py | T：普通导入、签名、行为通过 |
| 直接导入 management | 实现完整，SHA 与迁移前 __init__ 相同 | M21Compatibility.test_original_implementation_bytes_and_ast | T：原 3,199 字节实现不变 |
| scripts/lab.py sgb plan/prepare/aggregate | CLI:65–68 继续从旧包入口导入并分派 | M21Compatibility.test_cli_three_real_dispatches，三分支使用临时 registry | T：进程内运行实际脚本，项目外夹具；不是正式项目报告重写 |
| BeautifulSoup 四个旧模块 | 与四个新模块为同一模块对象，类/函数签名对应 | M22Compatibility.test_aliases_signatures_and_files | T：覆盖四组新旧导入及原定义的签名 |
| BeautifulSoup 模块属性/monkeypatch | 属性与函数 globals 归属同一新实现 | test_monkeypatch_reaches_function_globals；现有 BS 的 patch.object(bs, read/sha256) 用例 | T：实际受控调用通过 |
| importlib.reload(旧 BeautifulSoup 模块) | 按规范模块名重载，新旧别名仍指向同一对象 | test_reload_preserves_old_aliases；test_probe_never_initializes_model_or_dispatches_paid_batch_or_budget | T：四模块通过 |
| 旧 smoke 冷启动，搜索路径已配置 | 兼容文件执行新 smoke.main；实际静态 probe 仍 NOT_RUN | test_old_smoke_module_command_runs_canonical_static_probe；独立 python -m ... --help 返回 0 | T：真实 shell 验证到 help；完整静态 probe 用临时夹具进程内验证 |
| 未配置项目搜索路径的独立旧 smoke 命令 | 当前默认 shell 返回 ModuleNotFoundError: degradation_lab | 本轮独立命令实测；加 PYTHONPATH 后 help 成功 | T：既有启动前置条件，非本次移动引入的业务故障 |
| 旧 smoke 已导入后，同进程 runpy.run_module(旧名) | 出现 RuntimeWarning 与 ImportError: loader ... cannot handle ... | M3BoundaryChecks.test_cold_smoke_and_warm_runpy_have_different_behavior | T：确认存在限制；不能记为该加载方式兼容通过 |
| patch 包级 sgb.plan 后调用 sgb.prepare | 不再替换 management.prepare 的 plan 全局引用 | M3BoundaryChecks.test_management_package_patch_does_not_replace_implementation_global | T：相较迁移前存在 patch 目标变化；未发现现有调用者依赖此用法 |
| Scrapy configure/paid_batch → Runner | 原专属身份、回调、准入检查保留，非测试 execute_batch caller 仍只有 Scrapy | test_sgb_runner.py 两个 Scrapy 入口用例；源码 scrapy024.py:205–215 | T+S：分派与 Mock 通过，不是新版本实机运行 |
| BeautifulSoup Agent | 文件与拒绝代码原位；构造第一步 raise RuntimeError | 原 BS guard 测试、M22 拒绝检查、原始字节比对 | T：AST 注入禁止初始化的基类验证；U：未通过真实 Harbor 工厂导入/构造 |

### 3.1 可复现的加载限制

在项目搜索路径已配置的干净 Python 进程中，以下正常导入与 reload 通过：

~~~python
import importlib
old = importlib.import_module("downstream_eval.sgb.beautifulsoup_smoke")
new = importlib.import_module(
    "downstream_eval.sgb.task_adapters.beautifulsoup037.smoke"
)
assert old is new
assert importlib.reload(old) is new
~~~

但同进程继续执行：

~~~python
import runpy
runpy.run_module("downstream_eval.sgb.beautifulsoup_smoke", run_name="__main__")
~~~

会失败，原因是别名对象的 __spec__.name 和 loader 已属于规范新模块。实测错误为：

~~~text
loader for downstream_eval.sgb.task_adapters.beautifulsoup037.smoke
cannot handle downstream_eval.sgb.beautifulsoup_smoke
~~~

独立 python -m 冷启动不预先注册该旧别名，因此这两个场景不能混同。本轮没有更改兼容壳。

管理 API 的导出也是函数对象导出，而非两个管理模块的完整状态镜像。若后续测试想替换 prepare 内部 plan，应明确作用于 downstream_eval.sgb.management.plan；是否需要支持旧包级 patch 语义应先决策，不能悄悄更改测试去掩盖行为差异。当前仓库静态搜索未发现该旧 patch 用法。

## 4. 路径与配置引用

### 4.1 当前有效、历史解释、待适配路径

| 引用/位置 | 当前判定 | 原因和限制 |
|---|---|---|
| 四个 BeautifulSoup 扁平 Python 路径 | 当前有效兼容入口 | 不是待删除死代码；新旧导入共享实现对象 |
| sgb.task_adapters.beautifulsoup037.* | 当前规范实现路径 | __file__/__name__/__spec__ 指向新模块；不能假定旧文件元信息不变 |
| BeautifulSoup agent_import_path | 当前保留的专属入口 | adapter.py:77 仍为 downstream_eval.sgb.beautifulsoup_agent:OfflineBeautifulSoupTerminus2；类未迁移 |
| runner.lock 的 agent_import_path | 当前锁定的旧框架入口 | downstream_eval.integration.terminus_compat:CompatibleTerminus2 原位；此锁不是 BS 的真实执行授权 |
| 当前 Scrapy agent_import_path | 当前有效专属入口 | scrapy024.py:29 使用 downstream_eval.sgb.scrapy_agent:ScrapyTerminus2 |
| s24d001 configs 中 integration.scrapy_agent | 仅历史解释；不直接支持当前工厂 | 旧文件已不存在，没有为它恢复伪造兼容文件 |
| s24d001 task.path = .../tasks/scrapy_task024_v1 | 仅历史解释，原清单仍保留 | 当前资产在 tasks/sgb/code_doc/scrapy-task-024；relocation 未覆盖旧 task 前缀 |
| 原运行/案例/文档/结果路径 | 部分可通过 resolver 读取 | relocations.json 的 12 条映射目标均存在；使用 inside/archived_path 的读取才会应用 |
| 原执行源码四路径 | 仅历史代码身份 | current 新位置不是同字节版本，不能靠改路径宣称历史代码一致 |
| scripts/sgb/scrapy024.py 的 C 盘 PREFLIGHT | 当前存在的本机依赖 | 指向项目外旧审计目录，Path.is_dir 为真；不是可移植安装保证 |
| CONTROL / LINUX_ROOT | 固定环境约定 | harbor-p0-control-20261018 和 /run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab；本轮未验证容器/挂载 |
| /workspace、/harbor/skills、/workspace/skill | 保留原配置与未验证状态 | BS 声明/Harbor 注入位置仍有运行时映射缺口；没有实机证明 |
| 新实现的相对导入 | 静态与导入测试通过 | .scoring/.exports/.adapter 与 from . import adapter as bs；包标记没有 eager import |
| Scrapy/Pydantic/脚本 __file__.parents | 当前未移动，根定位仍按原实现 | M3 没有修改深度；后续若移动必须逐项复核，不能直接套用 BS 处理 |
| tests 的 __file__ 与 helper 导入 | 当前有效但不适合机械搬目录 | test_sgb_layout 裸导入 test_sgb；BS smoke/evidence 引用其他测试模块的 helper |

原生 smoke 命令本轮实测：

1. 工作目录为 lab、默认搜索路径：python -B -m downstream_eval.sgb.beautifulsoup_smoke --help，退出 1，缺少 degradation_lab。
2. 在该进程明确设置 PYTHONPATH 包含 lab 与 lab/src 后，同一命令退出 0。该设置只存在于工具进程，没有修改持久环境或项目配置。

scripts/lab.py 自行加入 lab/src；Scrapy 控制端命令也显式传入 PYTHONPATH。因此需要把不同入口的环境前提写清楚，不能把测试 harness 注入搜索路径后的通过描述为任意 shell 都能直接启动。

### 4.2 生成配置与真实执行的界线

BS prepare 使用调用方显式传入的 profile、镜像 digest、超时、Skill 包和外部新目录；任务 ID、generator、experiment、scope 和 NoSkill/Skill 均有校验。派生 task.toml 的 schema_version 为 1.4；Agent import_path 没随目录归组改变。固定 TaskConfig 源码的离线 schema 测试通过，但镜像存在性、容器目录、挂载、远端 Skill 可见性和实际导出仍 U。

真实 s24d001 的 NoSkill1/CleanSkill1 配置保留 Linux 绝对路径、旧任务目录、旧 Agent import_path、旧 p1_profile/p1_manifest 和旧 trials_dir。CleanSkill1 manifest 的 generator_run_id 仍为 s24r005，staged_root 仍是 runs/downstream/...，记录 15 份 Skill 文件。它们是历史冻结记录，不能当成新候选代码的可运行配置模板直接重用。

## 5. 当前代码身份与冻结资产

### 5.1 BeautifulSoup 当前身份

- smoke.py:43–57 的 code_version.files 同时覆盖四个规范实现、四个兼容入口、两个新增包标记，并保留原 Agent/Runner/研究工具等字段。
- exports.py:52–67 的 context.code_version 也覆盖上述十个 M2 文件；Path(__file__) 现在绑定规范 exports.py，兼容入口另有明确路径。
- M22 的身份专项检查本轮重跑：完整覆盖十项；模拟规范 adapter.py 的 SHA256 改变会使 controller.verify 返回 False，恢复后为 True；把旧源码哈希重新标成当前收据也被拒绝。
- 上述是**当前工作树选定文件的字节身份**，不等于完整依赖闭包、内存中执行代码证明、发布提交身份、可信真实导出或持久化认证。已有收据仍是 evidence_kind=offline_fixture、会话 HMAC；控制器结束后缺少持久化可信验证机制，这个既有边界没有解决。
- 没有新增或改写历史 manifest。新目录可通过当前 code_version 逐项核验，但不能让旧代码身份“跟着目录自动更新”。

### 5.2 核心源码 SHA256

下列为本轮当前实测；四个新实现和兼容入口/包标记均与 M2-2 交付摘要一致，management 与迁移前原实现一致。

| 当前路径 | SHA256 |
|---|---|
| sgb/management.py | 723df85fb98d75079ef93d7f46169b26a40b9fb98399a48989deaaf33b4a9fd6 |
| sgb/__init__.py | 503b8854da9d8a475a8b31a44465f20c1c62f68a706dfadd3013d52b0b422a73 |
| sgb/runner.py | d3da5477d25fb9a134d8b1cd90232188d1fd6b8db8c360c1350c917512cfa234 |
| sgb/scrapy024.py | 75b69e42d40cf2f70c82649c9990325729dabc299748189daa7954ceb37b5bea |
| sgb/beautifulsoup_agent.py | ca2943d7fbd1656ba532dd5d29d7a73b3376c743f459c8d5d3b7bee1366ade9c |
| sgb/task_adapters/beautifulsoup037/adapter.py | 0dc89209e0a7c35ca6e4cbf70a9bd1b6947004f5ffc6e91f648dbaa9d6fcd6ef |
| sgb/task_adapters/beautifulsoup037/scoring.py | b7da4f4bdc094bdf34efec244c2334b20ca894c74d20ab181aa996b1ef15f6bb |
| sgb/task_adapters/beautifulsoup037/exports.py | db750efc3db25a6362a974d47448e8f61549413628c5bdaa77c440326ee3ab95 |
| sgb/task_adapters/beautifulsoup037/smoke.py | 1d79c16c95b4764912b13ba62521e8c92c2965355c0724e14d6ab8d5078c8dd5 |
| sgb/beautifulsoup037.py | b95f1b6bfedd883d84ee4ee82495a7b646058ea381d35540db99f5746174a8f1 |
| sgb/beautifulsoup_scoring.py | aa32645dd16aec7f89db913982fdcdc27ad93bacfc9d790c4029e90eb4a03b40 |
| sgb/beautifulsoup_exports.py | 5ed783ea22ba979e63c7fb2d15e95ca0d7247f0ab9d61c2dedb37ac49c325095 |
| sgb/beautifulsoup_smoke.py | 56a6a9f1b2b7f4b7b3f1d7d2f2f8393ca62cf3cd6e958dbf937d52da43840759 |
| sgb/task_adapters/__init__.py | 0c32613784ca9b52e5002622271e772dcbd66c20eb13c28ace668d1a93b2153e |
| sgb/task_adapters/beautifulsoup037/__init__.py | 477d586847c0abec3d25c84629a18201922243bbe9043f6aac1348652835057b |

本小节 sgb/ 前缀均指 downstream_eval/sgb/，不是另一物理目录。

### 5.3 冻结资产与锁

| 资产 | 本轮核验结果 |
|---|---|
| SGB 登记与原始快照 | audit_registry=PASS，187 项、2,602 个 snapshot 文件；revision 5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d；211 份来源 manifest。只是静态完整性，不是执行准入 |
| 原固定 Harbor | verify_sources 的 12 个源码文件 SHA256/Git blob 校验通过；uv.lock SHA256 通过；锁中版本 0.24.0、commit 2de4605b9404eada7d341388291e6e469c90330b |
| Scrapy scorer/source_manifest.json | frozen_inventory 459 项逐项 SHA256 全匹配 |
| Scrapy 原 instruction / Oracle | d349a7822e667628c4535ae278fc70b4e40c8831654516e7f11e737349cdee7c / dbde11a8dce8a699101792be3b48e85a672e91a0cdc6cc4de32862cffeeb3918 |
| BS 原 Oracle | c7ee6d37d069c02aa9c6059ed6dcc28857ad44dcdd002d73642fa4838a4c7e6c；原 15 项测试名清单未变，未运行 Oracle |
| Pydantic asset_manifest | files 中 8 项全部匹配，未运行其 demo/scorer |
| Scrapy/Pydantic test.original.sh | 均为 1,197 字节、46 个 CRLF，SHA256 2ad84cb7df6840331626a506a5e106ddb79de898da1737bf21471f1d3b8d472a |
| .gitattributes | f121360a29c132f30ba9dfdbd39abe0f914b77c1985aeb635a0a64fde129d4fa |
| runner.lock.json | 7faeb805a64e722a0a8a05ac8404a220707336d85be180a5913563b5a0638fd2 |
| relocations.json | 97aa8b450f87250d2a628aeef023cc1e51fa236214723629b6a0085bbbedf434 |
| 历史 budget.sqlite3 | 3676ad026cc373b6cea265177eda48205190ae8b89ed55b7fc6af8362aba6d09；用 mode=ro&immutable=1 读取 policy；未调用真实 Ledger 事务 |

git check-attr 对两份冻结 shell 返回 text: unset、eol: unspecified；代表性的 runs/gen、runs/eval、results/sgb、data/manifests/sgb 文件也为 text: unset。普通 adapter.py 保持 text/eol unspecified。没有运行换行转换或改属性规则。

runner.lock 中的 image_validation、full_dependency_installation 等 PASS 是历史文本。本轮源码锁验证不能证明当前 Docker 镜像、容器、安装环境或网络仍与历史状态相同。

## 6. 历史实验读取与重放风险

### 6.1 结果读取通过

登记中的 s24d001 batch_results.json 仍可通过 inside 与 legacy_runs 读取，SHA256 为 0887109d1762f55b9761faf53f84c2d0899bec797ad8e7f6426794e28b1706eb，与登记一致。六条记录可用现有 trial_record/summarize 在内存解析：NoSkill 为 0/3、CleanSkill 为 2/3，无 unscorable。这里只验证历史数据可读，没有生成或覆盖汇总文件，也没有重新评测。

归档测试还确认 s24m001、s24m002、s24m003、s24m004、s24m005、s24r005 能通过 resolve_run 定位到 SGB 生成目录；load_run(s24r005) 仍读到完成状态与 15 个注册 Skill。

### 6.2 执行清单不能直接代表当前代码

对 runs/eval/sgb/scrapy-task-024/s24d001/execution_manifest.json 的 975 项做只读比较：

| 解析方式 | 可找到且 SHA 匹配 |
|---|---:|
| 原相对路径直接读取 | 457 / 975 |
| 应用现有 relocations.relocated 后 | 507 / 975 |
| 另作人工路径对应：旧任务前缀 → 当前 SGB 任务目录 | 464 / 464，均存在且同 SHA |

最后一行是本轮内存比较，**没有写入 relocation 规则**。507 + 464 = 971；其余四项为已改版的源码/launcher：

| 历史路径 | 当前职责对应位置 | 历史 SHA256 | 当前 SHA256 |
|---|---|---|---|
| downstream_eval/integration/scrapy_agent.py | downstream_eval/sgb/scrapy_agent.py | afc1765500e87cb8471e26eb5d027cd9eb6330e6dc944f8814dd2b7adf182dc2 | dca2379f834e0fd22b88d9fa1ba36ff8fd8f5ba1cca43a4396694541727ce7d6 |
| downstream_eval/scrapy024.py | downstream_eval/sgb/scrapy024.py | d5b3820ce341b42b09f1c1029b379d360b970830be299546bc1533e9a8cdaedb | 75b69e42d40cf2f70c82649c9990325729dabc299748189daa7954ceb37b5bea |
| scripts/scrapy024.py | scripts/sgb/scrapy024.py | f7f8ed85d6e9a777c66e4fca05edb649822744ba21bc072262488848a8862671 | e6b5368963b8bbc4c26ddae01114bbd56be3a2c1c30b5e0e7dc366764682fd46 |
| scripts/Invoke-Scrapy024Calibration.ps1 | scripts/sgb/Invoke-Scrapy024Calibration.ps1 | 19c8897deab263124206f27a9a35e7756742182fa475b0f23500c2bd7ee12fa1 | c59de40ba87a3d4574b7ff207452708c684bbfbcf01671056ea4f04bfc3d0d9b |

这里没有把职责对应强行等同为同版本实现。当前 runner.verify_frozen 使用 root/name 直接校验，不应用 relocation；现有 relocation 也不覆盖上述四个源码路径或旧 task 前缀。因此旧 execution_manifest 不能直接作为当前代码的执行身份。

此外 results/sgb/audits/layout-20261024-001/migration.json 的 after 段仍记录原 __init__.py 哈希 723df85f...。它与当前 management.py 相同，与新兼容 __init__.py 不同。这是历史报告的正确保留，不能为“通过”而改写。

### 6.3 预算与防重复

- 真实 s24d001/batch.started 存在。原 budget policy 保留 scope=scrapy-task-024/s24r005/initial-calibration、六个交替 trial 标签、global_limit=36，files 有 975 项 Linux 绝对路径。
- inside/archived_path 的路径映射不改 ledger policy，也不重写配置中的字符串。旧数据库与清单不可能因 Python 模块别名自动变成新代码预算。
- calibration_output、Runner 的排重/身份校验和 launcher 的历史批次拒绝由现有离线测试确认。没有尝试重启真实历史批次。
- 后续若要运行当前候选代码，必须使用独立新身份/新记录和显式预算授权；不能修改旧清单、删除 marker、复用旧预算或把旧报告的成功声明移到新版本上。

## 7. 测试覆盖与未覆盖风险

### 7.1 本轮实际执行

| 测试组 | 发现/计数 | 通过 | 失败/错误 | 跳过 |
|---|---:|---:|---:|---:|
| 现有 BS 适配/Smoke/证据 3 文件 | 53 | 53 | 0 | 0 |
| 现有 Runner、Scrapy、SGB 管理 3 文件 | 46 | 45 | 0 | 1 |
| 现有 layout/archive 2 文件 | 11 | 10 | 0 | 1 |
| 会话内重跑 M2-1 专项 | 5 | 5 | 0 | 0 |
| 会话内重跑 M2-2 专项 | 10 | 10 | 0 | 0 |
| M3 边界复现专项 | 2 | 2 | 0 | 0 |
| **合计** | **127** | **125** | **0** | **2** |

两项跳过：
1. test_scrapy024.Scrapy024.test_scrapy_agent_sdk_uses_the_bounded_transport_without_real_network：原有 skip，当前环境缺少固定 Linux Harbor runtime。
2. test_sgb_archive.SGBArchive.test_relocated_loader_retains_logical_path_and_exact_stat_signature：本轮明确安全跳过；该用例会加载官方 AutoSkill4Doc pipeline，超出本轮启用的导入保护范围。没有认定它不存在或已失败，也没有放宽其断言。跳过标记只在内存验收进程中设置，测试文件未修改。

M3 的两个边界用例通过，表示成功复现了两个限制，不表示 warm runpy 或包级 patch 兼容通过。独立 shell 的默认搜索路径失败也单独记录于第 4 节，不隐含在“0 个 unittest 失败”中。

现有 110 项来自八个测试文件，各定向发现 ID 唯一，文件清单与 AST test 方法数对应；没有用全仓库 discover 冒险执行其他运行时测试。另 17 项为本次会话内检查，未混入仓库发现数。

### 7.2 关键验收点与证据

| 验收点 | 具体测试/检查 | 能证明什么 / 仍缺什么 |
|---|---|---|
| 管理准备与汇总 | test_sgb.SGB.test_preparation_is_nonexecuting_and_refuses_overwrite、test_empty_aggregate_never_invents_success、test_result_summary_is_mean_and_keeps_unscorable_separate | 现有行为通过；不是正式项目生成新报告 |
| 三个 CLI 分支与签名 | M21Compatibility.test_cli_three_real_dispatches、test_compat_exports_and_signatures、test_plan_and_error_semantics | 临时 registry 上实际脚本通过；这些专项尚未持久化到 tests |
| 管理原实现不变 | M21Compatibility.test_original_implementation_bytes_and_ast、test_historical_aggregate_equivalence | 原 3,199 字节与历史汇总等价；不承诺旧包级 monkeypatch 的所有语义 |
| 新旧 BS 模块 | M22Compatibility.test_aliases_signatures_and_files、test_monkeypatch_reaches_function_globals、test_reload_preserves_old_aliases | 四对同对象、签名、属性修改、reload 通过 |
| 旧 smoke 命令 | test_old_smoke_module_command_runs_canonical_static_probe、现有 test_cli_is_static_only_and_has_no_runtime_option、独立 --help | 同一静态逻辑与参数拒绝通过；需项目搜索路径，warm runpy 有限制 |
| Agent 拒绝 | test_offline_agent_gate_precedes_any_model_client_initialization、test_agent_rejection_guard_stays_in_place、M22 test_refusal_guards_are_still_active | AST guard/禁止基类初始化通过；真实工厂与 SDK 构造未验 |
| 独立后端未启用 | test_no_runtime_scorer_or_raw_callback_is_activated、test_real_receipt_mode_stops_before_reading_any_export | NOT_IMPLEMENTED/fixture-only/回调拒绝保持；不证明隔离或真实采集 |
| 提交与结果证据 | test_download_failure_is_unscorable_even_if_partial_file_exists、test_missing_junit_bad_exit_or_incomplete_outputs_never_pass、test_timeout_and_infrastructure_receipts_do_not_become_answers | 控制夹具的分类、身份与完整性拒绝通过；真实传输/独立运行仍未验证 |
| 新代码身份覆盖 | M22 test_smoke_identity_covers_implementations_shims_and_markers、test_receipt_identity_covers_all_moved_code_and_detects_change | 十项 M2 文件被当前记录覆盖；不是完整依赖/可信运行证明 |
| Scrapy 到 Runner 分派 | test_scrapy_entry_preserves_identity_and_passes_config_to_common_layer、test_scrapy_paid_entry_keeps_approval_readiness_runtime_and_task_success_policy | Mock 回调、19 断言策略与准入约束保留；没有实机 Trial |
| 预算与冻结身份 | test_budget_scope_mismatch_does_not_admit_or_recreate_budget、test_budget_frozen_file_set_must_match_execution_manifest、test_frozen_execution_changes_and_escape_are_rejected | 错误身份在 fixture 上拒绝，保护没有删减 |
| 历史 ID 排重 | test_completed_namespaced_batch_cannot_be_reused、test_host_launcher_uses_sgb_module_and_stops_before_old_batch_dispatch | 当前历史 marker/入口拒绝生效，无真实重启 |
| 历史读取 | test_old_run_ids_resolve_under_sgb_without_changing_registration、test_old_relative_and_absolute_paths_resolve_to_unchanged_bytes | 指定旧来源/生成运行可读；不是旧执行清单全部可解析 |
| 工程记录不进成功率 | test_engineering_records_cannot_be_converted_or_summarized_as_agent_success | smoke/fixture 不被公共统计误当真实 Agent 成功 |

### 7.3 证据缺口

M2-1 的 5 项、M2-2 的 10 项迁移专项只存在于会话内验收脚本。当前仓库测试确实覆盖很多原业务与保护，但没有永久固化这些专项的新路径、签名、别名、旧模块命令和十文件身份覆盖断言。未来只跑普通 unittest，不能自动获得本轮 127 项的全部证据。

本轮未运行全仓库测试、真实 Harbor/Terminus 工厂、镜像/挂载/容器、模型、Oracle、真实判分后端或真实提交传输。BeautifulSoup 结果仍不能用于新的真实成功率评估。

## 8. 公共性边界复核

| 部件 | 当前职责 | 不能扩大解释为 |
|---|---|---|
| management.py | SGB 登记规划、准备报告、历史观察汇总 | Agent launcher、环境准备工厂或执行准入 |
| runner.py | 显式配置、Skill 冻结、账本/排重、回调协调、记录 | 已覆盖全部来源类型；零模型通用 smoke runner |
| task_adapters/beautifulsoup037 | 单任务来源/配置/提交协议/证据接口与工程工具 | 公共 HTML 判分器、真实独立后端、全 Code Doc 执行器 |
| integration | 外部 Harbor 工具、Skill/预算机制及仍混杂的 P1 策略 | 所有函数均与任务/实验无关的纯 G 层 |
| tasks/sgb | 官方/派生配置、环境、冻结任务资产 | 可以为目录整齐随意移动或重新生成的源码 |
| scoring/results.py | 统一观察结果与均值统计，拒绝 smoke | 自动扫描所有新目录、修复不完整证据或解释任务业务 |

Runner 仍固定 paid 模式，含 p1_mode/profile/manifest、Docker、p1-observer、model_api_results=True 等约定；真实 execute_batch 的非测试调用者仍只有 Scrapy。BS 复用 trial_config 和 Mock 协调，不存在生产 Trial 接入证明。

integration/request_budget.py 的 Ledger/MeteredTransport 是机制，但 ledger_for_profile:240 等仍有旧 DATABASE/RECOVERY_DATABASE、Gold/A0/A1、六请求策略；p1_observer 保留 /harbor/skills 与 P1 日志/预算约定；skill_install 的部分检查依赖 Git/P0 fixture。归组没有消除这些边界，不应整体晋升 G 层。

登记静态审核仍是 Code Repo 123、Code Doc 28、Domain Knowledge Doc 36；executable_tasks=0。元数据可共用不意味着三类执行已经验证；没有新增三套类型 Runner，也没有证据支持立刻创建三套。

## 9. 按严重程度排序的发现

严重程度服务于本课题的兼容与复现决策，不表示安全漏洞分级。

| 优先级 | 发现与性质 | 证据/影响 | 最小后续动作 |
|---|---|---|---|
| P1，历史重放前阻断；既有 | 历史 Scrapy 执行清单和预算不能直接绑定当前代码 | 975 项仅 507 被现有 resolver 找到；464 项资产人工对应同字节，4 个源码版本已不同；旧绝对路径/Agent import_path/marker 仍冻结 | 保持历史不变；后续运行前单独建立新代码/配置/实验身份；复现旧版需审查的历史代码快照环境，不能改旧清单 |
| P1，真实评测前阻断；既有且刻意保留 | BS 真实 Agent、真实导出与独立判分未就绪 | Offline Agent、fixture-only、NOT_IMPLEMENTED；SDK 跳过；容器与传输 U | 等待单独授权与原研究阶段决策，本轮不补后端/隔离或选任务 |
| P2，兼容行为限制；M3 实测 | 旧 smoke 热加载 runpy 失败 | sys.modules 别名导致规范 __spec__/loader 名称；普通导入/reload/冷启动仍通过 | 明确支持边界；如需热 runpy，再单独设计兼容入口并加用例 |
| P2，兼容行为差异；M3 实测 | 包级 sgb.plan patch 不再影响 prepare 内部全局引用 | 迁移前会被替换，当前需 patch management.plan；未发现现有调用依赖 | 决定是否支持旧 patch 合约；禁止把它默认为“完全无行为差异” |
| P2，回归证据缺口 | 迁移专项尚未落入仓库测试 | 会话内 15 项不能被现有 discover 自动重复执行 | 下一批优先固化必要兼容回归，保持断言和保护，暂不搬测试目录 |
| P2，身份声明边界；既有 | code_version 为选定文件 SHA；fixture HMAC 只在会话有效 | 源码身份可查，但无完整执行依赖/真实采集/持久可信证明 | 保持“工作树+fixture”表述；不将当前收据升级为运行成功证明 |
| P3，启动前提与本机依赖 | 默认 shell smoke 缺少 src 搜索路径；Scrapy 固定外部 PREFLIGHT/CONTROL/LINUX_ROOT | 默认独立命令失败，设置 PYTHONPATH 的 help 成功；PREFLIGHT 当前存在，运行时未查 | 先明确命令环境说明与后续启动验收；不顺手改 launcher/环境配置 |

未发现本轮导致的资产字节破坏、暂存区变动、额外任务接入或新增真实执行能力。两处新复现的兼容边界不抹去已通过的正常路径，但足以否定“不加限定的完全兼容”声明。

## 10. 下一批建议与停止条件

1. **先固化兼容回归与支持合约**：优先将 M2 的必要专项纳入现有测试体系或一个专门测试文件；明确是否支持 warm runpy 和包级管理 patch。只是建议，M3 不新增测试文件、不搬测试目录、不改兼容壳。
2. **再评审最小迁移批次**：Scrapy 的代码身份、历史输出/预算与 launcher 耦合最强，暂不进入移动；Pydantic 仍是含 Docker scorer 的 demo，不能当成通用 Runner 的已验证第二实现。若后续选择其中任一项，先给出独立文件范围、根路径计算与身份检查方案。
3. **integration 保持原位，先做窄函数判断**：仅在两个真实调用者和输入约定都明确后，评审 fairness_identity 等小机制；不能以目录清理名义迁走整个 P1 observer/预算适配器。
4. **不扩大全类型框架**：三类来源仍保留登记/资产分类。新任务验证或真实 runtime smoke 属于单独研究/运行授权，不借 M3 自动开始。

进入下一批实施前需满足：本报告获审核；测试证据可重复运行；兼容行为范围明确；新文件身份覆盖真实实现；历史 manifest/账本/冻结字节保持不变。

任一阶段若需要改历史身份、取消拒绝保护、重用旧预算、启动模型/Agent/Docker 或扩大文件范围，应停止该阶段并报告。本轮可进入下一批的方案审核，不建议直接继续更多文件移动。

## 11. 已验证 / 静态判断 / 未验证清单

| 已验证 T | 静态判断 S | 未验证 U |
|---|---|---|
| 新旧导入、签名、BS monkeypatch/reload | 当前唯一生产 execute_batch caller 是 Scrapy | 当前候选代码的真实 Harbor Trial |
| 临时 registry 的 CLI 三分支、旧 smoke 静态 probe | integration 仍混有旧试点策略 | 容器、镜像身份、挂载和远端 Skill 可见性 |
| 默认独立 help 失败条件、带 PYTHONPATH 的 help 成功 | sgb 管理层与执行层职责仍分离 | 实际提交传输与可信采集 |
| warm runpy 与包级管理 patch 的限制 | 旧执行清单不能变成当前代码身份 | BS 独立后端与 Oracle 隔离 |
| 127 项定向检查的实际结果及两个 skip | code_version 不是完整执行/持久可信证明 | Code Repo/Domain 的公共 Runner 实跑 |
| 459 项冻结 scorer、2,602 项 snapshot、Pydantic 8 项、Harbor 12 项与 uv.lock | 下一批先补回归再移动更稳妥 | 原始 Oracle 的运行成绩、行为评分、首任务选型（S0.3 暂停） |

## 12. 本轮操作与交付复核

实际操作仅包括文件读取/目录列举、rg、AST/TOML/JSON 只读解析、SHA256/Git blob 计算、git --no-optional-locks status/rev-parse/diff/check-attr、只读不可变 SQLite policy 查询、经保护的离线测试与静态 --help。没有调用需要副作用的 preflight、真实 prepare/aggregate、paid_batch、真实 Trial、Docker 或评分进程；布局测试仅导入冻结预检模块并执行字节 verify，不执行 Oracle。

没有安装依赖或构建环境；没有执行 add/commit/push/reset/clean/checkout/restore。测试脚本与 skip 选择只存在于验收进程内，既有测试文件和断言没有修改。重跑的会话检查来源是本次会话 M2 验收脚本，不是仓库持久化的新测试。

报告交付后的实际 Git 与全树字节复核结果附后。

### 12.1 交付后实际复核

- 排除本报告及 .git/.idea 元数据后，全树仍为 30,130 个普通文件、1,672,399,681 字节、2 个 reparse link；集合 SHA256 仍为 4357f7d1e4c5ee84c7159d700de02f38b56fe95ff0e966e8ea677df312d2b72c，与审查开始一致。扫描范围内全部既有文件/链接身份未变。
- Git HEAD 仍为 3073a1a1a7119603ccb2ac738fae269a8223c0d9；index SHA256 仍为 2454cc749f587b0fee24774c9da654cd6ab0219b121b13a4ee457ee5e32acf33；暂存差异为空。
- 18 项 tracked 修改、880 项 tracked 删除全部保留；未跟踪数由 2,427 增至 2,428，唯一增量为本报告。剔除本报告后的完整 porcelain 状态 SHA256 仍为 c7cec2ad8db1b5541aa3115e499a21563fd280045cfeb1b6f8e565a9f7e4334a。
- 报告 UTF-8 可解析，十二个主要章节齐全、代码围栏成对，没有替换字符。本报告按交付要求新建，未覆盖旧报告。
- 本轮只新增本报告，没有修改任何既有项目文件；未实施 Scrapy、Pydantic、integration 或测试目录迁移。以上集合校验不覆盖 Git/IDE 的全部元数据，HEAD/index 已单独核验。

M3 报告完成，停止，等待用户审核。
