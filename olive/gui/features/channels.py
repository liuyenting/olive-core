from PySide2.QtWidgets import QVBoxLayout

from olive.gui.features.base import Feature

__all__ = ["ChannelsFeature"]


class ChannelsFeature(Feature):
    def __init__(self):
        super().__init__("Channels")

        layout = QVBoxLayout()
        layout.insertStretch(-1)

        self.widget.setLayout(layout)
