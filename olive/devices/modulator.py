from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np

from .base import Device
from .error import ChannelExistsError

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator", "SpatialLightModulator"]


class Modulator(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # dict value used for reverse lookup
        self._channels = dict()

    ##

    @abstractmethod
    def number_of_channels(self):
        """Maximum supported channels."""

    def defined_channels(self) -> Iterable[str]:
        """Get currently configured channels."""
        return tuple(self._channels.keys())

    @abstractmethod
    def new_channel(self, alias):
        """Create new channel and book-keep it internally."""

    def delete_channel(self, alias):
        assert alias in self._channels, f'"{alias}" does not exist"'
        self._channels.pop(alias)

        # ensure the channel is disabled
        self.disable(alias)

    ##

    @abstractmethod
    def is_enabled(self, alias) -> bool:
        """Is the channel enabled?"""

    @abstractmethod
    def enable(self, alias):
        """Enable a channel."""

    @abstractmethod
    def disable(self, alias):
        """Disable a channel."""


class AcustoOpticalModulator(Modulator, Device):
    """
    This primitive device refers to devices using acousto-optic effect to diffract and
    shift the frequency of light using sound waves at radio frequency.

    An oscillating (frequency) electric signal drives (power) the piezoelectric
    transducer to vibrate, which creates sound waves in the material. The moving
    periodic planes of expansion and compression change the refraction index.

    - channels
        - name
        - freqency
        - power

    - frequency range
    """

    @abstractmethod
    def get_frequency_range(self, alias):
        pass

    @abstractmethod
    def get_frequency(self, alias) -> float:
        pass

    @abstractmethod
    def set_frequency(self, alias, frequency: float):
        pass

    @abstractmethod
    def get_power_range(self, alias):
        pass

    @abstractmethod
    def get_power(self, alias) -> float:
        pass

    @abstractmethod
    def set_power(self, alias, power: float):
        pass


class ElectroOpticalModulator(Modulator, Device):
    """
    This primitive device refers to devices in which a signal-controlled element
    exhibiting an electro-optic effect is used to modulate a beam of light.

    The elector-optic effect is the change in the refractive index of a material
    resulting from the application of a DC (bias) or low-frequency (gain) electric
    field.

    - channel (1)
        - gain
        - bias

    - power range
        - gain
            - min
            - max
        - bias
            - min
            - max
    """

    pass


class SpatialLightModulator(Modulator, Device):
    """
    An object that imposes some form of spatially varying modulation on a beam of
    light.
    """

    @abstractmethod
    def get_image_shape(self) -> Tuple[int, int]:
        """Get maximum supported image shape."""

    ##

    @abstractmethod
    def get_image(self, alias) -> np.ndarray:
        pass

    @abstractmethod
    def set_image(self, alias, image: np.ndarray):
        pass
