"""Resolve archived SGB locations while preserving historical logical input identities."""
from contextlib import contextmanager
import json
from pathlib import Path
from unittest.mock import patch

MANIFEST='data/manifests/sgb/relocations.json'


def relocated(root,path):
    root=Path(root).resolve();path=Path(path).resolve()
    if not path.is_relative_to(root):raise ValueError('Archive path escapes project')
    manifest=root/MANIFEST
    if not manifest.is_file():return path
    mappings=json.loads(manifest.read_text(encoding='utf-8'))['paths']
    relative=path.relative_to(root).as_posix()
    for old,new in sorted(mappings.items(),key=lambda item:len(item[0]),reverse=True):
        if relative==old or relative.startswith(old+'/'):
            target=(root/(new+relative[len(old):])).resolve()
            if not target.is_relative_to(root):raise ValueError('Archive destination escapes project')
            return target
    return path


def archived_path(path):
    """Resolve a stored absolute path using the manifest in its original project root."""
    path=Path(path).resolve()
    for root in path.parents:
        if (root/MANIFEST).is_file():return relocated(root,path)
    return path


@contextmanager
def historical_input(source):
    """Read moved bytes with the original source_file and resume-key path, in memory only."""
    source=Path(source).resolve();physical=archived_path(source)
    if source==physical:
        yield
        return
    from AutoSkill4Doc.document import file_loader
    from AutoSkill4Doc import ingest,pipeline
    native_loader=file_loader.load_file_units
    native_signature=pipeline.DocumentBuildPipeline._file_input_signature

    def load(path,**kwargs):
        if Path(path).resolve()!=source:return native_loader(path,**kwargs)
        units,_=native_loader(str(physical),**kwargs)
        for unit in units:
            location=Path(unit['source_file'])
            unit['source_file']=str(source/location.relative_to(physical)) if physical.is_dir() else str(source)
        return units,str(source)

    def signature(*,file_path):
        if Path(file_path).resolve()!=source:return native_signature(file_path=file_path)
        value=native_signature(file_path=str(physical));value['path']=str(source)
        return value

    with patch.object(file_loader,'load_file_units',load),patch.object(ingest,'load_file_units',load),\
         patch.object(pipeline.DocumentBuildPipeline,'_file_input_signature',staticmethod(signature)):
        yield
