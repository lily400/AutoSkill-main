"""Scrapy feed export overwrite defaults.

Supported built-in backends:
- file and absolute local paths: overwrite by default
- ftp: overwrite by default
- s3: do not overwrite by default
- gs: do not overwrite by default
- stdout: do not overwrite by default
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI."""
    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    # Treat absolute local paths as filesystem destinations.
    if uri.startswith("/"):
        return True

    parsed = urlparse(uri)
    scheme = parsed.scheme

    if scheme == "file":
        return True
    if scheme == "ftp":
        return True
    if scheme == "s3":
        return False
    if scheme == "gs":
        return False
    if scheme == "stdout":
        return False

    raise ValueError(f"unsupported feed URI scheme: {scheme or uri!r}")
