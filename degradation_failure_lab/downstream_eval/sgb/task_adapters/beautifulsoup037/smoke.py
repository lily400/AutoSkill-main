"""Independent Task-037 engineering probe: static checks only, never a Harbor Trial."""
import argparse
import ast
import json
from pathlib import Path
import tomllib

from degradation_lab.io import inventory, read, sha256, utc
from . import adapter as bs
from downstream_eval.integration.harbor_adapter import verify_sources


def probe(root, prepared, output, *, task_id, runtime=False):
    """Write one NEW external engineering record. Runtime actions are deliberately unavailable."""
    if runtime:
        raise PermissionError('Runtime/model/network/container actions require separate authorization and implementation')
    if task_id != bs.TASK_ID:
        raise ValueError('Explicit BeautifulSoup task identity required')
    root, prepared = Path(root).resolve(), Path(prepared).resolve()
    destination = bs._new_external_workspace(root, output)
    if destination.is_relative_to(prepared) or prepared.is_relative_to(destination):
        raise ValueError('Engineering records must be separate from prepared inputs')
    preparation = bs.validate_prepared(root, prepared)
    official, mapping = bs.verify_assets(root)
    source, lock = verify_sources(root)
    base = source / 'src/harbor/environments/base.py'
    methods = {node.name for node in ast.walk(ast.parse(base.read_bytes()))
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    required = {'exec', 'is_dir', 'upload_dir', 'service_download_file'}
    if not required <= methods:
        raise ValueError('Pinned environment interface is missing required methods')
    task = prepared / bs.TASK_ID
    config = tomllib.loads((task / 'task.toml').read_text(encoding='utf-8'))
    profile = read(prepared / 'profile.json')
    skill_manifests = {}
    for label in profile['trial_order']:
        path = prepared / 'manifests' / (label + '.json')
        manifest = read(path)
        if manifest.get('task_id') != task_id:
            raise ValueError('Skill manifest task identity mismatch')
        skill_manifests[label] = {'manifest_sha256':sha256(path), 'files':manifest['files'],
                                 'host_path':manifest['staged_root']}
    code = ['downstream_eval/sgb/' + name for name in
            ('beautifulsoup037.py', 'beautifulsoup_smoke.py', 'beautifulsoup_scoring.py',
             'beautifulsoup_agent.py', 'beautifulsoup_exports.py', 'runner.py')]
    code += ['downstream_eval/sgb/task_adapters/' + name for name in
             ('__init__.py', 'beautifulsoup037/__init__.py',
              'beautifulsoup037/adapter.py', 'beautifulsoup037/scoring.py',
              'beautifulsoup037/exports.py', 'beautifulsoup037/smoke.py')]
    code += ['downstream_eval/scoring/results.py', 'downstream_eval/integration/harbor_adapter.py',
             'src/degradation_lab/io.py', 'src/degradation_lab/relocations.py']
    value = {
        'schema_version':1, 'run_kind':'runtime_smoke', 'task_id':task_id,
        'created_at':utc(), 'status':'OFFLINE_PREPARED', 'execution_status':'NOT_RUN',
        'model_calls':0, 'actual_http_attempts':0, 'real_agent_outcome':False,
        'model_api_results':False, 'task_success':None, 'research_budget_created':False,
        'code_version':{'basis':'working_tree_sha256', 'files':{p:sha256(root / p) for p in code}},
        'asset_identity':{'revision':mapping['revision'], 'task_key':mapping['task_key'],
                          'official_files':inventory(official),
                          'adapter_sha256':sha256(root / bs.MAPPING),
                          'runner_lock_sha256':sha256(root / 'downstream_eval/configs/runner.lock.json'),
                          'profile_sha256':sha256(prepared / 'profile.json'),
                          'task_files':inventory(task), 'skills':skill_manifests,
                          'harbor_version':lock['harbor_version'], 'harbor_commit':lock['harbor_commit'],
                          'environment_interface_sha256':sha256(base)},
        'environment_contract':{'required_methods':sorted(required), 'static_methods_present':True,
                                'agent':config['environment'], 'verifier':config['verifier'],
                                'artifacts':config['artifacts'], 'runtime_observation':'NOT_RUN'},
        'skill_paths':preparation['skill_paths'],
        'generator_identity_verified':False,
        'stages':[
            {'stage':'configuration_and_host_skill_integrity', 'status':'PASS', 'error_category':None},
            {'stage':'environment_and_remote_skill_visibility', 'status':'NOT_RUN',
             'error_category':'runtime_not_authorized'},
            {'stage':'artifact_transport', 'status':'NOT_RUN', 'error_category':'runtime_not_authorized'},
            {'stage':'independent_scorer', 'status':'BLOCKED', 'error_category':'isolated_backend_not_implemented'}],
        'blockers':preparation['blockers'] + ['isolated_backend_not_implemented'],
    }
    destination.mkdir(parents=True, exist_ok=False)
    with (destination / 'smoke.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New external engineering directory')
    parser.add_argument('--task-id', required=True)
    args = parser.parse_args(argv)
    value = probe(args.root, args.prepared, args.output, task_id=args.task_id)
    print(json.dumps({'run_kind':value['run_kind'], 'execution_status':value['execution_status'],
                      'task_success':None, 'model_calls':0, 'actual_http_attempts':0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
