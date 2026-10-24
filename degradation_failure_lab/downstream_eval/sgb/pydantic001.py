"""Compatibility entry for the grouped Pydantic001 engineering demonstration."""
import sys

from .task_adapters.pydantic001 import demo as _implementation

if __name__ == '__main__':
    raise SystemExit(_implementation.main())

sys.modules[__name__] = _implementation
