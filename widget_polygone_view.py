import os
import sys
from enum import Enum
from functools import partial
from os import listdir
from os.path import isfile, join
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import SIGNAL, QObject, QRect, SLOT
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QPushButton, QWidget, QLabel, \
    QVBoxLayout, QGraphicsProxyWidget
from PySide2.QtGui import QColor

from widget import Ui_Widget


class PolygonItemsDisplay(QtWidgets.QGraphicsPathItem):
    circle = QtGui.QPainterPath()
    circle.addEllipse(QtCore.QRectF(-10, -10, 20, 20))
    square = QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-15, -15, 30, 30))

    def __init__(self, annotationItem, index):
        super(PolygonItemsDisplay, self).__init__()
        self.mAnnotationItem = annotationItem
        # print("ANNOTATIONITEM", self.mAnnotationItem)
        self.mIndex = index
        self.setPath(PolygonItemsDisplay.circle)
        self.setBrush(QtGui.QColor("blue"))
        self.setPen(QtGui.QPen(QtGui.QColor("blue"), 2))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        self.setZValue(11)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def hoverEnterEvent(self, event):
        self.setPath(PolygonItemsDisplay.square)
        self.setBrush(QtGui.QColor("blue"))
        super(PolygonItemsDisplay, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPath(PolygonItemsDisplay.circle)
        self.setBrush(QtGui.QColor("blue"))
        super(PolygonItemsDisplay, self).hoverLeaveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setSelected(False)
        super(PolygonItemsDisplay, self).mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.isEnabled():
            self.mAnnotationItem.movePoint(self.mIndex, value)
        return super(PolygonItemsDisplay, self).itemChange(change, value)


class PolygonAnnotation(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(PolygonAnnotation, self).__init__(parent)
        self.mPoints = []
        self.setZValue(10)
        self.setPen(QtGui.QPen(QtGui.QColor("blue"), 2))
        self.setAcceptHoverEvents(True)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)

        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.setBrush(QtGui.QColor(63, 136, 143, 100))

        self.mItems = []

    def number_of_points(self):
        return len(self.mItems)

    def addPoint(self, p):
        self.mPoints.append(p)
        self.setPolygon(QtGui.QPolygonF(self.mPoints))
        item = PolygonItemsDisplay(self, len(self.mPoints) - 1)
        item.setScale(0.3)
        self.scene().addItem(item)
        self.mItems.append(item)
        item.setPos(p)

    def removeLastPoint(self):
        if self.mPoints:
            self.mPoints.pop()
            self.setPolygon(QtGui.QPolygonF(self.mPoints))
            it = self.mItems.pop()
            self.scene().removeItem(it)
            del it

    def movePoint(self, i, p):
        if 0 <= i < len(self.mPoints):
            self.mPoints[i] = self.mapFromScene(p)
            self.setPolygon(QtGui.QPolygonF(self.mPoints))

    def move_item(self, index, pos):
        if 0 <= index < len(self.mItems):
            item = self.mItems[index]
            item.setEnabled(False)
            item.setPos(pos)
            item.setEnabled(True)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for i, point in enumerate(self.mPoints):
                self.move_item(i, self.mapToScene(point))
        return super(PolygonAnnotation, self).itemChange(change, value)


class ImageScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(ImageScene, self).__init__(parent)
        self.imageItem = QtWidgets.QGraphicsPixmapItem()
        self.imageItem.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.addItem(self.imageItem)
        self.currentInstruction = Instructions.NoInstruction
        self.polygonItems = []
        self.imageName = ''
        self.polygonPoints = []
        self.colorCodeDictonary = {}
        self.getColorOfPoly = []
        self.categorizedPolys = {}

    def load_image(self, filename):
        self.imageItem.setPixmap(QtGui.QPixmap(filename))
        self.setSceneRect(self.imageItem.boundingRect())
        self.imageName = filename
        if filename in imagePolygon:
            imagePolyData = imagePolygon[filename]
            self.colorCodeDictonary = imagePolyData
            if 0 in self.colorCodeDictonary:
                self.createPoly(0)
            if 1 in self.colorCodeDictonary:
                self.createPoly(1)
            if 2 in self.colorCodeDictonary:
                self.createPoly(2)
            if 3 in self.colorCodeDictonary:
                self.createPoly(3)
            if 4 in self.colorCodeDictonary:
                self.createPoly(4)
            if 5 in self.colorCodeDictonary:
                self.createPoly(5)
            if 6 in self.colorCodeDictonary:
                self.createPoly(6)

    def createPoly(self, colorCode):
        # print('COLORCOLORCOLOR', self.colorCodeList[colorCode])
        self.categorizedPolys = {}
        for i in self.colorCodeDictonary[colorCode]:
            # print('III', i)
            self.polygonItem = PolygonAnnotation()
            self.setPolygonColor(colorCode)
            self.addItem(self.polygonItem)
            self.polygonItems.append(self.polygonItem)
            for k in i:
                self.positionAddPoint(k)
            if colorCode in self.categorizedPolys:
                self.categorizedPolys[colorCode].append(i)
            else:
                createTmpListCoord = []
                createTmpListCoord.append(i)
                self.categorizedPolys[colorCode] = createTmpListCoord
            self.polygonPoints = []
        # print('KATEGORIEN', self.categorizedPolys)

    def setPolygonColor(self, colorcode):
        if colorcode == 0:
            self.polygonItem.setBrush(QtGui.QColor(255, 0, 0, 150))
        elif colorcode == 1:
            self.polygonItem.setBrush(QtGui.QColor(0, 0, 255, 150))
        elif colorcode == 2:
            self.polygonItem.setBrush(QtGui.QColor(0, 255, 0, 150))
        elif colorcode == 3:
            self.polygonItem.setBrush(QtGui.QColor(255, 127, 36, 150))
        elif colorcode == 4:
            self.polygonItem.setBrush(QtGui.QColor(155, 48, 255, 150))
        elif colorcode == 5:
            self.polygonItem.setBrush(QtGui.QColor(0, 191, 255, 150))
        elif colorcode == 6:
            self.polygonItem.setBrush(QtGui.QColor(255, 0, 255, 150))

    def setCurrentInstruction(self, instruction, colorcode):
            print('TESTSESETSESE')
            self.currentInstruction = instruction
            self.polygonItem = PolygonAnnotation()
            self.setPolygonColor(colorcode)
            self.addItem(self.polygonItem)
            self.polygonItems.append(self.polygonItem)

            if self.currentInstruction == Instructions.PolygonInstruction:
                self.getColorOfPoly.append(self.polygonItem.brush().color())

            if len(self.polygonPoints) != 0 and len(self.getColorOfPoly) > 0:
                if self.getColorOfPoly[0].getRgb() == QColor(255, 0, 0, 150).getRgb():
                    self.onCreateColorList(0)
                elif self.getColorOfPoly[0].getRgb() == QColor(0, 0, 255, 150).getRgb():
                    self.onCreateColorList(1)
                elif self.getColorOfPoly[0].getRgb() == QColor(0, 255, 0, 150).getRgb():
                    self.onCreateColorList(2)
                elif self.getColorOfPoly[0].getRgb() == QColor(255, 127, 36, 150).getRgb():
                    self.onCreateColorList(3)
                elif self.getColorOfPoly[0].getRgb() == QColor(155, 48, 255, 150).getRgb():
                    self.onCreateColorList(4)
                elif self.getColorOfPoly[0].getRgb() == QColor(0, 191, 255, 150).getRgb():
                    self.onCreateColorList(5)
                elif self.getColorOfPoly[0].getRgb() == QColor(255, 0, 255, 150).getRgb():
                    self.onCreateColorList(6)


                print('CODELIST', self.colorCodeDictonary)

    def onCreateColorList(self, var):
        if var not in self.colorCodeDictonary:
            polyTmpPointsCoord = []
            polyTmpPointsCoord.append(self.polygonPoints)
            self.colorCodeDictonary[var] = polyTmpPointsCoord
        elif self.polygonPoints not in self.colorCodeDictonary[var]:
            self.colorCodeDictonary[var].append(self.polygonPoints)
        self.getColorOfPoly = []
        self.polygonPoints = []

    def mousePressEvent(self, event):
        if self.currentInstruction == Instructions.PolygonInstruction:
            self.positionAddPoint(event.scenePos())
            print('AAAAAAAA^')

        super(ImageScene, self).mousePressEvent(event)

    def positionAddPoint(self, position):
        self.polygonItem.removeLastPoint()
        self.polygonItem.addPoint(position)
        self.polygonItem.addPoint(position)
        self.polygonPoints.append(position)

    def mouseMoveEvent(self, event):
        if self.currentInstruction == Instructions.PolygonInstruction:
            self.polygonItem.movePoint(self.polygonItem.number_of_points() - 1, event.scenePos())
        super(ImageScene, self).mouseMoveEvent(event)

    def removePolygon(self):
        colorCode = None
        if self.polygonItem:
            for k in self.selectedItems():
                allPointsFromItem = k.mPoints[:-1]
                if k.brush().color().getRgb() == QColor(255, 0, 0, 150).getRgb():
                    colorCode = 0
                elif k.brush().color().getRgb() == QColor(0, 0, 255, 150).getRgb():
                    colorCode = 1
                elif k.brush().color().getRgb() == QColor(0, 255, 0, 150).getRgb():
                    colorCode = 2
                elif k.brush().color().getRgb() == QColor(255, 127, 36, 150).getRgb():
                    colorCode = 3
                elif k.brush().color().getRgb() == QColor(155, 48, 255, 150).getRgb():
                    colorCode = 4
                elif k.brush().color().getRgb() == QColor(0, 191, 255, 150).getRgb():
                    colorCode = 5
                elif k.brush().color().getRgb() == QColor(255, 0, 255, 150).getRgb():
                    colorCode = 6

                newCoordFromPoly = []
                for j in self.colorCodeDictonary[colorCode]:
                    if allPointsFromItem != j:
                        newCoordFromPoly.append(j)
                self.colorCodeDictonary[colorCode] = newCoordFromPoly
                while len(k.mPoints) > 0:
                    k.removeLastPoint()
                self.removeItem(k)
            for i in self.selectedItems():
                i.removeLastPoint()
                self.removeItem(i)

    def removeAllPolygone(self):
        addToImagePoly(self.colorCodeDictonary, self.imageName)
        for k in self.polygonItems:
            while len(k.mPoints) > 0:
                k.removeLastPoint()
            self.removeItem(k)
        self.polygonItems = []
        self.polygonPoints = []
        self.allPolygonPointsFromImg = []
        self.colorCodeDictonary = {}
        for i in self.selectedItems():
            self.removeItem(i)


imagePolygon = {}

def addToImagePoly(colorDict: dict, name: str):
    imagePolygon[name] = colorDict


class Instructions(Enum):
    NoInstruction = 0
    PolygonInstruction = 1
    BackItem = 0
    NextItem = 1


class Categorization(Enum):
    Red = 0
    Blue = 1
    Green = 2
    Orange = 3
    Purple = 4
    LightBlue = 5
    Pink = 6


class WidgetWindow(QWidget):
    factor = 2.0

    def __init__(self, parent=None):
        super(WidgetWindow, self).__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.setWindowTitle("Truth Data generator Parcels")
        self.ui.graphicsView.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.ui.graphicsView.setMouseTracking(True)
        self.mView = self.ui.graphicsView
        self.mScene = ImageScene(self)
        self.mView.setScene(self.mScene)
        self.counterImages = 0
        self.colorNum = 0
        self.directory = '/Users/dominim/Desktop/TestData'
        # self.directory = '/home/dominim/Desktop/Data/wa1122/wa1122/png_rgb/t000'
        self.filenames = [f for f in listdir(self.directory) if isfile(join(os.path.realpath(self.directory), f))]
        self.realpathImages = []
        for index, filename in enumerate(self.filenames):
            self.realpathImages.append(self.directory + '/' + filename)
        self.load_image(Instructions.BackItem)
        # self.ui.nextImageButton.clicked.connect(partial(self.load_image, Instructions.NextItem.value))
        # self.ui.backButton.clicked.connect(partial(self.load_image, Instructions.BackItem.value))
        # self.ui.removeButton.clicked.connect(self.mScene.removePolygon)

# ----------------------------------------------------------------------------------------------------------------------
#   initialize Buttons for drawing Polygone
# ----------------------------------------------------------------------------------------------------------------------

        self.ui.boxButton.setStyleSheet("color: #FF0000")  # Red 255, 0, 0
        self.ui.bagButton.setStyleSheet("color: #0000FF")  # blue 0, 0, 255
        self.ui.pouchButton.setStyleSheet("color: #00FF00")  # Green 0, 255, 0
        self.ui.unknownButton.setStyleSheet("color: #FF7F24")  # orange 255, 127, 36
        self.ui.restButton.setStyleSheet("color: #9B30FF")  # purple 155, 48, 255
        self.ui.flatButton.setStyleSheet("color: #00BFFF")  # Lightblue 0, 191, 255
        self.ui.armButton.setStyleSheet("color: #FF00FF")  # pink 255, 0 ,255

        self.ui.boxButton.clicked.connect(partial(self.setColorCode, Categorization.Red.value))
        self.ui.bagButton.clicked.connect(partial(self.setColorCode, Categorization.Blue.value))
        self.ui.pouchButton.clicked.connect(partial(self.setColorCode, Categorization.Green.value))
        self.ui.unknownButton.clicked.connect(partial(self.setColorCode, Categorization.Orange.value))
        self.ui.restButton.clicked.connect(partial(self.setColorCode, Categorization.Purple.value))
        self.ui.flatButton.clicked.connect(partial(self.setColorCode, Categorization.LightBlue.value))
        self.ui.armButton.clicked.connect(partial(self.setColorCode, Categorization.Pink.value))

# ----------------------------------------------------------------------------------------------------------------------
#   Set Shortcuts for QGraphicsView
# ----------------------------------------------------------------------------------------------------------------------

        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomIn, self.mView, self.zoomIn)
        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomOut, self.mView, self.zoomOut)

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self.mView,
                            activated=partial(self.load_image, Instructions.NextItem.value))
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), self.mView,
                            activated=partial(self.load_image, Instructions.BackItem.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self.mView,
                            activated=partial(self.mScene.setCurrentInstruction, Instructions.NoInstruction,
                                              self.colorNum))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_X), self.mView, self.mScene.removePolygon)

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A), self.mView,
                            activated=partial(self.mScene.setCurrentInstruction, Instructions.PolygonInstruction,
                                              self.colorNum))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_X), self.mView, self.mScene.removeAllPolygone)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Y), self.mView, self.mScene.removePolygon)

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_1), self.mView,
                            activated=partial(self.setColorCode, Categorization.Red.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_2), self.mView,
                            activated=partial(self.setColorCode, Categorization.Blue.value))
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_3), self.mView,
                                activated=partial(self.setColorCode, Categorization.Green.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_4), self.mView,
                            activated=partial(self.setColorCode, Categorization.Orange.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_5), self.mView,
                            activated=partial(self.setColorCode, Categorization.Purple.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_6), self.mView,
                            activated=partial(self.setColorCode, Categorization.LightBlue.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_7), self.mView,
                            activated=partial(self.setColorCode, Categorization.Pink.value))

# ----------------------------------------------------------------------------------------------------------------------
#   Set Categorization with from images with ColorCodes
# ----------------------------------------------------------------------------------------------------------------------

    def setColorCode(self, code):
        self.colorNum = code
        # print(self.colorNum)
        self.mScene.setCurrentInstruction(Instructions.PolygonInstruction, self.colorNum)

# ----------------------------------------------------------------------------------------------------------------------
#   Set View Modification with ZoomIn/-Out
# ----------------------------------------------------------------------------------------------------------------------

    @QtCore.Slot()
    def zoomIn(self):
        self.zoom(2)

    @QtCore.Slot()
    def zoomOut(self):
        self.zoom(1 / 2)

    def zoom(self, f):
        self.mView.scale(f, f)
        if self.mView.scene() is not None:
            self.mView.centerOn(self.mView.scene().imageItem)

    def showEvent(self, event: QtGui.QShowEvent):
        self.mView.fitInView(self.mScene.sceneRect(), QtCore.Qt.KeepAspectRatio)

# ----------------------------------------------------------------------------------------------------------------------
#   Load Images in QGraphicsScene and fit in QGraphicsView
# ----------------------------------------------------------------------------------------------------------------------

    @QtCore.Slot()
    def load_image(self, imageNavigation):
        self.mScene.removeAllPolygone()
        if imageNavigation == 1 and self.counterImages < self.realpathImages.__len__() - 1:
            self.counterImages = self.counterImages + 1
        elif imageNavigation == 0 and self.counterImages > 0:
            self.counterImages = self.counterImages - 1
        else:
            self.counterImages = 0

        if self.realpathImages[self.counterImages]:
            self.mScene.load_image(self.realpathImages[self.counterImages])
            self.mView.fitInView(self.mScene.imageItem, QtCore.Qt.KeepAspectRatio)
            self.mView.centerOn(self.mScene.imageItem)


# class MainWindow(QMainWindow):
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # m = MainWindow()
    # w = WidgetWindow(m)
    # m.show()
    w = WidgetWindow()
    w.show()
    sys.exit(app.exec_())