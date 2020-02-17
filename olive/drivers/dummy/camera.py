import glob
import logging
import os
from typing import Iterable

import numpy as np

from olive.drivers.base import Driver
from olive.devices.base import DeviceInfo
from olive.devices import Camera

__all__ = ["PseudoCamera", "PseudoCameraDriver"]

logger = logging.getLogger(__name__)


class PseudoCamera(Camera):
    def __init__(self, driver, path):
        super().__init__(driver)
        self._path = path

    ##

    async def test_open(self):
        pass

    async def _open(self):
        pass

    async def close(self):
        pass

    ##

    async def enumerate_properties(self):
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
    def info(self):
        return DeviceInfo(
            version="0.0", vendor="olive", model=self.sample, serial_number="DEADBEEF"
        )

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
        self._resources = []

    ##

    def initialize(self):
        root = os.path.join(os.path.dirname(__file__), "resources")
        self._resources.extend(glob.glob(os.path.join(root, "*.tif")))

    def shutdown(self):
        self._resources = []

    async def enumerate_devices(self) -> Iterable[PseudoCamera]:
        return [PseudoCamera(self, path) for path in self._resources]
