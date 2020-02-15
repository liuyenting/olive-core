from pprint import pprint

import coloredlogs

from olive.devices import DeviceManager
from olive.core import DriverManager

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

drv_mgr = DriverManager()
dev_mgr = DeviceManager()

print("\n** all drivers **")
pprint(drv_mgr.drivers)

print("\n** categorized drivers **")
pprint(drv_mgr._drivers)

Drv = drv_mgr.drivers[0]

print("\n** before instantiation")
pprint(dev_mgr.devices)

dev = Drv()
dev.initialize(None)

print("\n** after instantiation")
pprint(dev_mgr.devices)

dev.close()

print("\n** after cleanup**")
pprint(dev_mgr.devices)
