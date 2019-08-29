import logging
from pprint import pprint

import coloredlogs

from olive.drivers.ophir.meters import Nova2


coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def select_device():
    return Nova2(None, 'COM5', 38400)


def main():
    device = select_device()

    device.open()

    print(device.get_property('head_type'))

    device.close()


if __name__ == "__main__":
    main()
