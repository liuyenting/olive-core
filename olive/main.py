import logging
from pprint import pprint
import sys

import coloredlogs

from olive.core import Dispatcher, DriverManager
from olive.scripts.calibration import AOTFCalibration

# disable tifffile warning
logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)


def main():
    aotf_cal_script = AOTFCalibration()
    pprint(aotf_cal_script.get_features())


if __name__ == "__main__":
    main()
