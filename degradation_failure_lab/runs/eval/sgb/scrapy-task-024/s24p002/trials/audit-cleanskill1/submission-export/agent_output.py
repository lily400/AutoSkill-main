"""Resolve Scrapy feed export default overwrite behavior for built-in backends.

Supported defaults:
- Local filesystem (file:///... or absolute paths): overwrite=False
- FTP (ftp://...): overwrite=True
- S3 (s3://...): overwrite=True
- GCS (gs://...): overwrite=True
- Standard output (stdout:): overwrite=False
"""
from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI.

    Absolute paths are treated as local filesystem feeds.
    Unsupported schemes raise ValueError.
    """
    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    if uri == "stdout:" or uri.startswith("stdout:"):
        return False

    parsed = urlparse(uri)

    # Absolute Unix-like path: treat as local filesystem feed.
    if parsed.scheme == "" and uri.startswith("/"):
        return False

    scheme = parsed.scheme.lower()

    if scheme in {"", "file"}:
        return False
    if scheme in {"ftp", "s3", "gs"}:
        return True

    raise ValueError(f"Unsupported feed URI scheme: {scheme or 'missing'}")
