from asyncio import Condition
import logging
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
    in_use: bool = field(init=False)

    def __post_init__(self):
        self.condition = Condition()
        self.in_test = False
        self.in_use = False


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
            self._ports[port] = SerialPort(port)

        logger.debug(f"{len(self._ports)} serial port(s) discovered")

    async def request_port(self, port):
        assert port in self._ports, f'"{port}" is not in the record'

        serial_port = self._ports[port]

        logger.debug(f'requesting "{port}"...')
        async with serial_port.condition:
            if serial_port.in_use:
                # someone can already use this port, stop trying
                raise PortAlreadyAssigned
            else:
                if serial_port.in_test:
                    # someone is testing, wait for them
                    logger.debug(f"waiting for other tests...")
                    await serial_port.condition.wait()
                    # TODO condition object requires further testing
                else:
                    logger.debug(f"port acquired")
                    # no one is testing it, let's go
                    serial_port.in_test = True
                    return port

    async def mark_port(self, port):
        serial_port = self._ports[port]

        logger.debug(f'"{port}" marked')
        async with serial_port.condition:
            serial_port.in_test = False
            serial_port.in_use = True

            # tell others, but not releasing the lock
            serial_port.condition.notify_all()

    async def release_port(self, port):
        assert port in self._ports, f'"{port}" is not in the record'

        serial_port = self._ports[port]

        logger.debug(f'"{port}" released')
        async with serial_port.condition:
            serial_port.in_test = False
            serial_port.in_use = False
