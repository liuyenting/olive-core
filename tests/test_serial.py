import logging
from pprint import pprint

import coloredlogs

from olive.drivers.aa.mds import MultiDigitalSynthesizer as MDS


coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

mds = MDS()
valid_devices = mds.enumerate_devices()
pprint(valid_devices)
dev = valid_devices[0]

dev.open()
print(dev.get_frequency(1))
dev.set_frequency(1, 100)
print(dev.get_frequency(1))
dev.close()
