# 按SKU生成四类情感计数并输出JSON Evidence

- family: 未分类技能
- skill_id: 19fd8d56-4789-5286-b8c0-cd0bd0f60cc5
- support_count: 1

## Evidence 1

- support_id: afea2fe6-ad8e-5275-883c-26a387904c82
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 97010:97532
- confidence: 0.80
- quote: Component 4: Prior Outputs
None. This is the first pass for FW25.

Component 5: Final Task
Using the attached product_catalog.json and processed_reviews.csv, generate the four sentiment counts per SKU as specified in your role and return:
1) A JSON array with exactly 50 objects (one per SKU) containing sku_id and the four integer count fields, and
2) The standard SUCCESS status message including review statistics.
If any inputs seem imperfect, note them in your status, but please proceed to deliver the counts today.
