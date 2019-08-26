import asyncio
import logging
import re

from serial import Serial
from serial.tools import list_ports

from olive.devices import AcustoOpticalModulator
from olive.devices.errors import UnsupportedDeviceError

__all__ = ["MultiDigitalSynthesizer"]

logger = logging.getLogger(__name__)


class MultiDigitalSynthesizer(AcustoOpticalModulator):
    def __init__(self):
        super().__init__()
        self._handle = None

    @classmethod
    def enumerate_devices(cls):
        async def test_port(loop, device, port):
            await device.initialize(port)
            await device.close()

        async def batch_test_port(loop, ports):
            return zip(
                ports,
                await asyncio.gather(
                    *[test_port(loop, cls(), port) for port in ports],
                    return_exceptions=True,
                ),
            )

        ports = [info.device for info in list_ports.comports()]
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(batch_test_port(loop, ports))
        return tuple(port for port, exception in results if exception is None)

    async def initialize(self, port, baudrate=9600, timeout=1000):
        """
        Initialize the synthesizer.

        Args:
            port (str): device name
            baudrate (int): baud rate
            timeout (int): timeout in ms
        """
        logger.debug(f'initializing "{port}"')

        if timeout:
            timeout /= 1000

        self._handle = Serial(
            port=port, baudrate=baudrate, timeout=timeout, write_timeout=timeout
        )
        version = await self._find_version()
        logger.debug(f"device version: {version}")

        await super().initialize()

    async def close(self):
        logger.debug(f'closing "{self.handle.port}"')
        # TODO flush first
        self.handle.close()

        await super().close()

    async def enumerate_attributes(self):
        pass

    async def get_attribute(self, name):
        pass

    async def set_attribute(self, name, value):
        pass

    @property
    def handle(self):
        return self._handle

    async def _find_version(self, pattern=r"MDS [vV]([\w\.]+).*//"):
        logger.info("finding version...")
        self.handle.write(b"\r")

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(self.executor, self.handle.read_until, "?")
        data = data.decode("utf-8")

        tokens = re.search(pattern, data, flags=re.MULTILINE)
        if tokens:
            return tokens.group(1)
        else:
            raise UnsupportedDeviceError
