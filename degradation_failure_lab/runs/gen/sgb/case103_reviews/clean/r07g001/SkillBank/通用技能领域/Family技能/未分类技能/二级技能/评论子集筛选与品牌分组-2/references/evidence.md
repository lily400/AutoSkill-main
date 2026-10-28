# 评论子集筛选与品牌分组 Evidence

- family: 未分类技能
- skill_id: 5f68eb1c-4e17-5d4f-9cd8-ca06e2efa98c
- support_count: 1

## Evidence 1

- support_id: bd4c3af0-d9b1-5cd7-85bc-40584f2a6739
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 16788:17091
- confidence: 0.70
- quote: From the processed reviews CSV, identify the subset where:

* `is_sportswear` \= "yes" AND `is_apparel_product` \= "yes"

Separate this subset into two groups:

* Nike reviews: `competitor_or_nike` \= "nike"  
* Competitor reviews: `competitor_or_nike` \= "competitor"

#### **Step 2: Analyze Each SKU**
