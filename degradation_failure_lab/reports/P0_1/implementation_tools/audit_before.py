import hashlib, json, pathlib, sys
lab = pathlib.Path(sys.argv[1])
up = lab.parent / 'AutoSkill-main'
def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
files = inventory(lab)
official = {}
for prefix in ('AutoSkill4Doc', 'autoskill', 'tests', 'pyproject.toml'):
    p = up / prefix
    for f in (p.rglob('*') if p.is_dir() else [p]):
        if f.is_file() and '__pycache__' not in f.parts and f.suffix != '.pyc':
            official[f.relative_to(up).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
parsed = {}
for rel in files:
    p = lab / rel
    if p.suffix == '.json':
        try:
            v = json.loads(p.read_text(encoding='utf-8'))
            parsed[rel] = {'type':type(v).__name__, 'keys':list(v) if isinstance(v,dict) else None, 'length':len(v)}
        except Exception as e: parsed[rel] = {'parse_error':str(e)}
out = lab / 'reports/P0_1'
out.mkdir(exist_ok=False)
for name,v in [('project_before.json',files),('upstream_before.json',official),('json_inventory.json',parsed)]:
    (out/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'audit_and_plan.md').write_text('''# P0.1 重构前审计与实施范围

审计覆盖 README、全部 scripts/configs/data/reports/tests 和两次 P0 运行。
project_before.json 保存所有既有文件的字节哈希；json_inventory.json 保存逐文件 JSON 解析结果。
上游生成代码、提示词、测试与包配置另有完整哈希基线。

可复用：官方 extract_from_doc 调用、公开 connector_factory 模型参数扩展、原样 HTTP 观测、
代码哈希保护、独立 SkillBank、新目录拒绝覆盖、官方四阶段结果、证据窗口与最终技能关联。

硬编码与问题：
- run_clean 默认单份 qsv 清单和扁平 run 目录；仅保存全局清单，没有输入字节快照。
- verify_run 固定 deepseek-flash、qsv 来源类别、单文档和 docskill 用户；不能验证通用案例。
- verify_run 虽称只读，实际覆盖运行内 verification/exports/artifact_manifest；历史重验应改为外部 sidecar。
- rules 是独立检查表，但没有案例、条件与规则级评价合同；quality_review 只有 Markdown。
- prepare_sources/audit_extra 是 P0 专用来源调查，不宜复制成每案例脚本。
- 旧配置重复模型和预算并混入来源与 family；缺少 case/condition/run 引用层。
- 新增 case002 原先至少要手工换清单、配置、验证器和审核路径；不能靠新增数据定义完成。
- 成功运行有四个候选、两个正式程序技能、两个可见副本及两个导航；注册丢弃不能称为内容合并。
- 失败运行保留提取/编译和注册异常；不能作为成功生成。
- 原始数据是官方来源重建，不是已确认论文快照；规则是 CUSTOM_TEST_DATA。

最小方案：少量通用模块负责严格字段验证、来源/案例解析、独立运行、真实官方适配、
只读 trace/verification、评价与聚合。只注册 case001；case002 仅在临时测试夹具内模拟。
旧文件和报告不搬迁，旧运行索引建立案例关联。历史规则逐字保留，历史判断结构化但不升级。
公共配置不含 case/source 信息；各案例只增加 JSON 和可校验输入清单。
新运行路径 runs/<case_id>/<condition_id>/<run_id>；退化接口仅接收已准备并固定哈希的输入，
不实现退化算子。本轮不调用模型。保留 P0 专用获取脚本，阻止旧 CLI 改写历史运行。

验收：旧成功记录通过通用验证、旧失败记录可读；共享来源、多条件、多次运行、隔离、
严格 schema、非 qsv/model 的夹具导出聚合均通过离线测试；历史与上游哈希保持一致。
''',encoding='utf-8')
print(json.dumps({'existing_files':len(files),'upstream_files':len(official),'json_files':len(parsed),'json_errors':[p for p,v in parsed.items() if 'parse_error' in v]}))
