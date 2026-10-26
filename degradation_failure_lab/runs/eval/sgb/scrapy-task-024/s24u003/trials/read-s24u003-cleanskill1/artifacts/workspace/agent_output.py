"""Resolve Scrapy feed export default overwrite behavior.

Supported built-in backends:
- local filesystem (file:///tmp/export.json or /tmp/export.json): overwrite=False
- FTP (ftp://server/export.json): overwrite=True
- S3 (s3://bucket/export.json): overwrite=True
- GCS (gs://bucket/export.json): overwrite=True
- stdout (stdout:): overwrite=False

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's default overwrite behavior for a feed URI."""
    if not isinstance(uri, str):
        raise TypeError("uri must be a string")

    if uri == "stdout:" or uri == "stdout":
        return False

    # Absolute filesystem paths are treated as local file backend.
    if uri.startswith("/"):
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme

    if scheme == "file":
        return False
    if scheme in {"ftp", "s3", "gs"}:
        return True

    raise ValueError(f"Unsupported feed URI scheme: {scheme or 'none'}")
