from abc import abstractmethod
from typing import Union

from .base import Device

__all__ = []


class States(Device):
    """
    State device has relatively small number of discrete states. The most common
    examples of state device are filter wheels and shutter.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}

    ##

    def get_alias(self, index):
        """Lookup state alias from its index."""

    def set_alias(self, index, alias):
        """Set an alias from the state."""

    def get_index(self, alias):
        """Lookup state index from its alias."""

    ##

    @abstractmethod
    def get_max_states(self) -> int:
        """Maximum supported states."""

    @abstractmethod
    def get_state(self):
        """Get currently selected state."""

    @abstractmethod
    def set_state(self, state: Union[int, str]):
        """
        Set new active state.

        Args:
            state (int or str): can be state index or its alias
        """
