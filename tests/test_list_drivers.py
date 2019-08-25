from pprint import pprint

import coloredlogs

from olive.core.drivers import DriverManager

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dm = DriverManager()

print("** all drivers **")
pprint(dm.drivers)

print("** categorized drivers **")
pprint(dm._drivers)
