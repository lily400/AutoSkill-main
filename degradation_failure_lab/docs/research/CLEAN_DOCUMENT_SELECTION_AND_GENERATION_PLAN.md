# Case002–Case005：Clean 文档选择、生成准备与质量审计方案

审计日期：2026-10-11。项目：D:/AS/AutoSkill-main；lab：D:/AS/AutoSkill-main/degradation_failure_lab；官方源码：D:/AS/AutoSkill-main/AutoSkill-main。当前项目 Git HEAD：a7e4b96714aa259db397675bc4055817e4576445；开始写报告前工作区干净。

## 一、结论与本轮边界

推荐顺序为：**Case002 qsv sort → Case003 Docker cp → Case004 Git reset → Case005 ripgrep User Guide**。四份原始文档均已从官方仓库实际获取、固定完整 Commit、计算原始字节数/行数/SHA-256并检查操作内容。它们分别提供高比例参数表、嵌套条件分支、状态表与多步流程、长篇多主题教程。另比较 qsv join 与 CPython venv 两份备选。

结论为 **CONDITIONAL GO：选样可进入下一轮准备，但不应直接启动四案例批量生成**。短文档可优先使用现有配置；Git 和尤其 ripgrep 的完整生成存在显著容量风险，需要分批审批。所有 Case002–Case005 编号目前只是推荐，尚未创建案例、下载归档原文或修改 catalog。

本课题的核心是**退化文档的高质量 Skill 生成**。本次 Clean 扩展用于识别原版生成链路的基础缺陷与跨样本复现情况，为之后有控制的文档退化研究建立基线；不以 DirectDoc/FrozenSkill 下游对比为中心，不实现 Agent 或 Oracle。此前三份 Case001 研究报告保留为历史材料，不将其下游实验建议自动继承为本轮研究路线。

本轮执行了只读源码/配置/产物检查、官方 HTTPS 来源和发布标签核验、无模型结构检查、既有案例 validate/list/plan/verify；未调用付费模型，未调用 run、prepare、evaluation-init、aggregate 或写出导出文件，未修改官方代码及 Case001 基线。Codex 的语义判断仍是初步分析，不是独立人工金标准。

## 二、当前 lab 的实际约束与复用能力

### 2.1 实际盘点

| 对象 | 实际状态与审计依据 |
| --- | --- |
| 数据 | data/catalog.json 只有 qsv 数据集和 qsv_select.json 来源清单；data/raw_sources/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/ 下有 select.md、LICENSE-MIT、Cargo.toml，没有另外四份候选原文 |
| 案例 | cases/ 只有 case001_qsv_select；实际阅读 case.json、conditions.json、rules.json、inputs/clean.json。只有 clean 条件；R1–R7 标为 analyst_checklist，分类 CUSTOM_TEST_DATA，provenance 为空 |
| 配置 | 实际阅读 configs/environment.json、configs/generation/deepseek_flash.json；官方路径从 lab 相对解析为 ../AutoSkill-main，不以当前终端目录代替 |
| 协议 | 完整检查 schemas/ 下 catalog、source、case、conditions、inputs、rules、evaluation 七份 schema；检查 src/degradation_lab/schema.py 的实际校验方式 |
| 运行器 | 阅读 scripts/lab.py、src/degradation_lab/cli.py、catalog.py、runner.py、io.py、adapter.py、provider_adapter.py；正式入口是 scripts/lab.py，不是 lab 根目录的 lab.py |
| 导出与评价 | 阅读 artifacts.py、evaluation.py。Case001 已有 results/exports/raecd75e08b34/ 下 11 个导出/验证文件和 results/run_index.jsonl；本轮未覆盖 |
| 已有运行 | 只读复验 raecd75e08b34：工程 PASS，24 项检查通过；1 Document、2 Window、4 SupportRecord、4 Draft、4 Spec、4 正式注册技能。execution.json 与 model_calls.json 实际记录 18 次成功 HTTP、57,472 total tokens，四次 classify_change 均 finish_reason=length |
| 官方相关实现 | 检查 AutoSkill4Doc/document/file_loader.py、ingest.py、document/windowing.py、models.py、stages/extractor.py、stages/compiler.py、store/versioning.py、core/llm_utils.py、taxonomy.py、prompts.py；检查 autoskill/utils/json.py 与 llm/openai.py 的相关解析/请求逻辑，而非用 README 替代 |

已有 Case001 的遗漏、操作契约冲突和注册默认创建用于提出待检验问题，不代表四份新文档也已经发生相同错误。既有工程 PASS 不包含句子级语义正确性、完整规则覆盖或 Register 响应根对象 schema 的成功保证。

### 2.2 新案例必须满足的约束

1. **来源可复现**：真实官方原文归档到 data/raw_sources/ 下；source_url 为 HTTPS，source_commit 为 40 位小写十六进制 Commit，source_path、repository、license、downloaded_at、sha256、document_type、local_path 完整。bytes 如填写必须吻合。发布标签须解析到 Commit，不能误用 annotated tag 对象 SHA。
2. **来源身份不能升级**：本次候选应使用 RECONSTRUCTED_OFFICIAL_SOURCE、paper_snapshot_verified=false；“官方来源”不等于 Anything2Skill 论文原始快照，不能使用 OFFICIAL_PAPER_DATA。人工规则清单仍是 CUSTOM_TEST_DATA。
3. **目录和 ID 一致**：case_id 符合 caseNNN_lowercase_name，与案例目录、rules、conditions、input manifest 一致；dataset/source/input/rule/condition ID 按协议唯一。catalog 必须先关联来源，case 的 source_ids 必须属于对应数据集。
4. **Clean 为原始字节**：kind=clean、operator=null、parameters={}；inputs/clean.json 的 path 必须直接指向权威来源文件，sha256=source_sha256=来源哈希。不转换格式、不翻译、不修正连字符、不删导航、不补外部链接内容，也不把摘录伪装成原文 Clean。
5. **单文档、单案例**：建议每个案例一个来源、一个 input001。许可证和版本说明保留在来源归档中，但不列入模型输入；否则文件加载器可能把它们当成额外 Document。不能把四文档拼接成一次案例以节省调用。
6. **规则先审核后冻结**：每项 source_evidence.lines 是原文件的显式一基行号列表，并非起止区间；例如 [39,44] 只表示两个定位点。原子规则必须区分条件、动作、参数、默认值、结果及例外。未经独立审核仍标 analyst_checklist/pending，不能标已验证金标准。
7. **配置分离**：generation_config 指向已有或另行批准的版本化配置；case.pipeline_overrides 当前只允许 domain、domain_type、family_name，不能塞入 Token/窗口/预算开关。建议 qsv/qsv-sort、docker/docker-cp、git/git-reset、ripgrep/ripgrep-guide 分别标识，不改变官方提示词或新增 taxonomy。
8. **历史隔离**：每次运行用全局唯一 run_id、全新空 SkillBank 和 run-local 输入/配置/包装层/官方代码哈希快照。不得重用 Case001 的 run 或现有 export/evaluation 目录。run 会追加 ledger；这属于下一轮批准后的写入，不是本轮已完成工作。
9. **路径防护与输出防覆盖**：先用 plan 检查 Windows 路径。verify --out 的导出器只禁止写入 run 内部，未保证目标不存在；aggregate 默认路径也会覆盖同名文件。下一轮必须使用新目标并预先检查存在性。

以上直接依据 catalog.py L25–39、L49–105，runner.py L10–40、L48–126，以及七份 schema。当前校验不替研究者证明来源的法律适用性、语义或规则清单完备性。

### 2.3 可直接复用与缺口

| 能力 | 复用结论 |
| --- | --- |
| 来源清单、案例/条件/输入定义与哈希检查 | 可以复用；需批准后追加来源和新案例文件，没有必要重构 |
| 原版 Ingest→Extract→Compile→Register 调用 | 可以复用；Markdown 和 UTF-8 AsciiDoc .txt 都走原始文本读取，无需安装渲染器。但“能读取”不等于章节解析正确 |
| 原始 API 请求/响应、stack、usage、finish_reason、异常观察 | 可以复用 adapter；本地 hashing embedding 不调用外部 embedding API。使用者仍须核对缺失 usage 与失败请求 |
| 导出、来源行匹配、阶段 ID 链与 Evidence Manifest | 可以复用 artifacts；行匹配是文本定位，ID 链是关联，不是语义支持证明 |
| 人工规则评价与汇总 | 可以复用 evaluation-init / evaluation-validate / aggregate；现有状态只有 correct、incorrect、uncertain、unreviewed，错误类型有 condition_error、exception_omission、parameter_mismatch、unsupported_addition、rule_omission、template_residue |
| 自动完整规则覆盖、阶段语义差分、内部一致性、注册截断专门判分 | 尚未实现。先以人工审计报告和现有 notes/trace_refs 记录，不在本轮增设功能 |
| 退化算子、自动生成变体、下游执行评价 | 当前条件协议能登记已有退化输入，不能据此称算子已实现。evaluation.py 是规则审核，不是 Agent 执行成功率评价；下游系统不是本次准备的前置条件 |

## 三、先比较候选，再确定 Case002–Case005

### 3.1 比较口径与候选表

统计来自 HTTPS 返回的**原始文件字节**，不是网页渲染/浏览器抽取结果。行数按 UTF-8 原文 LF 分行，末尾换行不另计空行。主选文档全文已阅读；qsv join 全文和 venv 的创建/选项/结构/激活表相关部分用于备选比较。表格行占比包含表头和分隔行，不包含 Git literal block 边界；导航尾行不计表格。代码块数量是语法块数量，不是原子任务数。

| 候选 | 格式；字节/行 | 结构、表格和步骤/规则特征 | 选择判断 |
| --- | --- | --- | --- |
| qsv sort | UTF-8 Markdown；5,381 / 72 | 1 标题+5 个二级章节；3 张参数表、22 行，占 30.6%；1 个 Usage 代码块。步骤低密度，参数优先级、随机/唯一性、表头条件集中于长表格行 | 推荐 Case002；与 Case001 同仓库同 Commit，优先做同来源生成器的表格控制样本 |
| Docker container cp | UTF-8 Markdown；6,006 / 131 | 6 个标题；1 张选项表、5 行，占 3.8%；5 个代码块。核心是源/目标类型、目标存在性和路径后缀的嵌套分支 | 推荐 Case003；长度与 sort 接近而表达结构明显不同 |
| Git git-reset | UTF-8 AsciiDoc 源文件 .txt；19,125 / 506 | 标题及 NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES/DISCUSSION/GIT 七节；10 组工作流示例；8 张等宽状态表、56 行，占 11.1%，不是 Markdown pipe 表 | 推荐 Case004；可检查格式、序列和 HEAD/index/worktree 状态是否被混淆 |
| ripgrep User Guide | UTF-8 Markdown；40,701 / 1,022 | 1 标题、TOC、11 个主题章和3个深层子章；0 表；46 个 fenced block，包含命令、输出、配置和脚本，不能全算操作步骤 | 推荐 Case005；长文、跨章节依赖与命令/输出边界压力样本，最后执行 |
| qsv join | UTF-8 Markdown；5,687 / 85 | 1 标题+6 章节；4 张表、27 行，占 31.8%；1 个 Usage 代码块；连接类型、空键及键变换条件丰富 | 第一备选；可替换容量不适配的样本，但与已有 qsv 来源结构相近、外部规则依赖更多 |
| CPython venv | UTF-8 reStructuredText；31,711 / 749 | 创建、工作机制、API、扩展 EnvBuilder 示例；1 张激活命令 grid 表 L225–239；大量 directive/版本条件；L59 有外部 include | 第二备选；适合补格式/平台条件，但 API 描述占比较大，来源边界与 include 必须先定协议 |

没有采用“每个领域挑一个”的机械策略。sort 与 Case001 形成有意义的同工具对照；Docker 同等短长度但分支密集；Git 加入不同标记语言和状态表；ripgrep 保留长篇教程。四份文档同时改变了长度、格式和操作复杂度，**不能用这四份材料独立识别“表格比例导致失败”的因果效应**。

### 3.2 Case002：qsv sort

- 官方原文：[固定 Commit 的 sort.md](https://raw.githubusercontent.com/dathere/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/docs/help/sort.md)；官方仓库：[dathere/qsv](https://github.com/dathere/qsv)。Commit：257ae7b38738688138dc430c2ccb4eef8766f3fc；同快照 Cargo.toml 的 package version 为 24.0.0。该 Commit 的提交/发布日期：UNKNOWN；版本号不冒充发布日期。
- 文件：docs/help/sort.md；5,381 字节、72 行；SHA-256：05bfbd4f41c7a4e55c3aeab71f5bbe8dd38659f4d00c5970c557df1f3feac693。
- 章节：Description、Usage、Sort Options、Random Sorting Options、Common Options。适合生成 CSV 行排序、比较模式选择、去重与随机化的程序型 Skill。
- 典型可核验规则：内存装载与大文件替代路径 L16–18；numeric 与 natural 同开时 natural 优先 L41；ignore-case 对单纯 numeric 不起作用 L43；unique 使用同一比较模式 L44；random 时比较标志用于 unique，reverse 不控制打乱 L52；faster 不保证稳定性 L56；no-headers 首行按数据排序 L66。应逐项原子化，不能合成“排序参数全部正确”一项。
- 获取需联网；冻结文件后，生成只需 Anything2Skill 的既有运行环境和批准的模型调用，不需要 qsv 可执行文件。未来行为核验需匹配版本 qsv；当前 PATH 未找到 qsv，其他位置/可用二进制身份 UNKNOWN。本轮不安装。
- 版权：同 Commit 的 LICENSE-MIT 与 Cargo.toml L11 已核验为 MIT；下一轮归档时保留许可及版权声明。不能由 MIT 直接断言生成内容毫无第三方权利限制。许可依据：[LICENSE-MIT](https://raw.githubusercontent.com/dathere/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/LICENSE-MIT)。
- 科研理由：既控制仓库/帮助文档生成器/版本，又增加优先级和条件组合，适于检查 Case001 的表格遗漏是否跨命令复现。
- 混杂：--select 明确转引 select 语法，外部测试/wiki 链接仍指 master；不能把链接内容自动补进冻结输入。源表中选项使用非 ASCII 连字符和 HTML 字符，Clean 必须原样保留，复制执行错误不能自动归为后加退化。随机种子不证明跨软件版本相同输出；操作核验未完成。

### 3.3 Case003：Docker container cp

- 官方原文：[固定 Commit 的 container_cp.md](https://raw.githubusercontent.com/docker/cli/e4078058de0a9f4d5cb65f946f4b8a090e19fffe/docs/reference/commandline/container_cp.md)；官方仓库：[docker/cli](https://github.com/docker/cli)。Commit：e4078058de0a9f4d5cb65f946f4b8a090e19fffe，为本轮只读查询 master 得到的固定快照；对应发布版本/发布日期：UNKNOWN。
- 文件：docs/reference/commandline/container_cp.md；6,006 字节、131 行；SHA-256：808ca152d4ea8bb4dbb12d31dcff15e9d3c958b85eaab4ccd4026cef1f14f764。曾核验 v28.0.4，但两条尝试的文档路径返回404；不把当前文件标成 v28.0.4 文档。
- 章节：Aliases、Options、Description、Examples、Corner cases。适合生成容器与宿主之间的文件复制/目的路径决策 Skill。
- 典型规则：运行或停止的容器均可复制 L28–33；容器路径相对根、宿主相对路径相对当前目录 L35–41；默认目标所有权与 archive 保留源所有权 L43–49；不创建缺失父目录 L50–52；文件→不存在且末尾为 / 的目标报错 L57–61；目录→已有目录时，SRC_PATH 是否以 /. 结束区分目录本身和内容 L67–78；本地 symlink 默认复制链接、-L 复制目标 L80–83；STDIN tar 的容器目标须是目录 L128–131。
- 获取需联网；仅生成不需要 Docker。行为核验需要 Docker 客户端、可信 daemon/容器和受控文件系统；当前 PATH 未找到 docker，daemon/镜像状态 UNKNOWN。不自动下载镜像、不安装、不操作用户容器。
- 版权：同 Commit 的 [LICENSE](https://raw.githubusercontent.com/docker/cli/e4078058de0a9f4d5cb65f946f4b8a090e19fffe/LICENSE) 为 Apache-2.0；[NOTICE](https://raw.githubusercontent.com/docker/cli/e4078058de0a9f4d5cb65f946f4b8a090e19fffe/NOTICE) 已实际核验。归档/再分发保留适用许可证、NOTICE、版权及变更说明；NOTICE 还提醒适用的使用/转移限制，具体适用性 UNKNOWN。本报告不提供法律保证。
- 科研理由：条件树中的错误可以精确定位到“哪个前提被删、哪个分支被反转”，不依赖模糊主题相似度；与 sort 接近的字节规模有利于观察格式差异。
- 混杂：权限、用户命名空间、Linux/Windows 路径、容器挂载和 symlink 都可能影响行为验证。通用说明、嵌套分支和例外之间不可互相覆盖；不把“目标不存在会创建目录”推广成“父目录也自动创建”。生成标记/选项表和 Unix tar 示例均按原文保留。

### 3.4 Case004：Git git-reset

- 官方原文：[固定 Commit 的 git-reset.txt](https://raw.githubusercontent.com/git/git/a52a24e03c8c711f1d5e252fba78f9276908129b/Documentation/git-reset.txt)；官方仓库：[git/git](https://github.com/git/git)。版本标签 v2.47.3 解析到 Commit：a52a24e03c8c711f1d5e252fba78f9276908129b；annotated tag 对象 ccff137f339698d014904044fb2cfa0c697b03dc 不是该 Commit。发布日期：UNKNOWN。
- 文件：Documentation/git-reset.txt；19,125 字节、506 行；SHA-256：372b401b153142441c139098f9de714351ab4f5c13efbac69ca7cd80989092cd。文件是 AsciiDoc 源文本，不将它描述成 Markdown 或渲染 man page。
- 适合生成按当前状态选择 reset 模式、撤销暂存、保留修改的版本控制操作 Skill；8 张状态表可检验步骤结果与模式描述是否一致。
- 典型规则：pathspec 形式只修改 index、不移动分支或修改工作区 L23–31；commit 形式移动 HEAD、先设置 ORIG_HEAD、默认 mixed L49–54；soft 不碰 index/worktree L57–61；mixed 改 index、保留 worktree L63–69；hard 改 index/worktree并可能删除妨碍写入的未跟踪路径 L71–74；merge/keep 的中止条件不同 L76–91；--pathspec-file-nul 仅在 --pathspec-from-file 下有意义 L115–126。L401–500 状态表和 L203–207 已共享提交警告提供交叉核对位置。
- 获取需联网；生成不需安装 Git 或 AsciiDoc 渲染器。当前 Git 为 2.53.0.windows.3，不是文档版本 2.47.3，因此未来本机执行不能直接充当固定版本的语义金标准。
- 版权：同 Commit [COPYING](https://raw.githubusercontent.com/git/git/a52a24e03c8c711f1d5e252fba78f9276908129b/COPYING) 明确项目 GPL v2 口径。尚未完成该文档所有可能文件级许可例外或生成 Skill 衍生许可的独立确认，相关结论 UNKNOWN；不得按 MIT 文档发布。公开原文、修改版或衍生成果前应确认适用条款并保留来源/许可。
- 科研理由：同一规则在描述、操作示例和状态表中重复表达，可检查 Extract 冲突、Compile 合并改变语义及最终输出契约不一致；非 Markdown 格式也测试摄取适配边界。
- 混杂及安全边界：仓库起始状态、已共享提交、未跟踪/冲突文件、子模块及 shell 引用都重要。**本轮不执行任何 reset；未来也不得在本项目/用户仓库验证生成指令**，如需执行，只能另行批准后使用可丢弃隔离仓库。格式造成的解析失败与文档本身的规则错误必须分开。

### 3.5 Case005：ripgrep User Guide

- 官方原文：[固定 Commit 的 GUIDE.md](https://raw.githubusercontent.com/BurntSushi/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/GUIDE.md)；官方仓库：[BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)。14.1.1 标签解析到 Commit：4649aa9700619f94cf9c66876e9549d83420e16c；annotated tag 对象 0e8390a66fbcf6eeac1aeb0541b367663a597c79 不作为 source_commit。发布日期：UNKNOWN。
- 文件：GUIDE.md；40,701 字节、1,022 行；SHA-256：9dd96f163700ab5b41296cef3555b535c80c19e2ea25c7925c21b133d96d9537。标签 URL 与 Commit URL 的内容哈希一致。
- 章节：Basics、Recursive search、Automatic filtering、两类 Manual filtering、Replacements、Configuration file、File encoding、Binary data、Preprocessor、Common options，及三个子章。适合生成递归检索与过滤、只改输出的替换、配置/预处理工作流 Skill。
- 典型规则：-F 将正则模式按字面量处理 L148–151；不同 ignore 文件的优先级 L180–189、240–247；后给 glob 覆盖前给 glob，顺序可导致无文件被搜索 L310–322；--type-add 只影响本次命令 L412–422；--replace 只改变输出、不修改文件 L536–538；配置逐行单参数且不做 escaping L547–559；参数和值用 = 同行或分两行 L592–601；--no-config 禁用环境配置 L621–625。二进制与递归/显式路径的不同处理 L738–765 应另做规则组。
- 获取需联网；文本生成不需额外工具。当前 PATH 的 rg 为 15.2.0，与来源 14.1.1 不同。未来若验证预处理示例，还可能需要 Unix shell、pdftotext/poppler、file、pzstd 等；这些工具和链接的 PDF 未核验/未安装，也不在冻结输入中。
- 版权：同 Commit [COPYING](https://raw.githubusercontent.com/BurntSushi/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/COPYING) 明确 Unlicense 或 MIT 双许可；[LICENSE-MIT](https://raw.githubusercontent.com/BurntSushi/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/LICENSE-MIT) 和 [UNLICENSE](https://raw.githubusercontent.com/BurntSushi/ripgrep/4649aa9700619f94cf9c66876e9549d83420e16c/UNLICENSE) 均实际核验。可采用已确认的 MIT 归档口径并保留版权/许可，外链图片和 PDF 的权利不自动随仓库许可覆盖。
- 科研理由：不同主题、默认规则、显式覆盖、代码与输出示例在长文中交织，适合观察窗口边界、信息筛除、重复抽取与成本放大。
- 混杂：指南假设 Unix；Basics L35–42 示例下载的是 0.7.1 源码，而文件快照是 14.1.1，示例行号/目录不能移用于当前源码。环境 ignore/config、终端颜色、并行输出、编码和预处理工具都会影响执行。保留完整原文，不能为预算静默裁掉后半段；超预算则记录容量删失，不宣称完成最终 Skill 质量审计。

### 3.6 两份备选的核验记录

**qsv join**：官方 [join.md](https://raw.githubusercontent.com/dathere/qsv/257ae7b38738688138dc430c2ccb4eef8766f3fc/docs/help/join.md)，同 qsv Commit / package 24.0.0 / MIT，发布日期 UNKNOWN。SHA-256：5b67ce4696f3d2e35f6082c31f64ca8df8e5730ac401ebf226477b3b3f3c22e7。5,687 字节、85 行，4 表；章节为 Description、Usage、Arguments、Join Options、Join Key Transformation Options、Common Options。适合 CSV 关联/反关联/半关联 Skill。默认 inner L16–17、忽略首尾空白与默认大小写敏感 L19–21、空键与 --nulls L60、anti/cross 对 keys-output 的例外 L61 都有原文证据。获取需联网，生成不需 qsv；行为验证工具当前未在 PATH 找到。外部 select 语法、重复键、null 和两输入顺序会形成依赖/歧义；与 sort 及 Case001 同结构，不能增加同等程度的格式代表性。按固定优先级作为替换选项，不能看到失败结果后偷偷换样本。

**CPython venv**：官方 [venv.rst](https://raw.githubusercontent.com/python/cpython/8183fa5e3f78ca6ab862de7fb8b14f3d929421e0/Doc/library/venv.rst)，v3.13.9 指向 Commit 8183fa5e3f78ca6ab862de7fb8b14f3d929421e0，发布日期 UNKNOWN；标签及 Commit URL 哈希一致。31,711 字节、749 行、1 张 grid 激活表；SHA-256：3e8d42ab6036140ab7d2bd6a4f51b39a472fe6fad1786e7c23dbca796ecac440。适合虚拟环境创建/选项/平台激活 Skill；已有目录复用 L71–79、--clear 清空已有内容 L127–129、--without-pip L135–137、--upgrade-deps 联网更新 L143–145 有明确支持。获取需联网；当前 Python 3.13.9 存在，但未创建环境或验证 venv，升级依赖可能需 PyPI，Windows 激活可能受策略影响。L59 include 引用的是平台可用性片段，**不是核心创建流程缺失**；API 与 EnvBuilder 示例混合也增大审计范围。需要预先确定“单原文件”边界，不能默默展开 include。[固定 LICENSE](https://raw.githubusercontent.com/python/cpython/8183fa5e3f78ca6ab862de7fb8b14f3d929421e0/LICENSE) 说明文档采用 PSF License Version 2，文档代码示例另有 PSF/0BSD 双许可，不能把整章都视为0BSD。归档保留许可/版权及适用变更说明。本轮只把它列为备选，不创建/清空任何虚拟环境。

## 四、无模型结构检查与容量含义

本轮仅在内存调用原版 parse_sections_from_text、DocumentRecord 与 build_windows_for_record(strategy=recommended,max_section_chars=10000)，不调用 LLM、完整 Ingest、Extract、Compile、Register、注册表或 store，不写中间产物。源文件通过字节哈希核对后显式 UTF-8 解码；第一次管道非 ASCII 字符受编码影响的结果已弃用，以下是重核结果。

| 推荐案例 | 规则式章节数 | 规则式窗口数 W | 原文字符数（strip 后） | 窗口字符长度 |
| --- | ---: | ---: | ---: | --- |
| Case002 sort | 6 | 1 | 5,270 | 1,277 |
| Case003 cp | 6 | 1 | 6,005 | 1,542 |
| Case004 reset | 1 | 4 | 19,124 | 1,389；918；2,297；374 |
| Case005 GUIDE | 35 | 23 | 40,688 | 合计18,801；单窗8–2,351 |

这些是**结构诊断，不是四次生成结果，不是正式 LLM 大纲下的窗口预测**。四文档均满足源码的 outline 候选触发条件；现有配置会尝试大纲模型，正式划分仍为 UNKNOWN。窗口字符合计不是规则覆盖率，不能用长度比代替语义评审。

可观察的结构风险：

- sort 的该规则式窗口包含简介、Usage、导航等，但三张选项表不在窗口文本中。说明表格遗漏值得跨案例检查，**不等于已证明未来正式运行同样遗漏**。
- cp 的该窗口保留 L54–83 的主要条件分支和链接规则，但所有权、父目录限制、tar 约束等并未完整进入。不能因为“有一个窗口”就认定原文规则全覆盖。
- Git 的非 Markdown 章节标题在该纯解析路径下未形成七节，作为单节再拆出四窗；正式 outline 能否恢复结构 UNKNOWN。
- GUIDE 的35个规则式章节包含正文枚举和代码块注释，如配置示例中的说明被当成标题。正式 outline 可能纠正，也可能改变窗口/调用量；需要保留真实模型大纲和每个窗口审计记录。

代码依据：ingest.py L843 的纯解析入口、L1016–1037 的正式大纲分支、L1117–1121 的窗口调用；windowing.py L270–284 的段落过滤和 L633–639 的默认 2,400 字符窗口。配置 max_chars_per_chunk=6000 **不能当作当前推荐 Ingest 窗口上限**，官方此处没有传入该值。

## 五、付费前配置核验、调用规模与分批计划

### 5.1 当前配置核验结果

| 项目 | 已核验事实 / 局限 |
| --- | --- |
| 模型/端点 | DeepSeek；OpenAI-compatible provider；https://api.deepseek.com；deepseek-flash。Case001 请求和返回均该模型标识；本轮没有访问模型 API |
| 公开服务文档 | 2026-10-11 核验的[官方模型与价格页](https://api-docs.deepseek.com/quick_start/pricing/)列出该模型名、端点和思考模式；当日别名对应 DeepSeek-V4.1-Flash。别名不固定权重版本，Case001 响应的同名字符串也不能证明以后模型内部版本相同 |
| 思考模式 | connector_factory=degradation_lab.provider_adapter:build；thinking_mode=disabled；适配器只加 thinking 参数，保留原版阶段预算，不改提示词/模型输出 |
| 长度与传输 | max_tokens=16384、max_input_chars=100000、timeout_s=180；四份原文均小于该输入字符限，但实际请求包含提示词、metadata、上下文，不能用原文长度保证不被截断 |
| 流程 | extract_strategy=recommended；section_outline_mode=llm；max_candidates_per_unit=4；max_units_per_document=0（不限制）；extract_workers=1；extract_retries=1；回退/repair/其它阶段 retry 也会增加调用 |
| 分块与速率 | max_chars_per_chunk=6000、overlap_chars=300、max_section_chars=10000；retrieval_score_threshold=0.3；10次/60秒。不能由这组参数计算出正式窗口数量 |
| 成本观察预算 | max_http_calls=32、max_observed_total_tokens=200000，每 run 独立；不是整批预算。Token 阈值在下一次请求之前检查，最后一条响应可能超阈值；usage 缺失会削弱观察 |
| Register 实际预算 | versioning.py L69–75、L106–140：无检索命中决策256、完整决策768、hierarchy128；不能由16384推断 Register 也获16384 |
| 凭证/账单 | 只检查 DEEPSEEK_API_KEY 是否存在，结果为存在，未显示值；是否可用、余额、授予额度、账户价格/账单均 UNKNOWN |
| 本地环境 | validate/list/plan/既有 verify 均成功；Python 启动出现“Failed to find real location”提示但退出码0，不据此宣布环境不可用。Git 2.53.0.windows.3、rg15.2.0、Python3.13.9；qsv/docker 在 PATH 未找到。未安装任何工具 |
| 官方/包装层偏置 | 任意工具 domain_type 会使用默认 taxonomy 的回退逻辑，不自动去除模板中的 therapist/intervention 用语。prompts.py L69–78、L192–196 及 windowing.py 领域标记值得持续检查；本轮不修复 |

### 5.2 预计调用规模：分清历史记录、情景估算与停止阈值

已观察 Case001：18 HTTP = 1 outline + 2 window planning + 4 draft expansion + 4 compile + 4 register + 3 hierarchy；prompt 49,171、completion 8,301、total 57,472 tokens。简单复制四次会是72次/229,888 tokens，**这只是历史参照，不是长文新案例预测**。

正常首次成功、无 repair/retry 的简化模型为：

N ≈ O + W + D + G + K + H

O 是大纲调用，W 是规划单元数量，D 是展开草稿数，G 是编译组数，K 是待注册 Spec 数，H 是导航/层级综合调用。数量不能由 source_id 或字节数直接确定；Compile 不保证每 Draft 恰对应一 Spec。以下只做容量敏感性分析，假设 O=1、H=3、每窗口1或4草稿且 G=K=D，使用第四节的规则式 W：

| 案例 | 每窗1草稿情景 | 每窗4草稿情景 | 在现有32次预算下的判断 |
| --- | ---: | ---: | --- |
| Case002 | 8 | 17 | 可优先试点；若正式划分/repair增加仍可能超预算 |
| Case003 | 8 | 17 | 可在 Case002 审计之后执行 |
| Case004 | 20 | 56 | 不能保证完整生成；须单独核对容量 |
| Case005 | 96 | 300 | 长文高风险；不建议当作32次可完整跑通的普通案例 |
| 四例合计 | 132 | 390 | 非置信区间、非硬上界、非已经发生的调用 |

零草稿、分组/合并、正式 LLM 大纲、fallback、重试都会改变上述数值；这些估算不是把“最多4候选”误当成“每文档4技能”。现有配置若四 run 均执行，HTTP 观察层最多128次；200,000×4=800,000仅是软停止阈值之和，不是收费 Token 硬上界，也不保证四 run 完成。短文阶段经验不能线性外推到长文。

**预计实际收费金额：UNKNOWN。** 原因是尚无新请求、输入/输出 Token、cache-hit/miss、执行时段/价格、失败请求收费和账户扣费结果。官方公开单价已可查，但不能据其编造本次总价；本轮未支付生成费用。下一轮按实际 prompt/completion/cache 分类 usage 与当时官方单价核算估算，最终以供应商账单为准；execution.billed_cost 目前为 null，不等于0。现有代码没有货币硬上限，应由用户明确批准调用/Token上限及账户侧花费限制。

### 5.3 分批执行顺序与审批门槛

1. **准备批，仍不调用模型**：获准后把固定 Commit 原文与许可证归档，追加来源/案例定义及原子规则清单；每案只定义 clean，一个原文输入。运行 validate 和四案 plan，检查来源哈希、字符编码、短路径、实际解析的输入数量、配置与审批预算。冻结审核口径，先处理规则歧义，不按模型输出倒改清单。
2. **第一批：仅 Case002，repeat=1**。复用 deepseek_flash.json，批准32 HTTP/200,000 observed-token软阈值；完成或失败都保存原样产物。立即逐阶段审计，报告真实调用、Token、截断和遗漏；不自动再跑 Case001。
3. **第二批：仅 Case003，repeat=1**。在第一批结果及用户确认后继续，仍使用同一基础配置。首批出现模板污染/默认注册不自动修代码，保留作为原版基线观察；预算/环境失效则先报告。
4. **第三批：Case004**。付费前单独确定容量：若维持32次，则允许得到预算删失运行但不能宣称最终技能审计完成；若批准增加容量，只新增版本化 lab 配置，保留模型、提示词、窗口策略和官方 Register 256/768/128。不覆写原配置；记录是否触发旧阈值，避免混入语义比较。
5. **第四批：Case005，单独容量审批**。完整文档预计显著高于默认预算；不能静默切成短文或增加 max_units 限制。可另行批准容量配置，或明确选择预算压力试验，或在生成前按预定备选替换并更新协议。不同选择回答不同问题，不能事后混报成四次完整 Clean 生成。

对任何新增容量配置，本轮不预先创建或擅定上限；四份完整原文的选样结论与“默认预算能否完成”是不同决定。不得一次批准后自动把失败样本改输入/改模型重跑。重复生成用于随机性评估可作为后续单独计划，此次准备只建议每文档一个初次 Clean run。

## 六、统一的 Clean 生成质量审计协议

### 6.1 先冻结评价对象与审核清单

每文档先枚举全部操作章节的候选原子规则，形成“条件→动作/参数→结果→例外”的清单，标注原文行号、格式、依赖及歧义。第三节只是起始例子，**不是四文档完整金标准**。主分析采用预先审核的、原文可明确支持的规则；歧义规则另表报告，不在生成后挑选容易成功的规则。

独立人工审阅建议至少两人，对同一判断标准审核并保留分歧；Codex 初稿只提供证据和初步分类。有明确日期/审核者/材料哈希后才可记录 human_annotated。允许一个文档生成多个技能；判断最终整套技能的规则覆盖时去重，同时分别评审每个技能声明范围，不能要求每个微技能包含全章，也不能借拆分隐藏整套遗漏。

### 6.2 逐阶段审核表

| 边界 | 必查内容 | 证据与判定方式 |
| --- | --- | --- |
| 原文→加载文本/Document | 字节快照、编码、raw_text/section 是否保留参数表、代码、状态表、否定、例外和章节前提 | 来源哈希+run 输入哈希；parsed_text_units、ingest result、Document/section 文本；语义与格式分别记录，不用字符长度代替覆盖 |
| Document→Window | 每条规则的条件和结论是否一起可见；表格列对应、nested list 父条件、代码/输出边界是否破坏；哪些规则未进入任何可见提取载荷 | 逐规则匹配实际 window.text 与传给 Extract 的 section/context/excerpt；窗口 span 跨过某行不等于该行文本存在。允许多窗共同支持，缺失条件不能算完整覆盖 |
| Window→SupportRecord→SkillDraft | 证据可见却未抽取、无能力窗口的合理空计划、正/负操作混淆、默认/优先级/参数/范围改变、source 未支持补充 | 原始 planning/expansion 请求响应、窗口、support.excerpt、draft 字段/正文。空计划记录内容与模型结果，不能仅据“无Draft”宣布错误；SupportRecord 大段引文不证明每句话被支持 |
| Draft→Spec | 编译分组、去重、合并、拆分后条件/步骤/示例/输出契约变化；是否继承上游错误或新引入错误 | source_draft_ids/support_ids 只定位，再比较真正字段/文本和 compile 原始响应。逐原子规则建立多对多关系，不强制一一映射 |
| Spec→Register→正式 SKILL.md | 注册 action/target/resolved_skill 是否改变语义；仅计正式程序技能而非导航/镜像副本；Evidence Manifest 引文是否保真 | 原始 classify 请求响应、registration 决策、真实 canonical Users/.../SKILL.md 和 evidence_manifest.json；核对 Spec body 与正式正文，若有变化逐项解释 |
| 最终内部与跨技能一致性 | procedure、decision rules、禁用条件、例子和 Output Contract 对同一条件是否一致；参数是否能构成操作；重复规则是否冲突；therapy 模板残留/无依据限制 | 人工语义审阅、文件/行号/字段/ID及必要短摘录；不能用关键词命中、标题相近或工程 PASS 替代 |

生成质量与执行可验证性分别报告。此阶段即使未安装 qsv/Docker，仍能审核原文支持与内部矛盾；不能因此称命令行为已经验证。若未来少量隔离行为核验用于消歧，它是生成质量证据补充，不自动变成 DirectDoc/FrozenSkill 的核心研究。

### 6.3 Register 截断、解析与默认行为专项

对每个 classify_change 和 hierarchy 请求记录：run/call/Spec ID、stack、分支/检索命中、payload.max_tokens、原始 completion、finish_reason、原始根 JSON 是否完整且 schema 合法、官方容错解析值/类型、最终 action、reason、target、resolved_skill 与 fallback。

重点区分四件事：模型明确输出 create；容错解析得到局部数组/非对象后变成空 dict；根对象 action 缺失/非法默认 create；合法 action 被后续局部重定向/限制改写。versioning.py L1371–1384 明确有 maybe_json_dict 和默认 create，core/llm_utils.py/ autoskill/utils/json.py 的 repair/片段解析必须结合原始响应审核，不能将 HTTP200 或 registration.actions.create 数量当作模型有效决策率。

报告每个 run 的 length 次数/相关调用数、严格根对象合法数、默认/回退数及适用分母。length 与默认 create 同时出现也不证明“若不截断必然 discard”；反事实仍 UNKNOWN。不修复现有响应、不增加官方阶段预算、不重发请求来“补齐基线”；这些改变只能在另行批准的改进组研究。

### 6.4 评价记录、指标与归因边界

规则级矩阵至少包含：rule_id、原子行为、源文件/行号、适用条件、Window、Support、Draft、Spec、正式文件、各阶段判断、具体错误类型、最早可观察异常位置、审核者与不确定性。新增句子级对照可以写研究侧报告，不向官方生成产物增加或覆盖字段。

现有评价 schema 中，明确遗漏/矛盾对应 incorrect 并填写 rule_omission/condition_error 等；unsupported 补充用 generated_addition 范围单独记录；uncertain 不作 correct/incorrect。没有原文支持位置时不伪造正向 evidence：注明“相关章节是审核范围而非支持引文”，无法诚实落入现有 schema 的附加断言先保留在报告。

建议报告下列分开的描述性指标，不合成未定义的“效果分数”：

- 工程状态、阶段数量、异常、预算中断及是否完成；
- 已审核规则数、完整保留/遗漏/矛盾/不确定数，按文档和规则类别报告；条件正确率与参数正确率另列，明确去重及分母；
- 每阶段新增/继承/修复/仍无法归因的语义问题；输出覆盖率与对实际输出断言的来源支持率分开；
- 每技能内部矛盾、跨技能矛盾、无依据附加断言和模板残留；
- 注册根对象合法率、截断/默认行为、HTTP/repair/retry次数、prompt/completion/cache/total Token与实际费用状态。

只凭阶段 ID 不做错误因果归因。可以说“异常最早可在某个真实输出观察到”；若原文有规则而实际全部提取载荷没有该语义，可定位暴露缺口，但不能推断模型收到完整证据后一定正确。下一阶段相关/无关退化要在**同一文档内**固定生成配置与审核清单并配对比较，不能用 Clean 跨文档差异当作退化效应。五份 Clean 小样本也不能给出普遍发生率、显著性或改进收益。

## 七、关键风险、UNKNOWN 与下一轮最小范围

| 风险/未知 | 处理原则 |
| --- | --- |
| 代表性与相关样本 | 有目的结构分层，不是随机语料样本；qsv两文档相关，规则/技能/调用不能当作独立文档样本 |
| 原文质量/版本/外部引用 | Commit/哈希已核验；提交和发布日期未独立核验，均 UNKNOWN；不跟随 master/外部网页补证据，单文件缺口写入边界说明 |
| 格式和语言 | Markdown/AsciiDoc 及英源/生成语言可能混杂；记录提示词模板偏置，不把它算成文档退化 |
| 模型别名漂移 | 当前公开标识已核验，未来具体权重/服务更新仍 UNKNOWN；记录日期、请求/返回标识、配置和响应，不声称完全冻结供应商模型 |
| Token/预算选择性失败 | 完整生成与 budget-censored 分开；失败样本也保留。默认预算不适配长文时禁止事后裁文、只报成功样本 |
| 环境和行为 | PATH检查不等于全机器安装审计；匹配版本工具、Docker daemon、Unix辅助工具、行为验证均未完成；安装/执行需另行授权 |
| 版权/公开发布 | 仓库许可已核验，例外、外链媒体、生成 Skill 的衍生权利判断和最终发布合规未完整验证，相关项 UNKNOWN |
| 人工标注可靠性 | 初稿不是金标准；补独立审阅和分歧记录。不同结构的规则数不同，不能直接合并一个 micro 平均掩盖长文权重 |

下一轮建议只批准以下最小工作：按本报告固定来源登记新案例，先完成人工原子规则清单与无模型 plan；**仅执行 Case002 一次原版 Clean 生成并完整审计/报告实际成本**。然后由用户确认 Case003 及中长文容量路线。官方修复、退化算子、Agent/Oracle、大量重复运行和模型切换均不包含在此范围。

本轮在提交本报告后停止。需要用户批准的是：四份选样是否接受；首批是否仅 Case002；长文是完整生成容量路线、明确预算压力路线，还是生成前替换备选。没有回答不代表授权调用模型。

## 八、核验方法与审查方法来源

官方原文与许可证通过只读 HTTPS 获取到内存并核验状态/原始字节；版本使用官方 git ls-remote 发布标签/分支，保留 peeled Commit。GitHub REST commit 接口本轮403限流，部分网页检索 cache miss、TLS/超时失败后以直接官方原文核验成功；未把失败的404正文计入文档规模。本报告源链接均指向支持相应条目的官方材料，非搜索结果页。

只读验证命令实际使用 scripts/lab.py 的 validate、list、Case001 plan、verify（无 --out）。它们确认当前基线可读取，并不验证尚未注册的 Case002–Case005。未运行测试夹具生成，也未把无模型窗口结构结果保存成真实运行。

审查采用 scientific-critical-thinking 的构念区分、预先规定规则/分母、混杂与选择性失败审查；未套用不适合此小样本工程案例的临床证据等级或统计显著性结论。方法参考：Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)。本轮核验 arXiv 当前记录为2026-09-02修订版本；该方法引用不代表本文实验结果已获外部验证。
