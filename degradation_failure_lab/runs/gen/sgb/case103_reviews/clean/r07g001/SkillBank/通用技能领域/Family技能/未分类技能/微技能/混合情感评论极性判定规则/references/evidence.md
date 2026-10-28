# 混合情感评论极性判定规则 Evidence

- family: 未分类技能
- skill_id: 7e9b6184-6ad1-511a-a756-2b9fff70151b
- support_count: 1

## Evidence 1

- support_id: ef75e796-9f2b-564b-bc85-b383a5f7b519
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 9212:9741
- confidence: 0.85
- quote: **Mixed reviews**: If a review contains both positive and negative sentiments:

* If the review is **primarily positive** with minor criticisms → count as positive  
* If the review is **primarily negative** with minor praise → count as negative  
* If the review is **equally balanced** → default to negative (conservative approach prioritizes avoiding mistakes)

Example: "Nike Tech Fleece is warm and stylish, but it pills after a few washes and the price is too high" → Count as **negative** (durability issue is significant)
