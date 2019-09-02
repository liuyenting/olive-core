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

    valid_wavelength = device.get_property("valid_wavelengths")
    logger.info(f"valid wavelength: {valid_wavelength}")

    valid_ranges = device.get_valid_ranges()

    current_range = device.get_current_range()
    logger.info(f"ranges: {valid_ranges} (current: {current_range})")

    device.set_current_range(valid_ranges[-1])
    current_range = device.get_current_range()
    logger.info(f"ranges: {valid_ranges} (current: {current_range})")

    fw = device.get_property('favorite_wavelengths')
    logger.info(f'favorites: {fw}')
    device.set_wavelength(600)

    unit = device.get_unit()
    for i in range(5):
        print(f"{device.readout()}{unit}")

    device.close()


if __name__ == "__main__":
    main()
