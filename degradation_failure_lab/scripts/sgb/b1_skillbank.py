"""Zero-model SkillBank planning, frozen references and consumer bindings."""
from pathlib import Path
import sys
LAB=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.skillbank import main

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main(LAB))
