# 无效或不完整输入处理 Evidence

- family: 未分类技能
- skill_id: 989858be-8cc3-59b7-88c9-980984e4038d
- support_count: 2

## Evidence 1

- support_id: 2fbe5791-8d08-5d1b-9ad2-c8c3480bce0d
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 11599:11844
- confidence: 0.70
- quote: **Critical requirements**:

* Exactly 50 objects (one per SKU in catalog)  
* Each object must have all 5 fields: `sku_id` and four count fields  
* All counts must be integers ≥ 0  
* SKU IDs must exactly match those in the product catalog

---

## Evidence 2

- support_id: ea714532-58aa-5385-8620-25d11de0bfba
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 16788:17091
- confidence: 0.60
- quote: From the processed reviews CSV, identify the subset where:

* `is_sportswear` \= "yes" AND `is_apparel_product` \= "yes"

Separate this subset into two groups:

* Nike reviews: `competitor_or_nike` \= "nike"  
* Competitor reviews: `competitor_or_nike` \= "competitor"

#### **Step 2: Analyze Each SKU**
