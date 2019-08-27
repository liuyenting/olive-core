import logging
from pprint import pprint

import coloredlogs

from olive.drivers.aa.mds import MultiDigitalSynthesizer as MDS


coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

mds = MDS()
devices = mds.enumerate_devices()
pprint(devices)
