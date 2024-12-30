import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow)

import WebServerService
from MainWindow import MainWindow
from WebServerService import web_server_service


def exit_all():
    """ Terminate all process on program exit. """
    m.terminate_app()


print("Start the Qt app...")
App = QApplication(sys.argv)
m = MainWindow()

m.show()
m.raise_()

try:
    sys.exit(App.exec())
finally:
    exit_all()
