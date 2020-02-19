import asyncio
import logging

import coloredlogs

from olive.core.managers import DriverManager
from olive.devices import AcustoOpticalModulator

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


async def run(device: AcustoOpticalModulator):
    await device.open()
    print(f"# ch: {device.number_of_channels()}")
    await device.close()


def main():
    loop = asyncio.get_event_loop()

    driver_mgmt = DriverManager()

    aom_drivers = driver_mgmt.query_drivers(AcustoOpticalModulator)
    print(aom_drivers)

    aom_driver = aom_drivers[0]
    aom_devices = loop.run_until_complete(aom_driver.enumerate_devices())
    print(aom_devices)

    aom_device = aom_devices[0]
    loop.run_until_complete(run(aom_device))


if __name__ == "__main__":
    main()
