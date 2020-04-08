import sys

from PySide2 import QtWidgets
import widget_polygone_view


class PolygonEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PolygonEditor, self).__init__(parent)
        print('EDITOR', widget_polygone_view.imagePolygon)

        w = widget_polygone_view.WidgetWindow(self)
        w.show()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    m = PolygonEditor()
    # w = WidgetWindow(m)
    m.resize(1000, 600)
    m.show()
    sys.exit(app.exec_())
