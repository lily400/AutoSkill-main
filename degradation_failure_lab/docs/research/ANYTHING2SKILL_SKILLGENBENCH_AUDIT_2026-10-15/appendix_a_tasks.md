# 附录 A：SkillGenBench 全部64个文档任务

统计快照：GitHub `5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d`。本表由已有机器清单生成；字符数为任务叙述性文档之和，保留工作树 CRLF，不计 Domain 的 `task.json` 描述符。

“静态齐全”仅表示有效 Oracle 文件存在且 Python 语法通过；“离线参考 x/y”是公开参考函数与原比较函数的一致性，不代表官方 Docker/Agent 执行。所有187个生成任务外层 `task.json` 均有严格JSON解析失败，属共同风险，此表不逐行重复。

|task_id|source_type|source_group|文档数|总字符数|Oracle静态/参考结果或关键风险|
|---|---|---|---:|---:|---|
|beautifulsoup4-task-037|code_doc|beautifulsoup4|4|3,485|静态齐全；行为/调用或多输入检查；容器未验|
|librosa-task-001|code_doc|librosa|1|329|静态齐全；固定fixture/API字面量弱约束；容器未验|
|moviepy-task-001|code_doc|moviepy|1|306|静态齐全；固定fixture/API字面量弱约束；容器未验|
|neurokit2-task-012|code_doc|neurokit2|2|8,134|静态齐全；来源API仅标题骨架；容器未验|
|neurokit2-task-014|code_doc|neurokit2|4|4,083|静态齐全；来源API仅标题骨架；容器未验|
|neurokit2-task-017|code_doc|neurokit2|3|4,449|静态齐全；来源API仅标题骨架；容器未验|
|neurokit2-task-024|code_doc|neurokit2|4|10,707|静态齐全；来源API仅标题骨架；容器未验|
|neurokit2-task-038|code_doc|neurokit2|4|11,274|静态齐全；来源API仅标题骨架；容器未验|
|neurokit2-task-044|code_doc|neurokit2|5|7,540|静态齐全；来源API仅标题骨架；容器未验|
|neurokit2-task-046|code_doc|neurokit2|4|6,325|静态齐全；来源API仅标题骨架；容器未验|
|pillow-task-001|code_doc|pillow|1|342|静态齐全；固定fixture/API字面量弱约束；容器未验|
|pillow-task-002|code_doc|pillow|1|385|静态齐全；固定fixture/API字面量弱约束；容器未验|
|pydantic-task-001|code_doc|pydantic|1|28,491|静态齐全；行为/调用或多输入检查；容器未验|
|pydantic-task-004|code_doc|pydantic|2|75,572|静态齐全；行为/调用或多输入检查；容器未验|
|pydantic-task-005|code_doc|pydantic|1|6,501|静态齐全；预建实例重验契约待核|
|scikitimage-task-001|code_doc|scikitimage|1|391|静态齐全；硬编码离线通过；常数模板峰无区分|
|scikitimage-task-002|code_doc|scikitimage|1|300|静态齐全；硬编码离线通过；隐含参数风险|
|scrapy-task-024|code_doc|scrapy|1|25,315|离线正确19/19；单规则错误18/19；非Docker/Agent|
|scrapy-task-041|code_doc|scrapy|4|136,431|静态齐全；行为/调用或多输入检查；容器未验|
|scrapy-task-050|code_doc|scrapy|2|71,057|静态齐全；依赖localhost爬取与子进程；容器未验|
|soundfile-task-007|code_doc|soundfile|4|71,267|静态齐全；行为/调用或多输入检查；容器未验|
|soundfile-task-010|code_doc|soundfile|4|71,267|静态齐全；行为/调用或多输入检查；容器未验|
|soundfile-task-012|code_doc|soundfile|4|71,267|静态齐全；行为/调用或多输入检查；容器未验|
|soundfile-task-015|code_doc|soundfile|4|71,267|静态齐全；行为/调用或多输入检查；容器未验|
|soundfile-task-020|code_doc|soundfile|4|71,267|静态齐全；绑定安装库源码字符串；容器未验|
|soundfile-task-021|code_doc|soundfile|1|303|静态齐全；固定fixture/API字面量弱约束；容器未验|
|soundfile-task-022|code_doc|soundfile|1|335|静态齐全；固定fixture/API字面量弱约束；容器未验|
|soundfile-task-023|code_doc|soundfile|1|325|静态齐全；固定fixture/API字面量弱约束；容器未验|
|lockdate_compliance_gate_001|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Finance|1|16,323|静态齐全；离线参考 6/10；日期异常/blocks不一致|
|currency_budget_normalizer_001|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Finance_2|1|56,437|静态齐全；离线参考 8/8|
|ethics_gate_triage_003|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Healthcare|1|36,360|静态齐全；离线参考 9/9|
|technique_adjusted_micronutrient_sodium_003|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Healthcare_2|1|60,951|静态齐全；离线参考 9/9|
|yoruba_milestone_timeline_builder_007|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Humanities|1|30,147|静态齐全；离线参考 8/8|
|aesthetic_judgment_validator_001|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Humanities_2|1|18,133|静态齐全；离线参考 10/10|
|venue_uncertainty_clarifier_007|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Legal_Advisory|1|65,250|静态齐全；离线参考 6/6|
|settlement_payout_timeline_estimator_008|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Legal_Advisory_2|1|179,801|静态齐全；离线参考 8/8|
|recipe_rewrite_validator_001|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Lifestyle|1|28,552|静态齐全；离线参考 10/10|
|playoff_micro_usage_extractor_001|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Lifestyle_2|1|25,492|静态齐全；离线参考 9/9|
|proactive_delay_notice_scheduler_002|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Management|1|54,390|静态齐全；离线参考 9/9|
|prematch_safety_gate_risk_matrix_004|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Management_2|1|61,171|静态齐全；离线参考 9/9|
|monitoring_gap_brief_classifier_001|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Science|1|18,153|静态齐全；离线参考 10/10|
|risk_interpretation_gatekeeper_002|domain_knowledge_doc|clbench_Domain_Knowledge_Reasoning_Science_2|1|42,236|静态齐全；离线参考 6/7；源评分常数缺失/期望不一致|
|governed_learning_update_decider_001|domain_knowledge_doc|clbench_Empirical_Discovery_Simulation_Experimental_Data|1|97,848|静态齐全；离线参考 10/10|
|precision_consistency_checker_007|domain_knowledge_doc|clbench_Empirical_Discovery_Simulation_Experimental_Data_2|1|115,131|静态齐全；离线参考 8/8|
|fla_packet_cadence_scope_validator_002|domain_knowledge_doc|clbench_Empirical_Discovery_Simulation_Observational_Data|1|76,349|静态齐全；离线参考 9/9|
|spectrum_concentration_estimator_008|domain_knowledge_doc|clbench_Empirical_Discovery_Simulation_Observational_Data_2|1|24,788|静态齐全；离线参考 6/7；NaN不自等|
|sanctuary_endgame_scheduler_002|domain_knowledge_doc|clbench_Empirical_Discovery_Simulation_Simulation_Environment|1|108,488|静态齐全；离线参考 8/8|
|capacity_aware_edge_admission_controller_006|domain_knowledge_doc|clbench_Empirical_Discovery_Simulation_Simulation_Environment_2|1|69,913|静态齐全；离线参考 8/8|
|shark_warranty_safety_gate_001|domain_knowledge_doc|clbench_Procedural_Task_Execution_Instructional_Procedures|1|82,054|静态齐全；离线参考 10/10|
|begging_provocation_brief_validator_001|domain_knowledge_doc|clbench_Procedural_Task_Execution_Instructional_Procedures_2|1|71,823|静态齐全；离线参考 10/10|
|reviews_csv_conformance_validator_007|domain_knowledge_doc|clbench_Procedural_Task_Execution_Operational_Procedures|1|98,869|静态齐全；离线参考 7/7|
|archivist_commit_decider_007|domain_knowledge_doc|clbench_Procedural_Task_Execution_Operational_Procedures_2|1|75,861|静态齐全；离线参考 9/9|
|acquisition_request_generator_004|domain_knowledge_doc|clbench_Procedural_Task_Execution_Workflow_Orchestration|1|90,480|静态齐全；离线参考 8/8|
|cutoff_compliant_placement_decider_002|domain_knowledge_doc|clbench_Procedural_Task_Execution_Workflow_Orchestration_2|1|52,942|静态齐全；离线参考 9/9|
|center_authority_lift_adjudicator_001|domain_knowledge_doc|clbench_Rule_System_Application_Game_Mechanics|1|59,846|静态齐全；离线参考 7/7|
|referee_attempt_decision_router_009|domain_knowledge_doc|clbench_Rule_System_Application_Game_Mechanics_2|1|28,392|静态齐全；离线参考 8/8|
|final_reviewer_decision_console_009|domain_knowledge_doc|clbench_Rule_System_Application_Legal_Regulatory|1|48,079|静态齐全；离线参考 7/7|
|ops_pack_gate_a_egress_veto_002|domain_knowledge_doc|clbench_Rule_System_Application_Legal_Regulatory_2|1|88,634|静态齐全；离线参考 10/10|
|wall_setting_scheduler_002|domain_knowledge_doc|clbench_Rule_System_Application_Mathematical_Formalism|1|59,308|静态齐全；离线参考 8/8|
|balanced_ternary_mux_sim_and_structure_check_007|domain_knowledge_doc|clbench_Rule_System_Application_Mathematical_Formalism_2|1|135,816|静态齐全；离线参考 8/8|
|polyddb_driver_registry_harness_008|domain_knowledge_doc|clbench_Rule_System_Application_Programming_Syntax|1|116,876|静态齐全；离线参考 8/8|
|yule_triage_autofix_002|domain_knowledge_doc|clbench_Rule_System_Application_Programming_Syntax_2|1|74,073|静态齐全；离线参考 10/10|
|roof_beam_count_and_order_validator_007|domain_knowledge_doc|clbench_Rule_System_Application_Technical_Standards|1|71,743|静态齐全；离线参考 8/8|
|gatekeeper_minireport_003|domain_knowledge_doc|clbench_Rule_System_Application_Technical_Standards_2|1|35,729|静态齐全；离线参考 9/9；批准token分支未覆盖|

**合计：64任务；45个库/上下文簇；106个文档路径实例；73个字节不同页面/context文件；60个文档集合。独立原始出版物数仍未知。**
