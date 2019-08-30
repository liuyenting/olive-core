import logging
from pprint import pprint

import coloredlogs

from olive.drivers.ophir.meters import Ophir

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def select_device():
    ophir = Ophir()
    ophir.initialize()
    valid_devices = ophir.enumerate_devices()
    logger.info(f"found {len(valid_devices)} device(s)")
    return valid_devices[0]


def main():
    device = select_device()

    device.open()

    print(device.get_property("current_range"))
    print(device.get_property("unit"))

    device.close()


if __name__ == "__main__":
    main()
