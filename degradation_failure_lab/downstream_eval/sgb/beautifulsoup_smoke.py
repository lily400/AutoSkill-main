"""Compatibility entry for the grouped BeautifulSoup Task-037 smoke module."""
import sys

from .task_adapters.beautifulsoup037 import smoke as _implementation

if __name__ == '__main__':
    raise SystemExit(_implementation.main())

sys.modules[__name__] = _implementation
