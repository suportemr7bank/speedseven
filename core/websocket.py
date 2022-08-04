"""
Websocket
"""

import redis


def is_websocket_available():
    """
    Test if websocket broker service is available
    """
    r = redis.Redis(host="127.0.0.1", port="6379", socket_connect_timeout=1)
    try:
        return r.ping()
    except (redis.exceptions.ConnectionError, ConnectionRefusedError):
        return False
