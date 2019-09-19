from abc import ABCMeta, abstractmethod, ABC
import logging


from olive.core import DeviceType

__all__ = [
    "Script",
    "ChannelsFeature",
    "TimeSeriesFeature",
    "ValueInspectorFeature",
]

logger = logging.getLogger(__name__)

##

"""
- time series
- virtual sheet
- tiles
- z stack
- channels
- value inspector
"""


class ScriptFeatureType(type):
    """All script features belong to this type."""


class ScriptFeature(metaclass=ScriptFeatureType):
    @abstractmethod
    def __init__(self):
        self.keywords = dict()


class TimeSeriesFeature(ScriptFeature):
    def set_timepoints(self, n):
        pass

    def set_interval(self, interval):
        pass


class ChannelsFeature(ScriptFeature):
    pass


class ValueInspectorFeature(ScriptFeature):
    pass


##


class ScriptType(ScriptFeatureType):
    """
    All concrete script belong to this type.

    Script are combinations of features and concrete instructions, and to avoid
    metaclass conflict, ScriptType is a subclass of ScriptFeatureType.
    """


class Script(metaclass=ScriptType):
    """
    Define how the system behave per acquisition request.
    """

    @abstractmethod
    def __init__(self):
        """Abstract __init__ to prevent instantiation."""

    ##

    def get_features(self):
        """Get supported features of the script."""
        return tuple(
            klass
            for klass in self.__class__.__bases__
            if issubclass(klass, ScriptFeature)
        )

    def get_requirements(self):
        """Retreieve device requirement of the script."""
        # only test non-inherited attributes
        attrs = set(dir(self)) - set(dir(Script))
        attrs = [getattr(self, attr) for attr in attrs]
        # ... we only cares about Device
        return [attr for attr in attrs if issubclass(type(attr), DeviceType)]

    def evaluate(self):
        """
        TODO
            1) convert all annotated properties to _device_alias

                main_camera =
        """
        pass

    ##

    @abstractmethod
    def setup(self):
        raise NotImplementedError

    @abstractmethod
    def loop(self):
        raise NotImplementedError

