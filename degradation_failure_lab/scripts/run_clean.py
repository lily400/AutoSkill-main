"""Legacy convenience entry; all real execution now uses the common runner."""
from pathlib import Path
import sys
LAB = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0,str(LAB/'src'))
from degradation_lab.runner import validate_config

if __name__=='__main__':
    from degradation_lab.cli import main
    sys.stdout.reconfigure(encoding='utf-8')
    # Old P0 configs/snapshots stay readable; new generation is case-driven.
    sys.argv[1:1] = ['run', '--case', 'case001_qsv_select', '--condition', 'clean']
    raise SystemExit(main())
