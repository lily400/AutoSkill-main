# Scrapy024 离线预处理修复

日期：2026-10-23。版本：**lab-preprocess-v1**。只改变独立副本的两个源文件；原版 Anything2Skill `94c47ca488d4ba4117d20272e66d49b9877e68cf`、原数据和 s24m001 保持不变。模型请求0。

## 1. 三个最小修改

官方代码根：`D:\AS\AutoSkill-main\AutoSkill-main`。补丁、逐文件前后 SHA 位于现有审计目录 [round2/preprocessing.patch](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m001/round2/preprocessing.patch)、[patch_manifest.json](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m001/round2/patch_manifest.json)。

| 问题与原设计意图 | 误判与最小修复 | 测试及剩余风险 |
|---|---|---|
| `AutoSkill4Doc/ingest.py:109–126 _looks_like_front_matter_heading` 排除作者/联系信息；496–556建节，528整节跳过 | 作者式标题长度≤24、去数字空格等后长度2–12，标题带数字/逗号或 preview 有@就被判作者；FTP正文前240字符有URI user-info。仅在**判定用 preview 副本**中去除 inline code 与 scheme://URI，再使用原规则；正文不改、不删URI | FTP、SSH、API内嵌邮箱样例不误判；真实裸邮箱作者、带脚注数字作者、Author/Abstract仍过滤。它不解决所有数字型API标题、联系人关键词或未标记裸邮箱的歧义；把真实作者邮箱放在inline code也可能减弱过滤。没有取消全部元数据规则。 |
| `document/windowing.py:114 _BULLET_RE`、257–285段落筛选希望保留过程/列表，排除长叙事和对话 | 旧正则 `^` 只看段落开头；介绍句后面的 `-` 不被识别，379/413字符段落触发>320丢弃。只加 `re.MULTILINE`，识别段落任意行的列表项；320阈值、对话过滤和关键词保持 | 保住默认参数及异常条件；通用长参数列表、缩进列表测试通过。没有列表/关键词的长技术叙述仍可能丢失；多行列表叙事可能增加保留量。不能宣称全库文档保真已修复。 |
| `document/windowing.py:452–502 _window_from_blocks` 原 UUID 希望可稳定续跑 | 原 key 仅doc、heading、局部段落序号、strategy，跨chunk可相同。key追加start/end及UTF-8正文SHA-256 | 同文同位置ID稳定；不同位置/内容不同ID；21个窗口实际写入、关闭重开后仍21个。全体ID发生版本迁移；不得复用旧run检查点。span仍是内部坐标，原文映射需旁路证据。 |

本修复没有在通用处理代码中写入 FTP、Scrapy、overwrite 或特定行号；目标行号只出现在**实验外部保真断言**，用于核验冻结研究规则，不参与文本生成。

## 2. 真实源文前后比较

| 项目 | 官方路径离线重放 | 独立修复副本 |
|---|---:|---:|
| sections | 35 | 36 |
| FTP section | 0 | 1 |
| windows | 18 | 21 |
| unique window IDs | 17 | 21 |
| 438–449完整规则同窗 | 0 | 1（窗口18） |
| 原始章节/窗口复现 | 与s24m001保存值逐字段相同 | 新方法输出，不冒充历史输入 |
| 正文代码围栏标记总数 | 6 | 6 |

源文有24个代码围栏标记；窗口有重叠与选择，标记计数不等于独立代码块保留率。修复不恢复全部代码片段。FTP重复支持136–137在section恢复，但仍未获得独立FTP语境窗口；主规则438–449已完整通过。详见保真报告。

补丁只有约十余行差异，涉及两文件。patched ingest SHA-256：`b9b1f0ac8a7096ae41567902dbd4e031439a784f780eb269e46b9f66148730b2`；patched windowing：`5542cf56ac5e99bea393c754f40dc69c9a361f5a72fa11b28593f792c290f855`。准备脚本从164项运行快照逐文件验哈希后建立副本，不修改官方目录。

## 3. 测试证据

最终有效记录：`round2/baseline_ok/`、`round2/patched_ok/`、`round2/probe_contract/`。

- **基线14个新增测试方法：6通过、8方法失败，共10条failure记录（含3个URI子测试），errors=0。** 这是预期的缺陷复现，不是通过报告。
- **修复30/30通过**：14个新增测试 +16个原 `tests/test_document_windowing.py`，无失败、错误、跳过。包含实际源文+保存Outline重放、完整规则/例外门禁、ID唯一性、原版 IntermediateRunWriter 的21窗口保存及重新打开，以及准入代码本地样例。
- **单请求合同9/9通过**：fake transport、网络audit hook禁止socket。覆盖空计划、坏JSON、坏schema、name过滤、非空待语义复核、超时、HTTP429/redirect、截断、响应封装错误；每例重复执行到同输出目录被拒绝。
- **本轮没有真实模型、真实Agent或真实生成成功结果。** 测试中的候选对象只在内存使用，没有写正式SKILL.md。

原测试覆盖了作者/摘要/参考文献、对话筛选、层级/Outline与长章节分块（test_document_windowing.py:31、60、279、298–424、476起），没有“短技术标题+URI的@”“介绍句后长列表”“跨chunk相同局部段号”的断言。因此本例未被原套件拦截。这是覆盖缺口分析，不能归因于作者故意忽略技术文档。

最初试跑含一个测试夹具末尾空格比较问题，以及Windows长路径 WinError206/扩展路径混用 WinError123；尝试沙箱临时目录又遇权限问题。最终只调整测试夹具和**本地测试临时路径**：在当前可写短路径创建专属目录，使用未改的原版 writer，打包 checkpoint_contract.zip 后清理自身临时文件。没有修改系统长路径设置/权限或官方 writer。失败尝试的已有日志保留在 round2/validation_attempts；它们不是通过证据。

## 4. 可重复零调用命令

以下输出目录必须不存在；换名重验，不覆盖已验收证据。Python使用现有环境，无需安装模型SDK或凭据。执行位置选实验室根目录，避免Windows长路径。

```powershell
Set-Location 'D:\AS\AutoSkill-main\degradation_failure_lab'
$audit = 'D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m001'
$run = 'D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m001'
$upstream = 'D:\AS\AutoSkill-main\AutoSkill-main'
python -B "$audit/round2/prepare_copy.py" --run $run --upstream $upstream --out "$audit/round2/recheck_copy"
python -B "$audit/round2/verify_offline.py" --run $run --upstream $upstream --baseline --out "$audit/round2/recheck_baseline"
python -B "$audit/round2/verify_offline.py" --run $run --upstream "$audit/round2/recheck_copy/patched_upstream" --out "$audit/round2/recheck_patched"
python -B "$audit/round2/test_single_window_probe.py" --bundle "$audit/round2/recheck_patched" --out "$audit/round2/recheck_probe_contract"
```

基线命令正常退出表示完成缺陷重放，必须读取其tests.json的失败数，不能只看shell码。修复命令遇测试失败直接非零退出，不生成可调用配置。所有检查在联网被audit hook禁止的进程执行；`single_window_probe.py`默认只有本地校验，只有后续获批后显式`--execute`才可发送一次请求。
