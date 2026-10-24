"""Compatibility entry for the grouped BeautifulSoup Task-037 exports module."""
import sys

from .task_adapters.beautifulsoup037 import exports as _implementation

sys.modules[__name__] = _implementation
