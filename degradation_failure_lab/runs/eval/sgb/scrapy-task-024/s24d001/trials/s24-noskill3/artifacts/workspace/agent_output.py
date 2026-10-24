"""Resolve Scrapy feed export default overwrite behavior for built-in storages.

Supported backends:
- Local filesystem (absolute paths and file:/// URIs): overwrite by default.
- FTP: do not overwrite by default.
- S3: do not overwrite by default.
- GCS/GS: do not overwrite by default.
- stdout: do not overwrite by default.
"""

from __future__ import annotations

from urllib.parse import urlsplit


def default_feed_overwrite(uri: str) -> bool:
    """Return Scrapy's default feed overwrite behavior for a feed URI.

    Raises:
        ValueError: If the URI scheme is unsupported.
    """
    if not isinstance(uri, str) or not uri:
        raise ValueError("Unsupported feed URI")

    # Absolute local filesystem paths are treated as local file feed URIs.
    if uri.startswith("/"):
        return True

    parsed = urlsplit(uri)
    scheme = parsed.scheme.lower()

    if scheme == "file":
        return True
    if scheme in {"ftp", "s3", "gs", "stdout"}:
        return False

    raise ValueError(f"Unsupported feed URI scheme: {scheme or uri}")
