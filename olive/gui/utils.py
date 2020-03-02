import socket

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
