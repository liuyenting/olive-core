from dataclasses import dataclass

__all__ = ["DeviceInfo"]


@dataclass
class DeviceInfo:
    version: str = ""
    vendor: str = ""
    model: str = ""
    serial_number: str = ""

    def __repr__(self) -> str:
        tokens = [
            ("", self.vendor),
            ("", self.model),
            ("version=", self.version),
            ("s/n=", self.serial_number),
        ]
        tokens[:] = [f"{name}{value}" for name, value in tokens if len(value) > 0]
        return f"<{', '.join(tokens)}>"
