from widget_polygone_view import *


class PolygonEditor(QtWidgets.QWidget):
    def __init__(self):
        super(PolygonEditor, self).__init__()
        # self.callDict(dictonary)
        WidgetWindow(self)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    p = PolygonEditor()
    p.resize(1000, 600)
    p.show()
    sys.exit(app.exec_())