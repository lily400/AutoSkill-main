
# Task001：首个 Pilot 范围

## 身份与目的

- `workflow_id`: `wf-orders-merge-latest-v1`
- 目的：用一个最小但包含顺序、时间、异常和副作用约束的 workflow，验证“文档—技能—执行—判题”链路能否被可信测量。
- 状态：探索性首个 Pilot；不代表正式数据集、独立 family 数量或正式假设检验。
- 与旧 case001 的关系：新建 workflow，不继承旧 case001 的任务、答案、合格状态或金额/客户汇总规则。

## 输入

任务显式提供有序 CSV 文件列表和一个新输出路径。CSV 使用 UTF-8 和表头 `order_id,updated_at,payload`。文件顺序以任务给出的列表为准，文件内顺序以记录出现顺序为准。

## 输出

成功时创建指定的新 CSV：每个 `order_id` 恰好一条获胜记录，记录字段来自同一输入行，`updated_at` 统一写为 UTC。首版不要求输出行排序。

## 研究边界

本 workflow 只研究多 CSV 合并、全量时间校验、UTC 比较、按订单选择最新整行、并列时按输入顺序取后者，以及输入/输出副作用控制。

下列内容不在范围内：金额计算或核验、客户汇总、复杂日期推断、无时区时间猜测、目录枚举顺序、输出行排序、正式退化强度、正式样本量和模型训练。

## 完成条件

Task001–005 阶段只要求 source、reference spec、canonical IR、provenance、工具契约和权限边界一致。任务实例、参考技能、oracle、mutant 和 verifier 从 Task006 起另行建立。
