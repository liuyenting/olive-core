from olive.devices import AcustoOpticalModulator
from olive.devices.protocols import SerialDevice

__all__ = ["MultiDigitalSynthesizer"]


class MultiDigitalSynthesizer(AcustoOpticalModulator, SerialDevice):
    pass
