# 评论分类字段小写规范化 Evidence

- family: 未分类技能
- skill_id: 2f1bc8c6-2861-5c8a-958a-6d30100bd274
- support_count: 1

## Evidence 1

- support_id: fdc1e70b-9e0b-5c65-b7f7-ff7f67aac842
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 94474:96599
- confidence: 0.75
- quote: Artifact 2 — processed_reviews.csv
Description: CSV exported by review_processor. Row count: ~28
Header:
review_id,review,is_sportswear,is_apparel_product,brand
Rows (sample):
1001,"Tech fleece hoodies are warm without bulk",yes,yes,Nike
1002,"Windbreaker tore after a month, super thin",yes,yes,BrandX
1003,"Love the moisture-wicking tees for cardio",yes,yes,Nike
1004,"Compression tights help with long runs",yes,yes,BrandY
1005,"Oversized hoodies look great but pill fast",yes,yes,BrandZ
1006,"Joggers fit is perfect, tapered but comfy",yes,yes,Nike
1007,"Par ka keeps me warm in January",yes,yes,BrandX
1008,"These streetwear cargos aren’t for training",yes,yes,BrandZ
1009,"Trail jacket packs into its own pocket",yes,yes,BrandY
1010,"T-shirt runs small and shrank",Yes,yes,Nike
1011,"Windbreaker is super light, stuffs easily in bag",yes,yes,BrandX
1012,"Shorts ride up; not great for squats",yes,yes,BrandZ
1013,"Dri-FIT shirts dry fast, no cling",yes,yes,Nike
1014,"Fleece crew too heavy for indoor workouts",yes,yes,Nike
1015,"Compression leggings cut off circulation",yes,yes,BrandY
...
Notes:
- The competitor_or_nike column is not present in this file.
- Row 1010 uses "Yes" (capitalized) in is_sportswear.

Artifact 3 — Review Analysis SOP (Excerpt)
- Validate product_catalog.json: must be an array of exactly 50 unique SKUs; each must include sku_id (string), category (tops|bottoms|outerwear), silhouette_description (non-empty string).
- Validate processed_reviews.csv: must include columns review_id, review, is_sportswear, is_apparel_product, brand, competitor_or_nike. Classification values must be strictly formatted (lowercase).
- If inputs are invalid, halt work and request corrected files.
- If filtered counts yield fewer than 10 Nike or fewer than 10 competitor reviews, note the low-volume condition in your status while proceeding.

Artifact 4 — Email Thread: Catalog Push (Summary)
From: merchandising_manager
To: data_ops
Subject: FW25 Catalog — target is 50 SKUs
Body: “FW24 shipped at 50; keep same target. If we’re short by one in the extract, we’ll fill it this week. Don’t block analysis.”
