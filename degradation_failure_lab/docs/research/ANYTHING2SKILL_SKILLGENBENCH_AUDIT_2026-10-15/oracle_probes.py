"""Offline probes: unchanged official assertions, explicitly rebound filesystem paths.

Not an official Docker/harness run. Does not call models or install dependencies.
"""
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
REPO = BASE / "SkillGenBench"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOLUTIONS = {
    "scikitimage-task-001": '''import numpy as np
from PIL import Image
from skimage.feature import match_template
def match_template_padding_summary(search_path, template_path):
    a=np.asarray(Image.open(search_path).convert("L"), dtype=float)
    b=np.asarray(Image.open(template_path).convert("L"), dtype=float)
    out={}
    for pad_input, suffix in [(False,"no_pad"),(True,"pad")]:
        r=match_template(a,b,pad_input=pad_input)
        out["shape_"+suffix]=list(map(int,r.shape))
        out["peak_"+suffix]=list(map(int,np.unravel_index(np.argmax(r),r.shape)))
    return out
''',
    "scikitimage-task-002": '''import numpy as np
from PIL import Image
from skimage.feature import corner_harris, corner_peaks
def detect_corner_summary(image_path):
    im=np.asarray(Image.open(image_path).convert("L"),dtype=float)/255.0
    response=corner_harris(im)
    points=sorted(corner_peaks(response,min_distance=1,threshold_rel=0.01).tolist())
    return {"response_shape":list(response.shape),"count":len(points),"first_points":points[:8]}
''',
}

results=[]
with tempfile.TemporaryDirectory(prefix="sgb_oracle_",dir=BASE) as temp:
    out=Path(temp)/"agent_output.py"
    for task_id, correct_code in SOLUTIONS.items():
        task=REPO/"skill_evaluation/code_doc/scikitimage"/task_id
        oracle=task/"tests/eval.py"
        before=hashlib.sha256(oracle.read_bytes()).hexdigest()
        mod=load(oracle,task_id.replace("-","_"))
        mod.OUTPUT_FILE=str(out)
        mod.INPUT_DIR=task/"context/input"
        mod.INPUT_PATH=task/"context/input/corner_cross.png"
        expected=mod.compute_expected()
        if task_id.endswith("001"):
            fn="match_template_padding_summary(search_path, template_path)"
            keywords="match_template pad_input"
        else:
            fn="detect_corner_summary(image_path)"
            keywords="corner_harris corner_peaks"
        variants={
            "correct_reference_implementation":correct_code,
            "prohibited_hardcoded_constants":f"# {keywords}\ndef {fn}:\n    return {expected!r}\n",
            "wrong_empty_dictionary":f"# {keywords}\ndef {fn}:\n    return {{}}\n",
        }
        for label,code in variants.items():
            out.write_text(code,encoding="utf-8")
            checks=[]
            for name in sorted(n for n in vars(mod) if n.startswith("test_")):
                try:
                    getattr(mod,name)()
                    checks.append({"check":name,"pass":True})
                except Exception as exc:
                    checks.append({"check":name,"pass":False,"error":repr(exc)})
            results.append({"task_id":task_id,"variant":label,"all_assertions_pass":all(c["pass"] for c in checks),"checks":checks,"expected":expected,"oracle_sha256":before})
        assert before==hashlib.sha256(oracle.read_bytes()).hexdigest()

import numpy, PIL, skimage
report={"scope":"OFFLINE_ASSERTIONS_WITH_PATH_REBINDING_NOT_DOCKER","official_oracle_files_modified":False,"models_called":False,"versions":{"python":sys.version,"numpy":numpy.__version__,"Pillow":PIL.__version__,"scikit_image":skimage.__version__},"results":results}
(BASE/"oracle_probe_results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
