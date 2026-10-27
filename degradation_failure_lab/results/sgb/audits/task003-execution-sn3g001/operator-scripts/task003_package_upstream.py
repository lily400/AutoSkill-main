import hashlib,json,tarfile
from pathlib import Path
root=Path(r'D:\AS\AutoSkill-main\degradation_failure_lab')
run=root/'runs/gen/sgb/case003_san/clean/sn3r001'
snapshot=json.loads((run/'upstream_before.json').read_text(encoding='utf-8'))
source=Path(json.loads((run/'environment.json').read_text(encoding='utf-8'))['upstream_path'])
target=root/'results/sgb/audits/task003-execution-sn3g001/upstream-inspection-snapshot.tar.gz'
if target.exists():raise FileExistsError(target)
with tarfile.open(target,'w:gz') as archive:
    for name,digest in snapshot.items():
        path=source/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
        archive.add(path,arcname=name,recursive=False)
print(json.dumps({'files':len(snapshot),'archive':str(target),'purpose':'Byte-identical code inspection only; no Agent access'}))
