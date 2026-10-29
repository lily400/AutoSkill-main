"""Zero-model Family catalog, source mapping and runtime configuration CLI."""
from pathlib import Path
import sys

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB/'src')]

from degradation_lab.family import main

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main(LAB))
