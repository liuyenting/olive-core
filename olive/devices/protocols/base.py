from abc import ABCMeta, abstractmethod

__all__ = ["Protocol"]


class Protocol(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
