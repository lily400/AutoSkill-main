"""Resolve Scrapy feed export default overwrite behavior.

Supported built-in backends:
- Local filesystem ("file:///tmp/export.json" or absolute path "/tmp/export.json"): default overwrite is False.
- FTP ("ftp://server/export.json"): default overwrite is True.
- Amazon S3 ("s3://bucket/export.json"): default overwrite is True.
- Google Cloud Storage ("gs://bucket/export.json"): default overwrite is True.
- Standard output ("stdout:"): treated as a built-in feed target with overwrite defaulting to False.

Unsupported URI schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's default overwrite flag for a built-in feed URI."""

    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    if uri.startswith("/"):
        return False

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        # Accept file:///absolute/path or file:/absolute/path style URIs.
        if parsed.netloc not in ("", "localhost"):
            raise ValueError(f"unsupported file URI: {uri}")
        return False

    if scheme in {"ftp", "s3", "gs"}:
        return True

    if scheme == "stdout":
        return False

    raise ValueError(f"unsupported feed URI scheme: {scheme or uri}")
