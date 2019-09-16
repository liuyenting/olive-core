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

__all__ = ["PathPage"]

logger = logging.getLogger(__name__)


class PathPage(QWizardPage):
    def __init__(self, create_new):
        super().__init__()

        self._create_new = create_new

        self.setTitle("Intro")

        if self.create_new:
            self.setSubTitle("Create a new profile.")
        else:
            raise NotImplementedError("open an existing profile is not supported yet")

        profile_path_label = QLabel("New profile path")
        profile_path_lineedit = QLineEdit()
        profile_path_button = QPushButton("...")
        profile_path_button.clicked.connect(self._get_profile_path)
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
        self._get_profile_path()

    ##

    @property
    def create_new(self):
        return self._create_new

    ##

    def _get_profile_path(self, home=None):
        if self.create_new:
            title = "Where to save the profile?"
            dialog_func = QFileDialog.getSaveFileName
        else:
            title = "Where is the profile?"
            dialog_func = QFileDialog.getOpenFileName

        # default to start from user home directory
        if not home:
            home = os.path.expanduser("~")

        profile_path, _ = dialog_func(self, title, home, "Profile (*.json)")

        # update local field
        self.setField("profile_path", profile_path)
        if self.create_new:
            logger.info(f'save profile to "{profile_path}"')
        else:
            logger.info(f'open profile from "{profile_path}"')
        return profile_path
