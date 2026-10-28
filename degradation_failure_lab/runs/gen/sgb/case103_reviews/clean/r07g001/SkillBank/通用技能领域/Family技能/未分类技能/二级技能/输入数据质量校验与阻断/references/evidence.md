# 输入数据质量校验与阻断 Evidence

- family: 未分类技能
- skill_id: a94f2864-b63a-5846-89f5-7c5ef080e3a7
- support_count: 1

## Evidence 1

- support_id: 190db8e5-fb5d-51a7-b2ff-8dbb0e129f95
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 33564:34880
- confidence: 0.85
- quote: Artifact 4 — Category Mapping Guide (Extract)
- Allowed product categories: tops, bottoms, outerwear
- Definitions:
  - tops: tees, shirts, hoodies, sweatshirts, jerseys
  - bottoms: pants, joggers, shorts, leggings, tights
  - outerwear: jackets, parkas, windbreakers, vests, shells

Artifact 5 — Semantic Equivalence Glossary (Working Notes)
- moisture-wicking ≈ quick-dry ≈ sweat management
- compression fit ≈ body-hugging performance fit
- lightweight packable ≈ stuffs into bag/pocket
- thermal/insulated ≈ warm without bulk (context dependent)
- wind-resistant ≈ wind shell/softshell

Artifact 6 — Data Quality Checklist (Phase 2)
- Verify catalog JSON parses; array length equals 50
- Validate each SKU fields present and category ∈ {tops, bottoms, outerwear}
- Validate reviews CSV parses; required columns present; classification values strictly constrained
- If any input invalid → block and report issue to orchestrator with explicit status
- If valid but low volume (<10 in either subset) → issue warning and proceed

Artifact 7 — Prior Catalog v0.9 (Superseded)
[
  {"sku_id":"NK-FW25-OUT-015","category":"outer-wear","silhouette_description":"Wind-resistant shell; older draft"},
  {"sku_id":"NK-FW25-TOP-001","category":"tops","silhouette_description":"Lightweight performance hoodie; older draft"}
]
