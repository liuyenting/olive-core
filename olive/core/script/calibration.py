from olive.core.devices import AcustoOptoModulator

from .base import Script


class AOTFCalibration(Script):
    """
    Automagically calibrate AOTF frequencies and power range.
    """

    aotf = AcustoOptoModulator

    def setup(self):
        pass

    def loop(self):
        pass
