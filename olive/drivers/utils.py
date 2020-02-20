from asyncio import Lock
import logging
from typing import Iterable

from serial.tools import list_ports

from olive.utils import Singleton

__all__ = ["SerialPortManager"]

logger = logging.getLogger(__name__)


class SerialPortManager(metaclass=Singleton):
    def __init__(self):
        self._ports = dict()
        self.refresh()

    ##

    def list_ports(self) -> Iterable[str]:
        return tuple(self._ports.keys())

    def refresh(self):
        ports = [port.device for port in list_ports.comports()]

        # remove old ports
        old_ports = set(self._ports.keys()) - set(ports)
        for port in old_ports:
            assert not self._ports[
                port
            ].locked(), "serial port still locked, but the OS cannot find it"
            del self._ports[port]

        # add new ports
        new_ports = set(ports) - set(self._ports.keys())
        for port in new_ports:
            self._ports[port] = Lock()

        logger.debug(f"{len(self._ports)} serial port(s) discovered")

    async def request_port(self, port):
        assert port in self._ports, f'"{port}" is not in the record'

        logger.debug(f'requesting "{port}"...')
        lock = self._ports[port]
        await lock.acquire()

        return port

    def release_port(self, port):
        assert port in self._ports, f'"{port}" is not in the record'

        logger.debug(f'"{port}" released')
        lock = self._ports[port]
        lock.release()
