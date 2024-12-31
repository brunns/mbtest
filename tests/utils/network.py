import logging
import socket

logger = logging.getLogger(__name__)


def internet_connection(host="8.8.8.8", port: int = 53, timeout: float = 1):
    """Check for internet connection.
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    from: https://stackoverflow.com/a/33117579/1073696
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    except OSError as ex:
        logger.warning("Unexpected", exc_info=ex)
        return False
    else:
        return True
