from abc import abstractmethod
from typing import Iterable, Tuple

import numpy as np

from .base import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator", "SpatialLightModulator"]


class Modulator(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # dict value used for reverse lookup
        self._channels = dict()

    ##

    @abstractmethod
    def get_max_channels(self):
        """Maximum supported channels."""

    @abstractmethod
    def create_channel(self, alias):
        """Create new channel and book-keeping it internally."""

    def delete_channel(self, alias):
        assert alias in self._channels, f'"{alias}" does not exist"'
        self.disable(alias)  # ensure the channel is disabled
        self._channels.pop(alias)

    ##

    @abstractmethod
    def is_enabled(self, alias) -> bool:
        """Is the channel enabled?"""

    @abstractmethod
    async def enable(self, alias):
        """Enable a channel."""

    @abstractmethod
    async def disable(self, alias):
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
    async def get_frequency_range(self, alias) -> Tuple[float, float]:
        pass

    @abstractmethod
    async def get_frequency(self, alias) -> float:
        pass

    @abstractmethod
    async def set_frequency(self, alias, frequency: float):
        pass

    @abstractmethod
    async def get_power_range(self, alias) -> Tuple[float, float]:
        pass

    @abstractmethod
    async def get_power(self, alias) -> float:
        pass

    @abstractmethod
    async def set_power(self, alias, power: float):
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

    def get_max_channels(self):
        return 1

    # TODO

    def create_channel(self):
        """Create new channel and book-keeping it internally."""
        logger.debug(f'EOM devices only have one channel')

    def delete_channel(self, alias):
        logger.debug(f'EOM devices only have one channel')

    ##

    @abstractmethod
    def is_enabled(self) -> bool:
        """Is the channel enabled?"""

    @abstractmethod
    async def enable(self):
        """Enable a channel."""

    @abstractmethod
    async def disable(self):
        """Disable a channel."""

    ##

    @abstractmethod
    async def get_gain_range(self, alias) -> Tuple[float, float]:
        pass

    @abstractmethod
    async def get_gain(self, alias) -> float:
        pass

    @abstractmethod
    async def set_gain(self, alias, gain: float):
        pass

    @abstractmethod
    async def get_bias_range(self, alias) -> Tuple[float, float]:
        pass

    @abstractmethod
    async def get_bias(self, alias) -> float:
        pass

    @abstractmethod
    async def set_bias(self, alias, bias: float):
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
    async def get_image(self, alias) -> np.ndarray:
        pass

    @abstractmethod
    async def set_image(self, alias, image: np.ndarray):
        pass
