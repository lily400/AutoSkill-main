"""Compatibility entry for the grouped BeautifulSoup Task-037 adapter module."""
import sys

from .task_adapters.beautifulsoup037 import adapter as _implementation

sys.modules[__name__] = _implementation
