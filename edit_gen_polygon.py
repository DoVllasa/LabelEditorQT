import sys

from PySide2 import QtWidgets
from PySide2.QtWidgets import QMainWindow
import widget_polygone_view


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        w = widget_polygone_view.WidgetWindow(self)
        w.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    m = MainWindow()
    # w = WidgetWindow(m)
    m.resize(1000, 600)
    m.show()
    sys.exit(app.exec_())
