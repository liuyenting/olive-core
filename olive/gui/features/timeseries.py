from collections import namedtuple

from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from olive.gui.features.base import Feature

__all__ = ["TimeSeriesFeature"]


class TimeSeriesFeature(Feature):
    UnitOption = namedtuple("UnitOption", ["ratio", "min", "max"])

    def __init__(self):
        super().__init__("Time Series")

        timepoints_label = QLabel("# of timepoints:")
        timepoints_value = QLineEdit()
        timepoints_validator = QIntValidator()
        timepoints_validator.setBottom(1)
        timepoints_value.setValidator(timepoints_validator)

        interval_label = QLabel("Interval:")
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
        layout.addWidget(timepoints_label)
        layout.addWidget(timepoints_value)
        layout.addWidget(interval_label)
        layout.addLayout(interval_layout)
        layout.insertStretch(-1)

        self.widget.setLayout(layout)

    ##

    def _update_interval_unit(self, index):
        pass
