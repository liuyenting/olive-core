from abc import abstractmethod
from collections import deque
from ctypes import c_uint8
from enum import auto, Enum
import logging
from multiprocessing.sharedctypes import RawArray

import numpy as np

from olive.core import Device

__all__ = ['BufferRetrieveMode', "Camera"]

logger = logging.getLogger(__name__)


class BufferRetrieveMode(Enum):
    Index = auto()  # return frame according to index
    Last = auto()  # return the latest acquired frame
    Next = auto()  # return next valid frame


class RingBuffer(object):
    """
    Buffer that mimics SimpleQueue object.

    Args:
        shape (tuple): shape of a frame
        frames (int, optional): number of frames
        dtype (dtype, optional): data type
    """

    def __init__(self, shape, nframes, dtype, allocator=lambda x: RawArray(c_uint8, x)):
        self._shape, self._dtype = shape, dtype

        # create raw arrays
        self._frames = [allocator(self.frame_size) for _ in range(nframes)]
        logger.info(f"buffer ALLOCATED, {nframes} frame(s), {shape}, {dtype}")

        # bookkeeping

    def qsize(self):
        """Number of frames await for retrieval."""
        return len(self._dirty)

    def empty(self):
        return len(self._dirty) == 0

    def flush(self):
        while not self.empty():
            self.push_clean(self.pop_dirty())

    def pop_dirty(self, block=True, timeout=None):
        """Return a frame to read."""
        return self._dirty.pop()

    def push_dirty(self, item):
        self._dirty.appendleft(item)

    def pop_clean(self, block=True, timeout=None):
        """Return a frame to write."""
        return self._clean.pop()

    def push_clean(self, item):
        self._clean.appendleft(item)

    ##

    @property
    def dtype(self):
        return self._dtype

    @property
    def frames(self):
        return self._frames

    @property
    def frame_size(self):
        (ny, nx), dtype = self.shape, self.dtype
        return (nx * ny) * np.dtype(dtype).itemsize

    @property
    def shape(self):
        return self._shape


class Camera(Device):
    def __init__(self, *args, **kwargs):
        self._buffer = None
        super().__init__(*args, **kwargs)

    """
    High level
    """

    def snap(self):
        """Capture a single image."""
        self.configure_acquisition(1)
        self.start_acquisition()

        self.get_image()
        frame = self._extract_frame()
        image = (
            np.frombuffer(frame, dtype=self.buffer.dtype)
            .reshape(self.buffer.shape)
            .copy()
        )
        self._release_frame(frame)

        self.stop_acquisition()
        self.unconfigure_acquisition()

        return image

    @abstractmethod
    def configure_grab(self):
        pass

    @abstractmethod
    def grab(self):
        """Perform an acquisition that loops continuously."""

    @abstractmethod
    def sequence(self, n_frames, out=None):
        """Acquire a specified number of images and then stops."""

    """
    Low level
    """

    def configure_acquisition(self, nframes, continuous=False):
        if continuous:
            self.configure_ring(nframes)

    def configure_ring(self, nframes):
        _, shape = self.get_roi()
        dtype = self.get_dtype()
        self._buffer = RingBuffer(shape, nframes, dtype)

    @abstractmethod
    def start_acquisition(self):
        """Starts an acquisition."""

    @abstractmethod
    def get_image(self, mode: BufferRetrieveMode, index=-1, copy=True, out=None):
        """
        Acquire specified frame.

        Args:
            mode (BufferRetrieveMode): TBD
            index (int): TBD
            copy (bool, optional): a copy will only be made if `out` is not specified
            out (array_like, optional): an array that can store the result
        """
        # reinterpret as a numpy array
        frame = self._extract_frame(mode, index)
        frame = np.frombuffer(frame, shape=self.buffer.shape, dtype=self.buffer.dtype)

        # store the value
        if out is None:
            out = frame.copy() if copy else frame
        else:
            out[:] = frame[:]
        return out

    @abstractmethod
    def _extract_frame(
        self, mode: BufferRetrieveMode = BufferRetrieveMode.Next, index=-1
    ):
        """Retrieve an acquired frame from the buffer WITHOUT making a copy."""

    def _release_frame(self, frame):
        """Release extracted frame, allowing it to be reused."""
        self.buffer.push_clean(frame)

    @abstractmethod
    def stop_acquisition(self):
        """Stops an acquistion."""

    def unconfigure_acquisition(self):
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
