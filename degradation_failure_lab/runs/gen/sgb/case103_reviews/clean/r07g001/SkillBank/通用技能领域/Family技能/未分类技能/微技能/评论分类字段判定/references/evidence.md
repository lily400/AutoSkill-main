# 评论分类字段判定 Evidence

- family: 未分类技能
- skill_id: 05006ada-1d31-5804-a934-35033693109c
- support_count: 1

## Evidence 1

- support_id: 7d8f3745-5faa-5612-9dc9-e22799e6c858
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 13142:13693
- confidence: 0.80
- quote: **Required structure**: CSV with columns:

* `review_id`, `review`, `is_sportswear`, `is_apparel_product`, `brand`, `competitor_or_nike`

**Validation checks**:

1. Valid CSV format that can be parsed  
2. All required columns present  
3. Classification columns contain only valid values:  
   * `is_sportswear`: only "yes" or "no"  
   * `is_apparel_product`: only "yes" or "no"  
   * `competitor_or_nike`: only "nike", "competitor", or "n/a"  
4. At least 20 rows present (minimum for meaningful analysis)

**If invalid, respond to orchestrator**:
