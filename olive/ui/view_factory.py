import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Dict, Type

from .base import PresenterBase, ViewBase

__all__ = ["ViewFactory"]

logger = logging.getLogger(__name__)


class ViewFactory(ABC, Mapping):
    name = None

    def __init__(self, name: str):
        self._name = name
        self._lut = self.create_lut()

    def __getitem__(self, key: PresenterBase) -> ViewBase:
        return self._lut[key]

    def __iter__(self):
        for key in self._lut.keys():
            yield key

    def __len__(self):
        return len(self._lut)

    ##

    @abstractmethod
    def create_lut(self) -> Dict[Type[PresenterBase], Type[ViewBase]]:
        """
        Create lookup table between presenters and their views. This only provides
        classes instead of the actual object.

        Returns:
            (dict of PresenterBase: ViewBase): a association dictionary
        """
