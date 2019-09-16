from collections import namedtuple

from PySide2.QtCore import Qt
from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QComboBox, QGridLayout, QLabel, QLineEdit

from olive.gui.features.base import Feature

__all__ = ["TimeSeriesFeature"]


class TimeSeriesFeature(Feature):
    UnitOption = namedtuple("UnitOption", ["ratio", "min", "max"])

    def __init__(self):
        super().__init__("Time Series")

        timepoints_label = QLabel("# of timepoints:")
        timepoints_label.setAlignment(Qt.AlignRight)
        timepoints_value = QLineEdit()
        timepoints_value.setAlignment(Qt.AlignHCenter)
        timepoints_validator = QIntValidator()
        timepoints_validator.setBottom(1)
        timepoints_value.setValidator(timepoints_validator)

        interval_label = QLabel("Interval:")
        interval_label.setAlignment(Qt.AlignRight)
        interval_value = QLineEdit()
        interval_value.setAlignment(Qt.AlignHCenter)
        interval_unit = QComboBox()
        interval_unit.addItem("min", self.UnitOption(60, 0.5, 360))
        interval_unit.addItem("s", self.UnitOption(1, 1e-3, 600))
        interval_unit.addItem("ms", self.UnitOption(1e-3, 1, 1e3))
        interval_unit.setCurrentIndex(1)
        # TODO pull data from current selected item
        # interval_value.setValidator(QDoubleValidator())

        layout = QGridLayout()
        layout.addWidget(timepoints_label, 0, 0, 1, 1)
        layout.addWidget(timepoints_value, 0, 1, 1, 1)
        layout.addWidget(interval_label, 1, 0, 1, 1)
        layout.addWidget(interval_value, 1, 1, 1, 1)
        layout.addWidget(interval_unit, 1, 2, 1, 1)

        layout.setRowStretch(2, 1)

        self.widget.setLayout(layout)

    ##

    def _update_interval_unit(self, index):
        pass
