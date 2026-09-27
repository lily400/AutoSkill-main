"""Validate registered data and its immutable seal; never calls a model."""
import argparse
from pathlib import Path
from data_contracts import load_dataset, freeze_dataset

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--freeze',action='store_true')
    p.add_argument('--root',default=str(Path(__file__).resolve().parents[1])); a=p.parse_args(argv)
    if a.freeze: freeze_dataset(a.root)
    d=load_dataset(a.root)
    print(f"DATA_VALID cases={len(d['cases'])} families={len(d['families'])} variants={len(d['variants'])} tasks={len(d['tasks'])}")
    print('STRUCTURE_ONLY; semantic correctness and task success are not established')
    return 0
if __name__=='__main__': raise SystemExit(main())
