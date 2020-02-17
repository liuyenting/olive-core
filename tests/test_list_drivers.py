import asyncio
from pprint import pprint

import coloredlogs

from olive.core import DriverManager
from olive.devices import Camera, DeviceManager

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

drv_mgr = DriverManager()
dev_mgr = DeviceManager()

print("\n** categorized drivers **")
pprint(drv_mgr._drivers)

drivers = drv_mgr.query_drivers(Camera)
pprint(drivers)
assert len(drivers) > 0, "no driver"

driver = drivers[0]

print("\n** before instantiation")
pprint(dev_mgr.devices)

loop = asyncio.get_event_loop()

devs = loop.run_until_complete(driver.enumerate_devices())
pprint(devs)
assert len(devs) > 0, "no device"

dev = devs[0]
dev.open()

print("\n** after instantiation")
pprint(dev_mgr.devices)

dev.close()

print("\n** after cleanup**")
pprint(dev_mgr.devices)
