# 产品目录JSON结构校验 Evidence

- family: 未分类技能
- skill_id: 07a1c597-7956-5d8e-aed6-d14736bd7484
- support_count: 1

## Evidence 1

- support_id: 24c21e3f-4bec-59ad-aabb-23a7526baea4
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 11981:12249
- confidence: 0.80
- quote: #### **Validating Product Catalog (JSON)**
**Required structure**: JSON array of objects, each with fields:

* `sku_id` (string, unique)  
* `category` (string: "tops", "bottoms", or "outerwear")  
* `silhouette_description` (string, non-empty)

**Validation checks**:
