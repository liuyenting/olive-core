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


def main_gui():
    from PySide2.QtWidgets import QApplication

    from olive.ui import MainWindow

    app = QApplication()
    mw = MainWindow()
    """
    TODO

    V 1) profile wizard
    2) retrieve {
        script object,
        sequencer object,
        alias-device relationship (+ device class) [ADR]
       }
    3) launcher dispatcher, feed script and ADR
    4) initialize sequencer and devices by dispatcher
    5) TODO, dunno what happened next
    """
    mw.show()
    app.exec_()


def main_cli():
    # discover drivers
    drv_mgr = DriverManager()
    print(f"drivers: {drv_mgr.drivers}")

    # load script
    aotf_cal_script = AOTFCalibration()
    print(f"features: {aotf_cal_script.get_features()}")

    # TODO scan for requirements
    # TODO scan for connected hardwares using drivers

    # TODO create relationship link

    # TODO dispatch
    # dispatcher = Dispatcher(aotf_cal_script)


if __name__ == "__main__":
    main_cli()
