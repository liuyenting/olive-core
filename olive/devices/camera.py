from abc import abstractmethod
import logging

from olive.core import Device

__all__ = ["Camera"]

logger = logging.getLogger(__name__)


class Camera(Device):
    """
    High level functions
    """

    @abstractmethod
    def snap(self):
        """Capture a single image to the user buffer."""

    @abstractmethod
    def configure_grab(self):
        pass

    @abstractmethod
    def grab(self):
        """Perform an acquisitino that loops continuously."""

    @abstractmethod
    def sequence(self):
        """Acquire a specified number of images and then stops."""

    """
    Acquisition:
        Configure, start, stop, and unconfigure an image acquisition.
    """

    @abstractmethod
    def configure_acquisition(self):
        pass

    @abstractmethod
    def start_acquisition(self):
        """
        Starts an acquisition.

        Use stop_acquisition() to stop the acquisition.
        """

    @abstractmethod
    def get_image(self):
        """Get data of the specified frame."""

    @abstractmethod
    def stop_acquisition(self):
        """Stops an acquistion."""

    @abstractmethod
    def unconfigure_acquisition(self):
        """Release resources used in the acquisition."""

    """
    Event:
        Register events.
    """

    """
    Register:
        Access registers.

    Note:
        DO WE NEED THIS?
    """

    """
    Utility:
        Get detailed error information.
    """

    """
     Snap2
     Configure Grab
     Grab2
     Sequence2
     Open Camera
     Close Camera
     Enumerate Cameras
     Enumerate Attributes
    Enumerate Video Modes

    --- low level ---
     Configure Acquisition
    Configure Ring Acquisition
     Start Acquisition
     Stop Acquisition
     Unconfigure Acquisition
     Get Image2
     (Get Image Data)
    Read Register2
    Write Register2
    Read Memory2
    Write Memory2
    Read Attributes
    Write Attributes
    Register for Events
    """
