"""Scrapy feed export default overwrite behavior.

Supported backends:
- file:///... and absolute local paths: overwrite by default.
- ftp://...: do not overwrite by default.
- s3://...: do not overwrite by default.
- gs://...: do not overwrite by default.
- stdout:: do not overwrite by default.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI."""
    if not isinstance(uri, str) or not uri:
        raise ValueError("Unsupported feed URI")

    # Absolute local path without scheme is treated as a file backend.
    if uri.startswith("/"):
        return True

    if uri == "stdout:" or uri == "stdout":
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme

    if scheme == "file":
        return True
    if scheme in {"ftp", "s3", "gs"}:
        return False

    raise ValueError(f"Unsupported feed URI scheme: {scheme or uri}")
