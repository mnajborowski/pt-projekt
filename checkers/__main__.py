import sys

from PyQt5.QtWidgets import QApplication

from checkers.gui.app_window import AppWindow

app = QApplication(sys.argv)
app.setApplicationName('Checkers')

app_window = AppWindow()
app_window.show()

sys.exit(app.exec_())
