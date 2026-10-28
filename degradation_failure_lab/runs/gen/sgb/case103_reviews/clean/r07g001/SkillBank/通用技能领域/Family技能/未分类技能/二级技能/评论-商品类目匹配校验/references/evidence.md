# 评论-商品类目匹配校验 Evidence

- family: 未分类技能
- skill_id: cec8d08c-dd63-5fc9-b329-41264046ef35
- support_count: 1

## Evidence 1

- support_id: 1933ef17-aeee-5fa7-87ab-d8a8ad02ce6e
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 5682:6220
- confidence: 0.90
- quote: #### **Category Matching (Hard Requirement)**
A review can only be applicable to a SKU if they share the same product category:

* Reviews mentioning tops/shirts/hoodies/jackets can only apply to SKUs with `category` \= "tops"  
* Reviews mentioning pants/joggers/shorts/tights can only apply to SKUs with `category` \= "bottoms"  
* Reviews mentioning outerwear/parkas/windbreakers/vests can only apply to SKUs with `category` \= "outerwear"

Determine the category of each review by analyzing which type of apparel product it discusses.
