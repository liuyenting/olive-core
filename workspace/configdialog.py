from qtpy import QtCore, QtGui, QtWidgets

import configdialog_rc


class ConfigurationPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ConfigurationPage, self).__init__(parent)

        configGroup = QtWidgets.QGroupBox("Server configuration")

        serverLabel = QtWidgets.QLabel("Server:")
        serverCombo = QtWidgets.QComboBox()
        serverCombo.addItem("Trolltech (Australia)")
        serverCombo.addItem("Trolltech (Germany)")
        serverCombo.addItem("Trolltech (Norway)")
        serverCombo.addItem("Trolltech (People's Republic of China)")
        serverCombo.addItem("Trolltech (USA)")

        serverLayout = QtWidgets.QHBoxLayout()
        serverLayout.addWidget(serverLabel)
        serverLayout.addWidget(serverCombo)

        configLayout = QtWidgets.QVBoxLayout()
        configLayout.addLayout(serverLayout)
        configGroup.setLayout(configLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(configGroup)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class UpdatePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UpdatePage, self).__init__(parent)

        updateGroup = QtWidgets.QGroupBox("Package selection")
        systemCheckBox = QtWidgets.QCheckBox("Update system")
        appsCheckBox = QtWidgets.QCheckBox("Update applications")
        docsCheckBox = QtWidgets.QCheckBox("Update documentation")

        packageGroup = QtWidgets.QGroupBox("Existing packages")

        packageList = QtWidgets.QListWidget()
        qtItem = QtWidgets.QListWidgetItem(packageList)
        qtItem.setText("Qt")
        qsaItem = QtWidgets.QListWidgetItem(packageList)
        qsaItem.setText("QSA")
        teamBuilderItem = QtWidgets.QListWidgetItem(packageList)
        teamBuilderItem.setText("Teambuilder")

        startUpdateButton = QtWidgets.QPushButton("Start update")

        updateLayout = QtWidgets.QVBoxLayout()
        updateLayout.addWidget(systemCheckBox)
        updateLayout.addWidget(appsCheckBox)
        updateLayout.addWidget(docsCheckBox)
        updateGroup.setLayout(updateLayout)

        packageLayout = QtWidgets.QVBoxLayout()
        packageLayout.addWidget(packageList)
        packageGroup.setLayout(packageLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(updateGroup)
        mainLayout.addWidget(packageGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(startUpdateButton)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class QueryPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QueryPage, self).__init__(parent)

        packagesGroup = QtWidgets.QGroupBox("Look for packages")

        nameLabel = QtWidgets.QLabel("Name:")
        nameEdit = QtWidgets.QLineEdit()

        dateLabel = QtWidgets.QLabel("Released after:")
        dateEdit = QtWidgets.QDateTimeEdit(QtCore.QDate.currentDate())

        releasesCheckBox = QtWidgets.QCheckBox("Releases")
        upgradesCheckBox = QtWidgets.QCheckBox("Upgrades")

        hitsSpinBox = QtWidgets.QSpinBox()
        hitsSpinBox.setPrefix("Return up to ")
        hitsSpinBox.setSuffix(" results")
        hitsSpinBox.setSpecialValueText("Return only the first result")
        hitsSpinBox.setMinimum(1)
        hitsSpinBox.setMaximum(100)
        hitsSpinBox.setSingleStep(10)

        startQueryButton = QtWidgets.QPushButton("Start query")

        packagesLayout = QtWidgets.QGridLayout()
        packagesLayout.addWidget(nameLabel, 0, 0)
        packagesLayout.addWidget(nameEdit, 0, 1)
        packagesLayout.addWidget(dateLabel, 1, 0)
        packagesLayout.addWidget(dateEdit, 1, 1)
        packagesLayout.addWidget(releasesCheckBox, 2, 0)
        packagesLayout.addWidget(upgradesCheckBox, 3, 0)
        packagesLayout.addWidget(hitsSpinBox, 4, 0, 1, 2)
        packagesGroup.setLayout(packagesLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(packagesGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(startQueryButton)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)

        self.contentsWidget = QtWidgets.QListWidget()
        self.contentsWidget.setViewMode(QtWidgets.QListView.IconMode)
        self.contentsWidget.setIconSize(QtCore.QSize(96, 84))
        self.contentsWidget.setMovement(QtWidgets.QListView.Static)
        self.contentsWidget.setMaximumWidth(128)
        self.contentsWidget.setSpacing(12)

        self.pagesWidget = QtWidgets.QStackedWidget()
        self.pagesWidget.addWidget(ConfigurationPage())
        self.pagesWidget.addWidget(UpdatePage())
        self.pagesWidget.addWidget(QueryPage())

        closeButton = QtWidgets.QPushButton("Close")

        self.createIcons()
        self.contentsWidget.setCurrentRow(0)

        closeButton.clicked.connect(self.close)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(closeButton)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

        self.setWindowTitle("Config Dialog")

    def changePage(self, current, previous):
        if not current:
            current = previous

        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        configButton = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton.setIcon(QtGui.QIcon(":/images/config.png"))
        configButton.setText("Configuration")
        configButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        configButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        updateButton = QtWidgets.QListWidgetItem(self.contentsWidget)
        updateButton.setIcon(QtGui.QIcon(":/images/update.png"))
        updateButton.setText("Update")
        updateButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        updateButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        queryButton = QtWidgets.QListWidgetItem(self.contentsWidget)
        queryButton.setIcon(QtGui.QIcon(":/images/query.png"))
        queryButton.setText("Query")
        queryButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        queryButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.contentsWidget.currentItemChanged.connect(self.changePage)


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec_())
