"""Compatibility command: read-only verification, external sidecar exports."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB/'src'))
from degradation_lab.artifacts import export_run


def verify(run):
    # Existing scripts\verify_run.py --run <old path> remains supported.
    return export_run(LAB, Path(run).name, LAB/'results/exports'/Path(run).name)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(); p.add_argument('--run',required=True)
    args=p.parse_args(); result=verify(Path(args.run))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
