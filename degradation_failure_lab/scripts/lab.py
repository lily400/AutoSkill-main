"""One entry point for every source, case, condition, run and review."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from degradation_lab.cli import main

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    try: raise SystemExit(main())
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError) as e:
        print(type(e).__name__ + ': ' + str(e), file=sys.stderr)
        raise SystemExit(2)
