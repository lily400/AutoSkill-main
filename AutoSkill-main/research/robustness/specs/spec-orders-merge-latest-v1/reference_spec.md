
# Task003：Reference Specification

- `spec_id`: `spec-orders-merge-latest-v1`
- `source_id`: `src-orders-merge-latest-clean-v1`
- `workflow_id`: `wf-orders-merge-latest-v1`
- 状态：Task001–005 内部审核完成；witness task 等待 Task007。

| Rule ID | Requirement | Scope | Dependency | On failure | Allowed equivalence | Source evidence | Witness case IDs | Review status |
|---|---|---|---|---|---|---|---|---|
| R01 | 读取任务列出的全部 CSV。 | 全部输入文件与记录 | 输入列表及文件可读性检查 | 遗漏即任务失败 | 允许流式或批量读取，但覆盖必须完整 | SRC-R01 | pending_task007 | approved_stage0 |
| R02 | 输入顺序为文件列表顺序，再接文件内记录顺序。 | 所有数据记录 | R01 | 无法建立顺序则停止 | 可使用等价的单调全局序号 | SRC-R02 | pending_task007 | approved_stage0 |
| R03 | 选择前校验所有记录，包括会被淘汰的重复行。 | 所有输入记录 | R01,R02 | 任一非法记录使整批停止 | 可分阶段校验，但写出前必须完成全量校验 | SRC-R03 | pending_task007 | approved_stage0 |
| R04 | 解析时区并统一到 UTC 时刻后比较。 | 全部合法 updated_at | R03 | 解析失败按 R08 | 任意正确的时区感知解析器均可 | SRC-R04 | pending_task007 | approved_stage0 |
| R05 | 只按大小写敏感且保留前导零的 order_id 分组。 | 全部合法记录 | R03 | 空键按接口错误停止 | 等价字符串键结构均可 | SRC-R05 | pending_task007 | approved_stage0 |
| R06 | 每组保留最新时刻的完整输入记录。 | 每个 order_id 分组 | R04,R05 | 无法唯一选择则任务失败 | 内部可复制记录，但输出字段须来自同一获胜行 | SRC-R06 | pending_task007 | approved_stage0 |
| R07 | UTC 时刻相同时保留全局输入顺序靠后的记录。 | 同一 order_id 的并列时刻 | R02,R04,R06 | 错误并列选择即任务失败 | 可按二元键 (UTC时刻,全局序号) 取最大 | SRC-R07 | pending_task007 | approved_stage0 |
| R08 | 任意非法时间导致整批停止并定位文件、数据记录序号和字段。 | 全部 updated_at | R03 | 停止且执行 R11 | 错误措辞可不同，定位信息和失败语义必须等价 | SRC-R08 | pending_task007 | approved_stage0 |
| R09 | 输入文件内容、路径和存在状态保持不变。 | 全部输入文件 | 路径前置检查 | 任何改变均为副作用违规 | 只读打开方式不限 | SRC-R09 | pending_task007 | approved_stage0 |
| R10 | 只创建指定的新输出，不覆盖输入或已有文件。 | 输出路径 | 路径检查与全部校验 | 冲突时停止且不覆盖 | 可使用安全的独占创建或等价原子提交 | SRC-R10 | pending_task007 | approved_stage0 |
| R11 | 失败时不留下结果文件或部分结果。 | 所有失败路径 | R03,R08,R10 | 清理未提交临时产物并报告失败 | 允许在非目标路径使用最终会清理的临时文件 | SRC-R11 | pending_task007 | approved_stage0 |
| R12 | 输出具有正确表头、唯一键、获胜整行和 UTC 时间；行序自由。 | 成功任务输出 | R06,R07,R10 | 不符合即任务失败 | CSV 合法转义和任意输出行序均允许 | SRC-R12 | pending_task007 | approved_stage0 |

## 接口约定

空列表、不可读文件、空文件、表头/字段数错误、空键、非法 CSV、非法或冲突输出路径均应停止且不留下结果文件。时间语法与输出格式以 source 第 2 节为准。

## 显式自由度

输出数据行顺序、错误报告的自然语言措辞、内部数据结构和等价的安全写入机制不计分；它们不得改变可观察内容、定位信息或副作用。

## 未决项

具体 witness task、expected result 和 verifier check 等待 Task007–009。不存在语义规则未决项。
