"""Resolve Scrapy feed export default overwrite behavior for built-in storages.

Supported backends:
- Local filesystem (absolute paths and file:// URIs): default overwrite is False.
- FTP (ftp://): default overwrite is False.
- S3 (s3://): default overwrite is True.
- Google Cloud Storage (gs://): default overwrite is True.
- stdout: default overwrite is False.

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's default overwrite behavior for a feed URI."""
    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    # Absolute local paths such as /tmp/export.json are treated as local files.
    if uri.startswith("/"):
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        return False
    if scheme == "ftp":
        return False
    if scheme == "s3":
        return True
    if scheme == "gs":
        return True
    if scheme == "stdout":
        return False

    raise ValueError(f"Unsupported feed URI scheme: {scheme or 'unknown'}")
