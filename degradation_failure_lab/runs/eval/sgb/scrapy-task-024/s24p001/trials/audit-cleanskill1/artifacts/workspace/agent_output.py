"""Scrapy feed export overwrite defaults by backend.

Supported built-in backends:
- Local filesystem (``file:///tmp/export.json`` or absolute paths like ``/tmp/export.json``): overwrite defaults to True.
- FTP (``ftp://server/export.json``): overwrite defaults to False.
- S3 (``s3://bucket/export.json``): overwrite defaults to False.
- GCS (``gs://bucket/export.json``): overwrite defaults to False.
- Standard output (``stdout:``): overwrite defaults to True.
"""

from __future__ import annotations

from urllib.parse import urlparse


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's default overwrite behavior for a feed URI.

    Parameters
    ----------
    uri:
        Feed URI or absolute local filesystem path.

    Returns
    -------
    bool
        The default value Scrapy uses for the ``overwrite`` option for the
        corresponding built-in feed storage backend.

    Raises
    ------
    ValueError
        If the URI scheme is unsupported.
    """

    if uri.startswith("/"):
        return True

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        return True
    if scheme == "ftp":
        return False
    if scheme == "s3":
        return False
    if scheme == "gs":
        return False
    if scheme == "stdout":
        return True

    raise ValueError(f"Unsupported feed URI scheme: {scheme or uri!r}")
