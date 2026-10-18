"""Exercise only official comparison helpers; no task runner or model call."""
import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

BASE=Path(__file__).resolve().parent
ROOT=BASE/'SkillGenBench'
TASK=ROOT/'skill_evaluation/domain_knowledge_doc/clbench_Empirical_Discovery_Simulation_Observational_Data_2/spectrum_concentration_estimator_008'
source=TASK/'tests/eval.py'
tree=ast.parse(source.read_text(encoding='utf-8'))
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'normalize_value','assert_close'}]
ns={'math':math}
exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),'exec'),ns)
bundle=json.loads((TASK/'tests/testcases.json').read_text(encoding='utf-8'))
checks=[]
for i,case in enumerate(bundle['test_cases'],1):
    try:
        ns['assert_close'](case['expected_output'],case['expected_output'],f'case_{i}')
        checks.append({'case':i,'expected_equals_itself':True})
    except AssertionError as exc:
        checks.append({'case':i,'expected_equals_itself':False,'error':str(exc)})
template=ROOT/'skill_evaluation/code_doc/scikitimage/scikitimage-task-001/context/input/template_10x10.png'
arr=np.asarray(Image.open(template))
report={'scope':'UNMODIFIED_COMPARISON_HELPERS_ONLY','task_id':'spectrum_concentration_estimator_008','checks':checks,'oracle_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scikitimage_task001_template':{'shape':list(arr.shape),'unique_values':np.unique(arr).tolist(),'variance':float(arr.var()),'sha256':hashlib.sha256(template.read_bytes()).hexdigest()}}
(BASE/'oracle_numeric_probe_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
