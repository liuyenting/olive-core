import logging
from pprint import pprint

import coloredlogs

from olive.drivers.ophir.meters import Nova2
from olive.drivers.ophir.sensors import Photodiode

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def select_device():
    meter = Nova2(None, "COM5", 9600)
    sensor = Photodiode(None, meter)
    return sensor


def main():
    device = select_device()

    device.open(test=True)

    return

    print(device.get_property("head_type"))
    print(device.get_property("current_range"))
    print(device.get_property("unit"))

    device.close()


if __name__ == "__main__":
    main()
