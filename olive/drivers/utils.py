from asyncio import Condition
import logging
import typing
from typing import Iterable
from dataclasses import dataclass, field

from serial.tools import list_ports

from olive.utils import Singleton
from .error import PortAlreadyAssigned

__all__ = ["SerialPortManager"]

logger = logging.getLogger("olive.drivers.serialmanager")


@dataclass
class SerialPort:
    # port
    uri: str
    # lock condition
    condition: Condition = field(init=False)

    # port under test
    in_test: bool = field(init=False)
    # port already found assignment
    in_use_by: typing.Any = field(init=False)

    def __post_init__(self):
        self.condition = Condition()
        self.in_test = False
        self.in_use_by = None


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
            if self._ports[port].locked():
                logger.error(f'"{port}" is still locked, but the OS cannot find it')
            # not matter what, we need to remove their references
            del self._ports[port]

        # add new ports
        new_ports = set(ports) - set(self._ports.keys())
        for port in new_ports:
            self._ports[port] = SerialPort(port)

        logger.debug(f"{len(self._ports)} serial port(s) discovered")

    async def request_port(self, port, user):
        """
        Request a port to operate on.

        Args:
            port (str): port name
            user (object): the downstream user
        """
        assert port in self._ports, f'"{port}" is not in the record'

        serial_port = self._ports[port]

        async with serial_port.condition:
            # NOTE
            # Windows 6.0+ support 256 communications port devices
            #   https://superuser.com/a/496668
            for _ in range(256):
                if serial_port.in_test:
                    # 1) is someone testing it?
                    logger.debug(f'"{user}" is waiting for "{port}"...')
                    await serial_port.condition.wait()
                elif serial_port.in_use_by is not None:
                    # 2) port in use, am I the owner?
                    if serial_port.in_use_by == user:
                        return port
                    else:
                        # someone can already use this port, stop trying
                        raise PortAlreadyAssigned
                else:
                    # 3) I am the first one, grab it
                    logger.debug(f'"{port}" acquired by "{user}"')
                    serial_port.in_test = True
                    return port
            else:
                logger.error("maxium serial request trials reached")
                raise PortAlreadyAssigned(
                    f"maxium serial request trials reached, give up"
                )

    async def mark_port(self, port, user):
        """
        Mark the port to be owned by a user.

        Args:
            port (str): port name
            user (object): the downstream user
        """
        serial_port = self._ports[port]

        logger.debug(f'"{port}" is now owned by "{user}"')
        async with serial_port.condition:
            serial_port.in_test = False
            serial_port.in_use_by = user

            # tell others, but not releasing the lock
            serial_port.condition.notify_all()

    async def release_port(self, port):
        assert port in self._ports, f'"{port}" is not in the record'

        serial_port = self._ports[port]

        logger.debug(f'"{port}" released')
        async with serial_port.condition:
            serial_port.in_test = False
            serial_port.in_use_by = None
