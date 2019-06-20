# encoding=utf-8
import logging
import socket

logger = logging.getLogger(__name__)


def internet_connection(host="8.8.8.8", port=53, timeout=1):
    """
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      from: https://stackoverflow.com/a/33117579/1073696
      """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        logger.warn(ex)
        return False
