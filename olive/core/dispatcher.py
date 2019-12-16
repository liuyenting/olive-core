import logging

from olive.core import DeviceManager

__all__ = ["Dispatcher"]

logger = logging.getLogger(__name__)


class Dispatcher(object):
    """
    Dispatch device confiugrations and formulate the sequence to execute on a sequencer.
    """

    def __init__(self, script):
        self._script = script
        self._device_manager = DeviceManager()

    ##

    def initialize(self):
        """Initialize all the devices."""
        # TODO

    def shutdown(self):
        """Shutdown all the devices."""
        pass

    def run(self):
        self.script.setup()
        try:
            while True:
                self.script.loop()
        except StopIteration:
            pass
        finally:
            # TODO cleanup
            pass

    def pause(self):
        pass

    def abort(self):
        pass

    ##

    @property
    def device_manager(self):
        return self._device_manager

    @property
    def script(self):
        return self._script
