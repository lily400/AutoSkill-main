"""Resolve Scrapy feed export default overwrite behavior for built-in storages.

Supported backends:
- Local filesystem (absolute paths and file:// URIs): default overwrite is False.
- FTP (ftp://): default overwrite is True.
- Amazon S3 (s3://): default overwrite is True.
- Google Cloud Storage (gs://): default overwrite is True.
- Standard output (stdout:): default overwrite is True.

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite value for a feed URI."""
    if uri == "stdout:" or uri.startswith("stdout:"):
        return True

    parsed = urlparse(uri)

    if parsed.scheme in ("", "file"):
        return False
    if parsed.scheme in {"ftp", "s3", "gs"}:
        return True

    raise ValueError(f"Unsupported feed URI scheme: {parsed.scheme or 'local'}")
