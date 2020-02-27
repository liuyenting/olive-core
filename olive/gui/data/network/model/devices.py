from dataclasses import dataclass

__all__ = []


@dataclass
class Device:
    """
    A data class for device info.
    """

    uuid: str

    vendor: str
    model: str
    version: str
    serial_number: str


@dataclass
class DevicesRequest:
    uuid: str = ""


@dataclass
class DevicesResponse:
    pass
