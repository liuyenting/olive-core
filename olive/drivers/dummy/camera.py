import logging
import os

import imageio
import numpy as np

from olive.core import Driver, DeviceInfo
from olive.devices import Camera

__all__ = ["PseudoCamera"]

logger = logging.getLogger(__name__)


class PseudoCamera(Camera):
    def __init__(self, sample="t1-head"):
        super().__init__()

        self._sample = sample
        self._buffer = None
        self._load_sample_to_buffer(sample)

    ##

    def test_open(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

    ##

    def info(self):
        return DeviceInfo(
            version="0.0", vendor="olive", model=self.sample, serial_number="DEADBEEF"
        )

    def enumerate_properties(self):
        pass

    ##

    def snap(self):
        pass

    def configure_grab(self):
        pass

    def grab(self):
        pass

    def sequence(self):
        pass

    ##

    def configure_acquisition(self):
        pass

    def start_acquisition(self):
        pass

    def get_image(self):
        pass

    def stop_acquisition(self):
        pass

    def unconfigure_acquisition(self):
        pass

    ##

    @property
    def buffer(self):
        return self._buffer

    @property
    def sample(self):
        return self._sample

    ##

    def _load_sample_to_buffer(self):
        """Load raw files from builtin resource pack to buffer."""
        filename, shape = {"t1-head": ("t1-head", (127, 256, 256))}[self.sample]
        res_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        path = os.path.join(res_dir, f"{filename}.raw")
        self._buffer = np.memmap(path, dtype=np.uint16, mode="r", shape=shape)


class PseudoCameraDriver(Driver):
    def __init__(self):
        super().__init__()

    ##

    def initialize(self):
        # TODO list contents in the resouce pack
        pass

    def shutdown(self):
        super().shutdown()

    def enumerate_devices(self) -> PseudoCamera:
        # TODO one camera only
        pass

