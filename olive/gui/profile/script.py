from functools import lru_cache
import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QSizePolicy,
    QTextEdit,
    QWizardPage,
)

from olive.core.script import Script
from olive.core.utils import enumerate_namespace_subclass
import olive.scripts

__all__ = ["ScriptPage"]

logger = logging.getLogger(__name__)


class ScriptPage(QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Script")
        self.setSubTitle(
            "Please select a script that can describe the necessary acquisition steps."
        )

        # left
        script_list = QListWidget()
        script_list_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        script_list_policy.setHorizontalStretch(1)
        script_list.setSizePolicy(script_list_policy)
        script_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # right
        description = QTextEdit()
        description_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        description_policy.setHorizontalStretch(2)
        description.setSizePolicy(description_policy)
        # use parent background color
        description.setAutoFillBackground(True)

        layout = QHBoxLayout()
        layout.addWidget(script_list)
        layout.addWidget(description)

        self.setLayout(layout)

    def initializePage(self):
        scripts = self._enumerate_scripts()

    ##

    @lru_cache(maxsize=1)
    def _enumerate_scripts(self):
        return enumerate_namespace_subclass(olive.scripts, Script)
