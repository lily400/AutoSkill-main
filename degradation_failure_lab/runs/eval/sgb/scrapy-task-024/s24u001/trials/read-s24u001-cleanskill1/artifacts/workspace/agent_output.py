"""Resolve Scrapy feed export default overwrite behavior.

Supported built-in backends:
- local filesystem (absolute paths and file:// URIs): overwrite=False
- ftp:// URIs: overwrite=True
- s3:// URIs: overwrite=True
- gs:// URIs: overwrite=True
- stdout: URI: overwrite=False

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI."""
    if not isinstance(uri, str) or uri == "":
        raise ValueError("uri must be a non-empty string")

    if uri == "stdout:" or uri.startswith("stdout:"):
        return False

    if uri.startswith("/"):
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        return False
    if scheme in {"ftp", "s3", "gs"}:
        return True

    raise ValueError(f"unsupported feed URI scheme: {scheme or 'missing'}")
