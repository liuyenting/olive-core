from abc import abstractmethod
import logging
from typing import NamedTuple

from olive.devices.base import Device

__all__ = ["Camera", "CameraInfo"]


class CameraInfo(NamedTuple):  # TODO move this to generic device definition
    #: version of the API
    version: str
    #: vendor name of the camera
    vendor: str
    #: modle name of the camera
    model: str
    #: camera serial number
    serial_number: str

    def __repr__(self) -> str:
        return f"<CameraInfo {self.vendor}, {self.model}, S/N={self.serial_number}>"


class Attribute(NamedTuple):
    readable: bool
    writable: bool
    name: str


class Camera(Device):
    @abstractmethod
    def __init__(self):
        super().__init__()

    """
    High level functions
        - Snap: Capture all or a portion of a single image to the user buffer
        - Grab: Perform an acquisition that loops continually on one or more internal buffers.
        - Sequence: Aquire a specified number of internal buffers and then stops.
    """

    def snap(self):
        pass

    def configure_grab(self):
        pass

    def grab(self):
        pass

    def sequence(self):
        pass

    """
    Acquisition:
        Configure, start, stop, and unconfigure an image acquisition.
    """

    def configure_acquisition(self):
        pass

    def start_acquisition(self):
        """
        Starts an acquisition.

        Use stop_acquisition() to stop the acquisition.
        """
        pass

    def get_image(self):
        """Get data of the specified frame."""
        pass

    def stop_acquisition(self):
        """Stops an acquistion."""
        pass

    def unconfigure_acquisition(self):
        pass

    """
    Attribute:
        Examine and change the acquisition or camera attributes.
    """

    # def enumerate_attributes(self):
    #    pass

    # def get_attribute(self, name):
    #    pass

    # def set_attribute(self, name, value):
    #    pass

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
    Session:
        Open, close, or enumerate sessions.
    """

    # def discover(cls):
    #    pass

    # def initialize(self):
    #    pass

    # def close(self):
    #    pass

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
