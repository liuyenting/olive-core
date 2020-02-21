import asyncio
import logging
from abc import abstractmethod
from ctypes import c_uint8
from enum import Enum, auto
from math import floor
from multiprocessing.sharedctypes import RawArray
from typing import List, Optional, Union

import numpy as np
from psutil import virtual_memory

from .base import Device
from .error import HostOutOfMemoryError, NotEnoughBufferError

__all__ = ["BufferRetrieveMode", "Camera"]

logger = logging.getLogger(__name__)


class BufferRetrieveMode(Enum):
    Latest = auto()  # return the latest acquired frame
    Next = auto()  # return next valid frame


class FrameBuffer(object):
    """
    An non-blocking ring buffer.

    Args:
        shape (tuple): shape of a frame
        dtype (dtype): frame data type
        frames (int, optional): number of frames
    """

    def __init__(self, shape, dtype, nframes=1):
        assert nframes >= 1, "frames in a ring buffer should be >= 1"

        self._shape, self._dtype = shape, dtype
        self._frames = [RawArray(c_uint8, self.nbytes) for _ in range(nframes)]

        self._read_index, self._write_index = 0, 0
        self._is_full = False

    ##

    @property
    def dtype(self):
        return self._dtype

    @property
    def maxsize(self):
        """Number of frames in the buffer."""
        return len(self._frames)

    @property
    def nbytes(self):
        """Number of bytes per frame."""
        (ny, nx), itemsize = self.shape, np.dtype(self.dtype).itemsize
        return (nx * ny) * itemsize

    @property
    def shape(self):
        """Shape of a frame."""
        return self._shape

    @property
    def frames(self) -> List[RawArray]:
        """Reference to the actual frame buffer."""
        return self._frames

    ##

    def reset(self):
        self._read_index, self._write_index = 0, 0
        self._is_full = False

    def full(self):
        return self._is_full

    def empty(self):
        return (not self._is_full) and (self._read_index == self._write_index)

    def write(self, frame):
        """
        Write a frame and put it to dirty queue.

        Args:
            frame (RawArray, optional): frame to write in the buffer, dummy write if
                `None`
        """
        if self.full():
            raise NotEnoughBufferError()
        self._frames[self._write_index][:] = frame

        self._write_index = (self._write_index + 1) % self.maxsize
        self._is_full = self._read_index == self._write_index

    def read(self) -> RawArray:
        """
        Return a new frame and put it back to clean queue.

        Returns:
            (RawArray): underlying array object
        """
        if self.empty():
            return None
        yield self._frames[self._read_index]

        self._read_index = (self._read_index + 1) % self.maxsize
        self._is_full = False

    def size(self):
        """Number of unread frames in the buffer."""
        size = self._read_index - self._write_index
        return self.maxsize + size if size < 0 else size  # wrap around if negative


class Camera(Device):
    """
    Args:
        max_memory_size (int or float, optional): maximum buffer memory size in bytes
            or percentage

    Attributes:
        continuous (bool): camera will continuously acquiring
    """

    def __init__(self, *args, max_memory_size=0.1, **kwargs):
        super().__init__(*args, **kwargs)

        self._buffer, self._max_memory_size = None, None
        self.set_max_memory_size(max_memory_size)

        self._continous = False

    ##

    @property
    def buffer(self):
        return self._buffer

    @property
    def is_continuous(self):
        return self._continous

    ##

    async def snap(self, out=None):
        """
        Capture a single image.

        By default, this creates a small ring buffer and store data in it. If the device provides a specialized snap function, override this method to use it instead.

        Args:
            out (np.ndarray, optional): store frame in this array if provided
        """
        # NOTE ring buffer requires minimally of 2 frames
        await self.configure_acquisition(1)

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

    async def sequence(self, frames: Union[int, np.ndarray]):
        """
        Acquire a specified number of images and then stops.

        Args:
            frames (int or np.ndarray): number of frames or an np.ndarray stack, where
                number of layers implies number of frames
        """
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

    ##

    async def configure_acquisition(self, n_frames: Optional[int] = None):
        """
        Configure resources required in an acquisition.

        Args:
            n_frames (int, optional): size of the frame buffer, maxmum number if not
                specified
        """
        coerced = False
        try:
            await self._configure_frame_buffer(n_frames)
        except HostOutOfMemoryError as err:
            logger.warning(str(err))
            n_frames = await self._configure_frame_buffer()
            logger.info(f"coerced buffer size is {n_frames} frame(s)")
            coerced = True

        # in continuous mode when:
        #   - specified explicitly
        #   - limited memory
        self._continous = (n_frames is None) or coerced

    async def _configure_frame_buffer(self, n_frames: Optional[int] = None):
        """
        Create frame buffer.

        Args:
            n_frames (int, optional): size of the frame buffer, maximum number if not
                specified

        Returns:
            (int): allocated number of frames
        """
        (_, shape), dtype = await self.get_roi(), await self.get_dtype()

        ny, nx = shape
        nbytes = (nx * ny) * np.dtype(dtype).itemsize

        max_bytes = self.get_max_memory_size()
        try:
            if max_bytes < nbytes * n_frames:
                max_bytes = self.get_max_memory_size()
                raise HostOutOfMemoryError(
                    f"requested buffer size exceeds memory limit ({max_bytes} bytes)"
                )
        except TypeError:
            # use maximum frames
            n_frames = max_bytes // nbytes

        logger.debug(f"allocated {n_frames} frame(s) in the buffer")
        self._buffer = FrameBuffer(shape, dtype, n_frames)

        return n_frames

    @abstractmethod
    def start_acquisition(self):
        """Starts an acquisition."""

    async def get_image(
        self,
        mode: BufferRetrieveMode = BufferRetrieveMode.Next,
        copy: bool = True,
        out: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Acquire specified frame.

        Args:
            mode (BufferRetrieveMode, optional): retrieve next or latest frame
            copy (bool, optional): copy frame from the buffer
            out (np.ndarray, optional): output array
        """
        while True:
            frame = self.buffer.read(mode)
            if frame is None:
                await asyncio.sleep(0)  # force release
            else:
                break

        if out is None:
            # reinterpret as a numpy array
            _out = np.frombuffer(frame, dtype=self.buffer.dtype)
            _out = np.reshape(_out, self.buffer.shape)
            if copy:
                # create a new copy
                out = np.copy(_out)
            else:
                out = _out
        else:
            # write into the frame
            out[:] = frame[:]

        return out

    @abstractmethod
    async def _retrieve_frame(self, mode: BufferRetrieveMode) -> RawArray:
        """Retrieve raw frame data from the camera and write it to the frame buffer."""

    @abstractmethod
    def stop_acquisition(self):
        """Stops an acquistion."""

    def unconfigure_acquisition(self):
        """Release resources used in the acquisition."""
        self._buffer = None
        logger.debug("buffer UNREFERENCED")

    ##

    @abstractmethod
    async def get_dtype(self):
        """Data type the camera generates."""
        pass

    @abstractmethod
    async def get_exposure_time(self):
        pass

    @abstractmethod
    async def set_exposure_time(self, value):
        pass

    def get_max_memory_size(self):
        return self._max_memory_size

    def set_max_memory_size(self, max_memory_size):
        if isinstance(max_memory_size, float):
            total_memory_size = virtual_memory().total
            max_memory_size = floor(max_memory_size * total_memory_size)
        self._max_memory_size = max_memory_size

    @abstractmethod
    async def get_max_roi_shape(self):
        pass

    @abstractmethod
    async def get_roi(self):
        """Set region of interest."""

    @abstractmethod
    async def set_roi(self, pos0=None, shape=None):
        """
        Set region of interest.

        - If `pos0` is None, `shape` is centered in the sensory boundary
        - If `shape` is None, `shape` will extend to the maximum sensor boundary.
        - If both `pos0` and `shape` are None, full sensor range is used.

        Args:
            pos0 (tuple of int, optional): top-left position
            shape (tuple of int, optional): shape of the region
        """
