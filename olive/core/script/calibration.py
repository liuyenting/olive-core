from olive.core.script import Script
from olive.devices import AcustoOpticalModulator, PowerSensor, SoftwareSequencer


class AOTFCalibration(Script):
    """
    Automagically calibrate AOTF frequencies and power range.
    """

    sequencer = SoftwareSequencer

    meter = PowerSensor
    aotf = AcustoOpticalModulator

    # TODO how to map functions?

    def setup(self):
        pass

    def loop(self):
        pass
