import socket
from contextlib import closing

__all__ = ["is_port_binded"]


def is_port_binded(host: str, port: int):
    """
    Test the service availability by a connection test.

    Args:
        host (str): host address
        port (int): target port

    Note:
        This does not guarantee the service binding to the port is our
        service-of-interest. Please tested it after establish connection with it.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except ConnectionRefusedError:
        return False


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
