import logging

from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QDesktopWidget, QMainWindow, QStatusBar

from olive.gui.profile import ProfileWizard
from olive.gui.resources import ICON

__all__ = ["MainWindow"]


logger = logging.getLogger(__name__)


class StatusBarLogger(logging.Handler):
    def __init__(self, statusbar: QStatusBar, timeout=5000):
        super().__init__()
        self.statusbar = statusbar
        self.timeout = timeout

    def emit(self, record):
        message = self.format(record)
        self.statusbar.showMessage(message, self.timeout)

    def writes(self, message):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Olive")

        # DEBUG, (800, 600)
        self.init_window_size((1024, 768))

        self.setup_menubar()
        self.setup_toolbar()
        self.setup_dockwidgets()
        self.setup_statusbar()

        logger.info("Done")

    ##

    def init_window_size(self, size=None, ratio=0.7):
        """
        Initial window size. If not specified, default to 70% of the screen size.
        """
        if size is None:
            size = QDesktopWidget().availableGeometry().size() * ratio
        elif isinstance(size, tuple):
            size = QSize(*size)
        self.resize(size)

    ##

    def setup_menubar(self):
        menubar = self.menuBar()

        """
        File
        """
        file_menu = menubar.addMenu("File")
        self._new_menu_action(file_menu, "New Profile", self.new_profile_action)
        self._new_menu_action(file_menu, 'Open Profile', None).setDisabled(True)
        file_menu.addSeparator()
        file_menu.addAction("Quit")

        """
        Tools
        """
        tools_menu = menubar.addMenu("Tools")

        """
        Window
        """
        window_menu = menubar.addMenu("Window")

        """
        Help
        """
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")

    def setup_toolbar(self):
        pass

    def setup_dockwidgets(self):
        """
        Create all the dockwidgets, but hide them all during startup. Their
        visibilities depend on loaded script.
        """
        # TODO populate dockwidgets using supported script features
        # NOTE who to query the features? dispatcher?
        pass

    def setup_statusbar(self):
        handler = StatusBarLogger(self.statusBar())
        logging.getLogger().addHandler(handler)

    ##

    def new_profile_action(self):
        wizard = ProfileWizard(create_new=True)
        wizard.exec_()
        if wizard.get_configured_profile():
            # TODO valid profile, start populating dock widgets
            pass

    ##

    def _new_menu_action(self, menu, name, callback, checkable=False, **kwargs):
        action = menu.addAction(name)
        if checkable:
            self._new_checkable_action(action, callback, **kwargs)
        else:
            self._new_triggerable_action(action, callback, **kwargs)
        return action

    def _new_checkable_action(self, action, callback, checked=False):
        action.setCheckable(True)
        action.setChecked(checked)
        action.toggled.connect(callback)

    def _new_triggerable_action(self, action, callback):
        action.triggered.connect(callback)
