from abc import abstractmethod
import logging
import os

from PySide2.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWizardPage,
)

__all__ = ["NewFilePage", "OpenFilePage"]

logger = logging.getLogger(__name__)


class FilePage(QWizardPage):
    def __init__(self, home=None):
        super().__init__()

        if not home:
            home = os.path.expanduser("~")
        self._home = home

        self.setTitle("Intro")

        profile_path_label = QLabel("New profile path")
        profile_path_lineedit = QLineEdit()
        profile_path_button = QPushButton("...")
        profile_path_button.clicked.connect(self._update_profile_path)
        profile_path_layout = QHBoxLayout()
        profile_path_layout.addWidget(profile_path_lineedit)
        profile_path_layout.addWidget(profile_path_button)

        layout = QVBoxLayout()
        layout.addWidget(profile_path_label)
        layout.addLayout(profile_path_layout)
        self.setLayout(layout)

        self.registerField("profile_path", profile_path_lineedit)

    def initializePage(self):
        # ask immediately
        self._update_profile_path()

    def validateCurrentPage(self):
        # TODO [create]->create new profile fd, [open]->deserialize from file
        return True

    ##

    @abstractmethod
    def _update_profile_path(self, profile_path):
        self.setField("profile_path", profile_path)


class NewFilePage(FilePage):
    def __init__(self):
        super().__init__()

        self.setSubTitle("Create a new profile.")

    def _update_profile_path(self):
        profile_path, _ = QFileDialog.getSaveFileName(
            self, "Where to save the profile?", self._home, "Profile (*.json)"
        )
        logger.info(f'save profile to "{profile_path}"')
        super()._update_profile_path(profile_path)


class OpenFilePage(FilePage):
    def __init__(self):
        super().__init__()

        raise NotImplementedError("open an existing profile is not supported yet")

    def _update_profile_path(self):
        profile_path, _ = QFileDialog.getOpenFileName(
            self, "Where is the profile?", self._home, "Profile (*.json)"
        )
        logger.info(f'open profile from "{profile_path}"')
        super()._update_profile_path(profile_path)

