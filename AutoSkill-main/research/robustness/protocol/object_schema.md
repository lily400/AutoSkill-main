
# Stage 0 实验对象与 ID 规范

## 关联链

`family → workflow → source/document → spec/reference_ir 或 predicted_ir → task → generation → skill → execution → judgment → comparison → freeze`

## 通用字段

每个对象至少记录稳定 ID、schema/version、创建时间、父对象 ID、状态、内容哈希及产物路径。对象内容变化时创建新版本，不覆盖已冻结版本。

| 对象 | ID 形式 | 当前实例或状态 |
|---|---|---|
| family | `fam-<slug>-vN` | `fam-csv-batch-record-selection-v1`，`pilot_provisional` |
| workflow | `wf-<slug>-vN` | `wf-orders-merge-latest-v1` |
| source | `src-<slug>-vN` | `src-orders-merge-latest-clean-v1` |
| document | `doc-<slug>-<condition>-vN` | `doc-orders-merge-latest-clean-v1` |
| spec | `spec-<slug>-vN` | `spec-orders-merge-latest-v1` |
| reference_ir | `ir-<slug>-vN` | `ir-orders-merge-latest-v1` |
| predicted_ir | `pir-<workflow>-<run>` | `pending` |
| task | `task-<workflow>-<case>` | `pending_task007` |
| generation | `gen-<method>-<workflow>-<repeat>` | `not_run` |
| skill | `skill-<generation>-<index>` | `not_run` |
| execution | `exec-<skill>-<task>-<repeat>` | `not_run` |
| judgment | `judge-<execution>-<verifier>` | `not_run` |
| comparison | `cmp-<scope>-vN` | `not_run` |
| freeze | `freeze-<scope>-vN` | `freeze-b0-stage0-v1` |

## 状态语义

- `pending`：字段或审核尚未确定。
- `not_run`：预定操作尚未执行。
- `unobserved`：操作已尝试但结果不可观测。
- `failed`：已观察到失败。
- `blocked`：前置条件未满足，操作未执行。

正式 family/workflow 数、数据划分数量、生成与执行重复、训练种子、δ、ε 和 degradation severity 均保持 `pending`，由后续 Pilot 和冻结程序决定。
