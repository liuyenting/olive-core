import asyncio
import logging

import coloredlogs

from olive.core.managers import DriverManager
from olive.devices import AcustoOpticalModulator

coloredlogs.install(
    level="DEBUG",
    fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


async def run(device: AcustoOpticalModulator):

    print("** start **")
    await device.open()
    print(f"# ch: {device.get_max_channels()}")

    # define new channel
    device.create_channel("488")
    device.create_channel("561")
    device.create_channel("640")

    device.delete_channel("561")
    device.create_channel("405")

    # turn new channel on
    await device.enable("488")
    fmin, fmax = await device.get_frequency_range("488")
    print(f"ln1, frange: [{fmin}, {fmax}]")
    fmin, fmax = await device.get_frequency_range("405")
    print(f"ln2, frange: [{fmin}, {fmax}]")
    await device.disable("488")

    pmin, pmax = await device.get_power_range("640")
    print(f"prange: [{pmin}, {pmax}]")

    await device.close()


async def main():
    driver_mgmt = DriverManager()
    await driver_mgmt.refresh()

    aom_drivers = driver_mgmt.query_drivers(AcustoOpticalModulator)
    assert len(aom_drivers) > 0, "unable to find any suitable driver"
    print(aom_drivers)

    aom_driver = aom_drivers[0]
    aom_devices = await aom_driver.enumerate_devices()
    print(aom_devices)

    aom_device = aom_devices[0]
    await run(aom_device)


if __name__ == "__main__":
    # NOTE
    # ALWAYS use `get_event_loop` at the root location, in order to guarantee that all
    # the loops in the program are attached in the same one.
    #
    # Since some loop-dependent objects are initialized during class creation, the loop
    # may already exist somewhere. Using `asyncio.run` seems to create an additional
    # implicit loop, causing the program to whine about 'attached to a different loop.'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
