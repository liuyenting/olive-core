from olive.devices import AcustoOpticalModulator

from olive.core.script import Script


class LLSM(Script):
    """
    Script for Lattice LightSheet Microscopes (LLSM).
    """

    aotf = AcustoOpticalModulator
    # camera = Camera # TODO debug failed here due to hamamatsu

    def setup(self):
        pass

    def loop(self):
        pass
