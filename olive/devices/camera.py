from abc import abstractmethod
from collections import deque
from ctypes import c_uint8
from enum import auto, Enum
import logging
from math import floor
from multiprocessing.sharedctypes import RawArray

import numpy as np
from psutil import virtual_memory

from olive.core import Device

__all__ = ["BufferRetrieveMode", "Camera"]

logger = logging.getLogger(__name__)


class BufferRetrieveMode(Enum):
    Latest = auto()  # return the latest acquired frame
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
        assert nframes >= 1, "frames in a ring buffer should be >= 1"

        self._shape, self._dtype = shape, dtype

        (ny, nx), dtype = self.shape, self.dtype
        nbytes = (nx * ny) * np.dtype(dtype).itemsize
        self._frames = [RawArray(c_uint8, nbytes) for _ in range(nframes)]

        self._dirty, self._clean = deque(), deque()
        self.reset()

    ##

    def reset(self):
        self._dirty.clear()
        self._clean.clear()

        for frame in self.frames:
            self._clean.appendleft(frame)

    def write(self, overwrite=False):
        """
        Request a frame to write in.
        """
        try:
            frame = self._clean.pop()
        except IndexError:
            # no clean frame to pop
            if overwrite:
                frame = self._dirty.pop()
            else:
                raise IndexError("not enough internal buffer")
        self._dirty.appendleft(frame)
        return frame

    def read(self):
        """
        Read a dirty frame.
        """
        try:
            frame = self._dirty.pop()
            self._clean.appendleft(frame)
            return frame
        except IndexError:
            # no dirty frame to pop
            return None

    def empty(self):
        return self.size() == 0

    def full(self):
        return len(self._clean) == 0

    def capacity(self):
        """Returns the maximum capacity of the buffer."""
        return len(self.frames)

    def size(self):
        return len(self._dirty)

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

    def snap(self, out=None):
        """Capture a single image."""
        self.configure_acquisition(1)

        self.start_acquisition()
        out = self.get_image(out=out)
        self.stop_acquisition()

        self.unconfigure_acquisition()

        return out

    def configure_grab(self):
        pass

    def grab(self):
        """Perform an acquisition that loops continuously."""

    def sequence(self, frames):
        """Acquire a specified number of images and then stops."""
        self.configure_acquisition(frames)

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
            yield self.get_image(out=frames[i, ...])
        self.stop_acquisition()

        self.unconfigure_acquisition()

        return frames

    """
    Low level
    """

    def configure_acquisition(self, n_frames, continuous=False):
        self.configure_ring(n_frames)

        # continuous when
        #   - specified explicitly
        #   - limited buffer
        self._continous = continuous or (n_frames != len(self.buffer.frames))

    def configure_ring(self, n_frames):
        (_, shape), dtype = self.get_roi(), self.get_dtype()

        ny, nx = shape
        nbytes = (nx * ny) * np.dtype(dtype).itemsize

        available_size = self.get_max_memory_size()
        if available_size < nbytes * n_frames:
            n_frames = available_size // nbytes
            logger.warning(
                f"exceeds memory limit ({available_size} bytes), coerce to {n_frames} frames"
            )
        self._buffer = RingBuffer(shape, dtype, n_frames)

    @abstractmethod
    def start_acquisition(self):
        """Starts an acquisition."""

    def get_image(self, index=None, copy=True, out=None):
        """
        Acquire specified frame.

        Args:
            TBA
        """
        # reinterpret as a numpy array
        frame = self._get_image_data()

        # store the value
        if out is None:
            out = frame.copy() if copy else frame
        else:
            out[:] = frame[:]
        return out

    def _get_image_data(self):
        """Retrieve a frame from the host-side ring buffer WITHOUT making a copy."""
        frame = self._extract_frame()
        return np.frombuffer(frame, dtype=self.buffer.dtype).reshape(self.buffer.shape)

    @abstractmethod
    def _extract_frame(self, mode: BufferRetrieveMode = BufferRetrieveMode.Next):
        """Retrieve new frame data from the camera."""

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
