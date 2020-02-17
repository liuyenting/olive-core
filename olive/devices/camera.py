from abc import abstractmethod
from ctypes import c_uint8
from enum import auto, Enum
import logging
from math import floor
from multiprocessing.sharedctypes import RawArray

import numpy as np
from psutil import virtual_memory
import trio

from .base import Device

__all__ = ["BufferRetrieveMode", "Camera"]

logger = logging.getLogger(__name__)


class BufferRetrieveMode(Enum):
    Latest = auto()  # return the latest acquired frame
    Next = auto()  # return next valid frame


class FrameBuffer(object):
    """
    Buffer that mimics SimpleQueue object.

    Args:
        shape (tuple): shape of a frame
        frames (int, optional): number of frames
        dtype (dtype, optional): data type
    """

    def __init__(self, shape, dtype, nframes=1):
        assert nframes >= 1, "frames in a ring buffer should be >= 1"

        self._shape, self._dtype = shape, dtype

        (ny, nx), dtype = self.shape, self.dtype
        nbytes = (nx * ny) * np.dtype(dtype).itemsize
        self._frames = [RawArray(c_uint8, nbytes) for _ in range(nframes)]

        self._read_index, self._write_index = 0, 0
        self._is_full = False

        self.reset()

    ##

    def reset(self):
        self._read_index, self._write_index = 0, 0
        self._is_full = False

    def full(self):
        return self._is_full

    def empty(self):
        return (not self.full()) and (self._read_index == self._write_index)

    def write(self, frame):
        if self.full():
            raise IndexError("not enough internal buffer")
        self.frames[self._write_index][:] = frame

        self._write_index = (self._write_index + 1) % self.capacity()
        self._is_full = self._read_index == self._write_index

    def read(self):
        if self.empty():
            return None
        frame = self.frames[self._read_index]

        self._read_index = (self._read_index + 1) % self.capacity()
        self._is_full = False

        return frame

    def capacity(self):
        """Returns the maximum capacity of the buffer."""
        return len(self.frames)

    def size(self):
        if self.full():
            return self.capacity()
        else:
            size = self._read_index - self._write_index
            if size < 0:
                return self.capacity() + size
            else:
                return size

    ##

    @property
    def dtype(self):
        return self._dtype

    @property
    def frames(self):
        return self._frames

    @property
    def shape(self):
        return self._shape


class Camera(Device):
    """
    Args:
        max_memory_size (optional): maximum buffer memory size in bytes or percentage

    Attributes:
        continuous (bool): camera will continuously acquiring
    """

    def __init__(self, *args, max_memory_size=0.1, **kwargs):
        super().__init__(*args, **kwargs)

        self._buffer, self._max_memory_size = None, None
        self.set_max_memory_size(max_memory_size)

        self._continous = False

    """
    High level
    """

    async def snap(self, out=None):
        """Capture a single image."""
        # NOTE ring buffer requires minimally of 2 frames
        await self.configure_acquisition(2)

        self.start_acquisition()
        out = await self.get_image(out=out)
        self.stop_acquisition()

        await self.unconfigure_acquisition()

        return out

    async def grab(self):
        """Perform an acquisition that loops continuously."""
        # TODO probe the system for optimal size
        await self.configure_acquisition(100, continuous=True)

        self.start_acquisition()
        with trio.CancelScope():
            while True:
                yield await self.get_image(mode=BufferRetrieveMode.Latest, copy=False)
        self.stop_acquisition()

        await self.unconfigure_acquisition()

    async def sequence(self, frames):
        """Acquire a specified number of images and then stops."""
        await self.configure_acquisition(frames)

        # prepare the buffer
        if isinstance(frames, np.ndarray):
            n_frames = frames.shape[0]
            logger.info(f"acquire {n_frames} frames to user buffer")
        else:
            n_frames = int(frames)
            frames = np.empty((n_frames,) + self.buffer.shape, dtype=self.buffer.dtype)
            logger.info(f"requested {n_frames} frames")

        self.start_acquisition()
        for i in range(n_frames):
            yield await self.get_image(mode=BufferRetrieveMode.Next, out=frames[i, ...])
        self.stop_acquisition()

        await self.unconfigure_acquisition()

    """
    Low level
    """

    async def configure_acquisition(self, n_frames, continuous=False):
        await self.configure_ring(n_frames)

        # continuous when
        #   - specified explicitly
        #   - limited buffer
        self._continous = continuous or (n_frames != len(self.buffer.frames))

    async def configure_ring(self, n_frames):
        (_, shape), dtype = self.get_roi(), self.get_dtype()

        ny, nx = shape
        nbytes = (nx * ny) * np.dtype(dtype).itemsize

        available_size = self.get_max_memory_size()
        if available_size < nbytes * n_frames:
            n_frames = available_size // nbytes
            logger.warning(
                f"exceeds memory limit ({available_size} bytes), coerce to {n_frames} frames"
            )
        self._buffer = FrameBuffer(shape, dtype, n_frames)

    @abstractmethod
    def start_acquisition(self):
        """Starts an acquisition."""

    async def get_image(
        self, mode: BufferRetrieveMode = BufferRetrieveMode.Next, copy=True, out=None
    ):
        """
        Acquire specified frame.

        Args:
            TBA
        """
        # reinterpret as a numpy array
        frame = await self._get_image_data(mode)

        # store the value
        if out is None:
            out = frame.copy() if copy else frame
        else:
            out[:] = frame[:]
        return out

    async def _get_image_data(self, mode: BufferRetrieveMode = BufferRetrieveMode.Next):
        """Retrieve a frame from the host-side ring buffer WITHOUT making a copy."""
        frame = await self._extract_frame(mode)
        return np.frombuffer(frame, dtype=self.buffer.dtype).reshape(self.buffer.shape)

    @abstractmethod
    async def _extract_frame(self, mode: BufferRetrieveMode):
        """Retrieve raw frame data from the camera."""

    @abstractmethod
    def stop_acquisition(self):
        """Stops an acquistion."""

    async def unconfigure_acquisition(self):
        """Release resources used in the acquisition."""
        self._buffer = None
        logger.debug("buffer UNREFERENCED")

    """
    Properties
    """

    @abstractmethod
    def get_dtype(self):
        pass

    @abstractmethod
    def get_exposure_time(self):
        pass

    @abstractmethod
    def set_exposure_time(self, value):
        pass

    def get_max_memory_size(self):
        return self._max_memory_size

    def set_max_memory_size(self, max_memory_size):
        if isinstance(max_memory_size, float):
            total_memory_size = virtual_memory().total
            max_memory_size = floor(max_memory_size * total_memory_size)
        self._max_memory_size = max_memory_size

    @abstractmethod
    def get_max_roi_shape(self):
        pass

    @abstractmethod
    def get_roi(self):
        """Set region of interest."""

    @abstractmethod
    def set_roi(self, pos0=None, shape=None):
        """
        Set region of interest.

        - If `pos0` is None, `shape` is centered in the sensory boundary
        - If `shape` is None, `shape` will extend to the maximum sensor boundary.
        - If both `pos0` and `shape` are None, full sensor range is used.

        Args:
            pos0 (tuple of int, optional): top-left position
            shape (tuple of int, optional): shape of the region
        """

    ##

    @property
    def buffer(self):
        return self._buffer

    @property
    def continuous(self):
        return self._continous
