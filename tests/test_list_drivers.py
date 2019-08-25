from pprint import pprint

import coloredlogs

from olive.core import DeviceManager, DriverManager

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

drv_mgr = DriverManager()
dev_mgr = DeviceManager()

print("\n** all drivers **")
pprint(drv_mgr.drivers)

print("\n** categorized drivers **")
pprint(drv_mgr._drivers)

CamDrv = drv_mgr.drivers[0]

print("\n** before instantiation")
pprint(dev_mgr.devices)

cam = CamDrv()
cam.initialize()

print("\n** after instantiation")
pprint(dev_mgr.devices)

cam.close()

print("\n** after cleanup**")
pprint(dev_mgr.devices)
