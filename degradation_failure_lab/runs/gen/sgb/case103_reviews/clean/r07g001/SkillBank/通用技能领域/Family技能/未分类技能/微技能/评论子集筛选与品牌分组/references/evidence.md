# 评论子集筛选与品牌分组 Evidence

- family: 未分类技能
- skill_id: 555ffad0-26e3-5408-a321-ea0963dca8e6
- support_count: 1

## Evidence 1

- support_id: ab7318e5-1b3b-5cc9-8630-f8cc5bc415d8
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 4921:5572
- confidence: 0.80
- quote: **2\. Processed Reviews (CSV)** The output from review\_processor containing classified reviews with columns:

* `review_id`: Unique identifier  
* `review`: Raw review text  
* `is_sportswear`: "yes" or "no"  
* `is_apparel_product`: "yes" or "no"  
* `brand`: Specific brand name or "N/A"  
* `competitor_or_nike`: "nike", "competitor", or "n/a"

You must filter this CSV to only analyze reviews where:

* `is_sportswear` \= "yes" AND  
* `is_apparel_product` \= "yes"

This filtering creates two subsets:

* **Nike reviews**: rows where `competitor_or_nike` \= "nike"  
* **Competitor reviews**: rows where `competitor_or_nike` \= "competitor"

---
