"""Determine Scrapy feed export default overwrite behavior.

Supported built-in backends and defaults:
- local filesystem (file:///... or absolute /path): overwrite=False
- FTP (ftp://...): overwrite=True
- S3 (s3://...): overwrite=True
- GCS (gs://...): overwrite=True
- stdout (stdout:): overwrite=False

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite setting for a feed URI."""
    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    if uri.startswith("/"):
        return False

    if uri == "stdout:" or uri.startswith("stdout:"):
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme

    if scheme == "file":
        return False
    if scheme in {"ftp", "s3", "gs"}:
        return True

    raise ValueError(f"Unsupported feed URI scheme: {scheme or 'missing'}")
