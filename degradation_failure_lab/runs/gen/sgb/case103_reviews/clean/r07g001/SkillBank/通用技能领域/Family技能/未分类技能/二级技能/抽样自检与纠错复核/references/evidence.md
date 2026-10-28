# 抽样自检与纠错复核 Evidence

- family: 未分类技能
- skill_id: 5d1c0a04-fb5b-51bf-90e4-19ad0e8463d7
- support_count: 1

## Evidence 1

- support_id: dd1d1668-f0cb-5353-bec2-70e871b5b792
- relation_type: support
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 15741:16066
- confidence: 0.80
- quote: Randomly select 3-5 SKUs and verify:

* Reviews counted as applicable actually discuss semantically similar attributes  
* Category matching was correctly applied  
* Sentiment classification was accurate

**If self-check reveals issues**: Correct the analysis before returning output. Do not return output with known errors.
