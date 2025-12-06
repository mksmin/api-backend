import ipaddress
import socket
from urllib.parse import urlparse

from misc.image.types import ALLOWED_SCHEMES


def _is_safe_url(
    url: str,
) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return False

        except (OSError, ValueError):
            blocked = (
                "localhost",
                "127.0.0.1",
            )
            if hostname.lower() in blocked:
                return False

    except Exception:  # noqa: BLE001
        return False

    return True
