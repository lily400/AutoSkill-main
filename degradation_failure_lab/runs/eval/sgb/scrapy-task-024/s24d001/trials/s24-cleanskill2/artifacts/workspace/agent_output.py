"""Scrapy feed export overwrite defaults by backend.

Supported built-in backends:
- Local filesystem (file:///... or an absolute path): overwrite defaults to False.
- FTP (ftp://...): overwrite defaults to True.
- S3 (s3://...): overwrite defaults to True.
- Google Cloud Storage (gs://...): overwrite defaults to True.
- Standard output (stdout:): overwrite defaults to False.

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI."""

    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    if uri == "stdout:":
        return False

    # Absolute local paths are treated as the local filesystem backend.
    if uri.startswith("/"):
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme
    if scheme == "file":
        return False
    if scheme == "ftp":
        return True
    if scheme == "s3":
        return True
    if scheme == "gs":
        return True

    raise ValueError(f"Unsupported feed URI scheme: {scheme or 'none'}")
