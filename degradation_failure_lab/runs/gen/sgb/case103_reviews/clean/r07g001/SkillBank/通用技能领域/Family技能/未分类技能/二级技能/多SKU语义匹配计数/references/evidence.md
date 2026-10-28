# 多SKU语义匹配计数 Evidence

- family: 未分类技能
- skill_id: 51f5a8db-c4dd-53b6-9943-d8f3f4098fdc
- support_count: 1

## Evidence 1

- support_id: 2e9cd190-33d0-5f67-9736-15c46dfee8dd
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 74067:83904
- confidence: 0.80
- quote: [Turn 8 - 2025-08-20T09:20:15] Message from: review_processor
If the brand flag is missing this time, it’s likely due to the new parser. I can try a patch, but not before 11:45 ET.

[Turn 9 - 2025-08-20T09:24:40] Message from: sales_forecaster
If you can at least separate Nike vs competitor by using the brand text, that’s sufficient for my noon run. We’ll refine after lunch.

[Turn 10 - 2025-08-20T09:27:52] Message from: social_monitor
Note that some reviews mention multiple items (e.g., hoodie + joggers in one post). Make sure not to undercount if they semantically match multiple SKUs.

[Turn 11 - 2025-08-20T09:33:05] Message from: orchestrator
Final reminder: Deliver the per-SKU counts JSON and a brief status message. If there are blockers, state them clearly so we can remediate fast.

Artifacts

Artifact 3 — Data Dictionary (Reviews CSV expected columns)
- review_id: string unique identifier
- review: full text
- is_sportswear: "yes" or "no"
- is_apparel_product: "yes" or "no"
- brand: canonical brand name or "N/A"
- competitor_or_nike: "nike" or "competitor" or "n/a"

Artifact 4 — Slack Snippet (Export Status)
[2025-08-19 23:41] review_processor: "Pushed the new exporter; columns should include competitor_or_nike now."
[2025-08-20 07:12] data_ops: "Parser warning: missing mapping for competitor_or_nike; may be absent in morning run."

Artifact 5 — Retail Launch Calendar (Noise)
- Oct: Core fleece refresh
- Nov: Black Friday promos
- Dec: Cold-weather outerwear focus
- Jan: Clearance reset

Artifact 6 — Data Quality SOP Excerpt
- Do not proceed with incomplete classification fields in processed reviews.
- Do not infer classification values from unrelated fields when absent.
- If required columns are missing, request corrected input from the source system.
