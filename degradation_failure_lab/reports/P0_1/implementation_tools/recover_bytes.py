import pathlib, subprocess, sys, json, hashlib
lab=pathlib.Path(sys.argv[1]).resolve(); repo=lab.parent
commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
digest=lambda b:hashlib.sha256(b).hexdigest()
entries={}
source=read(lab/'data/manifests/qsv_select.json')
targets={source['local_path']:source['sha256']}
for name in ('p0_qsv_select_clean_001','p0_qsv_select_clean_002'):
    for rel,h in read(lab/f'runs/{name}/artifact_manifest.json').items(): targets[f'runs/{name}/{rel}']=h
for rel,expected in targets.items():
    working=(lab/rel).read_bytes()
    if digest(working)==expected:continue
    blob=subprocess.check_output(['git','-C',str(repo),'show',commit+':degradation_failure_lab/'+rel])
    if digest(blob)!=expected or working.replace(b'\r\n',b'\n')!=blob:
        raise RuntimeError('Not a proven EOL-only checkout difference: '+rel)
    archive=lab/'data/legacy_bytes'/rel
    archive.parent.mkdir(parents=True,exist_ok=True); archive.write_bytes(blob)
    entries[rel]={'expected_sha256':expected,'working_sha256':digest(working),
                  'archived_path':archive.relative_to(lab).as_posix(),'git_commit':commit,
                  'git_path':'degradation_failure_lab/'+rel,'difference':'LF converted to CRLF during checkout'}
out=lab/'data/legacy_byte_index.json'
out.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
canonical=dict(source,local_path=entries[source['local_path']]['archived_path'])
(lab/'data/manifests/qsv_select_canonical.json').write_text(json.dumps(canonical,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
catalog=read(lab/'data/catalog.json'); catalog['datasets'][0]['source_manifests']=['data/manifests/qsv_select_canonical.json']
(lab/'data/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=lab/'cases/case001_qsv_select/inputs/clean.json'; inputs=read(p)
inputs['inputs'][0]['path']=canonical['local_path']
p.write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(lab/'.gitattributes').write_text('# Preserve exact source and run artifact bytes across Windows checkouts.\ndata/legacy_bytes/** -text\ndata/sources/** -text\nruns/** -text\n',encoding='utf-8')
(lab/'reports/P0_1/eol_recovery.json').write_text(json.dumps({'archive_commit':commit,'entries':entries,'original_files_overwritten':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'restored_independent_byte_snapshots':len(entries),'git_commit':commit}))
