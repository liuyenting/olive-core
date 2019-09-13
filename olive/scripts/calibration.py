import logging

from scipy.optimize import minimize

from olive.core.script import Script, ChannelsFeature
from olive.devices import AcustoOpticalModulator, PowerSensor, SoftwareSequencer

__all__ = ["AOTFCalibration"]

logger = logging.getLogger(__name__)


class AOTFCalibration(Script, ChannelsFeature):
    """
    Automagically calibrate AOTF frequencies and power range.

    This script will calibrate modulation frequencies for selected channels.
    """

    sequencer = SoftwareSequencer

    aotf = AcustoOpticalModulator
    power = PowerSensor

    # TODO how to map functions?

    def setup(self):
        fmin, fmax = self.aotf.get_frequency_range()

        # set to mid-power range
        pmin, pmax = self.aotf.get_power_range()
        self.aotf.set_power(1, (pmin + pmax) / 2)

        def func(f):
            self.aotf.set_frequency(f)
            return self.power.readout()

        res = minimize(func, (fmin + fmax) / 2, "Nelder-Mead")
        opt_success = "SUCCESS" if res.success else "FAILED"
        logger.info(f"minimize {opt_success}, f={res.x}")

    def loop(self):
        pass
