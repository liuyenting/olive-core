from olive.devices import AcustoOpticalModulator
from olive.devices.protocols import Serial

__all__ = ["MultiDigitalSynthesizer"]


class MultiDigitalSynthesizer(Serial, AcustoOpticalModulator):
    def __init__(self):
        super().__init__()

    @classmethod
    def discover(cls):
        pass

    def initialize(self, port, timeout=500):
        """
        Initialize the synthesizer.

        Args:
            port (str): device name
            timeout (int): timeout in mss
        """
        timeout /= 1000

        # SerialDevice.initialize(self, port, read_timeout=timeout, write_timeout=timeout)
        AcustoOpticalModulator.initialize(self)

    def close(self):
        super().close()

    def enumerate_attributes(self):
        pass

    def get_attribute(self, name):
        pass

    def set_attribute(self, name, value):
        pass
