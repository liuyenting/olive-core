import asyncio
import logging

import coloredlogs

from olive.core.managers import DriverManager
from olive.devices import AcustoOpticalModulator

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def run(device: AcustoOpticalModulator):
    loop = asyncio.get_event_loop()

    print("** start **")
    loop.run_until_complete(device.open())
    print(f"# ch: {device.number_of_channels()}")

    # define new channel
    device.new_channel("488")
    device.new_channel("561")
    device.new_channel("640")

    device.delete_channel("561")
    device.new_channel("405")

    # turn new channel on
    device.enable("488")
    fmin, fmax = device.get_frequency_range("488")
    print(f"frange: [{fmin}, {fmax}]")
    device.disable("488")

    pmin, pmax = device.get_power_range("488")
    print(f"prange: [{pmin}, {pmax}]")

    loop.run_until_complete(device.close())


def main():
    loop = asyncio.get_event_loop()

    driver_mgmt = DriverManager()

    aom_drivers = driver_mgmt.query_drivers(AcustoOpticalModulator)
    print(aom_drivers)

    aom_driver = aom_drivers[0]
    aom_devices = loop.run_until_complete(aom_driver.enumerate_devices())
    print(aom_devices)

    aom_device = aom_devices[0]
    run(aom_device)


if __name__ == "__main__":
    main()
