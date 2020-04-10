from widget_polygone_view import *
import sys


# class PolygonEditor:
#   def __init__(self, gui: QtruthApp):

# class PolygonEditor(QtWidgets.QWidget):
# class PolygonEditor:
#     def __init__(self, gui: MainWindow):
class PolygonEditor(QtWidgets.QWidget):
    def __init__(self):
        super(PolygonEditor, self).__init__()
        # self.callDict(dictonary)
        # WidgetWindow(gui/QQtruthApp)
        WidgetWindow(self)
        # WidgetWindow(gui)

    def getImagePolygonDictonary(test: dict):
        print('Polygon from widget_polygon_view', test)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    p = PolygonEditor()
    p.resize(1000, 600)
    p.show()
    sys.exit(app.exec_())