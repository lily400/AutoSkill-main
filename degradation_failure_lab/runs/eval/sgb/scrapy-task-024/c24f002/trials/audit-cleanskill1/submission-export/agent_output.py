"""Determine Scrapy feed export default overwrite behavior.

Supported built-in backends:
- Local filesystem (file:// URIs and absolute paths): overwrite defaults to False.
- FTP (ftp://): overwrite defaults to True.
- Amazon S3 (s3://): overwrite defaults to True.
- Google Cloud Storage (gs://): overwrite defaults to True.
- Standard output (stdout:): overwrite defaults to False.

Unsupported schemes raise ValueError.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's built-in default overwrite value for a feed URI."""

    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    # Absolute filesystem paths have no scheme and should be treated as local files.
    if not scheme:
        if uri.startswith("/"):
            return False
        raise ValueError(f"Unsupported feed URI scheme in {uri!r}")

    if scheme == "file":
        return False
    if scheme == "ftp":
        return True
    if scheme == "s3":
        return True
    if scheme == "gs":
        return True
    if scheme == "stdout":
        return False

    raise ValueError(f"Unsupported feed URI scheme: {scheme}")
