from collections import namedtuple
from functools import lru_cache
import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QWizardPage,
)

from olive.core.script import Script
from olive.core.utils import enumerate_namespace_classes

import olive.scripts

__all__ = ["ScriptPage"]

logger = logging.getLogger(__name__)


class ScriptListItem(QWidget):
    def __init__(self, klass, category):
        super().__init__()

        script_name = QLabel(klass.__name__)
        script_name.setStyleSheet("font: bold")

        script_category = QLabel(category.__name__)
        script_category.setStyleSheet("font: italic")

        layout = QVBoxLayout()
        layout.addWidget(script_name)
        layout.addWidget(script_category)

        self.setLayout(layout)


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
        self.script_list = script_list

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

        self._script = 123
        self.registerField("script", self, "script")

    def initializePage(self):
        self.script_list.clear()

        for category, klass in self._enumerate_scripts():
            # wrap the script as a widget
            script = ScriptListItem(klass, category)

            # create new empty entry
            item = QListWidgetItem(self.script_list)
            item.setSizeHint(script.minimumSizeHint())

            # add the wrapped script to the entry
            self.script_list.setItemWidget(item, script)

        # select first one
        self.script_list.setCurrentRow(0)

    def validateCurrentPage(self):
        item = self.script_list.currentItem()
        _, script = self.script_list.itemWidget(item)
        self.setField("script", script)
        return True

    ##

    @lru_cache(maxsize=1)
    def _enumerate_scripts(self):
        """
        Enumerate scripts using their package as category.

        Returns:
            (list of tuples): scripts and the package they reside in
        """
        return enumerate_namespace_classes(
            olive.scripts, lambda x: issubclass(x, Script), with_pkg=True
        )

    ##

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, klass):
        self._script = klass