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

    from olive.gui import MainWindow

    app = QApplication()
    mw = MainWindow()
    """
    TODO

    1) profile wizard
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
    aotf_cal_script = AOTFCalibration()
    pprint(aotf_cal_script.get_features())

    dispatcher = Dispatcher(aotf_cal_script)


if __name__ == "__main__":
    main_cli()
