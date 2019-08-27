import asyncio
import logging
import re
from typing import Union

from serial import Serial
from serial.tools import list_ports

from olive.core import Driver
from olive.devices import AcustoOpticalModulator
from olive.devices.errors import UnsupportedDeviceError

__all__ = ["MultiDigitalSynthesizer"]

logger = logging.getLogger(__name__)


class MDSnC(AcustoOpticalModulator):
    def __init__(self, driver):
        super().__init__(driver)
        self._handle = None

    ##

    def open(self, port, baudrate=19200, timeout=1000):
        """
        Open connection with the synthesizer.

        Args:
            port (str): device name
            baudrate (int): baud rate
            timeout (int): timeout in ms

        Notes:
            For virtual COM, baudrate does not really matter, 19200 bps is the default
            value for RS232 link.
        """
        if timeout:
            timeout /= 1000
        self._handle = Serial(
            port=port, baudrate=baudrate, timeout=timeout, write_timeout=timeout
        )

        # use version string to probe validity
        self._get_version()

        super().open()

    def close(self):
        # TODO revert to manual control
        # TODO flush output
        self.handle.close()
        super().close()

    ##

    def enumerate_properties(self):
        return ("version",)

    def get_property(self, name):
        func = getattr(self, f"_get_{name}")
        return func()

    def set_property(self, name, value):
        pass

    ##

    def get_frequency(self, channel):
        pass

    def set_frequency(self, channel, frequency):
        pass

    def get_power(self, channel):
        pass

    def set_power(self, channel, power):
        pass

    @property
    def handle(self):
        return self._handle

    def _get_version(self, pattern=r"MDS [vV]([\w\.]+).*//"):
        # CR to trigger message dump
        self.handle.write(b"\r")

        data = self.handle.read_until("?").decode("utf-8")
        print(f"** {self.handle.name} **")
        print(data)
        print("*****")
        tokens = re.search(pattern, data, flags=re.MULTILINE)
        if tokens:
            return tokens.group(1)
        else:
            raise UnsupportedDeviceError


class MultiDigitalSynthesizer(Driver):
    def __init__(self):
        super().__init__()

    ##

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def enumerate_devices(self) -> Union[MDSnC]:
        loop = asyncio.get_event_loop()

        async def test_port(port):
            device = MDSnC(self)

            def _test_port(port):
                logger.info(f"testing {port}...")
                device.open(port)
                device.close()

            return await loop.run_in_executor(device.executor, _test_port, port)

        ports = [info.device for info in list_ports.comports()]
        testers = [test_port(port) for port in ports]
        done, pending = loop.run_until_complete(asyncio.gather(*testers))

        devices = []
        for port, exception in done:
            if isinstance(exception, UnsupportedDeviceError):
                continue
            elif exception is None:
                devices.append(port)
            else:
                # unknown exception occurred
                raise exception
        return tuple(devices)

    ##

    def enumerate_attributes(self):
        pass

    def get_attribute(self, name):
        pass

    def set_attribute(self, name, value):
        pass

