"""Run unchanged upstream tests in a disposable copy to contain default stores."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from common import LAB, UPSTREAM, code_inventory, write_json


def main():
    before=code_inventory()
    with tempfile.TemporaryDirectory(prefix='p0_upstream_tests_') as directory:
        clone=Path(directory)
        for name in ('AutoSkill4Doc','autoskill','tests'):
            shutil.copytree(UPSTREAM/name,clone/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copyfile(UPSTREAM/'pyproject.toml',clone/'pyproject.toml')
        assert code_inventory(clone)==before
        env=dict(os.environ,PYTHONPATH=str(clone),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
        cmd=[sys.executable,'-B','-m','unittest','discover','-s',str(clone/'tests'),'-p','test_document*.py','-v']
        with (LAB/'reports/upstream_tests_isolated.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(cmd,cwd=clone,env=env,stdout=log,stderr=subprocess.STDOUT)
    write_json(LAB/'reports/upstream_tests_result.json',{'returncode':result.returncode,
        'source_copy_hashes_match':True,'original_upstream_unchanged':code_inventory()==before,
        'command_template':[sys.executable,'-B','-m','unittest','discover','-s','<identical temporary copy>/tests','-p','test_document*.py','-v']})
    print('UPSTREAM_TEST_EXIT='+str(result.returncode))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
