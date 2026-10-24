"""Resolve Scrapy feed export default overwrite behavior for built-in storage backends.

Supported built-in defaults:
- Local filesystem (file:///... or absolute paths): overwrite=False
- FTP (ftp://...): overwrite=True
- S3 (s3://...): overwrite=True
- GCS (gs://...): overwrite=True
- Standard output (stdout:): overwrite=False
Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI."""
    if not isinstance(uri, str):
        raise TypeError("uri must be a string")

    if uri.startswith("stdout:"):
        return False

    parsed = urlparse(uri)

    if parsed.scheme == "":
        # Treat absolute local paths like /tmp/export.json as filesystem feeds.
        if uri.startswith("/"):
            return False
        raise ValueError(f"Unsupported feed URI scheme in {uri!r}")

    if parsed.scheme == "file":
        return False
    if parsed.scheme == "ftp":
        return True
    if parsed.scheme == "s3":
        return True
    if parsed.scheme == "gs":
        return True

    raise ValueError(f"Unsupported feed URI scheme in {uri!r}")
