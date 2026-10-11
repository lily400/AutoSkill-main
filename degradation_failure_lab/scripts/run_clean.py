"""Deprecated compatibility shim; use ``python scripts/lab.py run``."""
from pathlib import Path
import sys
LAB = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0,str(LAB/'src'))

if __name__=='__main__':
    from degradation_lab.cli import main
    sys.stdout.reconfigure(encoding='utf-8')
    print('DEPRECATED: use scripts/lab.py run --case case001_qsv_select --condition clean', file=sys.stderr)
    sys.argv[1:1] = ['run', '--case', 'case001_qsv_select', '--condition', 'clean']
    raise SystemExit(main())
