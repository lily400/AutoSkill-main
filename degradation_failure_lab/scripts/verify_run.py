"""Deprecated compatibility shim; use ``python scripts/lab.py verify``."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB/'src'))
from degradation_lab.cli import main


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    if '--run' in args:
        index = args.index('--run') + 1
        args[index] = Path(args[index]).name
        if '--out' not in args:
            args.extend(['--out', 'results/exports/' + args[index]])
    print('DEPRECATED: use scripts/lab.py verify', file=sys.stderr)
    sys.argv[1:] = ['verify', *args]
    raise SystemExit(main())
