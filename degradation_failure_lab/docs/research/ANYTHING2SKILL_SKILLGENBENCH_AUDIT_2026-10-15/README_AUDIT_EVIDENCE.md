# 审计证据包说明

日期：2026-10-15。配套主报告为 `ANYTHING2SKILL_SKILLGENBENCH_FEASIBILITY_AUDIT_2026-10-15.md`。

本包仅包含审计文件、离线结果和复核脚本。没有生成新技能，没有调用模型，没有运行Agent或官方Docker评价，没有改动原始任务、Oracle或47份历史技能。

## 版本与路径

- SkillGenBench完整只读快照：`C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-15/SkillGenBench`，提交 `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。
- 原始审计脚本及所有输出：`C:/Users/lily/Documents/ChatGPT/回归解决退化文档/audit_2026-10-15`。
- 本地历史工程：`D:/AS/AutoSkill-main/degradation_failure_lab`；受评实现：`D:/AS/AutoSkill-main/AutoSkill-main`。
- 官方AutoSkill快照：原始审计目录下`AutoSkill-official-94c47ca/`，提交`94c47ca488d4ba4117d20272e66d49b9877e68cf`。164个运行指纹文件与本地完全一致；结果见`official_autoskill_comparison.json`，复核脚本`compare_official_autoskill.py`需要该相邻快照。
- HF版本：`4e23915c65f0f1e7c8bacea00feb33974d936ef9`；仅元数据与具名样本获取成功，失败项见 `hf_github_comparison.json`。样本文件并不代表完整数据集下载。
- 本机离线探针：Python 3.13.9，pytest 8.4.2，NumPy 2.3.5，Pillow 12.3.0，scikit-image 0.25.2。版本用于解释本轮结果，不代替官方Linux环境锁定。

## 阅读顺序

1. 主报告的四项裁决、失败归因树与P0–P5门槛。
2. `sgb_task_inventory.jsonl`或CSV：187任务、全部15个必需字段；`sgb_document_tasks_only.json`为64文档任务子集。
3. `deliverable_inventory_validation.json`：清单一致性31项检查；`sgb_data_summary.json`与`sgb_source_groups.json`：计数定义和解析失败全集。
4. `clean5_inventory.json`与`clean5_register_response_audit.json`：五个历史run、47 canonical和53次注册响应证据。
5. `runtime_contract_checks.json`、`agnostic_shared_materials_audit.json`：接口与路径、材料可见性问题。
6. `oracle_probe_results.json`：两个scikit-image任务的硬编码假阳性；`oracle_numeric_probe_results.json`：NaN自比较失败；`domain_reference_probe_results.json`：36领域参考的308例检查；`scrapy_oracle_probe_results.json`：单规则正反例敏感性。
7. 分项memo包含文件行号和推断边界；`artifact_manifest.json`记录本证据包交付文件的SHA256。

## 可复核命令与边界

所有脚本相对其自身目录寻找 `SkillGenBench/`，Clean脚本另外固定读取上述D盘历史工程。交付目录不包含完整源码；重跑应在原始审计目录进行，或先在新目录准备同提交的只读快照。不要直接对证据包运行脚本并覆盖归档结果。

以下为本机已有Python环境的复核示例；它们不会安装依赖，也不启动Agent。先查看脚本并确认输出目录为新的审计副本：

```powershell
python -B runtime_contract_checks.py
python -B audit_agnostic_inputs.py
python -B oracle_probes.py
python -B oracle_numeric_probe.py
python -B scrapy_oracle_probe.py
python -B probe_domain_reference.py
python -B build_data_appendix.py
```

完整数据扫描为 `scan_sgb_data.py`后接`annotate_sgb_data.py`；它们重新生成清单。Clean复核为`inspect_clean5.py`及`inspect_clean5_loader_register.py`。下载HF样本的`compare_hf_snapshot.py`包含网络访问，不是离线步骤。

领域参考脚本只在独立离线检查中执行已审阅的纯函数及实际比较器，不调用`original_eval.py`。后者含模型调用流程，不能将其当作离线复核命令。所有参考通过率只测公开参考与Oracle的一致性，不是生成方法、Agent能力或官方Benchmark成绩。

审计脚本中出现的正确/错误提交物都是确定性诊断夹具，不是新生成算法或正式Gold。Scrapy正确提交由已看测试的审计者编写；不能作为盲建Gold使用。任何后续修正任务、增加测试或更改隔离协议须另名扩展版本。
