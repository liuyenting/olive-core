from abc import abstractmethod
from collections import deque
from ctypes import c_uint8
from enum import auto, Enum
import logging
from multiprocessing import Lock
from multiprocessing.sharedctypes import RawArray

import numpy as np

from olive.core import Device

__all__ = ["BufferRetrieveMode", "Camera"]

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

    def __init__(self, shape, dtype, nframes=1):
        self._shape, self._dtype = shape, dtype

        self._lock = Lock()

        (ny, nx), dtype = self.shape, self.dtype
        nbytes = (nx * ny) * np.dtype(dtype).itemsize
        self._frames = [RawArray(c_uint8, nbytes) for _ in range(nframes)]

        self.reset()

    ##

    def reset(self):
        with self._lock:
            self._head = self._tail
            self._full = False

    def put(self, overwrite=False):
        with self._lock:
            if (not overwrite) and self.full():
                raise RuntimeError("buffer full")

            frame = self.frames[self._head]
            self._advance()
            return frame

    def get(self):
        with self._lock:
            if self.empty():
                return None

            frame = self.frames[self._tail]
            self._retreat()
            return frame

    def empty(self):
        return (not self.full()) and (self._head == self._tail)

    def full(self):
        return self._full

    def capacity(self):
        """Returns the maximum capacity of the buffer."""
        return len(self.frames)

    def size(self):
        if not self._full:
            if self._head >= self._tail:
                return self._head - self._tail
            else:
                return self.capacity() + (self._head - self._tail)

    ##

    def _advance(self):
        if self.full():
            self._tail = (self._tail + 1) % self.capacity()

        self._head = (self._head + 1) % self.capacity()
        self._full = self._head == self._tail

    def _retreat(self):
        self._full = False
        self._tail = (self._tail + 1) % self.capacity()

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
        (_, shape), dtype = self.get_roi(), self.get_dtype()
        self._buffer = RingBuffer(shape, dtype, nframes)

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
    def _extract_frame(self, index=None):
        """Retrieve an acquired frame from the buffer WITHOUT making a copy."""
        if index is None:
            return self.buffer.get()
        else:
            return self.buffer.frames[index]

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
