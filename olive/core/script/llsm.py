from olive.core.devices import Camera, AcustoOptoModulator

from .base import Script


class LLSM(Script):
    """
    Script for Lattice LightSheet Microscopes (LLSM).
    """

    aotf = AcustoOptoModulator
    camera = Camera

    def setup(self):
        pass

    def loop(self):
        pass
