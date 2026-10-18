
# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\csv-列选择与重排\SKILL.md

1: ---
2: id: "f4c4df75-6ea6-5d4d-b30c-d7e825084300"
3: name: "CSV 列选择与重排"
4: description: "使用 qsv select 按索引、名称、范围或正则选择、重排、反转、复制或删除 CSV 列。适用于需要从 CSV 中提取或调整列顺序的场景。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "select"
9:   - "csv"
10:   - "列选择"
11:   - "列重排"
12:   - "数据预处理"
13: triggers:
14:   - "需要从 CSV 中选择特定列"
15:   - "需要调整列顺序或删除列"
16:   - "需要按名称、索引、范围或正则筛选列"
17:   - "需要反转、复制或随机打乱列顺序"
18: examples:
19:   - input: "选择第一和第四列"
20:     output: "qsv select 1,4"
21:   - input: "删除 SSN、account_no 和 password 列"
22:     output: "qsv select '!/SSN|account_no|password/'"
23:   - input: "反转列顺序"
24:     output: "qsv select _-1"
25: ---
26: 
27: # CSV 列选择与重排
28: 
29: 使用 qsv select 按索引、名称、范围或正则选择、重排、反转、复制或删除 CSV 列。适用于需要从 CSV 中提取或调整列顺序的场景。
30: 
31: ## Prompt
32: 
33: 使用 qsv select 对 CSV 数据执行列级操作。根据目标选择合适的选择器语法：索引（如 1,4）、范围（如 1-4、3-）、名称（如 Header1-Header4）、正则（如 /^a/）、排除（如 !1-2）、末列特殊字符 _、重复名称索引（如 Foo[2]）。可组合多种选择器实现重排与复制。需要排序时加 --sort，需要随机打乱时加 --random（可配合 --seed 复现）。列名与选择器语法冲突时用引号包裹。
34: 
35: ## Objective
36: 
37: 从 CSV 数据中高效选择、重排、反转、复制或删除列。
38: ## Applicable Signals
39: 
40: - 输入为 CSV 格式数据
41: - 需要提取或调整列顺序
42: - 需要按列名或列索引定位列
43: - 需要删除敏感或不需要的列
44: 
45: ## Contraindications
46: 
47: - 需要处理非 CSV 格式数据
48: - 需要修改列内容而非选择列
49: 
50: ## Intervention Moves
51: 
52: - 按索引选择列：qsv select 1,4
53: - 按范围选择列：qsv select 1-4 或 qsv select 3-
54: - 按名称选择列：qsv select Header1-Header4
55: - 排除列：qsv select '!1-2'
56: - 使用末列特殊字符：qsv select 1,_
57: - 反转列顺序：qsv select _-1
58: - 正则选择列：qsv select /^a/
59: - 正则排除列：qsv select '!/SSN|account_no|password/'
60: - 排序：qsv select 1- --sort
61: - 随机打乱：qsv select 1- --random --seed 42
62: - 组合选择器重排与复制：qsv select 3-1,Header3-Header1,Header1,Foo[2],Header1
63: - 列名冲突时加引号：qsv select '"Date - Opening","Date - Actual Closing"'
64: 
65: ## Workflow Steps
66: 
67: - 确认输入为 CSV 数据并明确目标列
68: - 根据列位置或名称选择合适的选择器语法
69: - 组合选择器实现重排、复制或删除
70: - 按需添加 --sort 或 --random 选项
71: - 执行 qsv select 并验证输出列符合预期
72: 
73: ## Constraints
74: 
75: - 仅适用于 CSV 格式数据
76: - 仅执行列选择与重排，不修改列内容
77: - 列名与选择器语法冲突时需用引号包裹
78: 
79: ## Cautions
80: 
81: - 正则排除敏感列时需确认匹配范围，避免误删或遗漏
82: - 使用 --random 时建议配合 --seed 以保证可复现
83: 
84: ## Output Contract
85: 
86: - 输出包含所选列的新 CSV 数据。
87: 
88: ## Example Therapist Responses
89: 
90: ### Example 1
91: 
92: - Client/Input: 选择第一和第四列
93: - Therapist/Output: qsv select 1,4
94: 
95: ### Example 2
96: 
97: - Client/Input: 删除 SSN、account_no 和 password 列
98: - Therapist/Output: qsv select '!/SSN|account_no|password/'
99: 
100: ### Example 3
101: 
102: - Client/Input: 反转列顺序
103: - Therapist/Output: qsv select _-1
104: 
105: ## Triggers
106: 
107: - 需要从 CSV 中选择特定列
108: - 需要调整列顺序或删除列
109: - 需要按名称、索引、范围或正则筛选列
110: - 需要反转、复制或随机打乱列顺序
111: 
112: ## Examples
113: 
114: ### Example 1
115: 
116: Input:
117: 
118:   选择第一和第四列
119: 
120: Output:
121: 
122:   qsv select 1,4
123: 
124: ### Example 2
125: 
126: Input:
127: 
128:   删除 SSN、account_no 和 password 列
129: 
130: Output:
131: 
132:   qsv select '!/SSN|account_no|password/'
133: 
134: ### Example 3
135: 
136: Input:
137: 
138:   反转列顺序
139: 
140: Output:
141: 
142:   qsv select _-1

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\列排序与随机打乱\SKILL.md

1: ---
2: id: "500c276a-5f59-5af9-86f5-4c0fbf4ad1be"
3: name: "列排序与随机打乱"
4: description: "对选定的 CSV 列进行字典序排序或随机打乱，用于在列选择之后重新排列列顺序。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "select"
9:   - "列操作"
10:   - "排序"
11:   - "随机化"
12: triggers:
13:   - "需要按列名字典序排列列"
14:   - "需要随机打乱列顺序"
15:   - "需要在列选择后重新排列列"
16: examples:
17:   - input: "qsv select 1- --sort"
18:     output: "按列名字典序排列的列"
19:     notes: "字典序排序"
20:   - input: "qsv select 1- --random --seed 42"
21:     output: "以种子 42 随机打乱后的列"
22:     notes: "可复现的随机打乱"
23: ---
24: 
25: # 列排序与随机打乱
26: 
27: 对选定的 CSV 列进行字典序排序或随机打乱，用于在列选择之后重新排列列顺序。
28: 
29: ## Prompt
30: 
31: 在已确定要操作的列集合后，使用 qsv select 的 --sort 选项按列名字节值进行字典序排序，或使用 --random 选项随机打乱列顺序。可配合 --seed 使随机打乱结果可复现。
32: 
33: ## Objective
34: 
35: 对选定的列进行排序或随机打乱。
36: ## Applicable Signals
37: 
38: - 需要按列名字典序排列
39: - 需要随机打乱列顺序
40: 
41: ## Contraindications
42: 
43: - 需要保持原始列顺序
44: - 需要按列内容排序
45: 
46: ## Intervention Moves
47: 
48: - 使用 --sort 按字节值对列进行字典序排序
49: - 使用 --random 随机打乱列顺序
50: - 使用 --random --seed 使随机打乱可复现
51: 
52: ## Workflow Steps
53: 
54: - 确定要操作的列集合（如 1- 表示全部列）
55: - 选择 --sort 进行字典序排序，或选择 --random 进行随机打乱
56: - 如需可复现的随机结果，附加 --seed 指定种子
57: - 执行 qsv select 命令并检查输出列顺序
58: 
59: ## Constraints
60: 
61: - --sort 按列名的字节值排序，而非按列内容
62: - --random 打乱列顺序，不改变列内容
63: 
64: ## Cautions
65: 
66: - 随机打乱结果默认不可复现，如需复现须指定 --seed
67: 
68: ## Output Contract
69: 
70: - 输出排序或打乱后的列。
71: 
72: ## Example Therapist Responses
73: 
74: ### Example 1
75: 
76: - Client/Input: qsv select 1- --sort
77: - Therapist/Output: 按列名字典序排列的列
78: - Notes: 字典序排序
79: 
80: ### Example 2
81: 
82: - Client/Input: qsv select 1- --random --seed 42
83: - Therapist/Output: 以种子 42 随机打乱后的列
84: - Notes: 可复现的随机打乱
85: 
86: ## Triggers
87: 
88: - 需要按列名字典序排列列
89: - 需要随机打乱列顺序
90: - 需要在列选择后重新排列列
91: 
92: ## Examples
93: 
94: ### Example 1
95: 
96: Input:
97: 
98:   qsv select 1- --sort
99: 
100: Output:
101: 
102:   按列名字典序排列的列
103: 
104: Notes:
105: 
106:   字典序排序
107: 
108: ### Example 2
109: 
110: Input:
111: 
112:   qsv select 1- --random --seed 42
113: 
114: Output:
115: 
116:   以种子 42 随机打乱后的列
117: 
118: Notes:
119: 
120:   可复现的随机打乱

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\引用冲突列名进行-qsv-select\SKILL.md

1: ---
2: id: "b0592fe3-a3d5-539a-af63-d33035c20003"
3: name: "引用冲突列名进行 qsv select"
4: description: "当 CSV 列名包含空格、连字符等与 qsv select 选择器语法冲突的字符时，用引号正确引用列名，从而准确选中目标列。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "select"
9:   - "列选择"
10:   - "引用转义"
11:   - "特殊字符"
12: triggers:
13:   - "列名包含空格或连字符等特殊字符"
14:   - "列名与选择器语法冲突"
15:   - "直接书写列名导致解析错误或选中错误列"
16: examples:
17:   - input: "列名为 'Date - Opening' 与 'Date - Actual Closing'，需选择这两列"
18:     output: "qsv select '\"Date - Opening\",\"Date - Actual Closing\"'"
19:     notes: "用引号包裹含空格和连字符的列名以避免语法冲突"
20: ---
21: 
22: # 引用冲突列名进行 qsv select
23: 
24: 当 CSV 列名包含空格、连字符等与 qsv select 选择器语法冲突的字符时，用引号正确引用列名，从而准确选中目标列。
25: 
26: ## Prompt
27: 
28: 在执行 qsv select 选择列时，先检查目标列名是否包含空格、连字符或其他与选择器语法冲突的字符。若存在冲突，用引号将列名整体包裹后再传入选择器，确保列名被当作字面名称而非选择器表达式解析。
29: 
30: ## Objective
31: 
32: 正确引用包含特殊字符的列名以避免语法冲突。
33: ## Applicable Signals
34: 
35: - 列名包含空格、连字符等特殊字符
36: - 列名与选择器语法冲突
37: 
38: ## Contraindications
39: 
40: - 列名简单无特殊字符时无需引用
41: 
42: ## Intervention Moves
43: 
44: - 识别列名中与选择器语法冲突的字符
45: - 用引号包裹冲突列名后传入选择器
46: 
47: ## Workflow Steps
48: 
49: - 检查目标列名是否包含空格、连字符等特殊字符
50: - 若存在冲突，用引号将列名整体包裹
51: - 将引用后的列名作为选择器参数执行 qsv select
52: - 确认选中列与预期一致
53: 
54: ## Constraints
55: 
56: - 仅在列名与选择器语法冲突时使用引用
57: - 引用需包裹完整列名
58: 
59: ## Cautions
60: 
61: - 引用不当可能导致列名被误解析
62: 
63: ## Output Contract
64: 
65: - 正确解析列名并选择对应列。
66: 
67: ## Example Therapist Responses
68: 
69: ### Example 1
70: 
71: - Client/Input: 列名为 'Date - Opening' 与 'Date - Actual Closing'，需选择这两列
72: - Therapist/Output: qsv select '"Date - Opening","Date - Actual Closing"'
73: - Notes: 用引号包裹含空格和连字符的列名以避免语法冲突
74: 
75: ## Triggers
76: 
77: - 列名包含空格或连字符等特殊字符
78: - 列名与选择器语法冲突
79: - 直接书写列名导致解析错误或选中错误列
80: 
81: ## Examples
82: 
83: ### Example 1
84: 
85: Input:
86: 
87:   列名为 'Date - Opening' 与 'Date - Actual Closing'，需选择这两列
88: 
89: Output:
90: 
91:   qsv select '"Date - Opening","Date - Actual Closing"'
92: 
93: Notes:
94: 
95:   用引号包裹含空格和连字符的列名以避免语法冲突

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\SkillBank\Users\docskill\正则表达式列选择\SKILL.md

1: ---
2: id: "bd72bc3b-8c84-59c2-9fd4-5caba1a5350b"
3: name: "正则表达式列选择"
4: description: "使用正则表达式匹配列名，从 CSV 数据中选择或排除符合模式的列。适用于列名具有规律、需要按模式批量选择或排除列的场景。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "select"
9:   - "regex"
10:   - "column-selection"
11:   - "csv"
12: triggers:
13:   - "列名符合某种模式"
14:   - "需要批量选择或排除列"
15:   - "需要按列名模式移除敏感列"
16: examples:
17:   - input: "选择以 'a' 开头的列"
18:     output: "qsv select /^a/"
19:   - input: "移除 SSN、account_no 和 password 列"
20:     output: "qsv select '!/SSN|account_no|password/'"
21: ---
22: 
23: # 正则表达式列选择
24: 
25: 使用正则表达式匹配列名，从 CSV 数据中选择或排除符合模式的列。适用于列名具有规律、需要按模式批量选择或排除列的场景。
26: 
27: ## Prompt
28: 
29: 当需要按列名模式批量选择或排除列时，使用 qsv select 的正则表达式选择器。
30: 
31: 执行步骤：
32: 1. 确认列名具有可描述的模式（如统一前缀、包含数字、特定关键词）。
33: 2. 选择匹配模式：使用 /pattern/ 形式选择匹配的列，例如 qsv select /^a/ 选择以 a 开头的列。
34: 3. 排除匹配模式：使用 !/pattern/ 形式排除匹配的列，例如 qsv select '!/SSN|account_no|password/' 移除敏感列。
35: 4. 如模式包含特殊字符或空格，用引号包裹选择器。
36: 5. 验证输出列是否符合预期。
37: 
38: 注意：正则表达式匹配的是列名而非列内容；若列名无规律或需精确指定列，应改用索引或列名选择器。
39: 
40: ## Objective
41: 
42: 通过正则表达式匹配列名来选择或排除列。
43: ## Applicable Signals
44: 
45: - 列名具有统一前缀或后缀
46: - 列名包含特定关键词或数字模式
47: - 需要批量排除敏感列
48: 
49: ## Contraindications
50: 
51: - 列名无规律
52: - 需要精确指定列
53: - 需要按列内容而非列名筛选
54: 
55: ## Intervention Moves
56: 
57: - 使用 /pattern/ 选择匹配列
58: - 使用 !/pattern/ 排除匹配列
59: - 对含特殊字符的模式加引号
60: 
61: ## Workflow Steps
62: 
63: - 确认列名模式
64: - 构造正则选择器
65: - 执行 qsv select 命令
66: - 验证输出列
67: 
68: ## Constraints
69: 
70: - 正则表达式匹配列名而非列内容
71: - 模式含特殊字符时需加引号
72: 
73: ## Cautions
74: 
75: - 正则过于宽泛可能匹配到非预期列
76: - 排除敏感列后应确认输出不含敏感数据
77: 
78: ## Output Contract
79: 
80: - 输出匹配正则的列。
81: 
82: ## Example Therapist Responses
83: 
84: ### Example 1
85: 
86: - Client/Input: 选择以 'a' 开头的列
87: - Therapist/Output: qsv select /^a/
88: 
89: ### Example 2
90: 
91: - Client/Input: 移除 SSN、account_no 和 password 列
92: - Therapist/Output: qsv select '!/SSN|account_no|password/'
93: 
94: ## Triggers
95: 
96: - 列名符合某种模式
97: - 需要批量选择或排除列
98: - 需要按列名模式移除敏感列
99: 
100: ## Examples
101: 
102: ### Example 1
103: 
104: Input:
105: 
106:   选择以 'a' 开头的列
107: 
108: Output:
109: 
110:   qsv select /^a/
111: 
112: ### Example 2
113: 
114: Input:
115: 
116:   移除 SSN、account_no 和 password 列
117: 
118: Output:
119: 
120:   qsv select '!/SSN|account_no|password/'

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\Users\docskill\csv-内存排序执行\SKILL.md

1: ---
2: id: "353ba11e-1351-58c3-bb24-f91c7e24da8d"
3: name: "CSV 内存排序执行"
4: description: "使用 qsv sort 对可全部载入内存的 CSV 数据按字典序、自然序、数值、逆序、去重或随机顺序进行排序并输出结果。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "sort"
9:   - "CSV"
10:   - "数据变换"
11:   - "命令行排序"
12: triggers:
13:   - "需要对 CSV 文件进行排序"
14:   - "数据量可全部载入内存"
15:   - "需要字典序/自然序/数值/逆序/去重/随机排序"
16: ---
17: 
18: # CSV 内存排序执行
19: 
20: 使用 qsv sort 对可全部载入内存的 CSV 数据按字典序、自然序、数值、逆序、去重或随机顺序进行排序并输出结果。
21: 
22: ## Prompt
23: 
24: 在确认 CSV 数据可全部载入内存后，调用 qsv sort 并指定所需排序方式（字典序、自然序、数值、逆序、去重或随机），执行排序并输出排序后的 CSV。若数据量过大无法载入内存，改用 extsort；若仅需校验排序结果，改用 sortcheck。
25: 
26: ## Objective
27: 
28: 对可载入内存的 CSV 数据执行指定顺序的排序并输出排序结果。
29: ## Applicable Signals
30: 
31: - 需要对 CSV 文件进行排序
32: - 数据量可全部载入内存
33: - 需要字典序/自然序/数值/逆序/去重/随机排序
34: 
35: ## Contraindications
36: 
37: - CSV 文件过大无法载入内存（应改用 extsort）
38: - 仅需校验排序结果（应改用 sortcheck）
39: 
40: ## Intervention Moves
41: 
42: - 确认数据可全部载入内存
43: - 调用 qsv sort 并指定排序方式
44: - 输出排序后的 CSV
45: 
46: ## Workflow Steps
47: 
48: - 确认 CSV 数据可全部载入内存
49: - 调用 qsv sort 并指定所需排序方式（字典序、自然序、数值、逆序、去重或随机）
50: - 执行排序并输出排序后的 CSV
51: 
52: ## Constraints
53: 
54: - 此命令需要将所有 CSV 数据读入内存
55: - 若数据量过大无法载入内存，应改用 extsort
56: - 若仅需校验排序结果，应改用 sortcheck
57: 
58: ## Cautions
59: 
60: - 排序前需评估数据规模是否可全部载入内存
61: 
62: ## Output Contract
63: 
64: - 排序后的 CSV 输出或文件。
65: 
66: ## Triggers
67: 
68: - 需要对 CSV 文件进行排序
69: - 数据量可全部载入内存
70: - 需要字典序/自然序/数值/逆序/去重/随机排序

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\Users\docskill\大文件外存排序切换\SKILL.md

1: ---
2: id: "cc5a002d-6830-5192-b841-d8233e6ce4e3"
3: name: "大文件外存排序切换"
4: description: "当待排序 CSV 文件过大、可能无法全部载入内存时，将排序任务从默认内存排序切换为 extsort 外存排序方案，以完成大规模排序。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "csv"
9:   - "sort"
10:   - "extsort"
11:   - "外存排序"
12:   - "内存受限"
13: triggers:
14:   - "CSV 文件过大无法载入内存"
15:   - "需要排序但内存受限"
16:   - "排序任务可能超出可用内存"
17: examples:
18:   - input: "需要对一个可能无法全部载入内存的大 CSV 文件排序"
19:     output: "改用 extsort 命令执行外存排序，产出排序后的 CSV"
20:     notes: "数据可全部载入内存时应使用 qsv sort"
21: ---
22: 
23: # 大文件外存排序切换
24: 
25: 当待排序 CSV 文件过大、可能无法全部载入内存时，将排序任务从默认内存排序切换为 extsort 外存排序方案，以完成大规模排序。
26: 
27: ## Prompt
28: 
29: 判断待排序 CSV 是否可能无法全部载入内存。若内存受限或文件过大，改用 extsort 命令执行外存排序，而不是使用默认的内存排序命令。执行前确认输入文件路径与排序需求，执行后确认输出为完成排序的 CSV。
30: 
31: ## Objective
32: 
33: 在内存不足时选择外存排序方案完成大文件排序。
34: ## Applicable Signals
35: 
36: - 待排序 CSV 文件体积大，可能无法全部读入内存
37: - 运行环境内存受限
38: - 默认内存排序不可行或存在内存溢出风险
39: 
40: ## Contraindications
41: 
42: - 数据可全部载入内存时，应使用 qsv sort 而非外存排序
43: 
44: ## Intervention Moves
45: 
46: - 评估文件大小与可用内存，判断是否需要外存排序
47: - 将排序命令切换为 extsort
48: - 使用 extsort 执行大文件排序并产出排序后的 CSV
49: 
50: ## Workflow Steps
51: 
52: - 确认待排序 CSV 文件及排序需求
53: - 判断文件是否可能无法全部载入内存
54: - 若内存受限，改用 extsort 命令执行外存排序
55: - 确认输出为完成排序的 CSV 数据
56: 
57: ## Constraints
58: 
59: - 仅在内存受限或文件过大无法全部载入内存时使用外存排序
60: - 数据可全部载入内存时应使用 qsv sort
61: 
62: ## Cautions
63: 
64: - 外存排序适用于大文件场景，不应作为默认排序流程
65: 
66: ## Output Contract
67: 
68: - 使用 extsort 完成的大文件排序输出。
69: 
70: ## Example Therapist Responses
71: 
72: ### Example 1
73: 
74: - Client/Input: 需要对一个可能无法全部载入内存的大 CSV 文件排序
75: - Therapist/Output: 改用 extsort 命令执行外存排序，产出排序后的 CSV
76: - Notes: 数据可全部载入内存时应使用 qsv sort
77: 
78: ## Triggers
79: 
80: - CSV 文件过大无法载入内存
81: - 需要排序但内存受限
82: - 排序任务可能超出可用内存
83: 
84: ## Examples
85: 
86: ### Example 1
87: 
88: Input:
89: 
90:   需要对一个可能无法全部载入内存的大 CSV 文件排序
91: 
92: Output:
93: 
94:   改用 extsort 命令执行外存排序，产出排序后的 CSV
95: 
96: Notes:
97: 
98:   数据可全部载入内存时应使用 qsv sort

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case002_qsv_sort\clean\rd9ced750fa54\SkillBank\Users\docskill\排序结果校验\SKILL.md

1: ---
2: id: "7ab97840-0c8c-5685-88d2-36bdb1faefea"
3: name: "排序结果校验"
4: description: "使用 sortcheck 命令校验 CSV 数据是否已按预期顺序排序，用于验证排序正确性或检查数据有序性。"
5: version: "0.1.0"
6: tags:
7:   - "qsv"
8:   - "sortcheck"
9:   - "CSV"
10:   - "排序校验"
11:   - "数据验证"
12: triggers:
13:   - "需要验证 CSV 是否已排序"
14:   - "需要检查排序结果正确性"
15:   - "需要确认数据有序性"
16: ---
17: 
18: # 排序结果校验
19: 
20: 使用 sortcheck 命令校验 CSV 数据是否已按预期顺序排序，用于验证排序正确性或检查数据有序性。
21: 
22: ## Prompt
23: 
24: 当需要确认 CSV 数据是否已按预期顺序排序时，调用 sortcheck 命令进行校验。该技能只做校验，不执行实际排序。
25: 
26: 执行步骤：
27: 1. 确认目标 CSV 文件及期望的排序顺序（字典序、自然序、数值序、逆序、唯一或随机等）。
28: 2. 调用 sortcheck 命令对目标文件进行校验。
29: 3. 读取校验结果，判断是否通过。
30: 4. 若校验失败，向调用方返回失败结果，并提示可能需要使用 qsv sort 重新排序。
31: 
32: 注意：sortcheck 仅用于验证，不改变数据。
33: 
34: ## Objective
35: 
36: 检查 CSV 数据是否满足指定排序顺序。
37: ## Applicable Signals
38: 
39: - 需要验证 CSV 是否已排序
40: - 需要检查排序结果正确性
41: 
42: ## Contraindications
43: 
44: - 需要实际执行排序（应使用 qsv sort）
45: 
46: ## Intervention Moves
47: 
48: - 调用 sortcheck 命令对目标 CSV 进行排序校验
49: - 读取并返回校验结果（通过/失败）
50: 
51: ## Workflow Steps
52: 
53: - 确认目标 CSV 文件及期望的排序顺序
54: - 调用 sortcheck 命令进行校验
55: - 读取校验结果并判断是否通过
56: - 若失败则返回失败结果并提示可能需要使用 qsv sort 重新排序
57: 
58: ## Constraints
59: 
60: - 仅用于校验，不执行实际排序
61: - 不修改原始数据
62: 
63: ## Cautions
64: 
65: - sortcheck 只做验证，若校验失败需另行使用 qsv sort 进行排序
66: 
67: ## Output Contract
68: 
69: - 排序校验结果（通过/失败）。
70: 
71: ## Triggers
72: 
73: - 需要验证 CSV 是否已排序
74: - 需要检查排序结果正确性
75: - 需要确认数据有序性

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\Users\docskill\docker-cp-符号链接复制策略选择\SKILL.md

1: ---
2: id: "23370d93-9d3f-5142-bfed-e6ff22cb9b36"
3: name: "docker cp 符号链接复制策略选择"
4: description: "当 docker cp 的 SRC_PATH 为本地符号链接时，决定默认复制链接本身还是使用 -L 选项复制链接目标，用于需要明确控制符号链接处理语义的复制场景。"
5: version: "0.1.0"
6: tags:
7:   - "docker"
8:   - "docker-cp"
9:   - "符号链接"
10:   - "选项配置"
11: triggers:
12:   - "SRC_PATH 是本地符号链接"
13:   - "需要复制链接目标而非链接本身"
14:   - "需要明确控制符号链接复制语义"
15: examples:
16:   - input: "SRC_PATH 是本地符号链接，希望复制链接指向的目标内容"
17:     output: "在 docker cp 命令中添加 -L 选项，复制链接目标"
18:     notes: "默认不加 -L 时复制的是符号链接本身"
19:   - input: "SRC_PATH 是本地符号链接，希望保留链接本身"
20:     output: "不添加 -L 选项，复制符号链接本身"
21:     notes: "符合默认行为"
22: ---
23: 
24: # docker cp 符号链接复制策略选择
25: 
26: 当 docker cp 的 SRC_PATH 为本地符号链接时，决定默认复制链接本身还是使用 -L 选项复制链接目标，用于需要明确控制符号链接处理语义的复制场景。
27: 
28: ## Prompt
29: 
30: 在执行 docker cp 前，先判断 SRC_PATH 是否为本地符号链接。若是符号链接，默认行为是复制符号链接本身而非其目标；若需要复制链接指向的目标内容，则在命令中显式添加 -L 选项。确认后输出是否添加 -L 及实际复制对象。
31: 
32: ## Objective
33: 
34: 在符号链接源路径下选择复制链接本身或链接目标
35: ## Applicable Signals
36: 
37: - SRC_PATH 为本地符号链接
38: - 复制结果需要区分链接本身与链接目标
39: 
40: ## Contraindications
41: 
42: - SRC_PATH 不是符号链接
43: - 不需要控制符号链接语义
44: 
45: ## Intervention Moves
46: 
47: - 判断 SRC_PATH 是否为本地符号链接
48: - 默认保留复制链接本身的行为
49: - 如需复制链接目标则添加 -L 选项
50: 
51: ## Workflow Steps
52: 
53: - 确认 SRC_PATH 是本地路径且为符号链接
54: - 判断期望复制对象是链接本身还是链接目标
55: - 若复制链接目标，则在 docker cp 命令中加入 -L 选项
56: - 输出最终命令及复制对象说明
57: 
58: ## Constraints
59: 
60: - 仅在 SRC_PATH 为本地符号链接时适用
61: - 默认行为为复制符号链接本身，不加 -L
62: 
63: ## Cautions
64: 
65: - 若误判符号链接语义，可能复制到链接文件而非目标内容
66: 
67: ## Output Contract
68: 
69: - 确定是否添加 -L 选项并说明复制对象
70: 
71: ## Example Therapist Responses
72: 
73: ### Example 1
74: 
75: - Client/Input: SRC_PATH 是本地符号链接，希望复制链接指向的目标内容
76: - Therapist/Output: 在 docker cp 命令中添加 -L 选项，复制链接目标
77: - Notes: 默认不加 -L 时复制的是符号链接本身
78: 
79: ### Example 2
80: 
81: - Client/Input: SRC_PATH 是本地符号链接，希望保留链接本身
82: - Therapist/Output: 不添加 -L 选项，复制符号链接本身
83: - Notes: 符合默认行为
84: 
85: ## Triggers
86: 
87: - SRC_PATH 是本地符号链接
88: - 需要复制链接目标而非链接本身
89: - 需要明确控制符号链接复制语义
90: 
91: ## Examples
92: 
93: ### Example 1
94: 
95: Input:
96: 
97:   SRC_PATH 是本地符号链接，希望复制链接指向的目标内容
98: 
99: Output:
100: 
101:   在 docker cp 命令中添加 -L 选项，复制链接目标
102: 
103: Notes:
104: 
105:   默认不加 -L 时复制的是符号链接本身
106: 
107: ### Example 2
108: 
109: Input:
110: 
111:   SRC_PATH 是本地符号链接，希望保留链接本身
112: 
113: Output:
114: 
115:   不添加 -L 选项，复制符号链接本身
116: 
117: Notes:
118: 
119:   符合默认行为

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case003_docker_cp\clean\rab9a070dfa59\SkillBank\Users\docskill\docker-cp-路径语义判定\SKILL.md

1: ---
2: id: "0be52a4b-b68d-5166-a0c1-668834d1f64a"
3: name: "docker cp 路径语义判定"
4: description: "根据 SRC_PATH 与 DEST_PATH 的存在性、类型（文件/目录）以及是否以 / 或 /. 结尾，判定 docker cp 的复制行为或错误条件。用于在执行或解释 docker cp 前确定目标路径应如何被解释。"
5: version: "0.1.0"
6: tags:
7:   - "docker"
8:   - "docker-cp"
9:   - "路径语义"
10:   - "文件复制"
11:   - "知识参考"
12: triggers:
13:   - "需要预测 docker cp 对某组 SRC_PATH/DEST_PATH 的行为"
14:   - "目标路径不存在或类型不明确"
15:   - "源路径以 /. 结尾需要区分复制目录本身还是其内容"
16: examples:
17:   - input: "SRC_PATH 为文件，DEST_PATH 不存在"
18:     output: "文件被保存到在 DEST_PATH 新建的文件"
19:   - input: "SRC_PATH 为文件，DEST_PATH 不存在且以 / 结尾"
20:     output: "错误条件：目标目录必须已存在"
21:   - input: "SRC_PATH 为目录且以 /. 结尾，DEST_PATH 存在且为目录"
22:     output: "源目录的内容被复制进该目录"
23: ---
24: 
25: # docker cp 路径语义判定
26: 
27: 根据 SRC_PATH 与 DEST_PATH 的存在性、类型（文件/目录）以及是否以 / 或 /. 结尾，判定 docker cp 的复制行为或错误条件。用于在执行或解释 docker cp 前确定目标路径应如何被解释。
28: 
29: ## Prompt
30: 
31: 给定一组 SRC_PATH 与 DEST_PATH，按以下规则判定 docker cp 的复制语义或错误条件：
32: 1. 若 SRC_PATH 为文件：
33:    - DEST_PATH 不存在：文件被保存到在 DEST_PATH 新建的文件。
34:    - DEST_PATH 不存在且以 / 结尾：错误条件，目标目录必须已存在。
35:    - DEST_PATH 存在且为文件：目标被源文件内容覆盖。
36:    - DEST_PATH 存在且为目录：文件以 SRC_PATH 的 basename 复制进该目录。
37: 2. 若 SRC_PATH 为目录：
38:    - DEST_PATH 不存在：DEST_PATH 被创建为目录，源目录的内容被复制进去。
39:    - DEST_PATH 存在且为文件：错误条件，不能将目录复制到文件。
40:    - DEST_PATH 存在且为目录：
41:      - SRC_PATH 不以 /. 结尾：源目录本身被复制进该目录。
42:      - SRC_PATH 以 /. 结尾：源目录的内容被复制进该目录。
43: 3. 路径分隔符按 / 处理。
44: 4. 若 SRC_PATH 为本地符号链接，默认复制符号链接本身而非其目标；如需复制链接目标而非链接，需指定 -L 选项（该选项选择不在本判定范围内）。
45: 输出对给定路径组合的明确复制结果或错误条件判定。
46: 
47: ## Objective
48: 
49: 准确判定 docker cp 在给定源/目标路径组合下的复制语义与错误条件
50: ## Applicable Signals
51: 
52: - 提供了一组 SRC_PATH 与 DEST_PATH 需要判定行为
53: - DEST_PATH 的存在性或类型（文件/目录）不明确
54: - SRC_PATH 以 /. 结尾，需要区分复制目录本身还是其内容
55: - 需要确认某路径组合是否构成错误条件
56: 
57: ## Contraindications
58: 
59: - 需要实际执行复制而非判定语义
60: - 涉及符号链接目标复制选择（应使用 -L 相关规则）
61: 
62: ## Intervention Moves
63: 
64: - 确认 SRC_PATH 是文件还是目录
65: - 确认 DEST_PATH 是否存在及其类型（文件/目录）
66: - 检查 DEST_PATH 是否以 / 结尾
67: - 检查 SRC_PATH 是否以 /. 结尾
68: - 按规则表匹配并输出复制结果或错误条件
69: 
70: ## Workflow Steps
71: 
72: - 判定 SRC_PATH 的类型：文件或目录。
73: - 判定 DEST_PATH 的存在性与类型：不存在、文件或目录。
74: - 若 SRC_PATH 为文件：按 DEST_PATH 不存在 / 不存在且以 / 结尾 / 存在且为文件 / 存在且为目录 四种情形分别判定。
75: - 若 SRC_PATH 为目录：按 DEST_PATH 不存在 / 存在且为文件 / 存在且为目录 三种情形分别判定；在 DEST_PATH 为目录时进一步依据 SRC_PATH 是否以 /. 结尾区分复制目录本身还是其内容。
76: - 输出明确的复制结果或错误条件判定。
77: 
78: ## Constraints
79: 
80: - 路径分隔符按 / 处理。
81: - SRC_PATH 与 DEST_PATH 需按上述规则存在，否则为错误条件。
82: - 本判定不覆盖 -L 选项对符号链接目标的处理。
83: 
84: ## Cautions
85: 
86: - DEST_PATH 不存在且以 / 结尾时为目标目录必须已存在的错误条件。
87: - DEST_PATH 存在且为文件而 SRC_PATH 为目录时为不能将目录复制到文件的错误条件。
88: - SRC_PATH 为本地符号链接时默认复制符号链接本身而非其目标。
89: 
90: ## Output Contract
91: 
92: - 对给定路径组合输出明确的复制结果或错误条件判定。
93: 
94: ## Example Therapist Responses
95: 
96: ### Example 1
97: 
98: - Client/Input: SRC_PATH 为文件，DEST_PATH 不存在
99: - Therapist/Output: 文件被保存到在 DEST_PATH 新建的文件
100: 
101: ### Example 2
102: 
103: - Client/Input: SRC_PATH 为文件，DEST_PATH 不存在且以 / 结尾
104: - Therapist/Output: 错误条件：目标目录必须已存在
105: 
106: ### Example 3
107: 
108: - Client/Input: SRC_PATH 为目录且以 /. 结尾，DEST_PATH 存在且为目录
109: - Therapist/Output: 源目录的内容被复制进该目录
110: 
111: ## Triggers
112: 
113: - 需要预测 docker cp 对某组 SRC_PATH/DEST_PATH 的行为
114: - 目标路径不存在或类型不明确
115: - 源路径以 /. 结尾需要区分复制目录本身还是其内容
116: 
117: ## Examples
118: 
119: ### Example 1
120: 
121: Input:
122: 
123:   SRC_PATH 为文件，DEST_PATH 不存在
124: 
125: Output:
126: 
127:   文件被保存到在 DEST_PATH 新建的文件
128: 
129: ### Example 2
130: 
131: Input:
132: 
133:   SRC_PATH 为文件，DEST_PATH 不存在且以 / 结尾
134: 
135: Output:
136: 
137:   错误条件：目标目录必须已存在
138: 
139: ### Example 3
140: 
141: Input:
142: 
143:   SRC_PATH 为目录且以 /. 结尾，DEST_PATH 存在且为目录
144: 
145: Output:
146: 
147:   源目录的内容被复制进该目录

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\git-restore-命令语法与选项查阅\SKILL.md

1: ---
2: id: "3810431b-3f7d-505a-86e2-a7fde1141964"
3: name: "git restore 命令语法与选项查阅"
4: description: "提供 git restore 的调用形式与关键选项的查阅型参考，用于确认如何指定恢复来源、暂存区或工作区以及路径规格。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "命令参考"
10:   - "语法查阅"
11: triggers:
12:   - "需要确认 git restore 的语法或选项含义"
13:   - "需要了解 --source/--staged/--worktree/--patch 等参数用途"
14: ---
15: 
16: # git restore 命令语法与选项查阅
17: 
18: 提供 git restore 的调用形式与关键选项的查阅型参考，用于确认如何指定恢复来源、暂存区或工作区以及路径规格。
19: 
20: ## Prompt
21: 
22: 当调用方需要确认 git restore 的语法或选项含义时，提供其调用形式与关键选项说明：
23: - 基本形式：'git restore' [<options>] [--source=<tree>] [--staged] [--worktree] [--] <pathspec>...
24: - 从文件读取路径规格：'git restore' [<options>] [--source=<tree>] [--staged] [--worktree] --pathspec-from-file=<file> [--pathspec-file-nul]
25: - 交互式补丁模式：'git restore' (-p|--patch) [<options>] [--source=<tree>] [--staged] [--worktree] [--] [<pathspec>...]
26: 仅作语法与选项查阅，不代为执行恢复操作。
27: 
28: ## Objective
29: 
30: 让使用者快速查阅 git restore 的调用形式与关键选项
31: ## Applicable Signals
32: 
33: - 调用方询问 git restore 的调用形式
34: - 调用方询问 --source、--staged、--worktree、--patch 等选项用途
35: - 调用方需要确认路径规格的书写方式
36: 
37: ## Contraindications
38: 
39: - 需要执行具体恢复操作而非查阅语法
40: - 需要处理非 git restore 的其他 git 命令
41: 
42: ## Intervention Moves
43: 
44: - 列出 git restore 的基本调用形式
45: - 说明 --source=<tree> 用于指定恢复来源
46: - 说明 --staged 与 --worktree 用于指定恢复目标区域
47: - 说明 --pathspec-from-file 与 --pathspec-file-nul 用于从文件读取路径规格
48: - 说明 -p/--patch 用于交互式补丁模式
49: 
50: ## Workflow Steps
51: 
52: - 确认调用方需求为查阅 git restore 语法或选项
53: - 给出对应的调用形式
54: - 解释相关选项含义
55: - 如涉及具体操作，提示调用方自行执行
56: 
57: ## Constraints
58: 
59: - 仅提供语法与选项说明，不代为执行恢复操作
60: - 不扩展到其他 git 命令
61: 
62: ## Cautions
63: 
64: - 选项含义以官方文档为准，避免凭记忆给出不准确说明
65: 
66: ## Output Contract
67: 
68: - 使用者获得 git restore 的准确语法与选项说明
69: 
70: ## Triggers
71: 
72: - 需要确认 git restore 的语法或选项含义
73: - 需要了解 --source/--staged/--worktree/--patch 等参数用途

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\git-restore-默认恢复源解析\SKILL.md

1: ---
2: id: "7b96215d-c31b-5095-aed4-9eaca3b18ffb"
3: name: "Git Restore 默认恢复源解析"
4: description: "当 git restore 未显式指定恢复源 tree 时，根据是否使用 --staged 判定默认恢复来源：使用 --staged 时从 HEAD 恢复，否则从 index 恢复。用于恢复准备阶段确定恢复来源，不执行恢复动作。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "git-restore"
9:   - "默认源"
10:   - "恢复来源"
11:   - "HEAD"
12:   - "index"
13: triggers:
14:   - "用户未指定恢复源"
15:   - "需要判断默认从 HEAD 还是 index 恢复"
16: examples:
17:   - input: "git restore --staged file.txt（未指定源）"
18:     output: "恢复源为 HEAD"
19:     notes: "因使用 --staged"
20:   - input: "git restore file.txt（未指定源）"
21:     output: "恢复源为 index"
22:     notes: "未使用 --staged"
23: ---
24: 
25: # Git Restore 默认恢复源解析
26: 
27: 当 git restore 未显式指定恢复源 tree 时，根据是否使用 --staged 判定默认恢复来源：使用 --staged 时从 HEAD 恢复，否则从 index 恢复。用于恢复准备阶段确定恢复来源，不执行恢复动作。
28: 
29: ## Prompt
30: 
31: 在未显式指定恢复源 tree 时，按以下规则确定默认恢复源：若命令包含 --staged，则恢复源为 HEAD；否则恢复源为 index。据此确定后续恢复操作的来源，不执行具体恢复动作。
32: 
33: ## Objective
34: 
35: 确定未指定源时的默认恢复来源
36: ## Applicable Signals
37: 
38: - git restore 命令中未出现 -s/--source 指定恢复源
39: - 需要明确恢复内容来自 HEAD 还是 index
40: 
41: ## Contraindications
42: 
43: - 用户已明确指定恢复源 tree
44: 
45: ## Intervention Moves
46: 
47: - 检查命令是否包含 --staged
48: - 若包含 --staged 则判定恢复源为 HEAD
49: - 若不包含 --staged 则判定恢复源为 index
50: 
51: ## Workflow Steps
52: 
53: - 确认命令未指定恢复源 tree
54: - 检查是否使用 --staged 选项
55: - 若使用 --staged，则确定恢复源为 HEAD
56: - 若未使用 --staged，则确定恢复源为 index
57: 
58: ## Constraints
59: 
60: - 仅在未指定恢复源时适用
61: - 本规则只确定恢复来源，不执行恢复动作
62: 
63: ## Cautions
64: 
65: - --patch 模式可接受无 pathspec 并提示恢复所有已修改路径，与默认源解析相关但属独立行为
66: 
67: ## Output Contract
68: 
69: - 确定恢复源为 HEAD 或 index
70: 
71: ## Example Therapist Responses
72: 
73: ### Example 1
74: 
75: - Client/Input: git restore --staged file.txt（未指定源）
76: - Therapist/Output: 恢复源为 HEAD
77: - Notes: 因使用 --staged
78: 
79: ### Example 2
80: 
81: - Client/Input: git restore file.txt（未指定源）
82: - Therapist/Output: 恢复源为 index
83: - Notes: 未使用 --staged
84: 
85: ## Triggers
86: 
87: - 用户未指定恢复源
88: - 需要判断默认从 HEAD 还是 index 恢复
89: 
90: ## Examples
91: 
92: ### Example 1
93: 
94: Input:
95: 
96:   git restore --staged file.txt（未指定源）
97: 
98: Output:
99: 
100:   恢复源为 HEAD
101: 
102: Notes:
103: 
104:   因使用 --staged
105: 
106: ### Example 2
107: 
108: Input:
109: 
110:   git restore file.txt（未指定源）
111: 
112: Output:
113: 
114:   恢复源为 index
115: 
116: Notes:
117: 
118:   未使用 --staged

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\从指定-tree-恢复工作区文件\SKILL.md

1: ---
2: id: "d472e6a7-8895-56cb-9014-cb75cc3540b3"
3: name: "从指定 tree 恢复工作区文件"
4: description: "使用 git restore 的 -s/--source 选项，从指定 commit、branch 或 tag 对应的 tree 恢复工作区文件内容。适用于需要将工作区文件回退到某个历史版本或分支状态的场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "git-restore"
9:   - "source-tree"
10:   - "working-tree"
11:   - "file-restore"
12: triggers:
13:   - "需要将工作区文件回退到某个 commit/branch/tag 的内容"
14:   - "用户明确指定了恢复源 tree"
15: ---
16: 
17: # 从指定 tree 恢复工作区文件
18: 
19: 使用 git restore 的 -s/--source 选项，从指定 commit、branch 或 tag 对应的 tree 恢复工作区文件内容。适用于需要将工作区文件回退到某个历史版本或分支状态的场景。
20: 
21: ## Prompt
22: 
23: 当需要将工作区文件内容恢复为某个指定 tree（由 commit、branch 或 tag 命名）的版本时，使用 git restore 的 -s/--source 选项执行恢复。
24: 
25: 执行步骤：
26: 1. 确认恢复源：明确用户指定的 commit、branch 或 tag，作为 -s/--source 的取值。
27: 2. 确认恢复目标：默认恢复工作区文件；若同时给出 --staged，则从 HEAD 恢复内容。
28: 3. 执行恢复：git restore -s <tree> <pathspec>，将工作区文件内容替换为指定 tree 的版本。
29: 4. 校验结果：确认工作区文件内容与指定 tree 一致。
30: 
31: 注意：
32: - 若未指定恢复源，则内容从 index 恢复；若给出 --staged，则从 HEAD 恢复。
33: - 可使用 "A...B" 作为 A 与 B 的 merge base 快捷写法（仅当恰有一个 merge base 时）；A 与 B 至多省略一个，省略者默认为 HEAD。
34: - 本技能不涉及交互式 hunk 选择（--patch）。
35: 
36: ## Objective
37: 
38: 将工作区文件内容恢复为指定 tree 的版本
39: ## Applicable Signals
40: 
41: - 需要将工作区文件回退到某个 commit/branch/tag 的内容
42: - 用户明确指定了恢复源 tree
43: 
44: ## Contraindications
45: 
46: - 未指定恢复源且需要从 index 或 HEAD 恢复
47: - 需要交互式选择 hunk（--patch）
48: 
49: ## Intervention Moves
50: 
51: - 通过 -s/--source 指定恢复源 tree（commit、branch 或 tag）
52: - 执行 git restore -s <tree> <pathspec> 恢复工作区文件
53: - 校验工作区文件内容与指定 tree 一致
54: 
55: ## Workflow Steps
56: 
57: - 确认恢复源：明确用户指定的 commit、branch 或 tag，作为 -s/--source 的取值
58: - 确认恢复目标：默认恢复工作区文件；若同时给出 --staged，则从 HEAD 恢复内容
59: - 执行恢复：git restore -s <tree> <pathspec>，将工作区文件内容替换为指定 tree 的版本
60: - 校验结果：确认工作区文件内容与指定 tree 一致
61: 
62: ## Constraints
63: 
64: - 恢复源必须由 commit、branch 或 tag 命名
65: - 若未指定恢复源，内容从 index 恢复；若给出 --staged，则从 HEAD 恢复
66: - 使用 "A...B" 作为 merge base 快捷写法时，必须恰有一个 merge base，且 A 与 B 至多省略一个，省略者默认为 HEAD
67: 
68: ## Cautions
69: 
70: - 本技能聚焦于通过 -s/--source 指定恢复源，区别于默认源恢复和交互式恢复
71: - 不处理 --patch 交互式 hunk 选择
72: 
73: ## Output Contract
74: 
75: - 工作区文件内容与指定 tree 一致
76: 
77: ## Triggers
78: 
79: - 需要将工作区文件回退到某个 commit/branch/tag 的内容
80: - 用户明确指定了恢复源 tree

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\从指定源恢复工作区路径\SKILL.md

1: ---
2: id: "99f59c6f-5528-5ce9-9d2b-69222702e8d1"
3: name: "从指定源恢复工作区路径"
4: description: "使用 git restore 将工作区中指定路径的内容恢复为恢复源（默认索引）中的版本；若路径被跟踪但在恢复源中不存在，则删除该路径以匹配源。适用于需要将工作区部分路径回退到索引或指定提交版本的场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "工作区恢复"
10:   - "版本控制"
11: triggers:
12:   - "需要将工作区中某些路径的内容回退到索引或指定提交的版本"
13:   - "需要让工作区路径与恢复源保持一致（包括删除源中不存在的已跟踪文件）"
14: examples:
15:   - input: "需要将工作区中某路径内容回退到索引版本"
16:     output: "执行 git restore <path>，工作区该路径内容与索引一致"
17:     notes: "默认从索引恢复"
18:   - input: "需要将工作区某路径内容回退到指定提交版本"
19:     output: "执行 git restore --source <commit> <path>，工作区该路径内容与指定提交一致"
20:     notes: "使用 --source 指定恢复源"
21: ---
22: 
23: # 从指定源恢复工作区路径
24: 
25: 使用 git restore 将工作区中指定路径的内容恢复为恢复源（默认索引）中的版本；若路径被跟踪但在恢复源中不存在，则删除该路径以匹配源。适用于需要将工作区部分路径回退到索引或指定提交版本的场景。
26: 
27: ## Prompt
28: 
29: 执行 git restore 恢复工作区指定路径：
30: 1. 确认恢复目标为工作区路径（非仅索引）。
31: 2. 确认恢复源：默认从索引恢复；如需从其他提交恢复，使用 --source 指定。
32: 3. 对指定路径执行 git restore <path>。
33: 4. 若某路径被跟踪但在恢复源中不存在，该路径会被删除以匹配源，执行前需确认此行为符合预期。
34: 5. 完成后核对工作区指定路径内容与恢复源一致。
35: 
36: ## Objective
37: 
38: 将工作区指定路径的内容恢复为恢复源版本，并删除源中不存在的已跟踪路径。
39: ## Applicable Signals
40: 
41: - 工作区路径内容需要回退到索引版本
42: - 工作区路径内容需要回退到指定提交版本
43: - 需要让工作区路径与恢复源保持一致
44: 
45: ## Contraindications
46: 
47: - 需要同时恢复索引与工作区时应改用 --staged --worktree 组合
48: - 需要恢复未跟踪文件或清理未跟踪内容时不应使用本技能
49: 
50: ## Intervention Moves
51: 
52: - 确认恢复目标为工作区路径
53: - 确认恢复源（默认索引，可用 --source 指定其他提交）
54: - 对指定路径执行 git restore
55: - 核对恢复结果与恢复源一致
56: 
57: ## Workflow Steps
58: 
59: - 确认恢复目标为工作区路径
60: - 确认恢复源：默认从索引恢复，如需从其他提交恢复则使用 --source 指定
61: - 对指定路径执行 git restore <path>
62: - 注意：被跟踪但在恢复源中不存在的路径会被删除以匹配源
63: - 核对工作区指定路径内容与恢复源一致
64: 
65: ## Constraints
66: 
67: - 默认从索引恢复，除非使用 --source 指定其他提交
68: - 仅作用于指定路径，不涉及未跟踪文件清理
69: 
70: ## Cautions
71: 
72: - 若路径被跟踪但在恢复源中不存在，该路径会被删除以匹配源，执行前需确认此行为符合预期
73: 
74: ## Output Contract
75: 
76: - 工作区指定路径内容与恢复源一致，源中不存在的已跟踪路径被移除。
77: 
78: ## Example Therapist Responses
79: 
80: ### Example 1
81: 
82: - Client/Input: 需要将工作区中某路径内容回退到索引版本
83: - Therapist/Output: 执行 git restore <path>，工作区该路径内容与索引一致
84: - Notes: 默认从索引恢复
85: 
86: ### Example 2
87: 
88: - Client/Input: 需要将工作区某路径内容回退到指定提交版本
89: - Therapist/Output: 执行 git restore --source <commit> <path>，工作区该路径内容与指定提交一致
90: - Notes: 使用 --source 指定恢复源
91: 
92: ## Triggers
93: 
94: - 需要将工作区中某些路径的内容回退到索引或指定提交的版本
95: - 需要让工作区路径与恢复源保持一致（包括删除源中不存在的已跟踪文件）
96: 
97: ## Examples
98: 
99: ### Example 1
100: 
101: Input:
102: 
103:   需要将工作区中某路径内容回退到索引版本
104: 
105: Output:
106: 
107:   执行 git restore <path>，工作区该路径内容与索引一致
108: 
109: Notes:
110: 
111:   默认从索引恢复
112: 
113: ### Example 2
114: 
115: Input:
116: 
117:   需要将工作区某路径内容回退到指定提交版本
118: 
119: Output:
120: 
121:   执行 git restore --source <commit> <path>，工作区该路径内容与指定提交一致
122: 
123: Notes:
124: 
125:   使用 --source 指定恢复源

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\合并基快捷语法解析\SKILL.md

1: ---
2: id: "7147c9f5-6f4f-59d7-8f71-203e58032ac1"
3: name: "合并基快捷语法解析"
4: description: "解析 git restore 中 \"A...B\" 三点语法，将其解释为 A 与 B 的合并基（merge base），用于确定恢复源。当且仅当存在唯一合并基时有效，且可省略 A 或 B 之一（省略者默认 HEAD）。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "git-restore"
9:   - "merge-base"
10:   - "revision-syntax"
11:   - "恢复源解析"
12: triggers:
13:   - "用户使用 A...B 三点语法指定恢复源"
14:   - "需要基于两个分支的合并基恢复文件"
15: examples:
16:   - input: "git restore --source=A...B file.txt"
17:     output: "恢复源解析为 A 与 B 的合并基 commit"
18:     notes: "要求 A 与 B 之间存在唯一合并基"
19:   - input: "git restore --source=A... file.txt"
20:     output: "恢复源解析为 A 与 HEAD 的合并基 commit"
21:     notes: "省略 B 时默认 HEAD"
22: ---
23: 
24: # 合并基快捷语法解析
25: 
26: 解析 git restore 中 "A...B" 三点语法，将其解释为 A 与 B 的合并基（merge base），用于确定恢复源。当且仅当存在唯一合并基时有效，且可省略 A 或 B 之一（省略者默认 HEAD）。
27: 
28: ## Prompt
29: 
30: 当恢复源以 "A...B" 三点语法给出时，按以下规则解析：
31: 1. 确认存在唯一合并基；若存在多个合并基，该语法无效，应报错或要求用户改用显式 commit。
32: 2. 将 "A...B" 解释为 A 与 B 的合并基 commit，作为恢复源。
33: 3. 允许省略 A 或 B 之一，省略的一侧默认取 HEAD。
34: 4. 解析出合并基 commit 后，将其作为恢复源交给后续恢复流程使用。
35: 
36: ## Objective
37: 
38: 解析 A...B 合并基快捷语法以确定恢复源
39: ## Applicable Signals
40: 
41: - 恢复源参数中出现三点语法 "A...B"
42: - 用户希望以两个分支的合并基作为恢复内容来源
43: 
44: ## Contraindications
45: 
46: - 不存在唯一合并基（存在多个合并基）
47: - 用户未使用三点语法
48: 
49: ## Intervention Moves
50: 
51: - 识别三点语法并确认唯一合并基
52: - 将 "A...B" 解析为合并基 commit
53: - 对省略的一侧默认使用 HEAD
54: - 将解析结果作为恢复源传递
55: 
56: ## Workflow Steps
57: 
58: - 检测恢复源是否使用 "A...B" 三点语法
59: - 验证 A 与 B 之间是否存在唯一合并基
60: - 若唯一，解析为合并基 commit；若省略 A 或 B，则默认 HEAD
61: - 将合并基 commit 作为恢复源输出给恢复流程
62: 
63: ## Constraints
64: 
65: - 仅当存在唯一合并基时该语法有效
66: - 最多只能省略 A 和 B 中的一个，省略者默认 HEAD
67: 
68: ## Cautions
69: 
70: - 存在多个合并基时三点语法无效，需改用显式 commit 指定恢复源
71: 
72: ## Output Contract
73: 
74: - 确定合并基 commit 作为恢复源
75: 
76: ## Example Therapist Responses
77: 
78: ### Example 1
79: 
80: - Client/Input: git restore --source=A...B file.txt
81: - Therapist/Output: 恢复源解析为 A 与 B 的合并基 commit
82: - Notes: 要求 A 与 B 之间存在唯一合并基
83: 
84: ### Example 2
85: 
86: - Client/Input: git restore --source=A... file.txt
87: - Therapist/Output: 恢复源解析为 A 与 HEAD 的合并基 commit
88: - Notes: 省略 B 时默认 HEAD
89: 
90: ## Triggers
91: 
92: - 用户使用 A...B 三点语法指定恢复源
93: - 需要基于两个分支的合并基恢复文件
94: 
95: ## Examples
96: 
97: ### Example 1
98: 
99: Input:
100: 
101:   git restore --source=A...B file.txt
102: 
103: Output:
104: 
105:   恢复源解析为 A 与 B 的合并基 commit
106: 
107: Notes:
108: 
109:   要求 A 与 B 之间存在唯一合并基
110: 
111: ### Example 2
112: 
113: Input:
114: 
115:   git restore --source=A... file.txt
116: 
117: Output:
118: 
119:   恢复源解析为 A 与 HEAD 的合并基 commit
120: 
121: Notes:
122: 
123:   省略 B 时默认 HEAD

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\同时恢复工作区与索引\SKILL.md

1: ---
2: id: "c0045ec2-f265-563d-a6ca-764403b3cef9"
3: name: "同时恢复工作区与索引"
4: description: "使用 git restore --staged --worktree 同时将工作区和索引中指定路径的内容恢复为恢复源版本，用于一次性撤销暂存与工作区修改。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "staged"
10:   - "worktree"
11:   - "版本控制恢复"
12: triggers:
13:   - "需要一次性将工作区和索引中某些路径回退到同一恢复源"
14:   - "需要同时撤销暂存和工作区修改"
15: examples:
16:   - input: "需要同时撤销某路径的暂存与工作区修改"
17:     output: "执行 git restore --staged --worktree <path>，工作区与索引均回退到 HEAD 版本"
18: ---
19: 
20: # 同时恢复工作区与索引
21: 
22: 使用 git restore --staged --worktree 同时将工作区和索引中指定路径的内容恢复为恢复源版本，用于一次性撤销暂存与工作区修改。
23: 
24: ## Prompt
25: 
26: 当需要一次性将工作区和索引中某些路径回退到同一恢复源时，执行 git restore --staged --worktree <path>。默认从 HEAD 恢复（因指定了 --staged），如需从其他提交恢复，追加 --source <commit>。执行后确认工作区与索引中指定路径的内容均与恢复源一致。
27: 
28: ## Objective
29: 
30: 同时将工作区和索引中指定路径的内容恢复为恢复源版本。
31: ## Applicable Signals
32: 
33: - 工作区与索引均需回退到同一恢复源
34: - 需要同时撤销暂存和工作区修改
35: 
36: ## Contraindications
37: 
38: - 只需恢复工作区或只需恢复索引时不应使用本技能
39: - 需要保留工作区修改而仅调整索引时不应使用本技能
40: 
41: ## Intervention Moves
42: 
43: - 执行 git restore --staged --worktree <path>
44: - 如需从非 HEAD 恢复，追加 --source <commit>
45: - 核对工作区与索引内容是否与恢复源一致
46: 
47: ## Workflow Steps
48: 
49: - 确认需要同时恢复工作区和索引的路径
50: - 执行 git restore --staged --worktree <path>
51: - 如需从其他提交恢复，追加 --source <commit>
52: - 验证工作区与索引中指定路径的内容均与恢复源一致
53: 
54: ## Constraints
55: 
56: - 作用范围同时覆盖工作区和索引
57: - 默认从 HEAD 恢复，除非使用 --source 指定其他提交
58: 
59: ## Cautions
60: 
61: - 若路径在恢复源中不存在但被跟踪，将被移除以匹配恢复源
62: 
63: ## Output Contract
64: 
65: - 工作区和索引中指定路径的内容均与恢复源一致。
66: 
67: ## Example Therapist Responses
68: 
69: ### Example 1
70: 
71: - Client/Input: 需要同时撤销某路径的暂存与工作区修改
72: - Therapist/Output: 执行 git restore --staged --worktree <path>，工作区与索引均回退到 HEAD 版本
73: 
74: ## Triggers
75: 
76: - 需要一次性将工作区和索引中某些路径回退到同一恢复源
77: - 需要同时撤销暂存和工作区修改
78: 
79: ## Examples
80: 
81: ### Example 1
82: 
83: Input:
84: 
85:   需要同时撤销某路径的暂存与工作区修改
86: 
87: Output:
88: 
89:   执行 git restore --staged --worktree <path>，工作区与索引均回退到 HEAD 版本

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\强制启用-git-restore-进度报告\SKILL.md

1: ---
2: id: "44058e52-2d84-5119-a5fe-e2d4811e07a7"
3: name: "强制启用 git restore 进度报告"
4: description: "在执行 git restore 时通过 --progress 选项强制在标准错误流上报告进度，即使输出未连接到终端或已指定 --quiet；如需禁用则使用 --no-progress。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "git-restore"
9:   - "进度报告"
10:   - "输出控制"
11: triggers:
12:   - "需要监控恢复进度"
13:   - "输出未连接到终端但需要进度信息"
14: examples:
15:   - input: "git restore --progress <path>"
16:     output: "标准错误流上输出进度信息"
17:     notes: "即使输出未连接到终端或指定了 --quiet，仍强制报告进度"
18: ---
19: 
20: # 强制启用 git restore 进度报告
21: 
22: 在执行 git restore 时通过 --progress 选项强制在标准错误流上报告进度，即使输出未连接到终端或已指定 --quiet；如需禁用则使用 --no-progress。
23: 
24: ## Prompt
25: 
26: 在执行 git restore 时，若需要监控恢复进度，添加 --progress 选项以强制在标准错误流上输出进度信息，即使输出未连接到终端或已指定 --quiet。若需明确禁用进度输出，使用 --no-progress。
27: 
28: ## Objective
29: 
30: 强制启用进度报告输出
31: ## Applicable Signals
32: 
33: - 需要监控恢复进度
34: - 输出未连接到终端但需要进度信息
35: 
36: ## Contraindications
37: 
38: - 不需要进度输出
39: - 使用 --no-progress 明确禁用
40: 
41: ## Intervention Moves
42: 
43: - 在 git restore 命令中添加 --progress 选项
44: - 如需禁用进度输出则使用 --no-progress
45: 
46: ## Workflow Steps
47: 
48: - 确认需要监控恢复进度
49: - 在 git restore 命令中添加 --progress 选项
50: - 观察标准错误流上的进度信息
51: 
52: ## Constraints
53: 
54: - --progress 强制在标准错误流上报告进度，即使未连接到终端或指定了 --quiet
55: 
56: ## Cautions
57: 
58: - 进度信息输出到标准错误流，而非标准输出
59: 
60: ## Output Contract
61: 
62: - 标准错误流上输出进度信息
63: 
64: ## Example Therapist Responses
65: 
66: ### Example 1
67: 
68: - Client/Input: git restore --progress <path>
69: - Therapist/Output: 标准错误流上输出进度信息
70: - Notes: 即使输出未连接到终端或指定了 --quiet，仍强制报告进度
71: 
72: ## Triggers
73: 
74: - 需要监控恢复进度
75: - 输出未连接到终端但需要进度信息
76: 
77: ## Examples
78: 
79: ### Example 1
80: 
81: Input:
82: 
83:   git restore --progress <path>
84: 
85: Output:
86: 
87:   标准错误流上输出进度信息
88: 
89: Notes:
90: 
91:   即使输出未连接到终端或指定了 --quiet，仍强制报告进度

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\恢复时重建冲突合并标记\SKILL.md

1: ---
2: id: "a2921234-8368-5718-a917-fb40db95ccd1"
3: name: "恢复时重建冲突合并标记"
4: description: "使用 git restore -m/--merge 从索引恢复工作区文件时，在未合并路径上重建冲突合并标记，用于需要重新生成冲突标记以便手动解决的场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "git-restore"
9:   - "冲突解决"
10:   - "merge"
11: triggers:
12:   - "需要重新生成冲突标记"
13:   - "未合并路径的冲突标记被误删或需要重置"
14: examples:
15:   - input: "git restore -m <path>"
16:     output: "未合并路径中重新出现冲突合并标记"
17:     notes: "从索引恢复工作区文件并重建冲突状态"
18: ---
19: 
20: # 恢复时重建冲突合并标记
21: 
22: 使用 git restore -m/--merge 从索引恢复工作区文件时，在未合并路径上重建冲突合并标记，用于需要重新生成冲突标记以便手动解决的场景。
23: 
24: ## Prompt
25: 
26: 当需要从索引恢复工作区文件并重新生成未合并路径的冲突标记时，执行 git restore -m（或 --merge）。该操作在未合并路径上重建冲突合并状态，而非选择某一方。注意：不能与 --source 同时使用。
27: 
28: ## Objective
29: 
30: 在未合并路径上重建冲突合并标记
31: ## Applicable Signals
32: 
33: - 工作区未合并路径的冲突标记丢失或需要重置
34: - 需要从索引恢复文件并保留冲突状态
35: 
36: ## Contraindications
37: 
38: - 使用 --source 从 tree-ish 检出路径时
39: - 路径没有冲突
40: 
41: ## Intervention Moves
42: 
43: - 执行 git restore -m 或 git restore --merge 从索引恢复工作区文件
44: - 在未合并路径上重建冲突合并标记
45: 
46: ## Workflow Steps
47: 
48: - 确认目标路径处于未合并状态
49: - 确认未使用 --source 选项
50: - 执行 git restore -m（或 --merge）恢复文件并重建冲突标记
51: - 检查未合并路径中冲突合并标记是否重新出现
52: 
53: ## Constraints
54: 
55: - 该选项不能与 --source 同时使用
56: - 仅在从索引恢复工作区文件时有效
57: 
58: ## Cautions
59: 
60: - 在 git rebase 和 git pull --rebase 期间，ours 和 theirs 可能互换，需参考 git-checkout 中相同选项的说明
61: 
62: ## Output Contract
63: 
64: - 未合并路径中重新出现冲突合并标记
65: 
66: ## Example Therapist Responses
67: 
68: ### Example 1
69: 
70: - Client/Input: git restore -m <path>
71: - Therapist/Output: 未合并路径中重新出现冲突合并标记
72: - Notes: 从索引恢复工作区文件并重建冲突状态
73: 
74: ## Triggers
75: 
76: - 需要重新生成冲突标记
77: - 未合并路径的冲突标记被误删或需要重置
78: 
79: ## Examples
80: 
81: ### Example 1
82: 
83: Input:
84: 
85:   git restore -m <path>
86: 
87: Output:
88: 
89:   未合并路径中重新出现冲突合并标记
90: 
91: Notes:
92: 
93:   从索引恢复工作区文件并重建冲突状态

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\恢复暂存区文件至-head-版本\SKILL.md

1: ---
2: id: "feccf35d-9c79-5b75-90e3-6707ce898884"
3: name: "恢复暂存区文件至 HEAD 版本"
4: description: "使用 git restore --staged <file> 将索引中的指定文件恢复到 HEAD 版本，等价于 git reset。适用于需要取消暂存但保留工作区改动的场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "staged"
10:   - "index"
11:   - "unstage"
12: triggers:
13:   - "用户希望取消已暂存的改动但保留工作区文件"
14:   - "需要将索引恢复到 HEAD 状态"
15: examples:
16:   - input: "git restore --staged hello.c"
17:     output: "索引中的 hello.c 恢复到 HEAD 版本，工作区 hello.c 保持不变"
18:     notes: "等价于 git reset"
19: ---
20: 
21: # 恢复暂存区文件至 HEAD 版本
22: 
23: 使用 git restore --staged <file> 将索引中的指定文件恢复到 HEAD 版本，等价于 git reset。适用于需要取消暂存但保留工作区改动的场景。
24: 
25: ## Prompt
26: 
27: 当需要取消已暂存的改动但保留工作区文件内容时，执行 git restore --staged <file>，将索引中目标文件回退到 HEAD 版本。该操作仅作用于索引层，不修改工作区文件。
28: 
29: ## Objective
30: 
31: 将索引中指定文件回退到 HEAD 版本，同时保留工作区内容不变
32: ## Applicable Signals
33: 
34: - 用户希望取消已暂存的改动但保留工作区文件
35: - 需要将索引恢复到 HEAD 状态
36: 
37: ## Contraindications
38: 
39: - 需要同时丢弃工作区改动
40: - 需要恢复到非 HEAD 的特定提交
41: 
42: ## Intervention Moves
43: 
44: - 执行 git restore --staged <file> 将索引中目标文件恢复到 HEAD 版本
45: 
46: ## Workflow Steps
47: 
48: - 确认目标文件已暂存且需要取消暂存
49: - 执行 git restore --staged <file>
50: - 验证索引中目标文件与 HEAD 版本一致且工作区文件未改动
51: 
52: ## Constraints
53: 
54: - 仅操作索引层，不触及工作区
55: - 默认恢复到 HEAD 版本
56: 
57: ## Cautions
58: 
59: - 该操作等价于 git reset，不会丢弃工作区改动
60: 
61: ## Output Contract
62: 
63: - 索引中目标文件与 HEAD 版本一致，工作区文件未改动
64: 
65: ## Example Therapist Responses
66: 
67: ### Example 1
68: 
69: - Client/Input: git restore --staged hello.c
70: - Therapist/Output: 索引中的 hello.c 恢复到 HEAD 版本，工作区 hello.c 保持不变
71: - Notes: 等价于 git reset
72: 
73: ## Triggers
74: 
75: - 用户希望取消已暂存的改动但保留工作区文件
76: - 需要将索引恢复到 HEAD 状态
77: 
78: ## Examples
79: 
80: ### Example 1
81: 
82: Input:
83: 
84:   git restore --staged hello.c
85: 
86: Output:
87: 
88:   索引中的 hello.c 恢复到 HEAD 版本，工作区 hello.c 保持不变
89: 
90: Notes:
91: 
92:   等价于 git reset

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\恢复未合并路径时选择-ours-theirs-阶段\SKILL.md

1: ---
2: id: "918e0187-7a71-5a49-9ff9-5352d0eb6e89"
3: name: "恢复未合并路径时选择 ours/theirs 阶段"
4: description: "在使用 git restore 从索引恢复工作区文件时，针对未合并路径选择 stage #2 (ours) 或 #3 (theirs) 版本，用于从冲突中取某一方版本。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "git-restore"
9:   - "冲突解决"
10:   - "未合并路径"
11:   - "ours"
12:   - "theirs"
13: triggers:
14:   - "工作区存在未合并路径需要恢复"
15:   - "需要从索引中取 ours 或 theirs 版本"
16:   - "冲突解决时需要选择某一方版本"
17: examples:
18:   - input: "工作区存在未合并路径 file.txt，需要取 ours 版本"
19:     output: "执行 git restore --ours file.txt，file.txt 内容替换为 stage #2 版本"
20:     notes: "确认未使用 --source 选项"
21:   - input: "工作区存在未合并路径 file.txt，需要取 theirs 版本"
22:     output: "执行 git restore --theirs file.txt，file.txt 内容替换为 stage #3 版本"
23:     notes: "在 rebase 期间需注意 ours/theirs 可能互换"
24: ---
25: 
26: # 恢复未合并路径时选择 ours/theirs 阶段
27: 
28: 在使用 git restore 从索引恢复工作区文件时，针对未合并路径选择 stage #2 (ours) 或 #3 (theirs) 版本，用于从冲突中取某一方版本。
29: 
30: ## Prompt
31: 
32: 当工作区存在未合并路径且需要从索引恢复某一方版本时，使用 git restore 的 --ours 或 --theirs 选项。
33: 
34: 执行步骤：
35: 1. 确认目标路径处于未合并状态（存在冲突标记）。
36: 2. 确认当前操作不是从 tree-ish 检出（即未使用 --source 选项）。
37: 3. 选择阶段：--ours 对应 stage #2，--theirs 对应 stage #3。
38: 4. 执行 git restore --ours <path> 或 git restore --theirs <path>，将工作区文件替换为指定阶段内容。
39: 
40: 注意：在 git rebase 和 git pull --rebase 期间，ours 与 theirs 的含义可能互换，需参考 git-checkout 中相同选项的说明。
41: 
42: ## Objective
43: 
44: 在未合并路径上按指定阶段（ours 或 theirs）恢复文件内容
45: ## Applicable Signals
46: 
47: - 工作区存在未合并路径
48: - 需要从索引中取 ours 或 theirs 版本
49: - 路径带有冲突标记
50: 
51: ## Contraindications
52: 
53: - 使用 --source 从 tree-ish 检出路径时
54: - 路径没有冲突标记
55: 
56: ## Intervention Moves
57: 
58: - 确认路径处于未合并状态
59: - 确认未使用 --source 选项
60: - 选择 --ours (stage #2) 或 --theirs (stage #3)
61: - 执行 git restore 并验证文件内容
62: 
63: ## Workflow Steps
64: 
65: - 确认目标路径处于未合并状态
66: - 确认当前操作不是从 tree-ish 检出（未使用 --source）
67: - 选择阶段：--ours 对应 stage #2，--theirs 对应 stage #3
68: - 执行 git restore --ours <path> 或 git restore --theirs <path>
69: - 验证工作区文件已替换为指定阶段内容
70: 
71: ## Constraints
72: 
73: - --ours 和 --theirs 仅在从索引恢复工作区文件时可用
74: - 不能与 --source 选项同时使用
75: 
76: ## Cautions
77: 
78: - 在 git rebase 和 git pull --rebase 期间，ours 与 theirs 的含义可能互换，需参考 git-checkout 中相同选项的说明
79: 
80: ## Output Contract
81: 
82: - 未合并路径被替换为指定阶段（ours 或 theirs）的文件内容
83: 
84: ## Example Therapist Responses
85: 
86: ### Example 1
87: 
88: - Client/Input: 工作区存在未合并路径 file.txt，需要取 ours 版本
89: - Therapist/Output: 执行 git restore --ours file.txt，file.txt 内容替换为 stage #2 版本
90: - Notes: 确认未使用 --source 选项
91: 
92: ### Example 2
93: 
94: - Client/Input: 工作区存在未合并路径 file.txt，需要取 theirs 版本
95: - Therapist/Output: 执行 git restore --theirs file.txt，file.txt 内容替换为 stage #3 版本
96: - Notes: 在 rebase 期间需注意 ours/theirs 可能互换
97: 
98: ## Triggers
99: 
100: - 工作区存在未合并路径需要恢复
101: - 需要从索引中取 ours 或 theirs 版本
102: - 冲突解决时需要选择某一方版本
103: 
104: ## Examples
105: 
106: ### Example 1
107: 
108: Input:
109: 
110:   工作区存在未合并路径 file.txt，需要取 ours 版本
111: 
112: Output:
113: 
114:   执行 git restore --ours file.txt，file.txt 内容替换为 stage #2 版本
115: 
116: Notes:
117: 
118:   确认未使用 --source 选项
119: 
120: ### Example 2
121: 
122: Input:
123: 
124:   工作区存在未合并路径 file.txt，需要取 theirs 版本
125: 
126: Output:
127: 
128:   执行 git restore --theirs file.txt，file.txt 内容替换为 stage #3 版本
129: 
130: Notes:
131: 
132:   在 rebase 期间需注意 ours/theirs 可能互换

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\恢复索引内容\SKILL.md

1: ---
2: id: "ea0c6b32-c72a-5688-a8c1-26f398a892fc"
3: name: "恢复索引内容"
4: description: "使用 git restore --staged 将索引中指定路径的内容恢复为 HEAD 版本（默认），或通过 --source 指定其他提交作为恢复源。适用于需要取消暂存或回退索引中某些路径内容的场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "staged"
10:   - "index"
11:   - "版本控制"
12: triggers:
13:   - "需要取消暂存或回退索引中某些路径的内容"
14:   - "需要将索引内容与 HEAD 或指定提交对齐"
15: examples:
16:   - input: "git restore --staged file.txt"
17:     output: "索引中 file.txt 的内容恢复为 HEAD 版本"
18:     notes: "默认从 HEAD 恢复"
19:   - input: "git restore --staged --source abc123 file.txt"
20:     output: "索引中 file.txt 的内容恢复为提交 abc123 的版本"
21:     notes: "通过 --source 指定恢复源"
22: ---
23: 
24: # 恢复索引内容
25: 
26: 使用 git restore --staged 将索引中指定路径的内容恢复为 HEAD 版本（默认），或通过 --source 指定其他提交作为恢复源。适用于需要取消暂存或回退索引中某些路径内容的场景。
27: 
28: ## Prompt
29: 
30: 当需要将索引中指定路径的内容恢复为 HEAD 或指定提交版本时，执行 git restore --staged <path>。默认恢复源为 HEAD；如需从其他提交恢复，使用 --source <commit>。若同时需要修改工作区内容，应配合 --worktree 使用。
31: 
32: ## Objective
33: 
34: 将索引中指定路径的内容恢复为 HEAD 或指定提交的版本。
35: ## Applicable Signals
36: 
37: - 索引中某些路径的内容需要回退到 HEAD 版本
38: - 索引中某些路径的内容需要与指定提交对齐
39: - 需要取消暂存操作
40: 
41: ## Contraindications
42: 
43: - 需要同时修改工作区内容时应配合 --worktree 使用
44: - 仅需恢复工作区而不动索引时不应使用本技能
45: 
46: ## Intervention Moves
47: 
48: - 执行 git restore --staged <path> 将索引中指定路径恢复为 HEAD 版本
49: - 如需从其他提交恢复，添加 --source <commit> 参数
50: - 如需同时恢复工作区，添加 --worktree 参数
51: 
52: ## Workflow Steps
53: 
54: - 确认需要恢复的路径及目标恢复源（HEAD 或指定提交）
55: - 执行 git restore --staged <path>，默认从 HEAD 恢复
56: - 如需从其他提交恢复，添加 --source <commit>
57: - 如需同时恢复工作区，添加 --worktree
58: - 验证索引中指定路径的内容与目标恢复源一致
59: 
60: ## Constraints
61: 
62: - 默认恢复源为 HEAD
63: - 仅作用于索引，不修改工作区（除非配合 --worktree）
64: 
65: ## Cautions
66: 
67: - 若路径在恢复源中不存在但被跟踪，该路径将被移除以匹配恢复源
68: 
69: ## Output Contract
70: 
71: - 索引中指定路径的内容与 HEAD 或 --source 指定的提交一致。
72: 
73: ## Example Therapist Responses
74: 
75: ### Example 1
76: 
77: - Client/Input: git restore --staged file.txt
78: - Therapist/Output: 索引中 file.txt 的内容恢复为 HEAD 版本
79: - Notes: 默认从 HEAD 恢复
80: 
81: ### Example 2
82: 
83: - Client/Input: git restore --staged --source abc123 file.txt
84: - Therapist/Output: 索引中 file.txt 的内容恢复为提交 abc123 的版本
85: - Notes: 通过 --source 指定恢复源
86: 
87: ## Triggers
88: 
89: - 需要取消暂存或回退索引中某些路径的内容
90: - 需要将索引内容与 HEAD 或指定提交对齐
91: 
92: ## Examples
93: 
94: ### Example 1
95: 
96: Input:
97: 
98:   git restore --staged file.txt
99: 
100: Output:
101: 
102:   索引中 file.txt 的内容恢复为 HEAD 版本
103: 
104: Notes:
105: 
106:   默认从 HEAD 恢复
107: 
108: ### Example 2
109: 
110: Input:
111: 
112:   git restore --staged --source abc123 file.txt
113: 
114: Output:
115: 
116:   索引中 file.txt 的内容恢复为提交 abc123 的版本
117: 
118: Notes:
119: 
120:   通过 --source 指定恢复源

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\指定-git-restore-恢复位置\SKILL.md

1: ---
2: id: "fd6ef816-81a2-5586-afb6-35aa6f45c10c"
3: name: "指定 git restore 恢复位置"
4: description: "在执行 git restore 前明确恢复目标位置：默认恢复工作树，可用 --staged 仅恢复索引，或同时指定 --worktree 与 --staged 恢复两者；可选 -q/--quiet 抑制反馈信息。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "worktree"
10:   - "staged"
11:   - "恢复位置"
12: triggers:
13:   - "需要明确恢复目标是工作树还是暂存区"
14:   - "需要同时恢复工作树和索引"
15:   - "需要仅恢复索引"
16: examples:
17:   - input: "git restore --staged file.txt"
18:     output: "仅恢复索引中的 file.txt"
19:     notes: "仅恢复暂存区"
20:   - input: "git restore --worktree --staged file.txt"
21:     output: "同时恢复工作树和索引中的 file.txt"
22:     notes: "恢复两者"
23: ---
24: 
25: # 指定 git restore 恢复位置
26: 
27: 在执行 git restore 前明确恢复目标位置：默认恢复工作树，可用 --staged 仅恢复索引，或同时指定 --worktree 与 --staged 恢复两者；可选 -q/--quiet 抑制反馈信息。
28: 
29: ## Prompt
30: 
31: 在执行 git restore 前，先判断恢复目标：
32: 1. 若未指定 --worktree 或 --staged，默认仅恢复工作树。
33: 2. 若只需恢复索引（暂存区），使用 --staged。
34: 3. 若需同时恢复工作树和索引，同时指定 --worktree 与 --staged。
35: 4. 若需要安静输出、抑制反馈信息，可加 -q/--quiet（隐含 --no-progress）。
36: 确认恢复位置后再执行恢复命令。
37: 
38: ## Objective
39: 
40: 选择恢复操作作用于工作树、索引或两者
41: ## Applicable Signals
42: 
43: - 调用 git restore 但未明确恢复位置
44: - 需要区分工作树与索引的恢复范围
45: - 需要同时恢复工作树和索引
46: 
47: ## Contraindications
48: 
49: - 未明确恢复目标且默认工作树即可时无需显式指定
50: 
51: ## Intervention Moves
52: 
53: - 未指定位置时默认恢复工作树
54: - 使用 --staged 仅恢复索引
55: - 同时指定 --worktree 与 --staged 恢复两者
56: - 使用 -q/--quiet 抑制反馈信息
57: 
58: ## Workflow Steps
59: 
60: - 判断恢复目标：工作树、索引或两者
61: - 未指定时默认恢复工作树
62: - 仅恢复索引时使用 --staged
63: - 同时恢复两者时同时指定 --worktree 与 --staged
64: - 如需安静输出可加 -q/--quiet
65: - 确认位置后执行恢复
66: 
67: ## Constraints
68: 
69: - --worktree 与 --staged 用于指定恢复位置
70: - 未指定任一选项时默认恢复工作树
71: - --staged 仅恢复索引
72: - 同时指定两者则恢复工作树和索引
73: 
74: ## Cautions
75: 
76: - --quiet 会抑制反馈信息并隐含 --no-progress
77: 
78: ## Output Contract
79: 
80: - 按指定位置（工作树、索引或两者）完成恢复
81: 
82: ## Example Therapist Responses
83: 
84: ### Example 1
85: 
86: - Client/Input: git restore --staged file.txt
87: - Therapist/Output: 仅恢复索引中的 file.txt
88: - Notes: 仅恢复暂存区
89: 
90: ### Example 2
91: 
92: - Client/Input: git restore --worktree --staged file.txt
93: - Therapist/Output: 同时恢复工作树和索引中的 file.txt
94: - Notes: 恢复两者
95: 
96: ## Triggers
97: 
98: - 需要明确恢复目标是工作树还是暂存区
99: - 需要同时恢复工作树和索引
100: - 需要仅恢复索引
101: 
102: ## Examples
103: 
104: ### Example 1
105: 
106: Input:
107: 
108:   git restore --staged file.txt
109: 
110: Output:
111: 
112:   仅恢复索引中的 file.txt
113: 
114: Notes:
115: 
116:   仅恢复暂存区
117: 
118: ### Example 2
119: 
120: Input:
121: 
122:   git restore --worktree --staged file.txt
123: 
124: Output:
125: 
126:   同时恢复工作树和索引中的 file.txt
127: 
128: Notes:
129: 
130:   恢复两者

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\指定恢复源提交\SKILL.md

1: ---
2: id: "68365646-cd43-5640-9a09-7e236fcf0774"
3: name: "指定恢复源提交"
4: description: "使用 git restore --source 从指定提交而非默认源恢复路径内容，用于需要从特定历史版本恢复路径的场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "source"
10:   - "版本控制恢复"
11: triggers:
12:   - "需要从 HEAD 或索引以外的特定提交恢复路径内容"
13:   - "需要将路径内容回退到某个历史版本"
14: examples:
15:   - input: "需要将某路径内容回退到特定历史提交版本"
16:     output: "执行 git restore --source <commit> <path>，路径内容与指定提交版本一致"
17: ---
18: 
19: # 指定恢复源提交
20: 
21: 使用 git restore --source 从指定提交而非默认源恢复路径内容，用于需要从特定历史版本恢复路径的场景。
22: 
23: ## Prompt
24: 
25: 当需要从 HEAD 或索引以外的特定提交恢复路径内容时，使用 git restore --source <commit> 指定恢复源。执行前确认目标提交已明确，执行后验证指定路径内容与 --source 指定的提交版本一致。
26: 
27: ## Objective
28: 
29: 从 --source 指定的提交恢复指定路径的内容。
30: ## Applicable Signals
31: 
32: - 需要从 HEAD 或索引以外的特定提交恢复路径内容
33: - 需要将路径内容回退到某个历史版本
34: 
35: ## Contraindications
36: 
37: - 默认从 HEAD 或索引恢复即可满足需求时不应使用本技能
38: - 未明确目标提交时不应使用本技能
39: 
40: ## Intervention Moves
41: 
42: - 使用 git restore --source <commit> 指定恢复源
43: - 确认目标提交已明确
44: - 验证恢复后路径内容与指定提交版本一致
45: 
46: ## Workflow Steps
47: 
48: - 确认需要从特定提交而非默认源恢复路径内容
49: - 确定目标提交
50: - 执行 git restore --source <commit> <path>
51: - 验证指定路径内容与 --source 指定的提交版本一致
52: 
53: ## Constraints
54: 
55: - 必须明确指定目标提交
56: - 仅在默认恢复源不满足需求时使用
57: 
58: ## Cautions
59: 
60: - 未明确目标提交时不应使用本技能
61: 
62: ## Output Contract
63: 
64: - 指定路径的内容与 --source 指定的提交版本一致。
65: 
66: ## Example Therapist Responses
67: 
68: ### Example 1
69: 
70: - Client/Input: 需要将某路径内容回退到特定历史提交版本
71: - Therapist/Output: 执行 git restore --source <commit> <path>，路径内容与指定提交版本一致
72: 
73: ## Triggers
74: 
75: - 需要从 HEAD 或索引以外的特定提交恢复路径内容
76: - 需要将路径内容回退到某个历史版本
77: 
78: ## Examples
79: 
80: ### Example 1
81: 
82: Input:
83: 
84:   需要将某路径内容回退到特定历史提交版本
85: 
86: Output:
87: 
88:   执行 git restore --source <commit> <path>，路径内容与指定提交版本一致

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case004_git_restore\clean\r18307cee4f4c\SkillBank\Users\docskill\静默恢复模式\SKILL.md

1: ---
2: id: "7dca97c1-ee41-5695-a22a-13c36e81bc3d"
3: name: "静默恢复模式"
4: description: "使用 git restore 的 --quiet 选项抑制反馈消息，隐含 --no-progress，适用于脚本或需要安静输出的恢复场景。"
5: version: "0.1.0"
6: tags:
7:   - "git"
8:   - "restore"
9:   - "quiet"
10:   - "输出控制"
11: triggers:
12:   - "需要安静执行恢复操作"
13:   - "在自动化脚本中运行恢复"
14: examples:
15:   - input: "git restore --quiet file.txt"
16:     output: "静默恢复 file.txt，无反馈消息"
17:     notes: "隐含 --no-progress"
18: ---
19: 
20: # 静默恢复模式
21: 
22: 使用 git restore 的 --quiet 选项抑制反馈消息，隐含 --no-progress，适用于脚本或需要安静输出的恢复场景。
23: 
24: ## Prompt
25: 
26: 在执行 git restore 时，若需要安静输出，添加 --quiet（或 -q）选项。该选项会抑制反馈消息并隐含 --no-progress。仅在不需要查看恢复进度或反馈信息时使用。
27: 
28: ## Objective
29: 
30: 在恢复操作中抑制反馈输出
31: ## Applicable Signals
32: 
33: - 需要安静执行恢复操作
34: - 在自动化脚本中运行恢复
35: 
36: ## Contraindications
37: 
38: - 需要查看恢复进度或反馈信息
39: 
40: ## Intervention Moves
41: 
42: - 在 git restore 命令中添加 --quiet 或 -q 选项
43: 
44: ## Workflow Steps
45: 
46: - 确认当前场景不需要恢复反馈或进度信息
47: - 在 git restore 命令中添加 --quiet 或 -q 选项
48: - 执行恢复操作
49: 
50: ## Constraints
51: 
52: - --quiet 隐含 --no-progress
53: 
54: ## Cautions
55: 
56: - 使用 --quiet 后将无法看到恢复进度或反馈消息
57: 
58: ## Output Contract
59: 
60: - 无反馈消息的恢复完成
61: 
62: ## Example Therapist Responses
63: 
64: ### Example 1
65: 
66: - Client/Input: git restore --quiet file.txt
67: - Therapist/Output: 静默恢复 file.txt，无反馈消息
68: - Notes: 隐含 --no-progress
69: 
70: ## Triggers
71: 
72: - 需要安静执行恢复操作
73: - 在自动化脚本中运行恢复
74: 
75: ## Examples
76: 
77: ### Example 1
78: 
79: Input:
80: 
81:   git restore --quiet file.txt
82: 
83: Output:
84: 
85:   静默恢复 file.txt，无反馈消息
86: 
87: Notes:
88: 
89:   隐含 --no-progress

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\glob-过滤与覆盖顺序\SKILL.md

1: ---
2: id: "acf646a2-93f9-50a5-a034-031b4f7252f9"
3: name: "Glob 过滤与覆盖顺序"
4: description: "使用 ripgrep 的 -g 选项传入 glob 模式来精确包含或排除文件，并利用后出现的 glob 覆盖先前 glob 的规则控制最终匹配集合。适用于需要按扩展名或路径模式精细控制搜索文件范围的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "glob"
9:   - "文件过滤"
10:   - "搜索范围"
11: triggers:
12:   - "需要按扩展名或路径模式包含/排除文件"
13:   - "需要利用 glob 覆盖顺序实现先排除后包含"
14:   - "文件类型过滤不足以表达意图时"
15: examples:
16:   - input: "只搜索 *.toml 文件"
17:     output: "rg clap -g '!*.toml' -g '*.toml'"
18:     notes: "后出现的 -g '*.toml' 覆盖先前的排除规则，最终只搜索 toml 文件"
19: ---
20: 
21: # Glob 过滤与覆盖顺序
22: 
23: 使用 ripgrep 的 -g 选项传入 glob 模式来精确包含或排除文件，并利用后出现的 glob 覆盖先前 glob 的规则控制最终匹配集合。适用于需要按扩展名或路径模式精细控制搜索文件范围的场景。
24: 
25: ## Prompt
26: 
27: 当需要按扩展名或路径模式精确控制 ripgrep 搜索的文件集合时，使用 -g 传入 glob 模式。glob 按 .gitignore 语义解释，且后出现的 glob 会覆盖先前的 glob，因此可通过先排除再包含的顺序实现最终集合控制。执行步骤：1) 确定要包含或排除的文件模式；2) 用 -g '<pattern>' 传入 glob，排除模式以 ! 开头；3) 若需覆盖先前规则，将更具体的 glob 放在后面；4) 运行 rg 命令并检查结果文件集合是否符合预期。
28: 
29: ## Objective
30: 
31: 用 glob 模式精确包含或排除文件，并利用覆盖顺序控制最终集合
32: ## Applicable Signals
33: 
34: - 需要按扩展名或路径模式包含/排除文件
35: - 需要利用 glob 覆盖顺序实现先排除后包含
36: 
37: ## Contraindications
38: 
39: - 文件类型过滤已足够表达意图
40: - 需要跨命令持久过滤规则
41: 
42: ## Intervention Moves
43: 
44: - 使用 -g '<pattern>' 传入 glob 模式
45: - 排除模式以 ! 开头，如 -g '!*.toml'
46: - 将更具体的 glob 放在后面以覆盖先前规则
47: - 运行 rg 命令并验证结果文件集合
48: 
49: ## Workflow Steps
50: 
51: - 确定要包含或排除的文件模式
52: - 用 -g '<pattern>' 传入 glob，排除模式以 ! 开头
53: - 若需覆盖先前规则，将更具体的 glob 放在后面
54: - 运行 rg 命令并检查结果文件集合是否符合预期
55: 
56: ## Constraints
57: 
58: - glob 按 .gitignore 语义解释
59: - 后出现的 glob 会覆盖先前的 glob
60: 
61: ## Cautions
62: 
63: - 覆盖顺序容易导致意外结果，需确认最终生效的 glob 集合
64: 
65: ## Output Contract
66: 
67: - 一条使用 -g 的 rg 命令，搜索结果仅包含符合最终 glob 集合的文件
68: 
69: ## Example Therapist Responses
70: 
71: ### Example 1
72: 
73: - Client/Input: 只搜索 *.toml 文件
74: - Therapist/Output: rg clap -g '!*.toml' -g '*.toml'
75: - Notes: 后出现的 -g '*.toml' 覆盖先前的排除规则，最终只搜索 toml 文件
76: 
77: ## Triggers
78: 
79: - 需要按扩展名或路径模式包含/排除文件
80: - 需要利用 glob 覆盖顺序实现先排除后包含
81: - 文件类型过滤不足以表达意图时
82: 
83: ## Examples
84: 
85: ### Example 1
86: 
87: Input:
88: 
89:   只搜索 *.toml 文件
90: 
91: Output:
92: 
93:   rg clap -g '!*.toml' -g '*.toml'
94: 
95: Notes:
96: 
97:   后出现的 -g '*.toml' 覆盖先前的排除规则，最终只搜索 toml 文件

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-二进制文件搜索模式选择\SKILL.md

1: ---
2: id: "20e03fce-9b17-54bb-9332-a5e81eb3289a"
3: name: "ripgrep 二进制文件搜索模式选择"
4: description: "根据搜索目标选择 ripgrep 的二进制处理模式（默认、--binary 或 -a/--text），以控制检测到 NUL 字节后是否继续搜索，并在需要时避免二进制内容污染终端输出。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "binary-detection"
9:   - "search-mode"
10:   - "cli-flag"
11: triggers:
12:   - "需要搜索可能包含二进制数据的文件"
13:   - "希望避免二进制内容污染终端输出"
14:   - "需要确保在二进制文件中不遗漏匹配"
15: examples:
16:   - input: "需要搜索可能包含二进制数据的文件，同时避免二进制内容输出到终端"
17:     output: "使用 --binary 模式"
18:     notes: "继续搜索直到文件末尾或出现匹配，但不将二进制数据输出到终端"
19:   - input: "搜索以文本为主但含 NUL 字节的文件"
20:     output: "使用 -a/--text 模式"
21:     notes: "完全禁用二进制检测，按文本搜索"
22: ---
23: 
24: # ripgrep 二进制文件搜索模式选择
25: 
26: 根据搜索目标选择 ripgrep 的二进制处理模式（默认、--binary 或 -a/--text），以控制检测到 NUL 字节后是否继续搜索，并在需要时避免二进制内容污染终端输出。
27: 
28: ## Prompt
29: 
30: 在配置 ripgrep 搜索前，先判断目标文件是否可能包含二进制数据以及是否需要发现其中的匹配。
31: 
32: 1. 默认模式：递归目录遍历时自动移除二进制文件，一旦检测到二进制即停止搜索；若在检测到 NUL 字节前已打印匹配，会输出搜索提前停止的警告。此模式仅适用于递归目录遍历产生的文件；显式指定文件（如 rg foo binary-file）会自动以二进制模式搜索。
33: 2. 二进制模式（--binary）：检测到 NUL 字节后不总是停止，会继续搜索直到到达文件末尾或出现匹配；若报告无匹配，则文件中确实无匹配。用于发现所有文件中的匹配，同时避免将二进制数据输出到终端。
34: 3. 文本模式（-a/--text）：完全禁用二进制检测，将所有文件按文本搜索。适用于以文本为主但含 NUL 字节的文件，或专门搜索二进制数据。
35: 
36: 根据是否需要发现二进制文件中的匹配、是否要避免终端输出二进制内容、以及文件大小与内存风险，选定模式并给出对应命令行标志。
37: 
38: ## Objective
39: 
40: 为给定搜索任务选择正确的二进制处理模式（默认/--binary/-a/--text）
41: ## Applicable Signals
42: 
43: - 目标文件可能包含二进制数据
44: - 需要控制检测到 NUL 字节后的搜索行为
45: - 需要避免二进制数据被输出到终端
46: 
47: ## Contraindications
48: 
49: - 仅搜索纯文本文件且无需考虑二进制检测
50: - 对超大二进制文件使用文本模式可能导致内存问题
51: 
52: ## Intervention Moves
53: 
54: - 判断是否通过递归目录遍历搜索还是显式指定文件
55: - 默认模式：依赖自动移除二进制文件并在检测到二进制时停止搜索
56: - 二进制模式：使用 --binary 继续搜索直到文件末尾或出现匹配
57: - 文本模式：使用 -a/--text 完全禁用二进制检测
58: 
59: ## Workflow Steps
60: 
61: - 确认搜索目标是否可能包含二进制数据
62: - 确认是否需要发现二进制文件中的匹配
63: - 确认是否必须避免二进制内容输出到终端
64: - 在默认、--binary、-a/--text 中选择模式并应用对应标志
65: 
66: ## Constraints
67: 
68: - 默认模式的自动移除仅适用于递归目录遍历产生的文件
69: - 显式指定文件时会自动以二进制模式搜索
70: - 文本模式在超大二进制文件上可能消耗大量内存
71: 
72: ## Cautions
73: 
74: - 默认模式下若在检测到 NUL 字节前已打印匹配，会输出搜索提前停止的警告
75: - 二进制模式下若报告无匹配，则文件中确实无匹配
76: 
77: ## Output Contract
78: 
79: - 选定模式及对应命令行标志（默认、--binary 或 -a/--text）
80: 
81: ## Example Therapist Responses
82: 
83: ### Example 1
84: 
85: - Client/Input: 需要搜索可能包含二进制数据的文件，同时避免二进制内容输出到终端
86: - Therapist/Output: 使用 --binary 模式
87: - Notes: 继续搜索直到文件末尾或出现匹配，但不将二进制数据输出到终端
88: 
89: ### Example 2
90: 
91: - Client/Input: 搜索以文本为主但含 NUL 字节的文件
92: - Therapist/Output: 使用 -a/--text 模式
93: - Notes: 完全禁用二进制检测，按文本搜索
94: 
95: ## Triggers
96: 
97: - 需要搜索可能包含二进制数据的文件
98: - 希望避免二进制内容污染终端输出
99: - 需要确保在二进制文件中不遗漏匹配
100: 
101: ## Examples
102: 
103: ### Example 1
104: 
105: Input:
106: 
107:   需要搜索可能包含二进制数据的文件，同时避免二进制内容输出到终端
108: 
109: Output:
110: 
111:   使用 --binary 模式
112: 
113: Notes:
114: 
115:   继续搜索直到文件末尾或出现匹配，但不将二进制数据输出到终端
116: 
117: ### Example 2
118: 
119: Input:
120: 
121:   搜索以文本为主但含 NUL 字节的文件
122: 
123: Output:
124: 
125:   使用 -a/--text 模式
126: 
127: Notes:
128: 
129:   完全禁用二进制检测，按文本搜索

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-二进制检测行为解释\SKILL.md

1: ---
2: id: "ce28cd7a-282f-5d3d-9737-8380eaadabae"
3: name: "ripgrep 二进制检测行为解释"
4: description: "解释 ripgrep 在不同搜索模式下对二进制文件检测覆盖范围的差异，用于判断搜索结果是否受二进制检测影响。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "二进制检测"
9:   - "内存映射"
10:   - "搜索行为"
11: triggers:
12:   - "需要解释为何二进制文件在不同搜索模式下检测结果不一致"
13:   - "排查二进制文件匹配缺失或异常"
14: ---
15: 
16: # ripgrep 二进制检测行为解释
17: 
18: 解释 ripgrep 在不同搜索模式下对二进制文件检测覆盖范围的差异，用于判断搜索结果是否受二进制检测影响。
19: 
20: ## Prompt
21: 
22: 当需要解释或排查 ripgrep 对二进制文件的检测行为时，先确认当前搜索是否使用内存映射：若使用内存映射，二进制检测仅作用于文件前几 KB 以及每个匹配行；若不使用内存映射，则检测作用于所有被搜索的字节。据此判断当前搜索模式下二进制检测的覆盖范围，并据此解释匹配缺失或异常。
23: 
24: ## Objective
25: 
26: 帮助使用者理解 ripgrep 二进制检测行为随搜索模式变化的规则
27: ## Applicable Signals
28: 
29: - 二进制文件在不同搜索模式下检测结果不一致
30: - 二进制文件匹配缺失或异常
31: 
32: ## Contraindications
33: 
34: - 需要执行具体搜索命令
35: - 需要配置预处理器
36: 
37: ## Intervention Moves
38: 
39: - 确认当前搜索是否使用内存映射
40: - 根据搜索模式确定二进制检测的覆盖范围
41: - 据此解释匹配结果差异
42: 
43: ## Workflow Steps
44: 
45: - 确认当前 ripgrep 搜索是否使用内存映射
46: - 若使用内存映射，则二进制检测仅作用于文件前几 KB 以及每个匹配行
47: - 若不使用内存映射，则二进制检测作用于所有被搜索的字节
48: - 根据上述覆盖范围解释当前搜索的匹配结果
49: 
50: ## Constraints
51: 
52: - 仅用于解释检测行为，不提供具体搜索命令或预处理器配置
53: 
54: ## Cautions
55: 
56: - 二进制检测行为随搜索模式变化，解释结果时需先确认搜索模式
57: 
58: ## Output Contract
59: 
60: - 明确当前搜索模式下二进制检测的覆盖范围
61: 
62: ## Triggers
63: 
64: - 需要解释为何二进制文件在不同搜索模式下检测结果不一致
65: - 排查二进制文件匹配缺失或异常

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-基础行匹配搜索\SKILL.md

1: ---
2: id: "d58844fa-d303-523d-8af5-08eb4651beab"
3: name: "ripgrep 基础行匹配搜索"
4: description: "使用 ripgrep 对单个文件逐行匹配正则模式，并输出匹配行及其行号。适用于需要快速定位文本中符合模式的行的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "文本搜索"
9:   - "命令行"
10:   - "正则匹配"
11:   - "行匹配"
12: triggers:
13:   - "用户需要在文件中查找包含某模式的行"
14:   - "用户希望看到匹配行的行号"
15:   - "用户提供单个文件路径与搜索模式"
16: examples:
17:   - input: "rg 'fast\\w+' README.md"
18:     output: "75:  faster than both. (N.B. It is not, strictly speaking, a \"drop-in\" replacement\n119:### Is it really faster than everything else?"
19:     notes: "默认输出行号与匹配行"
20:   - input: "rg 'fn write\\('"
21:     output: "src/printer.rs\n469:    fn write(&mut self, buf: &[u8]) {"
22:     notes: "在源码中查找函数定义"
23: ---
24: 
25: # ripgrep 基础行匹配搜索
26: 
27: 使用 ripgrep 对单个文件逐行匹配正则模式，并输出匹配行及其行号。适用于需要快速定位文本中符合模式的行的场景。
28: 
29: ## Prompt
30: 
31: 对指定文件执行基础模式搜索：使用 rg 命令并传入正则模式与目标文件路径，ripgrep 会逐行读取文件内容，打印匹配的行并默认附带行号。若模式需要匹配单词变体，可使用正则量词（如 \w+ 或 \w*）控制匹配范围。若 ripgrep 报告未搜索任何文件，可加 --debug 排查，常见原因是 $HOME/.gitignore 中存在 * 规则。
32: 
33: ## Objective
34: 
35: 对指定文件执行基础模式搜索并输出带行号的匹配结果
36: ## Applicable Signals
37: 
38: - 用户提供单个文件路径与搜索模式
39: - 用户希望查看匹配行的行号
40: - 搜索范围限定在单个文件而非目录
41: 
42: ## Contraindications
43: 
44: - 需要跨文件递归搜索时
45: - 需要按文件类型或 glob 过滤时
46: 
47: ## Intervention Moves
48: 
49: - 使用 rg 命令传入正则模式与目标文件路径
50: - ripgrep 逐行读取文件并打印匹配行
51: - 默认输出包含行号
52: - 使用正则量词（如 \w+、\w*）控制匹配范围
53: 
54: ## Workflow Steps
55: 
56: - 确认目标文件路径与搜索模式
57: - 执行 rg '<pattern>' <file>
58: - 检查输出中的匹配行及行号
59: - 若未搜索到任何文件，加 --debug 排查 gitignore 规则
60: 
61: ## Constraints
62: 
63: - 仅针对单个文件执行搜索
64: - 模式语法遵循 ripgrep 的正则语法
65: 
66: ## Cautions
67: 
68: - 若 ripgrep 报告未搜索任何文件，常见原因是 $HOME/.gitignore 中存在 * 规则，可用 --debug 排查
69: 
70: ## Output Contract
71: 
72: - 终端输出匹配行及其行号
73: 
74: ## Example Therapist Responses
75: 
76: ### Example 1
77: 
78: - Client/Input: rg 'fast\w+' README.md
79: - Therapist/Output: 75:  faster than both. (N.B. It is not, strictly speaking, a "drop-in" replacement
80: 119:### Is it really faster than everything else?
81: - Notes: 默认输出行号与匹配行
82: 
83: ### Example 2
84: 
85: - Client/Input: rg 'fn write\('
86: - Therapist/Output: src/printer.rs
87: 469:    fn write(&mut self, buf: &[u8]) {
88: - Notes: 在源码中查找函数定义
89: 
90: ## Triggers
91: 
92: - 用户需要在文件中查找包含某模式的行
93: - 用户希望看到匹配行的行号
94: - 用户提供单个文件路径与搜索模式
95: 
96: ## Examples
97: 
98: ### Example 1
99: 
100: Input:
101: 
102:   rg 'fast\w+' README.md
103: 
104: Output:
105: 
106:   75:  faster than both. (N.B. It is not, strictly speaking, a "drop-in" replacement
107:   119:### Is it really faster than everything else?
108: 
109: Notes:
110: 
111:   默认输出行号与匹配行
112: 
113: ### Example 2
114: 
115: Input:
116: 
117:   rg 'fn write\('
118: 
119: Output:
120: 
121:   src/printer.rs
122:   469:    fn write(&mut self, buf: &[u8]) {
123: 
124: Notes:
125: 
126:   在源码中查找函数定义

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-常用选项速查\SKILL.md

1: ---
2: id: "262411b4-5c65-5347-81a7-550c08e3fc3f"
3: name: "ripgrep 常用选项速查"
4: description: "提供 ripgrep 常用命令行选项的参考清单，说明各选项的名称、作用与典型用法，用于快速查阅而非执行具体搜索任务。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "命令行"
9:   - "选项速查"
10:   - "参考"
11: triggers:
12:   - "需要确认某个 ripgrep 选项的含义或写法"
13:   - "想了解大小写、计数、上下文等常用标志"
14: examples:
15:   - input: "ripgrep 里怎么忽略大小写？"
16:     output: "-i/--ignore-case：搜索模式时忽略大小写差异，例如 rg -i fast 可匹配 fast、fASt、FAST 等。"
17:   - input: "smart-case 和 ignore-case 有什么区别？"
18:     output: "-S/--smart-case 类似 --ignore-case，但当模式包含大写字母时会自动禁用忽略大小写；通常写入别名或配置文件。"
19:   - input: "怎么只看匹配行数？"
20:     output: "-c/--count：报告匹配的总行数。"
21: ---
22: 
23: # ripgrep 常用选项速查
24: 
25: 提供 ripgrep 常用命令行选项的参考清单，说明各选项的名称、作用与典型用法，用于快速查阅而非执行具体搜索任务。
26: 
27: ## Prompt
28: 
29: 当使用者需要确认某个 ripgrep 选项的含义或写法时，按选项逐条给出其名称、作用与典型用法；只做参考性说明，不代为执行具体搜索任务。
30: 
31: ## Objective
32: 
33: 让使用者快速查阅 ripgrep 常用选项及其语义
34: ## Applicable Signals
35: 
36: - 需要确认某个 ripgrep 选项的含义或写法
37: - 想了解大小写、计数、上下文等常用标志
38: 
39: ## Contraindications
40: 
41: - 需要端到端完成一次具体搜索任务
42: - 需要排查配置或忽略规则问题
43: 
44: ## Intervention Moves
45: 
46: - 列出选项的短/长形式及其作用
47: - 说明该选项的典型用法或效果
48: 
49: ## Workflow Steps
50: 
51: - 确认使用者要查阅的选项或选项类别
52: - 给出该选项的名称、作用与典型用法
53: - 必要时提示相关选项的差异或组合使用
54: 
55: ## Constraints
56: 
57: - 仅提供参考说明，不执行具体搜索任务
58: - 不涉及配置或忽略规则问题的排查
59: 
60: ## Cautions
61: 
62: - 选项行为可能随版本变化，必要时提示以本地帮助输出为准
63: 
64: ## Output Contract
65: 
66: - 一份可检索的 ripgrep 常用选项说明清单
67: 
68: ## Example Therapist Responses
69: 
70: ### Example 1
71: 
72: - Client/Input: ripgrep 里怎么忽略大小写？
73: - Therapist/Output: -i/--ignore-case：搜索模式时忽略大小写差异，例如 rg -i fast 可匹配 fast、fASt、FAST 等。
74: 
75: ### Example 2
76: 
77: - Client/Input: smart-case 和 ignore-case 有什么区别？
78: - Therapist/Output: -S/--smart-case 类似 --ignore-case，但当模式包含大写字母时会自动禁用忽略大小写；通常写入别名或配置文件。
79: 
80: ### Example 3
81: 
82: - Client/Input: 怎么只看匹配行数？
83: - Therapist/Output: -c/--count：报告匹配的总行数。
84: 
85: ## Triggers
86: 
87: - 需要确认某个 ripgrep 选项的含义或写法
88: - 想了解大小写、计数、上下文等常用标志
89: 
90: ## Examples
91: 
92: ### Example 1
93: 
94: Input:
95: 
96:   ripgrep 里怎么忽略大小写？
97: 
98: Output:
99: 
100:   -i/--ignore-case：搜索模式时忽略大小写差异，例如 rg -i fast 可匹配 fast、fASt、FAST 等。
101: 
102: ### Example 2
103: 
104: Input:
105: 
106:   smart-case 和 ignore-case 有什么区别？
107: 
108: Output:
109: 
110:   -S/--smart-case 类似 --ignore-case，但当模式包含大写字母时会自动禁用忽略大小写；通常写入别名或配置文件。
111: 
112: ### Example 3
113: 
114: Input:
115: 
116:   怎么只看匹配行数？
117: 
118: Output:
119: 
120:   -c/--count：报告匹配的总行数。

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-忽略文件优先级与白名单配置\SKILL.md

1: ---
2: id: "91670e33-04d0-5a4a-9215-cd36a2391b00"
3: name: "ripgrep 忽略文件优先级与白名单配置"
4: description: "配置并解释 .rgignore/.ignore/.gitignore 的优先级与白名单规则，使 ripgrep 按预期包含或排除目录。适用于需要覆盖默认忽略行为或恢复被忽略目录的搜索场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "ignore-file"
9:   - "gitignore"
10:   - "whitelist"
11:   - "search-scope"
12: triggers:
13:   - "需要恢复被 .gitignore 忽略的目录"
14:   - "需要自定义忽略规则优先级"
15:   - "搜索范围被默认忽略规则意外排除"
16: examples:
17:   - input: ".gitignore 中包含 `log/`，需要恢复搜索 log 目录"
18:     output: "在更高优先级的 .ignore 或 .rgignore 中添加 `!log/` 白名单规则"
19:     notes: "ripgrep 先看到白名单规则，从而搜索该目录"
20: ---
21: 
22: # ripgrep 忽略文件优先级与白名单配置
23: 
24: 配置并解释 .rgignore/.ignore/.gitignore 的优先级与白名单规则，使 ripgrep 按预期包含或排除目录。适用于需要覆盖默认忽略行为或恢复被忽略目录的搜索场景。
25: 
26: ## Prompt
27: 
28: 当需要控制 ripgrep 的默认忽略行为时，按以下步骤配置忽略文件：
29: 1. 确认目标目录当前被哪一层忽略规则排除（.gitignore、.ignore 或 .rgignore）。
30: 2. 记住优先级顺序：.rgignore 高于 .ignore，.ignore 高于 .gitignore。
31: 3. 在需要覆盖的目录中放置更高优先级的忽略文件，并写入白名单规则（如 `!log/`）以恢复被忽略的目录。
32: 4. 忽略文件可放在任意目录，其规则相对于所在目录生效，与 .gitignore 一致。
33: 5. 若在大小写不敏感文件系统（如 Windows、macOS）上需要大小写不敏感处理，可使用 `--ignore-file-case-insensitive`，但注意可能有明显性能开销，默认关闭。
34: 6. 如需更深入的 glob 模式语义，参考 `man gitignore`。
35: 
36: ## Objective
37: 
38: 让使用者正确设置忽略文件优先级与白名单规则以控制搜索范围
39: ## Applicable Signals
40: 
41: - 目标目录被 .gitignore 排除但需要搜索
42: - 需要覆盖默认忽略行为
43: - 需要自定义忽略规则优先级
44: 
45: ## Contraindications
46: 
47: - 仅需临时排除少量文件（应使用 -g glob）
48: 
49: ## Intervention Moves
50: 
51: - 识别当前生效的忽略文件层级
52: - 在更高优先级文件中添加白名单规则（如 `!log/`）
53: - 必要时启用 --ignore-file-case-insensitive
54: 
55: ## Workflow Steps
56: 
57: - 确认目标目录被哪一层忽略规则排除
58: - 按 .rgignore > .ignore > .gitignore 的优先级选择放置位置
59: - 写入白名单规则恢复被忽略目录
60: - 在大小写不敏感文件系统上按需启用 --ignore-file-case-insensitive
61: 
62: ## Constraints
63: 
64: - 忽略文件可放在任意目录，规则相对于所在目录生效
65: - 白名单规则需放在更高优先级的忽略文件中才能生效
66: 
67: ## Cautions
68: 
69: - --ignore-file-case-insensitive 可能带来明显性能开销，默认关闭
70: 
71: ## Output Contract
72: 
73: - 一份可用的忽略文件配置及其优先级说明
74: 
75: ## Example Therapist Responses
76: 
77: ### Example 1
78: 
79: - Client/Input: .gitignore 中包含 `log/`，需要恢复搜索 log 目录
80: - Therapist/Output: 在更高优先级的 .ignore 或 .rgignore 中添加 `!log/` 白名单规则
81: - Notes: ripgrep 先看到白名单规则，从而搜索该目录
82: 
83: ## Triggers
84: 
85: - 需要恢复被 .gitignore 忽略的目录
86: - 需要自定义忽略规则优先级
87: - 搜索范围被默认忽略规则意外排除
88: 
89: ## Examples
90: 
91: ### Example 1
92: 
93: Input:
94: 
95:   .gitignore 中包含 `log/`，需要恢复搜索 log 目录
96: 
97: Output:
98: 
99:   在更高优先级的 .ignore 或 .rgignore 中添加 `!log/` 白名单规则
100: 
101: Notes:
102: 
103:   ripgrep 先看到白名单规则，从而搜索该目录

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-忽略规则与过滤控制\SKILL.md

1: ---
2: id: "5ba99044-a58d-58cf-bed4-9b314c6ed9f0"
3: name: "ripgrep 忽略规则与过滤控制"
4: description: "在递归搜索时按需启用或禁用 ripgrep 的忽略与过滤行为，包括 .gitignore、.ignore、.rgignore、隐藏文件、二进制文件和符号链接。适用于需要调整默认过滤范围或覆盖忽略规则的搜索任务。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "过滤"
9:   - "忽略规则"
10:   - "搜索范围"
11:   - "gitignore"
12: triggers:
13:   - "需要搜索被 .gitignore 忽略的文件"
14:   - "需要包含隐藏文件或目录"
15:   - "需要覆盖或补充忽略规则"
16:   - "需要搜索二进制文件或跟随符号链接"
17: examples:
18:   - input: "需要搜索被 .gitignore 忽略的配置文件"
19:     output: "使用 `--no-ignore` 或添加 `.rgignore` 覆盖规则后重新搜索"
20:     notes: "优先考虑补充忽略规则而非完全禁用忽略"
21:   - input: "需要搜索隐藏目录中的文件"
22:     output: "使用 `--hidden`（`-.`）标志执行搜索"
23: ---
24: 
25: # ripgrep 忽略规则与过滤控制
26: 
27: 在递归搜索时按需启用或禁用 ripgrep 的忽略与过滤行为，包括 .gitignore、.ignore、.rgignore、隐藏文件、二进制文件和符号链接。适用于需要调整默认过滤范围或覆盖忽略规则的搜索任务。
28: 
29: ## Prompt
30: 
31: 当默认过滤范围不符合搜索目标时，按以下顺序调整 ripgrep 的过滤与忽略行为：
32: 1. 明确当前搜索范围与期望范围的差异（被忽略的文件、隐藏文件、二进制文件、符号链接）。
33: 2. 选择最小必要的控制手段：
34:    - 禁用所有忽略相关过滤：`--no-ignore`。
35:    - 搜索隐藏文件与目录：`--hidden`（短标志 `-.`）。
36:    - 搜索二进制文件：`--text`（短标志 `-a`），注意二进制文件可能向终端输出控制字符。
37:    - 跟随符号链接：`--follow`（短标志 `-L`）。
38: 3. 如需保留默认忽略但补充或覆盖规则，使用 `.ignore`（应用无关）或 `.rgignore`（ripgrep 专用）文件，而不是直接禁用全部忽略。
39: 4. 注意 ripgrep 的忽略处理不仅限于 `.gitignore`，还包括 `$GIT_DIR/info/exclude` 以及全局忽略规则（通常为 `core.excludesFile`）。
40: 5. 执行搜索并核对结果范围是否符合预期。
41: 
42: ## Objective
43: 
44: 让使用者能够正确控制 ripgrep 的默认过滤与忽略规则，以扩大或缩小搜索范围。
45: ## Applicable Signals
46: 
47: - 默认搜索遗漏了目标文件
48: - 目标文件位于隐藏目录或被忽略路径中
49: - 需要临时或持久地覆盖忽略规则
50: 
51: ## Contraindications
52: 
53: - 仅需默认过滤行为且无需调整范围
54: - 搜索目标明确且默认规则已足够
55: 
56: ## Intervention Moves
57: 
58: - 使用 `--no-ignore` 禁用所有忽略相关过滤
59: - 使用 `--hidden`（`-.`）包含隐藏文件与目录
60: - 使用 `--text`（`-a`）搜索二进制文件
61: - 使用 `--follow`（`-L`）跟随符号链接
62: - 通过 `.ignore` 或 `.rgignore` 补充或覆盖忽略规则
63: 
64: ## Workflow Steps
65: 
66: - 确认默认过滤范围与期望范围的差异
67: - 选择最小必要的过滤控制标志或忽略规则文件
68: - 执行搜索并核对结果范围
69: - 必要时生成或调整 .ignore/.rgignore 配置
70: 
71: ## Constraints
72: 
73: - 优先使用最小必要的控制手段，避免无差别禁用全部忽略
74: - 使用 `--text` 时需注意二进制文件可能输出控制字符
75: 
76: ## Cautions
77: 
78: - `--text` 可能向终端输出控制字符，导致终端行为异常
79: - 禁用忽略过滤可能引入大量无关文件，影响结果可读性
80: 
81: ## Output Contract
82: 
83: - 得到符合预期过滤范围的搜索结果，或生成相应的 .ignore/.rgignore 配置。
84: 
85: ## Example Therapist Responses
86: 
87: ### Example 1
88: 
89: - Client/Input: 需要搜索被 .gitignore 忽略的配置文件
90: - Therapist/Output: 使用 `--no-ignore` 或添加 `.rgignore` 覆盖规则后重新搜索
91: - Notes: 优先考虑补充忽略规则而非完全禁用忽略
92: 
93: ### Example 2
94: 
95: - Client/Input: 需要搜索隐藏目录中的文件
96: - Therapist/Output: 使用 `--hidden`（`-.`）标志执行搜索
97: 
98: ## Triggers
99: 
100: - 需要搜索被 .gitignore 忽略的文件
101: - 需要包含隐藏文件或目录
102: - 需要覆盖或补充忽略规则
103: - 需要搜索二进制文件或跟随符号链接
104: 
105: ## Examples
106: 
107: ### Example 1
108: 
109: Input:
110: 
111:   需要搜索被 .gitignore 忽略的配置文件
112: 
113: Output:
114: 
115:   使用 `--no-ignore` 或添加 `.rgignore` 覆盖规则后重新搜索
116: 
117: Notes:
118: 
119:   优先考虑补充忽略规则而非完全禁用忽略
120: 
121: ### Example 2
122: 
123: Input:
124: 
125:   需要搜索隐藏目录中的文件
126: 
127: Output:
128: 
129:   使用 `--hidden`（`-.`）标志执行搜索

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-捕获组替换引用\SKILL.md

1: ---
2: id: "73f7abc9-4725-56f2-93a2-0493fac9b3ba"
3: name: "ripgrep 捕获组替换引用"
4: description: "在 ripgrep 的 --replace 中使用捕获组引用（如 $1）将匹配中的子组内容重组进替换文本，适用于需要基于匹配结构生成新文本的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "replace"
9:   - "capture-group"
10:   - "output-rewrite"
11: triggers:
12:   - "替换文本需要引用匹配中的子组"
13:   - "需要基于匹配结构重组输出"
14: examples:
15:   - input: "rg 'fast\\s+(\\w+)' README.md -r 'fast-$1'"
16:     output: "匹配中的子组内容被重组进替换文本，如 fast-while、fast-because"
17:     notes: "使用 $1 引用第一个捕获组"
18: ---
19: 
20: # ripgrep 捕获组替换引用
21: 
22: 在 ripgrep 的 --replace 中使用捕获组引用（如 $1）将匹配中的子组内容重组进替换文本，适用于需要基于匹配结构生成新文本的场景。
23: 
24: ## Prompt
25: 
26: 当替换文本需要引用匹配中的子组时，在模式中定义捕获组，并在 --replace 的替换文本中使用 $1、$2 等引用对应子组内容。可结合 --only-matching（-o）使替换仅作用于匹配部分。
27: 
28: ## Objective
29: 
30: 利用捕获组构造替换文本
31: ## Applicable Signals
32: 
33: - 替换文本需要引用匹配中的子组
34: - 需要基于匹配结构重组输出
35: 
36: ## Contraindications
37: 
38: - 替换文本为固定常量
39: - 模式中无捕获组
40: 
41: ## Intervention Moves
42: 
43: - 在搜索模式中定义捕获组
44: - 在 --replace 替换文本中使用 $1、$2 等引用子组
45: - 必要时结合 --only-matching（-o）限定替换范围
46: 
47: ## Workflow Steps
48: 
49: - 确认替换文本需要引用匹配中的子组内容
50: - 在搜索模式中定义捕获组
51: - 在 --replace 的替换文本中使用 $1、$2 等引用对应子组
52: - 必要时结合 --only-matching（-o）使替换仅作用于匹配部分
53: - 检查输出中匹配是否被含捕获组内容的替换文本替代
54: 
55: ## Constraints
56: 
57: - 替换文本中的捕获组引用必须与模式中定义的捕获组对应
58: 
59: ## Cautions
60: 
61: - --replace 仅作用于匹配部分；若需替换整行，需在模式中包含整行
62: 
63: ## Output Contract
64: 
65: - 输出中匹配被含捕获组内容的替换文本替代
66: 
67: ## Example Therapist Responses
68: 
69: ### Example 1
70: 
71: - Client/Input: rg 'fast\s+(\w+)' README.md -r 'fast-$1'
72: - Therapist/Output: 匹配中的子组内容被重组进替换文本，如 fast-while、fast-because
73: - Notes: 使用 $1 引用第一个捕获组
74: 
75: ## Triggers
76: 
77: - 替换文本需要引用匹配中的子组
78: - 需要基于匹配结构重组输出
79: 
80: ## Examples
81: 
82: ### Example 1
83: 
84: Input:
85: 
86:   rg 'fast\s+(\w+)' README.md -r 'fast-$1'
87: 
88: Output:
89: 
90:   匹配中的子组内容被重组进替换文本，如 fast-while、fast-because
91: 
92: Notes:
93: 
94:   使用 $1 引用第一个捕获组

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-替换与配置预处理流程\SKILL.md

1: ---
2: id: "a4245429-7e5f-5215-b208-20f621b76667"
3: name: "ripgrep 替换与配置预处理流程"
4: description: "在用户明确替换目标或配置意图时，使用 ripgrep 的替换功能修改匹配内容，并通过配置文件、编码设置、二进制数据处理及预处理器优化搜索行为。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "替换"
9:   - "配置"
10:   - "预处理器"
11:   - "编码"
12:   - "二进制数据"
13: triggers:
14:   - "用户需要对匹配内容执行替换"
15:   - "用户需要配置 ripgrep 的编码、二进制或预处理器行为"
16: ---
17: 
18: # ripgrep 替换与配置预处理流程
19: 
20: 在用户明确替换目标或配置意图时，使用 ripgrep 的替换功能修改匹配内容，并通过配置文件、编码设置、二进制数据处理及预处理器优化搜索行为。
21: 
22: ## Prompt
23: 
24: 当用户需要对匹配内容执行替换，或需要配置 ripgrep 的编码、二进制或预处理器行为时，按以下步骤执行：
25: 1. 确认替换目标或配置意图，明确要修改的内容或要定制的搜索环境。
26: 2. 若执行替换，使用 ripgrep 的替换功能修改匹配内容，并核对替换结果输出。
27: 3. 若需定制搜索环境，依次处理配置文件、文件编码、二进制数据及预处理器相关设置。
28: 4. 验证配置生效后的搜索行为是否发生预期改变。
29: 5. 输出替换结果或配置生效后的搜索行为改变作为交付物。
30: 
31: ## Objective
32: 
33: 完成替换操作并配置预处理与编码等高级搜索选项
34: ## Applicable Signals
35: 
36: - 用户需要对匹配内容执行替换
37: - 用户需要配置 ripgrep 的编码、二进制或预处理器行为
38: 
39: ## Contraindications
40: 
41: - 仅需简单搜索且无需修改文件内容
42: - 用户未明确替换目标或配置意图
43: 
44: ## Intervention Moves
45: 
46: - 使用 ripgrep 的替换功能修改匹配内容
47: - 通过配置文件定制搜索行为
48: - 设置文件编码处理
49: - 处理二进制数据
50: - 配置预处理器以优化搜索
51: 
52: ## Workflow Steps
53: 
54: - 确认替换目标或配置意图
55: - 执行替换操作或应用配置设置
56: - 验证替换结果或配置生效后的搜索行为改变
57: - 输出交付物
58: 
59: ## Constraints
60: 
61: - 仅在用户明确替换目标或配置意图时执行
62: - 替换操作需核对结果输出
63: 
64: ## Cautions
65: 
66: - 替换操作可能修改文件内容，需确认目标无误
67: - 配置变更可能影响后续搜索行为，需验证生效
68: 
69: ## Output Contract
70: 
71: - 替换结果输出或配置文件生效后的搜索行为改变
72: 
73: ## Triggers
74: 
75: - 用户需要对匹配内容执行替换
76: - 用户需要配置 ripgrep 的编码、二进制或预处理器行为

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-替换匹配文本\SKILL.md

1: ---
2: id: "81628702-defb-59fc-857a-998b747f9977"
3: name: "ripgrep 替换匹配文本"
4: description: "使用 --replace/-r 将 ripgrep 输出中匹配到的文本片段替换为指定内容，仅作用于匹配部分而非整行，不修改源文件。适用于需要改写或标注命中片段的输出场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "replace"
9:   - "output-rewrite"
10:   - "micro-skill"
11: triggers:
12:   - "需要把命中片段替换为其他文本"
13:   - "希望输出中直接呈现替换后的内容"
14: examples:
15:   - input: "rg fast README.md -r FAST"
16:     output: "输出中所有 fast 匹配片段被替换为 FAST"
17:     notes: "仅替换匹配部分"
18:   - input: "rg '^.*fast.*$' README.md -r FAST"
19:     output: "整行被替换为 FAST"
20:     notes: "匹配覆盖整行以实现整行替换"
21:   - input: "rg fast README.md -or FAST"
22:     output: "仅匹配部分被替换为 FAST"
23:     notes: "结合 --only-matching 与 --replace"
24: ---
25: 
26: # ripgrep 替换匹配文本
27: 
28: 使用 --replace/-r 将 ripgrep 输出中匹配到的文本片段替换为指定内容，仅作用于匹配部分而非整行，不修改源文件。适用于需要改写或标注命中片段的输出场景。
29: 
30: ## Prompt
31: 
32: 当需要把 ripgrep 命中片段替换为其他文本时，使用 --replace（或 -r）标志。该标志仅替换输出中匹配的部分，不修改源文件。若需替换整行，需让匹配覆盖整行（例如使用 '^.*pattern.*$'），或结合 --only-matching/-o 与 --replace 达到相同效果。
33: 
34: ## Objective
35: 
36: 对匹配文本片段执行替换输出
37: ## Applicable Signals
38: 
39: - 需要把命中片段替换为其他文本
40: - 希望输出中直接呈现替换后的内容
41: 
42: ## Contraindications
43: 
44: - 需要替换整行而非匹配片段
45: - 需要修改源文件内容而非仅输出
46: 
47: ## Intervention Moves
48: 
49: - 使用 --replace/-r 指定替换文本
50: - 仅替换匹配部分而非整行
51: - 如需替换整行，让匹配覆盖整行或结合 --only-matching/-o 与 --replace
52: 
53: ## Workflow Steps
54: 
55: - 确认目标为替换输出中的匹配片段
56: - 使用 rg pattern file -r REPLACEMENT 执行替换
57: - 如需整行替换，使用 rg '^.*pattern.*$' file -r REPLACEMENT 或 rg pattern file -or REPLACEMENT
58: 
59: ## Constraints
60: 
61: - --replace 仅作用于匹配部分，不修改源文件
62: 
63: ## Cautions
64: 
65: - 替换整行需让匹配覆盖整行，否则仅替换匹配片段
66: 
67: ## Output Contract
68: 
69: - 输出中匹配片段被替换为指定文本
70: 
71: ## Example Therapist Responses
72: 
73: ### Example 1
74: 
75: - Client/Input: rg fast README.md -r FAST
76: - Therapist/Output: 输出中所有 fast 匹配片段被替换为 FAST
77: - Notes: 仅替换匹配部分
78: 
79: ### Example 2
80: 
81: - Client/Input: rg '^.*fast.*$' README.md -r FAST
82: - Therapist/Output: 整行被替换为 FAST
83: - Notes: 匹配覆盖整行以实现整行替换
84: 
85: ### Example 3
86: 
87: - Client/Input: rg fast README.md -or FAST
88: - Therapist/Output: 仅匹配部分被替换为 FAST
89: - Notes: 结合 --only-matching 与 --replace
90: 
91: ## Triggers
92: 
93: - 需要把命中片段替换为其他文本
94: - 希望输出中直接呈现替换后的内容
95: 
96: ## Examples
97: 
98: ### Example 1
99: 
100: Input:
101: 
102:   rg fast README.md -r FAST
103: 
104: Output:
105: 
106:   输出中所有 fast 匹配片段被替换为 FAST
107: 
108: Notes:
109: 
110:   仅替换匹配部分
111: 
112: ### Example 2
113: 
114: Input:
115: 
116:   rg '^.*fast.*$' README.md -r FAST
117: 
118: Output:
119: 
120:   整行被替换为 FAST
121: 
122: Notes:
123: 
124:   匹配覆盖整行以实现整行替换
125: 
126: ### Example 3
127: 
128: Input:
129: 
130:   rg fast README.md -or FAST
131: 
132: Output:
133: 
134:   仅匹配部分被替换为 FAST
135: 
136: Notes:
137: 
138:   结合 --only-matching 与 --replace

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-替换预览与配置持久化\SKILL.md

1: ---
2: id: "2921cff6-f52c-582e-a935-672d57441537"
3: name: "ripgrep 替换预览与配置持久化"
4: description: "使用 ripgrep 的替换选项输出替换后的文本预览（不修改原文件），并将常用搜索选项写入 ripgrep 配置文件以持久化搜索行为。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "替换"
9:   - "配置"
10:   - "文本处理"
11: triggers:
12:   - "用户需要预览替换结果"
13:   - "用户希望保存常用搜索选项到配置文件"
14: examples:
15:   - input: "用户希望预览将 'fast' 替换为 'quick' 的结果"
16:     output: "使用 ripgrep 替换选项输出替换后的文本预览"
17:     notes: "不修改原文件"
18:   - input: "用户希望保存常用搜索选项到配置文件"
19:     output: "生成或更新 ripgrep 配置文件"
20:     notes: "配置文件应包含用户指定的常用选项"
21: ---
22: 
23: # ripgrep 替换预览与配置持久化
24: 
25: 使用 ripgrep 的替换选项输出替换后的文本预览（不修改原文件），并将常用搜索选项写入 ripgrep 配置文件以持久化搜索行为。
26: 
27: ## Prompt
28: 
29: 当用户需要预览替换结果或希望保存常用搜索选项到配置文件时，使用本技能。执行步骤：1) 确认用户意图是替换预览还是配置持久化；2) 若为替换预览，使用 ripgrep 的替换选项输出替换后的文本，不直接修改原文件；3) 若为配置持久化，将常用选项写入 ripgrep 配置文件；4) 验证输出或配置文件内容是否符合预期。
30: 
31: ## Objective
32: 
33: 执行模式替换预览并管理 ripgrep 配置
34: ## Applicable Signals
35: 
36: - 用户需要预览替换结果
37: - 用户希望保存常用搜索选项到配置文件
38: 
39: ## Contraindications
40: 
41: - 仅需搜索不需要替换时
42: - 不需要持久化配置时
43: 
44: ## Intervention Moves
45: 
46: - 使用 ripgrep 替换选项输出替换后的文本
47: - 将常用选项写入 ripgrep 配置文件
48: 
49: ## Workflow Steps
50: 
51: - 确认用户意图是替换预览还是配置持久化
52: - 若为替换预览，使用 ripgrep 的替换选项输出替换后的文本，不直接修改原文件
53: - 若为配置持久化，将常用选项写入 ripgrep 配置文件
54: - 验证输出或配置文件内容是否符合预期
55: 
56: ## Constraints
57: 
58: - 替换操作应仅输出预览，不直接修改原文件
59: - 配置文件应使用 ripgrep 支持的格式
60: 
61: ## Cautions
62: 
63: - 替换预览可能因正则表达式语法差异产生意外结果
64: - 配置文件中的选项可能影响后续所有搜索行为
65: 
66: ## Output Contract
67: 
68: - 输出替换后的文本或生成配置文件
69: 
70: ## Example Therapist Responses
71: 
72: ### Example 1
73: 
74: - Client/Input: 用户希望预览将 'fast' 替换为 'quick' 的结果
75: - Therapist/Output: 使用 ripgrep 替换选项输出替换后的文本预览
76: - Notes: 不修改原文件
77: 
78: ### Example 2
79: 
80: - Client/Input: 用户希望保存常用搜索选项到配置文件
81: - Therapist/Output: 生成或更新 ripgrep 配置文件
82: - Notes: 配置文件应包含用户指定的常用选项
83: 
84: ## Triggers
85: 
86: - 用户需要预览替换结果
87: - 用户希望保存常用搜索选项到配置文件
88: 
89: ## Examples
90: 
91: ### Example 1
92: 
93: Input:
94: 
95:   用户希望预览将 'fast' 替换为 'quick' 的结果
96: 
97: Output:
98: 
99:   使用 ripgrep 替换选项输出替换后的文本预览
100: 
101: Notes:
102: 
103:   不修改原文件
104: 
105: ### Example 2
106: 
107: Input:
108: 
109:   用户希望保存常用搜索选项到配置文件
110: 
111: Output:
112: 
113:   生成或更新 ripgrep 配置文件
114: 
115: Notes:
116: 
117:   配置文件应包含用户指定的常用选项

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-自动编码处理\SKILL.md

1: ---
2: id: "2c814928-5d5a-5b76-b753-698a489a180e"
3: name: "ripgrep 自动编码处理"
4: description: "在搜索时依赖 ripgrep 默认的 --encoding auto 行为，让其根据文件内容自动推断编码，并在必要时对模式或文件进行转码，以匹配 ASCII、latin1、UTF-8 及 Windows 环境常见的 UTF-16。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "encoding"
9:   - "auto"
10:   - "utf-16"
11:   - "latin1"
12:   - "utf-8"
13: triggers:
14:   - "搜索包含非 ASCII 或 UTF-16 编码的文件"
15:   - "不确定文件编码时希望 ripgrep 自动处理"
16: ---
17: 
18: # ripgrep 自动编码处理
19: 
20: 在搜索时依赖 ripgrep 默认的 --encoding auto 行为，让其根据文件内容自动推断编码，并在必要时对模式或文件进行转码，以匹配 ASCII、latin1、UTF-8 及 Windows 环境常见的 UTF-16。
21: 
22: ## Prompt
23: 
24: 当搜索目标可能包含非 ASCII 或 UTF-16 编码的文件，且不确定文件编码时，依赖 ripgrep 的默认 --encoding auto 行为：让 ripgrep 自动推断文件编码，并在必要时对模式或文件进行转码，使两者编码一致。无需手动指定编码即可执行搜索。
25: 
26: ## Objective
27: 
28: 理解并正确使用 ripgrep 的自动编码处理行为，避免因编码不匹配导致搜索失败。
29: ## Applicable Signals
30: 
31: - 文件包含非 ASCII 字节
32: - 文件可能为 UTF-16 编码（常见于 Windows 环境）
33: - 文件编码未知
34: 
35: ## Contraindications
36: 
37: - 需要强制指定特定编码进行精确匹配
38: - 文件为二进制数据且未启用相应处理
39: 
40: ## Intervention Moves
41: 
42: - 使用默认的 --encoding auto 让 ripgrep 自动推断编码
43: - 在必要时由 ripgrep 对模式或文件进行转码以匹配编码
44: 
45: ## Workflow Steps
46: 
47: - 确认搜索目标可能包含非 ASCII 或 UTF-16 编码的文件
48: - 使用默认 --encoding auto（无需显式指定）执行搜索
49: - 由 ripgrep 自动推断编码并在必要时转码模式或文件
50: - 检查搜索是否返回匹配结果
51: 
52: ## Constraints
53: 
54: - ripgrep 无法可靠地预先得知文件编码
55: - 模式编码必须与文件编码匹配，或通过转码使两者一致
56: - ripgrep 最适合纯文本文件，常见编码为 ASCII、latin1、UTF-8，UTF-16 在 Windows 环境常见
57: 
58: ## Cautions
59: 
60: - 编码不匹配可能导致搜索失败或漏匹配
61: - 二进制数据需要相应处理选项，不能仅依赖编码自动推断
62: 
63: ## Output Contract
64: 
65: - 搜索命令正确执行并返回匹配结果，无需手动指定编码。
66: 
67: ## Triggers
68: 
69: - 搜索包含非 ASCII 或 UTF-16 编码的文件
70: - 不确定文件编码时希望 ripgrep 自动处理

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-自动过滤规则说明\SKILL.md

1: ---
2: id: "d90ef9b1-ea8c-53b5-8b8d-9d4b724a1f48"
3: name: "ripgrep 自动过滤规则说明"
4: description: "说明并应用 ripgrep 默认的自动过滤机制：在递归搜索时默认忽略 gitignore/ignore/rgignore 规则匹配的文件、隐藏文件与目录、二进制文件，并且不跟随符号链接。适用于希望减少无关结果、聚焦源码或文本内容的搜索场景，也用于解释为何某些文件未出现在搜索结果中。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "自动过滤"
9:   - "递归搜索"
10:   - "gitignore"
11:   - "ignore"
12:   - "rgignore"
13: triggers:
14:   - "用户希望搜索结果排除版本控制忽略文件、隐藏文件或二进制文件"
15:   - "用户需要理解为何某些文件未出现在 ripgrep 搜索结果中"
16:   - "用户进行递归目录搜索并希望聚焦源码或文本内容"
17: examples:
18:   - input: "为什么我搜索时没有看到 .gitignore 中列出的文件？"
19:     output: "ripgrep 默认会忽略匹配 .gitignore、.ignore、.rgignore glob 模式的文件与目录，因此这些文件不会出现在结果中。"
20:     notes: "说明默认过滤行为"
21:   - input: "我只想搜索 src 目录下的内容。"
22:     output: "可以显式指定目录，例如 `rg 'fn write\\(' src`，这样 ripgrep 会将搜索限制在 src 目录。"
23:     notes: "限定搜索目录以缩小范围"
24: ---
25: 
26: # ripgrep 自动过滤规则说明
27: 
28: 说明并应用 ripgrep 默认的自动过滤机制：在递归搜索时默认忽略 gitignore/ignore/rgignore 规则匹配的文件、隐藏文件与目录、二进制文件，并且不跟随符号链接。适用于希望减少无关结果、聚焦源码或文本内容的搜索场景，也用于解释为何某些文件未出现在搜索结果中。
29: 
30: ## Prompt
31: 
32: 当调用方希望缩小 ripgrep 递归搜索范围、排除版本控制忽略项、隐藏文件或二进制文件，或需要解释某些文件为何未被搜索到时，使用本参考技能。
33: 
34: 执行要点：
35: 1. 确认当前搜索为递归目录搜索（未显式指定文件路径时，ripgrep 默认搜索当前目录，等价于 `rg foo ./`）。
36: 2. 说明默认忽略的四类内容：
37:    - 匹配 `.gitignore`（含全局与仓库级，以及同一 git 仓库父目录中的 .gitignore）、`.ignore`（冲突时优先于 gitignore）、`.rgignore`（冲突时优先于 .ignore）glob 模式的文件与目录；
38:    - 隐藏文件与目录；
39:    - 二进制文件（含 `NUL` 字节即视为二进制）；
40:    - 符号链接不被跟随。
41: 3. 若调用方需要搜索被忽略的内容，提示这些默认行为可通过相应标志切换，而不是直接假设结果完整。
42: 4. 若调用方需要限定搜索目录，可显式指定目录（如 `rg 'fn write\(' src`）以缩小范围。
43: 
44: 本技能为参考性知识，不替代手动过滤（globs、文件类型）等可执行操作。
45: 
46: ## Objective
47: 
48: 说明并应用 ripgrep 默认忽略规则以缩小搜索范围
49: ## Applicable Signals
50: 
51: - 递归搜索返回结果少于预期
52: - 搜索结果中缺少被版本控制忽略或隐藏的文件
53: - 用户询问 ripgrep 默认不搜索哪些内容
54: 
55: ## Contraindications
56: 
57: - 用户明确要求搜索被忽略的文件或目录
58: - 需要搜索二进制内容且未调整默认行为
59: 
60: ## Intervention Moves
61: 
62: - 说明默认忽略的四类内容：gitignore/ignore/rgignore glob、隐藏文件与目录、二进制文件、符号链接
63: - 说明 .ignore 优先于 gitignore、.rgignore 优先于 .ignore 的优先级关系
64: - 说明未指定路径时默认搜索当前目录
65: - 提示可通过标志切换默认忽略行为以搜索被忽略内容
66: 
67: ## Workflow Steps
68: 
69: - 确认搜索为递归目录搜索
70: - 列出 ripgrep 默认忽略的四类内容及其优先级
71: - 根据调用方目标判断默认过滤是否满足需求
72: - 若需搜索被忽略内容，提示需调整默认行为而非依赖默认结果
73: 
74: ## Constraints
75: 
76: - 本技能仅描述默认过滤行为，不执行手动过滤（globs、文件类型）操作
77: - 默认忽略行为可通过标志切换，说明时不应将其表述为不可更改
78: 
79: ## Cautions
80: 
81: - 默认不跟随符号链接，可能遗漏链接目标中的匹配
82: - 二进制文件默认被忽略，若需搜索二进制内容需显式调整行为
83: 
84: ## Output Contract
85: 
86: - 调用方获得对 ripgrep 默认忽略规则的清晰说明，并能据此判断搜索结果中不包含被默认忽略的文件类型或目录是否符合预期。
87: 
88: ## Example Therapist Responses
89: 
90: ### Example 1
91: 
92: - Client/Input: 为什么我搜索时没有看到 .gitignore 中列出的文件？
93: - Therapist/Output: ripgrep 默认会忽略匹配 .gitignore、.ignore、.rgignore glob 模式的文件与目录，因此这些文件不会出现在结果中。
94: - Notes: 说明默认过滤行为
95: 
96: ### Example 2
97: 
98: - Client/Input: 我只想搜索 src 目录下的内容。
99: - Therapist/Output: 可以显式指定目录，例如 `rg 'fn write\(' src`，这样 ripgrep 会将搜索限制在 src 目录。
100: - Notes: 限定搜索目录以缩小范围
101: 
102: ## Triggers
103: 
104: - 用户希望搜索结果排除版本控制忽略文件、隐藏文件或二进制文件
105: - 用户需要理解为何某些文件未出现在 ripgrep 搜索结果中
106: - 用户进行递归目录搜索并希望聚焦源码或文本内容
107: 
108: ## Examples
109: 
110: ### Example 1
111: 
112: Input:
113: 
114:   为什么我搜索时没有看到 .gitignore 中列出的文件？
115: 
116: Output:
117: 
118:   ripgrep 默认会忽略匹配 .gitignore、.ignore、.rgignore glob 模式的文件与目录，因此这些文件不会出现在结果中。
119: 
120: Notes:
121: 
122:   说明默认过滤行为
123: 
124: ### Example 2
125: 
126: Input:
127: 
128:   我只想搜索 src 目录下的内容。
129: 
130: Output:
131: 
132:   可以显式指定目录，例如 `rg 'fn write\(' src`，这样 ripgrep 会将搜索限制在 src 目录。
133: 
134: Notes:
135: 
136:   限定搜索目录以缩小范围

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-自定义文件类型临时定义\SKILL.md

1: ---
2: id: "db337ffa-3819-5740-a11c-d8374160a702"
3: name: "ripgrep 自定义文件类型临时定义"
4: description: "通过 --type-add 在当前 ripgrep 命令中临时定义新的文件类型（如 web:*.{html,css,js}），并用 -t<类型名> 应用过滤，可用 --type-list 验证定义。适用于内置类型不覆盖的常用文件组合，且只需在当前命令生效的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "文件类型过滤"
9:   - "type-add"
10:   - "type-list"
11:   - "搜索准备"
12: triggers:
13:   - "内置类型不包含所需文件组合"
14:   - "需要临时按自定义扩展名集合搜索"
15:   - "希望用简短类型名替代重复的 -g glob 写法"
16: examples:
17:   - input: "需要搜索 html、css、js 文件中的 title"
18:     output: "rg --type-add 'web:*.{html,css,js}' -tweb title"
19:     notes: "花括号合并多个扩展名，-tweb 应用新类型"
20:   - input: "验证自定义类型是否已定义"
21:     output: "rg --type-add 'web:*.{html,css,js}' --type-list"
22:     notes: "新类型会出现在列表中，即使不属于内置类型"
23: ---
24: 
25: # ripgrep 自定义文件类型临时定义
26: 
27: 通过 --type-add 在当前 ripgrep 命令中临时定义新的文件类型（如 web:*.{html,css,js}），并用 -t<类型名> 应用过滤，可用 --type-list 验证定义。适用于内置类型不覆盖的常用文件组合，且只需在当前命令生效的场景。
28: 
29: ## Prompt
30: 
31: 当内置文件类型不覆盖所需扩展名组合时，使用 --type-add 在当前命令中定义自定义类型，并用 -t<类型名> 应用该过滤。定义后可用 --type-list 验证新类型是否出现。注意 --type-add 仅对当前命令生效，不会持久保存。
32: 
33: ## Objective
34: 
35: 为当前命令临时定义并应用自定义文件类型
36: ## Applicable Signals
37: 
38: - 需要搜索的扩展名集合未被任何内置类型覆盖
39: - 用户希望用 -t 类型名而非重复书写 -g glob
40: - 需要临时组合多种扩展名（如 html、css、js）作为一类
41: 
42: ## Contraindications
43: 
44: - 需要跨命令持久生效（应使用 shell alias 或配置文件）
45: - 仅需使用已有内置类型
46: 
47: ## Intervention Moves
48: 
49: - 使用 --type-add '<名称>:<glob>' 定义新类型，多个扩展名可用花括号合并
50: - 使用 -t<名称> 应用该类型过滤
51: - 使用 --type-list 验证新类型是否出现在列表中
52: 
53: ## Workflow Steps
54: 
55: - 确认内置类型不覆盖目标扩展名组合（可用 --type-list 查看）
56: - 用 --type-add 定义自定义类型，例如 --type-add 'web:*.{html,css,js}'
57: - 用 -t<类型名> 应用过滤并执行搜索
58: - 如需验证，运行 --type-list 确认新类型已列出
59: 
60: ## Constraints
61: 
62: - --type-add 仅对当前命令生效，不会持久保存
63: - 类型名与 glob 需符合 ripgrep 类型定义语法
64: 
65: ## Cautions
66: 
67: - 若需在每条命令中生效，应改用 shell alias 或配置文件，而非依赖 --type-add
68: 
69: ## Output Contract
70: 
71: - 一条包含 --type-add 的 rg 命令，且 --type-list 能显示新类型
72: 
73: ## Example Therapist Responses
74: 
75: ### Example 1
76: 
77: - Client/Input: 需要搜索 html、css、js 文件中的 title
78: - Therapist/Output: rg --type-add 'web:*.{html,css,js}' -tweb title
79: - Notes: 花括号合并多个扩展名，-tweb 应用新类型
80: 
81: ### Example 2
82: 
83: - Client/Input: 验证自定义类型是否已定义
84: - Therapist/Output: rg --type-add 'web:*.{html,css,js}' --type-list
85: - Notes: 新类型会出现在列表中，即使不属于内置类型
86: 
87: ## Triggers
88: 
89: - 内置类型不包含所需文件组合
90: - 需要临时按自定义扩展名集合搜索
91: - 希望用简短类型名替代重复的 -g glob 写法
92: 
93: ## Examples
94: 
95: ### Example 1
96: 
97: Input:
98: 
99:   需要搜索 html、css、js 文件中的 title
100: 
101: Output:
102: 
103:   rg --type-add 'web:*.{html,css,js}' -tweb title
104: 
105: Notes:
106: 
107:   花括号合并多个扩展名，-tweb 应用新类型
108: 
109: ### Example 2
110: 
111: Input:
112: 
113:   验证自定义类型是否已定义
114: 
115: Output:
116: 
117:   rg --type-add 'web:*.{html,css,js}' --type-list
118: 
119: Notes:
120: 
121:   新类型会出现在列表中，即使不属于内置类型

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-递归搜索与自动过滤\SKILL.md

1: ---
2: id: "dc2d24fe-1569-5c3e-8e82-7e165fcb1c61"
3: name: "ripgrep 递归搜索与自动过滤"
4: description: "在目录树中递归搜索模式，并利用 ripgrep 默认的自动过滤（遵循 .gitignore、跳过二进制文件等）缩小搜索范围。适用于在代码库或目录树中查找匹配内容。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "递归搜索"
9:   - "自动过滤"
10:   - "目录遍历"
11: triggers:
12:   - "用户需要在多个文件或整个目录中搜索模式"
13:   - "用户希望自动忽略被 gitignore 的文件"
14:   - "在代码库或目录树中查找匹配内容"
15: examples:
16:   - input: "在 ripgrep 源码目录中搜索函数定义"
17:     output: "src/printer.rs\n469:    fn write(&mut self, buf: &[u8]) {"
18:     notes: "递归搜索跨文件返回匹配行及行号"
19: ---
20: 
21: # ripgrep 递归搜索与自动过滤
22: 
23: 在目录树中递归搜索模式，并利用 ripgrep 默认的自动过滤（遵循 .gitignore、跳过二进制文件等）缩小搜索范围。适用于在代码库或目录树中查找匹配内容。
24: 
25: ## Prompt
26: 
27: 当需要在多个文件或整个目录中搜索模式时，直接对目标目录运行 ripgrep 递归搜索，无需显式指定文件列表。ripgrep 默认会递归遍历目录，并自动应用过滤规则（如遵循 .gitignore、跳过二进制文件），从而缩小搜索范围。若结果为空或提示未搜索任何文件，可使用 --debug 排查过滤原因（例如 $HOME/.gitignore 中的 * 规则）。
28: 
29: ## Objective
30: 
31: 在目录树中递归搜索模式并应用默认过滤规则
32: ## Applicable Signals
33: 
34: - 搜索目标跨越多个文件或整个目录
35: - 希望自动忽略被 gitignore 的文件
36: - 需要跳过二进制文件
37: 
38: ## Contraindications
39: 
40: - 仅需搜索单个已知文件时
41: - 需要手动指定文件类型或 glob 过滤时
42: 
43: ## Intervention Moves
44: 
45: - 对目标目录直接运行 ripgrep 递归搜索
46: - 依赖默认自动过滤缩小搜索范围
47: - 结果为空时使用 --debug 排查过滤原因
48: 
49: ## Workflow Steps
50: 
51: - 确定要搜索的目录树范围
52: - 对目标目录运行 ripgrep 递归搜索模式
53: - 依赖默认自动过滤（遵循 .gitignore、跳过二进制文件）缩小结果
54: - 若提示未搜索任何文件，使用 --debug 排查过滤规则
55: 
56: ## Constraints
57: 
58: - 递归搜索面向目录树而非单个文件
59: - 默认过滤行为依赖 .gitignore 等规则
60: 
61: ## Cautions
62: 
63: - 若存在 $HOME/.gitignore 中的 * 规则，可能导致未搜索任何文件
64: 
65: ## Output Contract
66: 
67: - 输出跨文件的匹配结果列表
68: 
69: ## Example Therapist Responses
70: 
71: ### Example 1
72: 
73: - Client/Input: 在 ripgrep 源码目录中搜索函数定义
74: - Therapist/Output: src/printer.rs
75: 469:    fn write(&mut self, buf: &[u8]) {
76: - Notes: 递归搜索跨文件返回匹配行及行号
77: 
78: ## Triggers
79: 
80: - 用户需要在多个文件或整个目录中搜索模式
81: - 用户希望自动忽略被 gitignore 的文件
82: - 在代码库或目录树中查找匹配内容
83: 
84: ## Examples
85: 
86: ### Example 1
87: 
88: Input:
89: 
90:   在 ripgrep 源码目录中搜索函数定义
91: 
92: Output:
93: 
94:   src/printer.rs
95:   469:    fn write(&mut self, buf: &[u8]) {
96: 
97: Notes:
98: 
99:   递归搜索跨文件返回匹配行及行号

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-配置文件默认选项设置\SKILL.md

1: ---
2: id: "556e78e5-fde6-567c-a379-e2b65df28a06"
3: name: "ripgrep 配置文件默认选项设置"
4: description: "通过 ripgrep 配置文件持久化默认选项，避免依赖 shell 别名。适用于需要为 ripgrep 设置稳定默认参数时。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "配置文件"
9:   - "默认选项"
10:   - "配置管理"
11: triggers:
12:   - "需要为 ripgrep 设置持久默认选项"
13:   - "shell 别名不方便或不适用"
14: examples:
15:   - input: "希望 ripgrep 默认忽略大小写并显示行号"
16:     output: "在配置文件中逐行写入对应选项，每行一个参数，保存后默认生效"
17:     notes: "每行去除首尾空白，`#` 开头行作为注释"
18:   - input: "在配置文件中写入带引号或转义的复杂表达式"
19:     output: "不适用：配置文件没有转义机制，每行会作为单个参数原样传入"
20:     notes: "复杂 shell 语法应改用其他方式"
21: ---
22: 
23: # ripgrep 配置文件默认选项设置
24: 
25: 通过 ripgrep 配置文件持久化默认选项，避免依赖 shell 别名。适用于需要为 ripgrep 设置稳定默认参数时。
26: 
27: ## Prompt
28: 
29: 当需要为 ripgrep 设置持久默认选项且 shell 别名不适用时，创建或修改 ripgrep 配置文件。
30: 
31: 执行要点：
32: 1. 确认目标：需要持久生效的默认选项，而非临时覆盖。
33: 2. 按配置文件格式逐行写入选项：每一行是一个 shell 参数，写入前去除首尾空白。
34: 3. 以 `#` 开头的行（前面可有任意空白）视为注释并被忽略。
35: 4. 注意没有转义机制：每一行会作为单个命令行参数原样传给 ripgrep，因此不要依赖引号、转义或复杂 shell 语法。
36: 5. 保存后验证默认选项是否按预期生效。
37: 
38: ## Objective
39: 
40: 了解并正确使用 ripgrep 配置文件来设置默认选项
41: ## Applicable Signals
42: 
43: - 需要为 ripgrep 设置持久默认选项
44: - shell 别名不方便或不适用
45: 
46: ## Contraindications
47: 
48: - 需要临时覆盖选项时
49: - 需要转义或复杂 shell 语法时
50: 
51: ## Intervention Moves
52: 
53: - 创建或修改 ripgrep 配置文件
54: - 按行写入 shell 参数形式的选项
55: - 使用 `#` 行添加注释
56: - 验证默认选项生效
57: 
58: ## Workflow Steps
59: 
60: - 确认需要持久化的默认选项
61: - 创建或打开 ripgrep 配置文件
62: - 逐行写入选项，每行一个 shell 参数并去除首尾空白
63: - 用 `#` 开头行添加注释（可选）
64: - 保存并验证默认选项生效
65: 
66: ## Constraints
67: 
68: - 每一行是一个 shell 参数，写入前去除首尾空白
69: - 以 `#` 开头的行（前面可有任意空白）被忽略
70: - 没有转义机制，每行作为单个命令行参数原样传给 ripgrep
71: 
72: ## Cautions
73: 
74: - 不要依赖引号、转义或复杂 shell 语法
75: - 配置文件用于持久默认选项，不适合临时覆盖
76: 
77: ## Output Contract
78: 
79: - 正确创建或修改 ripgrep 配置文件，使默认选项生效
80: 
81: ## Example Therapist Responses
82: 
83: ### Example 1
84: 
85: - Client/Input: 希望 ripgrep 默认忽略大小写并显示行号
86: - Therapist/Output: 在配置文件中逐行写入对应选项，每行一个参数，保存后默认生效
87: - Notes: 每行去除首尾空白，`#` 开头行作为注释
88: 
89: ### Example 2
90: 
91: - Client/Input: 在配置文件中写入带引号或转义的复杂表达式
92: - Therapist/Output: 不适用：配置文件没有转义机制，每行会作为单个参数原样传入
93: - Notes: 复杂 shell 语法应改用其他方式
94: 
95: ## Triggers
96: 
97: - 需要为 ripgrep 设置持久默认选项
98: - shell 别名不方便或不适用
99: 
100: ## Examples
101: 
102: ### Example 1
103: 
104: Input:
105: 
106:   希望 ripgrep 默认忽略大小写并显示行号
107: 
108: Output:
109: 
110:   在配置文件中逐行写入对应选项，每行一个参数，保存后默认生效
111: 
112: Notes:
113: 
114:   每行去除首尾空白，`#` 开头行作为注释
115: 
116: ### Example 2
117: 
118: Input:
119: 
120:   在配置文件中写入带引号或转义的复杂表达式
121: 
122: Output:
123: 
124:   不适用：配置文件没有转义机制，每行会作为单个参数原样传入
125: 
126: Notes:
127: 
128:   复杂 shell 语法应改用其他方式

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\ripgrep-默认编码行为与漏匹配风险判断\SKILL.md

1: ---
2: id: "17838585-2c20-5ed4-9773-850b706e45b4"
3: name: "ripgrep 默认编码行为与漏匹配风险判断"
4: description: "在未显式指定 -E/--encoding 时，判断 ripgrep 默认 --encoding auto 的匹配与转码行为，并评估是否存在漏匹配非 UTF-8 文件的风险。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "encoding"
9:   - "BOM"
10:   - "UTF-16"
11:   - "UTF-8"
12:   - "knowledge_reference"
13: triggers:
14:   - "需要确认默认编码是否会漏匹配非 UTF-8 文件"
15:   - "搜索目标文件可能为 UTF-16 或含 BOM"
16:   - "在未显式指定 -E/--encoding 时评估默认行为"
17: examples:
18:   - input: "搜索目标文件可能为 UTF-16，未指定编码"
19:     output: "默认 --encoding auto 会通过 BOM 嗅探识别 UTF-16 BOM 并转码为 UTF-8 后搜索，但会带来额外性能开销。"
20:     notes: "若文件无 BOM 或为其他编码，需显式指定 -E/--encoding。"
21: ---
22: 
23: # ripgrep 默认编码行为与漏匹配风险判断
24: 
25: 在未显式指定 -E/--encoding 时，判断 ripgrep 默认 --encoding auto 的匹配与转码行为，并评估是否存在漏匹配非 UTF-8 文件的风险。
26: 
27: ## Prompt
28: 
29: 当需要判断 ripgrep 默认编码行为是否满足搜索需求时，使用本参考：确认默认 --encoding auto 假定所有输入为 ASCII 兼容（ASCII、latin1、UTF-8）；说明正则引擎的 Unicode 特性（如 \w、.）假定 UTF-8，遇到非 UTF-8 字节不会匹配；说明默认对文件前三个字节做 BOM 嗅探，若为 UTF-16 BOM 则转码为 UTF-8 后搜索，并伴随性能开销；说明其他编码需通过 -E/--encoding 指定，且除非文件有 BOM，否则假定所有文件均为该编码并执行转码。据此给出默认编码行为与潜在漏匹配风险的判断结论。
30: 
31: ## Objective
32: 
33: 理解并预测 ripgrep 在默认编码设置下的匹配与转码行为
34: ## Applicable Signals
35: 
36: - 未指定 -E/--encoding，使用默认 --encoding auto
37: - 目标文件可能为 UTF-16 或含 BOM
38: - 正则包含 Unicode 特性（如 \w、.）且文件可能非 UTF-8
39: 
40: ## Contraindications
41: 
42: - 已明确指定 -E/--encoding 且需覆盖默认行为时
43: 
44: ## Intervention Moves
45: 
46: - 确认默认假定输入为 ASCII 兼容（ASCII、latin1、UTF-8）
47: - 说明 Unicode 正则特性假定 UTF-8，遇到非 UTF-8 字节不匹配
48: - 说明默认对文件前三个字节做 BOM 嗅探，UTF-16 BOM 触发转码为 UTF-8 后搜索
49: - 说明转码带来额外性能开销
50: - 说明其他编码需通过 -E/--encoding 指定，且除非有 BOM 否则假定所有文件为该编码并转码
51: 
52: ## Workflow Steps
53: 
54: - 确认当前是否使用默认 --encoding auto
55: - 判断目标文件可能的编码类型（ASCII 兼容、UTF-16、其他）
56: - 评估默认行为下是否存在漏匹配风险
57: - 如需覆盖默认行为，改用 -E/--encoding 指定编码
58: 
59: ## Constraints
60: 
61: - 默认 --encoding auto 假定所有输入为 ASCII 兼容
62: - Unicode 正则特性假定 UTF-8，非 UTF-8 字节不会匹配
63: - BOM 嗅探仅读取文件前三个字节
64: - 指定 -E/--encoding 时，除非文件有 BOM，否则假定所有文件均为该编码
65: 
66: ## Cautions
67: 
68: - UTF-16 转码会带来额外性能开销
69: - 若文件包含无效 UTF-16，将用 Unicode 替换码点替代无效码元
70: 
71: ## Output Contract
72: 
73: - 对默认编码行为与潜在漏匹配风险的判断结论
74: 
75: ## Example Therapist Responses
76: 
77: ### Example 1
78: 
79: - Client/Input: 搜索目标文件可能为 UTF-16，未指定编码
80: - Therapist/Output: 默认 --encoding auto 会通过 BOM 嗅探识别 UTF-16 BOM 并转码为 UTF-8 后搜索，但会带来额外性能开销。
81: - Notes: 若文件无 BOM 或为其他编码，需显式指定 -E/--encoding。
82: 
83: ## Triggers
84: 
85: - 需要确认默认编码是否会漏匹配非 UTF-8 文件
86: - 搜索目标文件可能为 UTF-16 或含 BOM
87: - 在未显式指定 -E/--encoding 时评估默认行为
88: 
89: ## Examples
90: 
91: ### Example 1
92: 
93: Input:
94: 
95:   搜索目标文件可能为 UTF-16，未指定编码
96: 
97: Output:
98: 
99:   默认 --encoding auto 会通过 BOM 嗅探识别 UTF-16 BOM 并转码为 UTF-8 后搜索，但会带来额外性能开销。
100: 
101: Notes:
102: 
103:   若文件无 BOM 或为其他编码，需显式指定 -E/--encoding。

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\二进制搜索安全警告\SKILL.md

1: ---
2: id: "333103a1-0dae-5e40-b77d-50779da67cef"
3: name: "二进制搜索安全警告"
4: description: "在使用 --text（-a）搜索二进制文件时，提醒用户二进制文件可能向终端输出控制字符，导致终端出现异常行为。适用于任何启用二进制搜索的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "二进制搜索"
9:   - "安全警告"
10:   - "终端风险"
11: triggers:
12:   - "用户计划使用 --text 或 -a 搜索二进制文件"
13:   - "搜索命令涉及二进制内容且启用了文本模式"
14: examples:
15:   - input: "用户计划使用 --text 搜索二进制文件"
16:     output: "警告：二进制文件可能向终端输出控制字符，可能导致终端异常行为，请谨慎使用该标志并采取适当预防措施。"
17: ---
18: 
19: # 二进制搜索安全警告
20: 
21: 在使用 --text（-a）搜索二进制文件时，提醒用户二进制文件可能向终端输出控制字符，导致终端出现异常行为。适用于任何启用二进制搜索的场景。
22: 
23: ## Prompt
24: 
25: 当调用方计划使用 --text 或 -a 搜索二进制文件时，先给出明确风险警告：二进制文件可能向终端输出控制字符，可能导致终端出现异常行为。提醒用户谨慎使用该标志，并建议采取适当预防措施后再执行搜索。
26: 
27: ## Objective
28: 
29: 防止因搜索二进制文件而导致的终端控制字符风险。
30: ## Applicable Signals
31: 
32: - 用户计划使用 --text 或 -a 搜索二进制文件
33: - 命令中同时出现二进制目标与文本模式标志
34: 
35: ## Contraindications
36: 
37: - 不涉及二进制文件搜索
38: - 未启用 --text 或 -a 的普通文本搜索
39: 
40: ## Intervention Moves
41: 
42: - 在启用二进制搜索前发出明确风险警告
43: - 说明二进制文件可能输出控制字符并导致终端异常行为
44: - 建议用户采取适当预防措施后再执行
45: 
46: ## Workflow Steps
47: 
48: - 识别调用方是否计划使用 --text 或 -a 搜索二进制文件
49: - 发出风险警告：二进制文件可能向终端输出控制字符，可能导致终端异常行为
50: - 提示用户谨慎使用该标志并采取适当预防措施
51: - 在用户确认或采取预防措施后再继续搜索
52: 
53: ## Constraints
54: 
55: - 仅在启用二进制搜索（--text 或 -a）时触发
56: - 警告必须明确说明控制字符与终端异常行为的风险
57: 
58: ## Cautions
59: 
60: - 二进制文件可能输出控制字符，导致终端出现异常行为
61: - 使用 --text 或 -a 时需谨慎
62: 
63: ## Output Contract
64: 
65: - 用户被明确警告二进制搜索的潜在风险，并采取适当预防措施。
66: 
67: ## Example Therapist Responses
68: 
69: ### Example 1
70: 
71: - Client/Input: 用户计划使用 --text 搜索二进制文件
72: - Therapist/Output: 警告：二进制文件可能向终端输出控制字符，可能导致终端异常行为，请谨慎使用该标志并采取适当预防措施。
73: 
74: ## Triggers
75: 
76: - 用户计划使用 --text 或 -a 搜索二进制文件
77: - 搜索命令涉及二进制内容且启用了文本模式
78: 
79: ## Examples
80: 
81: ### Example 1
82: 
83: Input:
84: 
85:   用户计划使用 --text 搜索二进制文件
86: 
87: Output:
88: 
89:   警告：二进制文件可能向终端输出控制字符，可能导致终端异常行为，请谨慎使用该标志并采取适当预防措施。

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\启用隐藏文件与二进制搜索\SKILL.md

1: ---
2: id: "088793ac-d485-536e-ad5b-2089c759e532"
3: name: "启用隐藏文件与二进制搜索"
4: description: "使用 --hidden（-.）搜索隐藏文件与目录，使用 --text（-a）搜索二进制文件，并在启用 --text 时注意二进制文件可能向终端输出控制字符的风险。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "搜索范围扩展"
9:   - "标志启用"
10:   - "隐藏文件"
11:   - "二进制文件"
12: triggers:
13:   - "需要搜索隐藏文件或目录"
14:   - "需要搜索二进制文件内容"
15: examples:
16:   - input: "需要搜索隐藏目录中的匹配内容"
17:     output: "使用 --hidden（-.）标志执行搜索并返回隐藏文件中的匹配结果"
18:     notes: "突破默认隐藏文件过滤"
19:   - input: "需要搜索二进制文件中的匹配内容"
20:     output: "使用 --text（-a）标志执行搜索并返回二进制文件中的匹配结果"
21:     notes: "注意二进制文件可能输出控制字符"
22: ---
23: 
24: # 启用隐藏文件与二进制搜索
25: 
26: 使用 --hidden（-.）搜索隐藏文件与目录，使用 --text（-a）搜索二进制文件，并在启用 --text 时注意二进制文件可能向终端输出控制字符的风险。
27: 
28: ## Prompt
29: 
30: 当需要突破 ripgrep 默认过滤以搜索隐藏文件或二进制文件时：
31: 1. 搜索隐藏文件与目录：使用 --hidden（短标志 -.）。
32: 2. 搜索二进制文件：使用 --text（短标志 -a）。
33: 3. 使用 --text 时须谨慎：二进制文件可能向终端输出控制字符，导致终端行为异常。
34: 仅在确有需要时启用这些标志，避免无谓地扩大搜索范围。
35: 
36: ## Objective
37: 
38: 在需要时安全地启用隐藏文件或二进制文件搜索。
39: ## Applicable Signals
40: 
41: - 默认搜索未覆盖隐藏文件或目录
42: - 默认搜索跳过二进制文件
43: 
44: ## Contraindications
45: 
46: - 不需要搜索隐藏或二进制文件
47: - 终端环境无法安全处理控制字符
48: 
49: ## Intervention Moves
50: 
51: - 添加 --hidden（-.）以搜索隐藏文件与目录
52: - 添加 --text（-a）以搜索二进制文件
53: - 在使用 --text 前评估终端对控制字符的承受能力
54: 
55: ## Workflow Steps
56: 
57: - 确认当前搜索确实需要覆盖隐藏文件或二进制文件
58: - 对隐藏文件搜索添加 --hidden（-.）
59: - 对二进制文件搜索添加 --text（-a）
60: - 在启用 --text 时留意终端可能出现的控制字符输出
61: 
62: ## Constraints
63: 
64: - 仅在确有需要时启用这些标志
65: - 使用 --text 时须意识到二进制文件可能输出控制字符
66: 
67: ## Cautions
68: 
69: - 二进制文件可能向终端输出控制字符，可能导致终端行为异常
70: 
71: ## Output Contract
72: 
73: - 成功搜索到隐藏文件或二进制文件中的匹配内容。
74: 
75: ## Example Therapist Responses
76: 
77: ### Example 1
78: 
79: - Client/Input: 需要搜索隐藏目录中的匹配内容
80: - Therapist/Output: 使用 --hidden（-.）标志执行搜索并返回隐藏文件中的匹配结果
81: - Notes: 突破默认隐藏文件过滤
82: 
83: ### Example 2
84: 
85: - Client/Input: 需要搜索二进制文件中的匹配内容
86: - Therapist/Output: 使用 --text（-a）标志执行搜索并返回二进制文件中的匹配结果
87: - Notes: 注意二进制文件可能输出控制字符
88: 
89: ## Triggers
90: 
91: - 需要搜索隐藏文件或目录
92: - 需要搜索二进制文件内容
93: 
94: ## Examples
95: 
96: ### Example 1
97: 
98: Input:
99: 
100:   需要搜索隐藏目录中的匹配内容
101: 
102: Output:
103: 
104:   使用 --hidden（-.）标志执行搜索并返回隐藏文件中的匹配结果
105: 
106: Notes:
107: 
108:   突破默认隐藏文件过滤
109: 
110: ### Example 2
111: 
112: Input:
113: 
114:   需要搜索二进制文件中的匹配内容
115: 
116: Output:
117: 
118:   使用 --text（-a）标志执行搜索并返回二进制文件中的匹配结果
119: 
120: Notes:
121: 
122:   注意二进制文件可能输出控制字符

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\手动过滤-glob-与文件类型\SKILL.md

1: ---
2: id: "53070b07-3563-58f9-b86e-13f7ccdf58ba"
3: name: "手动过滤：glob 与文件类型"
4: description: "通过 glob 模式或文件类型选项手动控制 ripgrep 搜索包含或排除的文件范围。适用于自动过滤不满足需求、需要精确指定文件集合的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "手动过滤"
9:   - "glob"
10:   - "文件类型"
11:   - "搜索范围限定"
12: triggers:
13:   - "用户需要仅搜索特定扩展名或路径模式的文件"
14:   - "自动过滤规则排除了用户实际需要搜索的文件"
15:   - "需要按文件类型包含或排除搜索范围"
16: examples:
17:   - input: "需要仅在 src 目录下搜索特定模式"
18:     output: "rg 'pattern' src"
19:     notes: "通过指定目录限定搜索范围"
20:   - input: "需要按文件类型限定搜索"
21:     output: "使用 -t/--type 指定类型或 -T/--type-not 排除类型"
22:     notes: "文件类型选项可精确控制搜索的文件集合"
23: ---
24: 
25: # 手动过滤：glob 与文件类型
26: 
27: 通过 glob 模式或文件类型选项手动控制 ripgrep 搜索包含或排除的文件范围。适用于自动过滤不满足需求、需要精确指定文件集合的场景。
28: 
29: ## Prompt
30: 
31: 当默认自动过滤无法满足搜索需求时，使用 glob 模式或文件类型选项手动限定 ripgrep 的搜索文件集合。
32: 
33: 执行步骤：
34: 1. 确认默认自动过滤（.gitignore/.ignore/.rgignore、隐藏文件、二进制文件、符号链接）是否已排除用户实际需要搜索的文件。
35: 2. 若需要按路径模式限定，使用 glob 选项（如 -g/--glob）指定包含或排除模式。
36: 3. 若需要按文件类型限定，使用文件类型选项（如 -t/--type 指定类型，-T/--type-not 排除类型）。
37: 4. 注意特殊文件类型 `all` 的语义，按需使用。
38: 5. 运行搜索并确认结果范围已精确限定到符合 glob 或文件类型条件的文件。
39: 
40: 注意：glob 与文件类型选项可组合使用以进一步收窄范围。
41: 
42: ## Objective
43: 
44: 使用 glob 或文件类型参数精确限定搜索文件集合
45: ## Applicable Signals
46: 
47: - 默认自动过滤排除了用户实际需要搜索的文件
48: - 用户明确描述目标文件的扩展名或路径模式
49: - 需要按文件类型包含或排除搜索范围
50: 
51: ## Contraindications
52: 
53: - 默认自动过滤已满足需求且无需额外限定
54: - 用户无法明确描述目标文件模式
55: 
56: ## Intervention Moves
57: 
58: - 使用 glob 选项（-g/--glob）指定包含或排除的路径模式
59: - 使用文件类型选项（-t/--type 包含，-T/--type-not 排除）限定文件类型
60: - 组合 glob 与文件类型选项进一步收窄搜索范围
61: - 使用特殊文件类型 `all` 覆盖默认类型过滤
62: 
63: ## Workflow Steps
64: 
65: - 确认默认自动过滤是否排除了用户实际需要搜索的文件
66: - 根据需求选择 glob 模式或文件类型选项
67: - 使用 -g/--glob 指定路径包含或排除模式
68: - 使用 -t/--type 或 -T/--type-not 指定或排除文件类型
69: - 运行搜索并确认结果范围已精确限定
70: 
71: ## Constraints
72: 
73: - glob 与文件类型选项可组合使用以进一步收窄范围
74: - 需理解特殊文件类型 `all` 的语义后再使用
75: 
76: ## Cautions
77: 
78: - 过度限定搜索范围可能遗漏用户实际需要的文件
79: - glob 模式与文件类型选项的优先级和交互需注意
80: 
81: ## Output Contract
82: 
83: - 搜索范围被精确限定到符合 glob 或文件类型条件的文件
84: 
85: ## Example Therapist Responses
86: 
87: ### Example 1
88: 
89: - Client/Input: 需要仅在 src 目录下搜索特定模式
90: - Therapist/Output: rg 'pattern' src
91: - Notes: 通过指定目录限定搜索范围
92: 
93: ### Example 2
94: 
95: - Client/Input: 需要按文件类型限定搜索
96: - Therapist/Output: 使用 -t/--type 指定类型或 -T/--type-not 排除类型
97: - Notes: 文件类型选项可精确控制搜索的文件集合
98: 
99: ## Triggers
100: 
101: - 用户需要仅搜索特定扩展名或路径模式的文件
102: - 自动过滤规则排除了用户实际需要搜索的文件
103: - 需要按文件类型包含或排除搜索范围
104: 
105: ## Examples
106: 
107: ### Example 1
108: 
109: Input:
110: 
111:   需要仅在 src 目录下搜索特定模式
112: 
113: Output:
114: 
115:   rg 'pattern' src
116: 
117: Notes:
118: 
119:   通过指定目录限定搜索范围
120: 
121: ### Example 2
122: 
123: Input:
124: 
125:   需要按文件类型限定搜索
126: 
127: Output:
128: 
129:   使用 -t/--type 指定类型或 -T/--type-not 排除类型
130: 
131: Notes:
132: 
133:   文件类型选项可精确控制搜索的文件集合

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\指定编码搜索非-utf-8-文件\SKILL.md

1: ---
2: id: "1efdc8b0-83a3-5986-bbce-022f17e507e2"
3: name: "指定编码搜索非 UTF-8 文件"
4: description: "使用 -E/--encoding 指定编码（如 none）并配合 -a 搜索非 UTF-8 或 UTF-16 文件，必要时用 (?-u) 关闭 Unicode 模式以匹配原始字节。适用于目标文件为 UTF-16 或其他非 UTF-8 编码、或需要按原始字节序列匹配的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "encoding"
9:   - "non-utf8"
10:   - "byte-matching"
11:   - "micro-skill"
12: triggers:
13:   - "目标文件为 UTF-16 或其他非 UTF-8 编码"
14:   - "需要按原始字节序列匹配"
15:   - "默认 BOM sniffing 或 UTF-8 假设无法得到预期匹配"
16: examples:
17:   - input: "rg '(?-u)\\(\\x045\\x04@\\x04;\\x04>\\x04:\\x04' -E none -a some-utf16-file"
18:     output: "在指定编码 none 下按原始字节匹配并返回结果"
19:     notes: "使用 (?-u) 关闭 Unicode 模式，-E none 指定编码，-a 处理非文本文件"
20: ---
21: 
22: # 指定编码搜索非 UTF-8 文件
23: 
24: 使用 -E/--encoding 指定编码（如 none）并配合 -a 搜索非 UTF-8 或 UTF-16 文件，必要时用 (?-u) 关闭 Unicode 模式以匹配原始字节。适用于目标文件为 UTF-16 或其他非 UTF-8 编码、或需要按原始字节序列匹配的场景。
25: 
26: ## Prompt
27: 
28: 当目标文件不是 UTF-8（例如 UTF-16）或需要按原始字节序列匹配时，使用 -E/--encoding 指定编码，并配合 -a 处理二进制/非文本文件；若需按原始字节匹配，则在模式前加 (?-u) 关闭 Unicode 模式。执行后确认在指定编码下返回正确匹配结果。
29: 
30: ## Objective
31: 
32: 在非 UTF-8 编码文件中正确执行字节级或转码级搜索
33: ## Applicable Signals
34: 
35: - 文件为 UTF-16 或其他非 UTF-8 编码
36: - 需要按原始字节序列匹配
37: - 默认编码假设导致匹配失败
38: 
39: ## Contraindications
40: 
41: - 文件为普通 UTF-8 且无需字节级匹配时
42: 
43: ## Intervention Moves
44: 
45: - 使用 -E/--encoding 指定编码（如 none）
46: - 配合 -a 处理非文本/二进制文件
47: - 必要时在模式前加 (?-u) 关闭 Unicode 模式以匹配原始字节
48: 
49: ## Workflow Steps
50: 
51: - 确认目标文件编码为非 UTF-8（如 UTF-16）或需要字节级匹配
52: - 使用 -E/--encoding 指定编码，必要时用 none
53: - 配合 -a 以处理非文本文件
54: - 若需按原始字节匹配，在模式前加 (?-u) 关闭 Unicode 模式
55: - 执行搜索并确认返回正确匹配结果
56: 
57: ## Constraints
58: 
59: - 指定编码后 ripgrep 会假定所有搜索文件均为该编码（除非文件带 BOM）
60: - 转码会带来额外性能开销
61: 
62: ## Cautions
63: 
64: - 转码步骤会增加性能开销
65: - 若文件包含无效 UTF-16，将替换为 Unicode 替换码点
66: 
67: ## Output Contract
68: 
69: - 在指定编码下返回正确匹配结果
70: 
71: ## Example Therapist Responses
72: 
73: ### Example 1
74: 
75: - Client/Input: rg '(?-u)\(\x045\x04@\x04;\x04>\x04:\x04' -E none -a some-utf16-file
76: - Therapist/Output: 在指定编码 none 下按原始字节匹配并返回结果
77: - Notes: 使用 (?-u) 关闭 Unicode 模式，-E none 指定编码，-a 处理非文本文件
78: 
79: ## Triggers
80: 
81: - 目标文件为 UTF-16 或其他非 UTF-8 编码
82: - 需要按原始字节序列匹配
83: - 默认 BOM sniffing 或 UTF-8 假设无法得到预期匹配
84: 
85: ## Examples
86: 
87: ### Example 1
88: 
89: Input:
90: 
91:   rg '(?-u)\(\x045\x04@\x04;\x04>\x04:\x04' -E none -a some-utf16-file
92: 
93: Output:
94: 
95:   在指定编码 none 下按原始字节匹配并返回结果
96: 
97: Notes:
98: 
99:   使用 (?-u) 关闭 Unicode 模式，-E none 指定编码，-a 处理非文本文件

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\按文件类型过滤搜索\SKILL.md

1: ---
2: id: "67355610-8f2e-500b-9ff9-3fd12fe37c8e"
3: name: "按文件类型过滤搜索"
4: description: "使用 ripgrep 内置或自定义文件类型（-t/-T、--type-add）来包含或排除特定类型文件，替代重复书写 glob，稳定限定搜索文件集合。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "文件类型过滤"
9:   - "搜索范围"
10:   - "type-add"
11:   - "type-list"
12: triggers:
13:   - "用户反复对同一类文件（如 Rust、C、web 文件）执行搜索"
14:   - "需要排除某类文件而非逐个写 glob"
15:   - "需要查看或定义 ripgrep 文件类型"
16: examples:
17:   - input: "反复搜索 Rust 文件中的 'fn run'"
18:     output: "rg 'fn run' -trust"
19:     notes: "用内置 rust 类型替代 -g '*.rs'"
20:   - input: "搜索 C 文件中的 'int main'"
21:     output: "rg 'int main' -tc"
22:     notes: "用内置 c 类型替代 -g '*.{c,h}'"
23:   - input: "搜索 web 文件（html/css/js）中的 'title'"
24:     output: "rg --type-add 'web:*.{html,css,js}' -tweb title"
25:     notes: "自定义类型仅对当前命令生效"
26: ---
27: 
28: # 按文件类型过滤搜索
29: 
30: 使用 ripgrep 内置或自定义文件类型（-t/-T、--type-add）来包含或排除特定类型文件，替代重复书写 glob，稳定限定搜索文件集合。
31: 
32: ## Prompt
33: 
34: 当用户反复对同一类文件执行搜索，或需要排除某类文件而非逐个写 glob 时，使用文件类型过滤来稳定限定搜索文件集合。
35: 
36: 执行步骤：
37: 1. 判断目标文件类型是否属于 ripgrep 内置类型；可用 `rg --type-list` 查看类型及其对应 glob。
38: 2. 若为内置类型，使用 `-t<type>`（如 `-trust`、`-tc`）包含该类型文件，或使用 `-T<type>`（如 `-Trust`）排除该类型文件。
39: 3. 若目标类型不存在，使用 `--type-add '<name>:<glob>'` 定义自定义类型，再用 `-t<name>` 应用；多个 glob 可合并为 `*.{ext1,ext2}` 形式。
40: 4. 注意 `--type-add` 仅对当前命令生效，不会持久保存；如需跨命令复用，应改用 shell alias 或配置文件。
41: 5. 确认命令能正确包含/排除目标文件类型后交付。
42: 
43: ## Objective
44: 
45: 用文件类型过滤替代重复 glob，稳定限定搜索文件集合
46: ## Applicable Signals
47: 
48: - 用户反复对同一类文件（如 Rust、C、web 文件）执行搜索
49: - 需要排除某类文件而非逐个写 glob
50: 
51: ## Contraindications
52: 
53: - 只需一次性简单 glob 过滤
54: - 需要跨命令持久保存自定义类型（应改用 shell alias 或配置文件）
55: 
56: ## Intervention Moves
57: 
58: - 用 `rg --type-list` 查看内置类型及其 glob
59: - 用 `-t<type>` 包含指定类型文件
60: - 用 `-T<type>` 排除指定类型文件
61: - 用 `--type-add '<name>:<glob>'` 定义自定义类型并配合 `-t<name>` 应用
62: 
63: ## Workflow Steps
64: 
65: - 判断目标文件类型是否为 ripgrep 内置类型，必要时用 `rg --type-list` 查看
66: - 内置类型：使用 `-t<type>` 包含或 `-T<type>` 排除
67: - 非内置类型：使用 `--type-add '<name>:<glob>'` 定义，再用 `-t<name>` 应用
68: - 确认 `--type-add` 仅对当前命令生效，如需持久化改用 shell alias 或配置文件
69: - 验证命令能正确包含/排除目标文件类型
70: 
71: ## Constraints
72: 
73: - `--type-add` 只对当前命令生效，不会持久保存
74: - `-t` 表示包含该类型文件，`-T` 表示排除该类型文件
75: 
76: ## Cautions
77: 
78: - 若需要跨命令复用自定义类型，不要依赖 `--type-add`，应改用 shell alias 或配置文件
79: 
80: ## Output Contract
81: 
82: - 一条使用 -t/-T 或 --type-add 的 rg 命令，能正确包含/排除目标文件类型
83: 
84: ## Example Therapist Responses
85: 
86: ### Example 1
87: 
88: - Client/Input: 反复搜索 Rust 文件中的 'fn run'
89: - Therapist/Output: rg 'fn run' -trust
90: - Notes: 用内置 rust 类型替代 -g '*.rs'
91: 
92: ### Example 2
93: 
94: - Client/Input: 搜索 C 文件中的 'int main'
95: - Therapist/Output: rg 'int main' -tc
96: - Notes: 用内置 c 类型替代 -g '*.{c,h}'
97: 
98: ### Example 3
99: 
100: - Client/Input: 搜索 web 文件（html/css/js）中的 'title'
101: - Therapist/Output: rg --type-add 'web:*.{html,css,js}' -tweb title
102: - Notes: 自定义类型仅对当前命令生效
103: 
104: ## Triggers
105: 
106: - 用户反复对同一类文件（如 Rust、C、web 文件）执行搜索
107: - 需要排除某类文件而非逐个写 glob
108: - 需要查看或定义 ripgrep 文件类型
109: 
110: ## Examples
111: 
112: ### Example 1
113: 
114: Input:
115: 
116:   反复搜索 Rust 文件中的 'fn run'
117: 
118: Output:
119: 
120:   rg 'fn run' -trust
121: 
122: Notes:
123: 
124:   用内置 rust 类型替代 -g '*.rs'
125: 
126: ### Example 2
127: 
128: Input:
129: 
130:   搜索 C 文件中的 'int main'
131: 
132: Output:
133: 
134:   rg 'int main' -tc
135: 
136: Notes:
137: 
138:   用内置 c 类型替代 -g '*.{c,h}'
139: 
140: ### Example 3
141: 
142: Input:
143: 
144:   搜索 web 文件（html/css/js）中的 'title'
145: 
146: Output:
147: 
148:   rg --type-add 'web:*.{html,css,js}' -tweb title
149: 
150: Notes:
151: 
152:   自定义类型仅对当前命令生效

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\递归搜索与路径限定\SKILL.md

1: ---
2: id: "bc7ca9e9-ff78-5700-9df3-2ff04282a3d9"
3: name: "递归搜索与路径限定"
4: description: "使用 ripgrep 在当前目录或指定目录下递归搜索模式，并通过显式路径参数将搜索范围限定到目标目录。适用于需要快速定位代码或文本匹配且希望控制搜索根目录的场景。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "递归搜索"
9:   - "路径限定"
10:   - "基础搜索"
11: triggers:
12:   - "用户需要在当前目录或子目录中查找匹配模式"
13:   - "用户希望将搜索限制在某个特定目录而非整个仓库"
14:   - "需要快速定位代码或文本匹配并控制搜索根目录"
15: examples:
16:   - input: "rg 'fn write\\('"
17:     output: "在 src 与 termcolor 目录中返回匹配文件路径、行号及匹配行内容"
18:     notes: "未指定路径时默认搜索当前目录"
19:   - input: "rg 'fn write\\(' src"
20:     output: "src/printer.rs\n469:    fn write(&mut self, buf: &[u8]) {"
21:     notes: "显式路径将搜索限制在 src 目录"
22:   - input: "rg -F 'fn write('"
23:     output: "按字面字符串匹配，效果等同于转义后的正则"
24:     notes: "-F 将模式解释为字面字符串"
25: ---
26: 
27: # 递归搜索与路径限定
28: 
29: 使用 ripgrep 在当前目录或指定目录下递归搜索模式，并通过显式路径参数将搜索范围限定到目标目录。适用于需要快速定位代码或文本匹配且希望控制搜索根目录的场景。
30: 
31: ## Prompt
32: 
33: 当需要在当前目录或子目录中查找匹配模式，或希望将搜索限制在某个特定目录而非整个仓库时，使用 ripgrep 执行递归搜索。
34: 
35: 执行步骤：
36: 1. 确认搜索模式（pattern）与目标根目录。
37: 2. 若未指定路径，ripgrep 默认搜索当前目录，即 `rg foo` 等价于 `rg foo ./`。
38: 3. 若需限定范围，在模式后显式给出目录，例如 `rg 'fn write\(' src`，将搜索限制在 `src` 目录。
39: 4. 若模式包含正则特殊字符（如 `(`），需转义，或使用 `-F` 将模式解释为字面字符串，例如 `rg -F 'fn write('`。
40: 5. 返回匹配文件路径、行号及匹配行内容。
41: 
42: 注意：默认情况下 ripgrep 会自动过滤 .gitignore/.ignore/.rgignore 匹配项、隐藏文件与目录、二进制文件（含 NUL 字节），且不跟随符号链接；这些行为可通过相应标志切换。
43: 
44: ## Objective
45: 
46: 在指定目录范围内执行递归模式搜索并返回匹配文件与行号
47: ## Applicable Signals
48: 
49: - 需要在当前目录或子目录中查找匹配模式
50: - 希望将搜索限制在某个特定目录而非整个仓库
51: 
52: ## Contraindications
53: 
54: - 需要跨多个不相关根目录搜索且无法用单一路径表达
55: - 搜索目标是非文本二进制数据且未启用相应处理
56: 
57: ## Intervention Moves
58: 
59: - 未指定路径时默认搜索当前目录（rg foo 等价于 rg foo ./）
60: - 在模式后显式给出目录以限定搜索范围（rg 'fn write\(' src）
61: - 对含正则特殊字符的模式进行转义，或使用 -F 按字面字符串匹配
62: 
63: ## Workflow Steps
64: 
65: - 确认搜索模式与目标根目录
66: - 未指定路径时默认搜索当前目录
67: - 需要限定时在模式后显式给出目录
68: - 对含正则特殊字符的模式转义或使用 -F
69: - 返回匹配文件路径、行号及匹配行内容
70: 
71: ## Constraints
72: 
73: - 默认自动过滤 .gitignore/.ignore/.rgignore 匹配项、隐藏文件与目录、二进制文件，且不跟随符号链接
74: - 这些默认过滤行为可通过相应标志切换
75: 
76: ## Cautions
77: 
78: - 模式中的正则特殊字符需转义，否则可能产生非预期匹配
79: - 二进制文件默认被忽略，如需搜索需启用相应处理
80: 
81: ## Output Contract
82: 
83: - 返回匹配文件路径、行号及匹配行内容
84: 
85: ## Example Therapist Responses
86: 
87: ### Example 1
88: 
89: - Client/Input: rg 'fn write\('
90: - Therapist/Output: 在 src 与 termcolor 目录中返回匹配文件路径、行号及匹配行内容
91: - Notes: 未指定路径时默认搜索当前目录
92: 
93: ### Example 2
94: 
95: - Client/Input: rg 'fn write\(' src
96: - Therapist/Output: src/printer.rs
97: 469:    fn write(&mut self, buf: &[u8]) {
98: - Notes: 显式路径将搜索限制在 src 目录
99: 
100: ### Example 3
101: 
102: - Client/Input: rg -F 'fn write('
103: - Therapist/Output: 按字面字符串匹配，效果等同于转义后的正则
104: - Notes: -F 将模式解释为字面字符串
105: 
106: ## Triggers
107: 
108: - 用户需要在当前目录或子目录中查找匹配模式
109: - 用户希望将搜索限制在某个特定目录而非整个仓库
110: - 需要快速定位代码或文本匹配并控制搜索根目录
111: 
112: ## Examples
113: 
114: ### Example 1
115: 
116: Input:
117: 
118:   rg 'fn write\('
119: 
120: Output:
121: 
122:   在 src 与 termcolor 目录中返回匹配文件路径、行号及匹配行内容
123: 
124: Notes:
125: 
126:   未指定路径时默认搜索当前目录
127: 
128: ### Example 2
129: 
130: Input:
131: 
132:   rg 'fn write\(' src
133: 
134: Output:
135: 
136:   src/printer.rs
137:   469:    fn write(&mut self, buf: &[u8]) {
138: 
139: Notes:
140: 
141:   显式路径将搜索限制在 src 目录
142: 
143: ### Example 3
144: 
145: Input:
146: 
147:   rg -F 'fn write('
148: 
149: Output:
150: 
151:   按字面字符串匹配，效果等同于转义后的正则
152: 
153: Notes:
154: 
155:   -F 将模式解释为字面字符串

# D:\AS\AutoSkill-main\degradation_failure_lab\runs\case005_ripgrep_guide\clean\r64cee24fae18\SkillBank\Users\docskill\预处理器配置与使用流程\SKILL.md

1: ---
2: id: "2776509a-ba61-5ae0-b356-5714fc16123e"
3: name: "预处理器配置与使用流程"
4: description: "定义并运行预处理器命令，将任意文件内容转换为文本后再由 ripgrep 搜索，从而扩展可搜索的内容类型。当需要搜索无法直接读取的二进制或专有格式文件，或希望在不修改 ripgrep 核心的情况下扩展搜索能力时使用。"
5: version: "0.1.0"
6: tags:
7:   - "ripgrep"
8:   - "preprocessor"
9:   - "content-conversion"
10:   - "search"
11: triggers:
12:   - "需要搜索无法直接读取的二进制或专有格式文件"
13:   - "希望在不修改 ripgrep 核心的情况下扩展搜索能力"
14: ---
15: 
16: # 预处理器配置与使用流程
17: 
18: 定义并运行预处理器命令，将任意文件内容转换为文本后再由 ripgrep 搜索，从而扩展可搜索的内容类型。当需要搜索无法直接读取的二进制或专有格式文件，或希望在不修改 ripgrep 核心的情况下扩展搜索能力时使用。
19: 
20: ## Prompt
21: 
22: 在搜索前为 ripgrep 配置预处理器：指定一个可将每个文件输入转换为文本的命令，使 ripgrep 能够搜索原本无法直接读取的内容。执行时先确认预处理器命令可用且安全，再将其接入 ripgrep 搜索流程，最后验证转换后的文本可被正常搜索到。
23: 
24: ## Objective
25: 
26: 通过预处理器将非文本内容转换为可搜索文本
27: ## Applicable Signals
28: 
29: - 目标文件为二进制或专有格式，无法被 ripgrep 直接读取
30: - 需要扩展 ripgrep 可搜索的内容类型
31: 
32: ## Contraindications
33: 
34: - 文件本身已是纯文本
35: - 预处理器命令不可用或存在安全风险
36: 
37: ## Intervention Moves
38: 
39: - 定义可将每个文件输入转换为文本的预处理器命令
40: - 将预处理器接入 ripgrep 搜索流程
41: - 验证转换后的文本可被搜索到
42: 
43: ## Workflow Steps
44: 
45: - 确认目标内容无法被 ripgrep 直接读取，需要预处理器转换
46: - 定义预处理器命令，使其将每个文件输入转换为文本
47: - 将预处理器接入 ripgrep 搜索流程
48: - 运行搜索并验证转换后的文本可被搜索到
49: 
50: ## Constraints
51: 
52: - 预处理器命令必须可用
53: - 预处理器命令不得存在安全风险
54: 
55: ## Cautions
56: 
57: - 预处理器会作用于每个被搜索文件的输入，需确保其行为符合预期
58: 
59: ## Output Contract
60: 
61: - 预处理器成功转换文件内容，ripgrep 能搜索到转换后的文本
62: 
63: ## Triggers
64: 
65: - 需要搜索无法直接读取的二进制或专有格式文件
66: - 希望在不修改 ripgrep 核心的情况下扩展搜索能力