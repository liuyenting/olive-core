from pprint import pprint

import coloredlogs

from olive.drivers.aa.mds import MultiDigitalSynthesizer as MDS


coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

pprint(MDS.discover())

aotf = MDS()

aotf.initialize("COM3")


aotf.close()
