import asyncio
import logging
import threading
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

    async def write(self, frame):
        """
        TBA

        Args:
            frame (RawArray, optional): frame to write in the buffer, dummy write if
                `None`
        """
        while True:
            try:
                self.write_nowait(frame)
            except NotEnoughBufferError:
                await asyncio.sleep(0)
            else:
                break

    def write_nowait(self, frame):
        """
        TBA

        Args:
            frame (RawArray, optional): frame to write in the buffer, dummy write if
                `None`
        """
        if self.full():
            raise NotEnoughBufferError()
        self._frames[self._write_index][:] = frame
        self._advance_write_index()

    def _advance_write_index(self):
        self._write_index = (self._write_index + 1) % self.maxsize
        self._is_full = self._read_index == self._write_index

    async def read(self) -> RawArray:
        while True:
            frame = self.read_nowait()
            if frame is None:
                await asyncio.sleep(0)
            else:
                break

    def read_nowait(self) -> RawArray:
        """
        Return a new frame and put it back to clean queue.

        Returns:
            (RawArray): underlying array object
        """
        if self.empty():
            return None
        yield self._frames[self._read_index]
        self._advance_read_index()

    def _advance_read_index(self):
        self._read_index = (self._read_index + 1) % self.maxsize
        self._is_full = False

    def size(self):
        """Number of unread frames in the buffer."""
        size = self._read_index - self._write_index
        return self.maxsize + size if size < 0 else size  # wrap around if negative


class Worker(threading.Thread):
    """
    Worker thread that retrieve frame from the camera to frame buffer.
    """

    def __init__(self):
        super().__init__()

        self._buffer, self._async_func = None, None
        self._stop_event = threading.Event()

    ##

    def run(self):
        async def wrapper():
            while not self._stop_event.is_set():
                frame = await self._async_func
                self._buffer.write_nowait(frame)

        self._stop_event.clear()
        asyncio.run(wrapper())

    ##

    def set_buffer(self, buffer: FrameBuffer):
        self._buffer = buffer

    def set_retrieval_function(self, func):
        self._async_func = func

    ##

    def stop(self):
        self._stop_event.set()


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

        self._continous, self._acquisition_mode = False, BufferRetrieveMode.Next

        self._worker = Worker()

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
        await self.configure_acquisition(1)

        self.start_acquisition()
        out = await self.get_image(out=out)
        self.stop_acquisition()

        self.unconfigure_acquisition()

        return out

    async def grab(self, lossy=False):
        """
        Perform an acquisition that loops continuously.

        Args:
            lossy (bool, optional): should we ignore frames
        """
        await self.configure_acquisition(lossy=lossy)

        self.start_acquisition()
        while True:
            yield await self.get_image(copy=False)
        self.stop_acquisition()

        self.unconfigure_acquisition()

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
            yield await self.get_image(out=frames[i, ...])
        self.stop_acquisition()

        self.unconfigure_acquisition()

    ##

    async def configure_acquisition(self, n_frames: Optional[int] = None, lossy=False):
        """
        Configure resources required in an acquisition.

        Args:
            n_frames (int, optional): size of the frame buffer, maxmum number if not
                specified
            lossy (bool, optional): should we ignore frames
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

        self._acquisition_mode = (
            BufferRetrieveMode.Latest if lossy else BufferRetrieveMode.Next
        )

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
        """
        Start the acquisition.

        Base function only launches the acquisition thread, if other setups are
        required, please configure them first and call `super().start_acquisition()` as
        the last step.
        """
        self._worker.set_buffer(self.buffer)
        func = self._retrieve_frame(self._acquisition_mode)
        self._worker.set_retrieval_function(func)

        # RUN!
        self._worker.run()

    @abstractmethod
    async def _retrieve_frame(self, mode: BufferRetrieveMode) -> RawArray:
        """Retrieve raw frame data from the camera and write it to the frame buffer."""

    async def get_image(
        self, copy: bool = True, out: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Acquire specified frame.

        If no worker exists
        Args:
            copy (bool, optional): copy frame from the buffer
            out (np.ndarray, optional): output array
        """
        frame = await self.buffer.read()

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
    def stop_acquisition(self):
        """Stops an acquistion."""
        self._worker.stop()
        self._worker.join()  # wait until the thread is terminated

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
