import asyncio
import logging

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
        loop = asyncio.get_event_loop()

        ports = [info.device for info in list_ports.comports()]

        async def batch_initialize():
            futures = []
            for port in ports:
                dut = cls()
                future = loop.run_in_executor(cls.executor, dut.initialize, port)
                futures.append(future)
            await asyncio.wait(fs={futures[0]}, return_when=asyncio.ALL_COMPLETED)
        loop.run_until_complete(batch_initialize())

        # TODO close all devices

    def initialize(self, port, baudrate=19200, timeout=500):
        """
        Initialize the synthesizer.

        Args:
            port (str): device name
            baudrate (int): baud rate
            timeout (int): timeout in ms
        """
        logger.debug(f'initializing "{port}"')

        timeout /= 1000

        serial = Serial(
            port=port, baudrate=baudrate, timeout=timeout, write_timeout=timeout
        )
        self._find_version(serial)

        self._handle = serial
        super().initialize()

    def close(self):
        # TODO flush first
        self.handle.close()

        super().close()

    def enumerate_attributes(self):
        pass

    def get_attribute(self, name):
        pass

    def set_attribute(self, name, value):
        pass

    @property
    def handle(self):
        return self._handle

    def _find_version(self, serial):
        import time

        time.sleep(5)
