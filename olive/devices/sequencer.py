from abc import abstractmethod
from functools import wraps
import logging

__all__ = ["SoftwareSequencer", "HardwareSequencer"]


logger = logging.getLogger(__name__)


class SequencerType(type):
    """All sequencers belong to this type."""


class Sequencer(metaclass=SequencerType):
    """
    A sequencer runs a sequence of instructions, in order to manipulate devices in
    timely manners.
    """

    @abstractmethod
    def __init__(self):
        pass


class SoftwareSequencer(Sequencer):
    """
    We can directly use software sequencer.
    """

    def __init__(self):
        super().__init__()


class HardwareSequencer(SoftwareSequencer):
    """
    Hardware sequencers uses embedded hardwares through-out most of its execution stages to provide real-time mainpulations, while fallback to software implementations using IRQ when necessary.

    Note:
        Therefore, it is a subset of the SoftwareSequencer.
    """

    class GPIO(object):
        pass

    class DigitalIO(GPIO):
        pass

    class DigitalInput(DigitalIO):
        pass

    class DigitalOutput(DigitalIO):
        pass

    class AnalogIO(GPIO):
        pass

    class AnalogInput(AnalogIO):
        pass

    class AnalogOutput(AnalogIO):
        pass

    class PatternBuffer(object):
        pass

    @abstractmethod
    def __init__(self):
        super().__init__()

    @property
    def digital(self):
        # TODO manipulate dict?
        pass

    @property
    def analog(self):
        pass

    """
    # TODO

    - digital input
    - digital output

    - analog input
    - analog output (static)
    - analog waveform

    - digital trigger
        - edge
        - level
    """
