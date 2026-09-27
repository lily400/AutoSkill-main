# 案例资产的固定约定

case001、case002等各自包含case.json、clean/source.md、evaluation/contract.json、evaluation/fixtures.json和degradation目录。
代码通用，不为每个案例复制一套Python。case.json的所有文件路径相对实验目录；文件必须属于它所在的案例。

contract.rules条目格式：{"id":"R01","source_text":"从本案例干净文档摘出的完整规则"}。
fixtures.cases条目格式：{"id":"test01","input":"待测试输入","expect":"success","outputs":{"目标文件":"期望内容"}}。
错误分支expect为error，outputs为{}，可附error_record/error_field。设计期望答案是人工工作，与运行产物严格区分。
当前CSV夹具是开发测试，没有自动判题器；后续其他任务需要其对应独立判题实现。

未来退化配方放在case目录下degradation/recipes/。字段包括case_id、condition="degraded"、input_file、input_sha256、
clean_sha256、repeat_id、degradation。input_file和generator_file采用相对实验目录的完整路径；case_id要匹配case.json。
degradation包含type、severity、seed、generator_file、generator_sha256、parameters、edits。
edits记录修改前后文本、源字符区间和操作；生成器脚本也放在该案例degradation内，运行时保存副本。
文件/配方/脚本哈希和配对会被验证，但正式实验仍须补充可重放变换的一致性检查。

运行示例：run_case.py --case case001 --method chunk --variant degradation/recipes/实际配方.json --baseline-run 实际干净运行编号。
repeat_id必须与干净运行一致，其他方法参数/源码/依赖/评测契约也必须一致。不要把干净规则传给退化生成过程补答案。
