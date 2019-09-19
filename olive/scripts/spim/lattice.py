import logging

from olive.core.script import Script
from olive.devices import AcustoOpticalModulator

__all__ = ["LatticeLightsheet"]

logger = logging.getLogger(__name__)


class LatticeLightsheet(Script):
    """
    Script for Lattice LightSheet Microscopes (LLSM).
    """

    aotf = AcustoOpticalModulator
    # camera = Camera # TODO debug failed here due to hamamatsu

    def setup(self):
        pass

    def loop(self):
        pass
