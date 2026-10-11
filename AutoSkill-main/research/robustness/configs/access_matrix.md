
# Task005：角色访问矩阵

| 对象 | Generator | Executor | Verifier | 评测控制端 |
|---|---:|---:|---:|---:|
| 当前 document | 允许 | 禁止 | 允许核验 | 允许 |
| 当前 task 与输入文件 | 禁止 | 允许 | 允许 | 允许 |
| 当前 generated Skill | 仅自身产物 | 允许 | 允许 | 允许 |
| 通用工具说明 | 允许 | 允许 | 允许 | 允许 |
| reference spec / expected result | 禁止 | 禁止 | 允许 | 允许 |
| verifier 实现 | 禁止 | 禁止 | 允许 | 允许 |
| locked-test truth | 禁止 | 禁止 | 允许 | 允许 |
| reference skill | 禁止；R 条件另行授权 | 禁止；仅 R 条件授权 | 允许 | 允许 |
| gold reference IR | 测试阶段禁止 | 禁止 | 允许 | 训练分区按协议授权 |
| 其他条件的 paired document | 禁止 | 禁止 | 审核时允许 | 允许 |

## 隔离要求

- 每次 generation 使用独立会话、独立运行目录和空技能存储。
- Executor 只接收当前 task、当前 Skill 和获准工具，不接收 source、gold IR 或评测反馈。
- Verifier 在独立受控进程读取隐藏真值；只分目录而不限制权限不算隔离。
- judgment 不回流用于同一 locked test 的生成、修复、提示或候选选择。
