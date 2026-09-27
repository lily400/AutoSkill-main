"""Install evidence recording, then execute the unchanged official module entry."""
import os
import runpy
import sys
from pathlib import Path
from trace_http import install
from trace_runtime import install as install_runtime

if __name__ == '__main__':
    root=Path(os.environ['SKILL_LAB_FRAMEWORK']).resolve()
    import AutoSkill4Doc, autoskill
    for module in (AutoSkill4Doc, autoskill):
        if Path(module.__file__).resolve()!=root/module.__name__/'__init__.py':
            raise RuntimeError('Unexpected official module origin')
    install(os.environ['SKILL_LAB_TRACE'])
    install_runtime(os.environ['SKILL_LAB_TRACE'])
    sys.argv=['AutoSkill4Doc',*sys.argv[1:]]
    runpy.run_module('AutoSkill4Doc',run_name='__main__',alter_sys=True)
