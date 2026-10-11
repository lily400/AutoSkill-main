# P0–P0.2 完整历史归档

归档来源：`master` 在 `c820a0ee341b3c46b34ec4be0294516fe5aa764e` 的完整提交。

GitHub 保留分支：[`archive/p0-p02-full-20261011`](https://github.com/lily400/AutoSkill-main/tree/archive/p0-p02-full-20261011)。

该分支包含原始 P0/P0.1/P0.2 文件、两次真实 P0 运行及其 SKILL.md、旧来源和字节证明、模型 HTTP 请求/响应、审计与验证报告，以及 `legacy/` 中的旧实现；清理分支仅保留现行公共框架。

**归档性质**：这里使用 Git 分支的不可改动历史提交作为仓库内恢复依据，未创建用户本地磁盘上的第二份备份，也尚未在 Windows 环境实际复测从归档分支恢复历史 P0。不能将 Git 分支存在等同于已完成离线恢复验证。

可通过临时工作树恢复旧版而不污染现行工作目录（在仓库根目录执行）：

```powershell
git fetch origin archive/p0-p02-full-20261011
git worktree add ..\AutoSkill-main-P0-archive origin/archive/p0-p02-full-20261011
```

随后按归档版本 README/P0 报告指定环境核验旧源码、原文、SKILL.md、P0 运行与 `verify`。工作树须有可访问的官方源码及正确的路径条件；绝对路径可能需要显式配置，切勿修改历史产物伪装成功。

**不要删除归档分支或重写其历史**。若需要仓库外灾备，请自行在安全位置克隆/打包该归档提交并验证哈希。
