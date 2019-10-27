import logging

from PySide2.QtWidgets import QWizard

from olive.gui.profile import (
    NewFilePage,
    OpenFilePage,
    ScriptPage,
    SequencerPage,
    DevicesPage,
    SummaryPage,
)

__all__ = ["ProfileWizard"]

logger = logging.getLogger(__name__)


class ProfileWizard(QWizard):
    def __init__(self, create_new=False):
        super().__init__()

        self.setWindowTitle("Profile Wizard")
        self.setWizardStyle(QWizard.ModernStyle)

        self.setModal(True)

        if create_new:
            self.addPage(NewFilePage())
        else:
            self.addPage(OpenFilePage())
        self.addPage(ScriptPage())
        self.addPage(SequencerPage())
        self.addPage(DevicesPage())
        self.addPage(SummaryPage())

    def get_configured_profile(self):
        return {'script': self.field('script')}
