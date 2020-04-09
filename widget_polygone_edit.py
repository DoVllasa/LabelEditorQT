import os
import sys
from enum import Enum
from functools import partial
from os import listdir
from os.path import isfile, join
from warnings import warn
from PySide2 import QtWidgets, QtGui, QtCore
import copy

from PySide2.QtWidgets import QWidget, QMainWindow
from PySide2.QtGui import QColor
from widget import Ui_Widget
import edit_gen_polygon


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
        # self.setFlag(QtWidgets.QGraphicsItem.ItemPositionChange, True)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemSelectedHasChanged, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.setBrush(QtGui.QColor(63, 136, 143, 100))
        self.mItems = []
        self.test =[]

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
            # self.mPoints[i] = p
            self.setPolygon(QtGui.QPolygonF(self.mPoints))
            # print('POLY', self.mapFromScene(p))
            # print('POLY', self.mPoints[:-1])
            # if self.mouseReleaseEvent(self):
            #     print('POLYAFTERRELEASE', self.mPoints)


    def move_item(self, index, pos):
        if 0 <= index < len(self.mItems):
            item = self.mItems[index]
            item.setEnabled(False)
            item.setPos(pos)
            self.movePoint(index, pos)
            self.test.append(pos)
            # print('MPOINTSBEVOR', pos)
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
        self.savedCategoryDictonary = {}
        self.getColorOfPoly = []
        self.categorizedPolys = {}
        self.colorDefinition = {}
        self.colorDefinition[Categorization.Box.value] = QtGui.QColor(255, 0, 0, 150)
        self.colorDefinition[Categorization.Bag.value] = QtGui.QColor(0, 0, 255, 150)
        self.colorDefinition[Categorization.Bundle.value] = QtGui.QColor(0, 255, 0, 150)
        self.colorDefinition[Categorization.Unknown.value] = QtGui.QColor(255, 127, 36, 150)
        self.colorDefinition[Categorization.Rest.value] = QtGui.QColor(155, 48, 255, 150)
        self.colorDefinition[Categorization.Flat.value] = QtGui.QColor(255, 255, 0, 150)
        self.colorDefinition[Categorization.TransparentBag.value] = QtGui.QColor(0, 191, 255, 150)


    def load_image(self, filename):
        self.imageItem.setPixmap(QtGui.QPixmap(filename))
        self.setSceneRect(self.imageItem.boundingRect())
        self.imageName = filename
        print('POLYGONE', imagePolygon)
        if filename in imagePolygon:
            # print(imagePolygon)
            imagePolyData = imagePolygon[filename]
            self.savedCategoryDictonary = imagePolyData
            for i in self.savedCategoryDictonary.keys():
                self.createPoly(i)

    def createPoly(self, categorizationOfPolygone):
        self.categorizedPolys = {}
        for i in self.savedCategoryDictonary[categorizationOfPolygone]:
            self.polygonItem = PolygonAnnotation()
            # self.setPolygonColor(categorizationOfPolygone)
            self.polygonItem.setBrush(self.colorDefinition[categorizationOfPolygone])
            self.addItem(self.polygonItem)
            self.polygonItems.append(self.polygonItem)
            for k in i:
                self.positionAddPoint(k)
            if categorizationOfPolygone in self.categorizedPolys:
                self.categorizedPolys[categorizationOfPolygone].append(i)
            else:
                createTmpListCoord = []
                createTmpListCoord.append(i)
                self.categorizedPolys[categorizationOfPolygone] = createTmpListCoord
            self.polygonPoints = []


    def setCurrentInstruction(self, instruction, category: str):
        self.currentInstruction = instruction
        self.polygonItem = PolygonAnnotation()
        # self.setPolygonColor(category)
        self.polygonItem.setBrush(self.colorDefinition[category])
        self.addItem(self.polygonItem)
        self.polygonItems.append(self.polygonItem)
        print('BEVORBEOVR', self.savedCategoryDictonary)
        self.savedCategoryDictonary = {}
        for i in self.polygonItems:
            if len(i.mPoints) != 0:
                for k in self.colorDefinition.keys():
                    if self.colorDefinition[k].getRgb() == i.brush().color().getRgb():
                        listTest = copy.copy(i.mPoints)
                        if k not in self.savedCategoryDictonary:
                            polyTmpPointsCoord = []
                            polyTmpPointsCoord.append(listTest)
                            self.savedCategoryDictonary[k] = polyTmpPointsCoord
                            # self.savedCategoryDictonary[k] = listTest
                            break
                        elif listTest not in self.savedCategoryDictonary[k]:
                            print('FAIL')
                            # listTest = copy.copy(i.mPoints)
                            self.savedCategoryDictonary[k].append(listTest)
                            break
        print('SAVEDSAVEDSAVED', self.savedCategoryDictonary)
            # self.getColorOfPoly.append(self.polygonItem.brush().color())

        # if len(self.polygonPoints) != 0 and len(self.getColorOfPoly) > 0:
        # if len(self.polygonPoints) != 0:
        # for i in self.polygonItems:
        #     if len(i.mPoints) != 0:
        #         for k in self.colorDefinition.keys():
        #             if self.colorDefinition[k].getRgb() == i.brush().color().getRgb():
        #                 if k not in self.savedCategoryDictonary:
        #                     polyTmpPointsCoord = []
        #                     polyTmpPointsCoord.append(i.mPoints)
        #                     self.savedCategoryDictonary[k] = polyTmpPointsCoord
        #                     break
        #                 elif i.mPoints not in self.savedCategoryDictonary[k]:
        #                     self.savedCategoryDictonary[k].append(i.mPoints)
        #                     break



    #     if self.currentInstruction == Instructions.PolygonInstruction:
    #         self.getColorOfPoly.append(self.polygonItem.brush().color())
    #
    #     if len(self.polygonPoints) != 0 and len(self.getColorOfPoly) > 0:
    #         for i in self.colorDefinition.keys():
    #             if self.colorDefinition[i].getRgb() == self.getColorOfPoly[0].getRgb():
    #                 self.onCreateColorList(i)
    #                 break
    #
    #             # print('CODELIST', self.savedCategoryDictonary)
    #
    # def onCreateColorList(self, var):
    #     if var not in self.savedCategoryDictonary:
    #         polyTmpPointsCoord = []
    #         polyTmpPointsCoord.append(self.polygonPoints)
    #         self.savedCategoryDictonary[var] = polyTmpPointsCoord
    #     elif self.polygonPoints not in self.savedCategoryDictonary[var]:
    #         self.savedCategoryDictonary[var].append(self.polygonPoints)
    #     print(self.savedCategoryDictonary)
    #     self.getColorOfPoly = []
    #     self.polygonPoints = []

    def mousePressEvent(self, event):
        if self.currentInstruction == Instructions.PolygonInstruction:
            self.positionAddPoint(event.scenePos())
        super(ImageScene, self).mousePressEvent(event)

    def positionAddPoint(self, position):
        self.polygonItem.removeLastPoint()
        self.polygonItem.addPoint(position)
        self.polygonItem.addPoint(position)
        # self.polygonPoints.append(position)

    def mouseMoveEvent(self, event):
        if self.currentInstruction == Instructions.PolygonInstruction:
            self.polygonItem.movePoint(self.polygonItem.number_of_points() - 1, event.scenePos())
        super(ImageScene, self).mouseMoveEvent(event)

    def removePolygon(self):
        categorizationType = None
        if self.polygonItem:
            for items in self.selectedItems():
                try:
                    allCoordinatesFromItem = items.mPoints[:-1]
                except AttributeError:
                    warn('You tried to remove before finishing')
                    return

                for i in self.colorDefinition.keys():
                    if self.colorDefinition[i].getRgb() == items.brush().color().getRgb():
                        categorizationType = i
                        break
                newCoordFromPoly = []
                for itemsCoordinates in self.savedCategoryDictonary[categorizationType]:
                    if allCoordinatesFromItem != itemsCoordinates:
                        newCoordFromPoly.append(itemsCoordinates)
                if len(newCoordFromPoly) != 0:
                    self.savedCategoryDictonary[categorizationType] = newCoordFromPoly
                else:
                    del self.savedCategoryDictonary[categorizationType]
                while len(items.mPoints) > 0:
                    items.removeLastPoint()
                # self.removeItem(items)
            for i in self.selectedItems():
                i.removeLastPoint()
                # self.removeItem(i)

    def removeAllPolygone(self):
        # print('POLYGONINFOS', i.mPoints)
        # print('FARBCODE', i.brush().color().getRgb())

        setInformationFromImage(self.savedCategoryDictonary, self.imageName)

        for k in self.polygonItems:
            while len(k.mPoints) > 0:
                k.removeLastPoint()
            self.removeItem(k)
        self.savedCategoryDictonary = {}
        self.polygonItems = []
        # for i in self.selectedItems():
        #     self.removeItem(i)




imagePolygon = {}

def setInformationFromImage(catgorizedDict: dict, name: str):
    imagePolygon[name] = catgorizedDict

    print('ImagePoly', imagePolygon)
    # edit_gen_polygon.PolygonEditor.callDict(imagePolygon)


class Instructions(Enum):
    NoInstruction = 0
    PolygonInstruction = 1
    BackItem = 0
    NextItem = 1

# Über Categorization.Box.name ebenfall auf 'Box'
# Farbcode abspeichern, also Box = 'QtColor(255,0,0)'

class Categorization(Enum):
    Box = 'Box'
    Bag = 'Bag'
    Bundle = 'Bundle'
    Unknown = 'unknown'
    Rest = 'Rest'
    Flat = 'Flat'
    TransparentBag = 'Transparent bag'


# class WidgetWindow(QWidget):
#     factor = 2.0
#
#     def __init__(self, parent=None):
#         super(WidgetWindow, self).__init__(parent)
#         self.ui = Ui_Widget()
#         self.ui.setupUi(self)
#         self.setWindowTitle("Truth Data generator Parcels")
#         self.ui.graphicsView.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
#         self.ui.graphicsView.setMouseTracking(True)
#         self.mView = self.ui.graphicsView
#         self.mScene = ImageScene(self)
#         self.mView.setScene(self.mScene)
#         self.counterImages = 0
#         self.colorNum = 0
#         # self.directory = '/Users/dominim/Desktop/TestData'
#         self.directory = '/Users/dominimvllasa/Desktop/TestData'
#         # self.directory = '/home/dominim/Desktop/Data/wa1122/wa1122/png_rgb/t000'
#         self.filenames = [f for f in listdir(self.directory) if isfile(join(os.path.realpath(self.directory), f))]
#         self.realpathImages = []
#         for index, filename in enumerate(self.filenames):
#             self.realpathImages.append(self.directory + '/' + filename)
#         self.load_image(Instructions.BackItem)
#         # self.ui.nextImageButton.clicked.connect(partial(self.load_image, Instructions.NextItem.value))
#         # self.ui.backButton.clicked.connect(partial(self.load_image, Instructions.BackItem.value))
#         # self.ui.removeButton.clicked.connect(self.mScene.removePolygon)
#
# # ----------------------------------------------------------------------------------------------------------------------
# #   initialize Buttons for drawing Polygone
# # ----------------------------------------------------------------------------------------------------------------------
#
#         self.ui.boxButton.setStyleSheet("color: #FF0000")  # Red 255, 0, 0
#         self.ui.bagButton.setStyleSheet("color: #0000FF")  # blue 0, 0, 255
#         self.ui.bundleButton.setStyleSheet("color: #00FF00")  # Green 0, 255, 0
#         self.ui.unknownButton.setStyleSheet("color: #FF7F24")  # orange 255, 127, 36
#         self.ui.restButton.setStyleSheet("color: #9B30FF")  # purple 155, 48, 255
#         self.ui.flatButton.setStyleSheet("color: #FFFF00")  # pink 255, 255, 0
#         self.ui.transaprentBagButton.setStyleSheet("color: #00BFFF")  # Lightblue 0, 191, 255
#
#         self.ui.boxButton.clicked.connect(partial(self.setColorCode, Categorization.Box.value))
#         self.ui.bagButton.clicked.connect(partial(self.setColorCode, Categorization.Bag.value))
#         self.ui.bundleButton.clicked.connect(partial(self.setColorCode, Categorization.Bundle.value))
#         self.ui.unknownButton.clicked.connect(partial(self.setColorCode, Categorization.Unknown.value))
#         self.ui.restButton.clicked.connect(partial(self.setColorCode, Categorization.Rest.value))
#         self.ui.flatButton.clicked.connect(partial(self.setColorCode, Categorization.Flat.value))
#         self.ui.transaprentBagButton.clicked.connect(partial(self.setColorCode, Categorization.TransparentBag.value))
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# #   Set Shortcuts for QGraphicsView
# # ----------------------------------------------------------------------------------------------------------------------
#
#         QtWidgets.QShortcut(QtGui.QKeySequence.ZoomIn, self.mView, self.zoomIn)
#         QtWidgets.QShortcut(QtGui.QKeySequence.ZoomOut, self.mView, self.zoomOut)
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self.mView,
#                             activated=partial(self.load_image, Instructions.NextItem.value))
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), self.mView,
#                             activated=partial(self.load_image, Instructions.BackItem.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self.mView,
#                             activated=partial(self.mScene.setCurrentInstruction, Instructions.NoInstruction,
#                                               Categorization.Box.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A), self.mView,
#                             activated=partial(self.mScene.setCurrentInstruction, Instructions.PolygonInstruction,
#                                               Categorization.Box.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_X), self.mView, self.mScene.removeAllPolygone)
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Y), self.mView, self.mScene.removePolygon)
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_1), self.mView,
#                             activated=partial(self.setColorCode, Categorization.Box.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_2), self.mView,
#                             activated=partial(self.setColorCode, Categorization.Bag.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_3), self.mView,
#                                 activated=partial(self.setColorCode, Categorization.Bundle.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_4), self.mView,
#                             activated=partial(self.setColorCode, Categorization.Unknown.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_5), self.mView,
#                             activated=partial(self.setColorCode, Categorization.Rest.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_6), self.mView,
#                             activated=partial(self.setColorCode, Categorization.Flat.value))
#
#         QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_7), self.mView,
#                             activated=partial(self.setColorCode, Categorization.TransparentBag.value))
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# #   Set Categorization with from images with ColorCodes
# # ----------------------------------------------------------------------------------------------------------------------
#
#     def setColorCode(self, catrgory: str):
#         self.mScene.setCurrentInstruction(Instructions.PolygonInstruction, catrgory)
#
# # ----------------------------------------------------------------------------------------------------------------------
# #   Set View Modification with ZoomIn/-Out
# # ----------------------------------------------------------------------------------------------------------------------
#
#     @QtCore.Slot()
#     def zoomIn(self):
#         self.zoom(2)
#
#     @QtCore.Slot()
#     def zoomOut(self):
#         self.zoom(1 / 2)
#
#     def zoom(self, f):
#         self.mView.scale(f, f)
#         if self.mView.scene() is not None:
#             self.mView.centerOn(self.mView.scene().imageItem)
#
#     def showEvent(self, event: QtGui.QShowEvent):
#         self.mView.fitInView(self.mScene.sceneRect(), QtCore.Qt.KeepAspectRatio)
#
# # ----------------------------------------------------------------------------------------------------------------------
# #   Load Images in QGraphicsScene and fit in QGraphicsView
# # ----------------------------------------------------------------------------------------------------------------------
#
#     @QtCore.Slot()
#     def load_image(self, imageNavigation):
#         self.mScene.removeAllPolygone()
#         if imageNavigation == 1 and self.counterImages < self.realpathImages.__len__() - 1:
#             self.counterImages = self.counterImages + 1
#         elif imageNavigation == 0 and self.counterImages > 0:
#             self.counterImages = self.counterImages - 1
#         else:
#             self.counterImages = 0
#
#         if self.realpathImages[self.counterImages]:
#             self.mScene.load_image(self.realpathImages[self.counterImages])
#             self.mView.fitInView(self.mScene.imageItem, QtCore.Qt.KeepAspectRatio)
#             self.mView.centerOn(self.mScene.imageItem)

#
# class MainWindow(QMainWindow):
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)


# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     # m = MainWindow()
#     # w = WidgetWindow(m)
#     # m.show()
#     w = WidgetWindow()
#     w.show()
#     sys.exit(app.exec_())