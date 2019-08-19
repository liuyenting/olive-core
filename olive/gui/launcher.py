import sys

from PySide2.QtWidgets import QApplication

from olive.gui.hub import Hub

if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = Hub()
    win.show()

    sys.exit(app.exec_())
