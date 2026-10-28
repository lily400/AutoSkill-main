# 语义匹配结果抽样质量检查 Evidence

- family: 未分类技能
- skill_id: 3350a33c-d6b2-5fdf-8f8e-c122b1618d1f
- support_count: 1

## Evidence 1

- support_id: ba475eac-99a9-545c-9b2f-89d38d39920f
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 15206:15739
- confidence: 0.60
- quote: ### **3\. Logical Consistency Check**

* Total counts across all SKUs should not exceed total number of filtered reviews (since reviews can apply to multiple SKUs, totals may exceed review count, but order of magnitude should be reasonable)  
* SKUs in same category should have similar ranges of counts (not drastically different unless justified by descriptions)  
* At least some SKUs should have non-zero counts (if ALL SKUs have zero counts, likely an error in semantic matching)

### **4\. Semantic Quality Check (Spot-check)**
