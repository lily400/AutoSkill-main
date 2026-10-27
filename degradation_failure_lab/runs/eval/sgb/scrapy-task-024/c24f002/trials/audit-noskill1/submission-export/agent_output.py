"""Scrapy feed-export default overwrite behavior by backend.

Supported built-in backends:
- Local filesystem ("file:///..." and absolute paths like "/tmp/export.json"): defaults to overwrite.
- FTP ("ftp://..."): defaults to no overwrite.
- S3 ("s3://..."): defaults to no overwrite.
- GCS ("gs://..."): defaults to no overwrite.
- Standard output ("stdout:"): defaults to overwrite/streaming behavior.

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite behavior for a feed URI."""

    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    # Absolute local filesystem paths are treated as file backend URIs.
    if uri.startswith("/"):
        return True

    parsed = urlparse(uri)

    # Special-case stdout: which Scrapy treats as a supported built-in target.
    if uri == "stdout:" or (parsed.scheme == "stdout" and not parsed.netloc and not parsed.path):
        return True

    scheme = parsed.scheme
    if scheme == "file":
        return True
    if scheme in {"ftp", "s3", "gs"}:
        return False

    raise ValueError(f"Unsupported feed URI scheme: {scheme or uri!r}")
