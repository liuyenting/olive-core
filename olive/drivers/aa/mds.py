from olive.devices import AcustoOpticalModulator
from olive.devices.protocols import SerialDevice

__all__ = ["MultiDigitalSynthesizer"]


class MultiDigitalSynthesizer(SerialDevice, AcustoOpticalModulator):
    def __init__(self):
        super().__init__()

    def initialize(self, port, timeout=500):
        """
        Initialize the synthesizer.

        Args:
            port (str): device name
            timeout (int): timeout in mss
        """
        timeout /= 1000
        SerialDevice.initialize(self, port, read_timeout=timeout, write_timeout=timeout)

        # AcustoOpticalModulator.initialize(self)
