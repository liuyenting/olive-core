from abc import abstractmethod

from olive.core import Device

__all__ = ["Sequencer"]


class Sequencer(Device):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
