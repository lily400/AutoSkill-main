"""Determine Scrapy feed export default overwrite behavior by backend.

Supported backends:
- Local filesystem (absolute paths or file:// URIs): overwrite defaults to True.
- FTP (ftp://): overwrite defaults to True.
- S3 (s3://): overwrite defaults to False.
- Google Cloud Storage (gs://): overwrite defaults to False.
- Standard output (stdout:): overwrite defaults to False.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite setting for a feed URI."""
    if uri in {"stdout:", "stdout"}:
        return False

    if uri.startswith("/"):
        return True

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        return True
    if scheme == "ftp":
        return True
    if scheme == "s3":
        return False
    if scheme == "gs":
        return False

    raise ValueError(f"Unsupported feed URI scheme: {scheme or uri!r}")
