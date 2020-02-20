import logging
from abc import abstractmethod
from ctypes import c_uint8
from enum import Enum, auto
from math import floor
from multiprocessing.sharedctypes import RawArray
from typing import Optional, Union

import numpy as np
from psutil import virtual_memory

from .base import Device
from .error import HostOutOfMemoryError

__all__ = ["BufferRetrieveMode", "Camera"]

logger = logging.getLogger(__name__)


class BufferRetrieveMode(Enum):
    Latest = auto()  # return the latest acquired frame
    Next = auto()  # return next valid frame


class FrameBuffer(object):
    """
    A buffer wrapper class that

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

    @property
    def dtype(self):
        return self._dtype

    @property
    def frames(self):
        return self._frames

    @property
    def shape(self):
        """Shape of a frame."""
        return self._shape

    ##

    def reset(self):
        self._read_index, self._write_index = 0, 0
        self._is_full = False

    def full(self):
        return self._is_full

    def empty(self):
        return (not self.full()) and (self._read_index == self._write_index)

    async def put(self, frame: RawArray):
        """
        Write a frame and put it to dirty queue.

        Args:
            frame (RawArray): frame to write in the buffer
        """
        if self.full():
            raise IndexError("not enough internal buffer")
        self.frames[self._write_index][:] = frame

        self._write_index = (self._write_index + 1) % self.capacity()
        self._is_full = self._read_index == self._write_index

    def put_done(self):
        # TODO put item, task_done
        pass

    async def get(self) -> RawArray:
        """
        Return a new frame and put it back to clean queue.

        Returns:
            (RawArray): underlying array object
        """
        if self.empty():
            return None
        frame = self.frames[self._read_index]

        self._read_index = (self._read_index + 1) % self.capacity()
        self._is_full = False

        return frame

    def get_done(self):
        # TODO put item, task_done
        pass

    def capacity(self):
        """Returns the maximum capacity of the buffer."""
        return len(self.frames)

    def size(self):
        """Number of unread frames."""
        if self.full():
            return self.capacity()
        else:
            size = self._read_index - self._write_index
            if size < 0:
                return self.capacity() + size  # wrap around
            else:
                return size


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
    def continuous(self):
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

    async def configure_acquisition(self, n_frames):
        """
        Configure resources required in an acquisition.

        Args:
            n_frames (int): size of the frame buffer
                - n_frames > 0, fixed number of frames
                - n_frames <= 0, continuous acquisition, buffer size determined
                    automagically
        """

        max_bytes = self.get_max_memory_size()
        ratio = 1
        while True:
            try:
                await self._configure_frame_buffer(n_frames // ratio)
                break
            except HostOutOfMemoryError:
                ratio *= 2
                logger.warning(
                    f"exceeds memory limit ({max_bytes} bytes), shrink {ratio}x"
                )

        # in continuous mode when:
        #   - specified explicitly
        #   - limited memory
        self._continous = (n_frames <= 0) or (ratio > 1)

    async def _configure_frame_buffer(self, n_frames):
        (_, shape), dtype = await self.get_roi(), await self.get_dtype()

        ny, nx = shape
        nbytes = (nx * ny) * np.dtype(dtype).itemsize

        max_bytes = self.get_max_memory_size()
        if max_bytes < nbytes * n_frames:
            raise HostOutOfMemoryError()

        logger.debug(f"allocated {n_frames} frame(s) in the buffer")
        self._buffer = FrameBuffer(shape, dtype, n_frames)

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
        frame = await self.buffer.read(mode)

        if out is None:
            # reinterpret as a numpy array
            _out = np.frombuffer(frame, dtype=self.buffer.dtype)
            _out = np.reshape(_out, self.buffer.shape)
            if copy:
                # create a new copy
                return np.copy(_out)
            else:
                return _out
        else:
            # write into the frame
            out[:] = frame[:]
            return out

    @abstractmethod
    async def _retrieve_frame(self, mode: BufferRetrieveMode) -> RawArray:
        """Retrieve raw frame data from the buffer."""

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
