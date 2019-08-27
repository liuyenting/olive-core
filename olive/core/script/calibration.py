from olive.core.script import Script
from olive.devices import AcustoOpticalModulator


class AOTFCalibration(Script):
    """
    Automagically calibrate AOTF frequencies and power range.
    """

    aotf = AcustoOpticalModulator

    def setup(self):
        pass

    def loop(self):
        pass
