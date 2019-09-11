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
    drv_mgr = DriverManager()
    pprint(drv_mgr)
    """
    aotf_cal_script = AOTFCalibration()
    dispatcher = Dispatcher(aotf_cal_script)

    # TODO associate requirements with actual devices

    dispatcher.initialize()
    dispatcher.run()
    dispatcher.shutdown()
    """


if __name__ == "__main__":
    main()
