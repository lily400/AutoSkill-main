
# 官方测试结果

## 原样运行

固定解释器，在临时可写副本中执行：

```powershell
D:noconda1\envsutoskill\python.exe -m pytest -p no:cacheprovider -q -ra tests
```

结果：`148 passed, 8 failed`，总计 156 项，耗时约 15 秒。没有修改官方源码或测试。

## 失败分类

Windows 路径前置问题影响六项：测试硬编码 `/tmp`，Windows 解析为 `C:	mp`；其中 registry 断言使用混合路径格式，五个 versioning 用例在创建 `C:	mp
on-persistent` 时先遇到权限错误。

在临时测试副本中仅替换这些测试路径以做诊断后，仍有六项代码/测试契约失败：

1. `test_build_resumes_streamed_register_without_recompiling_processed_documents`：预期抛出 `RuntimeError`，实际未抛出。
2. `test_parallel_document_extraction_preserves_input_order`：并行结果为 B、A，预期保持 A、B。
3. `test_classify_change_hits_zero_uses_compact_create_discard_prompt`：捕获的 system prompt 为空，缺少预期文本。
4. `test_classify_change_includes_single_peer_candidate_for_split_signal`：实际 `split`，预期 `create`。
5. `test_classify_change_invalid_merge_target_falls_back_to_create`：实际 `strengthen`，预期 `create`。
6. `test_classify_change_payload_includes_contract_fields`：实际 `strengthen`，预期 `create`。

结论：测试套件当前不全绿；包含 Windows 测试可移植性问题和官方代码/测试契约不一致。本轮只记录，不修复 B0。
