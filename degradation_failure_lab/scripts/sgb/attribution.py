"""Audit an explicit historical pair without model, Agent, Docker or Oracle execution."""
import argparse
import json
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import inside, read
from downstream_eval.sgb.attribution import audit_pair, export_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True, help='Lab-relative pair/review JSON')
    parser.add_argument('--output', help='New lab-relative directory under results/sgb/attributions')
    args = parser.parse_args()
    spec = read(inside(LAB, args.spec))
    if args.output:
        report = export_report(LAB, spec, inside(LAB, args.output))
        result = {k: report[k] for k in ('analysis_id', 'comparability', 'task_difference')}
        result['report'] = str(inside(LAB, args.output) / 'report.md')
    else:
        result = audit_pair(LAB, spec)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
