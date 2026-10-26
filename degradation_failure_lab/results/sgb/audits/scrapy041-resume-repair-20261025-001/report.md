# Scrapy041 四文档断点恢复修复

结论：本次真实检查点的零模型恢复验证通过；尚未执行付费续跑，也未生成新的 Clean Skill。

## 原因与最小修复

- 原入口仅接受单文档、连续窗口前缀。本次父运行 r13fe557951 为四文档，35 个窗口中完成 34 个，request-response.md 的窗口 a665c1c0-1e9d-51cc-b809-f6ee35b87f8c 因 SSL EOF 未完成。
- 新增多文档恢复分支，核对每个窗口的文档身份、原文/位置、模型请求和候选草稿数量，拒绝成功但未保存检查点的 Plan/Expand，保留已完成窗口。
- 官方流式编译会把未 skipped 的错误文档也当作已处理。本次没有任何编译/注册模型请求或成功规格；因此在新运行副本中排除 compile/register/final 的空结果，保留原文件与排除清单哈希。并未修改官方生成算法。
- 新增显式累计预算参数；预算继承父运行的 88 次尝试和 453608 Token，不清零。用户已授权累计 900000 Token、150 次 HTTP 尝试，授权记录在 authorization.json。旧 config.json 不变。
- 多文档恢复目前限定在尚未发生编译/注册模型调用且没有成功下游规格的检查点；不声称支持任意阶段的恢复。

## 变更

- src/degradation_lab/resume.py：多文档检查点核对、副本缓存排除、子运行预算记录及耗尽时提前拒绝。
- src/degradation_lab/runner.py：转交显式续跑预算。
- src/degradation_lab/cli.py：新增 --max-observed-total-tokens、--max-http-calls 续跑参数。
- tests/test_resume_multidoc.py：6 项零模型回归；现有单文档 11 项测试一并运行。

## 验证

17 项测试通过。证据：tests.log、validation.json。真实官方恢复流程在临时副本中复用 ingest 与 34 个窗口，只将失败的 1 个窗口交给替身提取器；保留 49 个候选草稿，并将 4 份文档全部送到替身编译器。实际模型传输被禁止，测试没有生成真实技能。

父运行 artifact_manifest.json 中 366 个文件哈希全部一致；测试还核对父目录完整文件清单不变。官方源码未改动。s41r002 尚未创建，供用户实际续跑使用。测试中的原024续跑仍通过。

## 执行命令

在 degradation_failure_lab 目录执行：

```powershell
python scripts/lab.py resume --run r13fe557951 --run-id s41r002 --max-observed-total-tokens 900000
```

HTTP 累计上限继承150次；Token为发起下一请求前检查的软阈值。仅新运行配置记录新上限。SSL故障的根因没有在本次修改中修复，失败请求是否在服务端执行或计费无法证明。真实提取、编译、注册成功与质量核验仍需实际续跑后检查。本次未启动模型、下游Agent或Scrapy041对照实验。
