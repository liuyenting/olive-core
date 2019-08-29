import logging
from pprint import pprint

import coloredlogs

from olive.drivers.aa.mds import MultiDigitalSynthesizer as MDS


coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def select_device():
    mds = MDS()
    valid_devices = mds.enumerate_devices()
    logger.info(f"found {len(valid_devices)} device(s)")
    return valid_devices[0]


def main():
    device = select_device()

    device.open()

    fmin, fmax = device.get_property("freq_range")
    logger.info(f"frequency range [{fmin}, {fmax}]")

    device.set_frequency(4, (fmax + fmin) / 2)
    print(device.get_frequency(4))
    print(device._get_power_range(4))

    device.close()


if __name__ == "__main__":
    main()
