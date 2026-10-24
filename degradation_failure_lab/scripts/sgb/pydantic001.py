"""Zero-model source/case/Oracle demo. Run from the project root with Docker available."""
from pathlib import Path
import sys

LAB=Path(__file__).resolve().parents[2]
sys.dont_write_bytecode=True
sys.path[:0]=[str(LAB),str(LAB/'src')]
from downstream_eval.sgb.pydantic001 import main

if __name__=='__main__':raise SystemExit(main())
