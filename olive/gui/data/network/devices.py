import logging
from collections.abc import Mapping

from .base import APIClient

__all__ = ["Devices"]

logger = logging.getLogger(__name__)


class Devices(APIClient, Mapping):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    ##

    def get_available_devices(self):
        """
        Retrieve avaialble devices.

        Returns:
            (list of str): a list of device ID
        """
        response = self.get("/devices")
        assert response.status_code == 200
        assert response.status_code != 400, "invalid UUID"
        # rebuild device from the UUID
        return response.text

    def get_available_device_classes(self):
        """
        Retrieve available device classes.

        Returns:
            (list of str): a list of class names
        """
        pass
