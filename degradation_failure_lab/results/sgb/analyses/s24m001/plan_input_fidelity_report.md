# Scrapy024 Plan 输入保真

日期：2026-10-23；本轮模型调用0。**旧历史真实请求不保真；独立修复副本的待发送请求通过目标块保真检查。后者还没有发送给模型。**

## 1. 输入冻结和判断范围

实际源：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m001\inputs\input001\feed-exports.md`。

| 表示 | SHA-256 |
|---|---|
| 原始字节 | `a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d` |
| LF规范化文本 | `146fb31cfd581caf9db541241170395ce73e47148e105f9ccd8965d27e157042` |
| 历史raw_text（去末尾LF） | `17dd35bd2491dc078ccbc0783844256f3ba57dc66420fbabcbbbc7797f4f1660` |

来源版本是SkillGenBench `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。`data/raw_sources/scrapy/<commit>/feed-exports.md` 和冻结的generation/sources/topics副本保持相同原始哈希。本轮未补写、精简或重新下载Clean材料。所有行号基于此冻结文件。

`round2/fidelity.py` 的外部门禁使用源文438–449行的**整块词序内容**，只折叠空白，不只搜索FTP=True。将参数名、FTP默认值、APPE或例外删除/改错都必须失败。这是针对已确定研究规则的输入检查，非通用预处理中的特例保留。

## 2. 逐阶段保留情况

| 证据对象 | 原文→旧sections | 旧windows/真实Plan请求 | 修复sections | 修复windows/待发送请求 |
|---|---|---|---|---|
| FTP标题、URI、连接说明（124起） | Outline已选择，建节时整节被作者规则删除 | FTP小节example URI缺失；文档其他位置的FTP示例不能替代其上下文 | 完整FTP节恢复 | 窗口8保留FTP标题、URI和连接说明 |
| 重复支持136–137（本backend overwrite默认True） | 随FTP节删除 | 相同字面句出现在旧w9/w11，但上下文是S3/GCS，不证明FTP支持存活 | 原FTP节恢复 | 不能确认在FTP语境中保留；w11/w13同句仍有FTP/S3/GCS三个原文候选，附近上下文指向S3/GCS。不要将文本命中误记为FTP证据 |
| overwrite定义438–439（True覆盖、False追加） | FEEDS节保留 | 所属379字符段落被筛掉，所有18个Plan均无定义 | 保留 | 379字符段落进入w18及待发送excerpt |
| 默认表441–443（Local=False、FTP=True） | 保留 | 95字符段落保留于w14/HTTP015；但前邻是item_filter，参数作用域缺失 | 保留 | 与overwrite定义连续位于w18 |
| FTP追加例外445–446（可能不支持APPE） | FEEDS节保留 | 所属413字符段落被筛掉，所有18个Plan均无APPE | 保留 | 与默认表连续位于w18 |
| 其他后端例外447–449（S3/GCS不追加、stdout不覆盖） | 保留 | 与413字符段落一起丢失 | 保留 | 原文顺序保留，未把“不支持追加”改写成FTP普遍不支持 |

修复保住**一个完整主规则窗口**，不声称源文每处重复支持或整份文档全部保真。严格分组会继续选择性丢段。`round2/patched_filter_trace.json` 显示FTP重复支持段通过320字筛选，但它的独立FTP语境未进入最终窗口；该记录中的window_text_matches只说明字面相同，明确带有重复来源警告。

原始作者和段落判定的代码与设计意图见 [preprocessing_fix_report.md](D:/AS/AutoSkill-main/degradation_failure_lab/results/analysis/s24m001/preprocessing_fix_report.md)。历史分支未保存逐项日志，本轮源文→section→window使用原实际函数和保存Outline响应重放，旧输出与历史逐字段一致。

## 3. 18份真实历史请求复核

`round2/baseline_ok/historical_plan_checks.json` 逐项记录HTTP编号、匹配窗口序号、完整正文SHA、请求文件SHA、字符数、标题、围栏数、raw message、finish_reason、usage。复用前次 `evidence/window_request_map.csv` 的18行详细ID和成本表。

- HTTP002–019逐一对应窗口1–18，excerpt+span匹配各只有一个；18个正文/请求哈希均不同，窗口不空；不是只发送ID/摘要。
- 18个输入有共享段落，但不存在重复整个窗口；8/18 ID相同不能解释为相同文本。只用ID做证据键会覆盖，改用序号+正文SHA复核。
- 所有请求都有真实excerpt，标题/section字段保留；但正文选择性删除了代码、定义和例外。源文围栏24，旧窗口合计6；不能据此计算独立代码保留率。
- 原始响应均为单choice，content逐字 `{"skills": []}`，finish_reason=stop，每次5输出tokens。没有未保存的额外choice/reasoning字段，无法读取模型内部决策理由。
- 原始请求中无完整438–449块；目标值表只在HTTP015保留。没有“非空候选在后续被过滤为零”的证据。

## 4. 冻结的单窗口待发送证据

文件均位于 `D:\AS\AutoSkill-main\degradation_failure_lab\results\analysis\s24m001\round2\patched_ok`。

| 项目 | 值 |
|---|---|
| 方法 | lab-preprocess-v1；原版Plan提示词和解析未改 |
| window ordinal / ID | 18 / `08edca37-0bfc-5bfc-bcb2-1e04d7ba55b0` |
| 正文长度 | 1,552 Unicode字符 |
| 正文SHA-256 | `50633e25c245a5767379d5e04d7dbcb30913a51b4a5da9465b61091fd2e03b07` |
| 请求文件SHA-256 | `a3265af49b00d88538f90c49f56c71a88aec0ba87e1cf79da7d83d4ff1de81f1` |
| system prompt SHA-256 | `295ee9cd6633d30897b2028a7a53a4e9b06a399c40c29b78d99413f515629be6`，与全部历史Plan一致 |
| 源文映射 | 8个段落均有唯一原文匹配；按420–421、423、425–430、432–433、435–439、441–443、445–452、454定位 |
| 保真断言 | 完整438–449块进入序列化user.excerpt，包含前置“各feed定义的accepted keys和fallback”说明 |
| 模型执行状态 | 未发送；没有新响应；不是历史或真实模型验证结果 |

原有window.span不普遍等于源文件偏移：历史18份只有1份能直接切回同文。修复没有改变这套坐标系统。`single_window_source_map.json` 用保留词序、折叠空白的逐段匹配保存源offset/行号；保留所有候选而非武断指定来源。选中w18的8段均唯一，其余窗口仍可能重复/歧义。

源文语义应保持为：缺省FTP overwrite=True；显式False表示尝试追加，部分FTP服务器可能不支持APPE；不同后端支持能力分别描述。默认True不等于禁止用户显式False，也不等于所有FTP服务器都能追加。这些是后续人工语义核查的判据，本轮没有用模型改写它们。

**问题A的局部验收通过：冻结目标规则及必要上下文已在修复后的待发送输入中。问题B未执行：模型是否认可为可提取资产仍未知。**
