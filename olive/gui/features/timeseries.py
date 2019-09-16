from collections import namedtuple

from PySide2.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
)

from olive.gui.features.base import Feature

__all__ = ["TimeSeriesFeature"]


class TimeSeriesFeature(Feature):
    UnitOption = namedtuple("UnitOption", ["ratio", "min", "max"])

    def __init__(self):
        super().__init__("Time Series")

        interval_value = QLineEdit()

        interval_unit = QComboBox()
        interval_unit.addItem("min", self.UnitOption(60, 0.5, 360))
        interval_unit.addItem("s", self.UnitOption(1, 1e-3, 600))
        interval_unit.addItem("ms", self.UnitOption(1e-3, 1, 1e3))
        interval_unit.setCurrentIndex(1)
        # TODO pull data from current selected item
        # interval_value.setValidator(QDoubleValidator())
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(interval_value)
        interval_layout.addWidget(interval_unit)

        layout = QVBoxLayout()
        layout.addLayout(interval_layout)

        self.setLayout(layout)

    ##

    def _update_interval_unit(self, index):
        pass
