import argparse
import json
from pathlib import Path
from .artifacts import export_run, inspect_run
from .catalog import CaseManager
from .evaluation import aggregate, init_evaluation, validate_evaluation
from .io import inside, read
from .runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(description='Offline catalogs/evidence; run invokes the official paid model API')
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[2]))
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('list')
    for name in ('plan','run'):
        p = sub.add_parser(name)
        p.add_argument('--case', nargs='+', required=True)
        p.add_argument('--condition', nargs='+')
        p.add_argument('--repeat', type=int, default=1)
        if name=='run': p.add_argument('--run-id', help='Only for a single case/condition/repeat')
    p = sub.add_parser('verify'); p.add_argument('--run', required=True)
    p.add_argument('--out', help='Project-relative external sidecar directory')
    p = sub.add_parser('aggregate'); p.add_argument('--out', default='results/aggregates/current')
    p.add_argument('--case', nargs='+')
    p = sub.add_parser('evaluation-init'); p.add_argument('--run', required=True)
    p.add_argument('--evaluation-id', default='initial_review')
    p = sub.add_parser('evaluation-validate'); p.add_argument('--file', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.command in ('list','validate'):
        manager = CaseManager(root)
        cases = manager.list_cases()
        if args.command=='validate':
            for case_id in cases:
                bundle = manager.load(case_id)
                for c in bundle['conditions']['conditions']: manager.condition(bundle,c['condition_id'])
            for p in sorted((root/'evaluations').rglob('*.json')): validate_evaluation(root,read(p))
        result = {'cases':cases, 'sources':list(manager.sources.sources), 'status':'VALID'}
    elif args.command in ('plan','run'):
        manager = CaseManager(root)
        runner = ExperimentRunner(root, manager)
        plans = []
        # Validate the complete batch before starting any paid request.
        for case_id in args.case:
            bundle = runner.cases.load(case_id)
            conditions = args.condition or [c['condition_id'] for c in bundle['conditions']['conditions']]
            for cid in conditions: plans.append(runner.plan(case_id,cid,args.repeat))
        if args.command=='plan': result=plans
        else:
            if args.run_id and (len(plans)!=1 or args.repeat!=1): raise ValueError('Explicit run-id requires one run')
            result=[]
            for plan in plans:
                for _ in range(args.repeat):
                    path, code = runner.run(plan['case_id'],plan['condition_id'],args.run_id)
                    result.append({'path':str(path),'exit_code':code})
            print(json.dumps(result,ensure_ascii=False,indent=2))
            return int(any(r['exit_code'] for r in result))
    elif args.command=='verify':
        result = export_run(root,args.run,inside(root,args.out)) if args.out else inspect_run(root,args.run)[0]
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='PASS' else 1
    elif args.command=='aggregate': result=aggregate(root,inside(root,args.out),args.case)
    elif args.command=='evaluation-init': result={'path':str(init_evaluation(root,args.run,args.evaluation_id))}
    else:
        validate_evaluation(root,read(inside(root,args.file))); result={'status':'VALID'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0
