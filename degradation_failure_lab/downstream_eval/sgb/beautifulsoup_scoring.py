"""Compatibility entry for the grouped BeautifulSoup Task-037 scoring module."""
import sys

from .task_adapters.beautifulsoup037 import scoring as _implementation

sys.modules[__name__] = _implementation
