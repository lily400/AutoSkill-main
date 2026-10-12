# Clean 多案例规则级证据追踪

审计日期：2026-10-12。仅依据已保存 Clean 记录，无付费模型调用、无历史改写。  
本报告是初步语义审计，所有 CORRECT 均指来源规则在指定观察层次正确表达，不代表已执行通过。没有独立人工金标准或自动整体正确性证明。

## 1. 定位约定与证据边界

- C1–C5 为案例；RUN1–RUN5 为下节定义的运行根绝对路径；M1–M5 为官方 intermediate 根；SRC1–SRC5 为冻结来源。各案例 W／D／S／K／F 别名独立编号，不跨案例复用 ID。
- Hn 指本 run 的第 n 次 HTTP 尝试；准确文件为 RUNx\http\三位编号\request.json 和 response.json。如 C5 H27：D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r8ac019d9b468\http\027\response.json。
- response 中的文本字段：choices[0].message.content；request.messages 中 user 为 JSON payload。Plan 看 skills[slot-1]；Expand 看 skill；Compile 看对应 groups／skills 返回及阶段 SkillSpec。
- 原始规则／源行号针对 SRC 文本的 1-based 行。产物正文行号针对 canonical SKILL.md。JSON 以文件、字段、实际 ID 定位，不能把 JSON 内转义换行当 Markdown 行号。
- 原始文件索引、Window ID、Support ID、Draft ID、Spec ID 和正式技能路径见第 2 节。阶段列表：Mx\ingest\result.json 的 documents／windows；Mx\extract\result.json 的 support_records／skill_drafts；Mx\compile\result.json 的 skill_specs；Mx\register\decisions\<skill_id>.json 和 register\result.json。
- 冻结来源与 run 输入快照分别存在；Document.raw_text 为输入文本 strip 后内容；Window 是官方结构筛选，不是完整原文。分析者 rules.json 是待审核清单；新增 A 类原子规则只在本报告提出，不写回原 rules。
- 判断：CORRECT / OMITTED / CONTRADICTED / UNSUPPORTED / UNCERTAIN / NOT_EVALUABLE。未完成 run 的最终规则一律 NOT_EVALUABLE；另列 Draft 或 Ingest 已观察状态。错误阶段是“最早可观察”，不推断模型内部推理。
- “—”表示没有对应产物／没有该规则内容，不表示存在某个虚构 Support。某个技能有来源 Window 链接也不意味着窗口支持该技能每句话。

## 2. 全量运行、窗口、技能与调用索引

### C1：case001_qsv_select

- RUN1（运行根）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34`
- M1（官方中间目录）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\.runtime\intermediate_runs\20261011T153331_26f9a7a9`
- SRC1：`D:\AS\AutoSkill-main\degradation_failure_lab\data\raw_sources\qsv\257ae7b38738688138dc430c2ccb4eef8766f3fc\select.md`
- 输入快照：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\inputs\input001\select.md`
- Document ID：`9c83d04d-0209-59d7-8e84-066c2d8161fe`。字节 4795，源文档 179 行；SHA-256：`74e7ac8247d670bc5e351551a4bf76dd12f9de358dffaea5f593e2fd29cca384`。

| Window 别名 | 实际 Window ID | 正文字符 | Plan HTTP | 候选数 | Expand HTTP（slot 顺序） | 落盘 Draft |
|---|---|---:|---|---:|---|---|
| W1 | `245afa09-be7e-56de-9a7a-f895fd5aa81a` | 2363 | H2 | 4 | H3、H4、H5、H6 | D1、D2、D3、D4 |
| W2 | `7ad0d07f-a2a3-5552-a285-2e102136d0f9` | 465 | H7 | 0 | — | 0 |

候选数来自 Plan 原始回答；“未调用”不是空计划。

| Draft 别名／名称 | Draft ID | Support 别名／ID | Window | Plan→Expand | Spec 别名／ID |
|---|---|---|---|---|---|
| D1 CSV 列选择与重排 | `def5f116-bce7-54b1-afcd-cbfb3db8c337` | S1 `819cec2f-0f64-5faa-baec-06919fde83af` | W1 | H2→H3 | K1 `f4c4df75-6ea6-5d4d-b30c-d7e825084300` |
| D2 正则表达式列选择 | `0e55a3de-b1dc-50cf-93fb-2259c51f7403` | S2 `76983d71-789e-5f48-b781-ff2ec59ba71b` | W1 | H2→H4 | K2 `bd72bc3b-8c84-59c2-9fd4-5caba1a5350b` |
| D3 列排序与随机打乱 | `89f8089b-9739-5ad3-ae4e-f2298dd209c8` | S3 `df120f38-3d43-51b7-a677-74f37e20013f` | W1 | H2→H5 | K3 `500c276a-5f59-5af9-86f5-4c0fbf4ad1be` |
| D4 列名冲突引用 | `1bb58b76-1f3a-555d-ae51-b3173a8dcbc6` | S4 `01b26d5a-543b-550f-9b28-34d3399135f3` | W1 | H2→H6 | K4 `b0592fe3-a3d5-539a-af63-d33035c20003` |

| Spec / Final 别名 | 正式技能文件（canonical，准确绝对路径） | 版本 | Compile HTTP | Register HTTP |
|---|---|---|---|---|
| K1/F1 CSV 列选择与重排 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\csv-列选择与重排\SKILL.md` | 0.1.0 | H8 | H12 |
| K2/F2 正则表达式列选择 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\正则表达式列选择\SKILL.md` | 0.1.0 | H9 | H13 |
| K3/F3 列排序与随机打乱 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\列排序与随机打乱\SKILL.md` | 0.1.0 | H10 | H14 |
| K4/F4 引用冲突列名进行 qsv select | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\引用冲突列名进行-qsv-select\SKILL.md` | 0.1.0 | H11 | H15 |

### C2：case002_qsv_sort

- RUN2（运行根）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54`
- M2（官方中间目录）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\.runtime\intermediate_runs\20261011T222240_1c1d949c`
- SRC2：`D:\AS\AutoSkill-main\degradation_failure_lab\data\raw_sources\qsv\257ae7b38738688138dc430c2ccb4eef8766f3fc\sort.md`
- 输入快照：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\inputs\input001\sort.md`
- Document ID：`e52fb956-42d7-5d59-b850-b7c9b757c5d9`。字节 5381，源文档 72 行；SHA-256：`05bfbd4f41c7a4e55c3aeab71f5bbe8dd38659f4d00c5970c557df1f3feac693`。

| Window 别名 | 实际 Window ID | 正文字符 | Plan HTTP | 候选数 | Expand HTTP（slot 顺序） | 落盘 Draft |
|---|---|---:|---|---:|---|---|
| W1 | `939e2088-3c3a-5b52-a18d-6e50ca62de2b` | 1277 | H2 | 3 | H3、H4、H5 | D1、D2、D3 |

候选数来自 Plan 原始回答；“未调用”不是空计划。

| Draft 别名／名称 | Draft ID | Support 别名／ID | Window | Plan→Expand | Spec 别名／ID |
|---|---|---|---|---|---|
| D1 CSV 内存排序执行 | `3e450260-60ae-5f6e-9f31-b68874db4af9` | S1 `e3a9b88d-57eb-556f-b008-f905272777f7` | W1 | H2→H3 | K1 `353ba11e-1351-58c3-bb24-f91c7e24da8d` |
| D2 大文件外存排序切换 | `740004e0-dbb4-5493-95b1-f06253756552` | S2 `3afebf9e-2810-5f4f-ac21-11e1a450191a` | W1 | H2→H4 | K2 `cc5a002d-6830-5192-b841-d8233e6ce4e3` |
| D3 排序结果校验 | `542ae1df-a500-5424-b9cf-f43c219fc254` | S3 `fc70e9a3-1dcd-5a3f-aebb-9f7a9f0dfb78` | W1 | H2→H5 | K3 `7ab97840-0c8c-5685-88d2-36bdb1faefea` |

| Spec / Final 别名 | 正式技能文件（canonical，准确绝对路径） | 版本 | Compile HTTP | Register HTTP |
|---|---|---|---|---|
| K1/F1 CSV 内存排序执行 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\Users\docskill\csv-内存排序执行\SKILL.md` | 0.1.0 | H6 | H11 |
| K2/F2 大文件外存排序切换 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\Users\docskill\大文件外存排序切换\SKILL.md` | 0.1.0 | H7 | H12 |
| K3/F3 排序结果校验 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\Users\docskill\排序结果校验\SKILL.md` | 0.1.0 | H9 | H13 |

### C3：case003_docker_cp

- RUN3（运行根）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59`
- M3（官方中间目录）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\.runtime\intermediate_runs\20261011T222517_541bbc3a`
- SRC3：`D:\AS\AutoSkill-main\degradation_failure_lab\data\raw_sources\docker\e4078058de0a9f4d5cb65f946f4b8a090e19fffe\container_cp.md`
- 输入快照：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\inputs\input001\container_cp.md`
- Document ID：`f743e24b-67d6-533d-a213-19a964b22100`。字节 6006，源文档 131 行；SHA-256：`808ca152d4ea8bb4dbb12d31dcff15e9d3c958b85eaab4ccd4026cef1f14f764`。

| Window 别名 | 实际 Window ID | 正文字符 | Plan HTTP | 候选数 | Expand HTTP（slot 顺序） | 落盘 Draft |
|---|---|---:|---|---:|---|---|
| W1 | `770febe2-ee74-5a3f-bcaf-4fe54846c365` | 1542 | H2 | 2 | H3、H4 | D1、D2 |

候选数来自 Plan 原始回答；“未调用”不是空计划。

| Draft 别名／名称 | Draft ID | Support 别名／ID | Window | Plan→Expand | Spec 别名／ID |
|---|---|---|---|---|---|
| D1 docker cp 路径语义判定 | `94ede446-63eb-59cd-8484-f6be4a4e6055` | S1 `49d718ba-5350-5ed1-9b11-565cd8657fbd` | W1 | H2→H3 | K1 `0be52a4b-b68d-5166-a0c1-668834d1f64a` |
| D2 docker cp 符号链接复制策略选择 | `d9e1ef03-59a6-5d0c-a0fd-bfddb5ca00d7` | S2 `baeb1e83-f43b-50f7-a46d-a0c734012431` | W1 | H2→H4 | K2 `23370d93-9d3f-5142-bfed-e6ff22cb9b36` |

| Spec / Final 别名 | 正式技能文件（canonical，准确绝对路径） | 版本 | Compile HTTP | Register HTTP |
|---|---|---|---|---|
| K1/F1 docker cp 路径语义判定 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\Users\docskill\docker-cp-路径语义判定\SKILL.md` | 0.1.0 | H5 | H7 |
| K2/F2 docker cp 符号链接复制策略选择 | `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\Users\docskill\docker-cp-符号链接复制策略选择\SKILL.md` | 0.1.0 | H6 | H9 |

### C4：case004_git_reset

- RUN4（运行根）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_reset\clean\rfad98180a468`
- M4（官方中间目录）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_reset\clean\rfad98180a468\SkillBank\.runtime\intermediate_runs\20261011T223020_ac1d4158`
- SRC4：`D:\AS\AutoSkill-main\degradation_failure_lab\data\raw_sources\git\a52a24e03c8c711f1d5e252fba78f9276908129b\git-reset.txt`
- 输入快照：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_reset\clean\rfad98180a468\inputs\input001\git-reset.txt`
- Document ID：`eb088018-f583-5cbe-a0ad-6c06ee86e16c`。字节 19125，源文档 506 行；SHA-256：`372b401b153142441c139098f9de714351ab4f5c13efbac69ca7cd80989092cd`。

| Window 别名 | 实际 Window ID | 正文字符 | Plan HTTP | 候选数 | Expand HTTP（slot 顺序） | 落盘 Draft |
|---|---|---:|---|---:|---|---|
| W1 | `2920f356-92f8-50e1-9d64-1f4b2390e21d` | 25 | H2 | 0 | — | 0 |
| W2 | `452611c0-7627-5e6d-b781-b5d4f0663119` | 58 | H3 | 0 | — | 0 |
| W3 | `2c23c001-8504-5d7b-b535-ab3c493169fc` | 288 | H4 | 3 | H5、H6 失败 | 0 |
| W4 | `16136f30-8356-540a-ab9d-008636f24858` | 1377 | 未调用 | NOT_EVALUABLE | — | 0 |
| W5 | `ffe915e9-17f9-5de6-ba5e-ca1e92158d8c` | 918 | 未调用 | NOT_EVALUABLE | — | 0 |
| W6 | `7df7b25a-e426-58fa-84f9-dcc12418fc67` | 532 | 未调用 | NOT_EVALUABLE | — | 0 |
| W7 | `b89e1ec6-1ca0-56d6-8699-bbee638d6f18` | 8 | 未调用 | NOT_EVALUABLE | — | 0 |
| W8 | `486a2dec-cf8c-5cab-8862-986229645693` | 2286 | 未调用 | NOT_EVALUABLE | — | 0 |
| W9 | `2a1679b0-6fc7-5dec-a2bf-8bbe2f43b864` | 374 | 未调用 | NOT_EVALUABLE | — | 0 |

候选数来自 Plan 原始回答；“未调用”不是空计划。

无持久化 Draft、Support、Spec、正式技能；Git H5 原始返回不分配虚构 Draft ID。

### C5：case005_ripgrep_guide

- RUN5（运行根）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r8ac019d9b468`
- M5（官方中间目录）：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r8ac019d9b468\SkillBank\.runtime\intermediate_runs\20261011T223054_f5f786a7`
- SRC5：`D:\AS\AutoSkill-main\degradation_failure_lab\data\raw_sources\ripgrep\4649aa9700619f94cf9c66876e9549d83420e16c\GUIDE.md`
- 输入快照：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r8ac019d9b468\inputs\input001\GUIDE.md`
- Document ID：`f524c684-0781-5a1a-9daa-db1d1cf67095`。字节 40701，源文档 1022 行；SHA-256：`9dd96f163700ab5b41296cef3555b535c80c19e2ea25c7925c21b133d96d9537`。

| Window 别名 | 实际 Window ID | 正文字符 | Plan HTTP | 候选数 | Expand HTTP（slot 顺序） | 落盘 Draft |
|---|---|---:|---|---:|---|---|
| W1 | `0fa569e2-0bb5-5c35-83aa-733ad9d821f2` | 2255 | H2 | 3 | H3、H4、H5 | D3、D4、D5 |
| W2 | `b3ae4d29-0cdd-5047-96ac-8535b815a417` | 1293 | H6 | 3 | H7、H8、H9 | D8、D9、D10 |
| W3 | `02175724-b880-587e-b1af-5ab2376d5ea5` | 149 | H10 | 2 | H11、H12 | D1、D2 |
| W4 | `7897e283-7cc4-55d0-92d6-a1729e1628d9` | 86 | H13 | 0 | — | 0 |
| W5 | `5c86686a-e0fd-5d17-94d3-ee8e369bd8e9` | 88 | H14 | 1 | H15 | D6 |
| W6 | `68ba324f-f8e0-5ec3-8ffe-0351cac18d58` | 77 | H16 | 0 | — | 0 |
| W7 | `d9205b45-ea37-57e2-b08b-740b4134cdff` | 244 | H17 | 2 | H18、H19 | D11、D12 |
| W8 | `8045f264-d3c3-5da8-9886-40591f21a794` | 124 | H20 | 1 | H21 | D7 |
| W9 | `e5a3800a-d5ed-5d92-9f4a-3d8514989009` | 2261 | H22 | 2 | H23、H24 | D13、D14 |
| W10 | `f020278f-d611-5865-ac61-0db5541fa2da` | 2257 | H25 | 3 | H26、H27、H28 | D18、D19、D20 |
| W11 | `e6a6abd5-78bc-5af6-b817-a091a6bfdc38` | 1818 | H29 | 3 | H30、H31、H32 | D15、D16、D17 |
| W12 | `e89d757e-a01e-51b9-9b3d-cd5553e07eea` | 966 | 未调用 | NOT_EVALUABLE | — | 0 |
| W13 | `b28f45a9-9aa5-5fa0-ba2a-1d2f7233bd46` | 201 | 未调用 | NOT_EVALUABLE | — | 0 |
| W14 | `bee528d4-b7a3-5e70-b309-2a3f3b91518f` | 39 | 未调用 | NOT_EVALUABLE | — | 0 |
| W15 | `aeb81e3a-46b5-5042-a5f0-069944829b76` | 31 | 未调用 | NOT_EVALUABLE | — | 0 |
| W16 | `f31a2c64-0166-55d2-894d-68e9f031d424` | 8 | 未调用 | NOT_EVALUABLE | — | 0 |
| W17 | `f8ec7adf-9bcd-5b8d-9b39-260959fffdf6` | 14 | 未调用 | NOT_EVALUABLE | — | 0 |
| W18 | `06e351e1-046d-53a1-acaf-76c0af873686` | 14 | 未调用 | NOT_EVALUABLE | — | 0 |
| W19 | `0b997476-b58d-584e-b478-c45f4d486be1` | 43 | 未调用 | NOT_EVALUABLE | — | 0 |
| W20 | `176f2c1e-af9f-5713-9039-075c77af7e8c` | 794 | 未调用 | NOT_EVALUABLE | — | 0 |
| W21 | `487f6383-4d1f-5024-843a-b9ce7b2566a1` | 1708 | 未调用 | NOT_EVALUABLE | — | 0 |
| W22 | `e654348f-dac7-5522-b23d-f2d223b7fa23` | 2351 | 未调用 | NOT_EVALUABLE | — | 0 |
| W23 | `1f4eae79-e48f-525d-a556-8f70d9f2b92b` | 1980 | 未调用 | NOT_EVALUABLE | — | 0 |

候选数来自 Plan 原始回答；“未调用”不是空计划。

| Draft 别名／名称 | Draft ID | Support 别名／ID | Window | Plan→Expand | Spec 别名／ID |
|---|---|---|---|---|---|
| D1 Gitignore 忽略规则优先级解析 | `85ad0f6c-8126-5ee7-bd11-c061b5a4fb8c` | S1 `9b46778e-e7cd-5345-9f48-5a4b8b63b210` | W3 | H10→H11 | 不存在 |
| D2 父目录 Gitignore 继承判定 | `8f2d8b70-33fa-5bb4-9550-90a94c844b5a` | S2 `dc73b66b-2cdd-5376-83d1-ff7d432075ad` | W3 | H10→H12 | 不存在 |
| D3 ripgrep 基础行匹配搜索 | `4746ff77-aee6-58ee-9ac0-64a9f3cbd302` | S3 `3c7e856b-51cd-57ce-9dbe-b53d33c0df3e` | W1 | H2→H3 | 不存在 |
| D4 ripgrep 正则量词模式搜索 | `cfae498b-fafc-5136-97f8-542d19560899` | S4 `73647cb2-6682-5557-ac84-ea0774ead6a8` | W1 | H2→H4 | 不存在 |
| D5 ripgrep 无结果调试排障 | `cbf9c1a8-f723-5f6a-877d-342a54431b89` | S5 `422488b3-883d-52b7-bc57-d81e06930e50` | W1 | H2→H5 | 不存在 |
| D6 忽略规则优先级判定 | `8a89ca27-48f5-51d1-9b3f-87e1e8af47e4` | S6 `bd540732-9aef-516b-9984-f77839c1cd9f` | W5 | H14→H15 | 不存在 |
| D7 二进制文件文本搜索安全规则 | `c74c98c5-b86a-5369-ba3c-e3cb8dd597c2` | S7 `78b8f3ca-2b9e-59f9-9211-6a62ff9d58d8` | W8 | H20→H21 | 不存在 |
| D8 递归目录搜索与路径限定 | `38edee64-7f0f-5c20-821b-1f330eaf6c83` | S8 `66bdcb35-341e-5574-8892-b70c4017a636` | W2 | H6→H7 | 不存在 |
| D9 正则特殊字符转义与字面量搜索 | `a65550e4-fcee-55c8-9999-90734b6cdbea` | S9 `05a9cd7a-d8c2-58a5-bc90-d263b3dd00ee` | W2 | H6→H8 | 不存在 |
| D10 ripgrep 默认自动过滤规则 | `bfd84176-c06a-574a-988a-b15c824bb6b4` | S10 `6a153fe5-27fb-57ec-9d41-be36a21f65fc` | W2 | H6→H9 | 不存在 |
| D11 禁用忽略规则搜索 | `d1ccae10-e30e-532d-992e-2db8a476e0d0` | S11 `816d6e89-7337-580f-90ad-367dccfe2e38` | W7 | H17→H18 | 不存在 |
| D12 搜索隐藏文件 | `073093da-2f53-505b-9351-49d5b2d433ec` | S12 `0977c449-dea2-504b-bb15-10c3f154e657` | W7 | H17→H19 | 不存在 |
| D13 ripgrep 忽略规则优先级与覆盖配置 | `35768236-2b99-5360-a33d-ff4e442bc1eb` | S13 `21e07a24-7d11-59cd-99d6-378c5422d700` | W9 | H22→H23 | 不存在 |
| D14 ripgrep 手动 glob 过滤搜索 | `bb32d807-b123-527c-871a-38b392c3d0a8` | S14 `22c5f17f-4f10-5620-8757-62ccb8cfa44b` | W9 | H22→H24 | 不存在 |
| D15 临时自定义文件类型过滤 | `ffd19c8c-6d97-53f2-8513-bfce3c788149` | S15 `3ee8ecb2-b548-59ad-b624-32b5b12a3e23` | W11 | H29→H30 | 不存在 |
| D16 持久化自定义文件类型配置 | `8ca84348-1344-5f54-8277-b71c42bb971c` | S16 `3d4861e0-659e-5051-ab44-dee38c3b8c4b` | W11 | H29→H31 | 不存在 |
| D17 匹配文本替换输出 | `0f2baf64-67ab-5334-906d-e1f7ade1ecb1` | S17 `0226d500-7069-5d1e-9278-aed8532bfb20` | W11 | H29→H32 | 不存在 |
| D18 Glob 过滤搜索 | `3ce6adfe-1a7d-51d8-ba1a-e8b0180d3717` | S18 `1bf4094f-1aec-5bcc-a779-4531b477d135` | W10 | H25→H26 | 不存在 |
| D19 文件类型过滤搜索 | `4d02b214-6560-5cc4-9cee-e24a31c62244` | S19 `87aa581a-9c99-5ffa-96fa-e2f557e204f3` | W10 | H25→H27 | 不存在 |
| D20 查看文件类型定义 | `a5919895-6922-5206-bc16-f2a539bfb3d7` | S20 `fa83aca1-c9de-5463-8ab3-9ef6102ce744` | W10 | H25→H28 | 不存在 |

## 3. C1：qsv select 原子化审核

清单 R1、R2、R3、R4、R5、R7 均包含多个原子行为，应拆分；R6 涉及选择器引用与 shell 转义两个层次，不能把“出现引号”当正确命令证明。来源明确支持清单的操作含义，但部分生成文本只保留示例语法，没有充分解释端点／重复列索引。

| Rule ID | 原文规则 | 原文行号 SRC1 | Window | Support | Draft | Spec | Final Skill | 判断 | 最早异常阶段 | 证据 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1a | 1,4 取第 1 和第 4 列 | 27–30 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | H3 examples[0]；F1 19–20、92–93 |
| R1b | 1-4 取前 4 列，不是仅两个端点 | 33–36 | W1 | S1 | D1 | K1 | F1 | UNCERTAIN | Extract 表达不足 | H3/F1 53 只有“范围 1-4”；未明确前四列。不可只因关键词在场给 CORRECT |
| R2a | !1-2 排除前两列 | 51–54 | W1 | S1 | D1 | K1 | F1 | UNCERTAIN | Extract 表达不足 | F1 55 有排除语法，但没有清楚解释前两列；没有产生相反语义 |
| R2b | Foo[2] 取同名 Foo 的第三列 | 57–60 | W1 | S1 | D1 | K1 | F1 | UNCERTAIN | Extract 表达不足 | F1 33/62 有 Foo[2]，没有第三列或 0-based 同名索引解释 |
| R3a | _ 代表最后列 | 63–66 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 33、56 明确末列 |
| R3b | _-1 反转列顺序 | 69–72 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 23–24、57、102–103 |
| R4a | !/pattern/ 排除匹配列 | 87–90、154 | W1 | S1/S2 | D1/D2 | K1/K2 | F1/F2 | CONTRADICTED（F2）；F1 操作正确 | Plan H2 | H2 slot2 success_artifact 是匹配列；H4 prompt 正确排除但 output_contract 相反；F2 34、58 对 80 |
| R4b | --sort 按选定列名字节值排序 | 93–96、164 | W1（示例） | S1/S3 | D1/D3 | K1/K3 | F1/F3 | CORRECT | — | F3 31、48、61；明确不是按列内容排序 |
| R5a | --random 打乱所选列 | 105–120、162 | W1（示例） | S1/S3 | D1/D3 | K1/K3 | F1/F3 | CORRECT | — | F3 49、62；不能与 qsv sort 的行随机混同 |
| R5b | --seed 参数为整数 | 163 | — | — | — | — | 全部缺失 | OMITTED | Ingest Window | 表格未进 W1/W2；F3 有 seed 42 例子但无参数类型定义 |
| R6a | 与选择器语法冲突的列名必须引用 | 129–132、154 | W1（示例） | S1/S4 | D1/D4 | K1/K4 | F1/F4 | CORRECT（规则层） | — | F4 prompt 28、constraints 56–57 |
| R6b（辅助） | 原例的 shell／选择器转义能选择目标列 | 132 | W1 | S1/S4 | D1/D4 | K1/K4 | F1/F4 | UNCERTAIN（执行层） | 最早差异 Expand | 原例含反斜杠，H6/F4 72/91 的显示命令不同；未在目标 shell／qsv 版本执行 |
| R7a | --no-headers 第一行为数据 | 174 | — | — | — | — | 全部缺失 | OMITTED | Ingest Window | common options 不在任何 Extract payload |
| R7b | --delimiter 单个字符，默认逗号 | 175 | — | — | — | — | 全部缺失 | OMITTED | Ingest Window | 不仅旗标名称缺失，类型／约束／默认值也缺失 |
| R7c | --output 文件而非 stdout | 173 | — | — | — | — | 全部缺失 | OMITTED | Ingest Window | 最终文件没有对应操作／约束 |

### 3.1 已确认错误的完整链路：正则排除契约

SRC1 87–90 的例子删除匹配列；W1 正文包含这段，H2／H4 payload.excerpt 也包含，不归因于 Ingest。H2 slot2 description 指“选择或排除”，success_artifact 却是“输出匹配正则的列”。H4 skill.prompt 的步骤 3 和 intervention_moves[1] 明确 !/pattern/ 排除；output_contract 无条件要求输出匹配列。D2 → K2（H9）→ F2 的 34/58 与 80 行保持冲突。

S2 excerpt=整个 W1，confidence=.85，relation_type=support；它没有证明 output_contract 正确。F1 的正确排除例子与 F2 错误契约并存，也是跨技能局部不一致，而不是全技能集合统一把否定理解反了。

### 3.2 Window 与清单局限

W2 的 H7 为完整空计划。正文只有链接、Usage、导航／源文件信息等；重要参数表早在 Window 过滤中消失，不能称“模型读了参数表却提取为空”。

源码定位：D:\AS\AutoSkill-main\AutoSkill-main\AutoSkill4Doc\document\windowing.py 114、143–157、257–284、403–449。Arguments／Select Options／Common Options 的表格整块较长、没有段首 bullet/process signal，被过滤；fallback 使用已过滤 blocks，未恢复。R4a 的 inverted 说明虽在丢失表格中，正文正则例子仍充分支持否定，属于不同证据通道，不能把它整体列为 Ingest 遗漏。

新增待审核规则：选择器组合可重排／重复；3- 直到最后；column selector 反向范围；空 headers／no-headers 时按索引限制等需以原文实际支持范围单独建清单，不从工具惯例补规则。本报告没有声称当前 R1–R7 穷尽全部操作。

## 4. C2：qsv sort 原子化审核

R4 应拆成“随机对象为行”和“random 模式忽略 reverse”两个原子规则；R1／R2 是明确的参数优先级／适用条件，R3 是去重所用比较模式，R5 是算法稳定性，R6 是首行行为。现有引用行基本准确，但只有单行锚点，不足以代表整张参数表的所有语义。

| Rule ID | 原文规则 | 原文行号 SRC2 | Window | Support | Draft | Spec | Final Skill | 判断 | 最早异常阶段 | 证据 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | natural 比较覆盖 numeric | 41 | — | — | — | — | F1–F3 均无 | OMITTED | Ingest Window | 三表过滤；D1 只说支持自然／数值排序，无优先级 |
| R2 | numeric 且非 natural 时 ignore-case 无效 | 43 | — | — | — | — | F1–F3 均无 | OMITTED | Ingest Window | 条件与 flag 参数都未进入实际 H2–H5 摘录 |
| R3 | unique 按排序的同一比较模式判重 | 44 | — | — | — | — | F1–F3 均无 | OMITTED | Ingest Window | “支持去重”不足以表达如何比较重复 |
| R4a | random 随机打乱行 | 52 | — | — | D1 概述 | K1 概述 | F1 概述 | OMITTED（完整规则） | Ingest Window | 最终称随机顺序排序，未明确行随机操作参数；不是已确认把它写成列随机 |
| R4b | random 模式忽略 reverse | 52 | — | — | — | — | F1–F3 均无 | OMITTED | Ingest Window | 未表达模式交互 |
| R5 | faster 使用不稳定排序 | 56 | — | — | — | — | F1–F3 均无 | OMITTED | Ingest Window | 不应据未提 faster 推断模型以为稳定排序 |
| R6 | no-headers 首行作为数据参与排序 | 66 | — | — | — | — | F1–F3 均无 | OMITTED | Ingest Window | common options 整块缺失 |
| A1（补充） | sort 需要将所有数据读入内存；可能放不下则用 extsort | 16–18 | W1 | S1/S2 | D1/D2 | K1/K2 | F1/F2 | CORRECT（正向建议） | — | F1 54–55、F2 29 的条件路由 |
| A2（补充） | qsv sort [options] [input] 的入口 | 28–30 | W1 | S1 | D1 | K1 | F1 | CORRECT（入口）；具体参数缺口 | Ingest 后信息不足 | 有调用排序步骤，但没有细化成可执行参数命令 |
| A3（补充） | 小文件不得 extsort／只能内存不足才允许 | 来源无此排他规则 | W1 无支持 | S2 不足 | D2 | K2 | F2 | UNSUPPORTED | Plan H2 slot2 | do_not_use_when 添加排他性；H4 constraints；F2 42、59–64 |
| A4（补充） | sortcheck 能校验自然／数值／唯一／随机等全部模式 | 3 仅 also see | W1 仅导航支持 | S3 不足 | D3 | K3 | F3 | UNSUPPORTED | Expand H5（模式具体扩展） | F3 27；真实 sortcheck 参数／模式 UNKNOWN，未查其专门文档或执行 |

### 4.1 三张表的可重放过滤

SRC2 的 Sort Options、Random Sorting Options、Common Options 仍在 Document 中；全部 Window 只有 W1。离线官方 windowing 重放得到同一 ID／正文，三个 table-containing 段落分别 1269、1254、883 字符，没有 paragraph-start bullet／anchor，被 >320 规则删除。W1 的 span.start=7、end=5249 不是保留完整区间，实际正文只有 1277 字符。

H1 outline 失败后规则解析仍识别六 Section；不能把所有参数遗漏都归因于 outline 网络失败。段落过滤源码足以解释已保存结果，但没有“成功 outline 与回退 outline 的随机受控对照”，二者影响不能量化拆开。

### 4.2 Plan／Expand 的支持范围

H2 从概述／内存建议提出内存排序、外存切换、排序校验三个候选，职责大体合理。D1 不提供必要 flag，不能算完整命令编译。D2 把 if-large-then-extsort 的建议改为 only-large-can-extsort，最早在 Plan 适用边界。D3 的 sortcheck 完整规则不在来源中；H5 列出的“唯一／随机”预期顺序不能依靠 sort 的描述作独立证据。

H6、H7、H9 的 Compile 保持对应关键数组，部分描述改写更清楚，未补六条参数规则，未修来源外扩展。不能断言本例复现“否定方向反转”：此处主要是遗漏和无支持补充。

## 5. C3：Docker cp 原子化审核

清单 R6 缺少“源为目录、目标已存在且为目录”的适用条件，而且引用 74 行对应“不以 /. 结尾”的相反分支，正确内容在 76–78；R7 需保留 local symlink 限定和默认复制链接本身的配对分支。R5 必须包含“源为文件”，不能脱离上层嵌套条件。R3 应同时识别 -a 选项与 source ownership。只在报告中校正解释，不改历史 rules.json。

| Rule ID | 原文规则 | 原文行号 SRC3 | Window | Support | Draft | Spec | Final Skill | 判断 | 最早异常阶段 | 证据 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | 容器可运行或停止 | 32 | — | — | — | — | 两技能均无 | OMITTED | Ingest Window | 457 字符介绍段被过滤 |
| R2 | 容器路径相对于 /，开头 / 可省略 | 35–38 | — | — | — | — | 两技能均无 | OMITTED | Ingest Window | 466 字符路径段被过滤 |
| R3 | -a 按源 UID/GID 设置 ownership | 43–49 | — | — | — | — | 两技能均无 | OMITTED | Ingest Window | 权限／父目录长段未进 W1 |
| R4 | 不创建缺失的目标父目录 | 51–52 | — | — | — | — | 两技能均无 | OMITTED | Ingest Window | 注意“目标目录可新建”不意味着父目录递归创建 |
| R5a | 源为文件、目标不存在且以 / 结束，报错 | 57、60–61 | W1 | S1 | D1 | K1 | F1 | CORRECT（嵌套步骤） | — | F1 prompt 32/34，示例 19–20 |
| R5b（范围审查） | 上述错误不限源类型 | 来源不支持；对照 67–70 | W1 含正确分支 | S1 不支持扩大 | D1 | K1 | F1 | CONTRADICTED | Expand H3 cautions[0] | F1 86 无源文件条件；F1 38 却允许源目录→不存在目标创建 |
| R6a | 源目录，已有目标目录，源不以 /. 结束：复制目录本身 | 67、73–75 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 37、40–41 |
| R6b | 同前提、源以 /. 结束：复制目录内容 | 67、73、76–78 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 37、40、42、21–22；历史 74 单行锚点不足 |
| R7a | 本地源 symlink 默认复制链接本身 | 80–82 | W1 | S1/S2 | D1/D2 | K1/K2 | F1/F2 | CORRECT | — | F2 30、53、61 明确本地与默认 |
| R7b | 本地源 symlink 用 -L 复制目标 | 82–83 | W1 | S2 | D2 | K2 | F2 | CORRECT | — | F2 30、55、69 与对应默认分支一致 |
| A1 | 源文件→不存在且不属于末尾 / 错误分支的目标：新文件 | 57–59 | W1 | S1 | D1 | K1 | F1 | CORRECT（局部分支） | — | F1 33；需与 R4 全局父目录前提合用 |
| A2 | 源文件→已有目标文件：覆盖内容 | 62–63 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 35 |
| A3 | 源文件→已有目录：按 basename 放入 | 64–66 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 36 |
| A4 | 源目录→不存在目标：创建目录并复制内容 | 67–70 | W1 | S1 | D1 | K1 | F1 | CORRECT（步骤）；与 Caution 冲突 | Expand H3 条件压缩 | F1 38 对 86；仍遗漏 R4 |
| A5 | 源目录→已有文件：错误 | 71–72 | W1 | S1 | D1 | K1 | F1 | CORRECT | — | F1 39、87 条件保留 |
| A6 | 本地含冒号路径需显式相对／绝对前缀 | 85–90 | — | — | — | — | 两技能均无 | OMITTED | Ingest Window | 与 container:path 的消歧规则缺失 |
| A7 | stdin tar 解到容器时目标为目录等限制 | 128–131 | — | — | — | — | 两技能均无 | OMITTED | Ingest Window | 属更宽 cp 流程边界，不要求 symlink 微技能包办 |

### 5.1 保存好的结构与真正新引入的条件缺口

W1 整体包含 SRC3 54–83 的嵌套分支以及 symlink 说明；H2 Plan 两个候选是路径知识参考／symlink 微技能，划分有意义。H3 主 prompt 保持所有核心分支，并非 Docker 嵌套条件被 Ingest 全毁。

但 H3 skill.cautions[0] 是“DEST_PATH 不存在且以 / 结尾时为目标目录必须已存在的错误条件”，丢掉上层 SRC_PATH=file。Plan H2 只有通用“复制结果或错误条件判定”，没有这个无条件 Caution，因此其最早可观察阶段为 Expand，不是凭 D/K ID 反推。D1 该项被 H5 保留至 F1 86 行，与目录→缺失目标允许创建的 38 行不一致。这里只做来源／文本逻辑对照，没有执行 Docker 复制；实际任务受哪句话支配 UNKNOWN。

D1 constraints“需按上述规则存在”与源文 80 行一致，不能把这句话直接读成“所有目标必须已经存在”并算第二个确定错误。真正确定的异常是 Caution 失去源类型限定。两个正式技能都还有 compiler renderer 的 Therapist 残留，不等于 symlink 行为反了。

## 6. C4：Git reset 未完成运行的规则审查

原文为 AsciiDoc，不是 Markdown。H1 outline 成功识别 NAME／SYNOPSIS／DESCRIPTION／OPTIONS／EXAMPLES／DISCUSSION 六主标题，前言另形成 Section；这不证明示例和状态表的结构已正确转成可执行规则。

| Rule ID | 原文规则 | 原文行号 SRC4 | Window | Support | Draft | Spec | Final Skill | 判断 | 最早异常阶段／观察层 | 证据 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | pathspec 形式只改 index，不改 worktree／branch | 23–27 | W4；W3 仅语法 | — | — | — | 不存在 | NOT_EVALUABLE | Extract 网络停止 | H5 原始示例称默认 mixed，形式混淆风险 UNCERTAIN；W4 未调用 |
| R2 | commit reset 未指定模式默认 mixed | 49–54；63–66 | W3 语法；W4 有 default action，但 commit 前提段丢失 | — | — | — | 不存在 | NOT_EVALUABLE | Ingest 部分上下文丢失＋运行停止 | 602 字符 commit／soft 段过滤；不可称最终默认值错误 |
| R3 | soft 改 HEAD，不改 index／worktree | 49–61 | W8 状态表有 soft 行；描述段缺失 | — | — | — | 不存在 | NOT_EVALUABLE | Ingest 解释／例外丢失 | 不能说 soft 在所有窗口彻底不存在；H5 详情不来自 W3 完整定义 |
| R4 | mixed 改 index，不改 worktree | 63–69 | W4 | — | — | — | 不存在 | NOT_EVALUABLE | Extract 网络停止 | W4 保留源码规则但未 Plan |
| R5 | hard 改 index／worktree，破坏性细节需保留 | 71–74 | W5 | — | — | — | 不存在 | NOT_EVALUABLE | Extract 网络停止 | W5 含 hard；未调用不能说模型遗漏 |
| R6 | merge 在目标 commit 与 index 不同且存在 unstaged 时中止 | 76–85，尤其 81–82 | W5 | — | — | — | 不存在 | NOT_EVALUABLE | Extract 网络停止 | 清单“有 unstaged 就中止”不完整；按原文双条件审核 |
| R7 | keep 在目标 commit 与 HEAD 不同且存在 local changes 时中止 | 87–91 | W5 | — | — | — | 不存在 | NOT_EVALUABLE | Extract 网络停止 | 不能把所有 local changes 一概定义成 abort |
| A1 | --patch 按差异块交互选择／反向应用到 index | 40–47 | — | — | — | — | 不存在 | NOT_EVALUABLE | Ingest 确认遗漏 | 439 字符长段过滤；最终效果未观察 |
| A2 | --pathspec-from-file 文件输入及换行规则 | 115–121 | — | — | — | — | 不存在 | NOT_EVALUABLE | Ingest 确认遗漏 | 386 字符段过滤；下一条 NUL 规则留在 W6，前提分离 |
| A3 | --pathspec-file-nul 的 NUL 分隔和字面值 | 123–126 | W6 | — | — | — | 不存在 | NOT_EVALUABLE | Extract 网络停止 | 对应前置 from-file 条件未完整入窗 |
| A4 | 状态表中 A/B/C/D 的含义及允许／禁止组合 | DISCUSSION 表格及 392–399 图例 | W8/W9 表格；图例缺失 | — | — | — | 不存在 | NOT_EVALUABLE | Ingest 上下文缺失 | 不能因表格字面仍存在称完整状态语义已解析 |

### 6.1 EXAMPLES 与状态表

SRC4 EXAMPLES 从 136 行开始，十个 workflow 包括 Undo add、Undo commit/redone、topic branch、永久撤回、撤回 merge/pull、dirty tree merge、interrupted workflow、single file、keep changes、split commit。源段以 AsciiDoc 的“...::”文字和 + 连接，组成 975、659、512、421、1141、753、1059、571、1000、2671 字符块；全部在 _build_paragraph_blocks 被过滤。实际 W7 只有“--------”8 字符。它未被 Plan 调用，不应记为模型返回空计划。

W8 保存多个 aligned 状态表，W9 保存末尾 unmerged 表及 X/U 等文字。A/B/C/D 图例和一部分解释被过滤；只是文本保留，未转为经过验证的状态转换表。不能以“Git 文档有状态表”推出解析完全失败，也不能以“表格还在”推出语义支持完整。

### 6.2 失败状态与原始返回

H2/H3 分别对 25／58 字符窗口返回空；H4 SYNOPSIS 规划三个候选，H5 的原始响应成功但 H6 TLS EOF（retryable=false）阻断后续。Mx\extract\windows\<doc_id>\<W3>.json 的未解决节点及官方 errors 可核验；没有持久化 H5 的 Draft ID。后面 W4–W9 的知识输入未执行，Compile／Register 空结果不是完整零技能质量实验。

任何最终 R1–R7 分数均 NOT_EVALUABLE，不参与完成案例正确率；仍可以独立报告本例 Ingest 的确定结构损失。

## 7. C5：ripgrep 长教程部分结果

规则解析回退产生 35 Section。源码 _detect_headings（ingest.py 226–238）逐行无 fenced-code 状态；正文枚举和 config／shell 代码中的 # 注释成为标题。“Because who cares about case!?”等被用作编码段落父标题，结构与真实章节不一致。

该 run 23 Window 中只有前 11 个发生 Plan：其中 9 个非空，20 个 Expand 成功并落盘；W4/W6 空；W12–W23 未调用，不能记空。完成 Draft 数不代表后半教程已覆盖。

### 7.1 现有 R1–R6

| Rule ID | 原文规则 | 原文行号 SRC5 | Window | Support | Draft | Spec | Final Skill | 判断 | 最早异常阶段／观察层 | 证据 |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | -F 按字面量解释模式 | 148–151 | W2；另在 W23 | S9 | D9 | 不存在 | 不存在 | NOT_EVALUABLE；Draft CORRECT | —（局部保留）／预算阻断最终 | H6→H8；D9 prompt／intervention 明确 -F；W23 未调用 |
| R2a | --type-add 只当前命令，不自动保存 | 412–414 | W11 | S15/S16 | D15/D16 | 不存在 | 不存在 | NOT_EVALUABLE；Draft CORRECT | —（这一原子规则） | H30/H31 constraints 正确；不能掩盖持久化条件问题 |
| R2b（辅助） | 长期复用可 alias 或启用的 config；不是默认全局 | 414–422、547–552、621–625 | W11 有建议；启用前提／禁用例外无窗口 | S16 不完整 | D16 | 不存在 | 不存在 | NOT_EVALUABLE；Draft UNSUPPORTED 条件扩大 | Ingest 丢前提；Plan H29 无条件保证 | H31 cautions[1]“对所有…全局生效”，缺 env 与 --no-config |
| R3 | --replace 只改输出，绝不修改输入文件 | 536–538 | W12（未调用） | S17 不含明确 536 条款 | D17 正确补出该约束 | 不存在 | 不存在 | NOT_EVALUABLE；Draft CORRECT | 来源通道 UNKNOWN | H32 cautions 明确 no-file；W11 excerpt 没这完整条款，不能称本条未被生成 |
| R4 | config 需 RIPGREP_CONFIG_PATH 指向文件，不自动找预设目录 | 547–552，变量 549 | — | — | D16 缺该前提 | 不存在 | 不存在 | NOT_EVALUABLE；Ingest 确认遗漏 | Ingest Window | 416 字符段过滤；历史 anchor 548 不含变量本身 |
| R5a | config trim 后每行为一个 argument | 554 | W13 标题元数据 | — | — | 不存在 | 不存在 | NOT_EVALUABLE | 预算未调用 | 不能说标题信息完全消失 |
| R5b | config 每行原样作为单参数，无 shell escaping | 558–559 | W13 正文 | — | — | 不存在 | 不存在 | NOT_EVALUABLE | 预算未调用 | Document 与 Window 有内容，不能错误归为 Ingest 规则遗漏 |
| R6 | --no-config 禁止读环境配置 | 621–625 | — | — | — | 不存在 | 不存在 | NOT_EVALUABLE；Ingest 确认遗漏 | Window group/range 选择 | 原 317 字符 block 被保留，却没有进入实际 Window；不是 >320 长段过滤 |

R3 的生成约束在全原文有明确来源支持，但单个 Support excerpt 不包含那个明确的“不改文件”条款，区分“生成内容正确”和“此 Support 是否句子级支持”。不能猜它一定是训练记忆补充，亦不能因不在本窗口而判该条工具语义错误。

### 7.2 补充的关键规则／错误矩阵

| Rule ID | 原文规则或新增主张 | 原文行号 SRC5 | Window | Support | Draft | Spec | Final Skill | 判断（Draft 层；Final 均 NOT_EVALUABLE） | 最早异常阶段 | 证据 |
|---|---|---|---|---|---|---|---|---|---|---|
| A1a | -t 包含指定文件类型 | 376–377 | W10 | S19 | D19 | — | — | CORRECT（步骤） | — | H27 prompt／constraints 正确说明 |
| A1b | -T 排除指定类型，不能“仅返回指定类型” | 376–377 | W10 | S19 | D19 | — | — | CONTRADICTED（契约） | Plan H25 slot2 | success_artifact 与 H27 output_contract 只给包含结果 |
| A2 | -g 多次旗标较后覆盖；前缀 ! 排除 | 281–316 | W10 | S18 | D18 | — | — | CORRECT（主规则） | — | H26 否定语法／quote／较后优先正确 |
| A3 | 反转包含／排除 glob 顺序可能没有任何结果 | 318–322 | — | — | D18 没例外 | — | — | OMITTED（Draft 内容）；Final NOT_EVALUABLE | Ingest Window | 341 字符解释块过滤；保留覆盖规则不等于保留全部例外 |
| A4 | --no-ignore 禁用 ignore 相关过滤，不保证有匹配 | 196 | W7 | S11 | D11 | — | — | UNSUPPORTED（强后置保证） | Plan H17 slot1 | success_artifact / output_contract 保证输出含原忽略文件 |
| A5 | --hidden 将 hidden 纳入搜索范围 | 197–198 | W7 | S12 | D12 | — | — | CORRECT（旗标）；匹配保证需人工限定 | — | H19 正确 flag；仍需文件有匹配及不被其他机制排除 |
| A6 | -a 二进制文本搜索可能向终端输出控制字符 | 199–201 | W8 正文警告＋标题 flag | S7 | D7 | — | — | CORRECT（风险） | — | 短正文不等于无 flag：标题含 -a/--text |
| A7 | 必须确认重定向／安全终端才允许二进制搜索 | 来源没有此强制规范 | W8 无支持 | S7 不足 | D7 | — | — | UNSUPPORTED | Plan H20 | H21 prompt/constraints 加强制前提，原文只提示注意 |
| A8 | .rgignore > .ignore > .gitignore | 181–189、214–218 | W3/W5/W9 标题或正文 | S1/S6/S10/S13 | D1/D6/D10/D13 | — | — | CORRECT（明确 > 关系）；D10 呈现需复审 | — | D10 prose 先列 gitignore 再 .ignore/.rgignore 但括号正确，不能断言已经优先级反转 |
| A9 | 默认过滤适用于递归；显式指定隐藏文件可搜索 | 153–155、169–180、738–748 | W2 含递归起点；后半例外未完整入窗 | S10 不完整 | D10 | — | — | UNCERTAIN／适用范围过宽风险 | Ingest 例外损失＋Expand H9 未限定 | 不能把所有显式文件均不搜索当源文规则 |
| A10 | 手动 glob 应有 -g 的具体操作 | 281–295 | W10 有；W9 只有引入 | S14/S18 | D14/D18 | — | — | D18 CORRECT；D14 OMITTED 可执行细节 | 跨窗口分割；Expand H24 | D14 未指定 -g，rg clap 例子说明自己未过滤；不是错误示范已过滤 |
| A11 | --type-list 查询已知类型映射 | 379–383 | W10 | S20 | D20 | — | — | CORRECT | — | H28 类型名／glob 映射查询目的合理 |
| A12 | config 注释以 # 起始可有前置空白 | 555–556 | W13 | — | — | — | — | NOT_EVALUABLE | 预算未调用 | 文本留存但原 config # 示例被误识别标题 |
| A13 | 默认 UTF-16 BOM 转码及其他 -E encoding | 638–671 | W21 | — | — | — | — | NOT_EVALUABLE | 预算未调用 | 不能因没 Draft 称模型忽略了已读规则 |
| A14 | binary 检测与 mmap 策略；--no-mmap 一致性例外 | 771–780 | W22 有策略；长解释缺失 | — | — | — | — | NOT_EVALUABLE | Ingest 局部缺口＋预算 | 已定位文本规则；尚未经过独立人工金标准复核，不能用于定量评分 |

### 7.3 全部二十 Draft 的内容审核记录

下表不能变成未经定义的“20 个正确／错误”得分。同一 Draft 可同时有正确规则与错误合同；上节精确规则优先于整体标签。

| Draft | 已核对的操作内容 | 初步评价与局限 |
|---|---|---|
| D1 | .rgignore/.ignore/.gitignore 优先级及父目录 gitignore | 明确优先级正确；父目录／--no-require-git 语句应结合源文复审，与 D2/D6/D13 有重叠 |
| D2 | 同一 Git repository 的父目录忽略继承 | 有意义的局部前提技能；flag 的例外方向没有执行校验，不能按生成 confidence 证明 |
| D3 | 给 pattern／文件执行 rg，返回匹配行 | 基础任务可读；默认行号等输出不应不分终端／管道环境作普遍 Oracle |
| D4 | \w+、* 等正则量词与示例 | 主体符号含义合理；源中被过滤的解释不应当全部凭已见示例认定完整 |
| D5 | 搜索为空时 --debug 查忽略原因 | debug 建议有源支持；“最可能原因”不能推广成任意空结果都由 ignore 导致 |
| D6 | .rgignore 覆盖 .ignore，包含父目录 | 保留明确优先关系；Window 很短但 sibling heading 含规则，不能纯关键词判 unsupported |
| D7 | --text/-a 与终端控制字符风险 | 风险正确；强制防护后才能执行是额外 UNSUPPORTED 限制 |
| D8 | 当前／指定目录递归路径限定 | 核心路径搜索正确；Plan“需要过滤就不适用路径技能”是未经来源支持的排他路由 |
| D9 | regex 元字符转义与 -F literal | 两种操作组合合理且支持 R1；不同 shell 的 quoting 仍需固定环境 |
| D10 | 默认忽略文件、hidden、binary、symlink 过滤 | 类别概述有意义；优先顺序文字呈现不一致、递归适用范围／显式路径例外不足需复审 |
| D11 | --no-ignore 范围控制 | flag 正确；契约保证实际输出含原忽略文件，强于取消过滤规则 |
| D12 | --hidden / -. | 搜索范围开关正确；不是必然发现 hidden 中匹配项的保证 |
| D13 | .rgignore > .ignore > .gitignore 及局部覆盖 | 正确主关系，与 D1/D6 重叠；未完成 Compile，不能判最终冗余 |
| D14 | 用户选择手动 glob 过滤 | 缺具体 -g 与有效过滤演示；例子注明未过滤，不误报为反向过滤 |
| D15 | --type-add 当前定义＋-t 使用、--type-list 可查询 | R2a 正确；type-list 查询是可选验证，与结果属性表达的关系需人工澄清 |
| D16 | alias／配置文件持久类型定义 | 不自动持久化约束正确；缺 env 启用前提、全局生效保证缺例外 |
| D17 | --replace/-r、-o、整行匹配、输出改写 | 正确保留不修改文件；明确条款在 W12，而本次输入 W11，Support 不是完整单句证据 |
| D18 | -g 包含／! 排除、顺序覆盖、quote | 多分支主操作正确；反转顺序无结果的例外缺失 |
| D19 | -t／-T 类型包括／排除、--type-add | 两方向步骤正确；Output Contract 和排除方向相反，确认内部冲突 |
| D20 | --type-list 及管道查询类型定义 | 职责清晰的查询技能；工具实际返回格式仍未执行验证 |

### 7.4 C5 条件冲突的最早观测链路

类型过滤：SRC5 376–377 → W10 → H25 slot2（description 含包括／排除，success_artifact 仅指定类型）→ H27 skill（步骤 2 包括、步骤 3 排除，constraints 也正确区分，output_contract 无条件包括）→ D19。Compile／Final 不存在，链路到此停止。与 C1 的相似性是“多分支操作被单方向契约压缩”，不是两个模型对所有负号都理解错误。

配置：SRC5 547–552 的 416 字符启用块被过滤；621–625 的 317 字符 no-config 块保留但未入 Window。W11 有“将 type-add 放 config”的跨章节建议而没启用条件。H29 slot2 已要求后续所有命令可用，H31 又明确“所有命令全局”，D16 保留。可以定位分离前提与范围扩大的可见链路；不能证明若保留前提模型一定写对。

二进制安全：W8 124 字符正文警告＋section metadata flag → H20 success_artifact 添加保护前提 → H21 仅保护后执行 → D7。是安全建议规范化范围扩大，不是 source 已要求的强制操作。

## 8. Support／Compile 的逐阶段对应

全部 29 个 Support.excerpt 都等于对应 Window.text。多个 Support 指向同一 Window；别名 S 的 ID 在第 2 节完整列出。每个技能通常 support_count=1；不能从跨技能 29 条记录推出 29 份独立证据，也不能虚构本批已观察到高单技能计数。

九个正式 Evidence Manifest 的准确可见路径如下：

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\通用技能领域\Family技能\qsv-select\二级技能\CSV 列选择与重排\references\evidence_manifest.json`：skill_id=`f4c4df75-6ea6-5d4d-b30c-d7e825084300`，support_count=1，confidence=0.9，quote 等于 2363 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\通用技能领域\Family技能\qsv-select\微技能\列排序与随机打乱\references\evidence_manifest.json`：skill_id=`500c276a-5f59-5af9-86f5-4c0fbf4ad1be`，support_count=1，confidence=0.85，quote 等于 2363 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\通用技能领域\Family技能\qsv-select\微技能\引用冲突列名进行 qsv select\references\evidence_manifest.json`：skill_id=`b0592fe3-a3d5-539a-af63-d33035c20003`，support_count=1，confidence=0.8，quote 等于 2363 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\通用技能领域\Family技能\qsv-select\微技能\正则表达式列选择\references\evidence_manifest.json`：skill_id=`bd72bc3b-8c84-59c2-9fd4-5caba1a5350b`，support_count=1，confidence=0.85，quote 等于 2363 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\通用技能领域\Family技能\qsv-sort\二级技能\CSV 内存排序执行\references\evidence_manifest.json`：skill_id=`353ba11e-1351-58c3-bb24-f91c7e24da8d`，support_count=1，confidence=0.9，quote 等于 1277 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\通用技能领域\Family技能\qsv-sort\二级技能\大文件外存排序切换\references\evidence_manifest.json`：skill_id=`cc5a002d-6830-5192-b841-d8233e6ce4e3`，support_count=1，confidence=0.85，quote 等于 1277 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\通用技能领域\Family技能\qsv-sort\二级技能\排序结果校验\references\evidence_manifest.json`：skill_id=`7ab97840-0c8c-5685-88d2-36bdb1faefea`，support_count=1，confidence=0.8，quote 等于 1277 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\通用技能领域\Family技能\docker-cp\一级技能\docker cp 路径语义判定\references\evidence_manifest.json`：skill_id=`0be52a4b-b68d-5166-a0c1-668834d1f64a`，support_count=1，confidence=0.9，quote 等于 1542 字符 Window。

- `D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\通用技能领域\Family技能\docker-cp\微技能\docker cp 符号链接复制策略选择\references\evidence_manifest.json`：skill_id=`23370d93-9d3f-5142-bfed-e6ff22cb9b36`，support_count=1，confidence=0.85，quote 等于 1542 字符 Window。

Manifest 的 source_file 指向 run 输入快照；SRC 文件通过 input_manifest 的 source_id／source_sha256 关联。该链路可靠地说明从哪里提取，不证明来源支持额外 Caution。confidence 是模型字段，不是人工金标准或验证器评分。缺失父目录、config 环境变量等不会因为整 Window quote 很长而自动得到支持。

| Case / Draft→Spec | 逐项结构／语义对照 | 对已知错误是否修复 | Final 保真 |
|---|---|---|---|
| C1 D1→K1 | prompt、操作、Workflow、Constraints 等保留 | 未补参数表；仅结构组织 | F1 保留 Spec body |
| C1 D2→K2 | 正则选取与排除动作、单方向 Contract 原样 | 未修正 H2/H4 冲突 | F2 34/58 对 80 |
| C1 D3→K3 | 列排序／随机化、seed 建议保留 | 未增加 seed 整数定义 | F3 保留 |
| C1 D4→K4 | 名称／描述更完整，引用规则保留 | 没有证明 shell 转义正确 | F4 保留 |
| C2 D1→K1 | 描述精炼，操作数组同原稿 | 未补 six-rule checklist | F1 保留 |
| C2 D2→K2 | 描述改写，排他限制仍在 | 未纠正 only-large 规范扩大 | F2 42、59 |
| C2 D3→K3 | 排序校验步骤与模式列表保留 | 未核验来源外 sortcheck 能力 | F3 27 |
| C3 D1→K1 | 主体条件树与 Caution 同时保留 | 未修源类型条件缺失 | F1 38 对 86 |
| C3 D2→K2 | local symlink 默认／-L 分支保留 | 未见该局部规则有须修冲突 | F2 保留 |
| C4 / C5 | 无 Spec | NOT_EVALUABLE | 无 Final |

没有本批多 Draft 合并输出；不能把九个一对一编译当验证了去重／融合能力。Therapist 示例标题来自 D:\AS\AutoSkill-main\AutoSkill-main\AutoSkill4Doc\stages\compiler.py 126–170，已确认 Compile 本地 renderer 添加；不是原文规则。

## 9. Register 全量逐条审计及原始回答

三个完成案例均为 hits0：existing_skills=[]；C1 peer_count=3、C2=2、C3=1。实际请求 candidate_skill 没有 output_contract、完整 prompt、examples；support_summary.evidence_snippets 只给窗口开头截断摘要。代码：D:\AS\AutoSkill-main\AutoSkill-main\AutoSkill4Doc\store\versioning.py 680–739。不能假设 Register 已看到本文定位的全部语义冲突。

所有成功决策下列共同字段：

- max_tokens=256，completion_tokens=256，finish_reason=length。
- 完整根 JSON 不成立，strict json.loads 失败；官方 json_from_llm_text 返回 list=[]，maybe_json_dict 返回 {}；action／reason／resolved_skill 等根字段没有保留下来。
- versioning.py 1378–1384 默认 create、原 Spec 和 reason=create；官方 decision／change_log 动作与该重放一致。
- raw text 有部分 create 理由；不代表完整决策。有效 CREATE=0，有效 DISCARD=0，默认 CREATE=9（仅本批成功决策）。
- H10（C2）、H8（C3）为 TLS 失败尝试，无成功回答；各在 H11／H9 重试。C4/C5 未调用 Register，NOT_EVALUABLE。

| Case / HTTP | Skill ID／别名 | prompt / completion | peer_count | official parse | action／reason | 分类 |
|---|---|---:|---:|---|---|---|
| C1 H12 | K1 `f4c4df75-6ea6-5d4d-b30c-d7e825084300` | 1691 / 256 | 3 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C1 H13 | K2 `bd72bc3b-8c84-59c2-9fd4-5caba1a5350b` | 1691 / 256 | 3 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C1 H14 | K3 `500c276a-5f59-5af9-86f5-4c0fbf4ad1be` | 1691 / 256 | 3 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C1 H15 | K4 `b0592fe3-a3d5-539a-af63-d33035c20003` | 1691 / 256 | 3 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C2 H11 | K1 `353ba11e-1351-58c3-bb24-f91c7e24da8d` | 1274 / 256 | 2 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C2 H12 | K2 `cc5a002d-6830-5192-b841-d8233e6ce4e3` | 1274 / 256 | 2 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C2 H13 | K3 `7ab97840-0c8c-5685-88d2-36bdb1faefea` | 1274 / 256 | 2 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C3 H7 | K1 `0be52a4b-b68d-5166-a0c1-668834d1f64a` | 1205 / 256 | 1 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |
| C3 H9 | K2 `23370d93-9d3f-5142-bfed-e6ff22cb9b36` | 1205 / 256 | 1 | []→{} | create / create | 截断根 JSON 无效＋默认回退创建 |

以下完整抄录已保存的 content（保持它们在截断点结束，不补闭合符号）。真正证据是对应 response.json；报告中的展示不是新生成回答。

### C1 H12 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\http\012\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能覆盖 qsv select 的列选择与重排核心能力，与同批微技能（正则选择、排序/随机、引用冲突列名）互补而非重复，且无冲突证据，适合作为会话级技能保留。",
  "resolved_skill": {
    "skill_id": "f4c4df75-6ea6-5d4d-b30c-d7e825084300",
    "name": "CSV 列选择与重排",
    "description": "使用 qsv select 按索引、名称、范围或正则选择、重排、反转、复制或删除 CSV 列。适用于需要从 CSV 中提取或调整列顺序的场景。",
    "asset_type": "session_skill",
    "granularity": "session",
    "asset_node_id": "workflow_skill",
    "asset_level": 2,
    "objective": "从 CSV 数据中高效选择、重排、反转、复制或删除列。",
    "domain": "qsv",
    "task_family": "CSV 列操作",
   
```

### C1 H13 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\http\013\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能聚焦于使用正则表达式匹配列名进行选择或排除，与同批次的列排序、引用冲突列名及通用列选择技能在方法族和干预动作上均有明确区分，具备独立可执行价值，且无支持冲突证据，应保留为新技能。",
  "resolved_skill": {
    "skill_id": "bd72bc3b-8c84-59c2-9fd4-5caba1a5350b",
    "name": "正则表达式列选择",
    "description": "使用正则表达式匹配列名，从 CSV 数据中选择或排除符合模式的列。适用于列名具有规律、需要按模式批量选择或排除列的场景。",
    "asset_type": "micro_skill",
    "granularity": "micro",
    "asset_node_id": "micro_skill_node",
    "asset_level": 3,
    "objective": "通过正则表达式匹配列名来选择或排除列。",
    "domain": "qsv",
    "task_family": "CSV 列操作",
    "method_family": "
```

### C1 H14 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\http\014\response.json`，字段 choices[0].message.content。

```text
{"action": "create", "target_skill_ids": [], "reason": "Distinct micro skill for column sorting/randomization via qsv select --sort/--random; no existing skills and no same-batch redundancy (peer session skill covers broader selection but this is a focused, non-duplicative capability).", "resolved_skill": {"skill_id": "500c276a-5f59-5af9-86f5-4c0fbf4ad1be", "name": "列排序与随机打乱", "description": "对选定的 CSV 列进行字典序排序或随机打乱，用于在列选择之后重新排列列顺序。", "asset_type": "micro_skill", "granularity": "micro", "asset_node_id": "micro_skill_node", "asset_level": 3, "objective": "对选定的列进行排序或随机打乱。", "domain": "qsv", "task_family": "CSV 列操作", "method_family": "排序/随机化", "stage": "数据预处理", "workflow_steps": ["确定要操作的列集合（如 1- 表示全部列）",
```

### C1 H15 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\http\015\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能聚焦于 qsv select 中特殊字符列名的引用转义，与同批候选（正则选择、排序打乱、通用列选择）在方法族和干预动作上互补，无重复或冲突，且支持证据明确，应保留为独立微技能。",
  "resolved_skill": {
    "skill_id": "b0592fe3-a3d5-539a-af63-d33035c20003",
    "name": "引用冲突列名进行 qsv select",
    "description": "当 CSV 列名包含空格、连字符等与 qsv select 选择器语法冲突的字符时，用引号正确引用列名，从而准确选中目标列。",
    "asset_type": "micro_skill",
    "granularity": "micro",
    "asset_node_id": "micro_skill_node",
    "asset_level": 3,
    "objective": "正确引用包含特殊字符的列名以避免语法冲突。",
    "domain": "qsv",
    "task_family": "CSV 列操作",
    "method
```

### C2 H11 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\http\011\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能描述了使用 qsv sort 对可载入内存的 CSV 进行排序的独立能力，与同批次的 extsort 大文件外存排序和 sortcheck 排序校验技能互补且无冗余，支持证据充分且无冲突，应保留为新技能。",
  "resolved_skill": {
    "skill_id": "353ba11e-1351-58c3-bb24-f91c7e24da8d",
    "name": "CSV 内存排序执行",
    "description": "使用 qsv sort 对可全部载入内存的 CSV 数据按字典序、自然序、数值、逆序、去重或随机顺序进行排序并输出结果。",
    "asset_type": "session_skill",
    "granularity": "session",
    "asset_node_id": "workflow_skill",
    "asset_level": 2,
    "objective": "对可载入内存的 CSV 数据执行指定顺序的排序并输出排序结果。",
    "domain": "qsv",
    "task_family": "CSV
```

### C2 H12 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\http\012\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能描述了大文件内存受限时切换 extsort 外存排序的独立能力，与同批次的 qsv sort 内存排序和 sortcheck 校验技能互补，无重复或冲突，应保留。",
  "resolved_skill": {
    "skill_id": "cc5a002d-6830-5192-b841-d8233e6ce4e3",
    "name": "大文件外存排序切换",
    "description": "当待排序 CSV 文件过大、可能无法全部载入内存时，将排序任务从默认内存排序切换为 extsort 外存排序方案，以完成大规模排序。",
    "asset_type": "session_skill",
    "granularity": "session",
    "asset_node_id": "workflow_skill",
    "asset_level": 2,
    "objective": "在内存不足时选择外存排序方案完成大文件排序。",
    "domain": "qsv",
    "task_family": "CSV 数据处理",
    "method_family": "外存排序",
    "stage":
```

### C2 H13 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\http\013\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能为独立的排序校验能力，与同批次的排序执行和外存排序技能互补，无冗余或冲突，应保留。",
  "resolved_skill": {
    "skill_id": "7ab97840-0c8c-5685-88d2-36bdb1faefea",
    "name": "排序结果校验",
    "description": "使用 sortcheck 命令校验 CSV 数据是否已按预期顺序排序，用于验证排序正确性或检查数据有序性。",
    "asset_type": "session_skill",
    "granularity": "session",
    "asset_node_id": "workflow_skill",
    "asset_level": 2,
    "objective": "检查 CSV 数据是否满足指定排序顺序。",
    "domain": "qsv",
    "task_family": "CSV 数据处理",
    "method_family": "排序校验",
    "stage": "数据验证",
    "workflow_steps": [
      "确认目标 CSV 文件及期望的排序顺序",
      "调用 sortcheck 命令进行校验",
      "
```

### C3 H7 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\http\007\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能提供了 docker cp 路径语义判定的独立知识参考，与同批符号链接处理技能互补且无冲突，应保留。",
  "resolved_skill": {
    "skill_id": "0be52a4b-b68d-5166-a0c1-668834d1f64a",
    "name": "docker cp 路径语义判定",
    "description": "根据 SRC_PATH 与 DEST_PATH 的存在性、类型（文件/目录）以及是否以 / 或 /. 结尾，判定 docker cp 的复制行为或错误条件。用于在执行或解释 docker cp 前确定目标路径应如何被解释。",
    "asset_type": "knowledge_reference",
    "granularity": "session",
    "asset_node_id": "knowledge_reference_node",
    "asset_level": 1,
    "objective": "准确判定 docker cp 在给定源/目标路径组合下的复制语义与错误条件",
    "domain": "docker",
    "task_family": "容器文件复制",
    "method_family": "路径语义规则判定
```

### C3 H9 原始回答

文件：`D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\http\009\response.json`，字段 choices[0].message.content。

```text
{
  "action": "create",
  "target_skill_ids": [],
  "reason": "候选技能聚焦 docker cp 符号链接源路径下默认复制链接本身与使用 -L 复制链接目标的选项选择，与同批 peer 的路径语义判定技能互补且不重复，支持证据明确，无冲突，适合作为独立 micro_skill 保留。",
  "resolved_skill": {
    "skill_id": "23370d93-9d3f-5142-bfed-e6ff22cb9b36",
    "name": "docker cp 符号链接复制策略选择",
    "description": "当 docker cp 的 SRC_PATH 为本地符号链接时，决定默认复制链接本身还是使用 -L 选项复制链接目标，用于需要明确控制符号链接处理语义的复制场景。",
    "asset_type": "micro_skill",
    "granularity": "micro",
    "asset_node_id": "micro_skill_node",
    "asset_level": 3,
    "objective": "在符号链接源路径下选择复制链接本身或链接目标",
    "domain": "docker",
    "task_family": "容器文件复制",
    "
```

### 9.1 解析机制与结果边界

D:\AS\AutoSkill-main\AutoSkill-main\autoskill\utils\json.py 23 起在根解析失败后扫描内部 JSON 片段并评分；list 的分数可高于 dict，target_skill_ids=[] 是完整内部数组。D:\AS\AutoSkill-main\AutoSkill-main\AutoSkill4Doc\core\llm_utils.py 167–170 仅接受 dict；versioning.py 1371–1384 使用该空 dict 并默认创建。llm_complete_json repair 仅在解析抛异常时调用，内部 [] 不抛异常；所以“有 repair 提示模板”不是“repair 实际发生”。

本轮离线只调用两个纯解析函数，没有调用 complete 或 llm_complete_json_with_retries，没有模拟生成替换历史结果。九个样本均重放上述链路。默认 CREATE 是准入过程的可信度问题；可见 partial reason 可能本来支持 CREATE，但真实完整裁决、是否应丢弃、有无同批去重判断成效 UNKNOWN。不能替模型补一个 DISCARD 真值。

## 10. 无法核实、补充清单和复核路径

1. 所有 R1–R7／R1–R6 都只是分析者清单。原子化、改锚点和 A 类补充在本报告提出，没有改原规则或生成新的“已人工审核”记录。
2. 建议人工重点复核：C1 范围／重复列命令在正确 qsv 版本与固定 shell 中的解释；引用反斜杠；C2 extsort／sortcheck 来源外能力；Docker Caution 的条件作用域；Git 两种 reset 形式与表格；ripgrep 配置前提、递归范围、忽略优先级表达、type-add 验证命令。
3. 未执行任何 Git reset／Docker cp；没有调用 qsv／rg 构造执行 Oracle。CORRECT 为文本规则保留，实际任务成功／失败 UNKNOWN。
4. 导出错配源头 UNKNOWN；TLS 根因 UNKNOWN；模型固定权重／账单 UNKNOWN；两个未完成样本的 Compile／Register 质量 UNKNOWN。
5. 本报告不汇总一个“33 条规则准确率”：多原子规则、正确与冲突并存、额外规则、未完成截尾与未经人工确认都需要不同分母／范围。
6. 后续验证器至少区分：结构／哈希验证、规则语义审查、限定输入上的可执行反例、注册决策有效性。任何一层通过都不自动证明另三层通过。
7. 与《CLEAN_MULTI_CASE_GENERATION_AUDIT.md》一起复核；所有原始文件路径在本报告定义。报告提交后停止，等待批准。

方法约束参考同主报告已核验的 Scientific Agent Skills（arXiv:2609.00065），仅用于审查证据等级／范围，不作为本框架性能证据。https://doi.org/10.48550/arXiv.2609.00065

