"""Scrapy feed export default overwrite behavior.

Supported built-in feed storage backends:
- Local filesystem (`file:///tmp/export.json` or absolute paths like `/tmp/export.json`): overwrite enabled by default.
- FTP (`ftp://server/export.json`): overwrite disabled by default.
- Amazon S3 (`s3://bucket/export.json`): overwrite disabled by default.
- Google Cloud Storage (`gs://bucket/export.json`): overwrite disabled by default.
- Stdout (`stdout:`): overwrite enabled by default.

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default feed overwrite setting for *uri*."""

    if not isinstance(uri, str) or not uri:
        raise ValueError("feed URI must be a non-empty string")

    # Absolute local paths are treated as local filesystem feed URIs.
    if uri.startswith("/"):
        return True

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        return True
    if scheme == "stdout":
        return True
    if scheme in {"ftp", "s3", "gs"}:
        return False

    raise ValueError(f"unsupported feed URI scheme: {scheme or uri!r}")
