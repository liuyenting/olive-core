from abc import ABCMeta, abstractmethod
import logging


from olive.core import DeviceType

__all__ = ["Script", "TimeSeriesFeature", "ChannelsFeature"]

logger = logging.getLogger(__name__)

##

"""
- time series
- virtual sheet
- tiles
- z stack
- channels
"""


class ScriptFeatureType(type):
    """All script features belong to this type."""


class ScriptFeature(metaclass=ScriptFeatureType):
    @abstractmethod
    def __init__(self):
        pass


class TimeSeriesFeature(ScriptFeature):
    def set_timepoints(self, n):
        pass

    def set_interval(self, interval):
        pass


class ChannelsFeature(ScriptFeature):
    pass


##


class Script(metaclass=ABCMeta):
    """
    Define how the system behave per acquisition request.
    """

    #: device name in the script and their managed ID
    _device_alias = {}

    def __init__(self):
        pass

    ##

    def get_features(self):
        """Get supported features of the script."""
        klasses = self.__bases__
        return [klass for klass in klasses if issubclass(klass, ScriptFeatureType)]

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

