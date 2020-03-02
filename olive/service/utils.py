import socket
from contextlib import closing

__all__ = ["find_free_port"]


def find_free_port():
    """
    Find a random free port on localhost.

    Returns:
        port (int): free port number

    Note:
        This operation is no necessary atomic.

    Reference:
        On localhost, how do I pick a free port number?
            https://stackoverflow.com/a/45690594
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("localhost", 0))
        # set sockopt so we can quickly reuse the socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
