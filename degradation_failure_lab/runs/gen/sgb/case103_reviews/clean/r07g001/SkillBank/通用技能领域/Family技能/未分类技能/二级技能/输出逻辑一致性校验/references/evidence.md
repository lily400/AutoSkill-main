# 输出逻辑一致性校验 Evidence

- family: 未分类技能
- skill_id: ee25de74-f85b-5c3c-a2eb-10864f6b92fd
- support_count: 1

## Evidence 1

- support_id: 6d237e26-b709-58a7-a726-816684ab8e60
- relation_type: constraint
- document: input001\context.md
- doc_id: debb1776-1021-523f-adab-cc06d43c1776
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case103_reviews\clean\r07g001\inputs\input001\context.md
- section: # System Context
- span: 14966:15243
- confidence: 0.70
- quote: ### **2\. Data Validity Check**

* All `sku_id` values exactly match those in product catalog (case-sensitive)  
* All four count fields are integers  
* All counts are ≥ 0 (no negative values)  
* JSON is properly formatted and parseable

### **3\. Logical Consistency Check**
