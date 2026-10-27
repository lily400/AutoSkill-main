"""Built-in backend overwrite defaults from the supplied source document."""
from urllib.parse import urlsplit as _urlsplit

def default_feed_overwrite(uri):
    if not isinstance(uri, str):
        raise TypeError("uri must be a string")
    if not uri:
        raise ValueError("uri must not be empty")
    if uri.startswith("/"):
        return False
    defaults = {"file": False, "ftp": False, "s3": True, "gs": True, "stdout": False}
    scheme = _urlsplit(uri).scheme
    if scheme not in defaults:
        raise ValueError("unsupported scheme")
    return defaults[scheme]
