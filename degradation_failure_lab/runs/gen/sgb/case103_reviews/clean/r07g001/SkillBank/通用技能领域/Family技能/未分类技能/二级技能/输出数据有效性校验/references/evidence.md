# 输出数据有效性校验 Evidence

- family: 未分类技能
- skill_id: 84d5fe5e-e708-590e-8eef-c0647819df6e
- support_count: 1

## Evidence 1

- support_id: 0dbe296d-0b67-5e21-ab53-363999c37b43
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 14966:15243
- confidence: 0.80
- quote: ### **2\. Data Validity Check**

* All `sku_id` values exactly match those in product catalog (case-sensitive)  
* All four count fields are integers  
* All counts are ≥ 0 (no negative values)  
* JSON is properly formatted and parseable

### **3\. Logical Consistency Check**
