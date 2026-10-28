# 产品目录JSON校验 Evidence

- family: 未分类技能
- skill_id: 0aae9a09-ef4e-5695-9238-58901d557ac0
- support_count: 1

## Evidence 1

- support_id: 2ae4c5d0-7208-59c5-a7f2-26568fe43051
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 12227:12634
- confidence: 0.80
- quote: **Validation checks**:

1. Valid JSON format that can be parsed  
2. Array structure (not single object)  
3. Contains exactly 50 SKU objects  
4. Each SKU has all required fields  
5. No duplicate `sku_id` values  
6. All `category` values are valid ("tops", "bottoms", "outerwear")  
7. All `silhouette_description` fields contain meaningful text (not empty/null)

**If invalid, respond to orchestrator**:
