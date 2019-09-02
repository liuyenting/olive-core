from abc import abstractmethod

from olive.core import Device

__all__ = ["SoftwareSequencer", 'HardwareSequencer']

##


class SequencerType(type):
    """All sequencers belong to this type."""


class Sequencer(metaclass=SequencerType):
    """
    A sequencer runs a sequence of instructions, in order to manipulate devices in
    timely manners.
    """"

    @abstractmethod
    def __init__(self):
        pass


class SoftwareSequencer(Sequencer):
    pass


class HardwareSequencer(SoftwareSequencer):
    """
    Hardware sequencers uses embedded hardwares through-out most of its execution stages to provide real-time mainpulations, while fallback to software implementations using IRQ when necessary.

    Note:
        Therefore, it is a subset of the SoftwareSequencer.
    """
    pass
