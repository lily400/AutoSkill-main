# SKU计数逻辑一致性校验 Evidence

- family: 未分类技能
- skill_id: ad537d3f-8dab-5dd3-a8d9-41c8ac4abfb0
- support_count: 1

## Evidence 1

- support_id: dd1f2b7a-de86-5fce-b1aa-a202d201a5ec
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 15206:15739
- confidence: 0.70
- quote: ### **3\. Logical Consistency Check**

* Total counts across all SKUs should not exceed total number of filtered reviews (since reviews can apply to multiple SKUs, totals may exceed review count, but order of magnitude should be reasonable)  
* SKUs in same category should have similar ranges of counts (not drastically different unless justified by descriptions)  
* At least some SKUs should have non-zero counts (if ALL SKUs have zero counts, likely an error in semantic matching)

### **4\. Semantic Quality Check (Spot-check)**
